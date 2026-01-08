#!/bin/bash

# ============================================
# AI Tools Platform - Linux 一键部署脚本
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# 配置变量
REPO_URL="https://github.com/weixiaoluan/ai-tools.git"
APP_NAME="ai-tools"
APP_PORT=6066
DOMAIN="ai.flytest.com.cn"
INSTALL_DIR="/opt/ai-tools"

# 如果在项目目录内运行，使用当前目录
if [ -f "app.py" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    INSTALL_DIR="$SCRIPT_DIR"
fi

info "=========================================="
info "  AI Tools Platform 部署脚本"
info "=========================================="

check_dependencies() {
    info "检查系统依赖..."
    
    if command -v git &> /dev/null; then
        success "Git 已安装"
    else
        error "未找到 Git，请先安装: sudo apt install git"
    fi
    
    if command -v python3 &> /dev/null; then
        success "Python3: $(python3 --version 2>&1 | cut -d' ' -f2)"
    else
        error "未找到 Python3，请先安装: sudo apt install python3 python3-pip python3-venv"
    fi
    
    if command -v pip3 &> /dev/null; then
        success "pip3 已安装"
    else
        error "未找到 pip3: sudo apt install python3-pip"
    fi
    
    if command -v node &> /dev/null; then
        success "Node.js: $(node --version)"
    else
        error "未找到 Node.js，请先安装 Node.js 16+"
    fi
    
    if command -v npm &> /dev/null; then
        success "npm 已安装"
    else
        error "未找到 npm"
    fi
    
    if command -v mysql &> /dev/null; then
        success "MySQL 客户端已安装"
    else
        warn "未找到 MySQL 客户端"
    fi
    
    if command -v nginx &> /dev/null; then
        success "Nginx 已安装"
    else
        warn "未找到 Nginx，如需反向代理请先安装: sudo apt install nginx"
    fi
}

clone_or_pull() {
    info "获取代码..."
    
    if [ -d "$INSTALL_DIR/.git" ]; then
        cd "$INSTALL_DIR"
        git pull origin main
        success "代码已更新"
    else
        if [ -d "$INSTALL_DIR" ]; then
            warn "目录已存在但不是 Git 仓库，备份后重新克隆"
            mv "$INSTALL_DIR" "${INSTALL_DIR}.bak.$(date +%Y%m%d%H%M%S)"
        fi
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
        success "代码克隆完成"
    fi
}

setup_python_env() {
    info "设置 Python 虚拟环境..."
    
    cd "$INSTALL_DIR"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        success "虚拟环境创建成功"
    else
        warn "虚拟环境已存在"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    success "Python 依赖安装完成"
}

build_frontend() {
    info "构建前端项目..."
    
    cd "$INSTALL_DIR/frontend"
    
    if [ ! -d "node_modules" ]; then
        info "安装前端依赖..."
        npm install --silent
    fi
    
    info "执行前端构建..."
    npm run build
    
    cd "$INSTALL_DIR"
    
    info "复制构建文件..."
    mkdir -p static
    rm -rf static/*
    cp -r frontend/dist/* static/
    
    success "前端构建完成"
}

setup_env_file() {
    info "配置环境变量..."
    
    cd "$INSTALL_DIR"
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# MySQL 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=learnflow

# 服务端口
APP_PORT=$APP_PORT

# AI API 配置 (在系统设置页面配置)
EOF
        warn ".env 文件已创建，请编辑配置数据库连接"
    else
        success ".env 文件已存在"
    fi
}

create_systemd_service() {
    info "创建 systemd 服务..."
    
    SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
    
    sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=AI Tools Platform
After=network.target mysql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port $APP_PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable ${APP_NAME}
    success "systemd 服务创建完成"
}

create_nginx_config() {
    info "创建 Nginx 配置..."
    
    cd "$INSTALL_DIR"
    
    cat > nginx.conf << EOF
# AI Tools Platform - Nginx 配置
server {
    listen 80;
    server_name ${DOMAIN};

    access_log /var/log/nginx/${APP_NAME}_access.log;
    error_log /var/log/nginx/${APP_NAME}_error.log;

    location / {
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /static {
        proxy_pass http://127.0.0.1:${APP_PORT}/static;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 50M;
}
EOF

    success "Nginx 配置已创建: nginx.conf"
}

install_nginx_config() {
    if [ ! -f "$INSTALL_DIR/nginx.conf" ]; then
        create_nginx_config
    fi
    
    info "安装 Nginx 配置..."
    
    sudo cp "$INSTALL_DIR/nginx.conf" /etc/nginx/sites-available/${APP_NAME}
    
    if [ -L "/etc/nginx/sites-enabled/${APP_NAME}" ]; then
        sudo rm /etc/nginx/sites-enabled/${APP_NAME}
    fi
    sudo ln -s /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
    
    if sudo nginx -t; then
        sudo systemctl reload nginx
        success "Nginx 配置已安装并重载"
    else
        error "Nginx 配置测试失败"
    fi
}

start_service() {
    info "启动服务..."
    
    cd "$INSTALL_DIR"
    
    if systemctl is-active --quiet ${APP_NAME} 2>/dev/null; then
        sudo systemctl restart ${APP_NAME}
        success "服务已重启"
    elif [ -f "/etc/systemd/system/${APP_NAME}.service" ]; then
        sudo systemctl start ${APP_NAME}
        success "服务已启动 (systemd)"
    else
        source venv/bin/activate
        nohup python -m uvicorn app:app --host 0.0.0.0 --port $APP_PORT > app.log 2>&1 &
        echo $! > app.pid
        success "服务已启动 (PID: $(cat app.pid))"
    fi
    
    info "服务地址: http://localhost:${APP_PORT}"
}

stop_service() {
    info "停止服务..."
    
    cd "$INSTALL_DIR"
    
    if systemctl is-active --quiet ${APP_NAME} 2>/dev/null; then
        sudo systemctl stop ${APP_NAME}
        success "服务已停止 (systemd)"
    elif [ -f "app.pid" ]; then
        PID=$(cat app.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            rm app.pid
            success "服务已停止"
        fi
    else
        warn "未找到运行中的服务"
    fi
}

show_status() {
    info "服务状态:"
    
    if systemctl is-active --quiet ${APP_NAME} 2>/dev/null; then
        success "服务运行中 (systemd)"
        systemctl status ${APP_NAME} --no-pager -l
    elif [ -f "$INSTALL_DIR/app.pid" ]; then
        PID=$(cat "$INSTALL_DIR/app.pid")
        if kill -0 $PID 2>/dev/null; then
            success "服务运行中 (PID: $PID)"
        else
            warn "服务未运行"
        fi
    else
        warn "服务未运行"
    fi
}

show_logs() {
    if systemctl is-active --quiet ${APP_NAME} 2>/dev/null; then
        sudo journalctl -u ${APP_NAME} -f
    elif [ -f "$INSTALL_DIR/app.log" ]; then
        tail -f "$INSTALL_DIR/app.log"
    else
        warn "未找到日志文件"
    fi
}

update_code() {
    info "更新代码..."
    
    cd "$INSTALL_DIR"
    git pull origin main
    
    info "重新构建前端..."
    build_frontend
    
    info "重启服务..."
    if systemctl is-active --quiet ${APP_NAME} 2>/dev/null; then
        sudo systemctl restart ${APP_NAME}
    fi
    
    success "更新完成"
}

full_deploy() {
    info "=========================================="
    info "  开始完整部署..."
    info "=========================================="
    
    check_dependencies
    clone_or_pull
    setup_python_env
    build_frontend
    setup_env_file
    create_systemd_service
    create_nginx_config
    
    echo ""
    success "=========================================="
    success "  部署准备完成!"
    success "=========================================="
    echo ""
    info "下一步操作:"
    echo "  1. 编辑 .env 配置 MySQL: vim $INSTALL_DIR/.env"
    echo "  2. 启动服务: $INSTALL_DIR/deploy.sh start"
    echo "  3. 安装 Nginx: $INSTALL_DIR/deploy.sh nginx-install"
    echo "  4. 申请 HTTPS: sudo certbot --nginx -d ${DOMAIN}"
    echo ""
    info "服务端口: ${APP_PORT}"
    info "域名: ${DOMAIN}"
    info "安装目录: ${INSTALL_DIR}"
}

quick_deploy() {
    info "=========================================="
    info "  快速一键部署..."
    info "=========================================="
    
    check_dependencies
    clone_or_pull
    setup_python_env
    build_frontend
    setup_env_file
    create_systemd_service
    create_nginx_config
    
    # 启动服务
    start_service
    
    # 安装 Nginx (如果有)
    if command -v nginx &> /dev/null; then
        install_nginx_config
    fi
    
    echo ""
    success "=========================================="
    success "  一键部署完成!"
    success "=========================================="
    echo ""
    info "访问地址:"
    echo "  本地: http://localhost:${APP_PORT}"
    echo "  域名: http://${DOMAIN} (需配置DNS)"
    echo ""
    info "管理命令:"
    echo "  查看状态: $INSTALL_DIR/deploy.sh status"
    echo "  查看日志: $INSTALL_DIR/deploy.sh logs"
    echo "  重启服务: $INSTALL_DIR/deploy.sh restart"
    echo "  更新代码: $INSTALL_DIR/deploy.sh update"
}

show_help() {
    echo "用法: $0 [命令]"
    echo ""
    echo "部署命令:"
    echo "  deploy      完整部署 (从GitHub克隆，不启动服务)"
    echo "  quick       一键部署 (从GitHub克隆，自动启动)"
    echo "  update      更新代码并重启"
    echo "  build       仅构建前端"
    echo ""
    echo "服务命令:"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  status      查看状态"
    echo "  logs        查看日志"
    echo ""
    echo "配置命令:"
    echo "  nginx       生成 Nginx 配置"
    echo "  nginx-install  安装 Nginx 配置"
    echo "  systemd     创建 systemd 服务"
    echo ""
    echo "示例:"
    echo "  # 服务器首次部署"
    echo "  curl -fsSL https://raw.githubusercontent.com/weixiaoluan/ai-tools/main/deploy.sh | bash -s quick"
    echo ""
    echo "  # 或者手动部署"
    echo "  git clone https://github.com/weixiaoluan/ai-tools.git"
    echo "  cd ai-tools && chmod +x deploy.sh && ./deploy.sh quick"
}

case "${1:-help}" in
    deploy)
        full_deploy
        ;;
    quick)
        quick_deploy
        ;;
    update)
        update_code
        ;;
    build)
        build_frontend
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 2
        start_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    nginx)
        create_nginx_config
        ;;
    nginx-install)
        install_nginx_config
        ;;
    systemd)
        create_systemd_service
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "未知命令: $1"
        show_help
        ;;
esac
