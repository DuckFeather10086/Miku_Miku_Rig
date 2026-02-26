# MMR插件无头模式测试脚本

这个脚本用于在无头Blender模式下测试MMR插件生成控制器的功能。

## 使用方法

### 方法1: 使用提供的shell脚本（推荐）

```bash
cd /home/duckfeather/Miku_Miku_Rig
./run_test.sh
```

### 方法2: 直接运行Blender命令

```bash
cd /home/duckfeather/Miku_Miku_Rig
blender --background --python test_rig_generation.py
```

### 方法3: 指定Blender路径

如果Blender不在PATH中，可以设置环境变量：

```bash
export BLENDER=/path/to/blender
./run_test.sh
```

或者直接使用完整路径：

```bash
/path/to/blender --background --python test_rig_generation.py
```

## 脚本功能

1. **自动加载插件**: 脚本会自动检测并加载MMR插件
2. **加载blend文件**: 自动加载 `chisaBody5.blend` 文件
3. **查找骨骼**: 查找名为 "Genesis 9" 的骨骼对象
4. **应用预设**: 如果存在预设，会自动应用
5. **生成控制器**: 调用RIG2函数生成rigify控制器

## 配置

可以在 `test_rig_generation.py` 中修改以下变量：

```python
# blend文件路径
blend_file = os.path.join(script_dir, "MikuMikuRig", "mmr_operators", "chisaBody5.blend")

# 骨骼名称
armature_name = "Genesis 9"
```

## 故障排除

### 1. 找不到Blender

确保Blender已安装并在PATH中，或使用环境变量指定路径。

### 2. 插件加载失败

检查插件目录结构是否正确：
```
MikuMikuRig/
  ├── __init__.py
  ├── mmr_operators/
  │   ├── __init__.py
  │   ├── rig.py
  │   ├── preset.py
  │   └── ...
  └── ...
```

### 3. 找不到骨骼

脚本会列出所有可用的骨骼对象，检查输出中的骨骼名称列表。

### 4. 预设加载失败

如果预设加载失败，脚本会继续执行，但可能需要手动设置骨骼类型。

## 输出

脚本会输出详细的执行日志，包括：
- ✓ 成功步骤
- ✗ 失败步骤
- ⚠ 警告信息

## 注意事项

1. 无头模式下某些GUI相关功能可能不可用
2. 如果生成失败，检查错误日志以了解具体原因
3. 确保所有依赖（如rigify插件）已安装并启用
