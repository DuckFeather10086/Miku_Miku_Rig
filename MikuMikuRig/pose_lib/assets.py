"""Native Action assets containing portable MMR FK controls."""
import json
import math
import os
import re
import uuid
from pathlib import Path

import bpy
from bpy_extras import anim_utils
from mathutils import Quaternion, Vector

from . import rig_adapter as adapter

LIBRARY_NAME = 'MMR Poses'
SCHEMA = 1
BODY_CONTROLS = {'root', 'Center', 'Groove', 'torso', 'hips', 'chest', 'neck', 'head'}
TRANSLATIONS = {'Center', 'Groove', 'torso', 'hips', 'chest'}
FOLLOW_PROPS = {'FK_limb_follow', 'neck_follow', 'head_follow', 'torso_parent', 'finger_curve'}


def library_directory(context):
    configured = context.scene.mmr_property.pose_asset_directory.strip()
    if configured:
        return Path(bpy.path.abspath(configured)).resolve()
    library = context.preferences.filepaths.asset_libraries.get(LIBRARY_NAME)
    if library:
        return Path(bpy.path.abspath(library.path)).resolve()
    return Path(bpy.utils.user_resource('DATAFILES', path='MMR/PoseAssets', create=True))


def register_library(context, directory, *, persist=True):
    directory.mkdir(parents=True, exist_ok=True)
    libraries = context.preferences.filepaths.asset_libraries
    library = libraries.get(LIBRARY_NAME)
    if library is None:
        library = libraries.new(name=LIBRARY_NAME, directory=str(directory))
    else:
        library.path = str(directory)
    if persist:
        bpy.ops.wm.save_userpref()
    return library


def catalog(directory, category):
    category = category.strip().strip('/') or '通用姿势'
    if any(c in category for c in ':\r\n\\'):
        raise adapter.PoseAssetError('分类不能包含冒号、换行或反斜杠')
    path = directory / 'blender_assets.cats.txt'
    text = path.read_text(encoding='utf-8') if path.exists() else '# MMR pose asset catalogs\nVERSION 1\n'
    for line in text.splitlines():
        if not line.strip() or line.startswith('#') or line.startswith('VERSION'):
            continue
        fields = line.split(':', 2)
        if len(fields) == 3 and fields[1] == category:
            return fields[0]
    identifier = str(uuid.uuid5(uuid.NAMESPACE_URL, 'MMR Poses/' + category))
    temporary = path.with_suffix('.tmp')
    temporary.write_text(text.rstrip() + f'\n{identifier}:{category}:{category.replace("/", " - ")}\n', encoding='utf-8')
    os.replace(temporary, path)
    return identifier


def controls(rig, limbs):
    limb_names = {name for limb in limbs for name in limb['fk']}
    names = []
    for p in rig.pose.bones:
        n = p.name
        if n in limb_names or n in BODY_CONTROLS or re.fullmatch(
                r'(spine_fk(?:\.\d+)?|shoulder\.[LR]|breast\.[LR]|toe\.[LR]|'
                r'(?:f_(?:thumb|index|middle|ring|pinky)|thumb|toe_(?:thumb|index|middle|ring|pinky))'
                r'\.\d+(?:_master)?\.[LR](?:\.\d+)?)', n):
            names.append(n)
    return sorted(names)


def body_size(rig):
    positions = [rig.data.bones[n].head_local for n in ('head', 'foot_fk.L', 'foot_fk.R')]
    size = max(p.z for p in positions) - min(p.z for p in positions)
    if size < 1e-6:
        raise adapter.PoseAssetError('无法读取骨架的静止身高')
    return size


def quaternion(p):
    if p.rotation_mode == 'QUATERNION':
        return p.rotation_quaternion.normalized()
    if p.rotation_mode == 'AXIS_ANGLE':
        return Quaternion(Vector(p.rotation_axis_angle[1:]), p.rotation_axis_angle[0])
    return p.rotation_euler.to_quaternion()


def curves(action):
    if len(action.slots) != 1:
        raise adapter.PoseAssetError('姿势资产应只有一个骨架槽位')
    bag = anim_utils.action_get_channelbag_for_slot(action, action.slots[0])
    if bag is None:
        raise adapter.PoseAssetError('姿势资产没有控制通道')
    return bag.fcurves


def build_action(rig, limbs, name):
    action = bpy.data.actions.new(name)
    slot = action.slots.new('OBJECT', rig.name)
    bag = anim_utils.action_ensure_channelbag_for_slot(action, slot)
    names = controls(rig, limbs)
    properties = {}

    def insert(path, values, group):
        for index, value in enumerate(values):
            fc = bag.fcurves.new(path, index=index, group_name=group)
            fc.keyframe_points.insert(1, value)
    try:
        for name in names:
            p = rig.pose.bones[name]
            insert(p.path_from_id('rotation_quaternion'), quaternion(p), name)
            if name in {n for limb in limbs for n in limb['fk']}:
                insert(p.path_from_id('location'), (0, 0, 0), name)
                insert(p.path_from_id('scale'), (1, 1, 1), name)
            if name in TRANSLATIONS:
                insert(p.path_from_id('location'), p.location, name)
            # Rigify finger master Y scale is curl, not body proportion.
            if '_master.' in name:
                fc = bag.fcurves.new(p.path_from_id('scale'), index=1, group_name=name)
                fc.keyframe_points.insert(1, p.scale.y)
            for prop in FOLLOW_PROPS & set(p.keys()):
                properties.setdefault(name, {})[prop] = p[prop]
        for limb in limbs:
            p = rig.pose.bones[limb['prop']]
            properties.setdefault(p.name, {})['IK_FK'] = 1.0
            if 'FK_limb_follow' in p:
                properties[p.name]['FK_limb_follow'] = p['FK_limb_follow']
        for name, props in properties.items():
            for prop, value in props.items():
                insert(rig.pose.bones[name].path_from_id() + '[' + json.dumps(prop) + ']', [value], name)
        action['mmr_pose_schema'] = SCHEMA
        action['mmr_pose_metadata'] = json.dumps({
            'height': body_size(rig), 'controls': names, 'properties': properties,
            'fk_controls': [n for limb in limbs for n in limb['fk']],
            'source_rig': rig.name, 'frame': 1,
        }, ensure_ascii=False)
        action.asset_mark()
        action.asset_data.description = 'MMR FK 姿势；用“MMR · FK 应用姿势”跨体型应用，手脚接触位置用 IK 微调。'
        action.asset_data.tags.new('MMR')
        action.asset_data.tags.new('FK')
        return action
    except Exception:
        # Creation is transactional; never retain an incomplete asset.
        bpy.data.actions.remove(action)
        raise


def validate_action(action, rig, limbs):
    if action.get('mmr_pose_schema') != SCHEMA:
        raise adapter.PoseAssetError('这是未整理的旧资产；请先在原角色应用，再用 MMR 保存为 FK 姿势资产')
    metadata = json.loads(action['mmr_pose_metadata'])
    if set(metadata['controls']) - set(controls(rig, limbs)):
        raise adapter.PoseAssetError('姿势包含不支持的控制骨')
    if set(metadata['fk_controls']) != {n for limb in limbs for n in limb['fk']}:
        raise adapter.PoseAssetError('来源与目标的 FK 控制链不同，请使用相同控制器布局')
    names = set(metadata['controls']) | set(metadata['properties'])
    missing = names - set(rig.pose.bones.keys())
    if missing:
        raise adapter.PoseAssetError('目标缺少姿势控制骨: ' + ', '.join(sorted(missing)))
    allowed = {}
    for name in metadata['controls']:
        p = rig.pose.bones[name]
        allowed[p.path_from_id('rotation_quaternion')] = set(range(4))
        if name in metadata['fk_controls']:
            allowed[p.path_from_id('location')] = set(range(3))
            allowed[p.path_from_id('scale')] = set(range(3))
        if name in TRANSLATIONS:
            allowed[p.path_from_id('location')] = set(range(3))
        if '_master.' in name:
            allowed[p.path_from_id('scale')] = {1}
    for name, props in metadata['properties'].items():
        p = rig.pose.bones[name]
        for prop in props:
            if prop not in FOLLOW_PROPS | {'IK_FK'} or prop not in p:
                raise adapter.PoseAssetError(f'不兼容的姿势属性: {name}/{prop}')
            allowed[p.path_from_id() + '[' + json.dumps(prop) + ']'] = {0}
    found = set()
    for fc in curves(action):
        if fc.data_path not in allowed or fc.array_index not in allowed[fc.data_path]:
            raise adapter.PoseAssetError('资产包含非 FK 姿势通道: ' + fc.data_path)
        if len(fc.keyframe_points) != 1 or fc.modifiers or not math.isfinite(fc.keyframe_points[0].co.y):
            raise adapter.PoseAssetError('资产需要是单帧姿势，不能包含动画或曲线修改器')
        value = fc.keyframe_points[0].co.y
        if fc.data_path.endswith('["IK_FK"]') and abs(value - 1) > 1e-6:
            raise adapter.PoseAssetError('姿势资产不是完整 FK 状态')
        for name in metadata['fk_controls']:
            p = rig.pose.bones[name]
            if fc.data_path == p.path_from_id('scale') and abs(value - 1) > 1e-6:
                raise adapter.PoseAssetError('FK 姿势资产含有肢体拉伸')
            if fc.data_path == p.path_from_id('location') and abs(value) > 1e-6:
                raise adapter.PoseAssetError('FK 姿势资产含有肢体位移')
        found.add((fc.data_path, fc.array_index))
    if found != {(path, index) for path, indices in allowed.items() for index in indices}:
        raise adapter.PoseAssetError('姿势资产缺少控制通道')
    if not math.isfinite(metadata['height']) or metadata['height'] <= 0:
        raise adapter.PoseAssetError('姿势资产身高无效')
    return metadata


def apply_action(context, rig, action, *, adapt_translation=True):
    limbs = adapter.snap_definitions(rig)
    metadata = validate_action(action, rig, limbs)
    ratio = body_size(rig) / metadata['height'] if adapt_translation else 1.0
    selection = {p.name: p.select for p in rig.pose.bones}
    temporary = action.copy()
    temporary.asset_clear()
    try:
        # Only central-body translations adapt; root placement and limb lengths stay local.
        for fc in curves(temporary):
            if fc.data_path.endswith('.location'):
                fc.keyframe_points[0].co.y *= ratio
                fc.update()
        with adapter.pose_operation(context, rig):
            for p in rig.pose.bones:
                p.select = False
            rig.pose.apply_pose_from_action(temporary, evaluation_time=1)
            rig.update_tag()
            context.view_layer.update()
            for limb in limbs:
                if abs(rig.pose.bones[limb['prop']]['IK_FK'] - 1.0) > 1e-6:
                    raise adapter.PoseAssetError('FK 开关未生效；请检查现有驱动或动画')
    finally:
        for name, selected in selection.items():
            rig.pose.bones[name].select = selected
        bpy.data.actions.remove(temporary)
    return ratio


def save_asset(context, name, category, *, directory=None, persist_preferences=True):
    name = name.strip()
    if not name:
        raise adapter.PoseAssetError('请填写姿势名称')
    rig = adapter.require_rig(context)
    limbs = adapter.snap_definitions(rig)
    directory = Path(directory) if directory else library_directory(context)
    directory.mkdir(parents=True, exist_ok=True)
    catalog_id = catalog(directory, category)
    action = None
    try:
        with adapter.pose_operation(context, rig, restore_always=True):
            adapter.switch_to_fk(context, rig, limbs)
            action = build_action(rig, limbs, name)
            action.asset_data.catalog_id = catalog_id
            # Portable FK poses discard temporary limb stretch/offset, never rest-bone proportions.
            for limb in limbs:
                for bone in limb['fk']:
                    rig.pose.bones[bone].location = (0, 0, 0)
                    rig.pose.bones[bone].scale = (1, 1, 1)
            rig.update_tag()
            context.view_layer.update()
            from . import thumbnail
            thumbnail.set_preview(context, rig, action)
        slug = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name).strip(' .')[:60] or 'pose'
        path = directory / (slug + '-' + uuid.uuid4().hex[:10] + '.blend')
        temporary = path.with_suffix('.tmp.blend')
        try:
            bpy.data.libraries.write(str(temporary), {action}, fake_user=True, compress=True)
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
        register_library(context, directory, persist=persist_preferences)
        return action, path
    except Exception:
        # Restore the source pose and remove incomplete local assets on external I/O failure.
        if action:
            bpy.data.actions.remove(action)
        raise


def load_action(path, name):
    with bpy.data.libraries.load(str(path), link=False, assets_only=True) as (source, target):
        if name not in source.actions:
            raise adapter.PoseAssetError('文件中找不到此姿势资产: ' + name)
        target.actions = [name]
    return target.actions[0]
