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
  // 完整清空表单
  topic.value = ''
  description.value = ''
  files.value = []
  links.value = []
  activeSource.value = null
  linkInput.value = ''
}
</script>

<style scoped>
/* 高端专业版样式 */
.view {
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Hero区域 */
.hero { 
  text-align: center; 
  margin-bottom: 48px; 
  padding-top: 24px;
  position: relative;
}

.hero::before {
  content: '';
  position: absolute;
  top: -100px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
  pointer-events: none;
  z-index: -1;
}

.hero-badge { 
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px; 
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)); 
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 24px; 
  font-size: 13px; 
  font-weight: 600; 
  color: #6366f1; 
  margin-bottom: 20px;
  backdrop-filter: blur(8px);
}

.hero h2 { 
  font-size: 2.75rem; 
  font-weight: 800; 
  margin-bottom: 16px; 
  background: linear-gradient(135deg, #1e293b 0%, #6366f1 50%, #a855f7 100%); 
  -webkit-background-clip: text; 
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.03em;
  line-height: 1.2;
}

.hero p { 
  color: #64748b; 
  font-size: 1.15rem;
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.6;
}

/* 生成卡片 */
.generate-card { 
  position: relative; 
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.generate-card::before { 
  content: ''; 
  position: absolute; 
  top: 0; 
  right: 0; 
  width: 300px; 
  height: 300px; 
  background: radial-gradient(circle, rgba(99, 102, 241, 0.06) 0%, transparent 70%); 
  pointer-events: none; 
}

.generate-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.04) 0%, transparent 70%);
  pointer-events: none;
}

.input-lg { 
  font-size: 16px; 
  padding: 16px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: #f8fafc;
}

.input-lg:focus {
  border-color: #6366f1;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

/* 资料来源选项 */
.source-options { 
  display: flex; 
  gap: 12px; 
  margin-bottom: 16px; 
  flex-wrap: wrap; 
}

.source-option { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  padding: 12px 20px; 
  background: #ffffff; 
  border: 2px solid #e2e8f0; 
  border-radius: 12px; 
  cursor: pointer; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.source-option:hover { 
  border-color: #a5b4fc; 
  background: #f5f3ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.source-option.active { 
  border-color: #6366f1; 
  background: linear-gradient(135deg, #eef2ff, #f5f3ff);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.source-icon { font-size: 18px; }
.source-label { color: #334155; font-weight: 600; }

.source-input { 
  margin-top: 16px; 
  animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
}

@keyframes slideDown { 
  from { opacity: 0; transform: translateY(-10px); } 
  to { opacity: 1; transform: translateY(0); } 
}

/* 文件上传 */
.file-upload { 
  border: 2px dashed #cbd5e1; 
  border-radius: 16px; 
  padding: 40px 32px; 
  text-align: center; 
  cursor: pointer; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
}

.file-upload:hover { 
  border-color: #6366f1; 
  background: linear-gradient(135deg, #eef2ff, #f5f3ff);
  transform: scale(1.01);
}

.upload-icon { font-size: 48px; margin-bottom: 16px; }
.file-upload p { color: #334155; margin-bottom: 8px; font-size: 16px; font-weight: 600; }
.upload-hint { font-size: 13px; color: #94a3b8; }

.file-list, .link-list { margin-top: 16px; display: flex; flex-direction: column; gap: 10px; }

.file-item, .link-item { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  padding: 14px 16px; 
  background: #ffffff; 
  border: 1px solid #e2e8f0; 
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.file-item:hover, .link-item:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.file-item span, .link-url { flex: 1; font-size: 14px; color: #475569; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.file-item button, .link-item button { 
  background: #fef2f2; 
  border: none; 
  color: #ef4444; 
  font-size: 16px; 
  cursor: pointer;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.file-item button:hover, .link-item button:hover {
  background: #ef4444;
  color: #ffffff;
}

.link-input-group { display: flex; gap: 12px; }
.link-input-group .input-field { flex: 1; }
.link-icon { font-size: 16px; }

/* 联网搜索开关 */
.search-toggle { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  padding: 24px; 
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); 
  border: 2px solid #a7f3d0; 
  border-radius: 16px; 
  gap: 20px;
  transition: all 0.3s;
}

.search-toggle:hover {
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.15);
}

.search-info { display: flex; align-items: center; gap: 16px; flex: 1; }
.search-icon { font-size: 36px; }
.search-title { font-size: 16px; font-weight: 700; color: #065f46; margin-bottom: 4px; }
.search-desc { font-size: 13px; color: #047857; }

.toggle-switch { position: relative; width: 56px; height: 30px; flex-shrink: 0; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }

.toggle-slider { 
  position: absolute; 
  cursor: pointer; 
  top: 0; left: 0; right: 0; bottom: 0; 
  background: #cbd5e1; 
  border-radius: 30px; 
  transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
}

.toggle-slider:before { 
  position: absolute; 
  content: ""; 
  height: 24px; 
  width: 24px; 
  left: 3px; 
  bottom: 3px; 
  background: white; 
  border-radius: 50%; 
  transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15); 
}

.toggle-switch input:checked + .toggle-slider { background: linear-gradient(135deg, #10b981, #059669); }
.toggle-switch input:checked + .toggle-slider:before { transform: translateX(26px); }

/* 生成类型选择 */
.generate-type-section { margin-bottom: 28px; }
.generate-type-section > label { 
  display: block; 
  font-size: 15px; 
  font-weight: 700; 
  color: #1e293b; 
  margin-bottom: 14px; 
}

.type-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }

.type-card-inline {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  background: #ffffff;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.type-card-inline:hover { 
  border-color: #a5b4fc;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
}

.type-card-inline.active { 
  border-color: #6366f1; 
  background: linear-gradient(135deg, #eef2ff, #f5f3ff);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
}

.type-radio {
  width: 24px; height: 24px;
  border: 2px solid #cbd5e1;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.type-card-inline.active .type-radio { 
  border-color: #6366f1; 
  background: linear-gradient(135deg, #6366f1, #8b5cf6); 
}

.radio-checked { color: white; font-size: 12px; font-weight: bold; }

.type-icon-sm { font-size: 28px; }
.type-text h4 { font-size: 15px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.type-text p { font-size: 13px; color: #64748b; }

/* 按钮样式 */
.btn-lg { 
  padding: 18px 32px; 
  font-size: 16px;
  font-weight: 700;
  border-radius: 14px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-lg:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.5);
}

.btn-icon { margin-right: 10px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }

.generate-tip { 
  text-align: center; 
  font-size: 13px; 
  color: #94a3b8; 
  margin-top: 20px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

/* 特性网格 */
.feature-grid { 
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  gap: 20px; 
  margin-top: 48px; 
}

.feature-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e1;
}

.feature-icon {
  font-size: 36px;
  margin-bottom: 14px;
  display: block;
}

.feature-card h3 {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.feature-card p {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}

/* 响应式 - 平板 */
@media (max-width: 768px) {
  .hero { margin-bottom: 32px; padding-top: 16px; }
  .hero::before { width: 300px; height: 300px; }
  .hero-badge { font-size: 12px; padding: 6px 14px; margin-bottom: 14px; }
  .hero h2 { font-size: 1.75rem; line-height: 1.3; }
  .hero p { font-size: 1rem; }
  
  .generate-card { padding: 24px; border-radius: 16px; }
  
  .type-cards { grid-template-columns: 1fr; }
  .type-card-inline { padding: 16px; }
  .type-icon-sm { font-size: 24px; }
  .type-text h4 { font-size: 14px; }
  .type-text p { font-size: 12px; }
  
  .feature-grid { grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 32px; }
  .feature-card { padding: 20px; }
  .feature-icon { font-size: 30px; margin-bottom: 12px; }
  .feature-card h3 { font-size: 14px; }
  .feature-card p { font-size: 12px; }
  
  .search-toggle { padding: 18px; flex-direction: column; align-items: flex-start; gap: 14px; }
  .search-info { gap: 12px; }
  .search-icon { font-size: 28px; }
  .search-title { font-size: 15px; }
  .search-desc { font-size: 12px; }
  .toggle-switch { align-self: flex-end; }
  
  .source-options { gap: 10px; }
  .source-option { padding: 12px 16px; flex: 1; justify-content: center; }
  
  .link-input-group { flex-direction: column; gap: 10px; }
  .link-input-group .btn { width: 100%; }
  
  .file-upload { padding: 28px 20px; }
  .upload-icon { font-size: 36px; }
}

/* 响应式 - 手机 */
@media (max-width: 480px) {
  .hero h2 { font-size: 1.5rem; }
  .hero p { font-size: 0.95rem; }
  
  .generate-card { padding: 20px; }
  
  .feature-grid { grid-template-columns: 1fr; gap: 12px; }
  .feature-card { 
    padding: 18px; 
    display: flex;
    align-items: center;
    text-align: left;
    gap: 14px;
  }
  .feature-icon { font-size: 28px; margin-bottom: 0; flex-shrink: 0; }
  .feature-card h3 { margin-bottom: 4px; }
  
  .source-option { font-size: 13px; padding: 10px 14px; }
  .source-icon { font-size: 16px; }
  
  .input-lg { font-size: 15px; padding: 14px 16px; border-radius: 12px; }
  
  .btn-lg { padding: 16px 24px; font-size: 15px; border-radius: 12px; }
  .generate-tip { font-size: 12px; padding: 10px; }
  
  .type-card-inline { padding: 14px; gap: 12px; }
  .type-radio { width: 22px; height: 22px; }
  
  .file-upload { padding: 24px 16px; border-radius: 14px; }
  .upload-icon { font-size: 32px; margin-bottom: 12px; }
  .file-upload p { font-size: 14px; }
  
  .search-toggle { padding: 16px; border-radius: 14px; }
  .search-icon { font-size: 24px; }
  .search-title { font-size: 14px; }
}
</style>
