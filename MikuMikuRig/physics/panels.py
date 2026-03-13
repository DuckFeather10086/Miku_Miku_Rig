# Capsule colliders panel
import bpy
from .. import base


class MMR_PT_Capsule_Colliders(base.Mmr_Panel_Base):
    bl_idname = "MMR_PT_capsule_colliders"
    bl_label = "Capsule Colliders"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Select armature, then add capsules")
        op = layout.operator("mmr.add_capsule_colliders", text="Generate Capsule Colliders", icon='MESH_CAPSULE')
        layout.prop(context.scene.mmr_property, "capsule_scale", text="Scale")
        layout.prop(context.scene.mmr_property, "capsule_add_rigid_body", text="Add Rigid Body (passive)")
