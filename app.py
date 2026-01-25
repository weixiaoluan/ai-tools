"""
LearnFlow AI - 智能学习内容生成平台
FastAPI后端服务
"""
from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import tempfile
import shutil
import uuid
import json
import os
import hashlib
import threading
import httpx
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents import OutlineAgent, ArticleAgent, ChapterAgent, ContentParser
from config import AI_CONFIG
import database as db

app = FastAPI(title="LearnFlow AI")
security = HTTPBearer(auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 内存中的任务状态（用于实时更新）
tasks_memory = {}
TASK_MEMORY_MAX_SIZE = 100  # 最大缓存任务数

def cleanup_tasks_memory():
    """清理已完成的旧任务，防止内存泄漏"""
    if len(tasks_memory) > TASK_MEMORY_MAX_SIZE:
        completed_tasks = [k for k, v in tasks_memory.items() 
                          if v.get('status') in ('completed', 'failed')]
        # 删除最旧的一半已完成任务
        for task_id in completed_tasks[:len(completed_tasks)//2]:
            del tasks_memory[task_id]

# 并发线程池
executor = ThreadPoolExecutor(max_workers=12)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(username: str) -> str:
    return hashlib.sha256(f"{username}{datetime.now().isoformat()}{uuid.uuid4()}".encode()).hexdigest()

def load_ai_config():
    try:
        config = db.get_all_config() or {}
    except Exception as e:
        print(f"加载配置失败: {e}")
        config = {}
    AI_CONFIG["api_key"] = config.get("api_key", "")
    AI_CONFIG["api_base"] = config.get("api_base", "https://api.siliconflow.cn/v1")
    AI_CONFIG["model"] = config.get("model", "deepseek-ai/DeepSeek-V3")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="未登录")
    user = db.get_user_by_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="无效的登录凭证")
    return user

# 请求模型
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TopicRequest(BaseModel):
    topic: str
    description: Optional[str] = ""
    links: Optional[List[str]] = []
    enableSearch: Optional[bool] = False
    fileIds: Optional[List[dict]] = []  # 上传的文件信息列表

class OutlineRequest(BaseModel):
    outline_id: str
    feedback: Optional[str] = ""

class DocumentRequest(BaseModel):
    outline_id: str

class ConfigRequest(BaseModel):
    api_key: str
    api_base: Optional[str] = "https://api.siliconflow.cn/v1"
    model: Optional[str] = "deepseek-ai/DeepSeek-V3"
    provider: Optional[str] = "siliconflow"

class OutlineUpdateRequest(BaseModel):
    outline_id: str
    chapters: Optional[List[dict]] = None
    feedback: Optional[str] = ""

class ArticleUpdateRequest(BaseModel):
    title: str
    content: str

class BatchDeleteRequest(BaseModel):
    ids: List[str]

class AskQuestionRequest(BaseModel):
    article_id: str
    question: str

class SaveNoteRequest(BaseModel):
    article_id: str
    question: str
    answer: str

class GenerateInterviewRequest(BaseModel):
    article_id: str
    count: Optional[int] = 5

class AnswerInterviewRequest(BaseModel):
    question_id: int
    answer: str

# ========== 认证接口 ==========
@app.post("/api/auth/register")
async def register(request: UserRegister):
    if db.get_user(request.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6位")
    
    db.create_user(request.username, request.email, hash_password(request.password))
    return {"success": True, "message": "注册成功"}

@app.post("/api/auth/login")
async def login(request: UserLogin):
    user = db.get_user(request.username)
    if not user or user["password"] != hash_password(request.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = generate_token(request.username)
    db.update_user_token(request.username, token)
    
    return {"success": True, "user": {"username": user["username"], "email": user["email"], "token": token}}

# ========== 配置接口 ==========
# 支持深度思考的模型列表
DEEP_THINK_MODELS = [
    "deepseek-r1", "deepseek-reasoner", "r1-",
    "o1-", "o1-mini", "o1-preview",
    "qwq", "qwen-qwq",
    "claude-3-5-sonnet", "claude-3-opus",
    "gpt-4o", "gpt-4-turbo",
]

def check_deep_think_support(model: str) -> bool:
    """检查模型是否支持深度思考"""
    model_lower = model.lower()
    for pattern in DEEP_THINK_MODELS:
        if pattern in model_lower:
            return True
    return False

@app.get("/api/config")
async def get_config():
    config = db.get_all_config()
    current_provider = config.get("provider", "siliconflow")
    # 获取当前服务商的API Key
    api_key = config.get(f"api_key_{current_provider}", config.get("api_key", ""))
    model = config.get("model", "deepseek-ai/DeepSeek-V3")
    
    # 构建所有服务商的API Key状态（仅返回是否已配置）
    provider_keys = {}
    for p in ['siliconflow', 'aliyun', 'deepseek', 'openai', 'gemini', 'xinliu', 'custom']:
        key = config.get(f"api_key_{p}", "")
        provider_keys[p] = "***" + key[-4:] if key else ""
    
    return {
        "api_key": "***" + api_key[-4:] if api_key else "",
        "api_base": config.get("api_base", "https://api.siliconflow.cn/v1"),
        "model": model,
        "provider": current_provider,
        "configured": bool(api_key),
        "supports_deep_think": check_deep_think_support(model),
        "provider_keys": provider_keys
    }

@app.post("/api/config")
async def save_config(request: ConfigRequest, user: dict = Depends(get_current_user)):
    config = db.get_all_config()
    
    # 处理API Key
    if request.api_key == "__USE_EXISTING__":
        # 使用已存储的该服务商的API Key
        api_key = config.get(f"api_key_{request.provider}", "")
        if not api_key:
            raise HTTPException(status_code=400, detail="该服务商尚未配置API Key")
    else:
        # 新输入的API Key，按服务商存储
        api_key = request.api_key
        db.set_config(f"api_key_{request.provider}", api_key)
    
    # 更新当前使用的api_key（兼容旧逻辑）
    db.set_config("api_key", api_key)
    db.set_config("api_base", request.api_base)
    db.set_config("model", request.model)
    db.set_config("provider", request.provider)
    load_ai_config()
    return {"success": True, "message": "配置已保存"}

# ========== 页面路由 ==========
@app.get("/")
async def index():
    return FileResponse("static/index.html", headers={"Cache-Control": "no-cache"})

@app.get("/article/{article_id}")
async def article_page(article_id: str):
    return FileResponse("static/index.html", headers={"Cache-Control": "no-cache"})

# ========== 后台任务生成 ==========
MAX_RETRY_ATTEMPTS = 2  # 章节生成最大重试次数

def generate_single_chapter_sync(chapter: dict, outline: dict, enable_search: bool = False) -> dict:
    """生成单个章节，带重试机制"""
    last_error = None
    for attempt in range(MAX_RETRY_ATTEMPTS + 1):
        try:
            agent = ChapterAgent()
            content = agent.generate_chapter(chapter, outline, enable_search)
            return {"id": chapter["id"], "title": chapter["title"], "content": content, "status": "success"}
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRY_ATTEMPTS:
                import time
                time.sleep(2)  # 重试前等待2秒
                continue
    return {"id": chapter["id"], "title": chapter["title"], "content": f"生成失败: {str(last_error)}", "status": "failed"}

def run_article_generation(task_id: str, topic: str, description: str, username: str, enable_search: bool, links: list = None, file_ids: list = None):
    tasks_memory[task_id] = {"status": "running", "steps": [], "current_step": "🚀 开始生成文章..."}
    
    def add_step(step: str):
        tasks_memory[task_id]["steps"].append(step)
        tasks_memory[task_id]["current_step"] = step
        db.update_task(task_id, status="running", current_step=step)
    
    try:
        add_step("🚀 开始生成文章...")
        extra_context = ""
        
        # 处理上传的文件
        if file_ids and len(file_ids) > 0:
            add_step(f"📄 正在解析 {len(file_ids)} 个上传文件...")
            file_content = process_uploaded_files(file_ids)
            if file_content:
                extra_context += f"\n\n### 参考文件内容\n{file_content}"
                add_step("✅ 文件解析完成")
        
        if links and len(links) > 0:
            add_step(f"🔗 正在解析 {len(links)} 个参考链接...")
            parser = ContentParser()
            link_results = []
            for i, link in enumerate(links):
                add_step(f"📄 解析链接 ({i+1}/{len(links)})...")
                try:
                    result = parser.parse_url(link)
                    link_results.append(result)
                except Exception as e:
                    add_step(f"⚠️ 链接解析失败: {link[:50]}...")
            if link_results:
                add_step("📝 整合链接内容...")
                extra_context += parser.combine_sources(topic, link_results)
        
        if enable_search:
            add_step("🌐 正在联网搜索相关资料...")
            parser = ContentParser()
            search_results = parser.web_search(f"{topic} {description}")
            if search_results:
                add_step("📚 整理搜索结果...")
                for r in search_results:
                    if isinstance(r, dict) and r.get('results'):
                        extra_context += f"\n\n### 搜索资料\n{r['results'][:2000]}"
        
        add_step("✍️ AI正在撰写文章内容...")
        agent = ArticleAgent()
        result = agent.generate_article(topic, description, extra_context)
        
        add_step("✅ 文章生成完成，正在保存...")
        article_id = str(uuid.uuid4())[:8]
        article_data = {
            "id": article_id, "title": result.get("title", topic), "content": result.get("content", ""),
            "topic": topic, "type": "article", "user": username, "created_at": datetime.now().isoformat()
        }
        db.create_article(article_data)
        
        tasks_memory[task_id]["status"] = "completed"
        tasks_memory[task_id]["current_step"] = "🎉 文章已保存到文章列表"
        db.update_task(task_id, status="completed", current_step="🎉 文章已保存到文章列表")
        
    except Exception as e:
        tasks_memory[task_id]["status"] = "failed"
        tasks_memory[task_id]["error"] = str(e)
        db.update_task(task_id, status="failed", error=str(e))
    finally:
        cleanup_tasks_memory()  # 清理旧任务

def run_document_generation(task_id: str, outline: dict, username: str, enable_search: bool):
    chapters = outline.get("chapters", [])
    total = len(chapters)
    tasks_memory[task_id] = {"status": "running", "steps": [], "current_step": "🚀 开始生成文档...", "completed": 0, "total": total}
    
    def add_step(step: str):
        tasks_memory[task_id]["steps"].append(step)
        tasks_memory[task_id]["current_step"] = step
        db.update_task(task_id, current_step=step)
    
    add_step("🚀 开始生成学习文档...")
    add_step(f"📝 开始并发生成 {total} 个章节...")
    
    futures = {executor.submit(generate_single_chapter_sync, ch, outline, enable_search): ch["id"] for ch in chapters}
    
    results = []
    completed = 0
    
    for future in as_completed(futures):
        result = future.result()
        results.append(result)
        completed += 1
        tasks_memory[task_id]["completed"] = completed
        db.update_task(task_id, completed=completed)
        add_step(f"✅ 第{result['id']}章「{result['title']}」完成 ({completed}/{total})")
    
    add_step("💾 正在保存文档...")
    
    doc_id = str(uuid.uuid4())[:8]
    sorted_chapters = sorted(results, key=lambda x: x["id"])
    
    doc_data = {
        "id": doc_id, "title": outline.get("title", ""), "description": outline.get("description", ""),
        "topic": outline.get("topic", ""), "chapters": sorted_chapters, "user": username,
        "created_at": datetime.now().isoformat()
    }
    db.create_document(doc_data)
    
    for chapter in sorted_chapters:
        article_id = f"{doc_id}-{chapter['id']}"
        article_data = {
            "id": article_id, "title": chapter["title"], "content": chapter["content"],
            "topic": outline.get("topic", ""), "document_id": doc_id, "chapter_id": chapter["id"],
            "type": "chapter", "user": username, "created_at": datetime.now().isoformat()
        }
        db.create_article(article_data)
    
    tasks_memory[task_id]["status"] = "completed"
    tasks_memory[task_id]["current_step"] = "🎉 文档已保存到学习文档列表"
    db.update_task(task_id, status="completed", current_step="🎉 文档已保存到学习文档列表")
    cleanup_tasks_memory()  # 清理旧任务

# ========== 文件上传处理 ==========
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def parse_uploaded_file(file_path: str, filename: str) -> str:
    """解析上传的文件内容"""
    try:
        ext = filename.lower().split('.')[-1]
        
        if ext in ('txt', 'md'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()[:10000]  # 限制长度
        
        elif ext == 'pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages[:20]:  # 最多20页
                        text += page.extract_text() or ""
                    return text[:10000]
            except ImportError:
                return f"[PDF文件: {filename}，需要安装PyPDF2库]"
        
        elif ext in ('doc', 'docx'):
            try:
                import docx
                doc = docx.Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text[:10000]
            except ImportError:
                return f"[Word文件: {filename}，需要安装python-docx库]"
        
        return f"[不支持的文件类型: {ext}]"
    except Exception as e:
        return f"[文件解析失败: {str(e)}]"

@app.post("/api/upload/files")
async def upload_files(
    files: List[UploadFile] = File(...),
    user: dict = Depends(get_current_user)
):
    """上传文件并返回文件ID列表"""
    file_ids = []
    for file in files:
        file_id = str(uuid.uuid4())[:8]
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'txt'
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_ext}")
        
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        file_ids.append({
            "id": file_id,
            "name": file.filename,
            "path": file_path
        })
    
    return {"success": True, "files": file_ids}

def process_uploaded_files(file_ids: List[dict]) -> str:
    """处理上传的文件，提取内容"""
    contents = []
    for file_info in file_ids:
        if isinstance(file_info, dict) and file_info.get('path'):
            content = parse_uploaded_file(file_info['path'], file_info.get('name', ''))
            if content:
                contents.append(f"### 文件: {file_info.get('name', '未知')}\n{content}")
    return "\n\n".join(contents)

# ========== 生成接口 ==========
@app.post("/api/generate/article")
async def generate_article(request: TopicRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="请输入学习主题")
    
    task_id = str(uuid.uuid4())[:8]
    task_data = {
        "id": task_id, "type": "article", "status": "pending", "topic": topic,
        "user": user["username"], "current_step": "准备中...", "created_at": datetime.now().isoformat()
    }
    db.create_task(task_data)
    
    thread = threading.Thread(
        target=run_article_generation,
        args=(task_id, topic, request.description or "", user["username"], request.enableSearch, request.links or [], request.fileIds or [])
    )
    thread.start()
    
    return {"success": True, "task_id": task_id}

@app.post("/api/generate/outline")
async def generate_outline(request: TopicRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="请输入学习主题")
    
    try:
        agent = OutlineAgent()
        outline = agent.generate_outline(topic, request.description or "")
        
        outline_id = str(uuid.uuid4())[:8]
        outline_data = {
            **outline, "id": outline_id, "topic": topic,
            "links": request.links or [], "enableSearch": request.enableSearch,
            "user": user["username"], "created_at": datetime.now().isoformat()
        }
        db.create_outline(outline_data)
        return {"success": True, "outline": outline_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

@app.post("/api/regenerate/outline")
async def regenerate_outline(request: OutlineRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    original = db.get_outline(request.outline_id)
    if not original:
        raise HTTPException(status_code=404, detail="大纲不存在")
    
    try:
        agent = OutlineAgent()
        outline = agent.regenerate_outline(original.get("topic", ""), request.feedback or "")
        
        outline_id = str(uuid.uuid4())[:8]
        outline_data = {
            **outline, "id": outline_id, "topic": original.get("topic", ""),
            "links": original.get("links", []), "enableSearch": original.get("enableSearch", False),
            "user": user["username"], "created_at": datetime.now().isoformat()
        }
        db.create_outline(outline_data)
        return {"success": True, "outline": outline_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成失败: {str(e)}")

@app.post("/api/update/outline")
async def update_outline(request: OutlineUpdateRequest, user: dict = Depends(get_current_user)):
    outline = db.get_outline(request.outline_id)
    if not outline:
        raise HTTPException(status_code=404, detail="大纲不存在")
    
    db.update_outline(request.outline_id, request.chapters, request.feedback)
    updated = db.get_outline(request.outline_id)
    return {"success": True, "outline": updated}

@app.post("/api/generate/document")
async def generate_document(request: DocumentRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    outline = db.get_outline(request.outline_id)
    if not outline:
        raise HTTPException(status_code=404, detail="大纲不存在")
    
    task_id = str(uuid.uuid4())[:8]
    task_data = {
        "id": task_id, "type": "document", "status": "pending",
        "topic": outline.get("topic", ""), "user": user["username"],
        "total": len(outline.get("chapters", [])), "created_at": datetime.now().isoformat()
    }
    db.create_task(task_data)
    
    thread = threading.Thread(
        target=run_document_generation,
        args=(task_id, outline, user["username"], outline.get("enableSearch", True))
    )
    thread.start()
    
    return {"success": True, "task_id": task_id}

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    if task_id in tasks_memory:
        return tasks_memory[task_id]
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task

@app.get("/api/tasks")
async def list_tasks(user: dict = Depends(get_current_user)):
    tasks = db.get_tasks(user["username"])
    for task in tasks:
        task["task_id"] = task["id"]
        if task["id"] in tasks_memory:
            task.update(tasks_memory[task["id"]])
    return {"tasks": tasks}

# ========== 文章接口 ==========
@app.get("/api/articles")
async def list_articles(user: dict = Depends(get_current_user)):
    articles = db.get_articles(user["username"])
    return {"articles": articles}

@app.get("/api/articles/{article_id}")
async def get_article(article_id: str, user: dict = Depends(get_current_user)):
    article = db.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"article": article}

@app.get("/api/public/articles/{article_id}")
async def get_public_article(article_id: str):
    article = db.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"article": article}

@app.put("/api/articles/{article_id}")
async def update_article(article_id: str, request: ArticleUpdateRequest, user: dict = Depends(get_current_user)):
    db.update_article(article_id, request.title, request.content)
    article = db.get_article(article_id)
    return {"success": True, "article": article}

@app.delete("/api/articles/{article_id}")
async def delete_article(article_id: str, user: dict = Depends(get_current_user)):
    db.delete_article(article_id)
    return {"success": True}

@app.post("/api/articles/batch-delete")
async def batch_delete_articles(request: BatchDeleteRequest, user: dict = Depends(get_current_user)):
    for aid in request.ids:
        db.delete_article(aid)
    return {"success": True, "deleted": len(request.ids)}

# ========== 文档接口 ==========
@app.get("/api/documents")
async def list_documents(user: dict = Depends(get_current_user)):
    documents = db.get_documents(user["username"])
    return {"documents": documents}

@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str, user: dict = Depends(get_current_user)):
    document = db.get_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"document": document}

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str, user: dict = Depends(get_current_user)):
    db.delete_articles_by_document(doc_id)
    db.delete_document(doc_id)
    return {"success": True}

@app.post("/api/documents/batch-delete")
async def batch_delete_documents(request: BatchDeleteRequest, user: dict = Depends(get_current_user)):
    for doc_id in request.ids:
        db.delete_articles_by_document(doc_id)
        db.delete_document(doc_id)
    return {"success": True, "deleted": len(request.ids)}

# ========== AI问答接口 ==========
@app.post("/api/ask")
async def ask_question(request: AskQuestionRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    article = db.get_article(request.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    try:
        from agents.base_agent import BaseAgent
        agent = BaseAgent("AI助手", "你是一个专业的学习助手，根据文章内容回答用户问题。回答要准确、简洁、有帮助。")
        
        prompt = f"""请根据以下文章内容回答用户的问题。

## 文章内容
{article['content'][:6000]}

## 用户问题
{request.question}

请给出准确、有帮助的回答："""
        
        answer = agent.chat(prompt)
        return {"success": True, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回答失败: {str(e)}")

# ========== 笔记接口 ==========
@app.get("/api/notes/{article_id}")
async def get_notes(article_id: str, user: dict = Depends(get_current_user)):
    notes = db.get_notes(article_id, user["username"])
    return {"notes": notes}

@app.post("/api/notes")
async def save_note(request: SaveNoteRequest, user: dict = Depends(get_current_user)):
    note_id = db.create_note(request.article_id, request.question, request.answer, user["username"])
    return {"success": True, "note_id": note_id}

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, user: dict = Depends(get_current_user)):
    db.delete_note(note_id, user["username"])
    return {"success": True}

# ========== 面试题接口 ==========
@app.get("/api/interview/{article_id}")
async def get_interview_questions(article_id: str, user: dict = Depends(get_current_user)):
    questions = db.get_interview_questions(article_id, user["username"])
    return {"questions": questions}

@app.post("/api/interview/generate")
async def generate_interview_questions(request: GenerateInterviewRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    article = db.get_article(request.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    prompt = f"""根据以下文章内容，生成{request.count}道高质量的求职面试题。

文章标题：{article['title']}
文章内容：
{article['content'][:8000]}

要求：
1. 面试题要覆盖文章的核心知识点
2. 难度适中，符合实际面试场景
3. 包含概念理解题、应用场景题、对比分析题等不同类型
4. 每道题都要有参考答案

请按以下JSON格式输出（只输出JSON，不要其他内容）：
[
  {{"question": "面试题1", "reference_answer": "参考答案1"}},
  {{"question": "面试题2", "reference_answer": "参考答案2"}}
]"""

    try:
        import httpx
        api_base = AI_CONFIG.get('api_base', 'https://api.siliconflow.cn/v1')
        api_key = AI_CONFIG.get('api_key', '')
        model = AI_CONFIG.get('model', 'deepseek-ai/DeepSeek-V3')
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{api_base}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 4096
                }
            )
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 解析JSON
            import re
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                questions_data = json.loads(json_match.group())
                created_ids = []
                for q in questions_data:
                    qid = db.create_interview_question(
                        request.article_id, 
                        q["question"], 
                        q.get("reference_answer", ""),
                        user["username"]
                    )
                    created_ids.append(qid)
                return {"success": True, "count": len(created_ids)}
            else:
                raise HTTPException(status_code=500, detail="AI返回格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成面试题失败: {str(e)}")

@app.post("/api/interview/answer")
async def answer_interview_question(request: AnswerInterviewRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    question = db.get_interview_question(request.question_id, user["username"])
    if not question:
        raise HTTPException(status_code=404, detail="面试题不存在")
    
    prompt = f"""你是一位资深技术面试官，请评估以下面试回答。

面试题：{question['question']}

参考答案：{question['reference_answer']}

考生回答：{request.answer}

请从以下几个维度进行评估：
1. 正确性：回答是否正确
2. 完整性：是否覆盖了关键点
3. 专业性：表达是否专业、条理清晰
4. 深度：是否有深入理解和独到见解

请按以下JSON格式输出（只输出JSON）：
{{"score": 85, "feedback": "### 评分：85分\\n\\n**优点：**\\n- xxx\\n\\n**不足：**\\n- xxx\\n\\n**建议回答：**\\n更专业的回答方式是..."}}

score为0-100分，feedback使用Markdown格式详细点评并给出更好的回答建议。"""

    try:
        import httpx
        api_base = AI_CONFIG.get('api_base', 'https://api.siliconflow.cn/v1')
        api_key = AI_CONFIG.get('api_key', '')
        model = AI_CONFIG.get('model', 'deepseek-ai/DeepSeek-V3')
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{api_base}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2048
                }
            )
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                eval_data = json.loads(json_match.group())
                score = eval_data.get("score", 0)
                feedback = eval_data.get("feedback", "评估失败")
                
                db.update_interview_answer(request.question_id, request.answer, score, feedback, user["username"])
                return {"success": True, "score": score, "feedback": feedback}
            else:
                raise HTTPException(status_code=500, detail="AI返回格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评估答案失败: {str(e)}")

@app.post("/api/interview/regenerate/{question_id}")
async def regenerate_interview_question(question_id: int, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    old_question = db.get_interview_question(question_id, user["username"])
    if not old_question:
        raise HTTPException(status_code=404, detail="面试题不存在")
    
    article = db.get_article(old_question['article_id'])
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    prompt = f"""根据以下文章内容，生成1道新的高质量面试题（不要与旧题目重复）。

文章标题：{article['title']}
文章内容摘要：{article['content'][:4000]}

旧题目（请生成不同的）：{old_question['question']}

请按以下JSON格式输出（只输出JSON）：
{{"question": "新面试题", "reference_answer": "参考答案"}}"""

    try:
        import httpx
        api_base = AI_CONFIG.get('api_base', 'https://api.siliconflow.cn/v1')
        api_key = AI_CONFIG.get('api_key', '')
        model = AI_CONFIG.get('model', 'deepseek-ai/DeepSeek-V3')
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{api_base}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 1024
                }
            )
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                q_data = json.loads(json_match.group())
                db.delete_interview_question(question_id, user["username"])
                new_id = db.create_interview_question(
                    old_question['article_id'],
                    q_data["question"],
                    q_data.get("reference_answer", ""),
                    user["username"]
                )
                return {"success": True, "new_id": new_id, "question": q_data["question"], "reference_answer": q_data.get("reference_answer", "")}
            else:
                raise HTTPException(status_code=500, detail="AI返回格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成失败: {str(e)}")

@app.delete("/api/interview/{question_id}")
async def delete_interview_question(question_id: int, user: dict = Depends(get_current_user)):
    db.delete_interview_question(question_id, user["username"])
    return {"success": True}

# ========== AI对话接口（流式） ==========
class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []
    conversation_id: Optional[str] = None
    deep_think: Optional[bool] = True
    web_search: Optional[bool] = False

class ImageGenRequest(BaseModel):
    prompt: str

async def web_search(query: str) -> str:
    """使用DuckDuckGo进行网络搜索"""
    try:
        import urllib.parse
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(search_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                for result in soup.select('.result')[:5]:
                    title_elem = result.select_one('.result__title')
                    snippet_elem = result.select_one('.result__snippet')
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        snippet = snippet_elem.get_text(strip=True)
                        results.append(f"- {title}: {snippet}")
                if results:
                    return "\n".join(results)
        return ""
    except Exception as e:
        return ""

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    async def generate():
        try:
            # 根据开关构建系统提示
            if request.deep_think:
                system_content = "你是一个智能AI助手。请先进行深度思考和分析，展示你的推理过程，然后给出详细的回答。用分隔线---将思考过程和最终回答分开。"
            else:
                system_content = "你是一个智能AI助手。直接回答用户问题，不要展示思考过程，回答要简洁、准确。"
            
            # 联网搜索
            search_context = ""
            search_results_text = ""
            if request.web_search:
                search_results_text = await web_search(request.message)
                if search_results_text:
                    # 先发送搜索结果给前端显示
                    yield f"data: {json.dumps({'search_results': search_results_text})}\n\n"
                    search_context = f"\n\n以下是网络搜索到的参考资料，请结合这些信息回答（不要在回答中重复列出这些搜索结果）:\n{search_results_text}"
            
            messages = [{"role": "system", "content": system_content + search_context}]
            
            for h in request.history[-10:]:
                messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            
            messages.append({"role": "user", "content": request.message})
            
            api_base = AI_CONFIG.get('api_base', 'https://api.siliconflow.cn/v1')
            api_key = AI_CONFIG.get('api_key', '')
            model = AI_CONFIG.get('model', 'deepseek-ai/DeepSeek-V3')
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                url = f"{api_base.rstrip('/')}/chat/completions"
                async with client.stream(
                    "POST",
                    url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True,
                        "temperature": 0.7,
                        "max_tokens": 65536
                    }
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield f"data: {json.dumps({'error': f'API错误: {response.status_code}'})}"
                        return
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            data = line[5:].lstrip()
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if chunk.get("choices") and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content") or delta.get("reasoning_content", "")
                                    if content:
                                        yield f"data: {json.dumps({'content': content})}\n\n"
                            except json.JSONDecodeError:
                                pass
        except httpx.TimeoutException:
            yield f"data: {json.dumps({'error': '请求超时，请重试'})}"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/chat/image")
async def generate_chat_image(request: ImageGenRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    try:
        base_url = AI_CONFIG.get("api_base", "https://api.siliconflow.cn/v1")
        api_key = AI_CONFIG.get("api_key", "")
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/images/generations",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "black-forest-labs/FLUX.1-schnell",
                    "prompt": request.prompt,
                    "image_size": "1024x576",
                    "num_inference_steps": 20
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("images") and len(data["images"]) > 0:
                    return {"success": True, "url": data["images"][0].get("url", "")}
                if data.get("data") and len(data["data"]) > 0:
                    return {"success": True, "url": data["data"][0].get("url", "")}
            
            return {"success": False, "error": "图片生成失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ========== 聊天记录接口 ==========
@app.get("/api/conversations")
async def list_conversations(user: dict = Depends(get_current_user)):
    conversations = db.get_conversations(user["username"])
    return {"conversations": conversations}

@app.post("/api/conversations")
async def create_conversation(user: dict = Depends(get_current_user)):
    conv_id = str(uuid.uuid4())[:8]
    db.create_conversation(conv_id, user["username"])
    return {"success": True, "conversation_id": conv_id}

@app.get("/api/conversations/{conv_id}")
async def get_conversation(conv_id: str, user: dict = Depends(get_current_user)):
    conv = db.get_conversation(conv_id, user["username"])
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"conversation": conv}

@app.put("/api/conversations/{conv_id}")
async def update_conversation(conv_id: str, request: dict, user: dict = Depends(get_current_user)):
    db.update_conversation(conv_id, request.get("messages", []), request.get("title", ""))
    return {"success": True}

@app.delete("/api/conversations/{conv_id}")
async def delete_conversation(conv_id: str, user: dict = Depends(get_current_user)):
    db.delete_conversation(conv_id, user["username"])
    return {"success": True}

@app.post("/api/conversations/batch-delete")
async def batch_delete_conversations(request: BatchDeleteRequest, user: dict = Depends(get_current_user)):
    for conv_id in request.ids:
        db.delete_conversation(conv_id, user["username"])
    return {"success": True, "deleted": len(request.ids)}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("APP_PORT", 6066))
    print("🚀 AI Tools Platform 启动中...")
    print(f"📚 访问 http://localhost:{port} 开始使用")
    uvicorn.run(app, host="0.0.0.0", port=port)
