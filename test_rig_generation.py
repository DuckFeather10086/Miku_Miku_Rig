#!/usr/bin/env python3
"""
无头Blender脚本：测试MMR插件生成控制器
用法: blender --background --python test_rig_generation.py
"""

import bpy
import sys
import os

# 添加插件路径到sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
addon_path = os.path.join(script_dir, "MikuMikuRig")
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)

# 设置blend文件路径
blend_file = os.path.join(script_dir, "MikuMikuRig", "mmr_operators", "chisaBody5.blend")
armature_name = "Genesis 9"
preset_name = "Genesis9"  # 使用Genesis9预设

def setup_addon():
    """设置并启用插件"""
    print("=" * 60)
    print("设置MMR插件...")
    
    addon_name = "MikuMikuRig"
    
    try:
        # 确保插件目录在路径中
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        # 尝试导入并注册插件
        import importlib
        
        # 先尝试直接导入
        try:
            import MikuMikuRig
            # 如果已经注册过，先取消注册
            if hasattr(MikuMikuRig, 'register'):
                try:
                    MikuMikuRig.unregister()
                except:
                    pass
            MikuMikuRig.register()
            print(f"✓ 插件已手动注册")
        except ImportError as e:
            # 如果导入失败，尝试通过bpy.ops启用
            print(f"⚠ 直接导入失败，尝试通过bpy启用: {e}")
            
            # 获取插件路径
            addon_path = os.path.join(script_dir, addon_name)
            if os.path.exists(addon_path):
                # 尝试启用插件
                try:
                    bpy.ops.preferences.addon_enable(module=addon_name)
                    print(f"✓ 插件已通过bpy启用")
                except:
                    # 最后尝试：手动注册
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        addon_name, 
                        os.path.join(addon_path, "__init__.py")
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[addon_name] = module
                        spec.loader.exec_module(module)
                        if hasattr(module, 'register'):
                            module.register()
                        print(f"✓ 插件已通过文件加载注册")
                    else:
                        raise Exception("无法加载插件模块")
        
        # 验证插件是否可用
        if hasattr(bpy.types.Scene, 'mmr_property'):
            print(f"✓ 插件属性已注册")
        else:
            print(f"⚠ 警告: 插件属性未找到，但继续执行...")
        
        return True
        
    except Exception as e:
        print(f"✗ 插件注册失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_blend_file(filepath):
    """加载blend文件"""
    print("=" * 60)
    print(f"加载blend文件: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"✗ 文件不存在: {filepath}")
        return False
    
    try:
        # 清除当前场景
        bpy.ops.wm.read_homefile(app_template="")
        
        # 加载blend文件
        bpy.ops.wm.open_mainfile(filepath=filepath)
        print(f"✓ 文件加载成功")
        return True
    except Exception as e:
        print(f"✗ 加载文件失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_armature(name):
    """查找指定的骨骼对象"""
    print("=" * 60)
    print(f"查找骨骼: {name}")
    
    # 在所有场景中查找
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and obj.name == name:
            print(f"✓ 找到骨骼: {obj.name}")
            return obj
    
    # 如果精确匹配失败，尝试部分匹配
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and name in obj.name:
            print(f"✓ 找到相似骨骼: {obj.name}")
            return obj
    
    # 列出所有骨骼对象
    print("可用的骨骼对象:")
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            print(f"  - {obj.name}")
    
    print(f"✗ 未找到骨骼: {name}")
    return None

def setup_armature_context(armature):
    """设置骨骼上下文"""
    print("=" * 60)
    print("设置骨骼上下文...")
    
    try:
        # 清除选择
        bpy.ops.object.select_all(action='DESELECT')
        
        # 设置活动对象
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        
        print(f"✓ 活动对象已设置为: {armature.name}")
        return True
    except Exception as e:
        print(f"✗ 设置上下文失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_preset_if_needed(armature):
    """如果需要，加载预设"""
    print("=" * 60)
    print("检查预设...")
    
    try:
        # 确保预设模块已加载
        import importlib
        try:
            from MikuMikuRig.mmr_operators import preset
            # 重新加载以确保预设数据是最新的
            importlib.reload(preset)
        except ImportError:
            # 如果导入失败，尝试直接导入
            sys.path.insert(0, os.path.join(script_dir, "MikuMikuRig", "mmr_operators"))
            import preset
            importlib.reload(preset)
        
        # 确保预设数据已读取
        if not hasattr(preset, 'preset_dict_dict') or not preset.preset_dict_dict:
            print("⚠ 预设数据未加载，尝试读取...")
            preset.read_json('rig')
            preset.read_json('retarget')
        
        # 检查是否有预设数据
        scene = bpy.context.scene
        if not hasattr(scene, 'mmr_property'):
            print("⚠ 场景属性未初始化，尝试初始化...")
            # 尝试初始化
            try:
                from MikuMikuRig import MMR_property
                if not hasattr(bpy.types.Scene, 'mmr_property'):
                    bpy.types.Scene.mmr_property = bpy.props.PointerProperty(type=MMR_property)
            except:
                pass
        
        mmr_property = scene.mmr_property
        
        # 检查是否有可用的预设
        preset_dict = preset.preset_dict_dict.get('rig', {})
        if not preset_dict:
            print("⚠ 没有可用的预设，将使用默认设置（需要手动设置骨骼类型）")
            return True
        
        # 尝试使用Genesis9预设，如果不存在则使用第一个可用预设
        # 从全局变量获取预设名称
        target_preset_name = globals().get('preset_name', 'Genesis9')
        preset_names = list(preset_dict.keys())
        if preset_names:
            # 优先使用Genesis9预设
            if target_preset_name in preset_dict:
                preset_name = target_preset_name
                print(f"使用指定预设: {preset_name}")
            else:
                preset_name = preset_names[0]
                print(f"指定预设 '{target_preset_name}' 不存在，使用第一个可用预设: {preset_name}")
            
            # 设置预设名称
            try:
                mmr_property.rig_preset_name = preset_name
            except:
                print("⚠ 无法设置预设名称属性")
            
            # 读取预设
            if preset_name in preset_dict:
                preset_data = preset_dict[preset_name]
                # 预设数据格式: {bone_name: [bone_type, invert]}
                if isinstance(preset_data, dict):
                    preset.set_bone_type(armature.pose, preset_data)
                    print(f"✓ 预设已应用到 {len(preset_data)} 个骨骼")
                else:
                    print(f"⚠ 预设数据格式不正确: {type(preset_data)}")
                return True
        
        print("⚠ 没有可用的预设，将使用默认设置")
        return True
    except Exception as e:
        print(f"⚠ 预设加载失败，将使用默认设置: {e}")
        import traceback
        traceback.print_exc()
        return True

def generate_rig(armature):
    """生成控制器"""
    print("=" * 60)
    print("开始生成控制器...")
    
    try:
        from MikuMikuRig.mmr_operators import rig
        
        # 确保在正确的上下文中
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # 调用RIG2函数
        context = bpy.context
        result = rig.RIG2(context)
        
        if result:
            print("✓ 控制器生成成功!")
            
            # 查找生成的rig
            generated_rig = None
            for obj in bpy.data.objects:
                if obj.type == 'ARMATURE' and '_Rig' in obj.name:
                    generated_rig = obj
                    break
            
            if generated_rig:
                print(f"✓ 生成的控制器: {generated_rig.name}")
                # 确保rig在场景中
                if generated_rig.name not in bpy.context.scene.objects:
                    bpy.context.collection.objects.link(generated_rig)
                    print(f"✓ 已将rig添加到场景collection")
                # 确保rig可见
                generated_rig.hide_set(False)
                generated_rig.hide_viewport = False
                # 设置为活动对象
                bpy.context.view_layer.objects.active = generated_rig
                generated_rig.select_set(True)
                print(f"✓ rig已设置为活动对象")
            else:
                # 如果没有找到，列出所有armature
                print("⚠ 未找到生成的rig，当前所有armature对象:")
                for obj in bpy.data.objects:
                    if obj.type == 'ARMATURE':
                        print(f"  - {obj.name} (在场景: {obj.name in bpy.context.scene.objects})")
            
            return True
        else:
            print("✗ 控制器生成返回False")
            return False
            
    except Exception as e:
        print(f"✗ 生成控制器失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("MMR插件测试脚本 - 无头模式")
    print("=" * 60)
    
    # 1. 设置插件
    if not setup_addon():
        print("\n✗ 插件设置失败，退出")
        return 1
    
    # 2. 加载blend文件
    if not load_blend_file(blend_file):
        print("\n✗ 文件加载失败，退出")
        return 1
    
    # 3. 查找骨骼
    armature = find_armature(armature_name)
    if not armature:
        print("\n✗ 未找到骨骼，退出")
        return 1
    
    # 4. 设置上下文
    if not setup_armature_context(armature):
        print("\n✗ 上下文设置失败，退出")
        return 1
    
    # 5. 加载预设（可选）
    load_preset_if_needed(armature)
    
    # 6. 生成控制器
    if not generate_rig(armature):
        print("\n✗ 控制器生成失败")
        return 1
    
    print("\n" + "=" * 60)
    print("✓ 所有步骤完成!")
    print("=" * 60)
    
    # 保存结果
    output_file = blend_file.replace('.blend', '_rigged.blend')
    try:
        bpy.ops.wm.save_as_mainfile(filepath=output_file)
        print(f"✓ 结果已保存到: {output_file}")
    except Exception as e:
        print(f"⚠ 保存失败: {e}")
        print("但rig已生成，可以在Blender中手动保存")
    
    # 列出所有生成的armature对象
    print("\n生成的armature对象:")
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            print(f"  - {obj.name} (在场景中: {obj.name in bpy.context.scene.objects})")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n✗ 发生未处理的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
