import bpy

bl_info = {
    "name": "MikuMikuRig",
    "author": "William",
    "version": (0, 5, 7, 0),
    "blender": (5, 0, 0),
    "location": "3DView > Tools",
    "description": "快速为各种人形模型生成rigify控制器,一键套mixamo动作",
    "support": 'COMMUNITY',
    "category": "Rigging",
}

from . import base
from . import settings
from . import rig
from . import pose_lib
from . import physics
from . import mmr_operators
from . import translation


# Panels (Rig, Extra, About); animation and cloth panels removed
class MikuMikuRig_1(base.Mmr_Panel_Base):
    bl_idname = "MMR_PT_panel_1"
    bl_label = "Auto MMD rig"

    def draw(self, context):
        scene = context.scene
        mmr_property = scene.mmr_property
        layout = self.layout
        layout.label(text="Select armature then press the button")
        layout.operator("mmr.rig_preset", text="Generate MMD rig")
        layout.prop(mmr_property, 'bent_IK_bone', text="Bent IK bone")
        layout.prop(mmr_property, 'wrist_rotation_follow', text="Wrist rotation follow arm")
        layout.prop(mmr_property, 'auto_shoulder', text="Shoulder IK")
        layout.prop(mmr_property, 'solid_rig', text="Replace the controller")
        layout.prop(mmr_property, 'pole_target', text="Use pole target")


class MikuMikuRig_2(base.Mmr_Panel_Base):
    bl_idname = "MMR_PT_panel_2"
    bl_label = "Extra"

    def draw(self, context):
        scene = context.scene
        mmr_property = scene.mmr_property
        layout = self.layout
        layout.prop(mmr_property, 'min_ik_loop', text="Min IK loop")
        layout.operator("mmr.set_min_ik_loop", text="Set min IK loop")


class MikuMikuRig_5(base.Mmr_Panel_Base):
    bl_idname = "MMR_PT_panel_5"
    bl_label = "About"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        mmr_property = scene.mmr_property
        layout = self.layout
        layout.label(text="MikuMikuRig")
        layout.label(text="版本号:" + str(bl_info["version"]))
        layout.label(text="作者:小威廉伯爵")
        layout.prop(mmr_property, 'debug', text="Debug")


_panel_classes = (MikuMikuRig_1, MikuMikuRig_2, MikuMikuRig_5)

modules_to_register = (
    base,
    settings,
    rig,
    pose_lib,
    physics,
    mmr_operators,
    translation,
)


def register():
    for module in modules_to_register:
        module.register()
    for cls in _panel_classes:
        bpy.utils.register_class(cls)
    print(f"Registered: {bl_info['name']} version {bl_info['version']}")


def unregister():
    for cls in reversed(_panel_classes):
        bpy.utils.unregister_class(cls)
    for module in reversed(modules_to_register):
        module.unregister()
    print(f"Unregistered: {bl_info['name']}")
