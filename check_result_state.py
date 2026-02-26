import bpy

fp='/home/duckfeather/Miku_Miku_Rig/MikuMikuRig/mmr_operators/chisaBody5_rigged.blend'
bpy.ops.wm.open_mainfile(filepath=fp)

src=bpy.data.objects.get('Genesis 9')
rig=bpy.data.objects.get('Genesis 9_Rig')
print('SRC', bool(src), 'RIG', bool(rig))
if not src or not rig:
    raise SystemExit(0)

# count constraints on source pose bones
constraint_bones=[]
for pb in src.pose.bones:
    if len(pb.constraints)>0:
        names=[c.type+':'+c.name for c in pb.constraints]
        constraint_bones.append((pb.name,len(pb.constraints),names[:4]))

print('SOURCE_BONES_WITH_CONSTRAINTS', len(constraint_bones))
for item in constraint_bones[:30]:
    print('C', item)

# check specific mapped bones
for name in ['hip','pelvis','l_thigh','r_thigh','l_forearm','r_forearm','head']:
    pb=src.pose.bones.get(name)
    if pb:
        print('SRC_CONS', name, [c.type+':'+c.name for c in pb.constraints])

# rough position deltas for a few correspondences if exist
pairs=[('DEF-spine.004','spine.004'),('DEF-upper_arm.L','l_shoulder'),('DEF-thigh.L','l_thigh')]
for rb,sb in pairs:
    rb_b=rig.pose.bones.get(rb)
    sb_b=src.pose.bones.get(sb)
    if rb_b and sb_b:
        d=(rb_b.head-sb_b.head).length
        print('DELTA', rb, sb, round(d,6))
