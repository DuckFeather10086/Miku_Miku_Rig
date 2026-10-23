# Pose library: save/load Rigify poses as JSONL
import bpy

from . import operators
from . import panels
from . import asset_operators


def register():
    for cls in operators.Class_list:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(panels.MMR_PT_Pose_Library)
    for cls in asset_operators.CLASSES:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(panels.MMR_PT_Pose_Assets)
    bpy.types.ASSETBROWSER_MT_context_menu.append(asset_operators.draw_asset_menu)
    bpy.types.FILEBROWSER_HT_header.append(asset_operators.draw_asset_header)


def unregister():
    bpy.types.FILEBROWSER_HT_header.remove(asset_operators.draw_asset_header)
    bpy.types.ASSETBROWSER_MT_context_menu.remove(asset_operators.draw_asset_menu)
    bpy.utils.unregister_class(panels.MMR_PT_Pose_Assets)
    for cls in reversed(asset_operators.CLASSES):
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(panels.MMR_PT_Pose_Library)
    for cls in reversed(operators.Class_list):
        bpy.utils.unregister_class(cls)
