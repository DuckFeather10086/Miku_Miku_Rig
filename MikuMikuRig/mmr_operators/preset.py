from types import prepare_class
import bpy
import os
import json
from . import rig

#骨骼枚举属性部分

mmd_bone_type_list=[
'None',
'Root','Center','torso',
'LowerBody','UpperBody0','UpperBody','UpperBody2','Neck','Head',
'Eye_L','Eye_R',
'Shoulder_L','Arm_L','ArmTwist_L','Elbow_L','HandTwist_L','Wrist_L',
'Thumb0_L','Thumb1_L','Thumb2_L',
'IndexFinger1_L','IndexFinger2_L','IndexFinger3_L',
'MiddleFinger1_L','MiddleFinger2_L','MiddleFinger3_L',
'RingFinger1_L','RingFinger2_L','RingFinger3_L',
'LittleFinger1_L','LittleFinger2_L','LittleFinger3_L',
'Shoulder_R','Arm_R','ArmTwist_R','Elbow_R','HandTwist_R','Wrist_R',
'Thumb0_R','Thumb1_R','Thumb2_R',
'IndexFinger1_R','IndexFinger2_R','IndexFinger3_R',
'MiddleFinger1_R','MiddleFinger2_R','MiddleFinger3_R',
'RingFinger1_R','RingFinger2_R','RingFinger3_R',
'LittleFinger1_R','LittleFinger2_R','LittleFinger3_R',
'Leg_L','Knee_L','Ankle_L','ToeTipIK_L',
'LegIK_L',
'LegTipEX_L',
'Leg_R','Knee_R','Ankle_R','ToeTipIK_R',
'LegIK_R',
'LegTipEX_R',
]

rigify_bone_type_list=[
'None',
'Root',
'spine','spine.001','spine.002','spine.003','spine.004','spine.005','spine.006','spine.007',
'eye.L','eye.R',
'shoulder.L','upper_arm.L','ArmTwist_L','forearm.L','HandTwist_L','hand.L',
'thumb.01.L','thumb.02.L','thumb.03.L',
'f_index.01.L','f_index.02.L','f_index.03.L',
'f_middle.01.L','f_middle.02.L','f_middle.03.L',
'f_ring.01.L','f_ring.02.L','f_ring.03.L',
'f_pinky.01.L','f_pinky.02.L','f_pinky.03.L',
'shoulder.R','upper_arm.R','ArmTwist_R','forearm.R','HandTwist_R','hand.R',
'thumb.01.R','thumb.02.R','thumb.03.R',
'f_index.01.R','f_index.02.R','f_index.03.R',
'f_middle.01.R','f_middle.02.R','f_middle.03.R',
'f_ring.01.R','f_ring.02.R','f_ring.03.R',
'f_pinky.01.R','f_pinky.02.R','f_pinky.03.R',
'thigh.L','shin.L','foot.L','toe.L',
'toe_thumb.01.L','toe_thumb.02.L','toe_index.01.L','toe_index.02.L','toe_middle.01.L','toe_middle.02.L','toe_ring.01.L','toe_ring.02.L','toe_pinky.01.L','toe_pinky.02.L',
'thigh.R','shin.R','foot.R','toe.R',
'toe_thumb.01.R','toe_thumb.02.R','toe_index.01.R','toe_index.02.R','toe_middle.01.R','toe_middle.02.R','toe_ring.01.R','toe_ring.02.R','toe_pinky.01.R','toe_pinky.02.R',
]

bone_translate_dict_C={
    'None': '无', 
    'Root': '根骨骼', 'Center': '中心（重定向用骨骼）', 'torso': '躯干控制器（重定向用骨骼）', 
    'spine': '下半身', 'spine.001': '上半身0（非必要骨骼）', 'spine.002': '上半身1', 'spine.003': '上半身2', 'spine.004': '脖子', 'spine.005': '上颈（非必要骨骼）', 'spine.006': '头顶（非必要骨骼）', 'spine.007': '头', 'LowerBody':'下半身',
    'eye.L': '左眼（非必要骨骼）', 'eye.R': '右眼（非必要骨骼）', 
    'shoulder.L': '左肩膀', 'upper_arm.L': '左大臂', 'ArmTwist_L': '左大臂扭转骨骼（非必要骨骼）', 'forearm.L': '左小臂', 'HandTwist_L': '左小臂扭转骨骼（ 非必要骨骼）', 'hand.L': '左手腕', 
    'thumb.01.L': '左手大拇指0', 'thumb.02.L': '左手大拇指1', 'thumb.03.L': '左手大拇指2', 
    'f_index.01.L': '左手食指1', 'f_index.02.L': '左手食指2', 'f_index.03.L': '左手食指3', 
    'f_middle.01.L': '左手中指1', 'f_middle.02.L': ' 左手中指2', 'f_middle.03.L': '左手中指3', 
    'f_ring.01.L': '左手无名指1', 'f_ring.02.L': '左手无名指2', 'f_ring.03.L': '左手无名指3', 
    'f_pinky.01.L': '左手小拇指1', 'f_pinky.02.L': '左手小拇指2', 'f_pinky.03.L': '左手小拇指3', 
    'shoulder.R': '右肩膀', 'upper_arm.R': '右大臂', 'ArmTwist_R': '右大臂扭转骨骼（非必要骨骼）', 'forearm.R': '右小臂', 'HandTwist_R': '右小臂扭转骨骼（非必要骨骼）', 'hand.R': '右手腕', 
    'thumb.01.R': '右手大拇指0', 'thumb.02.R': '右手大拇指1', 'thumb.03.R': '右手大拇指2', 
    'f_index.01.R': '右手食指1', 'f_index.02.R': '右手食指2', 'f_index.03.R': '右手食指3', 
    'f_middle.01.R': '右手中指1', 'f_middle.02.R': '右手中指2', 'f_middle.03.R': '右手中指3', 
    'f_ring.01.R': '右手无名指1', 'f_ring.02.R': '右手无名指2', 'f_ring.03.R': '右手无名指3', 
    'f_pinky.01.R': '右手小拇指1', 'f_pinky.02.R': '右手小拇指2', 'f_pinky.03.R': '右手小拇指3', 
    'thigh.L': '左大腿', 'shin.L': '左小腿', 'foot.L': '左脚掌', 'toe.L': '左脚尖（整根，非必要）', 
    'toe_thumb.01.L': '左脚拇指1（非必要骨骼）', 'toe_thumb.02.L': '左脚拇指2（非必要骨骼）', 'toe_index.01.L': '左脚食趾1（非必要骨骼）', 'toe_index.02.L': '左脚食趾2（非必要骨骼）', 'toe_middle.01.L': '左脚中趾1（非必要骨骼）', 'toe_middle.02.L': '左脚中趾2（非必要骨骼）', 'toe_ring.01.L': '左脚无名趾1（非必要骨骼）', 'toe_ring.02.L': '左脚无名趾2（非必要骨骼）', 'toe_pinky.01.L': '左脚小趾1（非必要骨骼）', 'toe_pinky.02.L': '左脚小趾2（非必要骨骼）', 
    'LegIK_L': '左腿IK骨骼（重定向用骨骼）', 'ToeTipIK_L': '左脚掌IK骨骼（非必要骨骼）', 
    'thigh.R': '右大腿', 'shin.R': '右小腿', 'foot.R': '右脚掌', 'toe.R': '右脚尖（整根，非必要）', 
    'toe_thumb.01.R': '右脚拇指1（非必要骨骼）', 'toe_thumb.02.R': '右脚拇指2（非必要骨骼）', 'toe_index.01.R': '右脚食趾1（非必要骨骼）', 'toe_index.02.R': '右脚食趾2（非必要骨骼）', 'toe_middle.01.R': '右脚中趾1（非必要骨骼）', 'toe_middle.02.R': '右脚中趾2（非必要骨骼）', 'toe_ring.01.R': '右脚无名趾1（非必要骨骼）', 'toe_ring.02.R': '右脚无名趾2（非必要骨骼）', 'toe_pinky.01.R': '右脚小趾1（非必要骨骼）', 'toe_pinky.02.R': '右脚小趾2（非必要骨骼）', 
    'LegIK_R': '右腿IK骨骼（非必要骨骼）', 'ToeTipIK_R': '右脚掌IK骨骼（重定向用骨骼）'
    }

built_in_rig_dict_list=['None','MMD_JP','MMD_EN','VRoid']
built_in_retarget_dict_list=['None','mixamo','Rigify','FBX动捕','BVH动捕']


def get_ai_mapping_prompt_text():
    """Build English prompt for LLM to generate rig preset from skeleton structure and bone name semantics."""
    return r"""You are helping to configure a bone mapping for Miku Miku Rig (Blender add-on). Given a skeleton's structure and bone names, output a JSON mapping that assigns each source bone to a supported controller ID.

## Supported controllers (use only these IDs)

**Root & spine (order: root → spine → spine.001 → … → spine.007):**
- Root, Center
- spine, spine.001, spine.002, spine.003, spine.004, spine.005, spine.006, spine.007

**Rule — spine.007 is HEAD:** The rig expects spine.007 to be the head bone. You MUST map the skeleton's head bone to spine.007. If the source skeleton has more spine/neck/head bones than we have segments (spine through spine.007), shorten the match: map the head to spine.007 and assign the remaining spine IDs backwards toward the pelvis; leave any extra upper spines unmapped or merge them. Do not map spine.007 to a non-head bone.

**Eyes (optional):** eye.L, eye.R

**Arms (L/R):** shoulder.L/R, upper_arm.L/R, ArmTwist_L/R (optional), forearm.L/R, HandTwist_L/R (optional), hand.L/R
**Fingers (3 segments each, L/R):** thumb.01–03, f_index.01–03, f_middle.01–03, f_ring.01–03, f_pinky.01–03

**Critical finger rule (Genesis9-like hands):**
- Do NOT map metacarpal/palm helper bones (e.g. `*_metacarpal`, `*metacarpal*`) to finger controllers.
- Finger controllers (`f_*.01`) must map to the first real finger phalanx (e.g. index1/mid1/ring1/pinky1), not palm bones.
- If both metacarpal and finger-1 candidates exist, choose finger-1 and skip metacarpal entries.

**Legs (L/R):** thigh.L/R, shin.L/R, foot.L/R, toe.L/R (optional), ToeTipIK_L/R (optional), LegIK_L/R (for retarget)

**Toes (optional, L/R):** toe_thumb.01–02, toe_index.01–02, toe_middle.01–02, toe_ring.01–02, toe_pinky.01–02

## Output format (required)

You MUST output a single JSON object only: the preset mapping layer. Do NOT wrap it in "rig" or a preset name. The user will paste this into the add-on and type the preset name there.

- Keys: exact source bone names (as in the skeleton).
- Values: exactly [controller_id, invert] — controller_id is a string from the list above, invert is boolean (true/false).

Valid example (copy this structure only):
{"Head": ["spine.007", false], "Neck": ["spine.004", false], "LeftArm": ["upper_arm.L", false], "pelvis": ["spine", true]}

Invalid: do not output {"rig": {"MyPreset": { ... }}}. Output only the inner { "bone": ["id", false], ... } object.

## Task

Using the skeleton structure and bone name semantics provided by the user, produce the full mapping JSON. Only include bones that have a clear semantic match. Use L/R suffix for left/right. Remember: head bone → spine.007; if there are more spine segments than spine..001–.007, shorten so that head = spine.007. For finger mapping, skip metacarpal/palm helper bones and map only real finger segments.
"""


bpy.types.PoseBone.mmr_bone_invert=bpy.props.BoolProperty(
    default=False
)

'''bpy.types.PoseBone.mmr_bone_type=bpy.props.EnumProperty(
        items=[
            (name, name, '') for name in bone_type_list
        ],
        description=('Choose the bone type2 you want to use'),
    )'''
#预设属性改为字符串
bpy.types.PoseBone.mmr_bone_type=bpy.props.StringProperty(
        description=('Choose the bone type2 you want to use'),
    )

#骨架枚举属性部分

my_dir = os.path.dirname(os.path.realpath(__file__))
json_path = os.path.join(my_dir, "preset.json")
#rig_json_path = os.path.join(my_dir, "rig_preset.json")
#retarget_json_path = os.path.join(my_dir, "retarget_preset.json")
rig_preset_dict={}
retarget_preset_dict={}

preset_dict_dict={
    'rig':rig_preset_dict,
    'retarget':retarget_preset_dict
}


def get_preset(pose):
    preset={}
    for bone in pose.bones:
        if bone.mmr_bone_type!='':
            preset[bone.name]=(bone.mmr_bone_type,bone.mmr_bone_invert)
    return(preset)

def set_bone_type(pose,preset):
    posebones=pose.bones
    for bone in posebones:
        if bone.name in preset:
            bone_type,invert=preset[bone.name]
            bone.mmr_bone_invert=invert
            bone.mmr_bone_type=bone_type
        else:
            bone.mmr_bone_type=''
            bone.mmr_bone_invert=False
    
def read_json(preset_type):
    global preset_dict_dict
    if os.path.exists(json_path):
        with open(json_path, 'r',encoding='utf-8') as f:
            preset_dict_dict=json.load(f)
    else:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(preset_dict_dict, f, indent=4, ensure_ascii=False)


def reload_presets_from_disk():
    """Reload preset.json from disk into memory. Returns (success: bool, message: str)."""
    global preset_dict_dict
    if not os.path.exists(json_path):
        return False, "preset.json not found"
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return False, str(e)
    if not isinstance(data, dict) or 'rig' not in data or 'retarget' not in data:
        return False, "preset.json must contain 'rig' and 'retarget' top-level keys"
    preset_dict_dict.clear()
    preset_dict_dict.update(data)
    return True, "Presets reloaded from preset.json"

def write_json(preset_type):
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(preset_dict_dict, f, indent=4, ensure_ascii=False)

def add_preset(name,preset,preset_type='rig'):
    preset_dict=preset_dict_dict[preset_type]
    if name not in preset_dict:
        preset_dict[name]=preset
        write_json(preset_type)

def delete_preset(name,preset_type='rig'):
    preset_dict=preset_dict_dict[preset_type]
    if name in preset_dict:
        del preset_dict[name]
        write_json(preset_type)

def overwrite_preset(name,preset,preset_type='rig'):
    preset_dict=preset_dict_dict[preset_type]
    if name in preset_dict:
        preset_dict[name]=preset
        write_json(preset_type)

def get_rig_preset_item(self,context):
    preset_items=[]
    for name in preset_dict_dict['rig']:
        preset_items.append((name,name,''))
    return(preset_items)

def get_retarget_preset_item(self,context):
    preset_items=[]
    for name in preset_dict_dict['retarget']:
        preset_items.append((name,name,''))
    return(preset_items)

#初始化
read_json('rig')
read_json('retarget')


#操作器部分

class OT_Add_Preset(bpy.types.Operator):
    bl_idname = "mmr.add_preset" # python 提示
    bl_label = "Add Preset"
    bl_options = {'REGISTER', 'UNDO'}

    name:bpy.props.StringProperty(default='',description="新预设名称")
    preset_type:bpy.props.StringProperty(default='rig',description="预设类型")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'name',text="Preset Name")

    def execute(self,context):
        if rig.check_arm()==False:
            return{"CANCELLED"}
        obj = context.object
        pose=obj.pose
        preset=get_preset(pose)
        add_preset(self.name,preset,self.preset_type)
        return{"FINISHED"}

class OT_Delete_Preset(bpy.types.Operator):
    bl_idname = "mmr.delete_preset" # python 提示
    bl_label = "Delete Preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset_type:bpy.props.StringProperty(default='rig',description="预设类型")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="真的要删除预设吗？")

    def execute(self,context):
        scene=context.scene
        mmr_property=scene.mmr_property
        if self.preset_type == 'rig':
            name=mmr_property.rig_preset_name
        elif self.preset_type == 'retarget':
            name=mmr_property.retarget_preset_name
        delete_preset(name,self.preset_type)
        return{"FINISHED"}

class OT_Read_Preset(bpy.types.Operator):
    bl_idname = "mmr.read_preset" # python 提示
    bl_label = "Read Preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset_type:bpy.props.StringProperty(default='rig',description="预设类型")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="真的要读取预设吗？")

    def execute(self,context):
        scene=context.scene
        mmr_property=scene.mmr_property
        if rig.check_arm()==False:
            return{"CANCELLED"}
        obj = context.object
        pose=obj.pose
        preset_dict=preset_dict_dict[self.preset_type]
        if self.preset_type == 'rig':
            name=mmr_property.rig_preset_name
        elif self.preset_type == 'retarget':
            name=mmr_property.retarget_preset_name
        preset=preset_dict[name]
        set_bone_type(pose,preset)
        return{"FINISHED"}

class OT_Overwrite_Preset(bpy.types.Operator):
    bl_idname = "mmr.overwrite_preset" # python 提示
    bl_label = "Overwrite Preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset_type:bpy.props.StringProperty(default='rig',description="预设类型")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="真的要覆盖预设吗？")

    def execute(self,context):
        scene=context.scene
        mmr_property=scene.mmr_property
        if rig.check_arm()==False:
            return{"CANCELLED"}
        if self.preset_type == 'rig':
            name=mmr_property.rig_preset_name
        elif self.preset_type == 'retarget':
            name=mmr_property.retarget_preset_name
        obj = context.object
        pose=obj.pose
        preset=get_preset(pose)
        overwrite_preset(name,preset,self.preset_type)
        return{"FINISHED"}


class OT_Copy_AI_Prompt(bpy.types.Operator):
    bl_idname = "mmr.copy_ai_prompt"
    bl_label = "Copy AI Prompt"
    bl_description = "Generate English prompt for AI to create bone mapping from skeleton structure; copy to clipboard"
    bl_options = {'REGISTER'}

    def execute(self, context):
        text = get_ai_mapping_prompt_text()
        context.window_manager.clipboard = text
        self.report({'INFO'}, "AI prompt copied to clipboard")
        return {'FINISHED'}


class OT_Reload_Presets(bpy.types.Operator):
    bl_idname = "mmr.reload_presets"
    bl_label = "Reload preset.json"
    bl_description = "Reload preset.json from disk so edits take effect without restarting Blender"
    bl_options = {'REGISTER'}

    def execute(self, context):
        ok, msg = reload_presets_from_disk()
        if ok:
            for area in context.screen.areas:
                area.tag_redraw()
            self.report({'INFO'}, msg)
            return {'FINISHED'}
        self.report({'ERROR'}, msg)
        return {'CANCELLED'}


def _validate_preset_mapping(data):
    """Validate that data is a dict of bone_name -> [controller_id, invert]. Returns (True, None) or (False, error_msg)."""
    if not isinstance(data, dict):
        return False, "Must be a JSON object"
    for k, v in data.items():
        if not isinstance(k, str):
            return False, f"Key must be string, got: {type(k).__name__}"
        if not isinstance(v, (list, tuple)) or len(v) != 2:
            return False, f"Value for '{k}' must be [controller_id, invert], e.g. [\"spine.007\", false]"
        cid, inv = v[0], v[1]
        if not isinstance(cid, str):
            return False, f"Controller ID for '{k}' must be string"
        if not isinstance(inv, (bool, int)):
            return False, f"Invert for '{k}' must be boolean"
    return True, None


class OT_Add_Preset_From_Clipboard(bpy.types.Operator):
    bl_idname = "mmr.add_preset_from_clipboard"
    bl_label = "Add preset from clipboard"
    bl_description = "Paste AI-generated mapping from clipboard, enter preset name; adds as new rig preset and saves"
    bl_options = {'REGISTER'}

    preset_name: bpy.props.StringProperty(name="Preset Name", default="", description="Name for the new preset (e.g. Genesis9)")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name", text="Preset name")
        layout.label(text="Clipboard must contain only the mapping JSON (no \"rig\" or preset name wrapper).")

    def execute(self, context):
        name = self.preset_name.strip()
        if not name:
            self.report({'ERROR'}, "Preset name is required")
            return {'CANCELLED'}
        text = context.window_manager.clipboard
        if not (text and text.strip()):
            self.report({'ERROR'}, "Clipboard is empty; copy the AI-generated JSON first")
            return {'CANCELLED'}
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            self.report({'ERROR'}, f"Invalid JSON: {e}")
            return {'CANCELLED'}
        ok, err = _validate_preset_mapping(data)
        if not ok:
            self.report({'ERROR'}, err)
            return {'CANCELLED'}
        # Normalize values to [str, bool]
        normalized = {}
        for k, v in data.items():
            normalized[k] = [str(v[0]), bool(v[1])]
        preset_dict_dict['rig'][name] = normalized
        write_json('rig')
        for area in context.screen.areas:
            area.tag_redraw()
        self.report({'INFO'}, f"Preset \"{name}\" added and saved")
        return {'FINISHED'}


class OT_Rig_Preset(bpy.types.Operator):
    bl_idname = "mmr.rig_preset" # python 提示
    bl_label = "Rig Preset"
    bl_options = {'REGISTER', 'UNDO'}

    read:bpy.props.BoolProperty(default=True,description="读取预设")

    def execute(self,context):
        scene=context.scene
        mmr_property=scene.mmr_property
        if rig.check_arm()==False:
            return{"CANCELLED"}
        obj = context.object
        pose=obj.pose
        if self.read:
            preset_dict=preset_dict_dict['rig']
            preset_name=mmr_property.rig_preset_name
            preset=preset_dict[preset_name]
            set_bone_type(pose,preset)
        rig.RIG2(context)
        return{"FINISHED"}


class OT_Fix_All_Controllers_By_Preset(bpy.types.Operator):
    bl_idname = "mmr.fix_all_controllers_by_preset"
    bl_label = "Fix all controllers by preset"
    bl_description = "Apply current preset to source armature and regenerate rig controllers"
    bl_options = {'REGISTER', 'UNDO'}

    def _find_source_armature(self, context, preset):
        obj = context.object
        if not obj or obj.type != 'ARMATURE' or obj.pose is None:
            return None

        preset_bones = set(preset.keys())
        if any(name in obj.pose.bones for name in preset_bones):
            return obj

        if obj.name.endswith("_Rig"):
            source_name = obj.name[:-4]
            source_obj = bpy.data.objects.get(source_name)
            if source_obj and source_obj.type == 'ARMATURE' and source_obj.pose is not None:
                if any(name in source_obj.pose.bones for name in preset_bones):
                    return source_obj
        return None

    def execute(self, context):
        scene = context.scene
        mmr_property = scene.mmr_property
        preset_name = mmr_property.rig_preset_name
        preset_dict = preset_dict_dict.get('rig', {})
        if preset_name not in preset_dict:
            self.report({'ERROR'}, f'Preset "{preset_name}" not found')
            return {'CANCELLED'}

        preset = preset_dict[preset_name]
        source_arm = self._find_source_armature(context, preset)
        if source_arm is None:
            self.report({'ERROR'}, "Cannot find source armature. Select source armature or *_Rig generated from it.")
            return {'CANCELLED'}

        # Make source armature active so RIG2 reads and rebuilds from current preset mapping.
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        source_arm.select_set(True)
        context.view_layer.objects.active = source_arm
        set_bone_type(source_arm.pose, preset)
        rig.RIG2(context)
        self.report({'INFO'}, f'Controllers regenerated by preset "{preset_name}"')
        return {'FINISHED'}

def set_keymap():
    wm = bpy.context.window_manager
    #kc= wm.keyconfigs['Blender user']
    kc= wm.keyconfigs.user
    km = kc.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.type=='S' and kmi.shift==False and kmi.ctrl==False and kmi.alt==False:
            kmi.active=False
    km = kc.keymaps['Pose']
    for kmi in km.keymap_items:
        if kmi.type=='A' and kmi.shift==False and kmi.ctrl==False:
            kmi.active=False
    kmi = km.keymap_items.new('mmr.qa_assign', 'A', 'PRESS')
    kmi = km.keymap_items.new('mmr.qa_assign_invert', 'A', 'PRESS',alt=True)
    kmi = km.keymap_items.new('mmr.qa_skip', 'S', 'PRESS')

def reset_keymap():
    wm = bpy.context.window_manager
    #kc= wm.keyconfigs['Blender user']
    kc= wm.keyconfigs.user
    km = kc.keymaps['Pose']
    for kmi in km.keymap_items:
        if kmi.type=='A' and kmi.shift==False and kmi.ctrl==False:
            kmi.active=True
        if kmi.idname=='mmr.qa_assign' or kmi.idname== 'mmr.qa_assign_invert' or kmi.idname=='mmr.qa_skip':
            km.keymap_items.remove(kmi)
    km = kc.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.type=='S' and kmi.shift==False and kmi.ctrl==False and kmi.alt==False:
            kmi.active=True

class OT_QA_Start(bpy.types.Operator):
    bl_idname = "mmr.qa_start" # python 提示
    bl_label = "QA Start"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        scene=context.scene
        mmr_property=scene.mmr_property
        if rig.check_arm()==False:
            return{"CANCELLED"}
        mmr_property.quick_assign_mod=True
        mmr_property.quick_assign_index=1
        set_keymap()
        
        bpy.ops.object.mode_set(mode = 'POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        first_bone=context.view_layer.objects.active.data.bones[0]
        first_bone.select=True
        context.view_layer.objects.active.data.bones.active=first_bone

        return{"FINISHED"}

def QA_End(context):
    scene=context.scene
    mmr_property=scene.mmr_property
    mmr_property.quick_assign_mod=False
    mmr_property.quick_assign_index=1
    reset_keymap()

class OT_QA_End(bpy.types.Operator):
    bl_idname = "mmr.qa_end" # python 提示
    bl_label = "QA End"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        QA_End(context)
        
        return{"FINISHED"}

class OT_QA_Assign(bpy.types.Operator):
    bl_idname = "mmr.qa_assign" # python 提示
    bl_label = "QA Assign"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        scene=context.scene
        mmr_property=scene.mmr_property
        if mmr_property.quick_assign_mod==False:
            return{"FINISHED"}

        pose_bone = context.active_pose_bone or \
                    context.active_object.pose.bones.get(context.active_bone.name, None)
        if pose_bone is None:
            return{"FINISHED"}

        bone=pose_bone.bone
        if len(bone.children)!=0:
            child_bone=bone.children[0]
            bone.select=False
            child_bone.select=True
            context.view_layer.objects.active.data.bones.active=child_bone

        bone_type=rigify_bone_type_list[mmr_property.quick_assign_index]

        pose_bone.mmr_bone_type=bone_type
        pose_bone.mmr_bone_invert=False

        mmr_property.quick_assign_index+=1
        if mmr_property.quick_assign_index >= len(rigify_bone_type_list):
            QA_End(context)
        
        return{"FINISHED"}

class OT_QA_Assign_Invert(bpy.types.Operator):
    bl_idname = "mmr.qa_assign_invert" # python 提示
    bl_label = "QA Assign Invert"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        scene=context.scene
        mmr_property=scene.mmr_property
        if mmr_property.quick_assign_mod==False:
            return{"FINISHED"}

        pose_bone = context.active_pose_bone or \
                    context.active_object.pose.bones.get(context.active_bone.name, None)
        if pose_bone is None:
            return{"FINISHED"}

        bone=pose_bone.bone
        if len(bone.children)!=0:
            child_bone=bone.children[0]
            bone.select=False
            child_bone.select=True
            context.view_layer.objects.active.data.bones.active=child_bone

        bone_type=rigify_bone_type_list[mmr_property.quick_assign_index]

        pose_bone.mmr_bone_type=bone_type
        pose_bone.mmr_bone_invert=True

        mmr_property.quick_assign_index+=1
        if mmr_property.quick_assign_index >= len(rigify_bone_type_list):
            QA_End(context)
        
        return{"FINISHED"}

class OT_QA_Skip(bpy.types.Operator):
    bl_idname = "mmr.qa_skip" # python 提示
    bl_label = "QA Skip"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        scene=context.scene
        mmr_property=scene.mmr_property

        pose_bone = context.active_pose_bone or \
                    context.active_object.pose.bones.get(context.active_bone.name, None)

        bone=pose_bone.bone
        bone.select=False
        bone.select=True

        if mmr_property.quick_assign_mod==False:
            return{"FINISHED"}
        mmr_property.quick_assign_index+=1
        if mmr_property.quick_assign_index >= len(rigify_bone_type_list):
            QA_End(context)

        return{"FINISHED"}

#UI菜单部分

class Mmr_Panel_Base(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MMR"
    bl_context = "objectmode"

class MMR_Arm_Panel(Mmr_Panel_Base):
    bl_idname="MMR_PT_panel_12"
    bl_label = "Controller Preset"
    bl_context = ""
    

    def draw(self, context):
        layout = self.layout
        scene=context.scene
        mmr_property=scene.mmr_property
        row = layout.row()
        # Rig type field
        if mmr_property.quick_assign_mod:
            bone_type=rigify_bone_type_list[mmr_property.quick_assign_index]
            bone_type_C=''
            if bone_type in bone_translate_dict_C:
                bone_type_C=bone_translate_dict_C[bone_type]
            row = layout.row()
            row.label(text="正在指定骨骼：")
            row.label(text=bone_type,translate =False)
            row = layout.row()
            row.label(text=bone_type_C,translate =False)
            layout.operator("mmr.qa_assign",text='Assign (Hot Key:A)')
            layout.operator("mmr.qa_assign_invert",text='Assign Invert (Hot Key:Alt+A)')
            layout.operator("mmr.qa_skip",text='Skip (Hot Key:S)')
            layout.operator("mmr.qa_end",text='End Quick Assign')
        else:
            row.prop(mmr_property, 'rig_preset_name', text='preset')
            if mmr_property.rig_preset_name not in built_in_rig_dict_list or mmr_property.debug:
                row = layout.row()
                row.operator("mmr.add_preset")
                row.operator("mmr.delete_preset")
                row = layout.row()
                row.operator("mmr.read_preset")
                row.operator("mmr.overwrite_preset")
            else:
                row = layout.row()
                row.operator("mmr.add_preset")
                row.operator("mmr.read_preset")
            layout.operator("mmr.reload_presets", text="Reload preset.json")
            layout.operator("mmr.rig_preset",text='Generate Rig with Preset')
            ot=layout.operator("mmr.rig_preset",text='Generate Rig Without Preset')
            ot.read=False
            layout.operator("mmr.qa_start",text='Start Quick Assign')
            layout.operator("mmr.copy_ai_prompt", text="Generate AI Prompt")
            layout.operator("mmr.add_preset_from_clipboard", text="Add preset from clipboard")
            layout.operator("mmr.fix_all_controllers_by_preset", text="Fix all controllers by preset")
            layout.prop(mmr_property, "extra_options1", toggle=True,text='Extra Options')
            if mmr_property.extra_options1:
                layout.prop(mmr_property,'bent_IK_bone',text="Bent IK bone")
                #layout.prop(mmr_property,'wrist_rotation_follow',text="Wrist rotation follow arm")
                layout.prop(mmr_property,'auto_shoulder',text="Shoulder IK")
                #layout.prop(mmr_property,'solid_rig',text="Replace the controller")
                layout.prop(mmr_property,'pole_target',text="Use pole target")
                layout.prop(mmr_property,'extra_source_controllers',text="Extra source controllers")

class MMR_Bone_Panel(Mmr_Panel_Base):
    bl_idname="MMR_PT_panel_11"
    bl_label = 'MMR Bone Type'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'

    @classmethod
    def poll(cls, context):
        return context.active_bone

    def draw(self, context):
        pose_bone = context.active_pose_bone or \
                    context.active_object.pose.bones.get(context.active_bone.name, None)
        if pose_bone is None:
            return

        layout = self.layout

        c = layout.column()

        row = c.row(align=True)
        layout.prop(pose_bone, 'mmr_bone_type', text='Bone Type',translate =False)
        layout.prop(pose_bone, 'mmr_bone_invert', text='Invert')

class MMR_Retarget_Panel(Mmr_Panel_Base):
    bl_idname="MMR_PT_panel_13"
    bl_label = "Retarget" #菜单名
    bl_context = ""

    def draw(self, context):
        scene=context.scene
        mmr_property=scene.mmr_property
        layout = self.layout
        row = layout.row()
        row.prop(mmr_property, 'retarget_preset_name', text='preset')
        if mmr_property.retarget_preset_name not in built_in_retarget_dict_list or mmr_property.debug:
            row = layout.row()
            row.operator("mmr.add_preset").preset_type='retarget'
            row.operator("mmr.delete_preset").preset_type='retarget'
            row = layout.row()
            row.operator("mmr.read_preset").preset_type='retarget'
            row.operator("mmr.overwrite_preset").preset_type='retarget'
        else:
            row = layout.row()
            row.operator("mmr.add_preset").preset_type='retarget'
            row.operator("mmr.read_preset").preset_type='retarget'
        layout.operator("mmr.reload_presets", text="Reload preset.json")
        layout.label(text="Select rigify controller then press the button")
        #row=layout.row()
        #row.label(text='Arm:',translate =False)
        #row.prop(mmr_property, 'IKFK_arm',expand=True)
        #row=layout.row()
        #row.label(text='Leg:',translate =False)
        #row.prop(mmr_property, 'IKFK_leg',expand=True)
        layout.operator("mmr.import_mixamo",text="Import FBX/BVH")
        layout.operator("mmr.import_vmd",text="Import VMD")
        layout.operator("mmr.export_vmd",text="Bake and export VMD animation")
        layout.prop(mmr_property, "extra_options2", toggle=True,text='Extra Options')
        if mmr_property.extra_options2:
            layout.prop(mmr_property,'fade_in_out',text="Fade in out")
            layout.prop(mmr_property,'auto_action_scale',text="Auto animation scale")
            if mmr_property.auto_action_scale==False:
                layout.prop(mmr_property,'action_scale',text="Animation scale")
            layout.prop(mmr_property,'lock_location',text="Lock animation location")
            layout.prop(mmr_property,'import_as_NLA_strip',text="Import as NLA strip")
Class_list=[
    MMR_Bone_Panel,MMR_Arm_Panel,OT_Add_Preset,OT_Delete_Preset,OT_Read_Preset,OT_Overwrite_Preset,OT_Copy_AI_Prompt,OT_Reload_Presets,OT_Add_Preset_From_Clipboard,OT_Rig_Preset,OT_Fix_All_Controllers_By_Preset,
    OT_QA_Start,OT_QA_End,OT_QA_Assign,OT_QA_Assign_Invert,OT_QA_Skip,MMR_Retarget_Panel,
]
