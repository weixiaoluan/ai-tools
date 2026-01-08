#!/bin/bash

# AI Tools Platform - Docker 一键部署脚本
# 使用方法: curl -fsSL https://raw.githubusercontent.com/weixiaoluan/ai-tools/main/deploy-docker.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

INSTALL_DIR="/opt/ai-tools"
REPO_URL="https://github.com/weixiaoluan/ai-tools.git"

echo ""
echo -e "${BLUE}=========================================="
echo "  AI Tools Platform - Docker 一键部署"
echo -e "==========================================${NC}"
echo ""

# 1. 检查并安装 Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_success "Docker 已安装: $(docker --version)"
    else
        log_info "安装 Docker..."
        curl -fsSL https://get.docker.com | sh
        systemctl start docker
        systemctl enable docker
        log_success "Docker 安装完成"
    fi
}

# 2. 检查 Docker Compose (Docker 26+ 内置)
install_docker_compose() {
    if docker compose version &> /dev/null; then
        log_success "Docker Compose 已安装: $(docker compose version --short)"
    else
        log_error "Docker Compose 不可用，请升级 Docker"
        exit 1
    fi
}

# 3. 获取代码
get_code() {
    log_info "获取代码..."
    if [ -d "$INSTALL_DIR" ]; then
        cd "$INSTALL_DIR"
        git pull
        log_success "代码已更新"
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
        log_success "代码克隆完成"
    fi
    cd "$INSTALL_DIR"
}

# 4. 配置环境变量
setup_env() {
    if [ ! -f "$INSTALL_DIR/.env" ]; then
        log_info "创建 .env 配置文件..."
        cat > "$INSTALL_DIR/.env" << 'EOF'
# MySQL 配置
MYSQL_ROOT_PASSWORD=ai_tools_root_2024
MYSQL_DATABASE=ai_learning
MYSQL_USER=ai_user
MYSQL_PASSWORD=ai_password_2024
MYSQL_HOST=mysql
MYSQL_PORT=3306

# DeepSeek API (请替换为你的 API Key)
DEEPSEEK_API_KEY=your-deepseek-api-key

# JWT 密钥
JWT_SECRET=your-jwt-secret-key-change-in-production
EOF
        log_warn "请编辑 $INSTALL_DIR/.env 文件，配置 DEEPSEEK_API_KEY"
    else
        log_success ".env 配置文件已存在"
    fi
}

# 5. 构建并启动服务
start_services() {
    log_info "构建并启动 Docker 服务..."
    cd "$INSTALL_DIR"
    
    # 停止旧容器
    docker compose down 2>/dev/null || true
    
    # 构建并启动
    docker compose up -d --build
    
    log_success "服务启动完成!"
}

# 6. 配置 Nginx (可选)
setup_nginx() {
    if command -v nginx &> /dev/null; then
        log_info "配置 Nginx 反向代理..."
        cat > /etc/nginx/conf.d/ai-tools.conf << 'EOF'
server {
    listen 80;
    server_name ai.flytest.com.cn;

    location / {
        proxy_pass http://127.0.0.1:6066;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF
        nginx -t && systemctl reload nginx
        log_success "Nginx 配置完成"
    else
        log_warn "Nginx 未安装，跳过反向代理配置"
    fi
}

# 7. 显示状态
show_status() {
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  部署完成!"
    echo -e "==========================================${NC}"
    echo ""
    echo "服务地址: http://localhost:6066"
    echo "域名访问: http://ai.flytest.com.cn (需配置 DNS)"
    echo ""
    echo "常用命令:"
    echo "  查看日志: cd $INSTALL_DIR && docker compose logs -f"
    echo "  重启服务: cd $INSTALL_DIR && docker compose restart"
    echo "  停止服务: cd $INSTALL_DIR && docker compose down"
    echo "  更新部署: cd $INSTALL_DIR && git pull && docker compose up -d --build"
    echo ""
    echo -e "${YELLOW}注意: 请确保 .env 文件中的 DEEPSEEK_API_KEY 已正确配置${NC}"
    echo ""
    
    # 显示容器状态
    docker compose ps
}

# 执行部署
main() {
    install_docker
    install_docker_compose
    get_code
    setup_env
    start_services
    setup_nginx
    show_status
}

main
