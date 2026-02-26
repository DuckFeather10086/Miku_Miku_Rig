import bpy
fp='/home/duckfeather/Miku_Miku_Rig/MikuMikuRig/mmr_operators/chisaBody5_rigged.blend'
bpy.ops.wm.open_mainfile(filepath=fp)
rig=bpy.data.objects.get('Genesis 9_Rig')
if not rig:
    print('no rig'); raise SystemExit
parents=[b.name for b in rig.data.bones if b.name.endswith('_parent')]
print('PARENT_BONES',len(parents))
print(parents[:120])
