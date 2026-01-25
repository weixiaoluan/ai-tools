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
      <div class="modal-content modal-delete">
        <div class="modal-header">
          <h3>⚠️ 确认删除</h3>
          <button class="modal-close" @click="showDeleteModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="delete-warning">
            <div class="warning-icon">🗑️</div>
            <p class="warning-text">{{ deleteMessage }}</p>
          </div>
        </div>
        <div class="modal-footer">
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
import { useModal } from '../composables/useModal'

const modal = useModal()
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
  } catch (e) { modal.error('删除失败: ' + (e.response?.data?.detail || e.message)) }
}

onMounted(loadDocuments)
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

.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f5f9;
}

.view-header h2 {
  font-size: 1.75rem;
  font-weight: 800;
  background: linear-gradient(135deg, #1e293b 0%, #6366f1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
}

.header-actions { 
  display: flex; 
  gap: 12px; 
}

.header-actions .btn {
  padding: 12px 20px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-actions .btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.header-actions .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

.header-actions .btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* 内容列表 */
.content-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 20px;
  border: 2px dashed #e2e8f0;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.8;
}

.empty-state p {
  color: #64748b;
  font-size: 15px;
}

/* 内容卡片 */
.content-card { 
  display: flex; 
  align-items: flex-start; 
  gap: 16px;
  padding: 20px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.content-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.content-card.selected { 
  border-color: #6366f1; 
  background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.15);
}

.content-card.expanded { 
  padding-bottom: 0; 
}

/* 复选框 */
.checkbox-wrapper { 
  position: relative; 
  width: 22px; 
  height: 22px; 
  flex-shrink: 0; 
  margin-top: 2px; 
}

.checkbox-wrapper input { opacity: 0; width: 0; height: 0; }

.checkmark { 
  position: absolute; 
  top: 0; left: 0; 
  width: 22px; height: 22px; 
  background: #ffffff; 
  border: 2px solid #cbd5e1; 
  border-radius: 6px; 
  cursor: pointer;
  transition: all 0.2s;
}

.checkmark:hover {
  border-color: #6366f1;
}

.checkbox-wrapper input:checked ~ .checkmark { 
  background: linear-gradient(135deg, #6366f1, #8b5cf6); 
  border-color: #6366f1; 
}

.checkmark:after { 
  content: ""; 
  position: absolute; 
  display: none; 
  left: 7px; top: 3px; 
  width: 5px; height: 10px; 
  border: solid white; 
  border-width: 0 2px 2px 0; 
  transform: rotate(45deg); 
}

.checkbox-wrapper input:checked ~ .checkmark:after { display: block; }

/* 卡片内容 */
.card-content { flex: 1; min-width: 0; }

.card-header { 
  display: flex; 
  align-items: flex-start; 
  cursor: pointer;
  padding: 4px 0;
}

.card-info { flex: 1; }

.card-info h3 {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
  transition: color 0.2s;
}

.content-card:hover .card-info h3 {
  color: #6366f1;
}

.card-info p {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.5;
}

.content-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #94a3b8;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  color: #059669;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.expand-icon { 
  color: #94a3b8; 
  font-size: 12px; 
  padding: 6px 8px;
  background: #f1f5f9;
  border-radius: 6px;
  transition: all 0.2s;
}

.content-card:hover .expand-icon {
  background: #e2e8f0;
  color: #6366f1;
}

/* 章节列表 */
.chapter-list { 
  margin-top: 20px; 
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  margin-bottom: 20px;
}

.chapter-item { 
  display: flex; 
  align-items: center; 
  gap: 14px; 
  padding: 14px 16px; 
  background: #ffffff; 
  border: 1px solid #e2e8f0;
  border-radius: 10px; 
  margin-bottom: 10px; 
  cursor: pointer; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.chapter-item:last-child {
  margin-bottom: 0;
}

.chapter-item:hover { 
  border-color: #a5b4fc;
  background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.chapter-num { 
  width: 32px; height: 32px; 
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); 
  color: white; 
  border-radius: 8px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-size: 13px; 
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.chapter-title { 
  flex: 1; 
  font-size: 14px; 
  font-weight: 600;
  color: #334155; 
}

.chapter-status { font-size: 16px; }
.chapter-status.success { color: #10b981; }
.chapter-status.failed { color: #ef4444; }

/* 操作按钮 */
.card-actions { 
  display: flex; 
  gap: 8px; 
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.content-card:hover .card-actions {
  opacity: 1;
}

.card-actions button { 
  padding: 10px; 
  border-radius: 10px; 
  border: none; 
  cursor: pointer; 
  font-size: 14px;
  transition: all 0.2s;
}

.btn-view { 
  background: #f1f5f9; 
  color: #64748b; 
}

.btn-view:hover { 
  background: linear-gradient(135deg, #6366f1, #8b5cf6); 
  color: white;
  transform: scale(1.05);
}

.btn-delete { 
  background: #fef2f2; 
  color: #ef4444; 
}

.btn-delete:hover { 
  background: linear-gradient(135deg, #ef4444, #dc2626); 
  color: white;
  transform: scale(1.05);
}

/* 删除确认弹窗 */
.modal-delete {
  max-width: 420px;
}

.delete-warning {
  text-align: center;
  padding: 20px;
}

.warning-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.warning-text {
  font-size: 15px;
  color: #475569;
  line-height: 1.6;
}

/* 响应式 - 平板 */
@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .view-header h2 {
    font-size: 1.5rem;
  }
  
  .header-actions { 
    flex-direction: column; 
    width: 100%; 
  }
  
  .header-actions .btn { 
    width: 100%;
    justify-content: center;
  }
  
  .content-card {
    padding: 16px;
    gap: 12px;
  }
  
  .card-actions {
    opacity: 1;
  }
  
  .card-info h3 {
    font-size: 15px;
  }
  
  .card-info p {
    font-size: 13px;
    margin-bottom: 10px;
  }
  
  .content-meta {
    gap: 8px;
    font-size: 12px;
  }
  
  .chapter-list {
    padding: 14px;
    margin-top: 16px;
  }
  
  .chapter-item {
    padding: 12px;
    gap: 10px;
  }
  
  .chapter-num {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
  
  .chapter-title {
    font-size: 13px;
  }
  
  .empty-state {
    padding: 40px 16px;
  }
  
  .empty-icon {
    font-size: 48px;
  }
}

/* 响应式 - 手机 */
@media (max-width: 480px) {
  .content-card {
    padding: 14px;
    flex-wrap: wrap;
  }
  
  .checkbox-wrapper {
    width: 20px;
    height: 20px;
  }
  
  .checkmark {
    width: 20px;
    height: 20px;
  }
  
  .checkmark:after {
    left: 6px;
    top: 2px;
  }
  
  .card-content {
    width: calc(100% - 36px);
  }
  
  .card-actions {
    width: 100%;
    justify-content: flex-end;
    margin-top: 8px;
    padding-top: 12px;
    border-top: 1px solid #f1f5f9;
  }
  
  .card-actions button {
    padding: 8px 16px;
  }
  
  .tag {
    padding: 3px 8px;
    font-size: 11px;
  }
  
  .expand-icon {
    padding: 4px 6px;
    font-size: 10px;
  }
  
  .chapter-list {
    padding: 12px;
    margin-top: 14px;
    margin-bottom: 14px;
  }
  
  .chapter-item {
    padding: 10px 12px;
  }
  
  .chapter-num {
    width: 26px;
    height: 26px;
    font-size: 11px;
  }
}
</style>
