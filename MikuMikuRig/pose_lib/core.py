# Pose library core: JSONL read/write, all-bone save/load, optional FK/IK sync
import os
import json
import bpy
from .. import base
from .. import settings


def get_pose_library_directory(context):
    """Return the pose library directory (user-set or default)."""
    scene = context.scene
    mmr = scene.mmr_property
    path = mmr.pose_lib_directory.strip()
    if path:
        return path
    return settings.get_pose_library_default_directory()


def _ensure_directory(path):
    os.makedirs(path, exist_ok=True)
    return path


def _jsonl_path(dir_path):
    return os.path.join(dir_path, "poses.jsonl")


def _bone_pose_to_dict(pose_bone):
    """Export one pose bone to a JSON-serializable dict (all layers; no visibility filter)."""
    pb = pose_bone
    out = {
        "location": list(pb.location),
        "rotation_mode": pb.rotation_mode,
        "scale": list(pb.scale),
    }
    if pb.rotation_mode == 'QUATERNION':
        q = pb.rotation_quaternion
        out["rotation_quaternion"] = [q.w, q.x, q.y, q.z]
    else:
        e = pb.rotation_euler
        out["rotation_euler"] = [e.x, e.y, e.z]
    return out


def _dict_to_bone_pose(pb, data):
    """Apply saved dict to a pose bone."""
    if "location" in data:
        pb.location = data["location"]
    if "scale" in data:
        pb.scale = data["scale"]
    if "rotation_mode" in data:
        pb.rotation_mode = data["rotation_mode"]
    if "rotation_quaternion" in data:
        q = data["rotation_quaternion"]
        pb.rotation_quaternion = (q[0], q[1], q[2], q[3])
    elif "rotation_euler" in data:
        e = data["rotation_euler"]
        pb.rotation_euler = (e[0], e[1], e[2])


def _try_rigify_sync_limbs(armature):
    """Try to sync Rigify IK/FK so both represent the same pose. No-op if not Rigify."""
    if not armature or armature.type != 'ARMATURE':
        return
    data = armature.data
    rig_id = getattr(data, "rig_id", None) or data.get("rig_id")
    if not rig_id:
        return
    op_attr = f"rigify_generic_snap_{rig_id}"
    if not hasattr(bpy.ops.pose, op_attr):
        return
    pose_bones = armature.pose.bones
    # Common limb bone lists for default Rigify (names may vary per rig)
    limbs = [
        (['upper_arm_fk.L', 'forearm_fk.L', 'hand_fk.L'],
         ['upper_arm_ik.L', 'MCH-forearm_ik.L', 'MCH-upper_arm_ik_target.L'],
         ['upper_arm_ik.L', 'upper_arm_ik_target.L', 'hand_ik.L']),
        (['upper_arm_fk.R', 'forearm_fk.R', 'hand_fk.R'],
         ['upper_arm_ik.R', 'MCH-forearm_ik.R', 'MCH-upper_arm_ik_target.R'],
         ['upper_arm_ik.R', 'upper_arm_ik_target.R', 'hand_ik.R']),
        (['thigh_fk.L', 'shin_fk.L', 'foot_fk.L'],
         ['thigh_ik.L', 'MCH-thigh_ik.L', 'MCH-thigh_ik_target.L'],
         ['thigh_ik.L', 'thigh_ik_target.L', 'foot_ik.L']),
        (['thigh_fk.R', 'shin_fk.R', 'foot_fk.R'],
         ['thigh_ik.R', 'MCH-thigh_ik.R', 'MCH-thigh_ik_target.R'],
         ['thigh_ik.R', 'thigh_ik_target.R', 'foot_ik.R']),
    ]
    for output_bones, input_bones, ctrl_bones in limbs:
        required = output_bones + input_bones + ctrl_bones
        if any(name not in pose_bones for name in required):
            continue
        try:
            getattr(bpy.ops.pose, op_attr)(
                output_bones=json.dumps(output_bones),
                input_bones=json.dumps(input_bones),
                ctrl_bones=json.dumps(ctrl_bones),
            )
        except Exception:
            pass


def save_pose(context, pose_name, sync_ik_fk=True):
    """
    Save current pose of active armature to JSONL. Saves ALL bones (all layers).
    If sync_ik_fk, tries to sync Rigify limbs before sampling.
    Returns (success: bool, message: str).
    """
    obj = context.view_layer.objects.active
    if not obj or obj.type != 'ARMATURE':
        return False, "No armature selected"
    armature = obj
    if context.mode != 'POSE':
        try:
            bpy.ops.object.mode_set(mode='POSE')
        except RuntimeError:
            return False, "Could not switch to Pose mode"
    if sync_ik_fk:
        _try_rigify_sync_limbs(armature)
    pose = armature.pose
    bones_data = {}
    for pb in pose.bones:
        bones_data[pb.name] = _bone_pose_to_dict(pb)
    record = {
        "name": pose_name,
        "armature_name": armature.name,
        "bones": bones_data,
    }
    dir_path = get_pose_library_directory(context)
    _ensure_directory(dir_path)
    path = _jsonl_path(dir_path)
    lines = []
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        existing = json.loads(line)
                        if existing.get("name") != pose_name:
                            lines.append(line)
                    except json.JSONDecodeError:
                        lines.append(line)
        except OSError:
            pass
    lines.append(json.dumps(record, ensure_ascii=False))
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
    except OSError as e:
        return False, str(e)
    return True, f"Saved pose '{pose_name}'"


def load_pose(context, pose_name):
    """Load a pose by name from JSONL and apply to active armature. Returns (success, message)."""
    obj = context.view_layer.objects.active
    if not obj or obj.type != 'ARMATURE':
        return False, "No armature selected"
    dir_path = get_pose_library_directory(context)
    path = _jsonl_path(dir_path)
    if not os.path.exists(path):
        return False, "Pose library file not found"
    record = None
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("name") == pose_name:
                    record = data
                    break
            except json.JSONDecodeError:
                continue
    if not record or "bones" not in record:
        return False, f"Pose '{pose_name}' not found"
    if context.mode != 'POSE':
        try:
            bpy.ops.object.mode_set(mode='POSE')
        except RuntimeError:
            return False, "Could not switch to Pose mode"
    pose = obj.pose
    applied = 0
    for bone_name, bone_data in record["bones"].items():
        if bone_name not in pose.bones:
            continue
        _dict_to_bone_pose(pose.bones[bone_name], bone_data)
        applied += 1
    return True, f"Applied pose '{pose_name}' ({applied} bones)"


def list_poses(context):
    """Return list of (name, armature_name) from the JSONL file."""
    dir_path = get_pose_library_directory(context)
    path = _jsonl_path(dir_path)
    result = []
    if not os.path.exists(path):
        return result
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                name = data.get("name", "")
                arm = data.get("armature_name", "")
                if name:
                    result.append((name, arm))
            except json.JSONDecodeError:
                continue
    return result


def delete_pose_from_library(context, pose_name):
    """Remove one pose by name from JSONL. Returns (success, message)."""
    dir_path = get_pose_library_directory(context)
    path = _jsonl_path(dir_path)
    if not os.path.exists(path):
        return False, "Pose library not found"
    lines = []
    found = False
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            try:
                data = json.loads(line_stripped)
                if data.get("name") == pose_name:
                    found = True
                    continue
                lines.append(line_stripped)
            except json.JSONDecodeError:
                lines.append(line_stripped)
    if not found:
        return False, f"Pose '{pose_name}' not found"
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n' if lines else '')
    except OSError as e:
        return False, str(e)
    return True, f"Deleted pose '{pose_name}'"
