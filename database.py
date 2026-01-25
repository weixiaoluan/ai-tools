"""
数据库模块 - MySQL持久化存储（带连接池）
"""
import pymysql
from pymysql.cursors import DictCursor
import json
import os
import threading
import queue
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

# ========== 简易连接池实现 ==========
class ConnectionPool:
    """简易MySQL连接池"""
    
    def __init__(self, config: dict, pool_size: int = 5, max_overflow: int = 10):
        self.config = config
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self._pool = queue.Queue(maxsize=pool_size)
        self._current_size = 0
        self._lock = threading.Lock()
        
        # 预创建连接
        for _ in range(pool_size):
            try:
                conn = self._create_connection()
                self._pool.put(conn, block=False)
                self._current_size += 1
            except:
                break
    
    def _create_connection(self):
        """创建新连接"""
        return pymysql.connect(**self.config)
    
    def _validate_connection(self, conn):
        """验证连接是否有效"""
        try:
            conn.ping(reconnect=True)
            return True
        except:
            return False
    
    def get_connection(self):
        """获取连接"""
        # 尝试从池中获取
        try:
            conn = self._pool.get(block=False)
            if self._validate_connection(conn):
                return conn
            # 连接无效，创建新的
            conn = self._create_connection()
            return conn
        except queue.Empty:
            pass
        
        # 池为空，尝试创建新连接
        with self._lock:
            if self._current_size < self.pool_size + self.max_overflow:
                self._current_size += 1
                return self._create_connection()
        
        # 等待连接释放
        conn = self._pool.get(block=True, timeout=30)
        if self._validate_connection(conn):
            return conn
        return self._create_connection()
    
    def release_connection(self, conn):
        """释放连接回池"""
        try:
            if self._validate_connection(conn):
                self._pool.put(conn, block=False)
            else:
                with self._lock:
                    self._current_size -= 1
                try:
                    conn.close()
                except:
                    pass
        except queue.Full:
            # 池满，直接关闭
            with self._lock:
                self._current_size -= 1
            try:
                conn.close()
            except:
                pass
    
    def close_all(self):
        """关闭所有连接"""
        while not self._pool.empty():
            try:
                conn = self._pool.get(block=False)
                conn.close()
            except:
                pass
        self._current_size = 0

# 全局连接池
_connection_pool = None

def get_pool():
    """获取全局连接池"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool(DB_CONFIG, pool_size=5, max_overflow=10)
    return _connection_pool

def get_db():
    """获取数据库连接（从连接池）"""
    return get_pool().get_connection()

@contextmanager
def get_db_cursor():
    """数据库游标上下文管理器（使用连接池）"""
    pool = get_pool()
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        pool.release_connection(conn)

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
                password VARCHAR(255) NOT NULL,
                token VARCHAR(255),
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
        
        # 面试题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                article_id VARCHAR(50) NOT NULL,
                question TEXT NOT NULL,
                reference_answer LONGTEXT,
                user_answer LONGTEXT,
                score INT,
                feedback LONGTEXT,
                user VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                answered_at DATETIME,
                INDEX idx_article (article_id),
                INDEX idx_user (user)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 对话记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(500) DEFAULT '新对话',
                messages LONGTEXT,
                user VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user)
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

ALLOWED_TASK_FIELDS = {'status', 'current_step', 'completed', 'total', 'error'}

def update_task(task_id, **kwargs):
    """更新任务状态（防SQL注入）"""
    with get_db_cursor() as cursor:
        for key, value in kwargs.items():
            if key not in ALLOWED_TASK_FIELDS:
                continue
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

# ========== 面试题操作 ==========
def get_interview_questions(article_id, user):
    with get_db_cursor() as cursor:
        cursor.execute(
            'SELECT * FROM interview_questions WHERE article_id = %s AND user = %s ORDER BY created_at DESC',
            (article_id, user)
        )
        return cursor.fetchall()

def create_interview_question(article_id, question, reference_answer, user):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO interview_questions (article_id, question, reference_answer, user, created_at)
            VALUES (%s, %s, %s, %s, %s)
        ''', (article_id, question, reference_answer, user, datetime.now()))
        return cursor.lastrowid

def update_interview_answer(question_id, user_answer, score, feedback, user):
    with get_db_cursor() as cursor:
        cursor.execute('''
            UPDATE interview_questions 
            SET user_answer = %s, score = %s, feedback = %s, answered_at = %s 
            WHERE id = %s AND user = %s
        ''', (user_answer, score, feedback, datetime.now(), question_id, user))

def delete_interview_question(question_id, user):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM interview_questions WHERE id = %s AND user = %s', (question_id, user))

def get_interview_question(question_id, user):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM interview_questions WHERE id = %s AND user = %s', (question_id, user))
        return cursor.fetchone()

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

# ========== 对话记录操作 ==========
def get_conversations(user):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT id, title, created_at, updated_at FROM conversations WHERE user = %s ORDER BY updated_at DESC', (user,))
        return cursor.fetchall()

def get_conversation(conv_id, user):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM conversations WHERE id = %s AND user = %s', (conv_id, user))
        row = cursor.fetchone()
        if row:
            row['messages'] = json.loads(row['messages']) if row['messages'] else []
        return row

def create_conversation(conv_id, user, title='新对话'):
    with get_db_cursor() as cursor:
        cursor.execute('''
            INSERT INTO conversations (id, title, messages, user, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (conv_id, title, '[]', user, datetime.now(), datetime.now()))

def update_conversation(conv_id, messages, title=None):
    with get_db_cursor() as cursor:
        if title:
            cursor.execute('UPDATE conversations SET messages = %s, title = %s, updated_at = %s WHERE id = %s',
                          (json.dumps(messages, ensure_ascii=False), title, datetime.now(), conv_id))
        else:
            cursor.execute('UPDATE conversations SET messages = %s, updated_at = %s WHERE id = %s',
                          (json.dumps(messages, ensure_ascii=False), datetime.now(), conv_id))

def delete_conversation(conv_id, user):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM conversations WHERE id = %s AND user = %s', (conv_id, user))

# 初始化数据库
try:
    init_db()
    print("✅ MySQL 数据库初始化成功")
except Exception as e:
    print(f"⚠️ MySQL 数据库初始化失败: {e}")
    print("请确保 MySQL 服务已启动，并在 .env 文件中配置正确的数据库连接信息")
