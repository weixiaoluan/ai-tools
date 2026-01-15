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
    
    def _detect_topic_type(self, topic: str, description: str = "") -> str:
        """检测主题类型"""
        combined = f"{topic} {description}".lower()
        
        tech_keywords = ['python', 'java', 'javascript', 'react', 'vue', 'node', 'api', 
                        '编程', '开发', '代码', '算法', '数据库', 'sql', 'linux', 'docker',
                        '框架', '前端', '后端', '服务器', '云计算', 'ai', '机器学习', '深度学习']
        person_keywords = ['明星', '演员', '歌手', '艺人', '名人', '人物', '传记', '生平',
                          '介绍', '简介', '个人', '偶像', '球星', '运动员', '作家', '导演',
                          '企业家', '科学家', '政治家', '历史人物']
        science_keywords = ['科学', '物理', '化学', '生物', '天文', '地理', '历史', '文化',
                           '原理', '现象', '为什么', '如何', '什么是', '科普']
        life_keywords = ['美食', '旅游', '健康', '养生', '运动', '电影', '音乐', '游戏',
                        '时尚', '穿搭', '美妆', '宠物', '家居', '育儿']
        business_keywords = ['商业', '创业', '管理', '营销', '职场', '面试', '简历', 
                            '投资', '理财', '股票', '经济']
        
        for kw in tech_keywords:
            if kw in combined: return 'tech'
        for kw in person_keywords:
            if kw in combined: return 'person'
        for kw in science_keywords:
            if kw in combined: return 'science'
        for kw in life_keywords:
            if kw in combined: return 'life'
        for kw in business_keywords:
            if kw in combined: return 'business'
        return 'general'
    
    def _get_prompt_template(self, topic_type: str) -> str:
        """根据主题类型返回对应的提示词模板"""
        templates = {
            'tech': """【文章类型】技术教程类
【核心原则】以概念讲解为主，代码示例为辅，专业系统详细

【文章结构】
# [标题]
> 📚 **导读**：[核心内容概括]

## 1. 概述与背景
## 2. 核心概念详解
## 3. 实践示例（简洁代码+详细注释）
## 4. 最佳实践与常见问题
## 5. 总结""",

            'person': """【文章类型】人物介绍类
【核心原则】以人物故事为主线，生动有趣，不需要代码示例

【文章结构】
# [人物名称]：[一句话概括]
> 🌟 **人物简介**：[身份和成就]

## 1. 基本信息
## 2. 成长经历
## 3. 职业生涯
## 4. 个人特点与风格
## 5. 社会影响与评价
## 6. 趣闻轶事
## 7. 总结""",

            'science': """【文章类型】科普知识类
【核心原则】深入浅出，多用类比，不需要代码示例

【文章结构】
# [标题]：[副标题]
> 🔬 **导读**：[有趣的问题引入]

## 1. 引言
## 2. 基本概念
## 3. 原理解析
## 4. 发展历史
## 5. 实际应用
## 6. 有趣的事实
## 7. 总结与展望""",

            'life': """【文章类型】生活娱乐类
【核心原则】轻松有趣，实用性强，不需要代码示例

【文章结构】
# [标题]
> ✨ **导读**：[简短引言]

## 1. 开篇
## 2. 魅力所在
## 3. 详细介绍
## 4. 实用建议
## 5. 注意事项
## 6. 总结""",

            'business': """【文章类型】商业职场类
【核心原则】专业严谨，结合案例，不需要代码示例

【文章结构】
# [标题]
> 💼 **导读**：[核心观点]

## 1. 背景与现状
## 2. 核心概念
## 3. 案例分析
## 4. 实践策略
## 5. 常见误区
## 6. 总结与建议""",

            'general': """【文章类型】通用知识类
【核心原则】内容充实，结构清晰，只在必要时包含代码

【文章结构】
# [标题]
> 📖 **导读**：[核心内容概括]

## 1. 引言
## 2. 主要内容
## 3. 深入分析
## 4. 实际应用
## 5. 总结"""
        }
        return templates.get(topic_type, templates['general'])
    
    def _generate_image(self, prompt: str, api_base: str = "") -> str:
        """调用图片生成API"""
        try:
            api_key = AI_CONFIG.get("api_key", "")
            if not api_key:
                return ""
            
            # 使用配置的 API base 或默认 SiliconFlow
            base_url = api_base or AI_CONFIG.get("api_base", "https://api.siliconflow.cn/v1")
            
            # 尝试调用图片生成接口
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
    
    def _insert_images_to_article(self, content: str, topic: str, topic_type: str) -> str:
        """在文章合适位置插入AI生成的图片"""
        lines = content.split('\n')
        result_lines = []
        image_count = 0
        max_images = 3  # 最多插入3张图片
        
        # 找到所有二级标题的位置
        h2_positions = []
        for i, line in enumerate(lines):
            if line.startswith('## '):
                h2_positions.append(i)
        
        # 选择要插入图片的位置（第1个、中间、最后一个章节后）
        insert_after = []
        if len(h2_positions) >= 1:
            insert_after.append(h2_positions[0])  # 第一个章节后
        if len(h2_positions) >= 3:
            insert_after.append(h2_positions[len(h2_positions)//2])  # 中间章节后
        if len(h2_positions) >= 2:
            insert_after.append(h2_positions[-1])  # 最后一个章节后
        
        # 去重并排序
        insert_after = sorted(set(insert_after))[:max_images]
        
        for i, line in enumerate(lines):
            result_lines.append(line)
            
            # 在选定的章节标题后插入图片
            if i in insert_after and image_count < max_images:
                # 获取章节标题作为图片描述参考
                section_title = line.replace('## ', '').strip() if line.startswith('## ') else topic
                
                # 生成图片提示词
                image_prompt = self._create_image_prompt(topic, section_title, topic_type)
                
                if image_prompt:
                    # 生成图片
                    image_url = self._generate_image(image_prompt)
                    
                    if image_url:
                        # 在章节标题后插入空行和图片
                        result_lines.append('')
                        result_lines.append(f'![{section_title}]({image_url})')
                        result_lines.append('')
                        image_count += 1
                        print(f"已插入图片 {image_count}: {section_title}")
        
        return '\n'.join(result_lines)
    
    def _create_image_prompt(self, topic: str, section: str, topic_type: str) -> str:
        """根据主题和章节创建图片生成提示词"""
        style_hints = {
            'tech': 'modern technology, digital, clean design, professional',
            'person': 'portrait style, artistic, elegant, professional photography',
            'science': 'scientific illustration, educational, detailed, informative',
            'life': 'lifestyle, vibrant colors, warm atmosphere, inviting',
            'business': 'corporate, professional, modern office, business concept',
            'general': 'clean, modern, professional, high quality'
        }
        
        style = style_hints.get(topic_type, style_hints['general'])
        
        # 构建英文提示词
        prompt = f"A high-quality illustration for an article about '{topic}', specifically for the section '{section}'. Style: {style}. No text in image, visually appealing, suitable for blog article."
        
        return prompt
    
    def generate_article(self, topic: str, description: str = "", extra_context: str = "", generate_images: bool = True) -> dict:
        """生成完整的学习文章"""
        # 检测主题类型
        topic_type = self._detect_topic_type(topic, description)
        template = self._get_prompt_template(topic_type)
        
        context_section = ""
        if extra_context:
            context_section = f"\n\n【参考资料】\n{extra_context[:3000]}\n"

        prompt = f"""撰写一篇关于「{topic}」的文章。{f' 补充要求：{description}' if description else ''}{context_section}

{template}

【重要提醒】
1. 严格根据主题类型调整内容，不要生搬硬套模板
2. 如果主题与技术/编程无关，绝对不要包含代码示例
3. 文章要有深度和广度，字数3000-5000字
4. 内容要真实、准确、有价值

直接输出文章内容，使用Markdown格式。"""

        content = self.chat(prompt, temperature=0.7)
        
        # 生成并插入配图
        if generate_images:
            try:
                content = self._insert_images_to_article(content, topic, topic_type)
            except Exception as e:
                print(f"插入图片时出错: {e}")
        
        # 提取标题
        lines = content.strip().split('\n')
        title = topic
        if lines and lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
        
        return {
            "title": title,
            "content": content,
            "topic": topic,
            "topic_type": topic_type,
            "word_count": len(content)
        }
### 2.3 [要点3]
[详细内容]

## 3. 深入分析
[更深层次的探讨]

## 4. 实际应用/案例
[具体的例子或应用场景]

## 5. 总结
[核心要点回顾]"""
        }
        
        return templates.get(topic_type, templates['general'])
    
    def _generate_image_prompt(self, topic: str, section: str = "") -> str:
        """
        根据主题生成图片提示词
        """
        prompt = f"""为文章「{topic}」生成一张配图。
{f'图片用于章节：{section}' if section else ''}

要求：
1. 图片风格：现代、专业、高质量
2. 适合作为文章配图
3. 不包含文字
4. 色彩和谐，视觉效果好

直接返回英文的图片描述提示词，不超过100个单词。"""
        
        return self.chat(prompt, temperature=0.8)
    
    def _generate_image(self, prompt: str) -> str:
        """
        调用图片生成API生成图片
        返回图片URL
        """
        try:
            # 使用 SiliconFlow 的图片生成 API
            api_key = AI_CONFIG.get("api_key", "")
            if not api_key:
                return ""
            
            response = requests.post(
                "https://api.siliconflow.cn/v1/images/generations",
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
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("images") and len(data["images"]) > 0:
                    return data["images"][0].get("url", "")
            return ""
        except Exception as e:
            print(f"图片生成失败: {e}")
            return ""
    
    def generate_article(self, topic: str, description: str = "", extra_context: str = "", generate_images: bool = True) -> dict:
        """
        生成完整的学习文章
        
        Args:
            topic: 文章主题
            description: 补充描述
            extra_context: 额外的参考资料
            generate_images: 是否生成配图
            
        Returns:
            包含标题和内容的字典
        """
        # 检测主题类型
        topic_type = self._detect_topic_type(topic, description)
        template = self._get_prompt_template(topic_type)
        
        context_section = ""
        if extra_context:
            context_section = f"\n\n【参考资料】\n{extra_context[:3000]}\n"

        prompt = f"""撰写一篇关于「{topic}」的文章。{f' 补充要求：{description}' if description else ''}{context_section}

{template}

【重要提醒】
1. 严格根据主题类型调整内容，不要生搬硬套模板
2. 如果主题与技术/编程无关，绝对不要包含代码示例
3. 文章要有深度和广度，字数3000-5000字
4. 内容要真实、准确、有价值
5. 在适合插入图片的位置，使用 ![图片描述](IMAGE_PLACEHOLDER_N) 格式标记，N为序号

直接输出文章内容，使用Markdown格式。"""

        content = self.chat(prompt, temperature=0.7)
        
        # 生成配图
        if generate_images:
            # 查找所有图片占位符
            image_placeholders = re.findall(r'!\[([^\]]*)\]\(IMAGE_PLACEHOLDER_(\d+)\)', content)
            
            for desc, idx in image_placeholders:
                # 生成图片提示词
                image_prompt = self._generate_image_prompt(topic, desc)
                # 生成图片
                image_url = self._generate_image(image_prompt)
                
                if image_url:
                    # 替换占位符为实际图片URL
                    content = content.replace(
                        f'![{desc}](IMAGE_PLACEHOLDER_{idx})',
                        f'![{desc}]({image_url})'
                    )
                else:
                    # 如果生成失败，移除占位符
                    content = content.replace(f'![{desc}](IMAGE_PLACEHOLDER_{idx})\n', '')
                    content = content.replace(f'![{desc}](IMAGE_PLACEHOLDER_{idx})', '')
        
        # 提取标题
        lines = content.strip().split('\n')
        title = topic
        if lines and lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
        
        return {
            "title": title,
            "content": content,
            "topic": topic,
            "topic_type": topic_type,
            "word_count": len(content)
        }
