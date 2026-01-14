"""
数据库模块 - SQLite持久化存储（MySQL失败时的备选方案）
"""
import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# SQLite 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'learnflow.db')

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db_cursor():
    """数据库游标上下文管理器"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def init_db():
    """初始化数据库表"""
    with get_db_cursor() as cursor:
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password TEXT NOT NULL,
                token TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 文章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                topic TEXT,
                type TEXT DEFAULT 'article',
                document_id TEXT,
                chapter_id INTEGER,
                user TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            )
        ''')
        
        # 文档表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                topic TEXT,
                chapters TEXT,
                user TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 大纲表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outlines (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                topic TEXT,
                chapters TEXT,
                links TEXT,
                enable_search INTEGER DEFAULT 0,
                feedback TEXT,
                user TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                type TEXT,
                status TEXT,
                topic TEXT,
                user TEXT NOT NULL,
                current_step TEXT,
                completed INTEGER DEFAULT 0,
                total INTEGER DEFAULT 0,
                error TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 笔记表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT NOT NULL,
                question TEXT,
                answer TEXT,
                user TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

# ========== 用户操作 ==========
def get_user(username):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_token(token):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE token = ?', (token,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_user(username, email, password):
    with get_db_cursor() as cursor:
        cursor.execute(
            'INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)',
            (username, email, password, datetime.now().isoformat())
        )

def update_user_token(username, token):
    with get_db_cursor() as cursor:
        cursor.execute('UPDATE users SET token = ? WHERE username = ?', (token, username))

# ========== 文章操作 ==========
def get_articles(user, include_chapters=False):
    with get_db_cursor() as cursor:
        if include_chapters:
            cursor.execute('SELECT * FROM articles WHERE user = ? ORDER BY created_at DESC', (user,))
        else:
            cursor.execute('SELECT * FROM articles WHERE user = ? AND type != ? ORDER BY created_at DESC', (user, 'chapter'))
        return [dict(row) for row in cursor.fetchall()]

def get_article(article_id):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_article(article_data):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO articles (id, title, content, topic, type, document_id, chapter_id, user, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data['id'], article_data['title'], article_data.get('content', ''),
            article_data.get('topic', ''), article_data.get('type', 'article'),
            article_data.get('document_id'), article_data.get('chapter_id'),
            article_data['user'], article_data.get('created_at', datetime.now().isoformat())
        ))

def update_article(article_id, title, content):
    with get_db_cursor() as cursor:
        cursor.execute(
            'UPDATE articles SET title = ?, content = ?, updated_at = ? WHERE id = ?',
            (title, content, datetime.now().isoformat(), article_id)
        )

def delete_article(article_id):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))

def delete_articles_by_document(document_id):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM articles WHERE document_id = ?', (document_id,))

# ========== 文档操作 ==========
def get_documents(user):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM documents WHERE user = ? ORDER BY created_at DESC', (user,))
        docs = []
        for row in cursor.fetchall():
            doc = dict(row)
            doc['chapters'] = json.loads(doc['chapters']) if doc['chapters'] else []
            docs.append(doc)
        return docs

def get_document(doc_id):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        row = cursor.fetchone()
        if row:
            doc = dict(row)
            doc['chapters'] = json.loads(doc['chapters']) if doc['chapters'] else []
            return doc
        return None

def create_document(doc_data):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO documents (id, title, description, topic, chapters, user, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            doc_data['id'], doc_data['title'], doc_data.get('description', ''),
            doc_data.get('topic', ''), json.dumps(doc_data.get('chapters', []), ensure_ascii=False),
            doc_data['user'], doc_data.get('created_at', datetime.now().isoformat())
        ))

def delete_document(doc_id):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))

# ========== 大纲操作 ==========
def get_outline(outline_id):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM outlines WHERE id = ?', (outline_id,))
        row = cursor.fetchone()
        if row:
            outline = dict(row)
            outline['chapters'] = json.loads(outline['chapters']) if outline['chapters'] else []
            outline['links'] = json.loads(outline['links']) if outline['links'] else []
            outline['enableSearch'] = bool(outline['enable_search'])
            return outline
        return None

def create_outline(outline_data):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO outlines (id, title, description, topic, chapters, links, enable_search, user, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            outline_data['id'], outline_data.get('title', ''), outline_data.get('description', ''),
            outline_data.get('topic', ''), json.dumps(outline_data.get('chapters', []), ensure_ascii=False),
            json.dumps(outline_data.get('links', []), ensure_ascii=False),
            1 if outline_data.get('enableSearch') else 0,
            outline_data['user'], outline_data.get('created_at', datetime.now().isoformat())
        ))

def update_outline(outline_id, chapters=None, feedback=None):
    with get_db_cursor() as cursor:
        if chapters is not None:
            cursor.execute('UPDATE outlines SET chapters = ? WHERE id = ?', 
                          (json.dumps(chapters, ensure_ascii=False), outline_id))
        if feedback is not None:
            cursor.execute('UPDATE outlines SET feedback = ? WHERE id = ?', (feedback, outline_id))

# ========== 任务操作 ==========
def get_tasks(user):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM tasks WHERE user = ? ORDER BY created_at DESC', (user,))
        return [dict(row) for row in cursor.fetchall()]

def get_task(task_id):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_task(task_data):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO tasks (id, type, status, topic, user, current_step, completed, total, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_data['id'], task_data['type'], task_data.get('status', 'pending'),
            task_data.get('topic', ''), task_data['user'], task_data.get('current_step', ''),
            task_data.get('completed', 0), task_data.get('total', 0),
            task_data.get('created_at', datetime.now().isoformat())
        ))

def update_task(task_id, **kwargs):
    with get_db_cursor() as cursor:
        for key, value in kwargs.items():
            cursor.execute(f'UPDATE tasks SET {key} = ? WHERE id = ?', (value, task_id))

# ========== 笔记操作 ==========
def get_notes(article_id, user):
    with get_db_cursor() as cursor:
        cursor.execute(
            'SELECT * FROM notes WHERE article_id = ? AND user = ? ORDER BY created_at DESC',
            (article_id, user)
        )
        return [dict(row) for row in cursor.fetchall()]

def create_note(article_id, question, answer, user):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO notes (article_id, question, answer, user, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (article_id, question, answer, user, datetime.now().isoformat()))
        return cursor.lastrowid

def delete_note(note_id, user):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM notes WHERE id = ? AND user = ?', (note_id, user))

# ========== 配置操作 ==========
def get_config(key):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row['value'] if row else None

def set_config(key, value):
    with get_db_cursor() as cursor:
        cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))

def get_all_config():
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM config')
        return {row['key']: row['value'] for row in cursor.fetchall()}

# 初始化数据库
try:
    init_db()
    print("✅ SQLite 数据库初始化成功")
except Exception as e:
    print(f"⚠️ SQLite 数据库初始化失败: {e}")