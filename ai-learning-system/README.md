# AI Tools Platform

智能AI工具平台，提供多种AI能力工具。

## 功能特性

- 🚀 **AI 快速学** - 智能生成学习文档和文章
- 🎨 **AI 绘图** - 文字生成图片（即将上线）
- 💬 **AI 对话** - 智能对话助手（即将上线）

## 技术栈

- **后端**: Python FastAPI
- **前端**: Vue 3 + Vite
- **数据库**: MySQL
- **部署**: Nginx + Systemd

## 快速部署

### Linux 服务器一键部署

```bash
# 1. 克隆代码
git clone https://github.com/weixiaoluan/ai-tools.git
cd ai-tools

# 2. 赋予执行权限
chmod +x deploy.sh

# 3. 一键部署
./deploy.sh quick

# 4. 配置数据库（编辑 .env 文件）
vim .env

# 5. 重启服务
./deploy.sh restart
```

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- Nginx (可选，用于反向代理)

### 配置说明

编辑 `.env` 文件：

```env
# MySQL 数据库
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=learnflow

# 服务端口
APP_PORT=6066
```

### 管理命令

```bash
./deploy.sh status    # 查看状态
./deploy.sh logs      # 查看日志
./deploy.sh restart   # 重启服务
./deploy.sh stop      # 停止服务
./deploy.sh build     # 重新构建前端
```

### 申请 HTTPS

```bash
sudo certbot --nginx -d ai.flytest.com.cn
```

## 目录结构

```
ai-tools/
├── app.py              # FastAPI 后端入口
├── database.py         # 数据库操作
├── config.py           # 配置文件
├── agents/             # AI Agent 模块
├── frontend/           # Vue 前端项目
├── static/             # 静态文件（构建后）
├── deploy.sh           # 部署脚本
├── requirements.txt    # Python 依赖
└── .env.example        # 环境变量示例
```

## License

MIT
