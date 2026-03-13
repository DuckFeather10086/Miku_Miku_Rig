# Extra: min IK loop (Rigify-related only)
import bpy
from bpy.types import Operator
from ..rig import rig


def set_min_ik_loop(arm, min_ik_loop=10):
    if not arm or arm.type != 'ARMATURE':
        return False
    for bone in arm.pose.bones:
        for c in bone.constraints:
            if c.type == 'IK':
                if c.iterations < min_ik_loop:
                    c.iterations = min_ik_loop
    return True


class OT_Set_Min_IK_Loop(Operator):
    bl_idname = "mmr.set_min_ik_loop"
    bl_label = "Set Min IK Loop"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.view_layer.objects.active
        if not obj or obj.type != 'ARMATURE':
            return {'CANCELLED'}
        mmr_property = context.scene.mmr_property
        set_min_ik_loop(obj, mmr_property.min_ik_loop)
        self.report({'INFO'}, "Min IK loop set")
        return {'FINISHED'}


Class_list = [OT_Set_Min_IK_Loop]
