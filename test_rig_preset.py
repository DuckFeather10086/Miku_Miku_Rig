# Run: blender --background --python test_rig_preset.py
import sys
import os
repo = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, repo)
out = open(os.path.join(repo, "test_rig_out.txt"), "w")
def log(s):
    out.write(s + "\n")
    out.flush()
import bpy
import MikuMikuRig
MikuMikuRig.register()
log("addon registered")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.object.armature_add(enter_editmode=False)
arm = bpy.context.active_object
arm.name = "TestArm"
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones.new("Spine")
eb.head = (0, 0, 1)
eb.tail = (0, 0, 1.2)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

try:
    bpy.ops.mmr.rig_preset()
    log("rig_preset executed")
except Exception as e:
    log("rig_preset error: " + str(e))

MikuMikuRig.unregister()
log("Done.")
out.close()
