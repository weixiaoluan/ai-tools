<template>
  <div class="ds-chat-container">
    <!-- 侧边栏 -->
    <aside :class="['ds-sidebar', { collapsed: !sidebarOpen }]">
      <div class="ds-sidebar-header">
        <button class="ds-new-chat-btn" @click="newConversation">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>新对话</span>
        </button>
      </div>
      
      <div class="ds-conv-list">
        <div v-if="conversations.length === 0" class="ds-empty">
          <span>暂无对话记录</span>
        </div>
        <div 
          v-for="conv in conversations" 
          :key="conv.id" 
          :class="['ds-conv-item', { active: currentConvId === conv.id }]"
          @click="loadConversation(conv.id)"
        >
          <svg class="ds-conv-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <span class="ds-conv-title">{{ conv.title || '新对话' }}</span>
          <button class="ds-conv-delete" @click.stop="deleteConv(conv.id)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
      </div>

      <div class="ds-sidebar-footer">
        <button class="ds-back-btn" @click="$emit('back')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          <span>返回平台</span>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="ds-main">
      <!-- 顶部栏 -->
      <header class="ds-header">
        <button class="ds-menu-btn" @click="sidebarOpen = !sidebarOpen">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        <div class="ds-model-selector">
          <span class="ds-model-name">DeepSeek</span>
        </div>
      </header>

      <!-- 对话内容区 -->
      <main class="ds-content" ref="chatMain">
        <!-- 欢迎界面 -->
        <div v-if="messages.length === 0" class="ds-welcome">
          <div class="ds-logo">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 12h8M12 8v8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <h1>有什么可以帮你的？</h1>
          <div class="ds-suggestions">
            <button v-for="s in suggestions" :key="s" class="ds-suggestion" @click="sendSuggestion(s)">
              {{ s }}
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-else class="ds-messages">
          <template v-for="(msg, idx) in messages" :key="idx">
            <!-- 用户消息 -->
            <div v-if="msg.role === 'user'" class="ds-msg ds-msg-user">
              <div class="ds-msg-content">{{ msg.content }}</div>
            </div>
            
            <!-- AI消息 -->
            <div v-else class="ds-msg ds-msg-ai">
              <!-- 思考过程 - DeepSeek风格 -->
              <div v-if="getThinking(msg.content)" class="ds-thinking">
                <div class="ds-thinking-header" @click="toggleThinking(idx)">
                  <div class="ds-thinking-left">
                    <div class="ds-thinking-icon">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                      </svg>
                    </div>
                    <span class="ds-thinking-title">已深度思考</span>
                    <span class="ds-thinking-time" v-if="msg.thinkingTime">(用时 {{ msg.thinkingTime }} 秒)</span>
                  </div>
                  <div class="ds-thinking-right">
                    <span class="ds-thinking-toggle">{{ isThinkingExpanded(idx) ? '收起' : '展开' }}</span>
                    <svg :class="['ds-thinking-arrow', { expanded: isThinkingExpanded(idx) }]" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                  </div>
                </div>
                <div v-show="isThinkingExpanded(idx)" class="ds-thinking-body ds-thinking-markdown">
                  <div v-html="renderMarkdown(getThinking(msg.content))"></div>
                </div>
              </div>
              
              <!-- 正式回答 -->
              <div class="ds-msg-content ds-markdown" v-html="renderMarkdown(getAnswer(msg.content))"></div>
              
              <!-- 图片 -->
              <img v-if="msg.image" :src="msg.image" class="ds-msg-image" @click="previewImage(msg.image)" />
              
              <!-- 操作按钮 -->
              <div class="ds-msg-actions">
                <button class="ds-action-btn" @click="copyMessage(msg.content)" title="复制">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
                <button class="ds-action-btn" @click="regenerate(idx)" title="重新生成">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                  </svg>
                </button>
              </div>
            </div>
          </template>
          
          <!-- 联网搜索结果（可折叠） -->
          <div v-if="searchResults" class="ds-msg ds-msg-ai">
            <div class="ds-search-results">
              <div class="ds-search-header" @click="searchResultsExpanded = !searchResultsExpanded">
                <svg :class="['ds-search-arrow', { expanded: searchResultsExpanded }]" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
                <span>联网搜索结果</span>
                <span class="ds-search-count">{{ parseSearchResults(searchResults).length }}条来源</span>
              </div>
              <div v-show="searchResultsExpanded" class="ds-search-body">
                <div v-for="(item, idx) in parseSearchResults(searchResults)" :key="idx" class="ds-search-item">
                  <a :href="item.url" target="_blank" class="ds-search-link">
                    <span class="ds-search-idx">{{ idx + 1 }}</span>
                    <span class="ds-search-title">{{ item.title }}</span>
                  </a>
                  <p class="ds-search-snippet">{{ item.snippet }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 实时思考中状态 -->
          <div v-if="(isThinking && enableDeepThink) || streamingContent || streamingAnswer" class="ds-msg ds-msg-ai">
            <!-- 实时思考过程（可折叠） -->
            <div v-if="streamingContent && enableDeepThink" class="ds-thinking ds-thinking-active">
              <div class="ds-thinking-header" @click="streamingThinkingExpanded = !streamingThinkingExpanded">
                <div class="ds-thinking-left">
                  <svg v-if="!isThinking" :class="['ds-thinking-arrow', { expanded: streamingThinkingExpanded }]" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                  <div v-else class="ds-thinking-spinner"></div>
                  <span class="ds-thinking-title">{{ isThinking ? '正在深度思考...' : '已深度思考' }}</span>
                  <span class="ds-thinking-time">({{ thinkingSeconds }} 秒)</span>
                </div>
                <span class="ds-thinking-toggle">{{ streamingThinkingExpanded ? '收起' : '展开' }}</span>
              </div>
              <div v-show="streamingThinkingExpanded" class="ds-thinking-body ds-thinking-markdown">
                <div v-html="renderMarkdown(streamingContent)"></div>
              </div>
            </div>
            <!-- 正在输出的回答 -->
            <div v-if="streamingAnswer" class="ds-msg-content ds-markdown" v-html="renderMarkdown(streamingAnswer)"></div>
          </div>
          
          <!-- 输入中状态 -->
          <div v-if="loading && !isThinking && !streamingAnswer && !streamingContent" class="ds-msg ds-msg-ai">
            <div class="ds-typing">
              <span></span><span></span><span></span>
            </div>
          </div>
          
          <!-- 图片生成中 -->
          <div v-if="generatingImage" class="ds-msg ds-msg-ai">
            <div class="ds-generating">
              <div class="ds-thinking-spinner"></div>
              <span>正在生成图片...</span>
            </div>
          </div>
        </div>
      </main>

      <!-- 输入区域 -->
      <footer class="ds-footer">
        <div class="ds-input-area">
          <!-- 功能开关 -->
          <div class="ds-toggles">
            <label v-if="supportsDeepThink" class="ds-toggle" :class="{ active: enableDeepThink }">
              <input type="checkbox" v-model="enableDeepThink" />
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 6v6l4 2"></path>
              </svg>
              <span>深度思考</span>
            </label>
            <label class="ds-toggle" :class="{ active: enableWebSearch }">
              <input type="checkbox" v-model="enableWebSearch" />
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
              </svg>
              <span>联网搜索</span>
            </label>
          </div>
          <div class="ds-input-box">
            <textarea 
              v-model="inputText" 
              @keydown.enter.exact.prevent="sendMessage"
              @input="autoResize"
              placeholder="给 DeepSeek 发送消息"
              rows="1"
              ref="inputRef"
            ></textarea>
            <div class="ds-input-actions">
              <button 
                v-if="loading" 
                class="ds-stop-btn" 
                @click="stopGeneration"
                title="停止生成"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="6" width="12" height="12" rx="2"></rect>
                </svg>
              </button>
              <button 
                v-else
                class="ds-send-btn" 
                @click="sendMessage" 
                :disabled="!inputText.trim()"
                :class="{ active: inputText.trim() }"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
          </div>
          <p class="ds-disclaimer">AI 生成内容仅供参考</p>
        </div>
      </footer>
    </div>

    <!-- 图片预览 -->
    <div v-if="previewUrl" class="ds-preview-modal" @click="previewUrl = ''">
      <img :src="previewUrl" />
    </div>
    
    <!-- 复制成功提示 -->
    <div v-if="showCopyTip" class="ds-copy-tip">已复制到剪贴板</div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import axios from 'axios'

const emit = defineEmits(['back'])

// 状态
const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const isThinking = ref(false)
const thinkingSeconds = ref(0)
const generatingImage = ref(false)
const chatMain = ref(null)
const inputRef = ref(null)
const sidebarOpen = ref(true)
const thinkingExpanded = ref({})
const showCopyTip = ref(false)
const abortController = ref(null)
const streamingContent = ref('')  // 实时思考内容
const streamingAnswer = ref('')   // 实时回答内容
const streamingThinkingExpanded = ref(true)  // 思考过程默认展开
const enableDeepThink = ref(false)   // 深度思考开关
const enableWebSearch = ref(false)  // 联网搜索开关
const searchResults = ref('')  // 联网搜索结果
const searchResultsExpanded = ref(false)  // 搜索结果默认折叠
const supportsDeepThink = ref(false)  // 模型是否支持深度思考

// 聊天记录
const conversations = ref([])
const currentConvId = ref('')
const previewUrl = ref('')

let thinkingTimer = null

const suggestions = [
  '解释一下量子计算的基本原理',
  '用Python写一个快速排序算法',
  '帮我写一首关于春天的诗',
  '如何提高英语口语能力？'
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

// 提取思考过程
function getThinking(content) {
  if (!content) return ''
  
  // 检测思考过程的特征模式
  const thinkingIndicators = [
    /^1\.\s*\*\*[^*]+\*\*/, // 以 "1. **xxx**" 开头
    /^\*\*分析/, // 以 **分析 开头
    /^#+\s*思考/, // 以 # 思考 开头
    /^让我/, // 以 "让我" 开头
    /^首先.*分析/, // 以 "首先...分析" 开头
  ]
  
  const hasThinkingStart = thinkingIndicators.some(p => p.test(content.trim()))
  if (!hasThinkingStart) return ''
  
  // 寻找思考结束、正式回答开始的标记
  const answerMarkers = [
    /\n---\n/, // 分隔线
    /\n\*\*《[^》]+》\*\*\n/, // 诗歌标题格式
    /\n#{1,3}\s*《[^》]+》/, // 标题格式
    /\n好的[，,]?这是/, // "好的，这是"
    /\n以下是/, // "以下是"
    /\n这是一首/, // "这是一首"
    /\n根据你的要求/, // "根据你的要求"
  ]
  
  let splitIndex = -1
  for (const marker of answerMarkers) {
    const match = content.match(marker)
    if (match && match.index !== undefined) {
      if (splitIndex === -1 || match.index < splitIndex) {
        splitIndex = match.index
      }
    }
  }
  
  // 如果找到分隔点且思考内容足够长
  if (splitIndex > 100) {
    return content.substring(0, splitIndex).trim()
  }
  
  return ''
}

function getAnswer(content) {
  if (!content) return ''
  const thinking = getThinking(content)
  if (!thinking) return content
  
  let answer = content.substring(thinking.length).trim()
  // 移除开头的分隔线
  answer = answer.replace(/^---\s*\n*/, '').trim()
  return answer
}

function toggleThinking(idx) {
  // 默认展开，点击切换
  if (thinkingExpanded.value[idx] === undefined) {
    thinkingExpanded.value[idx] = false  // 第一次点击折叠
  } else {
    thinkingExpanded.value[idx] = !thinkingExpanded.value[idx]
  }
}

function isThinkingExpanded(idx) {
  // 默认展开
  return thinkingExpanded.value[idx] !== false
}

function scrollToBottom() {
  nextTick(() => {
    if (chatMain.value) {
      chatMain.value.scrollTop = chatMain.value.scrollHeight
    }
  })
}

function previewImage(url) {
  previewUrl.value = url
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

async function copyMessage(content) {
  try {
    await navigator.clipboard.writeText(getAnswer(content))
    showCopyTip.value = true
    setTimeout(() => showCopyTip.value = false, 2000)
  } catch (e) {
    console.error('复制失败', e)
  }
}

function startThinkingTimer() {
  thinkingSeconds.value = 0
  isThinking.value = true
  thinkingTimer = setInterval(() => {
    thinkingSeconds.value++
  }, 1000)
}

function stopThinkingTimer() {
  isThinking.value = false
  if (thinkingTimer) {
    clearInterval(thinkingTimer)
    thinkingTimer = null
  }
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
  currentConvId.value = ''
  messages.value = []
  inputRef.value?.focus()
}

async function loadConversation(convId) {
  try {
    const res = await axios.get(`/api/conversations/${convId}`)
    currentConvId.value = convId
    messages.value = res.data.conversation?.messages || []
    scrollToBottom()
  } catch (e) {
    console.error(e)
  }
}

async function saveConversation() {
  if (!currentConvId.value) {
    try {
      const res = await axios.post('/api/conversations')
      currentConvId.value = res.data.conversation_id
    } catch (e) {
      console.error(e)
      return
    }
  }
  const title = messages.value.find(m => m.role === 'user')?.content?.slice(0, 30) || '新对话'
  try {
    await axios.put(`/api/conversations/${currentConvId.value}`, { messages: messages.value, title })
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

function sendSuggestion(text) {
  inputText.value = text
  sendMessage()
}

function isImageRequest(text) {
  const patterns = [
    /^生成图片[:：]\s*(.+)/i,
    /^画一[张个幅][:：]?\s*(.+)/i,
    /^画[:：]\s*(.+)/i
  ]
  for (const p of patterns) {
    const m = text.match(p)
    if (m) return m[1].trim()
  }
  return null
}

async function generateImage(prompt) {
  generatingImage.value = true
  scrollToBottom()
  
  try {
    const res = await axios.post('/api/chat/image', { prompt })
    if (res.data.success && res.data.url) {
      messages.value.push({ role: 'assistant', content: '已为你生成图片：', image: res.data.url })
    } else {
      messages.value.push({ role: 'assistant', content: `图片生成失败：${res.data.error || '未知错误'}` })
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: `图片生成失败：${e.message}` })
  }
  
  generatingImage.value = false
  await saveConversation()
  scrollToBottom()
}

async function regenerate(idx) {
  // 找到该AI消息对应的用户消息
  let userMsgIdx = idx - 1
  while (userMsgIdx >= 0 && messages.value[userMsgIdx].role !== 'user') {
    userMsgIdx--
  }
  if (userMsgIdx < 0) return
  
  const userMsg = messages.value[userMsgIdx].content
  // 删除该AI消息及之后的消息
  messages.value = messages.value.slice(0, idx)
  // 重新发送
  inputText.value = userMsg
  messages.value = messages.value.slice(0, userMsgIdx)
  await sendMessage()
}

function stopGeneration() {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }
  loading.value = false
  stopThinkingTimer()
}

// 解析搜索结果文本为结构化数据
function parseSearchResults(text) {
  if (!text) return []
  const results = []
  // 匹配格式: - 标题 (URL): 内容  或  - 标题: 内容
  const lines = text.split('\n')
  let currentItem = null
  
  for (const line of lines) {
    const match = line.match(/^-\s*(.+?)\s*\(?(https?:\/\/[^\s\)]+)?\)?:\s*(.*)$/)
    if (match) {
      if (currentItem) results.push(currentItem)
      currentItem = {
        title: match[1].trim(),
        url: match[2] || '',
        snippet: match[3].trim()
      }
    } else if (currentItem && line.trim()) {
      currentItem.snippet += ' ' + line.trim()
    }
  }
  if (currentItem) results.push(currentItem)
  
  // 尝试从标题中提取URL（如果URL为空）
  return results.map(item => {
    if (!item.url) {
      // 尝试用标题搜索
      item.url = `https://www.google.com/search?q=${encodeURIComponent(item.title)}`
    }
    return item
  })
}

// 实时检测思考内容分隔点
function detectAnswerStart(content) {
  const markers = [
    /\n---\n/,
    /\n\*\*《[^》]+》\*\*\n/,
    /\n#{1,3}\s*《[^》]+》/,
    /\n好的[，,]?这是/,
    /\n以下是/,
    /\n这是一首/,
    /\n根据你的要求/,
    /\n你好[！!]/,
  ]
  
  for (const marker of markers) {
    const match = content.match(marker)
    if (match && match.index !== undefined && match.index > 100) {
      return match.index
    }
  }
  return -1
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

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
  streamingContent.value = ''
  streamingAnswer.value = ''
  streamingThinkingExpanded.value = true
  searchResults.value = ''
  startThinkingTimer()
  scrollToBottom()
  
  // 重置输入框高度
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }

  abortController.value = new AbortController()
  let fullContent = ''
  let answerStartIdx = -1

  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ 
        message: text, 
        history: messages.value.slice(-10),
        deep_think: enableDeepThink.value,
        web_search: enableWebSearch.value
      }),
      signal: abortController.value.signal
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data:')) {
          const data = line.slice(5).trim()
          if (data === '[DONE]') break
          try {
            const parsed = JSON.parse(data)
            // 处理搜索结果
            if (parsed.search_results) {
              searchResults.value = parsed.search_results
            }
            if (parsed.content) {
              fullContent += parsed.content
              
              // 实时检测分隔点
              if (answerStartIdx === -1) {
                answerStartIdx = detectAnswerStart(fullContent)
              }
              
              // 更新实时显示
              if (!enableDeepThink.value) {
                // 未开启深度思考，直接显示回答
                streamingAnswer.value = fullContent
                if (isThinking.value) {
                  stopThinkingTimer()
                }
              } else if (answerStartIdx === -1) {
                // 还在思考阶段
                streamingContent.value = fullContent
              } else {
                // 已进入回答阶段
                if (isThinking.value) {
                  stopThinkingTimer()
                }
                streamingContent.value = fullContent.substring(0, answerStartIdx).trim()
                streamingAnswer.value = fullContent.substring(answerStartIdx).replace(/^---\s*\n*/, '').trim()
              }
              
              scrollToBottom()
            }
            if (parsed.error) {
              streamingAnswer.value = `错误: ${parsed.error}`
            }
          } catch {}
        }
      }
    }

    // 流式结束，保存到消息列表
    const thinkingTime = thinkingSeconds.value
    stopThinkingTimer()
    
    messages.value.push({ 
      role: 'assistant', 
      content: fullContent, 
      thinkingTime 
    })
    
    // 清空实时内容
    streamingContent.value = ''
    streamingAnswer.value = ''

    const aiContent = fullContent
    const imgMatch = aiContent.match(/\[生成图片[:：]\s*([^\]]+)\]/i)
    if (imgMatch) {
      messages.value[messages.value.length - 1].content = aiContent.replace(/\[生成图片[:：][^\]]+\]/i, '').trim()
      await generateImage(imgMatch[1])
    }

    await saveConversation()
  } catch (e) {
    if (e.name !== 'AbortError') {
      stopThinkingTimer()
      messages.value.push({ role: 'assistant', content: `请求失败: ${e.message}` })
    }
  } finally {
    loading.value = false
    abortController.value = null
  }
  
  scrollToBottom()
}

onMounted(async () => {
  inputRef.value?.focus()
  await loadConversations()
  // 获取配置，检查模型是否支持深度思考
  try {
    const res = await axios.get('/api/config')
    supportsDeepThink.value = res.data.supports_deep_think || false
    enableDeepThink.value = supportsDeepThink.value  // 支持则默认开启
  } catch (e) {
    supportsDeepThink.value = false
  }
})

onUnmounted(() => {
  stopThinkingTimer()
})
</script>

<style scoped>
/* DeepSeek 风格样式 */
.ds-chat-container {
  display: flex;
  height: 100vh;
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 侧边栏 - DeepSeek风格 */
.ds-sidebar {
  width: 260px;
  background: #f7f7f8;
  border-right: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
  transition: all 0.25s ease;
  flex-shrink: 0;
  position: relative;
}

.ds-sidebar.collapsed {
  width: 0;
  margin-left: -260px;
}

.ds-sidebar-header {
  padding: 12px;
}

.ds-new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  cursor: pointer;
  transition: all 0.2s;
}

.ds-new-chat-btn:hover {
  background: #f0f0f0;
  border-color: #d5d5d5;
}

.ds-conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px;
}

.ds-conv-list::-webkit-scrollbar {
  width: 4px;
}

.ds-conv-list::-webkit-scrollbar-track {
  background: transparent;
}

.ds-conv-list::-webkit-scrollbar-thumb {
  background: #d1d1d1;
  border-radius: 4px;
}

.ds-empty {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 13px;
}

.ds-conv-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin: 2px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.ds-conv-item:hover {
  background: #ebebeb;
}

.ds-conv-item.active {
  background: #e3e3e3;
}

.ds-conv-icon {
  flex-shrink: 0;
  color: #666;
}

.ds-conv-title {
  flex: 1;
  font-size: 13px;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ds-conv-delete {
  opacity: 0;
  background: none;
  border: none;
  padding: 4px;
  color: #999;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s;
}

.ds-conv-item:hover .ds-conv-delete {
  opacity: 1;
}

.ds-conv-delete:hover {
  background: #ddd;
  color: #e53935;
}

.ds-sidebar-footer {
  padding: 12px;
  border-top: 1px solid #e5e5e5;
}

.ds-back-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: none;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.15s;
}

.ds-back-btn:hover {
  background: #ebebeb;
  color: #1a1a1a;
}

/* 主内容区 - DeepSeek风格 */
.ds-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #ffffff;
  position: relative;
}

.ds-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #ffffff;
  border-bottom: 1px solid #e5e5e5;
  position: sticky;
  top: 0;
  z-index: 10;
}

.ds-menu-btn {
  background: none;
  border: none;
  padding: 8px;
  color: #666;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s;
}

.ds-menu-btn:hover {
  background: #f0f0f0;
  color: #1a1a1a;
}

.ds-model-selector {
  margin-left: 12px;
}

.ds-model-name {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
}

/* 内容区 */
.ds-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  scroll-behavior: smooth;
}

.ds-content::-webkit-scrollbar {
  width: 6px;
}

.ds-content::-webkit-scrollbar-track {
  background: transparent;
}

.ds-content::-webkit-scrollbar-thumb {
  background: #d1d1d1;
  border-radius: 6px;
}

.ds-content::-webkit-scrollbar-thumb:hover {
  background: #b0b0b0;
}

/* 欢迎页 - DeepSeek风格 */
.ds-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 60px 24px;
  text-align: center;
}

.ds-logo {
  width: 64px;
  height: 64px;
  background: #4d6bfe;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.ds-logo svg {
  color: #ffffff;
  width: 32px;
  height: 32px;
}

.ds-welcome h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px;
}

.ds-welcome p {
  color: #666;
  font-size: 14px;
  margin-bottom: 32px;
}

.ds-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 600px;
}

.ds-suggestion {
  padding: 10px 16px;
  background: #f7f7f8;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 13px;
  color: #1a1a1a;
  cursor: pointer;
  transition: all 0.15s;
}

.ds-suggestion:hover {
  background: #ebebeb;
  border-color: #d5d5d5;
}

/* 消息列表 - DeepSeek风格 */
.ds-messages {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 20px;
}

.ds-msg {
  margin-bottom: 24px;
}

/* 用户消息 */
.ds-msg-user {
  display: flex;
  justify-content: flex-end;
}

.ds-msg-user .ds-msg-content {
  max-width: 70%;
  padding: 12px 16px;
  background: #4d6bfe;
  color: #ffffff;
  border-radius: 18px 18px 4px 18px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* AI消息 */
.ds-msg-ai {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.ds-msg-ai .ds-msg-content {
  font-size: 14px;
  line-height: 1.75;
  color: #1a1a1a;
}

/* 联网搜索结果 - DeepSeek风格 */
.ds-search-results {
  width: 100%;
  margin-bottom: 12px;
  background: #f7f7f8;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  overflow: hidden;
}

.ds-search-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #1a9058;
  font-weight: 500;
  font-size: 14px;
  background: #f0fdf4;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.ds-search-header:hover {
  background: #e6f7ed;
}

.ds-search-arrow {
  transition: transform 0.2s;
  flex-shrink: 0;
}

.ds-search-arrow.expanded {
  transform: rotate(90deg);
}

.ds-search-header svg {
  stroke: #1a9058;
}

.ds-search-count {
  margin-left: auto;
  font-size: 12px;
  color: #666;
  font-weight: 400;
}

.ds-search-body {
  padding: 0;
  border-top: 1px solid #e5e5e5;
}

.ds-search-item {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.ds-search-item:last-child {
  border-bottom: none;
}

.ds-search-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #1a73e8;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
}

.ds-search-link:hover {
  text-decoration: underline;
}

.ds-search-idx {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #e8f0fe;
  color: #1a73e8;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
  flex-shrink: 0;
}

.ds-search-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ds-search-snippet {
  margin: 0;
  font-size: 13px;
  color: #555;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 思考过程 - DeepSeek风格 */
.ds-thinking {
  width: 100%;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  overflow: hidden;
}

.ds-thinking-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
}

.ds-thinking-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ds-thinking-icon {
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}

.ds-thinking-title {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.ds-thinking-time {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-left: 4px;
}

.ds-thinking-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ds-thinking-toggle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.ds-thinking-arrow {
  color: rgba(255, 255, 255, 0.9);
  transition: transform 0.25s ease;
}

.ds-thinking-arrow.expanded {
  transform: rotate(180deg);
}

.ds-thinking-body {
  background: #ffffff;
  margin: 0 2px 2px 2px;
  border-radius: 0 0 10px 10px;
  padding: 16px 20px;
  font-size: 14px;
  color: #374151;
  line-height: 1.75;
  max-height: 500px;
  overflow-y: auto;
}

.ds-thinking-body::-webkit-scrollbar {
  width: 6px;
}

.ds-thinking-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.ds-thinking-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.ds-thinking-body::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* 思考过程 Markdown 优化样式 */
.ds-thinking-markdown :deep(p) {
  margin: 10px 0;
  line-height: 1.7;
}

.ds-thinking-markdown :deep(ul) {
  list-style-type: disc;
  padding-left: 24px;
  margin: 10px 0;
}

.ds-thinking-markdown :deep(ol) {
  list-style-type: decimal;
  padding-left: 24px;
  margin: 10px 0;
}

.ds-thinking-markdown :deep(ul ul) {
  list-style-type: circle;
  margin: 6px 0;
}

.ds-thinking-markdown :deep(ul ul ul) {
  list-style-type: square;
}

.ds-thinking-markdown :deep(li) {
  margin: 6px 0;
  line-height: 1.6;
}

.ds-thinking-markdown :deep(li > p) {
  margin: 4px 0;
}

.ds-thinking-markdown :deep(strong) {
  color: #4338ca;
  font-weight: 600;
}

.ds-thinking-markdown :deep(em) {
  color: #6366f1;
  font-style: italic;
}

.ds-thinking-markdown :deep(h1) {
  margin: 16px 0 10px;
  font-weight: 700;
  color: #1f2937;
  font-size: 16px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 6px;
}

.ds-thinking-markdown :deep(h2) {
  margin: 14px 0 8px;
  font-weight: 600;
  color: #374151;
  font-size: 15px;
}

.ds-thinking-markdown :deep(h3),
.ds-thinking-markdown :deep(h4) {
  margin: 12px 0 6px;
  font-weight: 600;
  color: #4b5563;
  font-size: 14px;
}

.ds-thinking-markdown :deep(code) {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  color: #7c3aed;
}

.ds-thinking-markdown :deep(pre) {
  background: #1f2937;
  border-radius: 8px;
  padding: 14px;
  margin: 12px 0;
  overflow-x: auto;
}

.ds-thinking-markdown :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #e5e7eb;
}

.ds-thinking-markdown :deep(blockquote) {
  border-left: 3px solid #8b5cf6;
  padding-left: 14px;
  margin: 12px 0;
  color: #6b7280;
  background: #faf5ff;
  padding: 10px 14px;
  border-radius: 0 6px 6px 0;
}

.ds-thinking-markdown :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 16px 0;
}

.ds-thinking-markdown :deep(a) {
  color: #6366f1;
  text-decoration: none;
}

.ds-thinking-markdown :deep(a:hover) {
  text-decoration: underline;
}

.ds-thinking-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e5e5e5;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 消息操作 - DeepSeek风格 */
.ds-msg-actions {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.15s;
}

.ds-msg-ai:hover .ds-msg-actions {
  opacity: 1;
}

.ds-action-btn {
  background: none;
  border: none;
  padding: 6px;
  color: #999;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s;
}

.ds-action-btn:hover {
  background: #f0f0f0;
  color: #1a1a1a;
}

/* 图片 */
.ds-msg-image {
  max-width: 400px;
  max-height: 300px;
  border-radius: 12px;
  margin-top: 12px;
  cursor: pointer;
}

/* 输入中 */
.ds-typing {
  display: flex;
  gap: 4px;
  padding: 12px 0;
}

.ds-typing span {
  width: 8px;
  height: 8px;
  background: #ccc;
  border-radius: 50%;
  animation: typing 1.4s ease-in-out infinite;
}

.ds-typing span:nth-child(2) { animation-delay: 0.2s; }
.ds-typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.ds-generating {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  color: #666;
  font-size: 14px;
}

/* 底部输入区 - DeepSeek风格 */
.ds-footer {
  padding: 16px 20px 24px;
  background: #ffffff;
  border-top: 1px solid #e5e5e5;
}

.ds-input-area {
  max-width: 800px;
  margin: 0 auto;
}

.ds-input-box {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px 16px;
  background: #f7f7f8;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  transition: all 0.2s;
}

.ds-input-box:focus-within {
  border-color: #4d6bfe;
  background: #ffffff;
}

.ds-input-box textarea {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  outline: none;
  max-height: 150px;
  min-height: 22px;
  color: #1a1a1a;
}

.ds-input-box textarea::placeholder {
  color: #999;
}

.ds-input-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.ds-send-btn, .ds-stop-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
}

.ds-send-btn {
  background: #e5e5e5;
  color: #999;
}

.ds-send-btn.active {
  background: #4d6bfe;
  color: #ffffff;
}

.ds-send-btn.active:hover {
  background: #3d5bee;
}

.ds-send-btn:disabled {
  cursor: not-allowed;
}

.ds-stop-btn {
  background: #e53935;
  color: #ffffff;
}

.ds-stop-btn:hover {
  background: #d32f2f;
}

/* 功能开关 - DeepSeek风格 */
.ds-toggles {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.ds-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f7f7f8;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  font-size: 13px;
  font-weight: 500;
  color: #666;
  user-select: none;
}

.ds-toggle input {
  display: none;
}

.ds-toggle svg {
  width: 16px;
  height: 16px;
}

.ds-toggle:hover {
  background: #ebebeb;
}

.ds-toggle.active {
  background: #4d6bfe;
  border-color: #4d6bfe;
  color: #ffffff;
}

.ds-toggle.active svg {
  stroke: #ffffff;
}

.ds-disclaimer {
  text-align: center;
  font-size: 11px;
  color: #999;
  margin-top: 12px;
}

/* 图片预览 */
.ds-preview-modal {
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

.ds-preview-modal img {
  max-width: 90%;
  max-height: 90%;
  border-radius: 8px;
}

/* 复制提示 */
.ds-copy-tip {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 20px;
  background: #1a1a1a;
  color: #ffffff;
  border-radius: 8px;
  font-size: 14px;
  z-index: 1000;
  animation: fadeInOut 2s ease;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0; }
  20%, 80% { opacity: 1; }
}

/* Markdown样式 */
.ds-markdown :deep(pre) {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 16px 0;
}

.ds-markdown :deep(code) {
  font-family: 'SF Mono', Monaco, 'Fira Code', monospace;
  font-size: 13px;
}

.ds-markdown :deep(p) { margin: 12px 0; }
.ds-markdown :deep(ul), .ds-markdown :deep(ol) { padding-left: 24px; margin: 12px 0; }
.ds-markdown :deep(li) { margin: 6px 0; }
.ds-markdown :deep(h1), .ds-markdown :deep(h2), .ds-markdown :deep(h3) { 
  margin: 20px 0 12px; 
  font-weight: 600;
  color: #1a1a1a;
}
.ds-markdown :deep(blockquote) {
  border-left: 3px solid #e5e5e5;
  padding-left: 16px;
  margin: 16px 0;
  color: #666;
}
.ds-markdown :deep(a) {
  color: #4f46e5;
  text-decoration: none;
}
.ds-markdown :deep(a:hover) {
  text-decoration: underline;
}

/* 响应式 - 平板 */
@media (max-width: 1024px) {
  .ds-sidebar {
    width: 220px;
  }
}

/* 响应式 - 手机 */
@media (max-width: 768px) {
  .ds-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    width: 280px;
    max-width: 85%;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }
  
  .ds-sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .ds-sidebar::after {
    content: '';
    position: fixed;
    top: 0;
    left: 100%;
    right: -100vw;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s;
  }
  
  .ds-sidebar:not(.collapsed)::after {
    opacity: 1;
    pointer-events: auto;
  }
  
  .ds-header {
    padding: 10px 12px;
  }
  
  .ds-model-name {
    font-size: 14px;
  }
  
  .ds-logo {
    width: 48px;
    height: 48px;
    border-radius: 12px;
  }
  
  .ds-logo svg {
    width: 24px;
    height: 24px;
  }
  
  .ds-welcome {
    padding: 40px 16px;
  }
  
  .ds-welcome h1 {
    font-size: 20px;
    margin-bottom: 6px;
  }
  
  .ds-welcome p {
    font-size: 13px;
    margin-bottom: 24px;
  }
  
  .ds-suggestions {
    gap: 8px;
  }
  
  .ds-suggestion {
    padding: 10px 14px;
    font-size: 12px;
  }
  
  .ds-messages {
    padding: 16px 12px;
  }
  
  .ds-msg {
    margin-bottom: 16px;
  }
  
  .ds-msg-user .ds-msg-content {
    max-width: 85%;
    padding: 10px 14px;
    font-size: 13px;
    border-radius: 14px 14px 4px 14px;
  }
  
  .ds-msg-ai .ds-msg-content {
    font-size: 13px;
    line-height: 1.7;
  }
  
  /* 思考过程手机适配 */
  .ds-thinking {
    border-radius: 10px;
    margin-bottom: 12px;
  }
  
  .ds-thinking-header {
    padding: 10px 14px;
  }
  
  .ds-thinking-icon {
    width: 20px;
    height: 20px;
  }
  
  .ds-thinking-icon svg {
    width: 12px;
    height: 12px;
  }
  
  .ds-thinking-title {
    font-size: 13px;
  }
  
  .ds-thinking-time {
    font-size: 11px;
  }
  
  .ds-thinking-toggle {
    font-size: 12px;
  }
  
  .ds-thinking-arrow {
    width: 14px;
    height: 14px;
  }
  
  .ds-thinking-body {
    padding: 14px 16px;
    font-size: 13px;
    max-height: 300px;
    margin: 0 2px 2px 2px;
  }
  
  .ds-thinking-markdown :deep(p) {
    margin: 8px 0;
    font-size: 13px;
  }
  
  .ds-thinking-markdown :deep(li) {
    font-size: 13px;
    margin: 4px 0;
  }
  
  .ds-thinking-markdown :deep(ul),
  .ds-thinking-markdown :deep(ol) {
    padding-left: 18px;
  }
  
  .ds-thinking-markdown :deep(h1) {
    font-size: 14px;
  }
  
  .ds-thinking-markdown :deep(h2) {
    font-size: 13px;
  }
  
  .ds-thinking-markdown :deep(h3),
  .ds-thinking-markdown :deep(h4) {
    font-size: 13px;
  }
  
  .ds-thinking-markdown :deep(strong) {
    font-size: 13px;
  }
  
  /* 输入区域手机适配 */
  .ds-footer {
    padding: 12px 12px 20px;
  }
  
  .ds-toggles {
    gap: 6px;
    margin-bottom: 10px;
  }
  
  .ds-toggle {
    padding: 6px 10px;
    font-size: 12px;
  }
  
  .ds-toggle svg {
    width: 14px;
    height: 14px;
  }
  
  .ds-input-box {
    padding: 10px 12px;
    border-radius: 10px;
  }
  
  .ds-input-box textarea {
    font-size: 14px;
  }
  
  .ds-send-btn, .ds-stop-btn {
    width: 34px;
    height: 34px;
  }
  
  .ds-disclaimer {
    font-size: 10px;
    margin-top: 8px;
  }
  
  /* 操作按钮始终显示 */
  .ds-msg-actions {
    opacity: 1;
  }
  
  .ds-action-btn {
    padding: 6px;
  }
  
  /* 搜索结果 */
  .ds-search-results {
    border-radius: 8px;
  }
  
  .ds-search-header {
    padding: 8px 12px;
    font-size: 12px;
  }
  
  .ds-search-body {
    padding: 0 12px 12px;
    font-size: 11px;
  }
  
  /* 图片适配 */
  .ds-msg-image {
    max-width: 100%;
    border-radius: 8px;
  }
  
  .ds-copy-tip {
    bottom: 80px;
    font-size: 12px;
    padding: 8px 16px;
  }
}

/* 响应式 - 小手机 */
@media (max-width: 480px) {
  .ds-sidebar {
    width: 100%;
    max-width: none;
  }
  
  .ds-sidebar::after {
    display: none;
  }
  
  .ds-welcome h1 {
    font-size: 18px;
  }
  
  .ds-welcome p {
    font-size: 12px;
  }
  
  .ds-suggestion {
    width: 100%;
    text-align: center;
    padding: 10px 12px;
  }
  
  .ds-msg-user .ds-msg-content {
    max-width: 88%;
  }
  
  .ds-thinking {
    border-radius: 8px;
  }
  
  .ds-thinking-header {
    padding: 8px 12px;
  }
  
  .ds-thinking-icon {
    width: 18px;
    height: 18px;
  }
  
  .ds-thinking-title {
    font-size: 12px;
  }
  
  .ds-thinking-time {
    font-size: 10px;
  }
  
  .ds-thinking-toggle {
    font-size: 11px;
  }
  
  .ds-thinking-body {
    padding: 12px 14px;
    max-height: 250px;
    font-size: 12px;
  }
  
  .ds-footer {
    padding: 10px 10px 16px;
  }
  
  .ds-toggles {
    gap: 4px;
  }
  
  .ds-toggle {
    padding: 5px 8px;
    font-size: 11px;
  }
}
</style>
