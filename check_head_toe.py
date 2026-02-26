import bpy

fp='/home/duckfeather/Miku_Miku_Rig/MikuMikuRig/mmr_operators/chisaBody5_rigged.blend'
bpy.ops.wm.open_mainfile(filepath=fp)
mmd=bpy.data.objects.get('Genesis 9')
rig=bpy.data.objects.get('Genesis 9_Rig')

print('objs:', bool(mmd), bool(rig))
if not (mmd and rig):
    raise SystemExit(1)

# report possible head controls
head_candidates=[n for n in ['head','neck','spine_fk.003','spine_fk.004','spine.007','spine.006'] if n in rig.pose.bones]
print('head candidates in rig:', head_candidates)

# check rel constraints around neck/head/toe
for src in ['spine.005','spine.006','spine.007','toe.L','toe.R']:
    pb=mmd.pose.bones.get(src)
    if not pb:
        print(src, 'not in source')
        continue
    rel=[(c.name,c.type,getattr(c,'subtarget','')) for c in pb.constraints if c.name.startswith('rel_')]
    print(src, 'rel=', rel)

# check toe parent helper bones exist
for n in ['toe.L_parent','toe.R_parent','ToeTipIK_L_parent','ToeTipIK_R_parent']:
    print(n, 'in rig bones =', n in rig.data.bones)
