# Miku_Miku_Rig

MikuMikuRig 是一个以 Rigify 生成为核心的 Blender 插件。当前分支参考原作者的模块化思路进行了重构，保留主控生成功能，并将动画导入/布料流程替换为更适合通用角色工作流的姿势库与胶囊碰撞体功能。

20260313：

- 支持 Blender 5.0
- 插件结构改为模块化
- 删除动画导入 / 布料转换模块
- 新增 JSONL 姿势库
- 新增挂载到源骨骼的低面数胶囊碰撞体

MikuMikuRig is a Blender add-on focused on Rigify controller generation. This branch has been refactored into a modular structure, keeping the main rig generation workflow while replacing animation import and cloth conversion with a JSONL pose library and bone-attached capsule colliders.

## 功能 Functions

- 一键为任意人形骨架生成 Rigify 控制器
- 支持预设驱动的骨骼映射，并可在已有 `_Rig` 上重新生成
- 提供 JSONL 姿势库：保存 / 加载 / 删除 Rigify 姿势
- 可为源骨骼批量生成低面数胶囊碰撞体
- 保留最小 IK 迭代次数设置工具

- Generate Rigify controllers for humanoid armatures
- Use preset-driven bone mapping and regenerate from an existing `_Rig`
- Save / load / delete Rigify poses with a JSONL pose library
- Choose a custom pose-library directory
- Optionally sync FK/IK before saving poses
- Save poses for all bones, including hidden bone layers / collections
- Generate low-poly capsule colliders attached to source bones
- Keep a utility for setting minimum IK iterations




![picture1](https://github.com/958261649/Miku_Miku_Rig/blob/main/preview/QQ%E6%88%AA%E5%9B%BE20210616125213.png)

![picture2](https://github.com/958261649/Miku_Miku_Rig/blob/main/preview/QQ%E6%88%AA%E5%9B%BE20210616125406.png)

视频演示：
https://www.bilibili.com/video/BV1vZ4y1P71a/

## 文档 / Docs

- **[AI：从骨架树生成 Rigify 骨骼映射](docs/AI_RIGIFY_MAPPING_TOOL.md)** — 供 AI 使用的工具说明：根据输出的骨架树结构，自动生成匹配 Rigify 控制器的 metarig 骨骼映射（preset.json 格式）。
