"""
SQLite 到 MySQL 数据库迁移脚本
将 SQLite 数据库的数据导出并导入到 MySQL 数据库
"""
import sqlite3
import pymysql
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# SQLite 数据库路径
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'learnflow.db')

# MySQL 配置
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'learnflow'),
    'charset': 'utf8mb4',
}

def get_sqlite_connection():
    """获取 SQLite 连接"""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_mysql_connection():
    """获取 MySQL 连接"""
    return pymysql.connect(**MYSQL_CONFIG)

def migrate_users(mysql_conn):
    """迁移用户表"""
    print("📦 迁移用户表...")
    sqlite_conn = get_sqlite_connection()
    try:
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()

        sqlite_cursor.execute('SELECT * FROM users')
        users = sqlite_cursor.fetchall()

        for user in users:
            user_dict = dict(user)
            mysql_cursor.execute('''
                INSERT INTO users (username, email, password, token, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE email=%s, password=%s, token=%s
            ''', (
                user_dict['username'], user_dict.get('email'), user_dict['password'],
                user_dict.get('token'), user_dict['created_at'],
                user_dict.get('email'), user_dict['password'], user_dict.get('token')
            ))

        mysql_conn.commit()
        print(f"✅ 用户表迁移完成，共 {len(users)} 条记录")
    finally:
        sqlite_conn.close()

def migrate_articles(mysql_conn):
    """迁移文章表"""
    print("📦 迁移文章表...")
    sqlite_conn = get_sqlite_connection()
    try:
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()

        sqlite_cursor.execute('SELECT * FROM articles')
        articles = sqlite_cursor.fetchall()

        for article in articles:
            article_dict = dict(article)
            mysql_cursor.execute('''
                INSERT INTO articles (id, title, content, topic, type, document_id, chapter_id, user, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE title=%s, content=%s, updated_at=%s
            ''', (
                article_dict['id'], article_dict['title'], article_dict.get('content'),
                article_dict.get('topic'), article_dict.get('type', 'article'),
                article_dict.get('document_id'), article_dict.get('chapter_id'),
                article_dict['user'], article_dict['created_at'], article_dict.get('updated_at'),
                article_dict['title'], article_dict.get('content'), article_dict.get('updated_at')
            ))

        mysql_conn.commit()
        print(f"✅ 文章表迁移完成，共 {len(articles)} 条记录")
    finally:
        sqlite_conn.close()

def migrate_documents(mysql_conn):
    """迁移文档表"""
    print("📦 迁移文档表...")
    sqlite_conn = get_sqlite_connection()
    try:
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()

        sqlite_cursor.execute('SELECT * FROM documents')
        documents = sqlite_cursor.fetchall()

        for doc in documents:
            doc_dict = dict(doc)
            mysql_cursor.execute('''
                INSERT INTO documents (id, title, description, topic, chapters, user, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE title=%s, description=%s, topic=%s, chapters=%s
            ''', (
                doc_dict['id'], doc_dict['title'], doc_dict.get('description'),
                doc_dict.get('topic'), doc_dict['chapters'], doc_dict['user'], doc_dict['created_at'],
                doc_dict['title'], doc_dict.get('description'), doc_dict.get('topic'), doc_dict['chapters']
            ))

        mysql_conn.commit()
        print(f"✅ 文档表迁移完成，共 {len(documents)} 条记录")
    finally:
        sqlite_conn.close()

def migrate_outlines(mysql_conn):
    """迁移大纲表"""
    print("📦 迁移大纲表...")
    sqlite_conn = get_sqlite_connection()
    try:
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()

        sqlite_cursor.execute('SELECT * FROM outlines')
        outlines = sqlite_cursor.fetchall()

        for outline in outlines:
            outline_dict = dict(outline)
            mysql_cursor.execute('''
                INSERT INTO outlines (id, title, description, topic, chapters, links, enable_search, feedback, user, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE title=%s, description=%s, topic=%s, chapters=%s, links=%s, enable_search=%s, feedback=%s
            ''', (
                outline_dict['id'], outline_dict.get('title'), outline_dict.get('description'),
                outline_dict.get('topic'), outline_dict.get('chapters'), outline_dict.get('links'),
                outline_dict.get('enable_search', 0), outline_dict.get('feedback'),
                outline_dict['user'], outline_dict['created_at'],
                outline_dict.get('title'), outline_dict.get('description'), outline_dict.get('topic'),
                outline_dict.get('chapters'), outline_dict.get('links'),
                outline_dict.get('enable_search', 0), outline_dict.get('feedback')
            ))

        mysql_conn.commit()
        print(f"✅ 大纲表迁移完成，共 {len(outlines)} 条记录")
    finally:
        sqlite_conn.close()

def migrate_tasks(mysql_conn):
    """迁移任务表"""
    print("📦 迁移任务表...")
    sqlite_conn = get_sqlite_connection()
    try:
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()

        sqlite_cursor.execute('SELECT * FROM tasks')
        tasks = sqlite_cursor.fetchall()

        for task in tasks:
            task_dict = dict(task)
            mysql_cursor.execute('''
                INSERT INTO tasks (id, type, status, topic, user, current_step, completed, total, error, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE status=%s, current_step=%s, completed=%s, total=%s, error=%s
            ''', (
                task_dict['id'], task_dict.get('type'), task_dict.get('status'),
                task_dict.get('topic'), task_dict['user'], task_dict.get('current_step'),
                task_dict.get('completed', 0), task_dict.get('total', 0),
                task_dict.get('error'), task_dict['created_at'],
                task_dict.get('status'), task_dict.get('current_step'),
                task_dict.get('completed', 0), task_dict.get('total', 0), task_dict.get('error')
            ))

        mysql_conn.commit()
        print(f"✅ 任务表迁移完成，共 {len(tasks)} 条记录")
    finally:
        sqlite_conn.close()

def migrate_notes(mysql_conn):
    """迁移笔记表"""
    print("📦 迁移笔记表...")
    sqlite_conn = get_sqlite_connection()
    try:
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()

        sqlite_cursor.execute('SELECT * FROM notes')
        notes = sqlite_cursor.fetchall()

        for note in notes:
            note_dict = dict(note)
            mysql_cursor.execute('''
                INSERT INTO notes (id, article_id, question, answer, user, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE question=%s, answer=%s
            ''', (
                note_dict['id'], note_dict['article_id'], note_dict.get('question'),
                note_dict.get('answer'), note_dict['user'], note_dict['created_at'],
                note_dict.get('question'), note_dict.get('answer')
            ))

        mysql_conn.commit()
        print(f"✅ 笔记表迁移完成，共 {len(notes)} 条记录")
    finally:
        sqlite_conn.close()

def migrate_config(mysql_conn):
    """迁移配置表"""
    print("📦 迁移配置表...")
    sqlite_conn = get_sqlite_connection()
    try:
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()

        sqlite_cursor.execute('SELECT * FROM config')
        configs = sqlite_cursor.fetchall()

        for config in configs:
            config_dict = dict(config)
            mysql_cursor.execute('''
                INSERT INTO config (`key`, value)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE value=%s
            ''', (
                config_dict['key'], config_dict['value'], config_dict['value']
            ))

        mysql_conn.commit()
        print(f"✅ 配置表迁移完成，共 {len(configs)} 条记录")
    finally:
        sqlite_conn.close()

def main():
    print("=" * 60)
    print("🔄 SQLite 到 MySQL 数据库迁移工具")
    print("=" * 60)

    # 检查 SQLite 数据库是否存在
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ SQLite 数据库文件不存在: {SQLITE_DB_PATH}")
        return

    # 连接 MySQL
    print(f"🔗 连接到 MySQL: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
    try:
        mysql_conn = get_mysql_connection()
        print("✅ MySQL 连接成功")
    except Exception as e:
        print(f"❌ MySQL 连接失败: {e}")
        print("请确保 MySQL 服务已启动，并在 .env 文件中配置正确的数据库连接信息")
        return

    try:
        # 执行迁移
        migrate_users(mysql_conn)
        migrate_articles(mysql_conn)
        migrate_documents(mysql_conn)
        migrate_outlines(mysql_conn)
        migrate_tasks(mysql_conn)
        migrate_notes(mysql_conn)
        migrate_config(mysql_conn)

        print("\n" + "=" * 60)
        print("🎉 数据迁移完成！")
        print("=" * 60)
        print("\n接下来请：")
        print("1. 确认 MySQL 数据库中的数据是否正确")
        print("2. 修改 app.py 中的数据库导入顺序，优先使用 MySQL")
        print("3. 重启应用")

    except Exception as e:
        print(f"\n❌ 迁移过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mysql_conn.close()

if __name__ == "__main__":
    main()