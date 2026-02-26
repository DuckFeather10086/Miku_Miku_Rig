#!/usr/bin/env python3
"""快速验证rig文件"""
import bpy
import os

# 检查两个文件
files = [
    "MikuMikuRig/mmr_operators/chisaBody5.blend",
    "MikuMikuRig/mmr_operators/chisaBody5_rigged.blend"
]

script_dir = os.path.dirname(os.path.abspath(__file__))

for file in files:
    filepath = os.path.join(script_dir, file)
    if not os.path.exists(filepath):
        print(f"✗ 文件不存在: {filepath}")
        continue
    
    print(f"\n{'='*60}")
    print(f"检查文件: {file}")
    print(f"{'='*60}")
    
    bpy.ops.wm.read_homefile(app_template="")
    bpy.ops.wm.open_mainfile(filepath=filepath)
    
    rigs = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
    print(f"Armature对象数量: {len(rigs)}")
    for rig in rigs:
        print(f"  - {rig.name} (隐藏: {rig.hide_viewport}, 骨骼数: {len(rig.data.bones)})")
        if '_Rig' in rig.name:
            print(f"    ✓ 这是生成的控制器!")
