# Run from repo root: blender --background --python test_addon_load.py
import sys
import os
repo = os.path.dirname(os.path.abspath(__file__))
if repo not in sys.path:
    sys.path.insert(0, repo)

import bpy
import MikuMikuRig
MikuMikuRig.register()

# Check key operators
assert hasattr(bpy.ops.mmr, "rig_preset"), "mmr.rig_preset missing"
assert hasattr(bpy.ops.mmr, "set_min_ik_loop"), "mmr.set_min_ik_loop missing"
assert hasattr(bpy.ops.mmr, "pose_lib_save"), "mmr.pose_lib_save missing"
assert hasattr(bpy.ops.mmr, "add_capsule_colliders"), "mmr.add_capsule_colliders missing"
for name in ('pose_asset_save', 'pose_asset_apply', 'pose_asset_ik', 'pose_asset_browse'):
    getattr(bpy.ops.mmr, name).get_rna_type()
print("All key operators registered.")

MikuMikuRig.unregister()
print("Test OK.")
