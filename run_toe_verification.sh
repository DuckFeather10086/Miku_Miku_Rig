#!/bin/bash
# 运行脚趾无头Blender回归验证脚本

# 获取脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERIFY_SCRIPT="$SCRIPT_DIR/verify_toe_regression.py"
# 优先使用rigged文件，如果不存在则使用原始文件
RIGGED_FILE="$SCRIPT_DIR/MikuMikuRig/mmr_operators/chisaBody5_rigged.blend"
BLEND_FILE="$SCRIPT_DIR/MikuMikuRig/mmr_operators/chisaBody5.blend"
if [ -f "$RIGGED_FILE" ]; then
    BLEND_FILE="$RIGGED_FILE"
fi

# 查找Blender可执行文件
BLENDER=""
if command -v blender &> /dev/null; then
    BLENDER="blender"
elif [ -f "/usr/bin/blender" ]; then
    BLENDER="/usr/bin/blender"
elif [ -f "/usr/local/bin/blender" ]; then
    BLENDER="/usr/local/bin/blender"
elif [ -d "/opt/blender" ]; then
    # 查找最新版本的blender
    BLENDER=$(find /opt/blender -name "blender" -type f | head -1)
fi

if [ -z "$BLENDER" ]; then
    echo "错误: 未找到Blender可执行文件"
    echo "请安装Blender或设置BLENDER环境变量"
    echo "例如: export BLENDER=/path/to/blender"
    exit 1
fi

echo "使用Blender: $BLENDER"
echo "验证脚本: $VERIFY_SCRIPT"
echo "Blend文件: $BLEND_FILE"
echo ""

# 运行无头模式验证
"$BLENDER" "$BLEND_FILE" --background --python "$VERIFY_SCRIPT"

exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✓ 脚趾验证成功完成!"
else
    echo ""
    echo "✗ 脚趾验证失败，退出代码: $exit_code"
fi

exit $exit_code
