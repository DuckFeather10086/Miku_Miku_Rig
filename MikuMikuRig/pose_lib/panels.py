# Pose library UI panel
import bpy
from .. import base
from . import core


class MMR_PT_Pose_Library(base.Mmr_Panel_Base):
    bl_idname = "MMR_PT_pose_library"
    bl_label = "旧 JSONL 姿势库"
    bl_options = {'DEFAULT_CLOSED'}
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
                row.label(text=name, icon='POSE_HLT')
                op_load = row.operator("mmr.pose_lib_load", text="Load")
                op_load.pose_name = name
                op_del = row.operator("mmr.pose_lib_delete", text="", icon='TRASH')
                op_del.pose_name = name


class MMR_PT_Pose_Assets(base.Mmr_Panel_Base):
    bl_idname = "MMR_PT_pose_assets"
    bl_label = "官方姿势资产 · MMR"
    bl_context = ""

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.mmr_property, 'pose_asset_directory')
        layout.operator('mmr.pose_asset_save', icon='ASSET_MANAGER')
        layout.operator('mmr.pose_asset_browse', icon='ASSET_MANAGER')
        layout.operator('mmr.pose_asset_apply', icon='POSE_HLT')
        layout.operator('mmr.pose_asset_ik', icon='CON_KINEMATIC')
        layout.label(text='FK 套姿势，IK 微调手脚落点')
