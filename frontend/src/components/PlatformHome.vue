<template>
  <div class="platform-container">
    <!-- 顶部导航 -->
    <header class="platform-header">
      <div class="header-content">
        <div class="platform-logo">
          <div class="logo-icon-box">
            <svg viewBox="0 0 24 24" fill="none" class="logo-svg">
              <path d="M12 2L2 7l10 5 10-5-10-5z" fill="url(#pgrad1)"/>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="url(#pgrad2)" stroke-width="2" fill="none"/>
              <defs>
                <linearGradient id="pgrad1" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#6366F1"/><stop offset="100%" style="stop-color:#8B5CF6"/>
                </linearGradient>
                <linearGradient id="pgrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#818CF8"/><stop offset="100%" style="stop-color:#A78BFA"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div class="logo-text">
            <h1>AI Tools</h1>
            <p>智能工具平台</p>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn-settings" @click="showSettings = true" title="系统设置">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
            </svg>
          </button>
          <div class="header-user" v-if="user">
            <span class="user-avatar">{{ user.username.charAt(0).toUpperCase() }}</span>
            <span class="user-name">{{ user.username }}</span>
            <button class="btn-logout" @click="$emit('logout')">退出</button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="platform-main">
      <div class="hero-section">
        <h1>🚀 AI 智能工具平台</h1>
        <p>探索强大的AI工具，提升您的工作与学习效率</p>
        <!-- API状态提示 -->
        <div :class="['api-status-bar', apiConfigured ? 'configured' : 'not-configured']" @click="showSettings = true">
          <span class="status-icon">{{ apiConfigured ? '✅' : '⚠️' }}</span>
          <span>{{ apiConfigured ? `已配置 ${currentProvider}` : '请先配置 API Key' }}</span>
          <span class="status-action">点击设置 →</span>
        </div>
      </div>

      <div class="tools-section">
        <div class="section-header">
          <h2>🛠️ 工具中心</h2>
          <p>选择您需要的AI工具开始使用</p>
        </div>
        
        <div class="tools-grid">
          <!-- AI快速学 -->
          <div class="tool-card featured" @click="enterLearnFlow">
            <div class="tool-header">
              <div class="tool-icon">📚</div>
              <span class="tool-badge hot">热门</span>
            </div>
            <h3>AI 快速学</h3>
            <p>智能生成学习文档和文章，快速掌握任何知识领域</p>
            <div class="tool-features">
              <span>✓ 智能大纲</span>
              <span>✓ 多章节文档</span>
              <span>✓ AI问答</span>
            </div>
            <button class="btn btn-primary btn-block">进入工具 →</button>
          </div>

          <!-- 更多工具占位 -->
          <div class="tool-card disabled">
            <div class="tool-header">
              <div class="tool-icon">🎨</div>
              <span class="tool-badge soon">即将上线</span>
            </div>
            <h3>AI 绘图</h3>
            <p>文字描述生成精美图片，释放您的创意想象</p>
            <div class="tool-features">
              <span>✓ 多种风格</span>
              <span>✓ 高清输出</span>
            </div>
            <button class="btn btn-secondary btn-block" disabled>敬请期待</button>
          </div>

          <div class="tool-card disabled">
            <div class="tool-header">
              <div class="tool-icon">💬</div>
              <span class="tool-badge soon">即将上线</span>
            </div>
            <h3>AI 对话</h3>
            <p>智能对话助手，解答各类问题与疑惑</p>
            <div class="tool-features">
              <span>✓ 多轮对话</span>
              <span>✓ 知识问答</span>
            </div>
            <button class="btn btn-secondary btn-block" disabled>敬请期待</button>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部 -->
    <footer class="platform-footer">
      <p>© 2025 AI Tools Platform. All rights reserved.</p>
    </footer>
    
    <!-- 设置弹窗 -->
    <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>⚙️ 系统设置</h3>
          <button class="modal-close" @click="showSettings = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="settings-section">
            <h4>🔑 API 配置</h4>
            <p class="section-desc">选择 AI 服务提供商并配置 API Key</p>
          </div>
          
          <div class="form-group">
            <label>服务提供商</label>
            <select v-model="provider" class="input-field" @change="onProviderChange">
              <option value="siliconflow">硅基流动 (SiliconFlow)</option>
              <option value="aliyun">阿里云百炼 (DashScope)</option>
              <option value="deepseek">DeepSeek</option>
              <option value="openai">OpenAI</option>
              <option value="gemini">Google Gemini</option>
              <option value="xinliu">心流 (iFlow)</option>
              <option value="custom">自定义</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>API Key</label>
            <input v-model="apiKey" type="password" class="input-field" :placeholder="keyPlaceholder" />
            <small class="form-hint">
              获取地址: <a :href="providerInfo.url" target="_blank">{{ providerInfo.url }}</a>
            </small>
          </div>
          
          <div class="form-group">
            <label>API Base URL</label>
            <input v-model="apiBase" type="text" class="input-field" :disabled="provider !== 'custom'" />
          </div>
          
          <div class="form-group">
            <label>模型选择</label>
            <select v-model="model" class="input-field">
              <optgroup v-for="group in modelGroups" :key="group.label" :label="group.label">
                <option v-for="m in group.models" :key="m.value" :value="m.value">
                  {{ m.label }}
                </option>
              </optgroup>
            </select>
          </div>
          
          <div v-if="statusMessage" :class="['config-status', statusType]">{{ statusMessage }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showSettings = false">取消</button>
          <button class="btn btn-primary" @click="saveConfig">💾 保存配置</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

defineProps({ user: Object })
const emit = defineEmits(['enter-tool', 'logout'])

// 设置相关
const showSettings = ref(false)
const provider = ref('siliconflow')
const apiKey = ref('')
const apiBase = ref('https://api.siliconflow.cn/v1')
const model = ref('deepseek-ai/DeepSeek-V3')
const keyPlaceholder = ref('请输入 API Key')
const statusMessage = ref('')
const statusType = ref('')
const apiConfigured = ref(false)
const currentProvider = ref('')

const providers = {
  siliconflow: {
    name: '硅基流动',
    url: 'https://cloud.siliconflow.cn',
    baseUrl: 'https://api.siliconflow.cn/v1',
    models: [
      { label: 'DeepSeek-V3.2 (最新推荐)', value: 'deepseek-ai/DeepSeek-V3.2' },
      { label: 'DeepSeek-V3.2 Pro', value: 'Pro/deepseek-ai/DeepSeek-V3.2' },
      { label: 'DeepSeek-V3', value: 'deepseek-ai/DeepSeek-V3' },
      { label: 'DeepSeek-R1', value: 'deepseek-ai/DeepSeek-R1' },
      { label: 'Qwen2.5-72B-Instruct', value: 'Qwen/Qwen2.5-72B-Instruct' }
    ]
  },
  aliyun: {
    name: '阿里云百炼',
    url: 'https://bailian.console.aliyun.com',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    models: [
      { label: 'DeepSeek-V3.2 685B 满血版 (推荐)', value: 'deepseek-v3.2' },
      { label: 'DeepSeek-V3.2-Exp 685B 满血版', value: 'deepseek-v3.2-exp' },
      { label: 'DeepSeek-V3.1 685B 满血版', value: 'deepseek-v3.1' },
      { label: 'DeepSeek-R1 685B 满血版', value: 'deepseek-r1' },
      { label: 'DeepSeek-R1-0528 685B 满血版', value: 'deepseek-r1-0528' },
      { label: 'DeepSeek-V3 671B 满血版', value: 'deepseek-v3' },
      { label: 'Qwen-Max', value: 'qwen-max' },
      { label: 'Qwen-Plus', value: 'qwen-plus' }
    ]
  },
  deepseek: {
    name: 'DeepSeek',
    url: 'https://platform.deepseek.com',
    baseUrl: 'https://api.deepseek.com/v1',
    models: [
      { label: 'DeepSeek Chat (推荐)', value: 'deepseek-chat' },
      { label: 'DeepSeek Coder', value: 'deepseek-coder' },
      { label: 'DeepSeek Reasoner', value: 'deepseek-reasoner' }
    ]
  },
  openai: {
    name: 'OpenAI',
    url: 'https://platform.openai.com',
    baseUrl: 'https://api.openai.com/v1',
    models: [
      { label: 'GPT-4o (推荐)', value: 'gpt-4o' },
      { label: 'GPT-4o Mini', value: 'gpt-4o-mini' },
      { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' }
    ]
  },
  gemini: {
    name: 'Google Gemini',
    url: 'https://aistudio.google.com',
    baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai',
    models: [
      { label: 'Gemini 2.0 Flash (推荐)', value: 'gemini-2.0-flash' },
      { label: 'Gemini 1.5 Pro', value: 'gemini-1.5-pro' }
    ]
  },
  xinliu: {
    name: '心流 (iFlow)',
    url: 'https://iflow.cn',
    baseUrl: 'https://apis.iflow.cn/v1',
    models: [
      { label: 'GLM-4.6 (推荐)', value: 'glm-4.6' },
      { label: 'iFlow Rome 30B', value: 'iflow-rome-30ba3b' },
      { label: 'Qwen3 Coder Plus', value: 'qwen3-coder-plus' },
      { label: 'Qwen3 Max', value: 'qwen3-max' },
      { label: 'Kimi K2', value: 'kimi-k2' },
      { label: 'DeepSeek-V3.2', value: 'deepseek-v3.2' },
      { label: 'DeepSeek-R1', value: 'deepseek-r1' }
    ]
  },
  custom: {
    name: '自定义',
    url: '',
    baseUrl: '',
    models: [{ label: '自定义模型', value: 'custom-model' }]
  }
}

const providerInfo = computed(() => providers[provider.value] || providers.siliconflow)

const modelGroups = computed(() => {
  const p = providers[provider.value]
  if (!p) return []
  return [{ label: p.name, models: p.models }]
})

function onProviderChange() {
  const p = providers[provider.value]
  if (p) {
    apiBase.value = p.baseUrl
    model.value = p.models[0]?.value || ''
  }
}

function enterLearnFlow() {
  if (!apiConfigured.value) {
    showSettings.value = true
    statusMessage.value = '⚠️ 请先配置 API Key 才能使用工具'
    statusType.value = 'warning'
    return
  }
  emit('enter-tool', 'learnflow')
}

async function loadConfig() {
  try {
    const res = await axios.get('/api/config')
    if (res.data.api_key) keyPlaceholder.value = `当前: ${res.data.api_key}`
    apiBase.value = res.data.api_base || 'https://api.siliconflow.cn/v1'
    model.value = res.data.model || 'deepseek-ai/DeepSeek-V3'
    provider.value = res.data.provider || 'siliconflow'
    
    // 根据 baseUrl 自动识别 provider
    if (!res.data.provider) {
      if (apiBase.value.includes('dashscope.aliyuncs.com')) provider.value = 'aliyun'
      else if (apiBase.value.includes('deepseek.com')) provider.value = 'deepseek'
      else if (apiBase.value.includes('openai.com')) provider.value = 'openai'
      else if (apiBase.value.includes('googleapis.com')) provider.value = 'gemini'
      else if (apiBase.value.includes('siliconflow.cn')) provider.value = 'siliconflow'
      else if (apiBase.value.includes('iflow.cn')) provider.value = 'xinliu'
      else provider.value = 'custom'
    }
    
    apiConfigured.value = res.data.configured
    currentProvider.value = providers[provider.value]?.name || provider.value
  } catch (e) { console.error(e) }
}

async function saveConfig() {
  if (!apiKey.value.trim()) { 
    statusMessage.value = '❌ 请输入 API Key'
    statusType.value = 'error'
    return 
  }
  try {
    const res = await axios.post('/api/config', { 
      api_key: apiKey.value, 
      api_base: apiBase.value, 
      model: model.value,
      provider: provider.value
    })
    if (res.data.success) {
      statusMessage.value = '✅ 配置保存成功！'
      statusType.value = 'success'
      keyPlaceholder.value = `当前: ***${apiKey.value.slice(-4)}`
      apiKey.value = ''
      apiConfigured.value = true
      currentProvider.value = providers[provider.value]?.name || provider.value
      setTimeout(() => { showSettings.value = false }, 1000)
    }
  } catch (e) { 
    statusMessage.value = '❌ 保存失败'
    statusType.value = 'error' 
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.platform-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
  display: flex;
  flex-direction: column;
}

.platform-header {
  background: var(--bg-white);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon-box {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--primary-bg), rgba(139, 92, 246, 0.1));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-svg { width: 28px; height: 28px; }

.logo-text h1 {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-text p { font-size: 11px; color: var(--text-muted); }

.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.user-name {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
}

.btn-logout {
  background: var(--bg-main);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #FEE2E2;
  border-color: #FECACA;
  color: var(--error);
}

.platform-main {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px;
  width: 100%;
}

.hero-section {
  text-align: center;
  margin-bottom: 48px;
}

.hero-section h1 {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary), var(--accent), #EC4899);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.hero-section p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.section-header {
  margin-bottom: 32px;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.section-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.tool-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 28px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tool-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  opacity: 0;
  transition: opacity 0.3s;
}

.tool-card:hover {
  transform: translateY(-6px);
  border-color: var(--primary-light);
  box-shadow: var(--shadow-xl);
}

.tool-card:hover::before { opacity: 1; }

.tool-card.featured {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.05));
  border-color: rgba(99, 102, 241, 0.2);
}

.tool-card.featured::before { opacity: 1; }

.tool-card.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.tool-card.disabled:hover {
  transform: none;
  box-shadow: none;
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.tool-icon { font-size: 2.5rem; }

.tool-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
}

.tool-badge.hot {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
}

.tool-badge.soon {
  background: var(--bg-main);
  color: var(--text-muted);
  border: 1px solid var(--border);
}

.tool-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.tool-card p {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.tool-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.tool-features span {
  font-size: 12px;
  color: var(--primary);
  background: var(--primary-bg);
  padding: 4px 10px;
  border-radius: 6px;
}

.platform-footer {
  text-align: center;
  padding: 24px;
  border-top: 1px solid var(--border);
  background: var(--bg-white);
}

.platform-footer p {
  color: var(--text-muted);
  font-size: 13px;
}

/* 头部操作区 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-settings {
  width: 40px;
  height: 40px;
  background: var(--bg-main);
  border: 1px solid var(--border);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.btn-settings:hover {
  background: var(--primary-bg);
  border-color: var(--primary);
  color: var(--primary);
}

/* API状态栏 */
.api-status-bar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 24px;
  font-size: 14px;
  margin-top: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.api-status-bar.configured {
  background: #D1FAE5;
  color: #059669;
}

.api-status-bar.not-configured {
  background: #FEF3C7;
  color: #D97706;
}

.api-status-bar:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.status-action {
  opacity: 0.7;
  font-size: 12px;
}

/* 设置弹窗内样式 */
.settings-section {
  margin-bottom: 20px;
}

.settings-section h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.section-desc {
  color: var(--text-secondary);
  font-size: 13px;
}

.form-hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.form-hint a {
  color: var(--primary);
  text-decoration: none;
}

.form-hint a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .platform-header { padding-top: env(safe-area-inset-top, 0px); }
  .header-content { padding: 12px 16px; }
  .logo-icon-box { width: 36px; height: 36px; border-radius: 10px; }
  .logo-svg { width: 22px; height: 22px; }
  .logo-text h1 { font-size: 1rem; }
  .logo-text p { font-size: 10px; }
  .user-name { display: none; }
  .user-avatar { width: 32px; height: 32px; font-size: 14px; }
  .btn-logout { padding: 6px 12px; font-size: 12px; }
  .btn-settings { width: 36px; height: 36px; }
  
  .platform-main { padding: 24px 16px; }
  .hero-section { margin-bottom: 32px; }
  .hero-section h1 { font-size: 1.5rem; line-height: 1.3; }
  .hero-section p { font-size: 0.95rem; }
  .api-status-bar { font-size: 13px; padding: 8px 16px; }
  
  .section-header { margin-bottom: 20px; }
  .section-header h2 { font-size: 1.25rem; }
  
  .tools-grid { grid-template-columns: 1fr; gap: 16px; }
  .tool-card { padding: 20px; }
  .tool-icon { font-size: 2rem; }
  .tool-card h3 { font-size: 1.1rem; }
  .tool-card p { font-size: 13px; }
  .tool-features { gap: 6px; }
  .tool-features span { font-size: 11px; padding: 3px 8px; }
  
  .platform-footer { padding: 20px 16px calc(20px + env(safe-area-inset-bottom, 0px)); }
}

@media (max-width: 480px) {
  .header-content { padding: 10px 12px; gap: 8px; }
  .platform-logo { gap: 8px; }
  .logo-icon-box { width: 32px; height: 32px; }
  .logo-svg { width: 20px; height: 20px; }
  
  .platform-main { padding: 20px 12px; }
  .hero-section h1 { font-size: 1.35rem; }
  
  .tool-card { padding: 16px; }
  .tool-header { margin-bottom: 12px; }
  .tool-badge { font-size: 10px; padding: 3px 8px; }
}
</style>
