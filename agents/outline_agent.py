"""
大纲生成Agent
负责根据学习主题生成系统化的学习目录
"""
import json
import re
from .base_agent import BaseAgent
from config import AGENT_ROLES, DOCUMENT_CONFIG


class OutlineAgent(BaseAgent):
    """大纲生成专家Agent"""
    
    def __init__(self):
        role = AGENT_ROLES["outline_generator"]
        super().__init__(role["name"], role["system_prompt"])
    
    def generate_outline(self, topic: str, description: str = "") -> dict:
        """
        生成学习大纲
        
        Args:
            topic: 学习主题
            description: 补充描述
            
        Returns:
            包含章节列表的字典
        """
        prompt = f"""请为以下学习主题生成一个系统化的学习目录大纲：

主题：{topic}
{f'补充说明：{description}' if description else ''}

要求：
1. 生成 {DOCUMENT_CONFIG['min_chapters']} 到 {DOCUMENT_CONFIG['max_chapters']} 个章节
2. 从基础到进阶，循序渐进
3. 覆盖该主题的核心知识点
4. 每个章节包含标题和简要描述

请严格按照以下JSON格式返回：
{{
    "title": "完整的学习文档标题",
    "description": "学习文档的整体描述",
    "chapters": [
        {{
            "id": 1,
            "title": "章节标题",
            "description": "章节简要描述",
            "keywords": ["关键词1", "关键词2"]
        }}
    ]
}}

只返回JSON，不要其他内容。"""

        response = self.chat(prompt, temperature=0.7)
        
        # 解析JSON
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                outline = json.loads(json_match.group())
                return outline
        except json.JSONDecodeError:
            pass
        
        # 如果解析失败，返回默认结构
        return {
            "title": f"{topic} 学习指南",
            "description": f"系统学习 {topic} 的完整教程",
            "chapters": [
                {"id": 1, "title": f"{topic} 入门介绍", "description": "基础概念和入门知识", "keywords": [topic]},
                {"id": 2, "title": f"{topic} 核心概念", "description": "核心知识点详解", "keywords": [topic]},
                {"id": 3, "title": f"{topic} 实践应用", "description": "实际应用和案例", "keywords": [topic]},
            ]
        }
    
    def regenerate_outline(self, topic: str, feedback: str = "") -> dict:
        """
        根据反馈重新生成大纲
        
        Args:
            topic: 学习主题
            feedback: 用户反馈
            
        Returns:
            新的大纲
        """
        prompt = f"""请根据以下反馈，重新生成学习大纲：

主题：{topic}
用户反馈：{feedback}

请生成一个更符合用户需求的学习目录，严格按照JSON格式返回。"""

        return self.generate_outline(topic, feedback)
