#!/bin/bash
# 金谷园饺子馆 CLI - 跨平台安装脚本
# 支持 macOS / Linux / Windows(WSL)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    print_info "检测到操作系统: $OS"
}

# 检测 Python
detect_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
        print_success "找到 Python: $PYTHON_VERSION"
        return 0
    elif command -v python &> /dev/null; then
        # 检查是否是 Python 3
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        if [[ $PYTHON_VERSION == 3.* ]]; then
            PYTHON_CMD="python"
            print_success "找到 Python: $PYTHON_VERSION"
            return 0
        fi
    fi
    return 1
}

# 检测 pip
detect_pip() {
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        PIP_CMD="$PYTHON_CMD -m pip"
        print_success "找到 pip"
        return 0
    elif command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
        print_success "找到 pip3"
        return 0
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
        print_success "找到 pip"
        return 0
    fi
    return 1
}

# 检测国内网络
detect_china_network() {
    # 尝试访问 Google，如果失败可能是国内网络
    if ! curl -s --max-time 3 https://www.google.com > /dev/null 2>&1; then
        IN_CHINA=true
        print_info "检测到国内网络环境，将使用镜像源"
    else
        IN_CHINA=false
        print_info "使用官方 PyPI 源"
    fi
}

# 安装 jgy
install_jgy() {
    print_info "正在安装 jgy..."
    
    # 检测是否需要 --break-system-packages (PEP 668)
    PIP_EXTRA_ARGS=""
    if $PIP_CMD install --help 2>/dev/null | grep -q "break-system-packages"; then
        PIP_EXTRA_ARGS="--break-system-packages"
        print_info "检测到系统保护，使用兼容模式安装"
    fi
    
    if [ "$IN_CHINA" = true ]; then
        # 使用国内镜像源
        $PIP_CMD install jgy -i https://pypi.tuna.tsinghua.edu.cn/simple --user $PIP_EXTRA_ARGS
    else
        $PIP_CMD install jgy --user $PIP_EXTRA_ARGS
    fi
    
    print_success "jgy 安装完成！"
}

# 配置 PATH
setup_path() {
    print_info "配置环境变量..."
    
    # 获取 pip 用户安装路径
    USER_BASE=$($PYTHON_CMD -m site --user-base 2>/dev/null || echo "$HOME/.local")
    SCRIPT_DIR="$USER_BASE/bin"
    
    # 检测当前 shell
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        if [ "$OS" = "macos" ]; then
            SHELL_CONFIG="$HOME/.bash_profile"
        else
            SHELL_CONFIG="$HOME/.bashrc"
        fi
    else
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    # 检查 PATH 是否已配置
    if grep -q "$SCRIPT_DIR" "$SHELL_CONFIG" 2>/dev/null; then
        print_success "PATH 已配置"
    else
        echo "" >> "$SHELL_CONFIG"
        echo "# jgy CLI 配置" >> "$SHELL_CONFIG"
        echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> "$SHELL_CONFIG"
        print_success "已自动配置 PATH: $SHELL_CONFIG"
    fi
    
    # 提示用户
    echo ""
    echo "=============================================="
    echo "  🎉 金谷园饺子馆 CLI 安装成功！"
    echo ""
    echo "  请运行以下命令使配置生效："
    echo ""
    echo "    source $SHELL_CONFIG"
    echo ""
    echo "  然后就能使用："
    echo ""
    echo "    jgy --help"
    echo "    jgy menu"
    echo "    jgy game"
    echo ""
    echo "=============================================="
    echo ""
}

# 主流程
main() {
    echo ""
    echo "🥟 金谷园饺子馆 CLI 安装程序"
    echo "=============================="
    echo ""
    
    # 1. 检测操作系统
    detect_os
    
    # 2. 检测 Python
    if ! detect_python; then
        print_error "未找到 Python 3"
        echo ""
        echo "请安装 Python 3.8 或更高版本："
        echo ""
        if [ "$OS" = "macos" ]; then
            echo "  方法1: brew install python3"
            echo "  方法2: 访问 https://python.org 下载安装包"
        elif [ "$OS" = "linux" ]; then
            echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
            echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
        else
            echo "  访问 https://python.org 下载安装包"
        fi
        echo ""
        exit 1
    fi
    
    # 检查 Python 版本
    PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
    PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 版本过低，需要 3.8 或更高版本"
        exit 1
    fi
    
    # 3. 检测 pip
    if ! detect_pip; then
        print_error "未找到 pip"
        echo "正在尝试安装 pip..."
        $PYTHON_CMD -m ensurepip --upgrade || {
            print_error "pip 安装失败，请手动安装"
            exit 1
        }
        detect_pip
    fi
    
    # 4. 检测网络环境
    detect_china_network
    
    # 5. 安装 jgy
    install_jgy
    
    # 6. 配置 PATH
    setup_path
}

# 运行主程序
main
