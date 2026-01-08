<template>
  <div class="view">
    <div class="view-header">
      <h2>📚 学习文档</h2>
      <div class="header-actions">
        <button v-if="selectedIds.length > 0" class="btn btn-danger btn-sm" @click="confirmBatchDelete">
          🗑️ 删除选中 ({{ selectedIds.length }})
        </button>
        <button class="btn btn-primary" @click="$emit('new')">+ 新建文档</button>
      </div>
    </div>
    
    <div class="content-list">
      <div v-if="documents.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p>暂无学习文档，点击上方按钮创建第一个</p>
      </div>
      
      <div v-for="doc in documents" :key="doc.id" :class="['content-card', { selected: selectedIds.includes(doc.id), expanded: expandedId === doc.id }]">
        <label class="checkbox-wrapper" @click.stop>
          <input type="checkbox" :checked="selectedIds.includes(doc.id)" @change="toggleSelect(doc.id)" />
          <span class="checkmark"></span>
        </label>
        <div class="card-content">
          <div class="card-header" @click="toggleExpand(doc.id)">
            <div class="card-info">
              <h3>{{ doc.title }}</h3>
              <p>{{ doc.description || '暂无描述' }}</p>
              <div class="content-meta">
                <span class="tag">学习文档</span>
                <span>📚 {{ doc.chapters?.length || 0 }} 章节</span>
                <span>📅 {{ formatDate(doc.created_at) }}</span>
              </div>
            </div>
            <span class="expand-icon">{{ expandedId === doc.id ? '▼' : '▶' }}</span>
          </div>
          
          <!-- 展开的文章列表 -->
          <div v-if="expandedId === doc.id" class="chapter-list">
            <div v-for="chapter in doc.chapters" :key="chapter.id" class="chapter-item" @click.stop="viewChapter(doc.id, chapter.id)">
              <span class="chapter-num">{{ chapter.id }}</span>
              <span class="chapter-title">{{ chapter.title }}</span>
              <span class="chapter-status" :class="chapter.status">{{ chapter.status === 'success' ? '✓' : '!' }}</span>
            </div>
          </div>
        </div>
        <div class="card-actions">
          <button class="btn-view" @click.stop="$emit('view', doc.id)">👁️</button>
          <button class="btn-delete" @click.stop="confirmDelete(doc)">🗑️</button>
        </div>
      </div>
    </div>
    
    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>⚠️ 确认删除</h3>
          <button class="modal-close" @click="showDeleteModal = false">✕</button>
        </div>
        <p class="modal-desc">{{ deleteMessage }}</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showDeleteModal = false">取消</button>
          <button class="btn btn-danger" @click="doDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const emit = defineEmits(['view', 'new', 'viewArticle'])

const documents = ref([])
const selectedIds = ref([])
const expandedId = ref(null)
const showDeleteModal = ref(false)
const deleteTarget = ref(null)
const isBatchDelete = ref(false)
const deleteMessage = ref('')

async function loadDocuments() {
  try {
    const res = await axios.get('/api/documents')
    documents.value = res.data.documents || []
  } catch (e) { console.error(e) }
}

function formatDate(str) {
  if (!str) return ''
  return new Date(str).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function toggleSelect(id) {
  const idx = selectedIds.value.indexOf(id)
  if (idx > -1) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function viewChapter(docId, chapterId) {
  emit('viewArticle', `${docId}-${chapterId}`)
}

function confirmDelete(doc) {
  deleteTarget.value = doc
  isBatchDelete.value = false
  deleteMessage.value = `确定要删除文档「${doc.title}」及其所有章节吗？此操作不可恢复。`
  showDeleteModal.value = true
}

function confirmBatchDelete() {
  isBatchDelete.value = true
  deleteMessage.value = `确定要删除选中的 ${selectedIds.value.length} 个文档及其所有章节吗？此操作不可恢复。`
  showDeleteModal.value = true
}

async function doDelete() {
  try {
    if (isBatchDelete.value) {
      await axios.post('/api/documents/batch-delete', { ids: selectedIds.value })
      selectedIds.value = []
    } else {
      await axios.delete(`/api/documents/${deleteTarget.value.id}`)
    }
    showDeleteModal.value = false
    loadDocuments()
  } catch (e) { alert('删除失败: ' + (e.response?.data?.detail || e.message)) }
}

onMounted(loadDocuments)
</script>

<style scoped>
.header-actions { display: flex; gap: 12px; }

.content-card { display: flex; align-items: flex-start; gap: 12px; }
.content-card.selected { border-color: var(--primary); background: var(--primary-bg); }
.content-card.expanded { padding-bottom: 0; }

.checkbox-wrapper { position: relative; width: 20px; height: 20px; flex-shrink: 0; margin-top: 4px; }
.checkbox-wrapper input { opacity: 0; width: 0; height: 0; }
.checkmark { position: absolute; top: 0; left: 0; width: 20px; height: 20px; background: var(--bg-main); border: 2px solid var(--border); border-radius: 4px; cursor: pointer; }
.checkbox-wrapper input:checked ~ .checkmark { background: var(--primary); border-color: var(--primary); }
.checkmark:after { content: ""; position: absolute; display: none; left: 6px; top: 2px; width: 5px; height: 10px; border: solid white; border-width: 0 2px 2px 0; transform: rotate(45deg); }
.checkbox-wrapper input:checked ~ .checkmark:after { display: block; }

.card-content { flex: 1; min-width: 0; }
.card-header { display: flex; align-items: flex-start; cursor: pointer; }
.card-info { flex: 1; }
.expand-icon { color: var(--text-muted); font-size: 12px; padding: 4px; }

.chapter-list { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
.chapter-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-main); border-radius: 8px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s; }
.chapter-item:hover { background: var(--primary-bg); }
.chapter-num { width: 28px; height: 28px; background: var(--primary); color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; }
.chapter-title { flex: 1; font-size: 14px; color: var(--text-primary); }
.chapter-status { font-size: 14px; }
.chapter-status.success { color: var(--success); }
.chapter-status.failed { color: var(--error); }

.card-actions { display: flex; gap: 8px; flex-shrink: 0; }
.card-actions button { padding: 8px; border-radius: 6px; border: none; cursor: pointer; font-size: 14px; }
.btn-view { background: var(--bg-main); color: var(--text-secondary); }
.btn-view:hover { background: var(--primary-bg); color: var(--primary); }
.btn-delete { background: #FEE2E2; color: var(--error); }
.btn-delete:hover { background: var(--error); color: white; }

@media (max-width: 768px) {
  .header-actions { flex-direction: column; width: 100%; }
  .header-actions .btn { width: 100%; }
}
</style>
