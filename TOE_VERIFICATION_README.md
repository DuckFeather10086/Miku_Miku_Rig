# 脚趾无头Blender回归验证

这个脚本用于在无头Blender模式下验证 `chisaBody5.blend` 文件中的脚趾骨骼、约束和控制器。

## 使用方法

### 方法1: 使用提供的shell脚本（推荐）

```bash
cd /home/duckfeather/Miku_Miku_Rig
./run_toe_verification.sh
```

### 方法2: 直接运行Blender命令

```bash
cd /home/duckfeather/Miku_Miku_Rig
blender MikuMikuRig/mmr_operators/chisaBody5.blend --background --python verify_toe_regression.py
```

### 方法3: 指定Blender路径

如果Blender不在PATH中，可以设置环境变量：

```bash
export BLENDER=/path/to/blender
./run_toe_verification.sh
```

或者直接使用完整路径：

```bash
/path/to/blender MikuMikuRig/mmr_operators/chisaBody5.blend --background --python verify_toe_regression.py
```

## 验证内容

脚本会检查以下内容：

### 第一部分：源骨骼脚趾检查

1. **基础脚趾骨骼存在性**
   - `toe.L` 和 `toe.R` 是否存在于源骨骼中

2. **分段脚趾骨骼存在性**（可选）
   - 每只脚5根脚趾，每根2节（thumb, index, middle, ring, pinky）
   - 共20个分段脚趾骨骼

3. **源骨骼脚趾约束**
   - `toe.L` 和 `toe.R` 是否有 `rel_` 开头的约束
   - 约束的目标骨骼

### 第二部分：生成的rig脚趾检查（如果rig已生成）

1. **Rig脚趾骨骼**
   - 基础脚趾控制器：`toe.L`, `toe.R`
   - DEF脚趾骨骼：`DEF-toe.L`, `DEF-toe.R`
   - DEF分段脚趾骨骼（可选）
   - ToeTipIK控制器：`ToeTipIK_L`, `ToeTipIK_R`（可选）

2. **Rig父级辅助骨骼**
   - `toe.L_parent`
   - `toe.R_parent`
   - `ToeTipIK_L_parent`
   - `ToeTipIK_R_parent`

3. **Rig脚趾约束**
   - DEF脚趾骨骼的约束配置
   - ToeTipIK约束（如果存在）

## 输出说明

脚本会输出详细的验证结果：

- `✓` 表示检查通过
- `✗` 表示检查失败
- `⚠` 表示警告（通常是可选项目）

最后会显示验证总结，包括所有检查项的通过/失败状态。

## 注意事项

1. **如果文件尚未生成rig**：
   - 脚本会跳过rig相关的检查
   - 提示先运行 `test_rig_generation.py` 生成rig

2. **分段脚趾骨骼是可选的**：
   - 如果源骨骼中没有分段脚趾，这是正常的
   - 脚本会标记为警告而不是错误

3. **ToeTipIK控制器是可选的**：
   - 某些预设可能不包含ToeTipIK控制器
   - 脚本会标记为警告而不是错误

## 故障排除

### 1. 找不到Blender

确保Blender已安装并在PATH中，或使用环境变量指定路径。

### 2. 找不到源骨骼

脚本会列出所有可用的armature对象，检查输出中的骨骼名称列表。

### 3. 文件加载失败

检查 `chisaBody5.blend` 文件是否存在且可读。

## 退出代码

- `0`: 所有验证通过
- `1`: 部分验证失败或发生错误
