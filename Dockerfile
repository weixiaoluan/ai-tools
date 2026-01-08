# 阶段1: 构建前端
FROM node:18-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/src/ ./src/
COPY frontend/vite.config.js ./
# 直接写入 index.html 内容避免文件系统问题
RUN echo '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"><title>AI Tools Platform</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"></head><body><div id="app"></div><script type="module" src="/src/main.js"></script></body></html>' > index.html
RUN npm run build

# 阶段2: 运行后端
FROM python:3.11-slim
WORKDIR /app

# 安装依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY *.py ./
COPY *.json ./
COPY agents/ ./agents/
COPY .env* ./

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /build/dist ./static/

# 暴露端口
EXPOSE 6066

# 启动命令
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "6066"]
