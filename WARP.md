# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

LearnFlow AI (AI学习系统) - A multi-agent AI system for generating learning content. Users input a topic, and the system generates either a single article or a multi-chapter learning document using LLM APIs.

## Development Commands

### Backend (Python/FastAPI)
```bash
# Install dependencies
pip install -r requirements.txt

# Start development server (runs on port 6066 by default)
python app.py
# or
python -m uvicorn app:app --host 0.0.0.0 --port 6066

# Environment variables are loaded from .env (copy from .env.example)
```

### Frontend (Vue 3/Vite)
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build
```

### Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or use deployment script
./deploy-docker.sh
```

## Architecture

### Multi-Agent System
The core architecture uses specialized agents that coordinate to generate content:

```
User Input → OutlineAgent → [Optional: user confirms outline] → ArticleAgent/ChapterAgent → Output
                                        ↓
                              ContentParser (for web search/URL parsing)
```

**Agent Classes** (`agents/`):
- `BaseAgent` - Base class with OpenAI API client, conversation history, and `chat()` method
- `OutlineAgent` - Generates document outlines (returns JSON structure with chapters)
- `ArticleAgent` - Generates single articles, auto-detects topic type (tech/person/science/life/business) and adjusts style
- `ChapterAgent` - Generates individual chapters for multi-chapter documents, supports parallel generation
- `ContentParser` - Parses URLs, text files, and provides web search functionality

### Backend Structure
- `app.py` - FastAPI application with all API routes, task management, and background thread generation
- `config.py` - AI_CONFIG dict (api_key, api_base, model) and AGENT_ROLES prompts
- `database.py` - MySQL operations using pymysql with context manager pattern

**Key Patterns**:
- Background tasks use `threading.Thread` for article generation
- Parallel chapter generation uses `ThreadPoolExecutor` (max 12 workers)
- Task status tracked in-memory (`tasks_memory` dict) and persisted to MySQL
- Auth uses Bearer token in HTTP header, tokens stored in users table

### Frontend Structure
Vue 3 SPA with component-based views:
- `App.vue` - Main routing logic (currentView/toolView state), sidebar, modals
- `components/HomeView.vue` - Topic input form
- `components/ArticlesView.vue` / `DocumentsView.vue` - List views
- `components/ArticleDetail.vue` / `DocumentDetail.vue` - Content rendering with marked.js + highlight.js

### Database Schema
MySQL database `learnflow` with tables:
- `users` - Authentication (username, password hash, token)
- `articles` - Generated articles (type: 'article' or 'chapter')
- `documents` - Multi-chapter documents (chapters stored as JSON)
- `outlines` - Pending outlines awaiting confirmation
- `tasks` - Generation task status tracking
- `notes` - User Q&A notes on articles
- `config` - Key-value API settings

## API Configuration

Supports OpenAI-compatible APIs. Configure in `.env`:
```
AI_API_KEY=your_key
AI_API_BASE=https://api.siliconflow.cn/v1  # or https://api.openai.com/v1
AI_MODEL=deepseek-ai/DeepSeek-V3  # or gpt-4o-mini
```

MySQL configuration:
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=learnflow
```

## Key API Endpoints

- `POST /api/generate/article` - Start article generation task (returns task_id)
- `POST /api/generate/outline` - Generate document outline for review
- `POST /api/generate/document` - Start multi-chapter document generation
- `GET /api/task/{task_id}` - Poll task status
- `GET /api/articles`, `GET /api/documents` - List user content
- `POST /api/config` - Update AI API settings
