"""MMR FK pose assets: use the generated Rigify snap definitions, not guessed chains."""
import ast
import json
from contextlib import contextmanager

import bpy


class PoseAssetError(ValueError):
    pass


def require_rig(context):
    rig = context.object
    if not rig or rig.type != 'ARMATURE' or not rig.data.get('rig_id'):
        raise PoseAssetError('请选择 MMR 生成的 Rigify 控制骨架')
    if rig.mode not in {'OBJECT', 'POSE'}:
        raise PoseAssetError('请先退出编辑模式')
    if rig.library or rig.data.library:
        raise PoseAssetError('请先让控制骨架成为可编辑的本地对象或库覆盖')
    return rig


def snap_definitions(rig):
    """Read literal operator arguments from this rig's generated UI, without executing text."""
    rig_id = rig.data['rig_id']
    for text in bpy.data.texts:
        source = text.as_string()
        if rig_id not in source or 'rigify_generic_snap_' not in source:
            continue
        tree = ast.parse(source)
        ids = [n.value.value for n in tree.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'rig_id' for t in n.targets)
               and isinstance(n.value, ast.Constant)]
        if rig_id not in ids:
            continue
        calls = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.If)):
                continue
            active = None
            for statement in node.body:
                if not isinstance(statement, ast.Assign):
                    active = None
                    continue
                value = statement.value
                if (isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute)
                        and value.func.attr == 'operator' and value.args
                        and isinstance(value.args[0], ast.Constant)):
                    op = value.args[0].value
                    active = {'operator': op, 'args': {}}
                    calls.append(active)
                elif active and len(statement.targets) == 1:
                    target = statement.targets[0]
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'props':
                        active['args'][target.attr] = ast.literal_eval(value)
                    else:
                        active = None
        generic = {tuple(json.loads(c['args']['output_bones'])): c for c in calls
                   if c['operator'] == 'pose.rigify_generic_snap_' + rig_id}
        limbs = []
        for c in calls:
            if c['operator'] != 'pose.rigify_limb_ik2fk_' + rig_id:
                continue
            fk = tuple(json.loads(c['args']['fk_bones']))
            if fk not in generic:
                raise PoseAssetError('Rigify UI 缺少对应的 FK 匹配定义')
            limb = {'to_fk': generic[fk], 'to_ik': c, 'fk': fk, 'prop': c['args']['prop_bone']}
            if limb['prop'] not in [x['prop'] for x in limbs]:
                limbs.append(limb)
        if len(limbs) != 4:
            raise PoseAssetError('当前仅支持具有双臂、双腿匹配定义的 MMR 人形骨架')
        for limb in limbs:
            args = limb['to_ik']['args']
            names = [limb['prop']]
            for key in ('fk_bones', 'ik_bones', 'ctrl_bones', 'tail_bones', 'extra_ctrls'):
                names.extend(json.loads(args.get(key, '[]')))
            missing = sorted(set(names) - set(rig.pose.bones.keys()))
            if missing:
                raise PoseAssetError('Rigify 匹配定义引用缺失骨骼: ' + ', '.join(missing))
            for call in (limb['to_fk'], limb['to_ik']):
                op = getattr(bpy.ops.pose, call['operator'].split('.', 1)[1])
                try:
                    op.get_rna_type()
                except KeyError as exc:
                    # A saved Rigify UI is not registered when script execution was disabled.
                    raise PoseAssetError('Rigify 匹配操作未加载；请在可信工程中启用其 Rig UI 后重试') from exc
        return limbs
    raise PoseAssetError('找不到此骨架的 Rigify UI 文本，请保留生成骨架时的 Rig UI')


def snapshot(rig):
    return {p.name: (p.location.copy(), p.rotation_mode, p.rotation_quaternion.copy(),
                     p.rotation_euler.copy(), tuple(p.rotation_axis_angle), p.scale.copy(),
                     {k: v for k, v in p.items() if isinstance(v, (float, int, bool))})
            for p in rig.pose.bones}


def restore(rig, state):
    for name, (loc, mode, quat, euler, axis, scale, props) in state.items():
        p = rig.pose.bones[name]
        p.rotation_mode = mode
        p.location, p.rotation_quaternion, p.rotation_euler = loc, quat, euler
        p.rotation_axis_angle, p.scale = axis, scale
        for key, value in props.items():
            p[key] = value
    rig.update_tag()
    bpy.context.view_layer.update()


@contextmanager
def pose_operation(context, rig, *, restore_always=False):
    state = snapshot(rig)
    mode = rig.mode
    auto = context.scene.tool_settings.use_keyframe_insert_auto
    context.scene.tool_settings.use_keyframe_insert_auto = False
    succeeded = False
    try:
        if mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        yield
        succeeded = True
    finally:
        if restore_always or not succeeded:
            restore(rig, state)
        context.scene.tool_settings.use_keyframe_insert_auto = auto
        if rig.mode != mode:
            bpy.ops.object.mode_set(mode=mode)


def call_snap(call):
    op = getattr(bpy.ops.pose, call['operator'].split('.', 1)[1])
    if op('EXEC_DEFAULT', **call['args']) != {'FINISHED'}:
        raise PoseAssetError('Rigify 匹配未完成')


def limb_result(rig, limb):
    # ORG bones are the evaluated output of the IK/FK blend, before tweak deformation.
    return [rig.pose.bones['ORG-' + name.replace('_fk', '')].matrix.copy() for name in limb['fk']]


def check_match(rig, limb, expected):
    actual = limb_result(rig, limb)
    size = max(rig.data.bones[name].length for name in limb['fk'])
    position_error = max((a.translation - b.translation).length for a, b in zip(actual, expected))
    angles = [a.to_quaternion().rotation_difference(b.to_quaternion()).angle
              for a, b in zip(actual, expected)]
    rotation_error = max(min(angle, abs(angle - 6.283185307)) for angle in angles)
    # Rigify's iterative IK solve has finite tolerance; fail with rollback on a real jump.
    if position_error > max(size * 0.003, 1e-5) or rotation_error > 0.02:
        raise PoseAssetError(f'{limb["prop"]} 匹配发生跳变: 位移 {position_error:.6g}, 角度 {rotation_error:.4g}')


def switch_to_fk(context, rig, limbs):
    for limb in limbs:
        prop = rig.pose.bones[limb['prop']]
        value = prop['IK_FK']
        if abs(value - 1.0) < 1e-6:
            continue
        if abs(value) > 1e-6:
            raise PoseAssetError('保存前请将 IK/FK 滑杆置于 0 或 1，暂不支持混合状态')
        expected = limb_result(rig, limb)
        call_snap(limb['to_fk'])
        prop['IK_FK'] = 1.0
        rig.update_tag()
        context.view_layer.update()
        check_match(rig, limb, expected)


def switch_to_ik(context, rig, limbs):
    for limb in limbs:
        prop = rig.pose.bones[limb['prop']]
        if abs(prop['IK_FK']) < 1e-6:
            continue
        if abs(prop['IK_FK'] - 1.0) > 1e-6:
            raise PoseAssetError('请将 IK/FK 滑杆置于 0 或 1')
        expected = limb_result(rig, limb)
        call_snap(limb['to_ik'])
        prop['IK_FK'] = 0.0
        rig.update_tag()
        context.view_layer.update()
        refine_ik_match(context, rig, limb, expected)
        check_match(rig, limb, expected)


def refine_ik_match(context, rig, limb, expected):
    """Refine the generated snap against actual evaluated joints.

    Older generated Rigify UIs stop their scale/rotation correction early. Fit only
    the IK controls (never edit bones, constraints or FK pose) to that saved result.
    """
    import numpy as np
    from mathutils import Quaternion, Matrix
    args = limb['to_ik']['args']
    names = json.loads(args['ctrl_bones'])
    base, pole, end = (rig.pose.bones[names[i]] for i in (0, 1, -1))
    use_pole = rig.pose.bones[limb['prop']].get('pole_vector', False)
    base_scale = base.scale.copy()
    base_rotation = base.matrix_basis.to_quaternion()
    end_location = end.location.copy()
    pole_matrix = pole.matrix.copy()
    axis = (expected[-1].translation - expected[0].translation).normalized()
    center = expected[0].translation
    length = sum(rig.data.bones[n].length for n in limb['fk'][:2])
    tail_names = json.loads(args.get('tail_bones', '[]'))
    tail_matrices = expected[len(json.loads(args['ik_bones'])):]
    target_positions = np.array([tuple(m.translation) for m in expected])
    target_rotations = np.array([tuple(m.to_quaternion().to_matrix()[r]) for m in expected[:2] for r in range(3)])

    def evaluate(parameters):
        base.scale = base_scale * float(np.exp(parameters[0]))
        end.location = end_location + type(end_location)(parameters[2:5] * length)
        if use_pole:
            matrix = pole_matrix.copy()
            matrix.translation = center + Matrix.Rotation(float(parameters[1]), 3, axis) @ (pole_matrix.translation - center)
            pole.matrix = matrix
        else:
            rotation = base_rotation @ Quaternion((0, 1, 0), float(parameters[1]))
            if base.rotation_mode == 'QUATERNION':
                base.rotation_quaternion = rotation
            elif base.rotation_mode == 'AXIS_ANGLE':
                ax, angle = rotation.to_axis_angle()
                base.rotation_axis_angle = (angle, *ax)
            else:
                base.rotation_euler = rotation.to_euler(base.rotation_mode, base.rotation_euler)
        context.view_layer.update()
        for name, matrix in zip(tail_names, tail_matrices):
            rig.pose.bones[name].matrix = matrix
            context.view_layer.update()
        actual = limb_result(rig, limb)
        positions = np.array([tuple(m.translation) for m in actual])
        rotations = np.array([tuple(m.to_quaternion().to_matrix()[r]) for m in actual[:2] for r in range(3)])
        return np.concatenate(((positions - target_positions).ravel() / length,
                               (rotations - target_rotations).ravel() * 0.2))

    parameters = np.zeros(5)
    residual = evaluate(parameters)
    for _ in range(12):
        if np.linalg.norm(residual) < 2e-4:
            break
        step = 1e-3
        jacobian = np.empty((len(residual), 5))
        for index in range(5):
            offset = np.zeros(5); offset[index] = step
            jacobian[:, index] = (evaluate(parameters + offset) - evaluate(parameters - offset)) / (2 * step)
        delta = np.linalg.solve(jacobian.T @ jacobian + np.eye(5) * 1e-5, -jacobian.T @ residual)
        delta = np.clip(delta, -.15, .15)
        improved = False
        for fraction in (1, .5, .25, .125):
            candidate = parameters + delta * fraction
            trial = evaluate(candidate)
            if np.linalg.norm(trial) < np.linalg.norm(residual):
                parameters, residual = candidate, trial
                improved = True
                break
        if not improved:
            break
    evaluate(parameters)
