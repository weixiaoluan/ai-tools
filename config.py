"""
AI学习系统配置文件
参考 weixiaoluan/trade 项目架构风格
"""
import os
from dotenv import load_dotenv

load_dotenv()

# AI API 配置
AI_CONFIG = {
    "api_key": os.getenv("AI_API_KEY", ""),
    "api_base": os.getenv("AI_API_BASE", "https://api.siliconflow.cn/v1"),
    "model": os.getenv("AI_MODEL", "deepseek-ai/DeepSeek-V3"),
    "temperature": 0.7,
    "max_tokens": 4096
}

# 文章生成配置
ARTICLE_CONFIG = {
    "min_words": 1500,
    "max_words": 5000,
    "style": "professional",  # professional, beginner, advanced
}

# 学习文档配置
DOCUMENT_CONFIG = {
    "min_chapters": 5,
    "max_chapters": 15,
    "chapter_min_words": 800,
    "chapter_max_words": 2000,
}

# Agent 角色定义
AGENT_ROLES = {
    "outline_generator": {
        "name": "大纲生成专家",
        "description": "负责根据学习主题生成系统化的学习目录大纲",
        "system_prompt": """你是一位专业的课程设计专家，擅长将复杂的知识体系拆解为循序渐进的学习路径。
你的任务是根据用户提供的学习主题，生成一个系统化、结构清晰的学习目录大纲。

要求：
1. 目录应该从基础到进阶，循序渐进
2. 每个章节标题要清晰明确
3. 覆盖该主题的核心知识点
4. 包含实践和应用章节
5. 返回JSON格式的目录结构"""
    },
    "article_writer": {
        "name": "文章撰写专家",
        "description": "负责撰写高质量的学习文章",
        "system_prompt": """你是一位资深的技术写作专家，擅长将复杂的技术概念用通俗易懂的方式讲解。
你的任务是根据给定的主题撰写一篇系统、专业的学习文章。

要求：
1. 内容要系统全面，覆盖核心知识点
2. 从基础概念讲起，循序渐进
3. 包含实际案例和代码示例（如适用）
4. 语言通俗易懂，适合学习者阅读
5. 使用Markdown格式输出
6. 文章结构清晰，包含引言、正文、总结"""
    },
    "chapter_writer": {
        "name": "章节撰写专家",
        "description": "负责根据大纲撰写具体章节内容",
        "system_prompt": """你是一位专业的教程撰写专家，擅长编写详细的学习章节内容。
你的任务是根据给定的章节标题和上下文，撰写详细的章节内容。

要求：
1. 内容要详实，深入浅出
2. 包含必要的代码示例和图解说明
3. 每个概念都要有清晰的解释
4. 适当添加小结和练习建议
5. 使用Markdown格式输出"""
    }
}
