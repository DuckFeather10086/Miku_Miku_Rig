# Miku_Miku_Rig
MikuMikuRig是一款集生成控制器，自动导入动画，自动布料为一体的blender插件。
注意：Blender3.0需要安装Rigify修复补丁


20260302：支持 Blender 5.0；支持脚趾细节映射。

MikuMikuRig is a Blender plugin that can generates rig, automatically imports animations as nla track, and automatically generates cloth.

## 功能 Functions
一键为任何骨骼生成Rigify控制器

一键为生成的控制器导入任何FBX动画，BVH动画和VMD动画。导入的动画将作为NLA片段存在。

一键把MMD刚体物理转换为布料系统

一键美化MMD骨骼

Generates Rigify controllers for any armature with one click.

Import any FBX,BVH and VMD animations as NLA strip with one click.

Converts MMD rigid bodies to cloth system with one click.

Decorate MMD armature with one click

![picture1](https://github.com/958261649/Miku_Miku_Rig/blob/main/preview/QQ%E6%88%AA%E5%9B%BE20210616125213.png)

![picture2](https://github.com/958261649/Miku_Miku_Rig/blob/main/preview/QQ%E6%88%AA%E5%9B%BE20210616125406.png)

视频演示：
https://www.bilibili.com/video/BV1vZ4y1P71a/

## 文档 / Docs

- **[AI：从骨架树生成 Rigify 骨骼映射](docs/AI_RIGIFY_MAPPING_TOOL.md)** — 供 AI 使用的工具说明：根据输出的骨架树结构，自动生成匹配 Rigify 控制器的 metarig 骨骼映射（preset.json 格式）。
