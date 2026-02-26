import bpy
fp='/home/duckfeather/Miku_Miku_Rig/MikuMikuRig/mmr_operators/chisaBody5_rigged.blend'
bpy.ops.wm.open_mainfile(filepath=fp)
src=bpy.data.objects.get('Genesis 9')
rig=bpy.data.objects.get('Genesis 9_Rig')
print('SRC',bool(src),'RIG',bool(rig))
if not src or not rig: raise SystemExit

rel=[]
copy_to_rig=[]
for pb in src.pose.bones:
    for c in pb.constraints:
        if c.name in {'rel_transforms','rel_location','rel_rotation'}:
            rel.append((pb.name,c.type,c.name,getattr(c,'subtarget','')))
        if hasattr(c,'target') and c.target==rig:
            copy_to_rig.append((pb.name,c.type,c.name,getattr(c,'subtarget','')))

print('REL_COUNT',len(rel))
for r in rel[:120]:
    print('REL',r)
print('COPY_TO_RIG_COUNT',len(copy_to_rig))
for r in copy_to_rig[:120]:
    print('CR',r)
