"""
LearnFlow AI - 智能学习内容生成平台
FastAPI后端服务
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import uuid
import json
import os
import hashlib
import threading
import httpx
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents import OutlineAgent, ArticleAgent, ChapterAgent, ContentParser
from config import AI_CONFIG, OAUTH_CONFIG

# 尝试使用MySQL，失败则使用SQLite
try:
    import database as db
    print("✅ 使用 MySQL 数据库")
except:
    import database_sqlite as db
    print("✅ 使用 SQLite 数据库（MySQL不可用）")

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
    try:
        if os.path.exists("static/assets"):
            app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except Exception as e:
        print(f"⚠️ 静态文件挂载失败: {e}")

# 内存中的任务状态（用于实时更新）
tasks_memory = {}

# 并发线程池
executor = ThreadPoolExecutor(max_workers=12)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(username: str) -> str:
    return hashlib.sha256(f"{username}{datetime.now().isoformat()}{uuid.uuid4()}".encode()).hexdigest()

def load_ai_config():
    config = db.get_all_config()
    AI_CONFIG["api_key"] = config.get("api_key", "")
    AI_CONFIG["api_base"] = config.get("api_base", "https://api.siliconflow.cn/v1")
    AI_CONFIG["model"] = config.get("model", "deepseek-ai/DeepSeek-V3")
    
    # 如果启用了 OAuth，尝试从数据库加载 OAuth token
    if OAUTH_CONFIG["enabled"]:
        # 注意：这里需要用户名，暂时留空，在实际调用时会动态加载
        pass

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

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

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

# ========== OAuth 认证接口 ==========
@app.get("/api/auth/oauth/login")
async def oauth_login():
    """OAuth 登录入口"""
    if not OAUTH_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="OAuth 认证未启用")
    
    # 生成 state 参数防止 CSRF
    state = str(uuid.uuid4())
    
    # 构建 OAuth 授权 URL
    auth_url = (
        f"{OAUTH_CONFIG['auth_url']}?"
        f"client_id={OAUTH_CONFIG['client_id']}&"
        f"redirect_uri={OAUTH_CONFIG['redirect_uri']}&"
        f"response_type=code&"
        f"scope={OAUTH_CONFIG['scope']}&"
        f"state={state}"
    )
    
    return {"success": True, "auth_url": auth_url, "state": state}

@app.get("/api/auth/callback")
async def oauth_callback(code: str, state: str):
    """OAuth 回调处理"""
    if not OAUTH_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="OAuth 认证未启用")
    
    try:
        # 交换授权码获取 access_token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                OAUTH_CONFIG["token_url"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": OAUTH_CONFIG["redirect_uri"],
                    "client_id": OAUTH_CONFIG["client_id"],
                    "client_secret": OAUTH_CONFIG["client_secret"],
                }
            )
            token_data = token_response.json()
            
            if "error" in token_data:
                raise HTTPException(status_code=400, detail=f"OAuth 错误: {token_data.get('error_description', token_data['error'])}")
            
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            
            # 获取用户信息（假设 OAuth 提供者返回用户信息）
            # 这里需要根据实际的 OAuth 提供者调整
            user_info_response = await client.get(
                "https://api.iflow.cn/v1/user/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info = user_info_response.json()
            
            username = user_info.get("username", f"oauth_{uuid.uuid4().hex[:8]}")
            email = user_info.get("email", "")
            
            # 检查用户是否存在
            existing_user = db.get_user(username)
            if existing_user:
                # 更新现有用户的 token
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                db.update_oauth_tokens(username, access_token, refresh_token, expires_at)
            else:
                # 创建新用户
                expires_at = datetime.now() + timedelta(seconds=expires_in)
                db.create_oauth_user(username, email, access_token, refresh_token, expires_at)
            
            # 生成会话 token
            session_token = generate_token(username)
            db.update_user_token(username, session_token)
            
            # 重定向到前端，携带 token
            return RedirectResponse(url=f"/?token={session_token}&username={username}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth 认证失败: {str(e)}")

@app.post("/api/auth/oauth/refresh")
async def refresh_oauth_token(user: dict = Depends(get_current_user)):
    """刷新 OAuth access token"""
    if not OAUTH_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="OAuth 认证未启用")
    
    tokens = db.get_oauth_tokens(user["username"])
    if not tokens:
        raise HTTPException(status_code=400, detail="未找到 OAuth token")
    
    try:
        async with httpx.AsyncClient() as client:
            refresh_response = await client.post(
                OAUTH_CONFIG["token_url"],
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": tokens["refresh_token"],
                    "client_id": OAUTH_CONFIG["client_id"],
                    "client_secret": OAUTH_CONFIG["client_secret"],
                }
            )
            refresh_data = refresh_response.json()
            
            if "error" in refresh_data:
                raise HTTPException(status_code=400, detail=f"刷新 token 失败: {refresh_data.get('error_description', refresh_data['error'])}")
            
            new_access_token = refresh_data.get("access_token")
            new_refresh_token = refresh_data.get("refresh_token", tokens["refresh_token"])
            expires_in = refresh_data.get("expires_in", 3600)
            
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            db.update_oauth_tokens(user["username"], new_access_token, new_refresh_token, expires_at)
            
            return {"success": True, "message": "Token 刷新成功"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新 token 失败: {str(e)}")

# ========== 配置接口 ==========
@app.get("/api/config")
async def get_config():
    config = db.get_all_config()
    api_key = config.get("api_key", "")
    return {
        "api_key": "***" + api_key[-4:] if api_key else "",
        "api_base": config.get("api_base", "https://apis.iflow.cn/v1"),
        "model": config.get("model", "TBStars2-200B-A13B"),
        "provider": config.get("provider", "iflow"),
        "configured": bool(api_key)
    }

@app.post("/api/config")
async def save_config(request: ConfigRequest, user: dict = Depends(get_current_user)):
    db.set_config("api_key", request.api_key)
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
def generate_single_chapter_sync(chapter: dict, outline: dict, enable_search: bool = False, username: str = "") -> dict:
    try:
        agent = ChapterAgent()
        if username and OAUTH_CONFIG["enabled"]:
            agent.set_user(username)
        content = agent.generate_chapter(chapter, outline, enable_search)
        return {"id": chapter["id"], "title": chapter["title"], "content": content, "status": "success"}
    except Exception as e:
        return {"id": chapter["id"], "title": chapter["title"], "content": f"生成失败: {str(e)}", "status": "failed"}

def run_article_generation(task_id: str, topic: str, description: str, username: str, enable_search: bool, links: list = None):
    tasks_memory[task_id] = {"status": "running", "steps": [], "current_step": "🚀 开始生成文章..."}
    
    def add_step(step: str):
        tasks_memory[task_id]["steps"].append(step)
        tasks_memory[task_id]["current_step"] = step
        db.update_task(task_id, status="running", current_step=step)
    
    try:
        add_step("🚀 开始生成文章...")
        extra_context = ""
        
        if links and len(links) > 0:
            add_step(f"🔗 正在解析 {len(links)} 个参考链接...")
            parser = ContentParser()
            link_results = []
            for i, link in enumerate(links):
                add_step(f"📄 解析链接 ({i+1}/{len(links)})...")
                try:
                    result = parser.parse_url(link)
                    link_results.append(result)
                except:
                    pass
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
        if username and OAUTH_CONFIG["enabled"]:
            agent.set_user(username)
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
    
    futures = {executor.submit(generate_single_chapter_sync, ch, outline, enable_search, username): ch["id"] for ch in chapters}
    
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
        args=(task_id, topic, request.description or "", user["username"], request.enableSearch, request.links or [])
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
        if user["username"] and OAUTH_CONFIG["enabled"]:
            agent.set_user(user["username"])
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
        if user["username"] and OAUTH_CONFIG["enabled"]:
            agent.set_user(user["username"])
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
        if user["username"] and OAUTH_CONFIG["enabled"]:
            agent.set_user(user["username"])
        
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

# ========== AI对话接口 ==========
@app.post("/api/chat")
async def chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    load_ai_config()
    if not AI_CONFIG.get("api_key"):
        raise HTTPException(status_code=400, detail="请先配置API Key")
    
    try:
        from agents.base_agent import BaseAgent
        agent = BaseAgent("AI对话助手", "你是一个智能对话助手，能够回答各种问题、提供建议、协助创作等。回答要准确、有帮助、友好。")
        if user["username"] and OAUTH_CONFIG["enabled"]:
            agent.set_user(user["username"])
        
        # 构建对话历史上下文
        context = ""
        if request.history:
            context = "以下是我们的对话历史：\n\n"
            for msg in request.history[-10:]:  # 只保留最近10轮对话
                role = "用户" if msg["role"] == "user" else "助手"
                context += f"{role}: {msg['content']}\n"
            context += "\n"
        
        context += f"用户最新问题: {request.message}\n\n请给出回答："
        
        answer = agent.chat(context)
        return {"success": True, "reply": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("APP_PORT", 6066))
    print("🚀 AI Tools Platform 启动中...")
    print(f"📚 访问 http://localhost:{port} 开始使用")
    uvicorn.run(app, host="0.0.0.0", port=port)
