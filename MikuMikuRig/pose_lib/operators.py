# Pose library operators
import bpy
from bpy.props import StringProperty
from . import core
from .. import base


class MMR_OT_Pose_Lib_Save(bpy.types.Operator):
    bl_idname = "mmr.pose_lib_save"
    bl_label = "Save Pose"
    bl_options = {'REGISTER', 'UNDO'}

    pose_name: StringProperty(name="Pose Name", default="", description="Name for this pose")

    def execute(self, context):
        scene = context.scene
        mmr = scene.mmr_property
        sync = getattr(mmr, 'pose_save_sync_ik_fk', True)
        ok, msg = core.save_pose(context, self.pose_name, sync_ik_fk=sync)
        if ok:
            self.report({'INFO'}, msg)
            return {'FINISHED'}
        base.alert_error("Pose Library", msg)
        return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'pose_name')
        layout.prop(context.scene.mmr_property, 'pose_save_sync_ik_fk', text="Sync FK/IK before save")


class MMR_OT_Pose_Lib_Load(bpy.types.Operator):
    bl_idname = "mmr.pose_lib_load"
    bl_label = "Load Pose"
    bl_options = {'REGISTER', 'UNDO'}

    pose_name: StringProperty(name="Pose Name", default="")

    def execute(self, context):
        ok, msg = core.load_pose(context, self.pose_name)
        if ok:
            self.report({'INFO'}, msg)
            return {'FINISHED'}
        base.alert_error("Pose Library", msg)
        return {'CANCELLED'}


class MMR_OT_Pose_Lib_Delete(bpy.types.Operator):
    bl_idname = "mmr.pose_lib_delete"
    bl_label = "Delete Pose"
    bl_options = {'REGISTER', 'UNDO'}

    pose_name: StringProperty(name="Pose Name", default="")

    def execute(self, context):
        ok, msg = core.delete_pose_from_library(context, self.pose_name)
        if ok:
            self.report({'INFO'}, msg)
            return {'FINISHED'}
        base.alert_error("Pose Library", msg)
        return {'CANCELLED'}


Class_list = [
    MMR_OT_Pose_Lib_Save,
    MMR_OT_Pose_Lib_Load,
    MMR_OT_Pose_Lib_Delete,
]
