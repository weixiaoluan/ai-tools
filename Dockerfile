# 阶段1: 构建前端
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/index.html ./
COPY frontend/vite.config.js ./
COPY frontend/src/ ./src/
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
COPY --from=frontend-builder /app/frontend/dist ./static/

# 暴露端口
EXPOSE 6066

# 启动命令
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "6066"]
