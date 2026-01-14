<template>
  <div class="view document-detail-view">
    <button class="btn-back" @click="$emit('back')">← 返回列表</button>
    
    <div class="document-layout">
      <nav class="document-toc" :class="{ 'toc-open': tocOpen }">
        <div class="toc-header">
          <h4>目录导航</h4>
          <button class="toc-close" @click="tocOpen = false">✕</button>
        </div>
        <a 
          v-for="ch in document?.chapters" 
          :key="ch.id"
          :class="['toc-item', { active: activeChapter === ch.id }]"
          @click="goToChapter(ch.id); tocOpen = false"
        >
          {{ ch.id }}. {{ ch.title }}
        </a>
      </nav>
      
      <!-- 移动端目录按钮 -->
      <button class="mobile-toc-btn" @click="tocOpen = true" v-if="document?.chapters?.length > 0">
        📑 目录
      </button>
      
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
          
          <div class="markdown-body" ref="contentRef">
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
    
    <!-- AI问答悬浮按钮 -->
    <button class="ai-fab" @click="showAiPanel = true" title="AI问答助手" v-if="viewingChapter">
      <svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor">
        <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A1.5 1.5 0 0 0 6 14.5A1.5 1.5 0 0 0 7.5 16A1.5 1.5 0 0 0 9 14.5A1.5 1.5 0 0 0 7.5 13m9 0a1.5 1.5 0 0 0-1.5 1.5a1.5 1.5 0 0 0 1.5 1.5a1.5 1.5 0 0 0 1.5-1.5a1.5 1.5 0 0 0-1.5-1.5M12 9a5 5 0 0 0-5 5v6h10v-6a5 5 0 0 0-5-5z"/>
      </svg>
    </button>

    <!-- AI问答面板 -->
    <div v-if="showAiPanel" class="ai-panel">
      <div class="ai-panel-header">
        <h3>🤖 AI问答助手</h3>
        <button class="ai-panel-close" @click="showAiPanel = false">✕</button>
      </div>
      
      <div class="ai-panel-body">
        <!-- 当前对话 -->
        <div v-if="currentAnswer" class="current-qa">
          <div class="qa-question">{{ currentQuestion }}</div>
          <div class="qa-answer" v-html="renderMarkdown(currentAnswer)"></div>
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
    
    <!-- 底部操作栏 -->
    <div class="article-bottom-bar" v-if="viewingChapter">
      <button class="bottom-action" @click="showNotesPanel = true">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
        <span>笔记</span>
        <span v-if="notes.length > 0" class="badge">{{ notes.length }}</span>
      </button>
      <button class="bottom-action" @click="showSharePanel = true">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
          <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/>
        </svg>
        <span>分享</span>
      </button>
    </div>
    
    <!-- 分享面板 -->
    <div v-if="showSharePanel" class="share-panel">
      <div class="share-panel-header">
        <h3>分享文章</h3>
        <button class="panel-close" @click="showSharePanel = false">✕</button>
      </div>
      <div class="share-options">
        <button class="share-btn wechat" @click="shareToWechat">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
            <path d="M9.5 4C5.36 4 2 6.69 2 10c0 1.89 1.08 3.56 2.78 4.66L4 17l2.5-1.5c.89.31 1.87.5 2.91.5.09 0 .18 0 .27-.01-.18-.64-.27-1.31-.27-2 0-3.87 3.58-7 8-7 .34 0 .67.02 1 .05C17.44 4.56 13.78 2.5 9.5 4zM7 9c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm5 0c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm5.5 2c-3.87 0-7 2.69-7 6s3.13 6 7 6c.78 0 1.53-.12 2.23-.33L21 24l-.78-2.33C21.94 20.19 22.5 18.67 22.5 17c0-3.31-3.13-6-7-6zm-2 7c-.41 0-.75-.34-.75-.75s.34-.75.75-.75.75.34.75.75-.34.75-.75.75zm4 0c-.41 0-.75-.34-.75-.75s.34-.75.75-.75.75.34.75.75-.34.75-.75.75z"/>
          </svg>
          <span>微信</span>
        </button>
        <button class="share-btn qq" @click="shareToQQ">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.2-.08-.06-.19-.04-.27-.02-.12.02-1.96 1.25-5.54 3.66-.52.36-1 .53-1.42.52-.47-.01-1.37-.26-2.03-.48-.82-.27-1.47-.42-1.42-.88.03-.24.37-.49 1.02-.75 3.98-1.73 6.64-2.87 7.97-3.43 3.8-1.58 4.59-1.86 5.1-1.87.11 0 .37.03.54.17.14.12.18.28.2.45-.01.06.01.24 0 .37z"/>
          </svg>
          <span>QQ</span>
        </button>
        <button class="share-btn wecom" @click="shareToWecom">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
          <span>企业微信</span>
        </button>
        <button class="share-btn dingtalk" @click="shareToDingtalk">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.95 14.5l-2.9-1.53c-.25-.13-.53-.2-.82-.2H11c-.28 0-.55.07-.8.2l-2.9 1.53c-.35.18-.75-.1-.68-.48l.5-2.93c.05-.27-.03-.55-.2-.77l-2.1-2.5c-.25-.3-.08-.75.3-.8l2.95-.4c.27-.04.51-.2.65-.44l1.32-2.68c.17-.35.67-.35.84 0l1.32 2.68c.14.24.38.4.65.44l2.95.4c.38.05.55.5.3.8l-2.1 2.5c-.17.22-.25.5-.2.77l.5 2.93c.07.38-.33.66-.68.48z"/>
          </svg>
          <span>钉钉</span>
        </button>
      </div>
      <button class="share-copy-btn" @click="copyShareLink">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
          <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
        </svg>
        复制链接
      </button>
    </div>
    
    <!-- 笔记面板 -->
    <div v-if="showNotesPanel" class="notes-panel">
      <div class="notes-panel-header">
        <h3>📝 我的笔记</h3>
        <button class="panel-close" @click="showNotesPanel = false">✕</button>
      </div>
      <div class="notes-panel-body">
        <div v-if="notes.length === 0" class="notes-empty">
          <div class="empty-icon">📝</div>
          <p>暂无笔记</p>
          <span>点击AI按钮提问，可将回答保存为笔记</span>
        </div>
        <div v-for="note in notes" :key="note.id" class="note-card">
          <div class="note-q">Q: {{ note.question }}</div>
          <div class="note-a" v-html="renderMarkdown(note.answer)"></div>
          <div class="note-footer">
            <span class="note-time">{{ formatDate(note.created_at) }}</span>
            <button class="note-delete-btn" @click="deleteNote(note.id)">删除</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 遮罩 -->
    <div v-if="showAiPanel || tocOpen || showSharePanel || showNotesPanel" class="panel-overlay" @click="showAiPanel = false; tocOpen = false; showSharePanel = false; showNotesPanel = false"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import axios from 'axios'

const props = defineProps({ document: Object })
defineEmits(['back'])

const activeChapter = ref(1)
const viewingChapter = ref(false)
const tocOpen = ref(false)
const contentRef = ref(null)

// AI问答
const showAiPanel = ref(false)
const question = ref('')
const asking = ref(false)
const currentQuestion = ref('')
const currentAnswer = ref('')
const notes = ref([])

// 分享和笔记面板
const showSharePanel = ref(false)
const showNotesPanel = ref(false)

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

const currentChapter = computed(() => {
  return props.document?.chapters?.find(c => c.id === activeChapter.value)
})

const currentChapterContent = computed(() => {
  return currentChapter.value?.content || ''
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
  loadNotes()
}

// AI问答功能
async function loadNotes() {
  if (!currentChapter.value) return
  const articleId = `${props.document?.id}-${activeChapter.value}`
  try {
    const res = await axios.get(`/api/notes/${articleId}`)
    notes.value = res.data.notes || []
  } catch (e) { console.error(e) }
}

async function askQuestion() {
  if (!question.value.trim() || asking.value) return
  asking.value = true
  currentQuestion.value = question.value
  currentAnswer.value = ''
  
  const articleId = `${props.document?.id}-${activeChapter.value}`
  try {
    const res = await axios.post('/api/ask', { article_id: articleId, question: question.value })
    currentAnswer.value = res.data.answer
    question.value = ''
  } catch (e) {
    currentAnswer.value = '抱歉，回答失败：' + (e.response?.data?.detail || e.message)
  }
  asking.value = false
}

async function saveAsNote() {
  if (!currentQuestion.value || !currentAnswer.value) return
  const articleId = `${props.document?.id}-${activeChapter.value}`
  try {
    await axios.post('/api/notes', { article_id: articleId, question: currentQuestion.value, answer: currentAnswer.value })
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

// 分享功能
function getShareUrl() {
  return `${window.location.origin}/article/${props.document?.id}-${activeChapter.value}`
}

function shareToWechat() {
  copyShareLink()
  alert('链接已复制，请在微信中粘贴分享')
}

function shareToQQ() {
  const url = encodeURIComponent(getShareUrl())
  const title = encodeURIComponent(currentChapter.value?.title || '学习文章')
  window.open(`https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${title}`, '_blank')
}

function shareToWecom() {
  copyShareLink()
  alert('链接已复制，请在企业微信中粘贴分享')
}

function shareToDingtalk() {
  const url = encodeURIComponent(getShareUrl())
  const title = encodeURIComponent(currentChapter.value?.title || '学习文章')
  window.open(`https://page.dingtalk.com/wow/dingtalk/act/shareurl?url=${url}&title=${title}`, '_blank')
}

function copyShareLink() {
  const url = getShareUrl()
  navigator.clipboard.writeText(url).then(() => {
    alert('链接已复制到剪贴板')
  }).catch(() => {
    const input = document.createElement('input')
    input.value = url
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    alert('链接已复制到剪贴板')
  })
}

watch(() => props.document, () => {
  activeChapter.value = 1
  viewingChapter.value = false
}, { immediate: true })
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
  .document-toc { position: fixed; left: 0; top: 0; bottom: 0; width: 280px; z-index: 1001; transform: translateX(-100%); transition: transform 0.3s; background: white; padding: 0; overflow-y: auto; }
  .document-toc.toc-open { transform: translateX(0); }
  .toc-header { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-bottom: 1px solid var(--border); }
  .toc-header h4 { margin: 0; }
  .toc-close { display: block; background: none; border: none; font-size: 20px; color: var(--text-muted); cursor: pointer; }
  .mobile-toc-btn { display: flex; position: fixed; bottom: 80px; right: 24px; padding: 10px 16px; background: white; border: 1px solid var(--border); border-radius: 20px; font-size: 13px; color: var(--text-primary); cursor: pointer; z-index: 99; box-shadow: var(--shadow-md); }
  .chapter-reader { padding-bottom: 80px; }
}

.toc-header { display: none; }
.toc-close { display: none; }
.mobile-toc-btn { display: none; }

/* AI悬浮按钮 */
.ai-fab {
  position: fixed;
  bottom: 140px;
  right: 24px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #A855F7 100%);
  color: white;
  border: none;
  border-radius: 50%;
  box-shadow: 0 6px 24px rgba(99, 102, 241, 0.45), 0 0 0 4px rgba(139, 92, 246, 0.15);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: pulse-glow 2s ease-in-out infinite;
}
.ai-fab:hover { 
  transform: scale(1.12) translateY(-2px); 
  box-shadow: 0 10px 36px rgba(99, 102, 241, 0.55), 0 0 0 6px rgba(139, 92, 246, 0.2); 
}
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 6px 24px rgba(99, 102, 241, 0.45), 0 0 0 4px rgba(139, 92, 246, 0.15); }
  50% { box-shadow: 0 6px 28px rgba(99, 102, 241, 0.55), 0 0 0 8px rgba(139, 92, 246, 0.1); }
}

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
.current-qa { background: linear-gradient(135deg, #EEF2FF, #F5F3FF); border-radius: 12px; padding: 16px; }
.qa-question { font-size: 14px; font-weight: 600; color: var(--primary); margin-bottom: 12px; }
.qa-answer { font-size: 14px; color: var(--text-secondary); line-height: 1.6; }
.qa-actions { display: flex; gap: 8px; margin-top: 12px; }
.ai-panel-footer { padding: 16px; border-top: 1px solid var(--border); display: flex; gap: 8px; }
.ai-input { flex: 1; padding: 12px 16px; border: 1px solid var(--border); border-radius: 24px; font-size: 14px; }
.ai-input:focus { outline: none; border-color: var(--primary); }
.ai-send-btn { padding: 12px 20px; background: var(--primary); color: white; border: none; border-radius: 24px; font-size: 14px; font-weight: 500; cursor: pointer; }
.ai-send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* 底部操作栏 */
.article-bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 32px;
  padding: 12px 20px calc(12px + env(safe-area-inset-bottom));
  background: white;
  border-top: 1px solid var(--border);
  z-index: 99;
}
.bottom-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  position: relative;
  padding: 4px 12px;
  transition: color 0.2s;
}
.bottom-action:hover { color: var(--primary); }
.bottom-action .badge {
  position: absolute;
  top: -2px;
  right: 0;
  background: var(--primary);
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
}

/* 分享面板 */
.share-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-radius: 20px 20px 0 0;
  padding: 20px 20px calc(20px + env(safe-area-inset-bottom));
  z-index: 1001;
  animation: slideUp 0.3s ease;
}
.share-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.share-panel-header h3 { font-size: 16px; font-weight: 600; }
.panel-close { background: none; border: none; font-size: 20px; color: var(--text-muted); cursor: pointer; }
.share-options {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 20px;
}
.share-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 12px;
  border-radius: 12px;
  transition: background 0.2s;
}
.share-btn:hover { background: var(--bg-main); }
.share-btn span { font-size: 12px; color: var(--text-secondary); }
.share-btn.wechat svg { color: #07C160; }
.share-btn.qq svg { color: #12B7F5; }
.share-btn.wecom svg { color: #2B7BD6; }
.share-btn.dingtalk svg { color: #3296FA; }
.share-copy-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  background: var(--bg-main);
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 14px;
  cursor: pointer;
}
.share-copy-btn:hover { background: var(--primary-bg); border-color: var(--primary); color: var(--primary); }

/* 笔记面板 */
.notes-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-radius: 20px 20px 0 0;
  max-height: 70vh;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}
.notes-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border);
}
.notes-panel-header h3 { font-size: 16px; font-weight: 600; }
.notes-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px calc(16px + env(safe-area-inset-bottom));
}
.notes-empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
}
.notes-empty .empty-icon { font-size: 48px; margin-bottom: 12px; }
.notes-empty p { font-size: 15px; color: var(--text-secondary); margin-bottom: 4px; }
.notes-empty span { font-size: 13px; }
.note-card {
  background: var(--bg-main);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}
.note-card .note-q { font-size: 14px; color: var(--primary); font-weight: 500; margin-bottom: 8px; }
.note-card .note-a { font-size: 14px; color: var(--text-secondary); line-height: 1.6; }
.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.note-time { font-size: 12px; color: var(--text-muted); }
.note-delete-btn { background: none; border: none; color: var(--error); font-size: 12px; cursor: pointer; }

.panel-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); z-index: 1000; }

@media (max-width: 768px) {
  .ai-fab { bottom: 140px; right: 16px; width: 54px; height: 54px; }
  .ai-panel { width: 100%; height: 80vh; border-radius: 20px 20px 0 0; }
}
</style>
