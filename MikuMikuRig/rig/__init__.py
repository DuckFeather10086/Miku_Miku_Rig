# MikuMikuRig rig: preset + Rigify generation
import bpy

from . import preset
from . import rig as rig_module

# Re-export for extra module: extra expects "rig" module with check_arm, decorate_mmd_arm, etc.
rig = rig_module

def register():
    for cls in preset.Class_list:
        bpy.utils.register_class(cls)
    for cls in rig_module.Class_list:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(rig_module.Class_list):
        bpy.utils.unregister_class(cls)
    for cls in reversed(preset.Class_list):
        bpy.utils.unregister_class(cls)
