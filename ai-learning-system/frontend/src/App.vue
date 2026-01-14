<template>
  <div class="app-root">
    <!-- 登录/注册页面 -->
    <LoginView v-if="currentView === 'login'" @login="handleLogin" @register="currentView = 'register'" />
    <RegisterView v-else-if="currentView === 'register'" @registered="currentView = 'login'" @login="currentView = 'login'" />
    
    <!-- 公开文章页面 -->
    <PublicArticle v-else-if="currentView === 'public-article'" :articleId="publicArticleId" @login="currentView = 'login'" />
    
    <!-- 平台首页 -->
    <PlatformHome v-else-if="currentView === 'platform'" :user="user" @enter-tool="enterTool" @logout="logout" />
    
    <!-- LearnFlow 工具主界面 -->
    <div v-else-if="currentView === 'learnflow'" class="app-container">
      <!-- 移动端菜单按钮 -->
      <button class="mobile-menu-btn" @click="toggleSidebar">{{ sidebarOpen ? '✕' : '☰' }}</button>
      
      <!-- 移动端遮罩 -->
      <div :class="['mobile-overlay', { active: sidebarOpen }]" @click="sidebarOpen = false"></div>
      
      <!-- 侧边栏 -->
      <aside :class="['sidebar', { open: sidebarOpen }]">
        <div class="logo">
          <button class="btn-back-platform" @click="backToPlatform">← 返回平台</button>
        </div>
        <div class="tool-title">
          <div class="tool-icon-box">📚</div>
          <div class="tool-text">
            <h1>AI 快速学</h1>
            <p>智能学习内容生成</p>
          </div>
        </div>
        
        <nav class="nav-menu">
          <button v-for="item in navItems" :key="item.id" :class="['nav-item', { active: toolView === item.id }]" @click="handleNavClick(item.id)">
            <span class="nav-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
            <span v-if="item.id === 'articles' && runningTasks > 0" class="task-badge">{{ runningTasks }}</span>
          </button>
        </nav>
        
        <div class="sidebar-footer">
          <div class="user-info" v-if="user">
            <span class="user-avatar">{{ user.username.charAt(0).toUpperCase() }}</span>
            <span class="user-name">{{ user.username }}</span>
          </div>
          <div class="api-status">
            <span :class="['status-dot', apiStatus]"></span>
            <span>{{ apiStatusText }}</span>
          </div>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <HomeView v-if="toolView === 'home'" @generate="handleGenerate" />
        <ArticlesView v-else-if="toolView === 'articles'" @view="viewArticle" @new="toolView = 'home'" />
        <DocumentsView v-else-if="toolView === 'documents'" @view="viewDocument" @viewArticle="viewArticle" @new="toolView = 'home'" />
        <SettingsView v-else-if="toolView === 'settings'" @saved="checkApiStatus" />
        <ArticleDetail v-else-if="toolView === 'article-detail'" :article="currentArticle" @back="goBack" />
        <DocumentDetail v-else-if="toolView === 'document-detail'" :document="currentDocument" @back="goBack" />
      </main>

      <!-- 大纲确认弹窗 -->
      <div v-if="showOutlineModal" class="modal-overlay" @click.self="showOutlineModal = false">
        <div class="modal-content modal-xl">
          <div class="modal-header">
            <h3>📋 确认学习大纲</h3>
            <button class="modal-close" @click="showOutlineModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="outline-info">
              <h4>{{ pendingOutline?.title }}</h4>
              <p>{{ pendingOutline?.description }}</p>
            </div>
            <div class="outline-chapters">
              <div v-for="(ch, idx) in pendingOutline?.chapters" :key="ch.id" class="outline-chapter-item">
                <div class="chapter-header">
                  <span class="chapter-badge">{{ ch.id }}</span>
                  <input v-model="ch.title" class="chapter-title-input" />
                  <button class="btn-icon-sm btn-delete-chapter" @click="removeChapter(idx)" title="删除章节">×</button>
                </div>
                <textarea v-model="ch.description" class="chapter-desc-input" rows="2" placeholder="章节描述..."></textarea>
              </div>
              <button class="btn-add-chapter" @click="addChapter">+ 添加章节</button>
            </div>
            <div class="feedback-section">
              <label>💡 补充要求（可选）</label>
              <textarea v-model="outlineFeedback" class="input-field" rows="3" placeholder="您可以补充更多要求..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="regenerateOutline" :disabled="outlineLoading">{{ outlineLoading ? '生成中...' : '🔄 重新生成' }}</button>
            <button class="btn btn-primary" @click="confirmOutline" :disabled="outlineLoading">✅ 确认生成文档</button>
          </div>
        </div>
      </div>
      
      <!-- 任务通知面板 -->
      <div class="task-panel" v-if="notifications.length > 0 || runningTasks > 0">
        <div class="task-panel-header" @click="taskPanelExpanded = !taskPanelExpanded">
          <div class="task-panel-title">
            <span v-if="runningTasks > 0" class="panel-spinner"></span>
            <span v-else class="panel-check">✓</span>
            <span>{{ runningTasks > 0 ? `${runningTasks} 个任务进行中` : '任务完成' }}</span>
          </div>
          <button class="panel-toggle">{{ taskPanelExpanded ? '收起' : '展开' }}</button>
        </div>
        <div class="task-panel-body" v-show="taskPanelExpanded">
          <div v-for="(notif, idx) in notifications" :key="idx" :class="['task-item', notif.type]">
            <div class="task-item-icon">
              <span v-if="notif.type === 'running'" class="item-spinner"></span>
              <span v-else-if="notif.type === 'success'">✓</span>
              <span v-else>!</span>
            </div>
            <div class="task-item-content">
              <p class="task-item-title">{{ notif.title }}</p>
              <p class="task-item-desc">{{ notif.desc }}</p>
              <div v-if="notif.progress" class="task-progress">
                <div class="task-progress-bar" :style="{ width: notif.progress + '%' }"></div>
              </div>
            </div>
            <button class="task-item-close" @click="removeNotification(idx)">×</button>
          </div>
          <div v-if="notifications.length === 0" class="task-empty">暂无任务</div>
        </div>
      </div>
    </div>

    <!-- AI 对话界面 -->
    <ChatView v-else-if="currentView === 'chat'" :user="user" @back="backToPlatform" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import PlatformHome from './components/PlatformHome.vue'
import HomeView from './components/HomeView.vue'
import ArticlesView from './components/ArticlesView.vue'
import DocumentsView from './components/DocumentsView.vue'
import SettingsView from './components/SettingsView.vue'
import ArticleDetail from './components/ArticleDetail.vue'
import DocumentDetail from './components/DocumentDetail.vue'
import LoginView from './components/LoginView.vue'
import RegisterView from './components/RegisterView.vue'
import PublicArticle from './components/PublicArticle.vue'
import ChatView from './components/ChatView.vue'

const navItems = [
  { id: 'home', icon: '🏠', label: '首页' },
  { id: 'articles', icon: '📝', label: '文章列表' },
  { id: 'documents', icon: '📚', label: '学习文档' }
]

// 视图状态
const currentView = ref('login')  // login, register, platform, learnflow, public-article
const toolView = ref('home')      // LearnFlow内部视图
const previousToolView = ref('home')
const publicArticleId = ref('')

const apiStatus = ref('disconnected')
const apiStatusText = ref('检查中...')
const sidebarOpen = ref(false)
const user = ref(null)

const notifications = ref([])
const runningTasks = ref(0)
const taskPanelExpanded = ref(true)

const currentArticle = ref(null)
const currentDocument = ref(null)

// 大纲相关
const showOutlineModal = ref(false)
const pendingOutline = ref(null)
const outlineFeedback = ref('')
const outlineLoading = ref(false)

// axios 拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      user.value = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      currentView.value = 'login'
    }
    return Promise.reject(error)
  }
)

function toggleSidebar() { sidebarOpen.value = !sidebarOpen.value }
function handleNavClick(view) { toolView.value = view; sidebarOpen.value = false }
function goBack() { toolView.value = previousToolView.value || 'home' }

function handleLogin(userData) {
  user.value = userData
  // 保存完整的登录数据包括过期时间
  localStorage.setItem('user', JSON.stringify(userData))
  localStorage.setItem('token', userData.token)
  localStorage.setItem('tokenExpire', userData.expireTime || (Date.now() + 30 * 24 * 60 * 60 * 1000))
  axios.defaults.headers.common['Authorization'] = `Bearer ${userData.token}`
  currentView.value = 'platform'
  checkApiStatus()
}

function logout() {
  user.value = null
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  localStorage.removeItem('tokenExpire')
  delete axios.defaults.headers.common['Authorization']
  currentView.value = 'login'
}

function enterTool(toolName) {
  if (toolName === 'learnflow') {
    currentView.value = 'learnflow'
    toolView.value = 'home'
    restoreRunningTasks()
  }
}

function backToPlatform() {
  currentView.value = 'platform'
}

function addNotification(title, desc, type = 'running') {
  const notif = { title, desc, type, progress: 0 }
  notifications.value.unshift(notif)
  if (type === 'running') runningTasks.value++
  taskPanelExpanded.value = true
  return 0
}

function updateNotification(idx, updates) {
  if (notifications.value[idx]) {
    if (notifications.value[idx].type === 'running' && updates.type !== 'running') runningTasks.value--
    Object.assign(notifications.value[idx], updates)
    if (updates.type === 'success') setTimeout(() => removeNotification(idx), 5000)
  }
}

function removeNotification(idx) {
  if (notifications.value[idx]?.type === 'running') runningTasks.value--
  notifications.value.splice(idx, 1)
}

async function handleGenerate(data) {
  const { topic, description, links, enableSearch, generateType } = data
  if (generateType === 'article') {
    await generateArticleAsync(topic, description, links, enableSearch)
  } else {
    await generateOutlineForConfirm(topic, description, links, enableSearch)
  }
}

async function generateArticleAsync(topic, description, links, enableSearch) {
  const notifIdx = addNotification('生成文章', `「${topic}」正在后台生成...`, 'running')
  try {
    const res = await axios.post('/api/generate/article', { topic, description, links, enableSearch })
    if (res.data.success) pollTaskStatus(res.data.task_id, notifIdx, 'article')
  } catch (e) {
    updateNotification(notifIdx, { type: 'error', desc: e.response?.data?.detail || '创建失败' })
  }
}

async function generateOutlineForConfirm(topic, description, links, enableSearch) {
  outlineLoading.value = true
  const notifIdx = addNotification('生成大纲', `「${topic}」正在生成学习大纲...`, 'running')
  try {
    const res = await axios.post('/api/generate/outline', { topic, description, links, enableSearch })
    if (res.data.success) {
      pendingOutline.value = res.data.outline
      updateNotification(notifIdx, { type: 'success', desc: '大纲生成完成，请确认' })
      showOutlineModal.value = true
    }
  } catch (e) {
    updateNotification(notifIdx, { type: 'error', desc: e.response?.data?.detail || '生成失败' })
  }
  outlineLoading.value = false
}

async function regenerateOutline() {
  if (!pendingOutline.value) return
  outlineLoading.value = true
  try {
    const res = await axios.post('/api/regenerate/outline', { outline_id: pendingOutline.value.id, feedback: outlineFeedback.value, chapters: pendingOutline.value.chapters })
    if (res.data.success) { pendingOutline.value = res.data.outline; outlineFeedback.value = '' }
  } catch (e) { alert('重新生成失败: ' + (e.response?.data?.detail || e.message)) }
  outlineLoading.value = false
}

function addChapter() {
  if (!pendingOutline.value) return
  const newId = (pendingOutline.value.chapters?.length || 0) + 1
  pendingOutline.value.chapters.push({ id: newId, title: `第${newId}章 新章节`, description: '请填写章节描述' })
}

function removeChapter(idx) {
  if (!pendingOutline.value || pendingOutline.value.chapters.length <= 1) return
  pendingOutline.value.chapters.splice(idx, 1)
  pendingOutline.value.chapters.forEach((ch, i) => { ch.id = i + 1 })
}

async function confirmOutline() {
  if (!pendingOutline.value) return
  showOutlineModal.value = false
  const notifIdx = addNotification('生成文档', `正在并发生成 ${pendingOutline.value.chapters.length} 个章节...`, 'running')
  try {
    await axios.post('/api/update/outline', { outline_id: pendingOutline.value.id, chapters: pendingOutline.value.chapters, feedback: outlineFeedback.value })
    const res = await axios.post('/api/generate/document', { outline_id: pendingOutline.value.id })
    if (res.data.success) pollTaskStatus(res.data.task_id, notifIdx, 'document')
  } catch (e) {
    updateNotification(notifIdx, { type: 'error', desc: e.response?.data?.detail || '生成失败' })
  }
  pendingOutline.value = null
  outlineFeedback.value = ''
}

function pollTaskStatus(taskId, notifIdx, type) {
  const check = async () => {
    try {
      const res = await axios.get(`/api/task/${taskId}`)
      if (res.data.current_step) updateNotification(notifIdx, { desc: res.data.current_step })
      if (res.data.status === 'completed') {
        updateNotification(notifIdx, { type: 'success', desc: type === 'article' ? '🎉 文章已生成' : '🎉 文档已生成', progress: 100 })
      } else if (res.data.status === 'running') {
        if (type === 'document' && res.data.completed !== undefined) {
          updateNotification(notifIdx, { progress: Math.round((res.data.completed / res.data.total) * 100) })
        }
        setTimeout(check, 1500)
      } else if (res.data.status === 'failed') {
        updateNotification(notifIdx, { type: 'error', desc: res.data.error || '生成失败' })
      } else { setTimeout(check, 1500) }
    } catch (e) { setTimeout(check, 3000) }
  }
  check()
}

async function viewArticle(id) {
  try {
    const res = await axios.get(`/api/articles/${id}`)
    currentArticle.value = res.data.article
    previousToolView.value = toolView.value
    toolView.value = 'article-detail'
  } catch (e) { alert('加载失败') }
}

async function viewDocument(id) {
  try {
    const res = await axios.get(`/api/documents/${id}`)
    currentDocument.value = res.data.document
    previousToolView.value = toolView.value
    toolView.value = 'document-detail'
  } catch (e) { alert('加载失败') }
}

async function checkApiStatus() {
  try {
    const res = await axios.get('/api/config')
    if (res.data.configured) { apiStatus.value = 'connected'; apiStatusText.value = 'API 已配置' }
    else { apiStatus.value = 'disconnected'; apiStatusText.value = '未配置API' }
  } catch (e) { apiStatus.value = 'error'; apiStatusText.value = '连接失败' }
}

async function restoreRunningTasks() {
  try {
    const res = await axios.get('/api/tasks')
    for (const task of (res.data.tasks || [])) {
      if (task.status === 'running' || task.status === 'pending') {
        const notifIdx = addNotification(task.type === 'article' ? '生成文章' : '生成文档', task.current_step || '正在生成中...', 'running')
        if (task.task_id || task.id) pollTaskStatus(task.task_id || task.id, notifIdx, task.type)
      }
    }
  } catch (e) { console.error('恢复任务失败', e) }
}

onMounted(async () => {
  const path = window.location.pathname
  if (path.startsWith('/article/')) {
    publicArticleId.value = path.replace('/article/', '')
    currentView.value = 'public-article'
    return
  }
  
  // 检查是否是 OAuth 回调
  const urlParams = new URLSearchParams(window.location.search)
  const oauthToken = urlParams.get('token')
  const oauthUsername = urlParams.get('username')
  
  if (oauthToken && oauthUsername) {
    // OAuth 登录成功
    const userData = { username: oauthUsername, token: oauthToken }
    handleLogin(userData)
    // 清除 URL 中的参数
    window.history.replaceState({}, document.title, window.location.pathname)
    return
  }
  
  const savedUser = localStorage.getItem('user')
  const token = localStorage.getItem('token')
  const tokenExpire = localStorage.getItem('tokenExpire')
  
  // 检查 token 是否过期（30天有效期）
  if (savedUser && token && tokenExpire) {
    const expireTime = parseInt(tokenExpire)
    if (Date.now() < expireTime) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      try {
        await axios.get('/api/config')
        user.value = JSON.parse(savedUser)
        currentView.value = 'platform'
      } catch (e) {
        // 只有在服务器明确返回401时才清除登录状态
        if (e.response?.status === 401) {
          localStorage.removeItem('user')
          localStorage.removeItem('token')
          localStorage.removeItem('tokenExpire')
          delete axios.defaults.headers.common['Authorization']
          currentView.value = 'login'
        } else {
          // 网络错误等情况，保持登录状态
          user.value = JSON.parse(savedUser)
          currentView.value = 'platform'
        }
      }
    } else {
      // token 已过期
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      localStorage.removeItem('tokenExpire')
      currentView.value = 'login'
    }
  } else {
    currentView.value = 'login'
  }
  checkApiStatus()
})
</script>

<style scoped>
.app-root { min-height: 100vh; }

.tool-title { display: flex; align-items: center; gap: 12px; padding: 20px 16px; background: linear-gradient(135deg, var(--primary-bg), rgba(139, 92, 246, 0.08)); border-radius: var(--radius-lg); margin-bottom: 24px; }
.tool-icon-box { font-size: 2rem; }
.tool-text h1 { font-size: 1.1rem; font-weight: 700; background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.tool-text p { font-size: 11px; color: var(--text-muted); }

.btn-back-platform { background: none; border: none; color: var(--text-secondary); font-size: 13px; cursor: pointer; padding: 8px 0; display: flex; align-items: center; gap: 4px; }
.btn-back-platform:hover { color: var(--primary); }

.task-badge { background: var(--primary); color: white; font-size: 11px; padding: 2px 6px; border-radius: 10px; margin-left: auto; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }

.user-info { display: flex; align-items: center; gap: 10px; padding: 12px; background: var(--bg-main); border-radius: var(--radius-sm); margin-bottom: 12px; }
.user-avatar { width: 32px; height: 32px; background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 14px; }
.user-name { flex: 1; font-size: 14px; color: var(--text-primary); font-weight: 500; }

/* 大纲弹窗 */
.outline-info { margin-bottom: 24px; padding: 20px; background: linear-gradient(135deg, #EEF2FF, #F5F3FF); border-radius: var(--radius-md); }
.outline-info h4 { font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; }
.outline-info p { color: var(--text-secondary); font-size: 14px; }
.outline-chapters { margin-bottom: 24px; }
.outline-chapter-item { background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 16px; margin-bottom: 12px; }
.chapter-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.chapter-badge { width: 28px; height: 28px; background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.chapter-title-input { flex: 1; padding: 8px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 14px; font-weight: 600; color: var(--text-primary); background: var(--bg-white); }
.chapter-title-input:focus { outline: none; border-color: var(--primary); }
.btn-delete-chapter { width: 28px; height: 28px; background: #FEE2E2; border: none; border-radius: 6px; color: var(--error); font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.btn-delete-chapter:hover { background: var(--error); color: white; }
.chapter-desc-input { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 13px; color: var(--text-secondary); background: var(--bg-white); resize: none; }
.chapter-desc-input:focus { outline: none; border-color: var(--primary); }
.btn-add-chapter { width: 100%; padding: 12px; background: var(--bg-white); border: 2px dashed var(--border); border-radius: var(--radius-md); color: var(--text-muted); font-size: 14px; cursor: pointer; transition: all 0.2s; }
.btn-add-chapter:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-bg); }
.feedback-section label { display: block; font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px; }

/* 任务面板 */
.task-panel { position: fixed; bottom: 24px; right: 24px; z-index: 900; width: 380px; background: white; border-radius: var(--radius-lg); box-shadow: 0 10px 40px rgba(0,0,0,0.15); overflow: hidden; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.task-panel-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; cursor: pointer; }
.task-panel-title { display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 600; }
.panel-spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite; }
.panel-check { font-size: 14px; }
.panel-toggle { background: rgba(255,255,255,0.2); border: none; color: white; font-size: 12px; padding: 4px 10px; border-radius: 12px; cursor: pointer; }
.panel-toggle:hover { background: rgba(255,255,255,0.3); }
.task-panel-body { max-height: 320px; overflow-y: auto; }
.task-item { display: flex; align-items: flex-start; gap: 12px; padding: 16px 20px; border-bottom: 1px solid var(--border-light); transition: background 0.2s; }
.task-item:hover { background: var(--bg-main); }
.task-item:last-child { border-bottom: none; }
.task-item-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }
.task-item.running .task-item-icon { background: var(--primary-bg); color: var(--primary); }
.task-item.success .task-item-icon { background: #D1FAE5; color: #059669; }
.task-item.error .task-item-icon { background: #FEE2E2; color: #DC2626; }
.item-spinner { width: 14px; height: 14px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.task-item-content { flex: 1; min-width: 0; }
.task-item-title { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.task-item-desc { font-size: 13px; color: var(--text-secondary); }
.task-progress { margin-top: 8px; height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }
.task-progress-bar { height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent)); border-radius: 2px; transition: width 0.3s ease; }
.task-item-close { background: none; border: none; color: var(--text-muted); font-size: 18px; cursor: pointer; padding: 0; line-height: 1; opacity: 0; transition: opacity 0.2s; }
.task-item:hover .task-item-close { opacity: 1; }
.task-item-close:hover { color: var(--error); }
.task-empty { padding: 32px; text-align: center; color: var(--text-muted); font-size: 14px; }

@media (max-width: 768px) {
  .task-panel { 
    bottom: 0; 
    right: 0; 
    left: 0; 
    width: 100%; 
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    max-height: 50vh;
  }
  .task-panel-header { padding: 14px 16px; }
  .task-panel-title { font-size: 13px; }
  .task-panel-body { max-height: calc(50vh - 50px); }
  .task-item { padding: 12px 16px; }
  .task-item-icon { width: 28px; height: 28px; font-size: 12px; }
  .task-item-title { font-size: 13px; }
  .task-item-desc { font-size: 12px; }
  
  .tool-title { padding: 16px; margin-bottom: 20px; }
  .tool-icon-box { font-size: 1.5rem; }
  .tool-text h1 { font-size: 1rem; }
  .tool-text p { font-size: 10px; }
  
  .outline-info { padding: 16px; margin-bottom: 20px; }
  .outline-info h4 { font-size: 1.1rem; }
  .outline-info p { font-size: 13px; }
  .outline-chapters { margin-bottom: 20px; }
  .outline-chapter-item { padding: 12px; margin-bottom: 10px; }
  .chapter-badge { width: 24px; height: 24px; font-size: 11px; }
  .chapter-title-input { padding: 8px 10px; font-size: 13px; }
  .chapter-desc-input { padding: 8px 10px; font-size: 12px; }
  .btn-add-chapter { padding: 10px; font-size: 13px; }
  .feedback-section label { font-size: 13px; }
}
</style>
