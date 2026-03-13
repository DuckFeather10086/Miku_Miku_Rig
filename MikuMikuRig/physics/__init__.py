# Physics: capsule colliders (Skinify-style)
import bpy

from . import operators
from . import panels


def register():
    for cls in operators.Class_list:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(panels.MMR_PT_Capsule_Colliders)


def unregister():
    bpy.utils.unregister_class(panels.MMR_PT_Capsule_Colliders)
    for cls in reversed(operators.Class_list):
        bpy.utils.unregister_class(cls)
