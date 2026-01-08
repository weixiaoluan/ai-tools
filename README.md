# 🤖 AI学习系统

基于多智能体架构的AI学习内容生成系统，参考 [weixiaoluan/trade](https://github.com/weixiaoluan/trade) 项目的设计风格。

## ✨ 功能特点

- **单篇文章生成**：输入学习主题，AI生成一篇系统、专业的学习文章
- **学习文档生成**：先生成目录大纲，确认后批量生成多章节学习文档
- **博客风格展示**：生成的内容以博客列表形式展示，支持Markdown渲染

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    用户界面                          │
│              (Flask + HTML/CSS/JS)                  │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                  Agent 协调层                        │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ OutlineAgent│ │ArticleAgent │ │ChapterAgent │   │
│  │  大纲生成    │ │  文章撰写   │ │  章节撰写   │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                   LLM API                           │
│        (OpenAI / DeepSeek / 硅基流动)               │
└─────────────────────────────────────────────────────┘
```

## 📦 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Flask |
| 前端 | HTML5 + CSS3 + JavaScript |
| LLM | OpenAI API 兼容接口 |
| Markdown渲染 | marked.js + highlight.js |

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ai-learning-system
pip install -r requirements.txt
```

### 2. 配置API Key

复制配置文件并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的 LLM API：

```env
# OpenAI
AI_API_KEY=sk-your-api-key
AI_API_BASE=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini

# 或使用硅基流动 DeepSeek
# AI_API_KEY=your-siliconflow-key
# AI_API_BASE=https://api.siliconflow.cn/v1
# AI_MODEL=deepseek-ai/DeepSeek-R1
```

### 3. 运行系统

```bash
python app.py
```

访问 http://localhost:5000 开始使用。

## 📖 使用说明

### 生成单篇文章

1. 在首页输入学习主题（如"Python装饰器"）
2. 点击"开始生成"
3. 选择"生成文章"
4. 等待AI生成完整的学习文章

### 生成学习文档

1. 在首页输入学习主题（如"机器学习入门"）
2. 点击"开始生成"
3. 选择"生成学习文档"
4. 预览AI生成的目录大纲
5. 可选择"重新生成"调整目录
6. 确认后，AI将批量生成所有章节

## 🤖 Agent 角色说明

| Agent | 职责 |
|-------|------|
| OutlineAgent | 根据学习主题生成系统化的目录大纲 |
| ArticleAgent | 撰写完整的单篇学习文章 |
| ChapterAgent | 根据大纲撰写具体章节内容 |

## 📄 许可证

MIT License
