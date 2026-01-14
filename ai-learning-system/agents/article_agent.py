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

        prompt = f"""撰写一篇关于「{topic}」的专业学习文章。{f' 要求：{description}' if description else ''}{context_section}

【核心原则】
1. 以概念讲解为主，代码示例为辅（文字内容占80%以上）
2. 每个知识点必须讲透彻：定义→原理→应用场景→注意事项
3. 专业、系统、详细，像教科书一样严谨

【文章要求】
- 字数3000-5000字，重点是知识讲解的深度和广度
- 代码示例简洁精炼，仅用于辅助说明概念
- 多用类比、图示说明、对比分析帮助理解

【输出格式】Markdown：

# [标题]

> 📚 **导读**：[本文核心内容概括]

## 1. 概述与背景
[详细介绍该技术/概念的背景、发展历程、为什么重要]

## 2. 核心概念详解
### 2.1 [概念1名称]
**定义**：[准确的定义]
**原理**：[底层原理详细解释]
**应用场景**：[什么情况下使用]
**与相关概念的区别**：[对比分析]

### 2.2 [概念2名称]
[同样的详细结构]

## 3. 工作机制与原理
[深入讲解内部工作原理，可用流程图文字描述]

## 4. 代码示例
```语言
// 简洁的示例代码，配合详细注释
```
**代码解析**：[逐行解释代码含义]

## 5. 最佳实践与常见问题
### 5.1 最佳实践
- ✅ [实践建议及原因]

### 5.2 常见误区
- ❌ [误区及正确做法]

## 6. 总结
### 核心要点回顾
1. [要点1]
2. [要点2]

### 延伸学习
[推荐的进阶学习方向]

直接输出文章内容。"""

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
