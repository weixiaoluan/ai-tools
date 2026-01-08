<template>
  <div class="view">
    <div class="hero">
      <div class="hero-badge">✨ AI 驱动</div>
      <h2>智能学习内容生成</h2>
      <p>输入你想学习的内容，AI将为你生成系统化的学习资料</p>
    </div>
    
    <div class="glass-card generate-card">
      <div class="form-group">
        <label>📚 学习主题</label>
        <input v-model="topic" type="text" class="input-field input-lg" placeholder="例如：Python编程入门、机器学习基础、React框架..." />
      </div>
      
      <div class="form-group">
        <label>📝 补充说明（可选）</label>
        <textarea v-model="description" class="input-field" placeholder="可以补充具体的学习目标、难度要求、侧重点等..."></textarea>
      </div>
      
      <!-- 资料来源选项 -->
      <div class="form-group">
        <label>📎 添加参考资料（可选）</label>
        <div class="source-options">
          <div v-for="source in sourceTypes" :key="source.id" :class="['source-option', { active: activeSource === source.id }]" @click="toggleSource(source.id)">
            <span class="source-icon">{{ source.icon }}</span>
            <span class="source-label">{{ source.label }}</span>
          </div>
        </div>
        
        <!-- 文件上传 -->
        <div v-if="activeSource === 'file'" class="source-input">
          <div class="file-upload" @click="triggerFileInput" @drop.prevent="handleDrop" @dragover.prevent>
            <input ref="fileInput" type="file" multiple accept=".pdf,.doc,.docx,.txt,.md" @change="handleFileSelect" hidden />
            <div class="upload-icon">📄</div>
            <p>点击或拖拽上传文档</p>
            <span class="upload-hint">支持 PDF、Word、TXT、Markdown</span>
          </div>
          <div v-if="files.length" class="file-list">
            <div v-for="(file, idx) in files" :key="idx" class="file-item">
              <span>📄 {{ file.name }}</span>
              <button @click="removeFile(idx)">×</button>
            </div>
          </div>
        </div>
        
        <!-- 链接输入 -->
        <div v-if="activeSource === 'link'" class="source-input">
          <div class="link-input-group">
            <input v-model="linkInput" type="url" class="input-field" placeholder="输入网页链接，如 https://example.com/article" @keyup.enter="addLink" />
            <button class="btn btn-primary btn-sm" @click="addLink">添加</button>
          </div>
          <div v-if="links.length" class="link-list">
            <div v-for="(link, idx) in links" :key="idx" class="link-item">
              <span class="link-icon">🔗</span>
              <span class="link-url">{{ link }}</span>
              <button @click="removeLink(idx)">×</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 联网搜索 -->
      <div class="form-group">
        <div class="search-toggle">
          <div class="search-info">
            <span class="search-icon">🌐</span>
            <div>
              <p class="search-title">启用联网搜索</p>
              <p class="search-desc">AI将自动搜索权威资料，获取最新信息</p>
            </div>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" v-model="enableSearch" />
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      
      <!-- 生成类型选择 -->
      <div class="generate-type-section">
        <label>🎯 选择生成类型</label>
        <div class="type-cards">
          <div :class="['type-card-inline', { active: generateType === 'article' }]" @click="generateType = 'article'">
            <div class="type-radio">
              <span v-if="generateType === 'article'" class="radio-checked">✓</span>
            </div>
            <div class="type-icon-sm">📝</div>
            <div class="type-text">
              <h4>单篇文章</h4>
              <p>快速生成一篇完整文章</p>
            </div>
          </div>
          <div :class="['type-card-inline', { active: generateType === 'document' }]" @click="generateType = 'document'">
            <div class="type-radio">
              <span v-if="generateType === 'document'" class="radio-checked">✓</span>
            </div>
            <div class="type-icon-sm">📚</div>
            <div class="type-text">
              <h4>学习文档</h4>
              <p>多章节深度学习资料</p>
            </div>
          </div>
        </div>
      </div>
      
      <button class="btn btn-primary btn-block btn-lg" @click="handleGenerate" :disabled="!topic.trim()">
        <span class="btn-icon">🚀</span>
        开始生成
      </button>
      <p class="generate-tip">💡 任务将在后台执行，您可以继续浏览其他页面</p>
    </div>
    
    <div class="feature-grid">
      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3>快速生成</h3>
        <p>AI智能分析主题，快速生成高质量学习内容</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🔄</div>
        <h3>后台处理</h3>
        <p>所有任务后台异步执行，不影响您的操作</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>并发生成</h3>
        <p>多章节同时生成，大幅提升效率</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <h3>联网搜索</h3>
        <p>自动搜索最新资料，内容更加权威准确</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['generate'])

const topic = ref('')
const description = ref('')
const activeSource = ref(null)
const enableSearch = ref(true)
const generateType = ref('article')

const sourceTypes = [
  { id: 'file', icon: '📄', label: '上传文档' },
  { id: 'link', icon: '🔗', label: '添加链接' }
]

const fileInput = ref(null)
const files = ref([])
const linkInput = ref('')
const links = ref([])

function toggleSource(id) { activeSource.value = activeSource.value === id ? null : id }
function triggerFileInput() { fileInput.value?.click() }
function handleFileSelect(e) { files.value.push(...Array.from(e.target.files)) }
function handleDrop(e) { files.value.push(...Array.from(e.dataTransfer.files)) }
function removeFile(idx) { files.value.splice(idx, 1) }
function addLink() {
  if (linkInput.value.trim() && !links.value.includes(linkInput.value.trim())) {
    links.value.push(linkInput.value.trim())
    linkInput.value = ''
  }
}
function removeLink(idx) { links.value.splice(idx, 1) }

function handleGenerate() {
  if (!topic.value.trim()) return
  emit('generate', { 
    topic: topic.value, 
    description: description.value,
    files: files.value,
    links: links.value,
    enableSearch: enableSearch.value,
    generateType: generateType.value
  })
  // 清空表单
  topic.value = ''
  description.value = ''
}
</script>

<style scoped>
.hero { text-align: center; margin-bottom: 40px; padding-top: 20px; }
.hero-badge { display: inline-block; padding: 6px 16px; background: linear-gradient(135deg, var(--primary-bg), rgba(124, 58, 237, 0.1)); border-radius: 20px; font-size: 13px; font-weight: 600; color: var(--primary); margin-bottom: 16px; }
.hero h2 { font-size: 2.5rem; font-weight: 800; margin-bottom: 12px; background: linear-gradient(135deg, var(--primary), #7C3AED, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero p { color: var(--text-secondary); font-size: 1.1rem; }

.generate-card { position: relative; overflow: hidden; }
.generate-card::before { content: ''; position: absolute; top: -50%; right: -50%; width: 100%; height: 100%; background: radial-gradient(circle, rgba(79, 70, 229, 0.03) 0%, transparent 70%); pointer-events: none; }

.input-lg { font-size: 16px; padding: 16px 18px; }

.source-options { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.source-option { display: flex; align-items: center; gap: 8px; padding: 10px 16px; background: var(--bg-main); border: 2px solid var(--border); border-radius: var(--radius-sm); cursor: pointer; transition: all 0.2s; font-size: 14px; }
.source-option:hover { border-color: var(--primary-light); background: var(--primary-bg); }
.source-option.active { border-color: var(--primary); background: var(--primary-bg); }
.source-icon { font-size: 16px; }
.source-label { color: var(--text-primary); font-weight: 500; }

.source-input { margin-top: 16px; animation: slideDown 0.3s ease; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

.file-upload { border: 2px dashed var(--border); border-radius: var(--radius-md); padding: 32px; text-align: center; cursor: pointer; transition: all 0.2s; background: var(--bg-main); }
.file-upload:hover { border-color: var(--primary); background: var(--primary-bg); }
.upload-icon { font-size: 40px; margin-bottom: 12px; }
.file-upload p { color: var(--text-primary); margin-bottom: 6px; font-size: 15px; font-weight: 500; }
.upload-hint { font-size: 13px; color: var(--text-muted); }

.file-list, .link-list { margin-top: 12px; display: flex; flex-direction: column; gap: 8px; }
.file-item, .link-item { display: flex; align-items: center; gap: 10px; padding: 12px 14px; background: var(--bg-main); border: 1px solid var(--border); border-radius: var(--radius-sm); }
.file-item span, .link-url { flex: 1; font-size: 14px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-item button, .link-item button { background: none; border: none; color: var(--error); font-size: 18px; cursor: pointer; }

.link-input-group { display: flex; gap: 12px; }
.link-input-group .input-field { flex: 1; }
.link-icon { font-size: 14px; }

.search-toggle { display: flex; align-items: center; justify-content: space-between; padding: 20px; background: linear-gradient(135deg, #EEF2FF, #F5F3FF); border: 2px solid var(--primary-bg); border-radius: var(--radius-md); gap: 16px; }
.search-info { display: flex; align-items: center; gap: 14px; flex: 1; }
.search-icon { font-size: 32px; }
.search-title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.search-desc { font-size: 13px; color: var(--text-muted); }

.toggle-switch { position: relative; width: 52px; height: 28px; flex-shrink: 0; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.toggle-slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: var(--border); border-radius: 28px; transition: 0.3s; }
.toggle-slider:before { position: absolute; content: ""; height: 22px; width: 22px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.3s; box-shadow: var(--shadow-sm); }
.toggle-switch input:checked + .toggle-slider { background: var(--primary); }
.toggle-switch input:checked + .toggle-slider:before { transform: translateX(24px); }

/* 生成类型选择 */
.generate-type-section { margin-bottom: 24px; }
.generate-type-section label { display: block; font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 12px; }

.type-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }

.type-card-inline {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-main);
  border: 2px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}
.type-card-inline:hover { border-color: var(--primary-light); }
.type-card-inline.active { border-color: var(--primary); background: var(--primary-bg); }

.type-radio {
  width: 22px; height: 22px;
  border: 2px solid var(--border);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}
.type-card-inline.active .type-radio { border-color: var(--primary); background: var(--primary); }
.radio-checked { color: white; font-size: 12px; font-weight: bold; }

.type-icon-sm { font-size: 24px; }
.type-text h4 { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.type-text p { font-size: 12px; color: var(--text-muted); }

.btn-lg { padding: 16px 28px; font-size: 16px; }
.btn-icon { margin-right: 8px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }

.generate-tip { text-align: center; font-size: 13px; color: var(--text-muted); margin-top: 16px; }

.feature-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 40px; }

@media (max-width: 768px) {
  .hero { margin-bottom: 24px; padding-top: 0; }
  .hero-badge { font-size: 12px; padding: 5px 12px; margin-bottom: 12px; }
  .hero h2 { font-size: 1.5rem; line-height: 1.3; }
  .hero p { font-size: 0.95rem; }
  
  .type-cards { grid-template-columns: 1fr; }
  .type-card-inline { padding: 14px; }
  .type-icon-sm { font-size: 20px; }
  .type-text h4 { font-size: 13px; }
  .type-text p { font-size: 11px; }
  
  .feature-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 24px; }
  
  .search-toggle { padding: 16px; flex-direction: column; align-items: flex-start; gap: 12px; }
  .search-info { gap: 10px; }
  .search-icon { font-size: 24px; }
  .search-title { font-size: 14px; }
  .search-desc { font-size: 12px; }
  .toggle-switch { align-self: flex-end; }
  
  .source-options { gap: 8px; }
  .source-option { padding: 10px 14px; flex: 1; justify-content: center; }
  
  .link-input-group { flex-direction: column; gap: 8px; }
  .link-input-group .btn { width: 100%; }
  
  .file-upload { padding: 24px 16px; }
  .upload-icon { font-size: 32px; }
}

@media (max-width: 480px) {
  .hero h2 { font-size: 1.35rem; }
  
  .feature-grid { grid-template-columns: 1fr; }
  
  .source-option { font-size: 13px; }
  .source-icon { font-size: 14px; }
  
  .input-lg { font-size: 15px; padding: 14px 16px; }
  
  .btn-lg { padding: 14px 24px; font-size: 15px; }
  .generate-tip { font-size: 12px; }
}
</style>
