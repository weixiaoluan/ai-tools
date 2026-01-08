"""
章节撰写Agent
负责根据大纲生成具体章节内容，支持联网搜索权威资料
"""
from .base_agent import BaseAgent
from .content_parser import ContentParser
from config import AGENT_ROLES, DOCUMENT_CONFIG


class ChapterAgent(BaseAgent):
    """章节撰写专家Agent"""
    
    def __init__(self):
        role = AGENT_ROLES["chapter_writer"]
        super().__init__(role["name"], role["system_prompt"])
        self.parser = None
    
    def _get_parser(self):
        if self.parser is None:
            self.parser = ContentParser()
        return self.parser
    
    def search_references(self, topic: str, keywords: list) -> str:
        """搜索权威参考资料"""
        try:
            parser = self._get_parser()
            search_query = f"{topic} {' '.join(keywords[:3])} 教程 官方文档"
            results = parser.web_search(search_query)
            
            if results and len(results) > 0:
                ref_text = "\n\n### 参考资料\n"
                for r in results[:3]:
                    if isinstance(r, dict):
                        ref_text += f"- {r.get('results', '')[:500]}\n"
                return ref_text
        except Exception as e:
            print(f"搜索参考资料失败: {e}")
        return ""
    
    def generate_chapter(self, chapter_info: dict, document_context: dict, enable_search: bool = False) -> str:
        """生成单个章节内容"""
        self.reset()
        
        chapters_overview = "\n".join([
            f"第{ch['id']}章: {ch['title']}" 
            for ch in document_context.get('chapters', [])
        ])
        
        # 搜索参考资料
        reference_content = ""
        if enable_search:
            keywords = chapter_info.get('keywords', [chapter_info['title']])
            reference_content = self.search_references(
                document_context.get('topic', ''),
                keywords
            )

        prompt = f"""请为以下学习文档撰写一个完整、详细的章节内容：

文档标题：{document_context.get('title', '')}
文档描述：{document_context.get('description', '')}

完整目录：
{chapters_overview}

当前需要撰写的章节：
- 章节序号：第{chapter_info['id']}章
- 章节标题：{chapter_info['title']}
- 章节描述：{chapter_info.get('description', '')}
{reference_content}

## 重要撰写要求
1. 章节字数必须在 2000-3500 字之间，内容要非常丰富
2. 每个知识点都要深入讲解，配合代码示例
3. 代码示例必须完整、可运行、有详细注释
4. 包含实际应用场景和最佳实践
5. 语言通俗易懂，适合学习者阅读

## Markdown格式要求（严格遵循）

# 第{chapter_info['id']}章 {chapter_info['title']}

> 📌 **本章概要**：[2-3句话概括本章核心内容和学习价值]

## 学习目标
完成本章学习后，你将能够：
- 🎯 [具体目标1]
- 🎯 [具体目标2]
- 🎯 [具体目标3]

---

## {chapter_info['id']}.1 [小节标题]

[详细内容，至少500字，深入讲解]

### 核心概念

> 💡 **重要提示**：[关键知识点说明]

### 代码示例

```language
// 完整的示例代码
// 包含详细注释
// 代码要可以直接运行
```

**代码解析：**
- [解释代码的关键部分]

### 实践要点

| 要点 | 说明 | 注意事项 |
|------|------|----------|
| xxx | xxx | xxx |

---

## {chapter_info['id']}.2 [小节标题]

[详细内容，至少500字]

### 深入理解

[深入讲解原理]

### 完整示例

```language
// 更复杂的完整示例
```

---

## {chapter_info['id']}.3 [小节标题]

[详细内容]

---

## {chapter_info['id']}.4 实战练习

### 练习1：[练习标题]

**需求描述：**
[详细描述]

**参考实现：**
```language
// 完整的参考代码
```

### 练习2：[练习标题]

**需求描述：**
[详细描述]

---

## 📝 本章小结

### 核心要点
- ✅ **[要点1]**：[说明]
- ✅ **[要点2]**：[说明]
- ✅ **[要点3]**：[说明]
- ✅ **[要点4]**：[说明]

### 常见问题

**Q: [问题1]？**
A: [详细解答]

**Q: [问题2]？**
A: [详细解答]

### 下一步学习
[引导到下一章的内容]

---

请严格按照上述格式输出，确保内容丰富、代码完整、排版美观。"""

        content = self.chat(prompt, temperature=0.7)
        return content
    
    def generate_all_chapters(self, outline: dict, progress_callback=None) -> list:
        """批量生成所有章节（串行方式，用于兼容）"""
        chapters = []
        total = len(outline.get('chapters', []))
        
        for i, chapter_info in enumerate(outline.get('chapters', [])):
            self.reset()
            content = self.generate_chapter(chapter_info, outline)
            chapters.append({
                "id": chapter_info['id'],
                "title": chapter_info['title'],
                "content": content
            })
            
            if progress_callback:
                progress_callback(i + 1, total, chapter_info['title'])
        
        return chapters
