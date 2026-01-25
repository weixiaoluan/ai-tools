"""
文章撰写Agent
负责生成单篇完整的学习文章，根据主题类型灵活调整内容风格
"""
import re
import requests
from .base_agent import BaseAgent
from config import AGENT_ROLES, ARTICLE_CONFIG, AI_CONFIG, IMAGE_CONFIG


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
                    "model": IMAGE_CONFIG.get("model", "black-forest-labs/FLUX.1-schnell"),
                    "prompt": prompt,
                    "image_size": IMAGE_CONFIG.get("image_size", "1024x576"),
                    "num_inference_steps": IMAGE_CONFIG.get("num_inference_steps", 20)
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

        prompt = f"""请撰写一篇关于「{topic}」的高质量深度学习文章。

{f'用户要求：{description}' if description else ''}
{context_section}

【核心写作原则】
1. **深度讲解优先**：每个知识点必须有详尽的概念讲解，至少包含：
   - 是什么：准确定义，用通俗易懂的语言解释
   - 为什么：设计初衷，解决什么问题，为什么需要它
   - 怎么用：使用场景、使用时机、最佳实践
   - 注意什么：常见误区、易错点、性能考虑
2. **代码必须详细注释**：每行代码都要有中文注释说明其作用
3. **循序渐进**：从简单到复杂，层层深入

【知识点讲解模板】
每个知识点按以下结构展开：
1. **概念定义**（2-3段）：用生活化类比解释抽象概念
2. **核心原理**（2-3段）：底层机制、工作流程
3. **应用场景**（列举3-5个实际场景）
4. **代码示例**（带详细中文注释）
5. **常见问题与解答**（FAQ形式）
6. **小结**（核心要点回顾）

【代码注释要求】
```python
# 定义一个单例类，确保全局只有一个实例
class Singleton:
    _instance = None  # 类变量，存储唯一实例
    
    def __new__(cls):  # 重写__new__方法控制实例创建
        if cls._instance is None:  # 判断是否已存在实例
            cls._instance = super().__new__(cls)  # 首次创建实例
        return cls._instance  # 返回唯一实例
```

【格式要求】
- 不限制字数，确保每个知识点讲解充分透彻
- 使用Markdown格式，标题层级清晰
- 重要概念用**加粗**突出
- 每个知识点的文字讲解不少于代码量的3倍

【禁止事项】
- 禁止代码没有注释
- 禁止概念一笔带过
- 禁止知识点只有代码没有详细解释

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
