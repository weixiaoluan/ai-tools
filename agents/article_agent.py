"""
文章撰写Agent
负责生成单篇完整的学习文章
"""
from .base_agent import BaseAgent
from config import AGENT_ROLES, ARTICLE_CONFIG


class ArticleAgent(BaseAgent):
    """文章撰写专家Agent"""
    
    def __init__(self):
        role = AGENT_ROLES["article_writer"]
        super().__init__(role["name"], role["system_prompt"])
    
    def generate_article(self, topic: str, description: str = "", extra_context: str = "") -> dict:
        """
        生成完整的学习文章
        
        Args:
            topic: 文章主题
            description: 补充描述
            extra_context: 额外的参考资料
            
        Returns:
            包含标题和内容的字典
        """
        context_section = ""
        if extra_context:
            context_section = f"\n参考资料：\n{extra_context[:3000]}\n"

        prompt = f"""撰写一篇关于「{topic}」的学习文章。{f' 要求：{description}' if description else ''}{context_section}

文章要求：
- 字数2000-4000字，内容丰富实用
- 包含代码示例（如适用）
- 结构清晰，循序渐进

输出格式（Markdown）：

# [标题]

> 📚 **导读**：[简要概括]

## 1. 引言
[背景介绍]

## 2. 核心概念
### 2.1 [概念1]
[详细说明+代码示例]

### 2.2 [概念2]
[详细说明]

## 3. 实践应用
### 3.1 实战案例
[完整代码示例]

### 3.2 最佳实践
- ✅ 推荐做法
- ❌ 避免做法

## 4. 总结
### 核心要点
1. [要点1]
2. [要点2]
3. [要点3]

### 学习建议
[后续学习方向]

直接输出文章内容，不要其他说明。"""

        content = self.chat(prompt, temperature=0.7)
        
        # 提取标题
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
