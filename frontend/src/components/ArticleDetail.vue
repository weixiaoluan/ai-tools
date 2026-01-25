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
        
        <!-- 文章末尾操作栏 -->
        <div class="article-footer-actions">
          <button class="footer-action-btn interview-btn" @click="showInterviewPanel = true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
            </svg>
            <span>面试题</span>
            <span v-if="interviewQuestions.length > 0" class="action-badge">{{ interviewQuestions.length }}</span>
          </button>
          <button class="footer-action-btn" @click="showNotesPanel = true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
            </svg>
            <span>笔记</span>
            <span v-if="notes.length > 0" class="action-badge">{{ notes.length }}</span>
          </button>
          <button class="footer-action-btn" @click="showSharePanel = true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/>
            </svg>
            <span>分享</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- AI问答悬浮按钮 -->
    <button class="ai-fab" @click="showAiPanel = true" title="AI问答助手">
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
    <div v-if="showAiPanel || tocOpen || showSharePanel || showNotesPanel || showInterviewPanel" class="panel-overlay" @click="closeAllPanels"></div>
    
    <!-- 面试题面板 -->
    <div v-if="showInterviewPanel" class="interview-panel">
      <div class="interview-panel-header">
        <h3>📝 面试题练习</h3>
        <button class="panel-close" @click="showInterviewPanel = false">✕</button>
      </div>
      <div class="interview-panel-body">
        <!-- 生成按钮 -->
        <div class="interview-generate-section">
          <button class="btn btn-primary" @click="generateInterviewQuestions" :disabled="generatingQuestions">
            {{ generatingQuestions ? '生成中...' : '🤖 AI生成面试题' }}
          </button>
          <span class="generate-hint">根据文章内容自动生成求职面试题</span>
        </div>
        
        <!-- 题目列表 -->
        <div v-if="interviewQuestions.length === 0 && !generatingQuestions" class="interview-empty">
          <div class="empty-icon">❓</div>
          <p>暂无面试题</p>
          <span>点击上方按钮生成面试题</span>
        </div>
        
        <div v-for="(q, idx) in interviewQuestions" :key="q.id" class="interview-card">
          <div class="interview-card-header">
            <span class="question-num">第 {{ idx + 1 }} 题</span>
            <div class="question-actions">
              <button class="action-icon-btn" @click="regenerateQuestion(q.id)" :disabled="q.regenerating" title="重新生成">
                🔄
              </button>
              <button class="action-icon-btn" @click="deleteQuestion(q.id)" title="删除">
                🗑️
              </button>
            </div>
          </div>
          <div class="question-text">{{ q.question }}</div>
          
          <!-- 未作答状态 -->
          <div v-if="!q.user_answer && !q.answering" class="answer-section">
            <textarea v-model="q.draft_answer" class="answer-input" placeholder="请输入你的答案..." rows="4"></textarea>
            <button class="btn btn-primary btn-sm" @click="submitAnswer(q)" :disabled="!q.draft_answer?.trim()">
              提交答案
            </button>
          </div>
          
          <!-- 作答中 -->
          <div v-if="q.answering" class="answering-status">
            <span class="loading-spinner"></span> AI评估中...
          </div>
          
          <!-- 已作答，显示评分 -->
          <div v-if="q.user_answer && q.score !== null" class="result-section">
            <div class="score-display" :class="getScoreClass(q.score)">
              <span class="score-num">{{ q.score }}</span>
              <span class="score-label">分</span>
            </div>
            <div class="user-answer-box">
              <div class="answer-label">我的答案：</div>
              <div class="answer-content">{{ q.user_answer }}</div>
            </div>
            <div class="feedback-box">
              <div class="feedback-label">AI点评：</div>
              <div class="feedback-content" v-html="renderAnswer(q.feedback)"></div>
            </div>
            <button class="btn btn-secondary btn-sm" @click="retryQuestion(q)">重新作答</button>
          </div>
        </div>
      </div>
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
          <div class="note-a" v-html="renderAnswer(note.answer)"></div>
          <div class="note-footer">
            <span class="note-time">{{ formatDate(note.created_at) }}</span>
            <button class="note-delete-btn" @click="deleteNote(note.id)">删除</button>
          </div>
        </div>
      </div>
    </div>
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

// 分享和笔记面板
const showSharePanel = ref(false)
const showNotesPanel = ref(false)

// 面试题
const showInterviewPanel = ref(false)
const interviewQuestions = ref([])
const generatingQuestions = ref(false)

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
  
  // 移除包裹整个内容的markdown代码块（如果存在）
  content = content.replace(/^```(?:markdown|md)?\s*\n([\s\S]*?)\n```\s*$/i, '$1')
  
  // 移除目录部分
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

// 分享功能
function getShareUrl() {
  return `${window.location.origin}/article/${props.article?.id}`
}

function shareToWechat() {
  // 微信需要通过二维码分享，这里复制链接提示用户
  copyShareLink()
  alert('链接已复制，请在微信中粘贴分享')
}

function shareToQQ() {
  const url = encodeURIComponent(getShareUrl())
  const title = encodeURIComponent(props.article?.title || '学习文章')
  window.open(`https://connect.qq.com/widget/shareqq/index.html?url=${url}&title=${title}`, '_blank')
}

function shareToWecom() {
  copyShareLink()
  alert('链接已复制，请在企业微信中粘贴分享')
}

function shareToDingtalk() {
  const url = encodeURIComponent(getShareUrl())
  const title = encodeURIComponent(props.article?.title || '学习文章')
  window.open(`https://page.dingtalk.com/wow/dingtalk/act/shareurl?url=${url}&title=${title}`, '_blank')
}

function copyShareLink() {
  const url = getShareUrl()
  navigator.clipboard.writeText(url).then(() => {
    alert('链接已复制到剪贴板')
  }).catch(() => {
    // 降级方案
    const input = document.createElement('input')
    input.value = url
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    alert('链接已复制到剪贴板')
  })
}

// 面试题功能
function closeAllPanels() {
  showAiPanel.value = false
  tocOpen.value = false
  showSharePanel.value = false
  showNotesPanel.value = false
  showInterviewPanel.value = false
}

async function loadInterviewQuestions() {
  if (!props.article?.id) return
  try {
    const res = await axios.get(`/api/interview/${props.article.id}`)
    interviewQuestions.value = (res.data.questions || []).map(q => ({
      ...q,
      draft_answer: '',
      answering: false,
      regenerating: false
    }))
  } catch (e) { console.error(e) }
}

async function generateInterviewQuestions() {
  if (generatingQuestions.value) return
  generatingQuestions.value = true
  try {
    await axios.post('/api/interview/generate', { article_id: props.article.id, count: 5 })
    await loadInterviewQuestions()
  } catch (e) {
    alert('生成面试题失败：' + (e.response?.data?.detail || e.message))
  }
  generatingQuestions.value = false
}

async function submitAnswer(q) {
  if (!q.draft_answer?.trim() || q.answering) return
  q.answering = true
  try {
    const res = await axios.post('/api/interview/answer', {
      question_id: q.id,
      answer: q.draft_answer
    })
    q.user_answer = q.draft_answer
    q.score = res.data.score
    q.feedback = res.data.feedback
  } catch (e) {
    alert('提交失败：' + (e.response?.data?.detail || e.message))
  }
  q.answering = false
}

async function regenerateQuestion(questionId) {
  const q = interviewQuestions.value.find(x => x.id === questionId)
  if (!q || q.regenerating) return
  q.regenerating = true
  try {
    const res = await axios.post(`/api/interview/regenerate/${questionId}`)
    const idx = interviewQuestions.value.findIndex(x => x.id === questionId)
    if (idx >= 0) {
      interviewQuestions.value[idx] = {
        id: res.data.new_id,
        question: res.data.question,
        reference_answer: res.data.reference_answer,
        user_answer: null,
        score: null,
        feedback: null,
        draft_answer: '',
        answering: false,
        regenerating: false
      }
    }
  } catch (e) {
    alert('重新生成失败：' + (e.response?.data?.detail || e.message))
  }
  q.regenerating = false
}

async function deleteQuestion(questionId) {
  if (!confirm('确定删除这道面试题吗？')) return
  try {
    await axios.delete(`/api/interview/${questionId}`)
    interviewQuestions.value = interviewQuestions.value.filter(q => q.id !== questionId)
  } catch (e) {
    alert('删除失败：' + (e.response?.data?.detail || e.message))
  }
}

function retryQuestion(q) {
  q.user_answer = null
  q.score = null
  q.feedback = null
  q.draft_answer = ''
}

function getScoreClass(score) {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

watch(() => props.article, () => { extractToc(); loadNotes(); loadInterviewQuestions() }, { immediate: true })
onMounted(() => { extractToc(); loadNotes(); loadInterviewQuestions() })
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
.ai-fab:active { transform: scale(1.05); }
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

/* 文章末尾操作栏 */
.article-footer-actions {
  display: flex;
  gap: 12px;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}
.footer-action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-main);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}
.footer-action-btn:hover {
  background: var(--primary-bg);
  border-color: var(--primary);
  color: var(--primary);
}
.footer-action-btn svg { opacity: 0.7; }
.footer-action-btn:hover svg { opacity: 1; }
.action-badge {
  background: var(--primary);
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
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
.share-panel-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }
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
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
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
.notes-panel-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }
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

/* 面试题面板 */
.interview-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  z-index: 1002;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.25s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translate(-50%, -48%); } to { opacity: 1; transform: translate(-50%, -50%); } }

.interview-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(135deg, #FEF3C7, #FDE68A);
  border-radius: 16px 16px 0 0;
}
.interview-panel-header h3 { font-size: 18px; font-weight: 600; color: #92400E; }

.interview-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.interview-generate-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px dashed var(--border);
}
.generate-hint { font-size: 13px; color: var(--text-muted); }

.interview-empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}
.interview-empty .empty-icon { font-size: 56px; margin-bottom: 16px; }
.interview-empty p { font-size: 16px; color: var(--text-secondary); margin-bottom: 8px; }

.interview-card {
  background: var(--bg-main);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid var(--border);
}
.interview-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.question-num {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  background: var(--primary-bg);
  padding: 4px 10px;
  border-radius: 12px;
}
.question-actions { display: flex; gap: 8px; }
.action-icon-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}
.action-icon-btn:hover { opacity: 1; }
.action-icon-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.question-text {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.6;
  margin-bottom: 16px;
}

.answer-section { margin-top: 12px; }
.answer-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 12px;
  font-family: inherit;
}
.answer-input:focus { outline: none; border-color: var(--primary); }

.answering-status {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  background: #FEF3C7;
  border-radius: 8px;
  color: #92400E;
  font-size: 14px;
}
.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #FCD34D;
  border-top-color: #F59E0B;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.result-section { margin-top: 12px; }
.score-display {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  padding: 8px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}
.score-num { font-size: 28px; font-weight: 700; }
.score-label { font-size: 14px; }
.score-high { background: #D1FAE5; color: #065F46; }
.score-medium { background: #FEF3C7; color: #92400E; }
.score-low { background: #FEE2E2; color: #991B1B; }

.user-answer-box, .feedback-box {
  background: white;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 12px;
}
.answer-label, .feedback-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.answer-content { font-size: 14px; color: var(--text-secondary); line-height: 1.6; }
.feedback-content { font-size: 14px; color: var(--text-primary); line-height: 1.7; }

.interview-btn { background: linear-gradient(135deg, #FEF3C7, #FDE68A) !important; border-color: #FCD34D !important; color: #92400E !important; }
.interview-btn:hover { background: linear-gradient(135deg, #FDE68A, #FCD34D) !important; }

/* 移动端适配 */
@media (max-width: 768px) {
  .article-detail-view { padding: 0 12px; }
  .article-title { font-size: 1.3rem; line-height: 1.5; }
  .article-meta { font-size: 13px; gap: 10px; padding-bottom: 16px; margin-bottom: 16px; }
  .document-toc { position: fixed; left: 0; top: 0; bottom: 0; width: 280px; z-index: 1001; transform: translateX(-100%); transition: transform 0.3s; background: white; }
  .document-toc.toc-open { transform: translateX(0); }
  .toc-header { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-bottom: 1px solid var(--border); }
  .toc-close { display: block; background: none; border: none; font-size: 20px; color: var(--text-muted); cursor: pointer; }
  .mobile-toc-btn { display: flex; position: fixed; bottom: 100px; right: 16px; padding: 10px 16px; background: white; border: 1px solid var(--border); border-radius: 20px; font-size: 13px; color: var(--text-primary); cursor: pointer; z-index: 99; box-shadow: var(--shadow-md); }
  .interview-panel { width: 95%; max-height: 90vh; }
  .interview-panel-body { padding: 16px; }
  .interview-generate-section { flex-direction: column; align-items: flex-start; gap: 10px; }
  .interview-card { padding: 16px; }
  .score-num { font-size: 24px; }
  .ai-fab { bottom: 32px; right: 16px; width: 54px; height: 54px; }
  .ai-panel { width: 100%; height: 80vh; border-radius: 20px 20px 0 0; }
  .article-content { padding: 16px; }
  .article-footer-actions { flex-wrap: wrap; margin-top: 24px; padding-top: 16px; }
  .footer-action-btn { padding: 8px 16px; font-size: 13px; }
}

@media (max-width: 480px) {
  .article-detail-view { padding: 0 8px; }
  .article-title { font-size: 1.15rem; }
  .article-meta { font-size: 12px; flex-direction: column; align-items: flex-start; gap: 8px; }
  .article-content { padding: 12px; }
  .ai-fab { width: 48px; height: 48px; bottom: 24px; right: 12px; }
  .ai-fab svg { width: 22px; height: 22px; }
  .mobile-toc-btn { bottom: 90px; right: 12px; padding: 8px 12px; font-size: 12px; }
  .share-options { gap: 16px; flex-wrap: wrap; }
  .share-btn { padding: 8px; }
  .share-btn svg { width: 28px; height: 28px; }
}
</style>
