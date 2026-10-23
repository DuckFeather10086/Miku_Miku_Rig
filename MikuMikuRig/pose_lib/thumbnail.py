"""Render a compact pose mannequin to the native asset preview; no viewport capture."""
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector


def set_preview(context, rig, action):
    names = ['ORG-' + n + side for side in ('.L', '.R')
             for n in ('upper_arm', 'forearm', 'hand', 'thigh', 'shin', 'foot')]
    names += [n for n in ('ORG-spine', 'ORG-spine.001', 'ORG-spine.002',
                          'ORG-spine.003', 'ORG-spine.004', 'ORG-neck', 'ORG-head',
                          'ORG-shoulder.L', 'ORG-shoulder.R') if n in rig.pose.bones]
    if 'ORG-head' not in rig.pose.bones:
        names.append('head')
    segments = [(rig.pose.bones[n].head.copy(), rig.pose.bones[n].tail.copy()) for n in names]
    points = [p for segment in segments for p in segment]
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center = (low + high) / 2
    size = max(high - low)
    scene = bpy.data.scenes.new('MMR Pose Thumbnail')
    camera_data = bpy.data.cameras.new('MMR Pose Thumbnail')
    camera = bpy.data.objects.new('MMR Pose Thumbnail', camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = size * 1.35
    camera.location = center + Vector((0.25, -2.5, 0.15)) * size
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = camera
    curve_data = bpy.data.curves.new('MMR Pose Mannequin', 'CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = size * 0.014
    curve_data.bevel_resolution = 2
    for start, end in segments:
        spline = curve_data.splines.new('POLY')
        spline.points.add(1)
        spline.points[0].co = (*start, 1)
        spline.points[1].co = (*end, 1)
    mannequin = bpy.data.objects.new('MMR Pose Mannequin', curve_data)
    mannequin.color = (0.25, 0.65, 0.9, 1)
    scene.collection.objects.link(mannequin)
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'OBJECT'
    scene.display.shading.background_type = 'WORLD'
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = True
    scene.render.resolution_x = scene.render.resolution_y = 256
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Standard'
    image = None
    try:
        with tempfile.TemporaryDirectory(prefix='mmr_pose_') as directory:
            scene.render.filepath = str(Path(directory) / 'preview.png')
            bpy.ops.render.render(scene=scene.name, write_still=True)
            image = bpy.data.images.load(scene.render.filepath, check_existing=False)
            preview = action.preview_ensure()
            preview.image_size = tuple(image.size)
            preview.image_pixels_float[:] = image.pixels[:]
    finally:
        if image:
            bpy.data.images.remove(image)
        bpy.data.objects.remove(mannequin, do_unlink=True)
        bpy.data.objects.remove(camera, do_unlink=True)
        bpy.data.curves.remove(curve_data)
        bpy.data.cameras.remove(camera_data)
        bpy.data.scenes.remove(scene)
