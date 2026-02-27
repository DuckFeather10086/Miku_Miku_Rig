#!/usr/bin/env python3
"""
脚趾无头Blender回归验证脚本
用法: blender --background --python verify_toe_regression.py
或者: blender chisaBody5.blend --background --python verify_toe_regression.py
"""

import bpy
import sys
import os
import math
import mathutils
from mathutils import Vector, Matrix

# 设置blend文件路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 优先检查rigged文件，如果不存在则检查原始文件
rigged_file = os.path.join(script_dir, "MikuMikuRig", "mmr_operators", "chisaBody5_rigged.blend")
blend_file = os.path.join(script_dir, "MikuMikuRig", "mmr_operators", "chisaBody5.blend")
# 如果rigged文件存在，使用rigged文件；否则使用原始文件
if os.path.exists(rigged_file):
    blend_file = rigged_file

# 脚趾骨骼名称定义
# 源骨骼中的实际名称（Genesis9等）
SOURCE_TOE_BASE_NAMES = ['l_toes', 'r_toes', 'toe.L', 'toe.R']  # 支持多种命名
SOURCE_TOE_SEGMENT_NAMES = [
    'l_bigtoe1', 'l_bigtoe2', 'l_indextoe1', 'l_indextoe2',
    'l_midtoe1', 'l_midtoe2', 'l_ringtoe1', 'l_ringtoe2',
    'l_pinkytoe1', 'l_pinkytoe2',
    'r_bigtoe1', 'r_bigtoe2', 'r_indextoe1', 'r_indextoe2',
    'r_midtoe1', 'r_midtoe2', 'r_ringtoe1', 'r_ringtoe2',
    'r_pinkytoe1', 'r_pinkytoe2',
    # 也支持rigify命名
    'toe_thumb.01.L', 'toe_thumb.02.L',
    'toe_index.01.L', 'toe_index.02.L',
    'toe_middle.01.L', 'toe_middle.02.L',
    'toe_ring.01.L', 'toe_ring.02.L',
    'toe_pinky.01.L', 'toe_pinky.02.L',
    'toe_thumb.01.R', 'toe_thumb.02.R',
    'toe_index.01.R', 'toe_index.02.R',
    'toe_middle.01.R', 'toe_middle.02.R',
    'toe_ring.01.R', 'toe_ring.02.R',
    'toe_pinky.01.R', 'toe_pinky.02.R',
]

# Rig中的rigify骨骼名称
RIG_TOE_BASE_NAMES = ['toe.L', 'toe.R']
RIG_TOE_SEGMENT_NAMES = [
    'toe_thumb.01.L', 'toe_thumb.02.L',
    'toe_index.01.L', 'toe_index.02.L',
    'toe_middle.01.L', 'toe_middle.02.L',
    'toe_ring.01.L', 'toe_ring.02.L',
    'toe_pinky.01.L', 'toe_pinky.02.L',
    'toe_thumb.01.R', 'toe_thumb.02.R',
    'toe_index.01.R', 'toe_index.02.R',
    'toe_middle.01.R', 'toe_middle.02.R',
    'toe_ring.01.R', 'toe_ring.02.R',
    'toe_pinky.01.R', 'toe_pinky.02.R',
]
TOE_IK_NAMES = ['ToeTipIK_L', 'ToeTipIK_R']
TOE_PARENT_HELPER_NAMES = ['toe.L_parent', 'toe.R_parent', 'ToeTipIK_L_parent', 'ToeTipIK_R_parent']

def load_blend_file(filepath):
    """加载blend文件"""
    print("=" * 60)
    print(f"加载blend文件: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"✗ 文件不存在: {filepath}")
        return False
    
    try:
        # 检查文件是否已经打开
        current_file = bpy.data.filepath
        if current_file and os.path.exists(current_file):
            try:
                if os.path.samefile(current_file, filepath):
                    print(f"✓ 文件已经打开: {os.path.basename(filepath)}")
                    return True
            except (OSError, ValueError):
                # samefile可能失败，继续加载
                pass
        
        # 如果文件已经打开但不是目标文件，先清除场景
        if current_file:
            bpy.ops.wm.read_homefile(app_template="")
        
        # 加载blend文件
        bpy.ops.wm.open_mainfile(filepath=filepath)
        print(f"✓ 文件加载成功")
        return True
    except Exception as e:
        print(f"✗ 加载文件失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_armatures():
    """查找源骨骼和生成的rig"""
    print("=" * 60)
    print("查找骨骼对象...")
    
    mmd_arm = None
    rig_arm = None
    
    # 查找源骨骼（通常是 Genesis 9）
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            if obj.name == 'Genesis 9' or 'Genesis' in obj.name:
                if '_Rig' not in obj.name:
                    mmd_arm = obj
                    print(f"✓ 找到源骨骼: {mmd_arm.name}")
                    break
    
    # 查找生成的rig（通常包含 _Rig）
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and '_Rig' in obj.name:
            rig_arm = obj
            print(f"✓ 找到生成的rig: {rig_arm.name}")
            break
    
    if not mmd_arm:
        print("⚠ 未找到源骨骼，列出所有armature对象:")
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                print(f"  - {obj.name}")
    
    if not rig_arm:
        print("⚠ 未找到生成的rig，可能文件尚未生成rig")
    
    return mmd_arm, rig_arm

def check_source_toe_bones(mmd_arm):
    """检查源骨骼中的脚趾骨骼"""
    print("=" * 60)
    print("检查源骨骼中的脚趾骨骼...")
    
    if not mmd_arm:
        print("✗ 源骨骼不存在，跳过检查")
        return False
    
    all_passed = True
    
    # 检查基础脚趾骨骼（支持多种命名）
    print("\n[基础脚趾骨骼]")
    found_base_toes = []
    for toe_name in SOURCE_TOE_BASE_NAMES:
        if toe_name in mmd_arm.pose.bones:
            found_base_toes.append(toe_name)
            print(f"  ✓ {toe_name} 存在")
    
    if not found_base_toes:
        print("  ✗ 未找到基础脚趾骨骼（l_toes/r_toes 或 toe.L/toe.R）")
        all_passed = False
    elif len(found_base_toes) < 2:
        print(f"  ⚠ 只找到 {len(found_base_toes)} 个基础脚趾骨骼，期望2个")
        all_passed = False
    
    # 检查分段脚趾骨骼（可选）
    print("\n[分段脚趾骨骼（可选）]")
    found_segments = []
    for toe_name in SOURCE_TOE_SEGMENT_NAMES:
        if toe_name in mmd_arm.pose.bones:
            found_segments.append(toe_name)
    
    if found_segments:
        print(f"  ✓ 找到 {len(found_segments)} 个分段脚趾骨骼")
        for name in sorted(found_segments)[:10]:  # 显示前10个
            print(f"    - {name}")
        if len(found_segments) > 10:
            print(f"    ... 还有 {len(found_segments) - 10} 个")
    else:
        print(f"  ⚠ 未找到分段脚趾骨骼（这是可选的）")
    
    return all_passed

def check_source_toe_constraints(mmd_arm):
    """检查源骨骼中脚趾的约束"""
    print("=" * 60)
    print("检查源骨骼中脚趾的约束...")
    
    if not mmd_arm:
        print("✗ 源骨骼不存在，跳过检查")
        return False
    
    all_passed = True
    
    # 查找实际存在的脚趾骨骼
    found_toe_bones = []
    for toe_name in SOURCE_TOE_BASE_NAMES:
        if toe_name in mmd_arm.pose.bones:
            found_toe_bones.append(toe_name)
    
    if not found_toe_bones:
        print("  ✗ 未找到脚趾骨骼，无法检查约束")
        return False
    
    for toe_name in found_toe_bones:
        pb = mmd_arm.pose.bones.get(toe_name)
        if not pb:
            continue
        
        # 查找 rel_ 开头的约束
        rel_constraints = [c for c in pb.constraints if c.name.startswith('rel_')]
        
        if rel_constraints:
            print(f"  ✓ {toe_name} 有 {len(rel_constraints)} 个 rel 约束:")
            for c in rel_constraints:
                subtarget = getattr(c, 'subtarget', '')
                print(f"    - {c.name} ({c.type}) -> {subtarget}")
        else:
            print(f"  ⚠ {toe_name} 没有 rel 约束（如果rig已生成，这是正常的）")
    
    return all_passed

def check_rig_toe_bones(rig_arm):
    """检查rig中的脚趾骨骼"""
    print("=" * 60)
    print("检查生成的rig中的脚趾骨骼...")
    
    if not rig_arm:
        print("✗ Rig不存在，跳过检查")
        return False
    
    all_passed = True
    
    # 检查基础脚趾控制器
    print("\n[基础脚趾控制器]")
    for toe_name in RIG_TOE_BASE_NAMES:
        if toe_name in rig_arm.pose.bones:
            print(f"  ✓ {toe_name} 控制器存在")
        else:
            print(f"  ✗ {toe_name} 控制器不存在")
            all_passed = False
    
    # 检查DEF脚趾骨骼
    print("\n[DEF脚趾骨骼]")
    def_toe_names = [f'DEF-{name}' for name in RIG_TOE_BASE_NAMES]
    for def_name in def_toe_names:
        if def_name in rig_arm.pose.bones:
            print(f"  ✓ {def_name} 存在")
        else:
            print(f"  ✗ {def_name} 不存在")
            all_passed = False
    
    # 检查分段DEF脚趾骨骼
    print("\n[DEF分段脚趾骨骼]")
    def_segment_names = [f'DEF-{name}' for name in RIG_TOE_SEGMENT_NAMES]
    found_def_segments = []
    for def_name in def_segment_names:
        if def_name in rig_arm.pose.bones:
            found_def_segments.append(def_name)
    
    if found_def_segments:
        print(f"  ✓ 找到 {len(found_def_segments)} 个DEF分段脚趾骨骼")
        for name in sorted(found_def_segments)[:10]:
            print(f"    - {name}")
        if len(found_def_segments) > 10:
            print(f"    ... 还有 {len(found_def_segments) - 10} 个")
    else:
        print(f"  ⚠ 未找到DEF分段脚趾骨骼（这是可选的）")
    
    # 检查ToeTipIK控制器
    print("\n[ToeTipIK控制器]")
    for ik_name in TOE_IK_NAMES:
        if ik_name in rig_arm.pose.bones:
            print(f"  ✓ {ik_name} 控制器存在")
        else:
            print(f"  ⚠ {ik_name} 控制器不存在（这是可选的）")
    
    return all_passed

def check_rig_toe_parent_helpers(rig_arm):
    """检查rig中的脚趾父级辅助骨骼"""
    print("=" * 60)
    print("检查rig中的脚趾父级辅助骨骼...")
    
    if not rig_arm:
        print("✗ Rig不存在，跳过检查")
        return False
    
    all_passed = True
    
    for parent_name in TOE_PARENT_HELPER_NAMES:
        if parent_name in rig_arm.data.bones:
            print(f"  ✓ {parent_name} 存在")
        else:
            print(f"  ✗ {parent_name} 不存在")
            all_passed = False
    
    return all_passed

def check_rig_toe_constraints(rig_arm):
    """检查rig中DEF脚趾骨骼的约束"""
    print("=" * 60)
    print("检查rig中DEF脚趾骨骼的约束...")
    
    if not rig_arm:
        print("✗ Rig不存在，跳过检查")
        return False
    
    all_passed = True
    
    # 检查DEF-toe.L和DEF-toe.R的约束
    for toe_name in RIG_TOE_BASE_NAMES:
        def_name = f'DEF-{toe_name}'
        pb = rig_arm.pose.bones.get(def_name)
        if not pb:
            print(f"  ✗ {def_name} 不存在，无法检查约束")
            all_passed = False
            continue
        
        # 查找约束
        constraints = list(pb.constraints)
        if constraints:
            print(f"  ✓ {def_name} 有 {len(constraints)} 个约束:")
            for c in constraints:
                subtarget = getattr(c, 'subtarget', '')
                print(f"    - {c.name} ({c.type}) -> {subtarget}")
        else:
            print(f"  ⚠ {def_name} 没有约束")
    
    # 检查DEF-toe.L和DEF-toe.R是否有ToeTipIK约束
    print("\n[检查ToeTipIK约束]")
    for toe_name in RIG_TOE_BASE_NAMES:
        def_name = f'DEF-{toe_name}'
        pb = rig_arm.pose.bones.get(def_name)
        if not pb:
            continue
        
        # 查找指向ToeTipIK的约束
        ik_constraints = [c for c in pb.constraints 
                         if 'ToeTipIK' in getattr(c, 'subtarget', '')]
        if ik_constraints:
            print(f"  ✓ {def_name} 有ToeTipIK约束")
        else:
            print(f"  ⚠ {def_name} 没有ToeTipIK约束（这是可选的）")
    
    return all_passed

def check_toe_position_alignment(mmd_arm, rig_arm):
    """检查脚趾控制器位置和目标骨骼脚趾位置是否一致"""
    print("=" * 60)
    print("检查脚趾控制器位置和目标骨骼脚趾位置一致性...")
    
    if not mmd_arm or not rig_arm:
        print("✗ 源骨骼或Rig不存在，跳过检查")
        return False
    
    all_passed = True
    tolerance = 0.001  # 位置容差（1mm）
    
    # 映射关系：源骨骼名称 -> rig控制器名称
    # 根据preset.json，Genesis9中 l_toes -> toe.L, r_toes -> toe.R
    position_pairs = [
        ('l_toes', 'toe.L'),
        ('r_toes', 'toe.R'),
    ]
    
    print("\n[位置一致性检查]")
    for source_name, rig_name in position_pairs:
        source_pb = mmd_arm.pose.bones.get(source_name)
        rig_pb = rig_arm.pose.bones.get(rig_name)
        
        if not source_pb:
            print(f"  ⚠ 源骨骼 {source_name} 不存在，跳过")
            continue
        
        if not rig_pb:
            print(f"  ✗ Rig控制器 {rig_name} 不存在")
            all_passed = False
            continue
        
        # 获取位置
        source_pos = source_pb.head.copy()
        rig_pos = rig_pb.head.copy()
        
        # 计算距离
        distance = (source_pos - rig_pos).length
        
        if distance < tolerance:
            print(f"  ✓ {source_name} <-> {rig_name}: 位置一致 (距离: {distance:.6f})")
        else:
            print(f"  ✗ {source_name} <-> {rig_name}: 位置不一致!")
            print(f"      源骨骼位置: ({source_pos.x:.6f}, {source_pos.y:.6f}, {source_pos.z:.6f})")
            print(f"      Rig位置:    ({rig_pos.x:.6f}, {rig_pos.y:.6f}, {rig_pos.z:.6f})")
            print(f"      距离: {distance:.6f} (容差: {tolerance})")
            all_passed = False
    
    # 检查DEF脚趾骨骼位置
    print("\n[DEF脚趾骨骼位置检查]")
    for toe_name in RIG_TOE_BASE_NAMES:
        def_name = f'DEF-{toe_name}'
        def_pb = rig_arm.pose.bones.get(def_name)
        
        if not def_pb:
            continue
        
        # 找到对应的源骨骼
        source_name = None
        if toe_name == 'toe.L':
            source_name = 'l_toes'
        elif toe_name == 'toe.R':
            source_name = 'r_toes'
        
        if source_name:
            source_pb = mmd_arm.pose.bones.get(source_name)
            if source_pb:
                source_pos = source_pb.head.copy()
                def_pos = def_pb.head.copy()
                distance = (source_pos - def_pos).length
                
                if distance < tolerance:
                    print(f"  ✓ {def_name} <-> {source_name}: 位置一致 (距离: {distance:.6f})")
                else:
                    print(f"  ⚠ {def_name} <-> {source_name}: 位置有差异 (距离: {distance:.6f})")
                    # DEF骨骼位置可能略有不同，所以只警告不报错
    
    return all_passed

def check_toe_master_stretch_direction(rig_arm):
    """检查所有toe master缩放时脚趾是否主要沿垂直方向运动"""
    print("=" * 60)
    print("检查所有toe_master缩放方向（垂直性）...")
    
    if not rig_arm:
        print("✗ Rig不存在，跳过检查")
        return False
    
    all_passed = True
    # master -> driven toe tip segment used for stretch direction test
    stretch_pairs = []
    for toe_name in ["thumb", "index", "middle", "ring", "pinky"]:
        stretch_pairs.append((f"toe_{toe_name}.01_master.L", f"DEF-toe_{toe_name}.02.L"))
        stretch_pairs.append((f"toe_{toe_name}.01_master.R", f"DEF-toe_{toe_name}.02.R"))

    bpy.context.view_layer.objects.active = rig_arm
    bpy.ops.object.mode_set(mode='POSE')

    print("\n[所有toe_master伸缩方向检查]")
    for master_name, driven_name in stretch_pairs:
        master_pb = rig_arm.pose.bones.get(master_name)
        driven_pb = rig_arm.pose.bones.get(driven_name)
        if not master_pb or not driven_pb:
            print(f"  ⚠ {master_name} 或 {driven_name} 不存在（可选）")
            continue

        print(f"  {master_name}:")
        print(f"    - lock_scale = {tuple(master_pb.lock_scale)}")

        # Reset pose transforms for deterministic test
        for pb in rig_arm.pose.bones:
            pb.location = (0.0, 0.0, 0.0)
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = (0.0, 0.0, 0.0)
            pb.scale = (1.0, 1.0, 1.0)
        bpy.context.view_layer.update()

        base_tail = driven_pb.tail.copy()
        # Rigify finger/toe master stretch is driven by local scale Y.
        master_pb.scale = (1.0, 1.3, 1.0)
        bpy.context.view_layer.update()
        delta = driven_pb.tail - base_tail
        dx = abs(delta.x)
        dy = abs(delta.y)
        dz = abs(delta.z)
        length = delta.length

        print(
            f"    - 缩放后尾端位移: ({delta.x:.6f}, {delta.y:.6f}, {delta.z:.6f}), len={length:.6f}"
        )
        print(f"    - 位移分量: |X|={dx:.6f}, |Y|={dy:.6f}, |Z|={dz:.6f}")

        # Pass criterion: vertical component should be dominant or near-dominant.
        # (Right side can be mirrored and include some forward component.)
        vertical_ok = (dz >= dx) and (dz >= dy * 0.8)
        if vertical_ok:
            print("    ✓ 伸缩方向以垂直分量为主（符合预期）")
        else:
            print("    ✗ 伸缩方向仍偏水平（需继续修正）")
            all_passed = False

    bpy.ops.object.mode_set(mode='OBJECT')
    return all_passed

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("脚趾无头Blender回归验证")
    print("=" * 60)
    
    # 1. 加载blend文件（如果还没有打开）
    current_file = bpy.data.filepath
    need_load = True
    if current_file and os.path.exists(current_file):
        try:
            if os.path.samefile(current_file, blend_file):
                need_load = False
                print(f"✓ 文件已经打开: {os.path.basename(blend_file)}")
        except (OSError, ValueError):
            # samefile可能失败，继续加载
            pass
    
    if need_load:
        if not load_blend_file(blend_file):
            print("\n✗ 文件加载失败，退出")
            return 1
    
    # 2. 查找骨骼
    mmd_arm, rig_arm = find_armatures()
    
    if not mmd_arm:
        print("\n✗ 未找到源骨骼，退出")
        return 1
    
    # 3. 检查源骨骼中的脚趾
    print("\n" + "=" * 60)
    print("第一部分：源骨骼脚趾检查")
    print("=" * 60)
    
    source_toe_ok = check_source_toe_bones(mmd_arm)
    source_constraints_ok = check_source_toe_constraints(mmd_arm)
    
    # 4. 检查生成的rig中的脚趾（如果存在）
    if rig_arm:
        print("\n" + "=" * 60)
        print("第二部分：生成的rig脚趾检查")
        print("=" * 60)
        
        rig_toe_ok = check_rig_toe_bones(rig_arm)
        rig_parent_ok = check_rig_toe_parent_helpers(rig_arm)
        rig_constraints_ok = check_rig_toe_constraints(rig_arm)
        position_ok = check_toe_position_alignment(mmd_arm, rig_arm)
        stretch_ok = check_toe_master_stretch_direction(rig_arm)
    else:
        print("\n" + "=" * 60)
        print("第二部分：生成的rig脚趾检查")
        print("=" * 60)
        print("⚠ Rig不存在，跳过rig检查")
        print("  提示：如果文件尚未生成rig，请先运行 test_rig_generation.py")
        rig_toe_ok = False
        rig_parent_ok = False
        rig_constraints_ok = False
        position_ok = False
        stretch_ok = False
    
    # 5. 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    results = {
        "源骨骼脚趾存在": source_toe_ok,
        "源骨骼脚趾约束": source_constraints_ok,
    }
    
    if rig_arm:
        results.update({
            "Rig脚趾骨骼": rig_toe_ok,
            "Rig父级辅助骨骼": rig_parent_ok,
            "Rig脚趾约束": rig_constraints_ok,
            "脚趾位置一致性": position_ok,
            "所有toe_master伸缩方向": stretch_ok,
        })
    
    all_passed = all(results.values())
    
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {status}: {name}")
    
    if all_passed:
        print("\n✓ 所有脚趾验证通过!")
        return 0
    else:
        print("\n✗ 部分验证失败，请检查上述输出")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n✗ 发生未处理的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
