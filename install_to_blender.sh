#!/bin/bash
# MikuMikuRig 安装脚本
# 将插件安装到 Blender 5.0 的插件目录

BLENDER_VERSION="5.0"
ADDON_NAME="MikuMikuRig"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/$ADDON_NAME"
TARGET_DIR="$HOME/.config/blender/$BLENDER_VERSION/scripts/addons/$ADDON_NAME"

echo "========================================="
echo "MikuMikuRig 安装脚本"
echo "========================================="
echo ""
echo "源目录: $SOURCE_DIR"
echo "目标目录: $TARGET_DIR"
echo ""

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo "错误: 找不到 $SOURCE_DIR 目录"
    exit 1
fi

# 创建目标目录（如果不存在）
mkdir -p "$(dirname "$TARGET_DIR")"

# 如果目标目录已存在，询问是否覆盖
if [ -d "$TARGET_DIR" ]; then
    echo "警告: 目标目录已存在: $TARGET_DIR"
    read -p "是否要覆盖现有安装? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安装已取消"
        exit 0
    fi
    rm -rf "$TARGET_DIR"
fi

# 复制插件文件
echo "正在复制插件文件..."
cp -r "$SOURCE_DIR" "$TARGET_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 安装成功!"
    echo ""
    echo "下一步:"
    echo "1. 打开 Blender 5.0"
    echo "2. 进入 Edit > Preferences > Add-ons"
    echo "3. 搜索 'MikuMikuRig'"
    echo "4. 勾选插件旁边的复选框以启用"
    echo ""
else
    echo ""
    echo "✗ 安装失败"
    exit 1
fi
