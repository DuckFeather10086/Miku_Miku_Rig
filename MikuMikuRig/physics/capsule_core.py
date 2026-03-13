# Capsule colliders: low-poly capsule meshes parented to bones (Skinify-style)
import bpy
import bmesh
import math
from mathutils import Matrix, Vector
from .. import base


def _make_capsule_mesh(name, radius=0.05, length=0.3, segments=8):
    """Create a low-poly cylinder mesh (capsule shape). Length along Z; rigid body CAPSULE uses bounds."""
    bm = bmesh.new()
    half = length / 2
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        bm.verts.new((x, y, -half))
        bm.verts.new((x, y, half))
    bm.verts.ensure_lookup_table()
    for i in range(segments):
        i2 = (i + 1) % segments
        bm.faces.new((
            bm.verts[2 * i], bm.verts[2 * i + 1], bm.verts[2 * i2 + 1], bm.verts[2 * i2]
        ))
    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _bone_capsule_size(bone, scale=1.0):
    """Return (radius, length) for a capsule along the bone."""
    length = (bone.tail - bone.head).length
    if length < 1e-5:
        length = 0.05
    radius = length * 0.2 * scale
    if radius < 0.008:
        radius = 0.008
    return radius, length


def add_capsule_colliders(context, armature, bone_names=None, scale=1.0, add_rigid_body=False):
    """
    Add capsule collider objects parented to bones. If bone_names is None, use deform bones.
    Returns (success: bool, message: str, created_objects: list).
    """
    if not armature or armature.type != 'ARMATURE':
        return False, "No armature selected", []
    if context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            return False, "Switch to Object mode", []
    if bone_names is None:
        bone_names = [b.name for b in armature.data.bones if b.use_deform]
        if not bone_names:
            bone_names = [b.name for b in armature.data.bones]
    created = []
    collection = armature.users_collection[0] if armature.users_collection else context.scene.collection
    for bone_name in bone_names:
        if bone_name not in armature.data.bones:
            continue
        bone = armature.data.bones[bone_name]
        radius, length = _bone_capsule_size(bone, scale)
        mesh = _make_capsule_mesh(f"cap_{armature.name}_{bone_name}", radius=radius, length=length)
        obj = bpy.data.objects.new(f"Cap_{bone_name}", mesh)
        collection.objects.link(obj)
        # Parent to bone: parent_type BONE, then set matrix_basis so capsule is centered on bone
        obj.parent = armature
        obj.parent_type = 'BONE'
        obj.parent_bone = bone_name
        # Capsule mesh is along Z; bone is along Y. Rotate 90° X so Z->Y, then place center at bone center
        obj.matrix_basis = Matrix.Rotation(math.radians(-90), 4, 'X') @ Matrix.Translation(Vector((0, bone.length / 2, 0)))
        if add_rigid_body:
            context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_add(type='PASSIVE')
            obj.rigid_body.collision_shape = 'CAPSULE'
        created.append(obj)
    return True, f"Created {len(created)} capsule(s)", created
