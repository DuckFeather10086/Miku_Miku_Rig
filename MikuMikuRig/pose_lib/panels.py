# Pose library UI panel
import bpy
from .. import base
from . import core


class MMR_PT_Pose_Library(base.Mmr_Panel_Base):
    bl_idname = "MMR_PT_pose_library"
    bl_label = "Pose Library"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mmr = scene.mmr_property
        layout.prop(mmr, 'pose_lib_directory', text="Directory")
        layout.separator()
        layout.operator("mmr.pose_lib_save", text="Save Pose", icon='FILE_TICK')
        layout.separator()
        poses = core.list_poses(context)
        if not poses:
            layout.label(text="No poses in library")
        else:
            for name, _arm_name in poses:
                row = layout.row(align=True)
                row.label(text=name, icon='POSE_DATA')
                op_load = row.operator("mmr.pose_lib_load", text="Load")
                op_load.pose_name = name
                op_del = row.operator("mmr.pose_lib_delete", text="", icon='TRASH')
                op_del.pose_name = name
