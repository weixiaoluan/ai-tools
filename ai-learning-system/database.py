"""
数据库模块 - MySQL持久化存储
"""
import pymysql
from pymysql.cursors import DictCursor
import json
import os
from datetime import datetime
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# MySQL 配置
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'learnflow'),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

def get_db():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

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
    # 先创建数据库（如果不存在）
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"创建数据库失败: {e}")
    
    with get_db_cursor() as cursor:
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(200),
                password VARCHAR(255),
                token VARCHAR(255),
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at DATETIME,
                auth_type VARCHAR(50) DEFAULT 'password',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 文章表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content LONGTEXT,
                topic VARCHAR(500),
                type VARCHAR(50) DEFAULT 'article',
                document_id VARCHAR(50),
                chapter_id INT,
                user VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                INDEX idx_user (user),
                INDEX idx_document (document_id),
                INDEX idx_type (type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 文档表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                topic VARCHAR(500),
                chapters LONGTEXT,
                user VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 大纲表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outlines (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(500),
                description TEXT,
                topic VARCHAR(500),
                chapters LONGTEXT,
                links LONGTEXT,
                enable_search TINYINT DEFAULT 0,
                feedback TEXT,
                user VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id VARCHAR(50) PRIMARY KEY,
                type VARCHAR(50),
                status VARCHAR(50),
                topic VARCHAR(500),
                user VARCHAR(100) NOT NULL,
                current_step TEXT,
                completed INT DEFAULT 0,
                total INT DEFAULT 0,
                error TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 笔记表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                article_id VARCHAR(50) NOT NULL,
                question TEXT,
                answer LONGTEXT,
                user VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_article (article_id),
                INDEX idx_user (user)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                `key` VARCHAR(100) PRIMARY KEY,
                value TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

# ========== 用户操作 ==========
def get_user(username):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        return cursor.fetchone()

def get_user_by_token(token):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE token = %s', (token,))
        return cursor.fetchone()

def create_user(username, email, password):
    with get_db_cursor() as cursor:
        cursor.execute(
            'INSERT INTO users (username, email, password, created_at) VALUES (%s, %s, %s, %s)',
            (username, email, password, datetime.now())
        )

def update_user_token(username, token):
    with get_db_cursor() as cursor:
        cursor.execute('UPDATE users SET token = %s WHERE username = %s', (token, username))

# ========== 文章操作 ==========
def get_articles(user, include_chapters=False):
    with get_db_cursor() as cursor:
        if include_chapters:
            cursor.execute('SELECT * FROM articles WHERE user = %s ORDER BY created_at DESC', (user,))
        else:
            cursor.execute('SELECT * FROM articles WHERE user = %s AND type != %s ORDER BY created_at DESC', (user, 'chapter'))
        return cursor.fetchall()

def get_article(article_id):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM articles WHERE id = %s', (article_id,))
        return cursor.fetchone()

def create_article(article_data):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO articles (id, title, content, topic, type, document_id, chapter_id, user, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            article_data['id'], article_data['title'], article_data.get('content', ''),
            article_data.get('topic', ''), article_data.get('type', 'article'),
            article_data.get('document_id'), article_data.get('chapter_id'),
            article_data['user'], article_data.get('created_at', datetime.now())
        ))

def update_article(article_id, title, content):
    with get_db_cursor() as cursor:
        cursor.execute(
            'UPDATE articles SET title = %s, content = %s, updated_at = %s WHERE id = %s',
            (title, content, datetime.now(), article_id)
        )

def delete_article(article_id):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM articles WHERE id = %s', (article_id,))

def delete_articles_by_document(document_id):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM articles WHERE document_id = %s', (document_id,))

# ========== 文档操作 ==========
def get_documents(user):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM documents WHERE user = %s ORDER BY created_at DESC', (user,))
        docs = []
        for row in cursor.fetchall():
            doc = dict(row)
            doc['chapters'] = json.loads(doc['chapters']) if doc['chapters'] else []
            docs.append(doc)
        return docs

def get_document(doc_id):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM documents WHERE id = %s', (doc_id,))
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
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            doc_data['id'], doc_data['title'], doc_data.get('description', ''),
            doc_data.get('topic', ''), json.dumps(doc_data.get('chapters', []), ensure_ascii=False),
            doc_data['user'], doc_data.get('created_at', datetime.now())
        ))

def delete_document(doc_id):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM documents WHERE id = %s', (doc_id,))

# ========== 大纲操作 ==========
def get_outline(outline_id):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM outlines WHERE id = %s', (outline_id,))
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            outline_data['id'], outline_data.get('title', ''), outline_data.get('description', ''),
            outline_data.get('topic', ''), json.dumps(outline_data.get('chapters', []), ensure_ascii=False),
            json.dumps(outline_data.get('links', []), ensure_ascii=False),
            1 if outline_data.get('enableSearch') else 0,
            outline_data['user'], outline_data.get('created_at', datetime.now())
        ))

def update_outline(outline_id, chapters=None, feedback=None):
    with get_db_cursor() as cursor:
        if chapters is not None:
            cursor.execute('UPDATE outlines SET chapters = %s WHERE id = %s', 
                          (json.dumps(chapters, ensure_ascii=False), outline_id))
        if feedback is not None:
            cursor.execute('UPDATE outlines SET feedback = %s WHERE id = %s', (feedback, outline_id))

# ========== 任务操作 ==========
def get_tasks(user):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM tasks WHERE user = %s ORDER BY created_at DESC', (user,))
        return cursor.fetchall()

def get_task(task_id):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM tasks WHERE id = %s', (task_id,))
        return cursor.fetchone()

def create_task(task_data):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO tasks (id, type, status, topic, user, current_step, completed, total, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            task_data['id'], task_data['type'], task_data.get('status', 'pending'),
            task_data.get('topic', ''), task_data['user'], task_data.get('current_step', ''),
            task_data.get('completed', 0), task_data.get('total', 0),
            task_data.get('created_at', datetime.now())
        ))

def update_task(task_id, **kwargs):
    with get_db_cursor() as cursor:
        for key, value in kwargs.items():
            cursor.execute(f'UPDATE tasks SET {key} = %s WHERE id = %s', (value, task_id))

# ========== 笔记操作 ==========
def get_notes(article_id, user):
    with get_db_cursor() as cursor:
        cursor.execute(
            'SELECT * FROM notes WHERE article_id = %s AND user = %s ORDER BY created_at DESC',
            (article_id, user)
        )
        return cursor.fetchall()

def create_note(article_id, question, answer, user):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO notes (article_id, question, answer, user, created_at)
            VALUES (%s, %s, %s, %s, %s)
        ''', (article_id, question, answer, user, datetime.now()))
        return cursor.lastrowid

def delete_note(note_id, user):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM notes WHERE id = %s AND user = %s', (note_id, user))

# ========== 配置操作 ==========
def get_config(key):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT value FROM config WHERE `key` = %s', (key,))
        row = cursor.fetchone()
        return row['value'] if row else None

def set_config(key, value):
    with get_db_cursor() as cursor:
        cursor.execute('INSERT INTO config (`key`, value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE value = %s', 
                      (key, value, value))

def get_all_config():
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM config')
        return {row['key']: row['value'] for row in cursor.fetchall()}

# ========== OAuth 认证操作 ==========
def create_oauth_user(username: str, email: str, access_token: str, refresh_token: str, expires_at: datetime):
    """创建 OAuth 用户"""
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO users (username, email, access_token, refresh_token, token_expires_at, auth_type, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (username, email, access_token, refresh_token, expires_at, 'oauth', datetime.now()))
        return cursor.lastrowid

def update_oauth_tokens(username: str, access_token: str, refresh_token: str, expires_at: datetime):
    """更新 OAuth token"""
    with get_db_cursor() as cursor:
        cursor.execute('''
            UPDATE users SET access_token = %s, refresh_token = %s, token_expires_at = %s
            WHERE username = %s
        ''', (access_token, refresh_token, expires_at, username))

def get_oauth_tokens(username: str):
    """获取用户的 OAuth token"""
    with get_db_cursor() as cursor:
        cursor.execute('''
            SELECT access_token, refresh_token, token_expires_at
            FROM users WHERE username = %s AND auth_type = %s
        ''', (username, 'oauth'))
        row = cursor.fetchone()
        if row:
            return {
                'access_token': row['access_token'],
                'refresh_token': row['refresh_token'],
                'expires_at': row['token_expires_at']
            }
        return None

# 初始化数据库
try:
    init_db()
    print("✅ MySQL 数据库初始化成功")
except Exception as e:
    print(f"⚠️ MySQL 数据库初始化失败: {e}")
    print("请确保 MySQL 服务已启动，并在 .env 文件中配置正确的数据库连接信息")
