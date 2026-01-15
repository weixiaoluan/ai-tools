"""
文章撰写Agent
负责生成单篇完整的学习文章，根据主题类型灵活调整内容风格
"""
import re
import requests
from .base_agent import BaseAgent
from config import AGENT_ROLES, ARTICLE_CONFIG, AI_CONFIG


class ArticleAgent(BaseAgent):
    """文章撰写专家Agent"""
    
    def __init__(self):
        role = AGENT_ROLES["article_writer"]
        super().__init__(role["name"], role["system_prompt"])
    
    def _generate_image(self, prompt: str) -> str:
        """调用图片生成API"""
        try:
            api_key = AI_CONFIG.get("api_key", "")
            if not api_key:
                return ""
            
            base_url = AI_CONFIG.get("api_base", "https://api.siliconflow.cn/v1")
            
            response = requests.post(
                f"{base_url.rstrip('/')}/images/generations",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "black-forest-labs/FLUX.1-schnell",
                    "prompt": prompt,
                    "image_size": "1024x576",
                    "num_inference_steps": 20
                },
                timeout=90
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("images") and len(data["images"]) > 0:
                    return data["images"][0].get("url", "")
                if data.get("data") and len(data["data"]) > 0:
                    return data["data"][0].get("url", "")
            return ""
        except Exception as e:
            print(f"图片生成失败: {e}")
            return ""
    
    def _insert_images_to_article(self, content: str, topic: str) -> str:
        """在文章合适位置插入AI生成的图片"""
        lines = content.split('\n')
        result_lines = []
        image_count = 0
        max_images = 2
        
        h2_positions = []
        for i, line in enumerate(lines):
            if line.startswith('## '):
                h2_positions.append(i)
        
        insert_after = []
        if len(h2_positions) >= 1:
            insert_after.append(h2_positions[0])
        if len(h2_positions) >= 3:
            insert_after.append(h2_positions[len(h2_positions)//2])
        
        insert_after = sorted(set(insert_after))[:max_images]
        
        for i, line in enumerate(lines):
            result_lines.append(line)
            
            if i in insert_after and image_count < max_images:
                section_title = line.replace('## ', '').strip() if line.startswith('## ') else topic
                prompt = f"A professional illustration for '{topic}' article, section '{section_title}'. Modern, clean, no text, visually appealing."
                
                image_url = self._generate_image(prompt)
                if image_url:
                    result_lines.append('')
                    result_lines.append(f'![{section_title}]({image_url})')
                    result_lines.append('')
                    image_count += 1
        
        return '\n'.join(result_lines)
    
    def generate_article(self, topic: str, description: str = "", extra_context: str = "", generate_images: bool = True) -> dict:
        """生成完整的学习文章"""
        context_section = ""
        if extra_context:
            context_section = f"\n\n参考资料：\n{extra_context[:3000]}\n"

        prompt = f"""请撰写一篇关于「{topic}」的高质量文章。

{f'用户要求：{description}' if description else ''}
{context_section}

写作要求：
1. 根据主题特点自由组织内容结构，不要套用固定模板
2. 文章要有独特视角和深度见解，避免泛泛而谈
3. 语言风格要符合主题特点：技术类专业严谨，人物类生动有趣，生活类轻松实用
4. 如果是技术编程类主题才需要代码示例，其他类型不要包含代码
5. 字数3000-5000字，内容充实有价值
6. 使用Markdown格式，标题层级清晰

直接输出文章内容："""

        content = self.chat(prompt, temperature=0.8)
        
        if generate_images:
            try:
                content = self._insert_images_to_article(content, topic)
            except Exception as e:
                print(f"插入图片时出错: {e}")
        
        lines = content.strip().split('\n')
        title = topic
        if lines and lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
        
        return {
            "title": title,
            "content": content,
            "topic": topic,
            "word_count": len(content)
        }
