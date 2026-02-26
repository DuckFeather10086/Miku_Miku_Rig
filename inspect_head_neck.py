import bpy
fp='/home/duckfeather/Miku_Miku_Rig/MikuMikuRig/mmr_operators/chisaBody5_rigged.blend'
bpy.ops.wm.open_mainfile(filepath=fp)
rig=bpy.data.objects.get('Genesis 9_Rig')
print('rig:', bool(rig))
if not rig:
    raise SystemExit(1)

cand=[n for n in rig.pose.bones.keys() if 'head' in n.lower() or 'neck' in n.lower() or n.startswith('spine_fk.')]
print('candidates:', len(cand))
for n in sorted(cand)[:80]:
    pb=rig.pose.bones[n]
    eb=rig.data.bones.get(n)
    print(n, 'len=', round(pb.length,4), 'shape_scale=', tuple(round(v,3) for v in pb.custom_shape_scale_xyz), 'has_shape=', bool(pb.custom_shape))

# edit connectivity
bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for n in ['neck','head','spine_fk.005','spine_fk.006','spine_fk.007']:
    eb=rig.data.edit_bones.get(n)
    if eb:
        print('EDIT', n, 'parent=', eb.parent.name if eb.parent else None, 'connect=', eb.use_connect,
              'head=', tuple(round(v,4) for v in eb.head), 'tail=', tuple(round(v,4) for v in eb.tail))
