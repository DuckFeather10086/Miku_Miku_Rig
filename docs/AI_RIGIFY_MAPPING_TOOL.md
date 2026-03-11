# AI 工具说明：Rigify 骨骼映射配置

本文档说明 Miku Miku Rig 的 metarig **支持哪些控制器**，以及如何让 AI 根据**骨架结构和骨骼名称语义**来配置对应的映射。

## 1. 使用方式

- 插件内提供 **「Generate AI Prompt」** 按钮（Controller Preset 面板），一键生成**英文 prompt** 并复制到剪贴板。
- 用户将当前**骨架的骨骼列表或树结构**交给 LLM，并粘贴该 prompt；LLM 根据 prompt 中列出的**支持的控制器**和**规则**，结合骨架结构与名称语义，输出符合 `preset.json` 格式的映射。
- 输出格式：`"源骨架骨骼名": ["Rigify控制器ID", invert]`，写入 `preset.json` 的 `rig` 或 `retarget` 对应预设即可。

## 2. Metarig 支持的控制器列表

以下为 metarig 支持的 Rigify 控制器 ID（与 `preset.py` 中 `rigify_bone_type_list` 一致）。AI 仅可配置这些 ID；未支持的控制器不要映射。

### 根与躯干（脊柱必须满足规则）

| 控制器 ID | 语义说明 |
|-----------|----------|
| `Root` | 根/全局父骨骼 |
| `Center` | 中心（重定向用） |
| `spine` | 下半身/骨盆 |
| `spine.001` … `spine.007` | 脊柱 1～7，从骨盆向头 |

**重要规则**：

- **`spine.007` 必须映射为头骨骼（head）**。程序假定 head 对应 `spine.007`，否则可能出现未预期错误。
- 若源骨架的脊柱/颈/头骨骼**多于**我们提供的 7 节（spine → spine.007），应**自行缩短匹配**：只映射到 head 为止，且 **head 必须对应 spine.007**；多余的更上方脊柱可省略或合并，不得让 spine.007 对应非头骨骼。

### 眼睛（可选）

| 控制器 ID | 语义 |
|-----------|------|
| `eye.L` / `eye.R` | 左眼 / 右眼 |

### 上肢

| 控制器 ID | 语义 |
|-----------|------|
| `shoulder.L` / `shoulder.R` | 肩 |
| `upper_arm.L` / `upper_arm.R` | 大臂 |
| `ArmTwist_L` / `ArmTwist_R` | 大臂扭转（可选） |
| `forearm.L` / `forearm.R` | 小臂 |
| `HandTwist_L` / `HandTwist_R` | 腕扭转（可选） |
| `hand.L` / `hand.R` | 手腕 |
| `thumb.01.L`–`thumb.03.L`（及 `.R`） | 拇指 3 节 |
| `f_index.01.L`–`f_index.03.L`（及 `.R`） | 食指 3 节 |
| `f_middle.01.L`–`f_middle.03.L`（及 `.R`） | 中指 3 节 |
| `f_ring.01.L`–`f_ring.03.L`（及 `.R`） | 无名指 3 节 |
| `f_pinky.01.L`–`f_pinky.03.L`（及 `.R`） | 小指 3 节 |

### 下肢

| 控制器 ID | 语义 |
|-----------|------|
| `thigh.L` / `thigh.R` | 大腿 |
| `shin.L` / `shin.R` | 小腿 |
| `foot.L` / `foot.R` | 脚掌 |
| `toe.L` / `toe.R` | 脚尖（整根，可选） |
| `ToeTipIK_L` / `ToeTipIK_R` | 脚尖 IK（可选） |
| `LegIK_L` / `LegIK_R` | 腿 IK（重定向用） |

### 脚趾（可选）

左侧：`toe_thumb.01.L`, `toe_thumb.02.L`, `toe_index.01.L`, `toe_index.02.L`, `toe_middle.01.L`, `toe_middle.02.L`, `toe_ring.01.L`, `toe_ring.02.L`, `toe_pinky.01.L`, `toe_pinky.02.L`  
右侧：将 `.L` 换为 `.R`。

## 3. 输出格式与代码对应

- 每条映射：`"源骨架骨骼名": ["Rigify控制器ID", invert]`，其中 `invert` 为布尔（骨骼方向与控制器相反时设为 `true`）。
- 预设写入 `MikuMikuRig/mmr_operators/preset.json` 的 `rig` 或 `retarget` 下对应预设名；`set_bone_type(pose, preset)` 会按此配置骨骼类型与 invert。

---

插件内「Generate AI Prompt」生成的英文 prompt 已包含上述控制器列表与 spine.007=head、缩短脊柱匹配等规则，供直接粘贴给 LLM 使用。
