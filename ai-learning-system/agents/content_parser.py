"""
内容解析Agent
负责解析文档、图片、链接等内容
"""
import os
import re
import json
import httpx
from typing import List, Optional
from .base_agent import BaseAgent
from config import AI_CONFIG


class ContentParser(BaseAgent):
    """内容解析专家Agent"""
    
    def __init__(self):
        system_prompt = """你是一位专业的内容分析专家，擅长从各种来源提取和整理信息。
你的任务是分析用户提供的内容，提取关键信息，并整理成结构化的学习资料。

要求：
1. 准确提取核心知识点
2. 保持信息的完整性和准确性
3. 整理成清晰的结构
4. 标注信息来源"""
        super().__init__("内容解析专家", system_prompt)
    
    def parse_text_file(self, content: str, filename: str) -> dict:
        """解析文本文件内容"""
        prompt = f"""请分析以下文档内容，提取关键信息：

文件名：{filename}
内容：
{content[:8000]}  # 限制长度

请提取：
1. 文档主题
2. 核心知识点（列表形式）
3. 重要概念和定义
4. 关键结论

以JSON格式返回：
{{"topic": "主题", "key_points": ["要点1", "要点2"], "concepts": ["概念1"], "conclusions": ["结论1"]}}"""
        
        response = self.chat(prompt)
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {"topic": filename, "key_points": [], "concepts": [], "conclusions": []}
    
    def parse_image(self, image_description: str) -> dict:
        """解析图片内容（通过描述）"""
        prompt = f"""请分析以下图片描述，提取学习相关的信息：

图片描述：{image_description}

请提取可能的学习要点和知识信息。"""
        
        response = self.chat(prompt)
        return {"description": image_description, "analysis": response}
    
    def parse_url(self, url: str) -> dict:
        """解析网页链接内容"""
        try:
            # 简单获取网页内容
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, follow_redirects=True)
                content = response.text
            
            # 简单提取文本（去除HTML标签）
            text = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', content)
            text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', content)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 限制长度
            text = text[:5000]
            
            prompt = f"""请分析以下网页内容，提取关键学习信息：

URL: {url}
内容摘要：
{text}

请提取：
1. 页面主题
2. 核心知识点
3. 重要信息

以JSON格式返回。"""
            
            response = self.chat(prompt)
            try:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    result = json.loads(json_match.group())
                    result["url"] = url
                    return result
            except:
                pass
            return {"url": url, "topic": "网页内容", "key_points": []}
        except Exception as e:
            return {"url": url, "error": str(e)}
    
    def web_search(self, query: str) -> List[dict]:
        """联网搜索（模拟，实际需要接入搜索API）"""
        prompt = f"""用户想要学习关于「{query}」的内容。

请基于你的知识，提供：
1. 该主题的最新发展和趋势
2. 推荐的学习资源和方向
3. 核心知识点概述

以结构化的方式回答。"""
        
        response = self.chat(prompt)
        return [{"query": query, "results": response}]
    
    def combine_sources(self, topic: str, sources: List[dict]) -> str:
        """整合多个来源的信息"""
        sources_text = "\n\n".join([
            f"来源 {i+1}:\n{json.dumps(s, ensure_ascii=False, indent=2)}"
            for i, s in enumerate(sources)
        ])
        
        prompt = f"""请整合以下多个来源的信息，为学习主题「{topic}」生成一份综合的参考资料：

{sources_text}

要求：
1. 去除重复信息
2. 整理成逻辑清晰的结构
3. 标注信息来源
4. 突出核心知识点

请以Markdown格式输出整合后的参考资料。"""
        
        return self.chat(prompt)
