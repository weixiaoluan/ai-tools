<template>
  <div class="view document-detail-view">
    <button class="btn-back" @click="$emit('back')">← 返回列表</button>
    
    <div class="document-layout">
      <nav class="document-toc">
        <h4>目录导航</h4>
        <a 
          v-for="ch in document?.chapters" 
          :key="ch.id"
          :class="['toc-item', { active: activeChapter === ch.id }]"
          @click="goToChapter(ch.id)"
        >
          {{ ch.id }}. {{ ch.title }}
        </a>
      </nav>
      
      <div class="document-content glass-card">
        <!-- 文档头部信息 -->
        <div v-if="!viewingChapter" class="document-header">
          <h1 class="document-title">{{ document?.title }}</h1>
          <p class="document-desc" v-if="document?.description">{{ document?.description }}</p>
          <div class="document-meta">
            <span class="tag">学习文档</span>
            <span>📚 {{ document?.chapters?.length || 0 }} 章节</span>
            <span>📅 {{ formatDate(document?.created_at) }}</span>
          </div>
          
          <div class="chapter-grid">
            <div 
              v-for="ch in document?.chapters" 
              :key="ch.id" 
              class="chapter-card"
              @click="goToChapter(ch.id)"
            >
              <span class="chapter-num">{{ ch.id }}</span>
              <div class="chapter-info">
                <h4>{{ ch.title }}</h4>
                <p>点击阅读本章内容</p>
              </div>
              <span class="chapter-arrow">→</span>
            </div>
          </div>
        </div>
        
        <!-- 单章节阅读视图 -->
        <div v-else class="chapter-reader">
          <div class="chapter-nav-top">
            <button class="btn-chapter-nav" @click="viewingChapter = false">
              📚 返回目录
            </button>
            <span class="chapter-indicator">第 {{ activeChapter }} / {{ document?.chapters?.length }} 章</span>
          </div>
          
          <div class="markdown-body">
            <div v-html="renderMarkdown(currentChapterContent)"></div>
          </div>
          
          <!-- 章节切换导航 -->
          <div class="chapter-navigation">
            <button 
              class="nav-btn prev" 
              :disabled="activeChapter <= 1"
              @click="goToChapter(activeChapter - 1)"
            >
              <span class="nav-icon">←</span>
              <span class="nav-text">
                <small>上一章</small>
                <span v-if="prevChapter">{{ prevChapter.title }}</span>
              </span>
            </button>
            
            <button 
              class="nav-btn next" 
              :disabled="activeChapter >= (document?.chapters?.length || 0)"
              @click="goToChapter(activeChapter + 1)"
            >
              <span class="nav-text">
                <small>下一章</small>
                <span v-if="nextChapter">{{ nextChapter.title }}</span>
              </span>
              <span class="nav-icon">→</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'

const props = defineProps({ document: Object })
defineEmits(['back'])

const activeChapter = ref(1)
const viewingChapter = ref(false)

// 配置 marked 使用 highlight.js
const renderer = new marked.Renderer()

renderer.code = function(code, language) {
  const lang = language || 'plaintext'
  let highlighted
  try {
    if (hljs.getLanguage(lang)) {
      highlighted = hljs.highlight(code, { language: lang }).value
    } else {
      highlighted = hljs.highlightAuto(code).value
    }
  } catch (e) {
    highlighted = code
  }
  return `<div class="code-block"><div class="code-header"><span class="code-lang">${lang}</span><button class="copy-btn" onclick="navigator.clipboard.writeText(this.parentElement.nextElementSibling.textContent)">复制</button></div><pre><code class="hljs language-${lang}">${highlighted}</code></pre></div>`
}

marked.use({ renderer, breaks: true, gfm: true })

const currentChapterContent = computed(() => {
  const ch = props.document?.chapters?.find(c => c.id === activeChapter.value)
  return ch?.content || ''
})

const prevChapter = computed(() => {
  return props.document?.chapters?.find(c => c.id === activeChapter.value - 1)
})

const nextChapter = computed(() => {
  return props.document?.chapters?.find(c => c.id === activeChapter.value + 1)
})

function renderMarkdown(content) { return marked(content || '') }

function formatDate(str) {
  if (!str) return ''
  return new Date(str).toLocaleDateString('zh-CN')
}

function goToChapter(id) {
  if (id < 1 || id > (props.document?.chapters?.length || 0)) return
  activeChapter.value = id
  viewingChapter.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.document-detail-view { max-width: 1200px; }
.document-content { flex: 1; min-width: 0; }
.document-title { font-size: 2rem; font-weight: 700; margin-bottom: 12px; color: var(--text-primary); line-height: 1.3; }
.document-desc { color: var(--text-secondary); font-size: 15px; margin-bottom: 16px; }
.document-meta { display: flex; gap: 16px; align-items: center; padding-bottom: 28px; margin-bottom: 28px; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 14px; flex-wrap: wrap; }

/* 章节卡片网格 */
.chapter-grid { display: flex; flex-direction: column; gap: 12px; }

.chapter-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-main);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.chapter-card:hover {
  border-color: var(--primary);
  background: var(--primary-bg);
  transform: translateX(4px);
}

.chapter-num {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.chapter-info { flex: 1; }
.chapter-info h4 { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.chapter-info p { font-size: 13px; color: var(--text-muted); }

.chapter-arrow { font-size: 20px; color: var(--primary); opacity: 0; transition: all 0.2s; }
.chapter-card:hover .chapter-arrow { opacity: 1; transform: translateX(4px); }

/* 章节阅读器 */
.chapter-reader { }

.chapter-nav-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.btn-chapter-nav {
  background: var(--bg-main);
  border: 1px solid var(--border);
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-chapter-nav:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.chapter-indicator {
  font-size: 14px;
  color: var(--text-muted);
  background: var(--bg-main);
  padding: 6px 14px;
  border-radius: 20px;
}

/* 章节切换导航 */
.chapter-navigation {
  display: flex;
  gap: 16px;
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid var(--border);
}

.nav-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: var(--bg-main);
  border: 2px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.nav-btn:hover:not(:disabled) {
  border-color: var(--primary);
  background: var(--primary-bg);
}

.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-btn.next {
  text-align: right;
  flex-direction: row;
  justify-content: flex-end;
}

.nav-icon {
  font-size: 24px;
  color: var(--primary);
}

.nav-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-text small {
  font-size: 12px;
  color: var(--text-muted);
}

.nav-text span:not(small) {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .document-title { font-size: 1.5rem; }
  .document-meta { gap: 12px; }
  .chapter-navigation { flex-direction: column; }
  .nav-btn.next { text-align: left; flex-direction: row; justify-content: flex-start; }
}
</style>
