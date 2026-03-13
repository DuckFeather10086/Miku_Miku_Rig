# MikuMikuRig settings: Scene property group and addon preferences
import os
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty


def _get_rig_preset_items(self, context):
    """Lazy import to avoid circular dependency."""
    from . import rig
    return rig.preset.get_rig_preset_item(self, context)




def get_pose_library_default_directory():
    """Default pose library directory under addon."""
    addon_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(addon_dir, "pose_library")


class MMR_property(bpy.types.PropertyGroup):
    # Rig options
    upper_body_controller: BoolProperty(default=True, description="上半身控制器")
    wrist_rotation_follow: BoolProperty(default=False, description="手腕旋转跟随手臂")
    bent_IK_bone: BoolProperty(default=False, description="弯曲IK骨骼")
    auto_shoulder: BoolProperty(default=False, description="肩膀联动")
    solid_rig: BoolProperty(default=False, description="实心控制器")
    pole_target: BoolProperty(default=False, description="极向目标")
    extra_source_controllers: BoolProperty(default=False, description="为额外源骨骼生成简易控制器")
    min_ik_loop: IntProperty(default=10, description="最小IK迭代次数", min=1)
    rig_preset_name: EnumProperty(
        items=_get_rig_preset_items,
        description="Choose the preset you want to use",
    )
    quick_assign_index: IntProperty(default=1, description="快速指定序号", min=1)
    quick_assign_mod: BoolProperty(default=False, description="快速指定模式")
    extra_options1: BoolProperty(default=False, description="高级选项")
    extra_options2: BoolProperty(default=False, description="高级选项")
    debug: BoolProperty(default=False, description="Debug")
    mass_multiply_rate: FloatProperty(default=12.5, description="刚体质量倍率", min=0)  # kept until physics/extra cleanup
    capsule_scale: FloatProperty(name="Capsule scale", default=1.0, min=0.1, max=5.0)
    capsule_add_rigid_body: BoolProperty(name="Add Rigid Body", default=False)

    # Pose library
    pose_lib_directory: StringProperty(
        name="Pose library directory",
        description="Directory for saving/loading pose library (JSONL)",
        default="",
        subtype='DIR_PATH',
    )
    pose_save_sync_ik_fk: BoolProperty(
        name="Sync FK/IK before save",
        description="When saving a pose, sync the active limb (FK/IK) so both represent the same pose, then save",
        default=True,
    )


_classes = (MMR_property,)


def register():
    for c in _classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.mmr_property = bpy.props.PointerProperty(type=MMR_property)


def unregister():
    del bpy.types.Scene.mmr_property
    for c in reversed(_classes):
        bpy.utils.unregister_class(c)
