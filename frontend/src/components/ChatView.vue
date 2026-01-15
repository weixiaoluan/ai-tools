<template>
  <div class="chat-container">
    <!-- 头部 -->
    <header class="chat-header">
      <button class="btn-back" @click="$emit('back')">← 返回平台</button>
      <div class="header-title">
        <span class="header-icon">💬</span>
        <h1>AI 对话</h1>
      </div>
      <button class="btn-new-chat" @click="clearChat">+ 新对话</button>
    </header>

    <!-- 对话区域 -->
    <main class="chat-main" ref="chatMain">
      <!-- 欢迎界面 -->
      <div v-if="messages.length === 0" class="welcome-section">
        <div class="welcome-icon">✨</div>
        <h2>你好，有什么可以帮你的？</h2>
        <p>我是你的AI助手，可以回答问题、提供建议、帮助创作等</p>
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
      </div>
    </main>

    <!-- 输入区域 -->
    <footer class="chat-footer">
      <div class="input-wrapper">
        <textarea 
          v-model="inputText" 
          @keydown.enter.exact.prevent="sendMessage"
          placeholder="输入消息..."
          rows="1"
          ref="inputRef"
        ></textarea>
        <button class="btn-send" @click="sendMessage" :disabled="!inputText.trim() || loading">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
      <p class="footer-hint">按 Enter 发送，Shift + Enter 换行</p>
    </footer>
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
const chatMain = ref(null)
const inputRef = ref(null)

const suggestions = [
  '解释一下量子计算',
  '写一首关于春天的诗',
  '如何学习编程？',
  '推荐几本好书'
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

function clearChat() {
  messages.value = []
  inputText.value = ''
}

function sendSuggestion(text) {
  inputText.value = text
  sendMessage()
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

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

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    messages.value.push({ role: 'assistant', content: '' })
    const assistantIdx = messages.value.length - 1
    loading.value = false

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

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
  } catch (e) {
    loading.value = false
    messages.value.push({ role: 'assistant', content: `请求失败: ${e.message}` })
  }
  
  scrollToBottom()
}

onMounted(() => {
  inputRef.value?.focus()
})
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
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

.welcome-icon {
  font-size: 4rem;
  margin-bottom: 24px;
}

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

.message.user {
  flex-direction: row-reverse;
}

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

.btn-send:hover:not(:disabled) {
  transform: scale(1.05);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.footer-hint {
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
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

.markdown-body :deep(p) {
  margin: 8px 0;
}

.markdown-body :deep(ul), .markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}

.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) {
  margin: 16px 0 8px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .chat-header { padding: 12px 16px; }
  .header-title h1 { font-size: 1rem; }
  .btn-new-chat { padding: 6px 12px; font-size: 12px; }
  
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
