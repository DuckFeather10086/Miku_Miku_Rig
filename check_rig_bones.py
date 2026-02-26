#!/usr/bin/env python3
"""检查生成的rig中有哪些DEF骨骼"""
import bpy
import os

filepath = "/home/duckfeather/Miku_Miku_Rig/MikuMikuRig/mmr_operators/chisaBody5_rigged.blend"
bpy.ops.wm.open_mainfile(filepath=filepath)

rig = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE' and '_Rig' in obj.name:
        rig = obj
        break

if rig:
    print(f"Rig名称: {rig.name}")
    print(f"总骨骼数: {len(rig.data.bones)}")
    
    print(f"\n所有骨骼类型统计:")
    bone_types = {}
    for bone in rig.data.bones:
        prefix = bone.name.split('-')[0] if '-' in bone.name else bone.name.split('.')[0]
        bone_types[prefix] = bone_types.get(prefix, 0) + 1
    for prefix, count in sorted(bone_types.items()):
        print(f"  {prefix}: {count}")
    
    print(f"\n前20个骨骼名称:")
    for i, bone in enumerate(list(rig.data.bones)[:20]):
        print(f"  {bone.name}")
    
    print(f"\n所有DEF骨骼:")
    def_bones = [b.name for b in rig.data.bones if 'DEF-' in b.name]
    print(f"DEF骨骼数量: {len(def_bones)}")
    if def_bones:
        for bone in sorted(def_bones)[:20]:
            print(f"  {bone}")
    
    print(f"\n所有ORG骨骼:")
    org_bones = [b.name for b in rig.data.bones if 'ORG-' in b.name]
    print(f"ORG骨骼数量: {len(org_bones)}")
    if org_bones:
        for bone in sorted(org_bones)[:20]:
            print(f"  {bone}")
