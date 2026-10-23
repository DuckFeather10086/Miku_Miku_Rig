"""Native Asset Browser integration for MMR FK poses."""
import bpy
from bpy.props import StringProperty, BoolProperty
from . import assets, rig_adapter


class MMR_OT_Pose_Asset_Save(bpy.types.Operator):
    bl_idname = 'mmr.pose_asset_save'
    bl_label = '保存 FK 姿势资产'
    bl_description = '临时匹配 FK，保存官方姿势资产和缩略图，恢复当前姿势；同名另存新资产'
    pose_name: StringProperty(name='名称', default='新姿势')
    category: StringProperty(name='分类', default='通用姿势')

    def execute(self, context):
        try:
            action, path = assets.save_asset(context, self.pose_name, self.category)
        except (ValueError, RuntimeError, OSError, KeyError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        context.scene.mmr_property.pose_asset_category = self.category
        refresh_browsers(context)
        self.report({'INFO'}, '已保存姿势资产: ' + str(path))
        return {'FINISHED'}

    def invoke(self, context, event):
        self.category = context.scene.mmr_property.pose_asset_category
        return context.window_manager.invoke_props_dialog(self)


def selected_asset(context):
    # asset is a context member supplied only by asset editors/shelves.
    if getattr(context, 'asset', None):
        return context.asset
    # N-panel actions use the selection in an already-open native Asset Browser.
    for area in context.screen.areas:
        if area.type == 'FILE_BROWSER' and area.ui_type == 'ASSETS':
            region = next(r for r in area.regions if r.type == 'WINDOW')
            with context.temp_override(area=area, region=region):
                if getattr(context, 'asset', None):
                    return context.asset
    raise rig_adapter.PoseAssetError('请先在官方资产浏览器选中一个 MMR FK 姿势资产')


class MMR_OT_Pose_Asset_Apply(bpy.types.Operator):
    bl_idname = 'mmr.pose_asset_apply'
    bl_label = 'MMR · FK 应用姿势'
    bl_description = '应用选中的 MMR 姿势资产；保持体型和根骨位置，按身高适配身体位移'
    bl_options = {'REGISTER', 'UNDO'}
    adapt_translation: BoolProperty(name='按身高适配身体位移', default=True)

    def execute(self, context):
        loaded = None
        try:
            rig = rig_adapter.require_rig(context)
            asset = selected_asset(context)
            if asset.id_type != 'ACTION':
                raise rig_adapter.PoseAssetError('请选择姿势 Action 资产')
            action = asset.local_id
            if action is None:
                loaded = action = assets.load_action(asset.full_library_path, asset.name)
            assets.apply_action(context, rig, action, adapt_translation=self.adapt_translation)
        except (ValueError, RuntimeError, OSError, KeyError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        finally:
            if loaded:
                bpy.data.actions.remove(loaded)
        self.report({'INFO'}, '已按 FK 应用；需要时点击“对齐并切到 IK”微调')
        return {'FINISHED'}


class MMR_OT_Pose_Asset_IK(bpy.types.Operator):
    bl_idname = 'mmr.pose_asset_ik'
    bl_label = '对齐并切到 IK'
    bl_description = '使用本角色的 Rigify 匹配，把手脚控制器对齐到当前 FK 姿势，再切换 IK'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            rig = rig_adapter.require_rig(context)
            limbs = rig_adapter.snap_definitions(rig)
            with rig_adapter.pose_operation(context, rig):
                rig_adapter.switch_to_ik(context, rig, limbs)
        except (ValueError, RuntimeError, KeyError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


def refresh_browsers(context):
    for area in context.screen.areas:
        if area.type == 'FILE_BROWSER' and area.ui_type == 'ASSETS':
            region = next(r for r in area.regions if r.type == 'WINDOW')
            with context.temp_override(area=area, region=region):
                bpy.ops.asset.library_refresh()
            area.tag_redraw()


class MMR_OT_Pose_Asset_Browse(bpy.types.Operator):
    bl_idname = 'mmr.pose_asset_browse'
    bl_label = '浏览官方姿势资产'
    bl_description = '打开独立官方资产浏览器，自动定位 MMR Poses 库'

    def execute(self, context):
        try:
            library = assets.register_library(context, assets.library_directory(context))
            bpy.ops.wm.window_new()
            window = context.window_manager.windows[-1]
            area = max(window.screen.areas, key=lambda a: a.width * a.height)
            area.type = 'FILE_BROWSER'
            area.ui_type = 'ASSETS'
            # File Browser parameters initialize on the next UI update.
            def configure():
                params = area.spaces.active.params
                if params is None:
                    return 0.1
                params.asset_library_reference = library.name
                params.filter_search = ''
                area.tag_redraw()
                return None
            bpy.app.timers.register(configure, first_interval=0.1)
        except (ValueError, RuntimeError, OSError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


def draw_asset_menu(self, context):
    asset = getattr(context, 'asset', None)
    if asset and asset.id_type == 'ACTION':
        self.layout.separator()
        self.layout.operator('mmr.pose_asset_apply', icon='POSE_HLT')


def draw_asset_header(self, context):
    if context.space_data.browse_mode == 'ASSETS':
        self.layout.operator('mmr.pose_asset_apply', text='MMR · FK 应用', icon='POSE_HLT')


CLASSES = (MMR_OT_Pose_Asset_Save, MMR_OT_Pose_Asset_Apply, MMR_OT_Pose_Asset_IK, MMR_OT_Pose_Asset_Browse)
