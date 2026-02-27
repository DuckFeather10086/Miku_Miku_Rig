#!/usr/bin/env python3
"""
修复MMR_Rig.blend中toe_thumb.01骨骼的轴向
确保toe_thumb_master的Y轴是垂直方向（Z方向），这样伸缩时会纵向旋转
"""
import bpy
import os
import math
import mathutils
from mathutils import Vector, Matrix

script_dir = os.path.dirname(os.path.abspath(__file__))
mmr_rig_file = os.path.join(script_dir, "MikuMikuRig", "mmr_operators", "MMR_Rig.blend")
# 确保路径正确
if not os.path.exists(mmr_rig_file):
    # 尝试相对路径
    mmr_rig_file = "MikuMikuRig/mmr_operators/MMR_Rig.blend"

bpy.ops.wm.open_mainfile(filepath=mmr_rig_file)

# 查找MMR_Rig_relative4
rig = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE' and 'MMR_Rig_relative4' in obj.name:
        rig = obj
        break

if not rig:
    print("未找到MMR_Rig_relative4")
    exit(1)

print(f"Rig名称: {rig.name}")
print("\n修复toe_thumb.01骨骼的轴向:")

bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')

# 查找toe_thumb.01.L和toe_thumb.01.R
toe_thumb_bones = ['toe_thumb.01.L', 'toe_thumb.01.R']

for name in toe_thumb_bones:
    edit_bone = rig.data.edit_bones.get(name)
    if not edit_bone:
        print(f"  ✗ {name} 不存在")
        continue
    
    print(f"\n  {name}")
    print(f"    - 当前Roll: {round(edit_bone.roll, 4)}")
    
    # 计算骨骼方向
    bone_dir = (edit_bone.tail - edit_bone.head).normalized()
    print(f"    - 骨骼方向: {tuple(round(v,4) for v in bone_dir)}")
    
    # 目标：Y轴应该是垂直方向（Z方向）
    # 对于脚趾，骨骼方向通常是向下的（Y负方向）
    # Y轴应该是向上的（Z正方向）
    
    # 计算目标Y轴（垂直向上）
    target_y = Vector((0, 0, 1))
    # 确保Y轴垂直于骨骼方向
    target_y = target_y - (target_y.dot(bone_dir)) * bone_dir
    if target_y.length < 0.001:
        # 如果骨骼方向已经是垂直的，使用X方向
        target_y = Vector((1, 0, 0)) - (Vector((1, 0, 0)).dot(bone_dir)) * bone_dir
    target_y.normalize()
    
    # 计算目标X轴 = 骨骼方向 × 目标Y
    target_x = bone_dir.cross(target_y)
    target_x.normalize()
    
    # 计算当前X轴
    # 使用GLOBAL_NEG_Y方式计算roll
    # 这会让Y轴指向-Y方向（向下），但我们需要Y轴向上
    # 所以需要旋转180度
    
    # 先计算一个参考X轴
    if abs(bone_dir.z) > 0.9:
        ref = Vector((1, 0, 0))
    else:
        ref = Vector((0, 0, 1))
    
    current_x_ref = ref.cross(bone_dir)
    if current_x_ref.length < 0.001:
        ref = Vector((0, 1, 0))
        current_x_ref = ref.cross(bone_dir)
    current_x_ref.normalize()
    
    # 应用当前roll
    roll_matrix = Matrix.Rotation(edit_bone.roll, 4, bone_dir)
    current_x = roll_matrix @ current_x_ref
    current_x = current_x - (current_x.dot(bone_dir)) * bone_dir
    current_x.normalize()
    
    # 计算从当前X到目标X的角度
    dot = current_x.dot(target_x)
    # 限制在[-1, 1]范围内
    dot = max(-1.0, min(1.0, dot))
    angle = math.acos(dot)
    
    # 检查方向
    cross = current_x.cross(target_x)
    if cross.dot(bone_dir) < 0:
        angle = -angle
    
    new_roll = edit_bone.roll + angle
    
    print(f"    - 需要调整的角度: {round(angle, 4)}")
    print(f"    - 新Roll: {round(new_roll, 4)}")
    
    # 应用新roll
    edit_bone.roll = new_roll
    
    # 验证
    roll_matrix = Matrix.Rotation(edit_bone.roll, 4, bone_dir)
    new_x = roll_matrix @ current_x_ref
    new_x = new_x - (new_x.dot(bone_dir)) * bone_dir
    new_x.normalize()
    new_y = bone_dir.cross(new_x)
    new_y.normalize()
    
    print(f"    - 修复后Y轴: {tuple(round(v,4) for v in new_y)}")
    y_z = abs(new_y.z)
    print(f"    - Y轴Z分量: {round(y_z, 4)}")
    
    if y_z > 0.7:
        print(f"    ✓ Y轴已调整为垂直方向")
    else:
        print(f"    ⚠ Y轴调整可能不够")

# 保存文件
print("\n保存MMR_Rig.blend...")
bpy.ops.wm.save_mainfile(filepath=mmr_rig_file)
print("✓ 文件已保存")
