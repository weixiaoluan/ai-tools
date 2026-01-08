<template>
  <div class="view article-detail-view">
    <button class="btn-back" @click="$emit('back')">← 返回列表</button>
    
    <div class="document-layout">
      <!-- 目录侧边栏 -->
      <aside class="document-toc" :class="{ 'toc-open': tocOpen }" v-if="tocItems.length > 0">
        <div class="toc-header">
          <h4>目录导航</h4>
          <button class="toc-close" @click="tocOpen = false">✕</button>
        </div>
        <div class="toc-title">{{ article?.title }}</div>
        <a v-for="item in tocItems" :key="item.id"
           :class="['toc-item', `toc-level-${item.level}`, { active: activeId === item.id }]"
           @click.prevent="scrollToHeading(item.id); tocOpen = false">
          {{ item.text }}
        </a>
      </aside>
      
      <!-- 移动端目录按钮 -->
      <button class="mobile-toc-btn" @click="tocOpen = true" v-if="tocItems.length > 0">
        📑 目录
      </button>
      
      <!-- 文章内容 -->
      <div class="article-content glass-card">
        <h1 class="article-title">{{ article?.title }}</h1>
        <div class="article-meta">
          <span>📅 {{ formatDate(article?.created_at) }}</span>
          <span class="tag">{{ article?.type === 'chapter' ? '章节' : '文章' }}</span>
        </div>
        <div class="markdown-body" ref="contentRef" v-html="renderedContent"></div>
      </div>
    </div>
    
    <!-- AI问答悬浮按钮 -->
    <button class="ai-fab" @click="showAiPanel = true" title="AI问答">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      </svg>
      <span>AI</span>
    </button>

    <!-- AI问答面板 -->
    <div v-if="showAiPanel" class="ai-panel">
      <div class="ai-panel-header">
        <h3>🤖 AI问答助手</h3>
        <button class="ai-panel-close" @click="showAiPanel = false">✕</button>
      </div>
      
      <div class="ai-panel-body">
        <!-- 历史笔记 -->
        <div v-if="notes.length > 0" class="notes-section">
          <h4>📝 我的笔记</h4>
          <div v-for="note in notes" :key="note.id" class="note-item">
            <div class="note-q">Q: {{ note.question }}</div>
            <div class="note-a">{{ note.answer }}</div>
            <button class="note-delete" @click="deleteNote(note.id)">删除</button>
          </div>
        </div>
        
        <!-- 当前对话 -->
        <div v-if="currentAnswer" class="current-qa">
          <div class="qa-question">{{ currentQuestion }}</div>
          <div class="qa-answer" v-html="renderAnswer(currentAnswer)"></div>
          <div class="qa-actions">
            <button class="btn btn-sm btn-primary" @click="saveAsNote">💾 保存为笔记</button>
            <button class="btn btn-sm btn-secondary" @click="clearAnswer">清除</button>
          </div>
        </div>
      </div>
      
      <div class="ai-panel-footer">
        <input v-model="question" class="ai-input" placeholder="输入你的问题..." @keyup.enter="askQuestion" :disabled="asking" />
        <button class="ai-send-btn" @click="askQuestion" :disabled="asking || !question.trim()">
          {{ asking ? '思考中...' : '发送' }}
        </button>
      </div>
    </div>
    
    <!-- 遮罩 -->
    <div v-if="showAiPanel || tocOpen" class="panel-overlay" @click="showAiPanel = false; tocOpen = false"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import axios from 'axios'

const props = defineProps({ article: Object })
defineEmits(['back'])

const contentRef = ref(null)
const tocItems = ref([])
const activeId = ref('')
const tocOpen = ref(false)

// AI问答
const showAiPanel = ref(false)
const question = ref('')
const asking = ref(false)
const currentQuestion = ref('')
const currentAnswer = ref('')
const notes = ref([])

// Markdown配置
const renderer = new marked.Renderer()
renderer.code = function(code, language) {
  const lang = language || 'plaintext'
  let highlighted
  try {
    highlighted = hljs.getLanguage(lang) ? hljs.highlight(code, { language: lang }).value : hljs.highlightAuto(code).value
  } catch (e) { highlighted = code }
  return `<div class="code-block"><div class="code-header"><span class="code-lang">${lang}</span><button class="copy-btn" onclick="navigator.clipboard.writeText(this.parentElement.nextElementSibling.textContent)">复制</button></div><pre><code class="hljs">${highlighted}</code></pre></div>`
}
marked.use({ renderer, breaks: true, gfm: true })

const renderedContent = computed(() => {
  if (!props.article?.content) return ''
  let content = props.article.content
  content = content.replace(/^##?\s*📖?\s*目录[\s\S]*?(?=^---|\n##?\s[^目])/m, '')
  return marked(content)
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function extractToc() {
  nextTick(() => {
    if (!contentRef.value) return
    const headings = contentRef.value.querySelectorAll('h1, h2, h3')
    tocItems.value = Array.from(headings).map((h, idx) => {
      const id = `heading-${idx}`
      h.id = id
      return { id, text: h.textContent, level: parseInt(h.tagName.charAt(1)) }
    })
    if (tocItems.value.length > 0) activeId.value = tocItems.value[0].id
  })
}

function scrollToHeading(id) {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeId.value = id
  }
}

function renderAnswer(text) { return marked(text) }

async function loadNotes() {
  if (!props.article?.id) return
  try {
    const res = await axios.get(`/api/notes/${props.article.id}`)
    notes.value = res.data.notes || []
  } catch (e) { console.error(e) }
}

async function askQuestion() {
  if (!question.value.trim() || asking.value) return
  asking.value = true
  currentQuestion.value = question.value
  currentAnswer.value = ''
  
  try {
    const res = await axios.post('/api/ask', { article_id: props.article.id, question: question.value })
    currentAnswer.value = res.data.answer
    question.value = ''
  } catch (e) {
    currentAnswer.value = '抱歉，回答失败：' + (e.response?.data?.detail || e.message)
  }
  asking.value = false
}

async function saveAsNote() {
  if (!currentQuestion.value || !currentAnswer.value) return
  try {
    await axios.post('/api/notes', { article_id: props.article.id, question: currentQuestion.value, answer: currentAnswer.value })
    await loadNotes()
    clearAnswer()
  } catch (e) { alert('保存失败') }
}

function clearAnswer() {
  currentQuestion.value = ''
  currentAnswer.value = ''
}

async function deleteNote(noteId) {
  if (!confirm('确定删除这条笔记吗？')) return
  try {
    await axios.delete(`/api/notes/${noteId}`)
    await loadNotes()
  } catch (e) { alert('删除失败') }
}

watch(() => props.article, () => { extractToc(); loadNotes() }, { immediate: true })
onMounted(() => { extractToc(); loadNotes() })
</script>

<style scoped>
.article-detail-view { max-width: 1200px; position: relative; }
.article-content { flex: 1; min-width: 0; }
.article-title { font-size: 1.75rem; font-weight: 700; margin-bottom: 16px; color: var(--text-primary); line-height: 1.4; }
.article-meta { display: flex; gap: 16px; align-items: center; padding-bottom: 24px; margin-bottom: 24px; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 14px; flex-wrap: wrap; }

.toc-header { display: none; }
.toc-close { display: none; }
.toc-title { font-size: 14px; font-weight: 600; color: var(--text-primary); padding: 8px 12px; margin-bottom: 8px; background: var(--bg-main); border-radius: 6px; }
.toc-level-2 { padding-left: 24px !important; }
.toc-level-3 { padding-left: 36px !important; font-size: 13px; }

.mobile-toc-btn { display: none; }

/* AI悬浮按钮 */
.ai-fab {
  position: fixed;
  bottom: 100px;
  right: 24px;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
  border: none;
  border-radius: 50%;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  z-index: 100;
  transition: all 0.3s;
}
.ai-fab:hover { transform: scale(1.1); box-shadow: 0 6px 30px rgba(99, 102, 241, 0.5); }
.ai-fab span { font-size: 10px; font-weight: 600; }

/* AI面板 */
.ai-panel {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 420px;
  max-width: 100%;
  height: 70vh;
  max-height: 600px;
  background: white;
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -10px 40px rgba(0,0,0,0.15);
  z-index: 1001;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }

.ai-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(135deg, #EEF2FF, #F5F3FF);
}
.ai-panel-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.ai-panel-close { background: none; border: none; font-size: 20px; color: var(--text-muted); cursor: pointer; }

.ai-panel-body { flex: 1; overflow-y: auto; padding: 16px; }

.notes-section h4 { font-size: 14px; color: var(--text-secondary); margin-bottom: 12px; }
.note-item { background: var(--bg-main); border-radius: 8px; padding: 12px; margin-bottom: 12px; position: relative; }
.note-q { font-size: 13px; color: var(--primary); font-weight: 500; margin-bottom: 6px; }
.note-a { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
.note-delete { position: absolute; top: 8px; right: 8px; background: none; border: none; color: var(--text-muted); font-size: 12px; cursor: pointer; }
.note-delete:hover { color: var(--error); }

.current-qa { background: linear-gradient(135deg, #EEF2FF, #F5F3FF); border-radius: 12px; padding: 16px; margin-top: 16px; }
.qa-question { font-size: 14px; font-weight: 600; color: var(--primary); margin-bottom: 12px; }
.qa-answer { font-size: 14px; color: var(--text-secondary); line-height: 1.6; }
.qa-actions { display: flex; gap: 8px; margin-top: 12px; }

.ai-panel-footer { padding: 16px; border-top: 1px solid var(--border); display: flex; gap: 8px; }
.ai-input { flex: 1; padding: 12px 16px; border: 1px solid var(--border); border-radius: 24px; font-size: 14px; }
.ai-input:focus { outline: none; border-color: var(--primary); }
.ai-send-btn { padding: 12px 20px; background: var(--primary); color: white; border: none; border-radius: 24px; font-size: 14px; font-weight: 500; cursor: pointer; }
.ai-send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.panel-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); z-index: 1000; }

/* 移动端适配 */
@media (max-width: 768px) {
  .article-title { font-size: 1.4rem; }
  .document-toc { position: fixed; left: 0; top: 0; bottom: 0; width: 280px; z-index: 1001; transform: translateX(-100%); transition: transform 0.3s; background: white; }
  .document-toc.toc-open { transform: translateX(0); }
  .toc-header { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-bottom: 1px solid var(--border); }
  .toc-close { display: block; background: none; border: none; font-size: 20px; color: var(--text-muted); cursor: pointer; }
  .mobile-toc-btn { display: flex; position: fixed; bottom: 170px; right: 24px; padding: 10px 16px; background: white; border: 1px solid var(--border); border-radius: 20px; font-size: 13px; color: var(--text-primary); cursor: pointer; z-index: 99; box-shadow: var(--shadow-md); }
  .ai-fab { bottom: 100px; right: 16px; width: 50px; height: 50px; }
  .ai-panel { width: 100%; height: 80vh; border-radius: 20px 20px 0 0; }
}
</style>
