"""
MMR Rig 升级脚本：复制 MMR_Rig_relative3 为 MMR_Rig_relative4，
并修改为 7 节 spine（至 spine.007）及左右脚分段脚趾骨骼。

用法（无头模式，脚本与 MMR_Rig.blend 同目录）:
  blender MMR_Rig.blend --background --python upgrade_mmr_rig_to_relative4.py

或在 Blender 中打开 MMR_Rig.blend，在文本编辑器中打开并运行此脚本。
运行后请保存 MMR_Rig.blend。若要让 MMR 插件使用新骨架，请将
MikuMikuRig/mmr_operators/rig.py 中的 rigify_arm_name 改为 "MMR_Rig_relative4"。
"""

import bpy
import mathutils

SOURCE_OBJ = "MMR_Rig_relative3"
TARGET_OBJ = "MMR_Rig_relative4"

# 脚趾名称（与 preset.py / rig.py 一致）：每脚 5 根，每根 2 节
TOE_NAMES_L = [
    ("toe_thumb.01.L", "toe_thumb.02.L"),
    ("toe_index.01.L", "toe_index.02.L"),
    ("toe_middle.01.L", "toe_middle.02.L"),
    ("toe_ring.01.L", "toe_ring.02.L"),
    ("toe_pinky.01.L", "toe_pinky.02.L"),
]
TOE_NAMES_R = [
    ("toe_thumb.01.R", "toe_thumb.02.R"),
    ("toe_index.01.R", "toe_index.02.R"),
    ("toe_middle.01.R", "toe_middle.02.R"),
    ("toe_ring.01.R", "toe_ring.02.R"),
    ("toe_pinky.01.R", "toe_pinky.02.R"),
]


def get_armature_object(name):
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "ARMATURE":
        return None
    return obj


def duplicate_armature_as(src_name, dst_name):
    """复制名为 src_name 的 armature 对象为 dst_name，并返回新对象（含独立 data）。"""
    src = get_armature_object(src_name)
    if src is None:
        raise RuntimeError("未找到骨架对象: %s" % src_name)
    # 复制 data（Armature），使 relative4 有独立骨骼数据
    arm_data = src.data.copy()
    new_obj = bpy.data.objects.new(dst_name, arm_data)
    new_obj.matrix_world = src.matrix_world.copy()
    # 链接到与源对象相同的集合，或主场景集合
    linked = False
    for coll in bpy.data.collections:
        if src.name in coll.objects:
            coll.objects.link(new_obj)
            linked = True
            break
    if not linked:
        bpy.context.scene.collection.objects.link(new_obj)
    return new_obj


def add_spine_005_007(arm_data):
    """在 Edit Mode 下为 arm_data 添加 spine.005 和 spine.007。"""
    bones = arm_data.edit_bones
    sp4 = bones.get("spine.004")
    sp6 = bones.get("spine.006")
    if not sp4 or not sp6:
        raise RuntimeError("缺少 spine.004 或 spine.006，请确保源骨架为 MMR metarig")

    # 插入 spine.005：spine.004 -> spine.005 -> spine.006
    sp5 = bones.new("spine.005")
    sp5.head = sp4.tail.copy()
    sp5.tail = sp6.head.copy()
    sp5.parent = sp4
    sp5.use_connect = True
    # 将 spine.006 的父级改为 spine.005（保持 head 位置不变）
    sp6.parent = sp5
    sp6.use_connect = True

    # 添加 spine.007：spine.006 -> spine.007（头骨）
    sp7 = bones.new("spine.007")
    sp7.head = sp6.tail.copy()
    length = sp4.length * 3.0
    sp7.tail = sp7.head + mathutils.Vector((0, 0, length))
    sp7.parent = sp6
    sp7.use_connect = True
    # 原 spine.006 的 tail 在代码里会接到 spine.007.head，这里已连接，无需改


def add_toe_bones(arm_data, side, toe_names_list, foot_name, toe_parent_name):
    """为一只脚添加 5 根脚趾、每根 2 节，父级为 toe_parent（toe.L / toe.R）。"""
    bones = arm_data.edit_bones
    foot = bones.get(foot_name)
    toe_parent = bones.get(toe_parent_name)
    if not foot or not toe_parent:
        return
    # 以 toe 的 head 为基准，用 foot 长度做比例
    base = toe_parent.head.copy()
    foot_len = foot.length
    seg1_len = max(foot_len * 0.15, 0.02)
    seg2_len = max(foot_len * 0.1, 0.01)
    # 沿 -Y 为趾尖方向；X 方向略展开五根趾
    dx_step = foot_len * 0.03
    start_dx = -2 * dx_step  # 从中间往两侧
    dir_y = mathutils.Vector((0, -1, 0))
    dir_z = mathutils.Vector((0, 0, 1))
    for i, (name_01, name_02) in enumerate(toe_names_list):
        dx = start_dx + i * dx_step
        if side == "R":
            dx = -dx
        head_01 = base + mathutils.Vector((dx, 0, 0))
        tail_01 = head_01 + dir_y * seg1_len
        # .01
        eb01 = bones.new(name_01)
        eb01.head = head_01
        eb01.tail = tail_01
        eb01.parent = toe_parent
        eb01.use_connect = False
        # .02
        eb02 = bones.new(name_02)
        eb02.head = tail_01
        eb02.tail = tail_01 + dir_y * seg2_len
        eb02.parent = eb01
        eb02.use_connect = True


def run():
    if get_armature_object(TARGET_OBJ) is not None:
        print("已存在 %s，请先删除或重命名后再运行" % TARGET_OBJ)
        return

    # 1) 复制对象
    new_obj = duplicate_armature_as(SOURCE_OBJ, TARGET_OBJ)
    arm_data = new_obj.data

    # 2) 进入新对象的 Edit Mode（需先选中并设为 active）
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    new_obj.select_set(True)
    bpy.context.view_layer.objects.active = new_obj
    bpy.ops.object.mode_set(mode="EDIT")

    # 3) 添加 spine.005、spine.007
    add_spine_005_007(arm_data)

    # 4) 添加左右脚趾骨骼（全部为 toe.L / toe.R 的子骨骼）
    add_toe_bones(arm_data, "L", TOE_NAMES_L, "foot.L", "toe.L")
    add_toe_bones(arm_data, "R", TOE_NAMES_R, "foot.R", "toe.R")

    bpy.ops.object.mode_set(mode="OBJECT")

    # 可选：若当前打开的是 MMR_Rig.blend 且已保存过，则自动保存
    if bpy.data.filepath and bpy.data.is_dirty:
        try:
            bpy.ops.wm.save_mainfile()
            print("已保存: %s" % bpy.data.filepath)
        except Exception as e:
            print("保存失败（可手动保存）: %s" % e)

    print("完成: %s 已创建（7 节 spine + 左右脚趾骨骼）" % TARGET_OBJ)


if __name__ == "__main__":
    run()
