<template>
  <div class="view settings-view">
    <div class="view-header">
      <h2>⚙️ 系统设置</h2>
    </div>
    
    <div class="glass-card">
      <div class="settings-section">
        <h3>🔑 API 配置</h3>
        <p class="section-desc">选择 AI 服务提供商并配置 API Key</p>
      </div>
      
      <div class="form-group">
        <label>服务提供商</label>
        <select v-model="provider" class="input-field" @change="onProviderChange">
          <option value="siliconflow">硅基流动 (SiliconFlow)</option>
          <option value="deepseek">DeepSeek</option>
          <option value="openai">OpenAI</option>
          <option value="gemini">Google Gemini</option>
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
      
      <button class="btn btn-primary btn-block" @click="saveConfig">💾 保存配置</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const emit = defineEmits(['saved'])

const provider = ref('siliconflow')
const apiKey = ref('')
const apiBase = ref('https://api.siliconflow.cn/v1')
const model = ref('deepseek-ai/DeepSeek-V3')
const keyPlaceholder = ref('请输入 API Key')
const statusMessage = ref('')
const statusType = ref('')

const providers = {
  siliconflow: {
    name: '硅基流动',
    url: 'https://cloud.siliconflow.cn',
    baseUrl: 'https://api.siliconflow.cn/v1',
    models: [
      { label: 'DeepSeek-V3 (推荐)', value: 'deepseek-ai/DeepSeek-V3' },
      { label: 'DeepSeek-R1', value: 'deepseek-ai/DeepSeek-R1' },
      { label: 'DeepSeek-R1-Distill-Qwen-32B', value: 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B' },
      { label: 'Qwen2.5-72B-Instruct', value: 'Qwen/Qwen2.5-72B-Instruct' },
      { label: 'Qwen2.5-32B-Instruct', value: 'Qwen/Qwen2.5-32B-Instruct' },
      { label: 'Qwen2.5-Coder-32B', value: 'Qwen/Qwen2.5-Coder-32B-Instruct' },
      { label: 'GLM-4-Plus', value: 'THUDM/GLM-4-Plus' },
      { label: 'Yi-Lightning', value: '01-ai/Yi-Lightning' }
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
      { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
      { label: 'GPT-4', value: 'gpt-4' },
      { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
      { label: 'o1', value: 'o1' },
      { label: 'o1-mini', value: 'o1-mini' },
      { label: 'o1-preview', value: 'o1-preview' }
    ]
  },
  gemini: {
    name: 'Google Gemini',
    url: 'https://aistudio.google.com',
    baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai',
    models: [
      { label: 'Gemini 2.0 Flash (推荐)', value: 'gemini-2.0-flash' },
      { label: 'Gemini 2.0 Flash-Lite', value: 'gemini-2.0-flash-lite' },
      { label: 'Gemini 1.5 Pro', value: 'gemini-1.5-pro' },
      { label: 'Gemini 1.5 Flash', value: 'gemini-1.5-flash' },
      { label: 'Gemini 1.5 Flash-8B', value: 'gemini-1.5-flash-8b' }
    ]
  },
  custom: {
    name: '自定义',
    url: '',
    baseUrl: '',
    models: [
      { label: '自定义模型', value: 'custom-model' }
    ]
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

async function loadConfig() {
  try {
    const res = await axios.get('/api/config')
    if (res.data.api_key) keyPlaceholder.value = `当前: ${res.data.api_key}`
    apiBase.value = res.data.api_base || 'https://api.siliconflow.cn/v1'
    model.value = res.data.model || 'deepseek-ai/DeepSeek-V3'
    provider.value = res.data.provider || 'siliconflow'
    
    // 根据 baseUrl 自动识别 provider
    if (!res.data.provider) {
      if (apiBase.value.includes('deepseek.com')) provider.value = 'deepseek'
      else if (apiBase.value.includes('openai.com')) provider.value = 'openai'
      else if (apiBase.value.includes('googleapis.com')) provider.value = 'gemini'
      else if (apiBase.value.includes('siliconflow.cn')) provider.value = 'siliconflow'
      else provider.value = 'custom'
    }
    
    if (res.data.configured) {
      statusMessage.value = '✅ API 已配置，可以开始使用'
      statusType.value = 'success'
    } else {
      statusMessage.value = '⚠️ 请配置 API Key 后使用'
      statusType.value = 'warning'
    }
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
      emit('saved')
    }
  } catch (e) { 
    statusMessage.value = '❌ 保存失败'
    statusType.value = 'error' 
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.settings-view { max-width: 640px; }
.settings-section { margin-bottom: 28px; }
.settings-section h3 { font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; color: var(--text-primary); }
.section-desc { color: var(--text-secondary); font-size: 14px; }
.form-hint { display: block; margin-top: 8px; font-size: 13px; color: var(--text-muted); }
.form-hint a { color: var(--primary); text-decoration: none; }
.form-hint a:hover { text-decoration: underline; }
</style>
