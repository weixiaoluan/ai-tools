<template>
  <div class="chat-view">
    <div class="chat-container">
      <!-- 对话头部 -->
      <div class="chat-header">
        <div class="header-left">
          <button class="btn-back" @click="$emit('back')">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
          </button>
          <div class="chat-title">
            <div class="title-icon">💬</div>
            <div>
              <h2>AI 对话助手</h2>
              <p>智能对话，解答您的疑问</p>
            </div>
          </div>
        </div>
        <button class="btn-new-chat" @click="startNewChat">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          新对话
        </button>
      </div>

      <!-- 消息区域 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-screen">
          <div class="welcome-icon">🤖</div>
          <h3>欢迎使用 AI 对话助手</h3>
          <p>我可以帮您解答问题、提供建议、协助创作等</p>
          <div class="suggestion-cards">
            <div v-for="suggestion in suggestions" :key="suggestion.text" class="suggestion-card" @click="sendMessage(suggestion.text)">
              <span class="suggestion-icon">{{ suggestion.icon }}</span>
              <span>{{ suggestion.text }}</span>
            </div>
          </div>
        </div>

        <div v-else class="messages-list">
          <div v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
            <div class="message-avatar">
              <span v-if="message.role === 'user'">{{ user?.username?.charAt(0).toUpperCase() || 'U' }}</span>
              <span v-else>🤖</span>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              <div class="message-actions" v-if="message.role === 'assistant'">
                <button class="action-btn" @click="copyMessage(message.content)" title="复制">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                  </svg>
                </button>
                <button class="action-btn" @click="regenerateResponse(index)" title="重新生成">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                    <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="isTyping" class="message assistant typing">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <div class="input-wrapper">
          <textarea
            ref="messageInput"
            v-model="inputMessage"
            class="message-input"
            placeholder="输入您的问题..."
            rows="1"
            @keydown="handleKeyDown"
            @input="autoResize"
          ></textarea>
          <button
            class="btn-send"
            @click="sendMessage()"
            :disabled="!inputMessage.trim() || isTyping"
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
        <p class="input-hint">按 Enter 发送，Shift + Enter 换行</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import axios from 'axios'

defineProps({ user: Object })
const emit = defineEmits(['back'])

const messages = ref([])
const inputMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref(null)
const messageInput = ref(null)

const suggestions = [
  { icon: '💡', text: '如何学习Python编程？' },
  { icon: '📚', text: '解释机器学习的基本概念' },
  { icon: '✍️', text: '帮我写一段产品介绍文案' },
  { icon: '🔍', text: '分析当前AI技术的发展趋势' }
]

function autoResize() {
  const textarea = messageInput.value
  textarea.style.height = 'auto'
  textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px'
}

function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

async function sendMessage(text = null) {
  const message = text || inputMessage.value.trim()
  if (!message || isTyping.value) return

  // 添加用户消息
  messages.value.push({ role: 'user', content: message })
  inputMessage.value = ''
  autoResize()
  
  await scrollToBottom()
  
  isTyping.value = true
  
  try {
    const res = await axios.post('/api/chat', {
      message: message,
      history: messages.value.slice(0, -1).map(m => ({
        role: m.role,
        content: m.content
      }))
    })
    
    if (res.data.reply) {
      messages.value.push({ role: 'assistant', content: res.data.reply })
    }
  } catch (e) {
    messages.value.push({ 
      role: 'assistant', 
      content: '抱歉，我遇到了一些问题。请稍后再试。' 
    })
  }
  
  isTyping.value = false
  await scrollToBottom()
}

async function regenerateResponse(index) {
  if (isTyping.value) return
  
  const userMessage = messages.value[index - 1]?.content
  if (!userMessage) return
  
  // 删除原来的回复
  messages.value = messages.value.slice(0, index)
  
  // 重新发送
  inputMessage.value = userMessage
  await sendMessage()
  inputMessage.value = ''
}

function copyMessage(text) {
  navigator.clipboard.writeText(text)
  alert('已复制到剪贴板')
}

function startNewChat() {
  messages.value = []
  inputMessage.value = ''
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function formatMessage(content) {
  // 简单的Markdown格式化
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

onMounted(() => {
  messageInput.value?.focus()
})
</script>

<style scoped>
.chat-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #F0F0F0;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 900px;
  margin: 0 auto;
  background: white;
}

/* 头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #E0E0E0;
  background: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back {
  width: 40px;
  height: 40px;
  background: none;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #5F6368;
  transition: background 0.2s;
}

.btn-back:hover {
  background: #F1F3F4;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 28px;
}

.chat-title h2 {
  font-size: 16px;
  font-weight: 500;
  color: #202124;
  margin: 0;
}

.chat-title p {
  font-size: 12px;
  color: #5F6368;
  margin: 0;
}

.btn-new-chat {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #F1F3F4;
  border: none;
  border-radius: 20px;
  color: #5F6368;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-new-chat:hover {
  background: #E8EAED;
}

/* 消息区域 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px;
  scroll-behavior: smooth;
}

.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  max-width: 500px;
  margin: 0 auto;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.welcome-screen h3 {
  font-size: 24px;
  font-weight: 500;
  color: #202124;
  margin-bottom: 8px;
}

.welcome-screen p {
  font-size: 14px;
  color: #5F6368;
  margin-bottom: 32px;
}

.suggestion-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  width: 100%;
}

.suggestion-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  background: #F1F3F4;
  border: 1px solid #E8EAED;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.suggestion-card:hover {
  background: #E8EAED;
  border-color: #DADCE0;
}

.suggestion-icon {
  font-size: 20px;
}

.suggestion-card span:last-child {
  font-size: 13px;
  color: #202124;
  line-height: 1.4;
}

/* 消息列表 */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message {
  display: flex;
  gap: 16px;
  padding: 20px;
}

.message.user {
  background: #F1F3F4;
  border-radius: 12px;
  flex-direction: row-reverse;
}

.message.assistant {
  background: white;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: linear-gradient(135deg, #4285F4, #34A853);
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.message.assistant .message-avatar {
  background: #F1F3F4;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  font-size: 15px;
  line-height: 1.6;
  color: #202124;
}

.message.user .message-text {
  color: #202124;
}

.message-text code {
  background: #F1F3F4;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
}

.message-text strong {
  font-weight: 600;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message:hover .message-actions {
  opacity: 1;
}

.action-btn {
  width: 32px;
  height: 32px;
  background: #F1F3F4;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #5F6368;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #E8EAED;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #9AA0A6;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 输入区域 */
.input-container {
  padding: 16px 20px 24px;
  border-top: 1px solid #E0E0E0;
  background: white;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px 16px;
  background: #F1F3F4;
  border-radius: 24px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  background: white;
  border-color: #DADCE0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.message-input {
  flex: 1;
  background: transparent;
  border: none;
  font-size: 16px;
  font-family: inherit;
  line-height: 1.5;
  resize: none;
  max-height: 150px;
  color: #202124;
}

.message-input:focus {
  outline: none;
}

.message-input::placeholder {
  color: #9AA0A6;
}

.btn-send {
  width: 40px;
  height: 40px;
  background: #1A73E8;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: background 0.2s;
  flex-shrink: 0;
}

.btn-send:hover:not(:disabled) {
  background: #1557B0;
}

.btn-send:disabled {
  background: #DADCE0;
  cursor: not-allowed;
}

.input-hint {
  font-size: 12px;
  color: #9AA0A6;
  text-align: center;
  margin-top: 8px;
}

/* 滚动条 */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #DADCE0;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #BDC1C6;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .chat-container {
    height: 100vh;
    max-width: 100%;
  }
  
  .chat-header {
    padding: 12px 16px;
  }
  
  .chat-title h2 {
    font-size: 14px;
  }
  
  .chat-title p {
    font-size: 11px;
  }
  
  .btn-new-chat {
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .messages-container {
    padding: 16px 12px;
  }
  
  .welcome-screen {
    padding: 40px 16px;
  }
  
  .welcome-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .welcome-screen h3 {
    font-size: 20px;
  }
  
  .welcome-screen p {
    font-size: 13px;
    margin-bottom: 24px;
  }
  
  .suggestion-cards {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .suggestion-card {
    padding: 12px;
  }
  
  .message {
    padding: 16px 12px;
    gap: 12px;
  }
  
  .message-avatar {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .message-text {
    font-size: 14px;
  }
  
  .input-container {
    padding: 12px 16px 20px;
  }
  
  .input-wrapper {
    padding: 10px 14px;
  }
  
  .message-input {
    font-size: 15px;
  }
  
  .btn-send {
    width: 36px;
    height: 36px;
  }
}
</style>