# Capsule colliders operators
import bpy
from .. import base
from . import capsule_core


class MMR_OT_Add_Capsule_Colliders(bpy.types.Operator):
    bl_idname = "mmr.add_capsule_colliders"
    bl_label = "Add Capsule Colliders"
    bl_description = "Create low-poly capsule colliders parented to armature bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.view_layer.objects.active
        if not obj or obj.type != 'ARMATURE':
            base.alert_error("Capsule Colliders", "Select an armature")
            return {'CANCELLED'}
        mmr = context.scene.mmr_property
        scale = getattr(mmr, 'capsule_scale', 1.0)
        add_rb = getattr(mmr, 'capsule_add_rigid_body', False)
        ok, msg, _ = capsule_core.add_capsule_colliders(
            context, obj, bone_names=None, scale=scale, add_rigid_body=add_rb
        )
        if ok:
            self.report({'INFO'}, msg)
            return {'FINISHED'}
        base.alert_error("Capsule Colliders", msg)
        return {'CANCELLED'}


Class_list = [MMR_OT_Add_Capsule_Colliders]
