#!/bin/bash
# 运行无头Blender测试脚本

# 获取脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEST_SCRIPT="$SCRIPT_DIR/test_rig_generation.py"

# 查找Blender可执行文件
# 尝试常见的Blender路径
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
echo "测试脚本: $TEST_SCRIPT"
echo ""

# 运行无头模式
"$BLENDER" --background --python "$TEST_SCRIPT"

exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✓ 测试成功完成!"
else
    echo ""
    echo "✗ 测试失败，退出代码: $exit_code"
fi

exit $exit_code
