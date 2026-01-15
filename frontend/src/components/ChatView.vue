<template>
  <div class="chat-container">
    <!-- 侧边栏 - 聊天记录 -->
    <aside :class="['chat-sidebar', { open: sidebarOpen }]">
      <div class="sidebar-header">
        <h3>💬 聊天记录</h3>
        <button class="btn-new" @click="newConversation">+ 新对话</button>
      </div>
      
      <div class="conversation-list">
        <div v-if="conversations.length === 0" class="empty-hint">暂无聊天记录</div>
        <div 
          v-for="conv in conversations" 
          :key="conv.id" 
          :class="['conversation-item', { active: currentConvId === conv.id, selected: selectedIds.includes(conv.id) }]"
          @click="loadConversation(conv.id)"
        >
          <input 
            type="checkbox" 
            :checked="selectedIds.includes(conv.id)" 
            @click.stop="toggleSelect(conv.id)"
            class="conv-checkbox"
          />
          <div class="conv-info">
            <p class="conv-title">{{ conv.title || '新对话' }}</p>
            <span class="conv-time">{{ formatTime(conv.updated_at) }}</span>
          </div>
          <button class="btn-delete-conv" @click.stop="deleteConv(conv.id)">×</button>
        </div>
      </div>
      
      <div v-if="selectedIds.length > 0" class="batch-actions">
        <button class="btn btn-danger btn-sm" @click="batchDelete">
          删除选中 ({{ selectedIds.length }})
        </button>
        <button class="btn btn-secondary btn-sm" @click="selectedIds = []">取消</button>
      </div>
    </aside>

    <!-- 主区域 -->
    <div class="chat-main-area">
      <!-- 头部 -->
      <header class="chat-header">
        <button class="btn-toggle-sidebar" @click="sidebarOpen = !sidebarOpen">☰</button>
        <button class="btn-back" @click="$emit('back')">← 返回平台</button>
        <div class="header-title">
          <span class="header-icon">💬</span>
          <h1>AI 对话</h1>
        </div>
        <button class="btn-new-chat" @click="newConversation">+ 新对话</button>
      </header>

      <!-- 对话区域 -->
      <main class="chat-main" ref="chatMain">
        <!-- 欢迎界面 -->
        <div v-if="messages.length === 0" class="welcome-section">
          <div class="welcome-icon">✨</div>
          <h2>你好，有什么可以帮你的？</h2>
          <p>我是你的AI助手，可以回答问题、提供建议、帮助创作，还可以生成图片</p>
          <div class="suggestion-chips">
            <button v-for="s in suggestions" :key="s" class="chip" @click="sendSuggestion(s)">{{ s }}</button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-else class="messages-list">
          <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
            <div class="message-avatar">
              <span v-if="msg.role === 'user'">👤</span>
              <span v-else>🤖</span>
            </div>
            <div class="message-content">
              <div v-if="msg.role === 'assistant'" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
              <div v-else>{{ msg.content }}</div>
              <!-- 图片显示 -->
              <img v-if="msg.image" :src="msg.image" class="chat-image" @click="previewImage(msg.image)" />
            </div>
          </div>
          <!-- 加载中 -->
          <div v-if="loading" class="message assistant">
            <div class="message-avatar"><span>🤖</span></div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
          <!-- 图片生成中 -->
          <div v-if="generatingImage" class="message assistant">
            <div class="message-avatar"><span>🤖</span></div>
            <div class="message-content">
              <div class="image-generating">🎨 正在生成图片...</div>
            </div>
          </div>
        </div>
      </main>

      <!-- 输入区域 -->
      <footer class="chat-footer">
        <div class="input-wrapper">
          <textarea 
            v-model="inputText" 
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="输入消息... (输入 生成图片:描述 可生成图片)"
            rows="1"
            ref="inputRef"
          ></textarea>
          <button class="btn-send" @click="sendMessage" :disabled="!inputText.trim() || loading">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
        <p class="footer-hint">按 Enter 发送 | 输入 生成图片:描述 可生成图片</p>
      </footer>
    </div>

    <!-- 图片预览 -->
    <div v-if="previewUrl" class="image-preview-modal" @click="previewUrl = ''">
      <img :src="previewUrl" />
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import axios from 'axios'

const emit = defineEmits(['back'])

const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const generatingImage = ref(false)
const chatMain = ref(null)
const inputRef = ref(null)
const sidebarOpen = ref(false)

// 聊天记录
const conversations = ref([])
const currentConvId = ref('')
const selectedIds = ref([])
const previewUrl = ref('')

const suggestions = [
  '解释一下量子计算',
  '写一首关于春天的诗',
  '生成图片:一只可爱的猫咪',
  '如何学习编程？'
]

marked.setOptions({
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true
})

function renderMarkdown(text) {
  return marked.parse(text || '')
}

function scrollToBottom() {
  nextTick(() => {
    if (chatMain.value) {
      chatMain.value.scrollTop = chatMain.value.scrollHeight
    }
  })
}

function formatTime(time) {
  if (!time) return ''
  const d = new Date(time)
  const now = new Date()
  if (d.toDateString() === now.toDateString()) {
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

function previewImage(url) {
  previewUrl.value = url
}

// 聊天记录操作
async function loadConversations() {
  try {
    const res = await axios.get('/api/conversations')
    conversations.value = res.data.conversations || []
  } catch (e) {
    console.error(e)
  }
}

async function newConversation() {
  try {
    const res = await axios.post('/api/conversations')
    currentConvId.value = res.data.conversation_id
    messages.value = []
    await loadConversations()
    sidebarOpen.value = false
  } catch (e) {
    console.error(e)
  }
}

async function loadConversation(convId) {
  try {
    const res = await axios.get(`/api/conversations/${convId}`)
    currentConvId.value = convId
    messages.value = res.data.conversation?.messages || []
    sidebarOpen.value = false
    scrollToBottom()
  } catch (e) {
    console.error(e)
  }
}

async function saveConversation() {
  if (!currentConvId.value) {
    await newConversation()
  }
  const title = messages.value.find(m => m.role === 'user')?.content?.slice(0, 30) || '新对话'
  try {
    await axios.put(`/api/conversations/${currentConvId.value}`, {
      messages: messages.value,
      title
    })
    await loadConversations()
  } catch (e) {
    console.error(e)
  }
}

async function deleteConv(convId) {
  if (!confirm('确定删除这个对话吗？')) return
  try {
    await axios.delete(`/api/conversations/${convId}`)
    if (currentConvId.value === convId) {
      currentConvId.value = ''
      messages.value = []
    }
    await loadConversations()
  } catch (e) {
    console.error(e)
  }
}

function toggleSelect(convId) {
  const idx = selectedIds.value.indexOf(convId)
  if (idx > -1) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(convId)
  }
}

async function batchDelete() {
  if (!confirm(`确定删除选中的 ${selectedIds.value.length} 个对话吗？`)) return
  try {
    await axios.post('/api/conversations/batch-delete', { ids: selectedIds.value })
    if (selectedIds.value.includes(currentConvId.value)) {
      currentConvId.value = ''
      messages.value = []
    }
    selectedIds.value = []
    await loadConversations()
  } catch (e) {
    console.error(e)
  }
}

function sendSuggestion(text) {
  inputText.value = text
  sendMessage()
}

// 检查是否是图片生成请求
function isImageRequest(text) {
  const patterns = [
    /^生成图片[:：]\s*(.+)/i,
    /^画一[张个幅][:：]?\s*(.+)/i,
    /^画[:：]\s*(.+)/i,
    /^generate image[:：]?\s*(.+)/i
  ]
  for (const p of patterns) {
    const match = text.match(p)
    if (match) return match[1].trim()
  }
  return null
}

async function generateImage(prompt) {
  generatingImage.value = true
  scrollToBottom()
  
  try {
    const res = await axios.post('/api/chat/image', { prompt })
    if (res.data.success && res.data.url) {
      messages.value.push({
        role: 'assistant',
        content: `已为你生成图片：`,
        image: res.data.url
      })
    } else {
      messages.value.push({
        role: 'assistant',
        content: `图片生成失败：${res.data.error || '未知错误'}。当前API可能不支持图片生成功能。`
      })
    }
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: `图片生成失败：${e.message}`
    })
  }
  
  generatingImage.value = false
  await saveConversation()
  scrollToBottom()
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  // 检查是否是图片生成请求
  const imagePrompt = isImageRequest(text)
  if (imagePrompt) {
    messages.value.push({ role: 'user', content: text })
    inputText.value = ''
    await generateImage(imagePrompt)
    return
  }

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        message: text,
        history: messages.value.slice(-10)
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    messages.value.push({ role: 'assistant', content: '' })
    const assistantIdx = messages.value.length - 1
    loading.value = false

    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') break
          try {
            const parsed = JSON.parse(data)
            if (parsed.content) {
              messages.value[assistantIdx].content += parsed.content
              scrollToBottom()
            }
            if (parsed.error) {
              messages.value[assistantIdx].content = `错误: ${parsed.error}`
            }
          } catch {}
        }
      }
    }

    // 检查AI回复是否包含图片生成指令
    const aiContent = messages.value[assistantIdx].content
    const imgMatch = aiContent.match(/\[生成图片[:：]\s*([^\]]+)\]/i)
    if (imgMatch) {
      messages.value[assistantIdx].content = aiContent.replace(/\[生成图片[:：][^\]]+\]/i, '').trim()
      await generateImage(imgMatch[1])
    }

    await saveConversation()
  } catch (e) {
    loading.value = false
    messages.value.push({ role: 'assistant', content: `请求失败: ${e.message}` })
  }
  
  scrollToBottom()
}

onMounted(async () => {
  inputRef.value?.focus()
  await loadConversations()
})
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
}

/* 侧边栏 */
.chat-sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  font-size: 1rem;
  font-weight: 600;
}

.btn-new {
  background: var(--primary);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.empty-hint {
  text-align: center;
  color: var(--text-muted);
  padding: 24px;
  font-size: 14px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.conversation-item:hover {
  background: var(--bg-main);
}

.conversation-item.active {
  background: var(--primary-bg);
  border: 1px solid var(--primary-light);
}

.conversation-item.selected {
  background: #FEF3C7;
}

.conv-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-time {
  font-size: 11px;
  color: var(--text-muted);
}

.btn-delete-conv {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 18px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .btn-delete-conv {
  opacity: 1;
}

.btn-delete-conv:hover {
  color: var(--error);
}

.batch-actions {
  padding: 12px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 8px;
}

/* 主区域 */
.chat-main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.btn-toggle-sidebar {
  display: none;
  background: none;
  border: 1px solid var(--border);
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
}

.btn-back {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-back:hover {
  background: var(--bg-main);
  color: var(--primary);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.header-icon { font-size: 1.5rem; }

.header-title h1 {
  font-size: 1.1rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.btn-new-chat {
  background: var(--primary-bg);
  border: 1px solid var(--primary-light);
  color: var(--primary);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-new-chat:hover {
  background: var(--primary);
  color: white;
}

.chat-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px;
}

.welcome-icon { font-size: 4rem; margin-bottom: 24px; }

.welcome-section h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.welcome-section p {
  color: var(--text-secondary);
  font-size: 1rem;
  margin-bottom: 32px;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.chip {
  background: white;
  border: 1px solid var(--border);
  padding: 12px 20px;
  border-radius: 24px;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.chip:hover {
  border-color: var(--primary);
  background: var(--primary-bg);
  color: var(--primary);
  transform: translateY(-2px);
}

.messages-list {
  max-width: 800px;
  margin: 0 auto;
}

.message {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.message.user { flex-direction: row-reverse; }

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: linear-gradient(135deg, var(--primary), var(--accent));
}

.message.assistant .message-avatar {
  background: white;
  border: 1px solid var(--border);
}

.message-content {
  max-width: 70%;
  padding: 16px 20px;
  border-radius: 16px;
  line-height: 1.6;
}

.message.user .message-content {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
  border-radius: 16px 16px 4px 16px;
}

.message.assistant .message-content {
  background: white;
  border: 1px solid var(--border);
  border-radius: 16px 16px 16px 4px;
}

.chat-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 12px;
  margin-top: 12px;
  cursor: pointer;
  transition: transform 0.2s;
}

.chat-image:hover {
  transform: scale(1.02);
}

.image-generating {
  color: var(--primary);
  font-size: 14px;
  padding: 8px 0;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-8px); opacity: 1; }
}

.chat-footer {
  padding: 16px 24px 24px;
  background: white;
  border-top: 1px solid var(--border);
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 12px;
  background: var(--bg-main);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 8px 8px 8px 20px;
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-bg);
}

.input-wrapper textarea {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  line-height: 1.5;
  resize: none;
  outline: none;
  max-height: 120px;
  padding: 8px 0;
}

.btn-send {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-send:hover:not(:disabled) { transform: scale(1.05); }
.btn-send:disabled { opacity: 0.5; cursor: not-allowed; }

.footer-hint {
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
}

/* 图片预览 */
.image-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: pointer;
}

.image-preview-modal img {
  max-width: 90%;
  max-height: 90%;
  border-radius: 8px;
}

/* Markdown样式 */
.markdown-body :deep(pre) {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 12px 0;
}

.markdown-body :deep(code) {
  font-family: 'Fira Code', monospace;
  font-size: 13px;
}

.markdown-body :deep(p) { margin: 8px 0; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { padding-left: 20px; margin: 8px 0; }
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) { margin: 16px 0 8px; font-weight: 600; }

@media (max-width: 768px) {
  .chat-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  
  .chat-sidebar.open {
    transform: translateX(0);
  }
  
  .btn-toggle-sidebar {
    display: block;
  }
  
  .chat-header { padding: 12px 16px; }
  .header-title h1 { font-size: 1rem; }
  .btn-new-chat { display: none; }
  
  .chat-main { padding: 16px; }
  .welcome-section { padding: 24px; }
  .welcome-icon { font-size: 3rem; }
  .welcome-section h2 { font-size: 1.25rem; }
  
  .message-content { max-width: 85%; padding: 12px 16px; }
  .message-avatar { width: 32px; height: 32px; font-size: 1rem; }
  
  .chat-footer { padding: 12px 16px 20px; }
  .input-wrapper { padding: 6px 6px 6px 16px; }
  .btn-send { width: 40px; height: 40px; }
}
</style>
