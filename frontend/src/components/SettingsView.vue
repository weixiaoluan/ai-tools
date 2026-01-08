<template>
  <div class="view settings-view">
    <div class="view-header">
      <h2>⚙️ 系统设置</h2>
    </div>
    
    <div class="glass-card">
      <div class="settings-section">
        <h3>🔑 API 配置</h3>
        <p class="section-desc">配置硅基流动 API 以使用 AI 生成功能</p>
      </div>
      
      <div class="form-group">
        <label>API Key</label>
        <input v-model="apiKey" type="password" class="input-field" :placeholder="keyPlaceholder" />
        <small class="form-hint">
          获取地址: <a href="https://cloud.siliconflow.cn" target="_blank">https://cloud.siliconflow.cn</a>
        </small>
      </div>
      
      <div class="form-group">
        <label>API Base URL</label>
        <input v-model="apiBase" type="text" class="input-field" />
      </div>
      
      <div class="form-group">
        <label>模型选择</label>
        <select v-model="model" class="input-field">
          <option value="deepseek-ai/DeepSeek-V3">DeepSeek-V3 (推荐)</option>
          <option value="deepseek-ai/DeepSeek-R1">DeepSeek-R1</option>
          <option value="Qwen/Qwen2.5-72B-Instruct">Qwen2.5-72B</option>
        </select>
      </div>
      
      <div v-if="statusMessage" :class="['config-status', statusType]">{{ statusMessage }}</div>
      
      <button class="btn btn-primary btn-block" @click="saveConfig">💾 保存配置</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const emit = defineEmits(['saved'])

const apiKey = ref('')
const apiBase = ref('https://api.siliconflow.cn/v1')
const model = ref('deepseek-ai/DeepSeek-V3')
const keyPlaceholder = ref('请输入您的硅基流动 API Key')
const statusMessage = ref('')
const statusType = ref('')

async function loadConfig() {
  try {
    const res = await axios.get('/api/config')
    if (res.data.api_key) keyPlaceholder.value = `当前: ${res.data.api_key}`
    apiBase.value = res.data.api_base || 'https://api.siliconflow.cn/v1'
    model.value = res.data.model || 'deepseek-ai/DeepSeek-V3'
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
  if (!apiKey.value.trim()) { statusMessage.value = '❌ 请输入 API Key'; statusType.value = 'error'; return }
  try {
    const res = await axios.post('/api/config', { api_key: apiKey.value, api_base: apiBase.value, model: model.value })
    if (res.data.success) {
      statusMessage.value = '✅ 配置保存成功！'
      statusType.value = 'success'
      keyPlaceholder.value = `当前: ***${apiKey.value.slice(-4)}`
      apiKey.value = ''
      emit('saved')
    }
  } catch (e) { statusMessage.value = '❌ 保存失败'; statusType.value = 'error' }
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
