#!/usr/bin/env python3
"""检查生成的rigged文件内容"""
import bpy
import sys

filepath = "/home/duckfeather/Miku_Miku_Rig/MikuMikuRig/mmr_operators/chisaBody5_rigged.blend"

bpy.ops.wm.open_mainfile(filepath=filepath)

print("=" * 60)
print("文件内容检查:")
print("=" * 60)
print(f"\n场景中的所有对象:")
for obj in bpy.context.scene.objects:
    print(f"  - {obj.name} (type: {obj.type}, visible: {not obj.hide_viewport})")

print(f"\n所有armature对象 (包括不在场景中的):")
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        in_scene = obj.name in bpy.context.scene.objects
        print(f"  - {obj.name} (在场景: {in_scene}, visible: {not obj.hide_viewport})")

print(f"\n活动对象: {bpy.context.view_layer.objects.active}")
if bpy.context.view_layer.objects.active:
    print(f"  类型: {bpy.context.view_layer.objects.active.type}")
