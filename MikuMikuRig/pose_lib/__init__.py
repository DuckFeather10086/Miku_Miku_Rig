# Pose library: save/load Rigify poses as JSONL
import bpy

from . import operators
from . import panels


def register():
    for cls in operators.Class_list:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(panels.MMR_PT_Pose_Library)


def unregister():
    bpy.utils.unregister_class(panels.MMR_PT_Pose_Library)
    for cls in reversed(operators.Class_list):
        bpy.utils.unregister_class(cls)
