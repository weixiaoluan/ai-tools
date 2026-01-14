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

        prompt = f"""撰写学习文档章节：

文档：{document_context.get('title', '')}
目录：{chapters_overview}

当前章节：第{chapter_info['id']}章 - {chapter_info['title']}
描述：{chapter_info.get('description', '')}
{reference_content}

【核心原则】
1. 以概念讲解为主，代码示例为辅（文字内容占80%以上）
2. 每个知识点必须讲透彻：定义→原理→应用场景→注意事项
3. 专业、系统、详细，像教科书一样严谨

【要求】
- 字数2000-3500字，重点是知识讲解的深度
- 代码示例简洁精炼，仅用于辅助说明
- 多用类比、对比分析帮助理解

【输出格式】Markdown：

# 第{chapter_info['id']}章 {chapter_info['title']}

> 📌 **本章概要**：[本章核心内容概括]

## 学习目标
- 🎯 [目标1]
- 🎯 [目标2]

---

## {chapter_info['id']}.1 [概念名称]
**定义**：[准确的定义]
**原理详解**：[深入讲解原理，为什么这样设计]
**应用场景**：[什么情况下使用]
**与相关概念对比**：[帮助区分理解]

## {chapter_info['id']}.2 [概念名称]
[同样的详细结构]

## {chapter_info['id']}.3 代码示例
```语言
// 简洁示例
```
**代码解析**：[详细解释每行代码的含义]

## {chapter_info['id']}.4 实战练习
[练习题目+思路提示]

---

## 📝 本章小结
- ✅ [核心要点1及理解要点]
- ✅ [核心要点2及理解要点]
- ✅ [核心要点3及理解要点]

直接输出章节内容。"""

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
