"""Blender 5.2: generated rigs with three proportions share one native FK asset.

blender -b --factory-startup --python-exit-code 1 -P test_pose_assets.py -- --out <directory>
"""
import argparse
import json
import sys
from pathlib import Path
import bpy
from mathutils import Euler, Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import MikuMikuRig
from MikuMikuRig.pose_lib import assets, rig_adapter as adapter


def generate(name, x_scale, z_scale):
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.armature_basic_human_metarig_add()
    meta = bpy.context.object
    bpy.ops.object.mode_set(mode='EDIT')
    geometry = {b.name: (b.head.copy(), b.tail.copy()) for b in meta.data.edit_bones}
    for bone in meta.data.edit_bones:
        head, tail = geometry[bone.name]
        bone.head = (head.x*x_scale, head.y, head.z*z_scale)
        bone.tail = (tail.x*x_scale, tail.y, tail.z*z_scale)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.pose.rigify_generate()
    rig = bpy.context.object
    rig.name = name
    return rig


def active(rig):
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True);bpy.context.view_layer.objects.active = rig


def rotation(rig, name, values):
    p = rig.pose.bones[name]
    p.rotation_mode = 'QUATERNION';p.rotation_quaternion = Euler(values).to_quaternion()


def main():
    parser = argparse.ArgumentParser();parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    args.out.mkdir(parents=True, exist_ok=True)
    MikuMikuRig.register()
    bpy.ops.preferences.addon_enable(module='rigify')
    rigs = [generate(name, width, height) for name,width,height in
            [('Small',.8,.75),('Medium',1.,1.),('Large',1.15,1.25)]]
    source = rigs[1];active(source)
    limbs = adapter.snap_definitions(source)
    for limb in limbs:source.pose.bones[limb['prop']]['IK_FK'] = 1.
    for side in ('.L','.R'):
        rotation(source,'upper_arm_fk'+side,(.2,.1,.35 if side=='.L' else -.35))
        rotation(source,'forearm_fk'+side,(.5,0,0))
        rotation(source,'thigh_fk'+side,(-.3,0,0))
        rotation(source,'shin_fk'+side,(.6,0,0))
    source.pose.bones['torso'].location.z = -.12
    source.update_tag();bpy.context.view_layer.update()
    expected = {name: assets.quaternion(source.pose.bones[name]) for name in assets.controls(source,limbs)}
    # Start from IK so saving exercises the real IK->FK path on all four limbs.
    with adapter.pose_operation(bpy.context,source):adapter.switch_to_ik(bpy.context,source,limbs)
    bpy.context.scene.tool_settings.use_keyframe_insert_auto=True
    before = adapter.snapshot(source)
    action,path = assets.save_asset(bpy.context,'三种比例共用姿势','回归测试/全身',directory=args.out/'library',persist_preferences=False)
    assert before == adapter.snapshot(source),'Saving changed the current pose'
    assert bpy.context.scene.tool_settings.use_keyframe_insert_auto
    bpy.context.scene.tool_settings.use_keyframe_insert_auto=False
    assert tuple(action.preview.image_size)==(256,256)
    image=bpy.data.images.new('Pose preview',width=256,height=256,alpha=True)
    image.pixels[:]=action.preview.image_pixels_float[:];image.filepath_raw=str(args.out/'preview.png');image.file_format='PNG';image.save()
    with bpy.data.libraries.load(str(path)) as (src,dst):
        assert src.actions and not src.objects, 'Asset file should not contain a character'
    loaded=assets.load_action(path,action.name)
    assert loaded.get('mmr_pose_schema')==assets.SCHEMA
    report=[]
    for rig in rigs:
        active(rig)
        # Existing selection must not accidentally limit the whole-pose application.
        for p in rig.pose.bones:p.select=False
        rig.pose.bones['head'].select=True
        rig.pose.bones['hand_fk.L'].rotation_mode='XYZ'
        root = rig.pose.bones['root'];root.location=(2,3,4);root.scale=(1.1,1.1,1.1)
        rig.pose.bones['thigh_fk.L'].scale=(1.2,1.2,1.2)
        rig.pose.bones['forearm_fk.L'].location=(.03,0,0)
        rest = {b.name: tuple(v for row in b.matrix_local for v in row) for b in rig.data.bones}
        ratio = assets.apply_action(bpy.context,rig,loaded)
        assert (root.location-Matrix.Translation((2,3,4)).translation).length<1e-6
        assert all(abs(s-1.1)<1e-6 for s in root.scale)
        assert rig.pose.bones['head'].select and not rig.pose.bones['thigh_fk.L'].select
        assert abs(rig.pose.bones['torso'].location.z - -.12*ratio)<1e-5
        assert all(abs(s-1)<1e-6 for s in rig.pose.bones['thigh_fk.L'].scale)
        assert rig.pose.bones['forearm_fk.L'].location.length<1e-6
        assert rest=={b.name:tuple(v for row in b.matrix_local for v in row) for b in rig.data.bones}
        max_angle=max(min(q.rotation_difference(assets.quaternion(rig.pose.bones[n])).angle,
                          abs(6.283185307-q.rotation_difference(assets.quaternion(rig.pose.bones[n])).angle)) for n,q in expected.items())
        assert max_angle < .02, max_angle
        rig_limbs=adapter.snap_definitions(rig)
        saved={l['prop']:adapter.limb_result(rig,l) for l in rig_limbs}
        with adapter.pose_operation(bpy.context,rig):adapter.switch_to_ik(bpy.context,rig,rig_limbs)
        error=max((m.translation-e.translation).length for l in rig_limbs for m,e in zip(adapter.limb_result(rig,l),saved[l['prop']]))
        report.append({'rig':rig.name,'translation_ratio':ratio,'rotation_error_radians':max_angle,'ik_position_error':error})
    # An untagged or polluted asset must fail before changing any current controls.
    bad=loaded.copy();bad['mmr_pose_schema']=0
    state=adapter.snapshot(rigs[-1])
    try:assets.apply_action(bpy.context,rigs[-1],bad)
    except ValueError:pass
    else:raise AssertionError('Untagged asset accepted')
    assert state==adapter.snapshot(rigs[-1])
    bpy.data.actions.remove(bad)
    action_name=action.name
    bpy.ops.wm.save_as_mainfile(filepath=str(args.out/'three_rigs.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(args.out/'three_rigs.blend'))
    assert bpy.data.actions[action_name].asset_data
    (args.out/'report.json').write_text(json.dumps({'cases':report,'source_restored':True,'reopen':True,'asset':str(path)},indent=2))
    MikuMikuRig.unregister();MikuMikuRig.register();MikuMikuRig.unregister()
    print('MMR POSE ASSETS PASSED',report)

if __name__=='__main__':main()
