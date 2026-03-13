import json
import math
import os
import shutil
import sys

repo = os.path.dirname(os.path.abspath(__file__))
if repo not in sys.path:
    sys.path.insert(0, repo)

import bpy
import MikuMikuRig
from MikuMikuRig.physics import capsule_core
from MikuMikuRig.pose_lib import core as pose_core
from MikuMikuRig.rig import preset as rig_preset_module


SOURCE_NAME = "Genesis 9"
RIG_NAME = "Genesis 9_Rig"
TEST_PRESET_NAME = "Genesis9_AutoTest"
POSE_DIR = os.path.join(repo, ".tmp_pose_lib_tests")


def log(message):
    print(f"[TEST] {message}")


def ensure(condition, message):
    if not condition:
        raise AssertionError(message)


def cleanup_pose_dir():
    if os.path.isdir(POSE_DIR):
        shutil.rmtree(POSE_DIR)


def set_active(obj):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def get_source():
    return bpy.data.objects[SOURCE_NAME]


def get_rig():
    return bpy.data.objects[RIG_NAME]


def result_finished(result):
    return result == {'FINISHED'} or "FINISHED" in result


def read_pose_records():
    path = os.path.join(POSE_DIR, "poses.jsonl")
    with open(path, "r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_generate_from_preset():
    scene = bpy.context.scene
    source = get_source()
    ensure("Genesis9" in rig_preset_module.preset_dict_dict["rig"], "Genesis9 preset missing")
    scene.mmr_property.rig_preset_name = "Genesis9"
    old_ptr = get_rig().as_pointer()
    set_active(source)
    result = bpy.ops.mmr.rig_preset()
    ensure(result_finished(result), "Generate rig with Genesis9 preset failed")
    rig = get_rig()
    ensure(rig.as_pointer() != old_ptr, "Rig object was not replaced on regenerate")
    for bone_name in ("upper_arm_fk.L", "forearm_fk.L", "hand_fk.L", "hand_ik.L"):
        ensure(bone_name in rig.pose.bones, f"Missing expected control bone: {bone_name}")
    log("generate_from_preset: pass")


def test_switch_preset_and_regenerate():
    scene = bpy.context.scene
    source = get_source()
    rig_preset_module.preset_dict_dict["rig"][TEST_PRESET_NAME] = dict(
        rig_preset_module.preset_dict_dict["rig"]["Genesis9"]
    )
    scene.mmr_property.rig_preset_name = TEST_PRESET_NAME
    old_ptr = get_rig().as_pointer()
    set_active(source)
    result = bpy.ops.mmr.rig_preset()
    ensure(result_finished(result), "Generate rig after preset switch failed")
    ensure(get_rig().as_pointer() != old_ptr, "Rig was not regenerated after preset switch")
    log("switch_preset_and_regenerate: pass")


def test_regenerate_with_existing_pose_from_selected_rig():
    scene = bpy.context.scene
    scene.mmr_property.rig_preset_name = TEST_PRESET_NAME
    rig = get_rig()
    set_active(rig)
    bpy.ops.object.mode_set(mode='POSE')
    pose_bone = rig.pose.bones["upper_arm_fk.L"]
    pose_bone.rotation_mode = "XYZ"
    pose_bone.rotation_euler = (0.35, -0.15, 0.1)
    bpy.context.view_layer.update()
    old_ptr = rig.as_pointer()
    result = bpy.ops.mmr.rig_preset()
    ensure(result_finished(result), "Regenerate from selected _Rig failed")
    ensure(get_rig().as_pointer() != old_ptr, "Rig was not recreated when regenerating from posed _Rig")
    log("regenerate_with_existing_pose_from_selected_rig: pass")


def test_pose_library_save_load_delete():
    scene = bpy.context.scene
    rig = get_rig()
    cleanup_pose_dir()
    scene.mmr_property.pose_lib_directory = POSE_DIR
    set_active(rig)
    bpy.ops.object.mode_set(mode='POSE')

    hidden_collection_name = None
    collections = list(getattr(rig.data, "collections_all", []))
    if collections and hasattr(collections[0], "is_visible"):
        hidden_collection_name = collections[0].name
        collections[0].is_visible = False

    pose_bone = rig.pose.bones["upper_arm_fk.L"]
    pose_bone.rotation_mode = "XYZ"
    pose_bone.rotation_euler = (0.4, -0.25, 0.15)
    expected_rotation = tuple(pose_bone.rotation_euler)

    scene.mmr_property.pose_save_sync_ik_fk = False
    result = bpy.ops.mmr.pose_lib_save('EXEC_DEFAULT', pose_name="pose_no_sync")
    ensure(result_finished(result), "pose_no_sync save failed")

    scene.mmr_property.pose_save_sync_ik_fk = True
    result = bpy.ops.mmr.pose_lib_save('EXEC_DEFAULT', pose_name="pose_sync")
    ensure(result_finished(result), "pose_sync save failed")

    records = read_pose_records()
    record_names = {record["name"] for record in records}
    ensure({"pose_no_sync", "pose_sync"}.issubset(record_names), "Pose records missing from JSONL")

    pose_record = next(record for record in records if record["name"] == "pose_no_sync")
    ensure(
        len(pose_record["bones"]) == len(rig.pose.bones),
        "Pose library did not save all bones",
    )

    if hidden_collection_name is not None:
        ensure(
            hidden_collection_name in [collection.name for collection in rig.data.collections_all],
            "Hidden collection setup failed",
        )

    pose_bone.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    result = bpy.ops.mmr.pose_lib_load('EXEC_DEFAULT', pose_name="pose_no_sync")
    ensure(result_finished(result), "pose_no_sync load failed")
    restored = tuple(round(value, 4) for value in pose_bone.rotation_euler)
    expected = tuple(round(value, 4) for value in expected_rotation)
    ensure(restored == expected, f"Pose load did not restore rotation: {restored} != {expected}")

    result = bpy.ops.mmr.pose_lib_delete('EXEC_DEFAULT', pose_name="pose_sync")
    ensure(result_finished(result), "pose_sync delete failed")
    remaining_names = {record["name"] for record in read_pose_records()}
    ensure("pose_sync" not in remaining_names, "pose_sync still present after delete")
    log("pose_library_save_load_delete: pass")


def test_capsule_core_and_operator():
    scene = bpy.context.scene
    source = get_source()

    ok, message, objects = capsule_core.add_capsule_colliders(
        bpy.context,
        source,
        bone_names=["pelvis", "l_thigh", "r_thigh"],
        scale=0.8,
        add_rigid_body=True,
    )
    ensure(ok, f"capsule_core failed: {message}")
    ensure(len(objects) == 3, "capsule_core did not create expected number of colliders")
    for obj in objects:
        ensure(obj.parent == source, "Capsule collider parent mismatch")
        ensure(obj.parent_type == 'BONE', "Capsule collider parent type should be BONE")
        ensure(obj.parent_bone in {"pelvis", "l_thigh", "r_thigh"}, "Capsule collider parent bone mismatch")
        ensure(obj.rigid_body is not None, "Capsule collider rigid body missing")
        ensure(obj.rigid_body.collision_shape == 'CAPSULE', "Capsule collider shape is not CAPSULE")

    bpy.ops.object.armature_add(enter_editmode=False)
    test_arm = bpy.context.active_object
    test_arm.name = "CapsuleTestArm"
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = test_arm.data.edit_bones
    first = edit_bones[0]
    first.name = "root"
    first.head = (0.0, 0.0, 0.0)
    first.tail = (0.0, 0.2, 0.0)
    second = edit_bones.new("child")
    second.head = first.tail
    second.tail = (0.0, 0.5, 0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

    before = {obj.name for obj in bpy.data.objects if obj.name.startswith("Cap_")}
    scene.mmr_property.capsule_scale = 1.0
    scene.mmr_property.capsule_add_rigid_body = True
    set_active(test_arm)
    result = bpy.ops.mmr.add_capsule_colliders()
    ensure(result_finished(result), "Capsule collider operator failed")
    after = {obj.name for obj in bpy.data.objects if obj.name.startswith("Cap_")}
    created_names = after - before
    ensure(len(created_names) >= 2, "Capsule collider operator did not create expected colliders")
    log("capsule_core_and_operator: pass")


def test_set_min_ik_loop():
    scene = bpy.context.scene
    rig = get_rig()
    set_active(rig)
    scene.mmr_property.min_ik_loop = 77
    result = bpy.ops.mmr.set_min_ik_loop()
    ensure(result_finished(result), "set_min_ik_loop operator failed")
    ik_constraints = [
        constraint
        for pose_bone in rig.pose.bones
        for constraint in pose_bone.constraints
        if constraint.type == 'IK'
    ]
    ensure(ik_constraints, "No IK constraints found on generated rig")
    ensure(
        min(constraint.iterations for constraint in ik_constraints) >= 77,
        "Not all IK constraints were updated",
    )
    log("set_min_ik_loop: pass")


def main():
    MikuMikuRig.register()
    try:
        test_generate_from_preset()
        test_switch_preset_and_regenerate()
        test_regenerate_with_existing_pose_from_selected_rig()
        test_pose_library_save_load_delete()
        test_capsule_core_and_operator()
        test_set_min_ik_loop()
        log("all workflow tests passed")
    finally:
        rig_preset_module.preset_dict_dict["rig"].pop(TEST_PRESET_NAME, None)
        cleanup_pose_dir()
        MikuMikuRig.unregister()


if __name__ == "__main__":
    main()
