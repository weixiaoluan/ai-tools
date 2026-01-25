<template>
  <div class="view">
    <div class="view-header">
      <h2>📝 文章列表</h2>
      <div class="header-actions">
        <button v-if="selectedIds.length > 0" class="btn btn-danger btn-sm" @click="confirmBatchDelete">
          🗑️ 删除选中 ({{ selectedIds.length }})
        </button>
        <button class="btn btn-primary" @click="$emit('new')">+ 新建文章</button>
      </div>
    </div>
    
    <div class="content-list">
      <div v-if="articles.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p>暂无文章，点击上方按钮创建第一篇</p>
      </div>
      
      <div v-for="article in articles" :key="article.id" :class="['content-card', { selected: selectedIds.includes(article.id), loading: clickLoading === article.id }]">
        <label class="checkbox-wrapper" @click.stop>
          <input type="checkbox" :checked="selectedIds.includes(article.id)" @change="toggleSelect(article.id)" />
          <span class="checkmark"></span>
        </label>
        <div class="card-content" @click="handleClick(article.id)">
          <h3>{{ article.title }}</h3>
          <p>{{ article.topic || '暂无描述' }}</p>
          <div class="content-meta">
            <span class="tag">{{ article.type === 'chapter' ? '章节' : '文章' }}</span>
            <span>📅 {{ formatDate(article.created_at) }}</span>
          </div>
        </div>
        <div class="card-actions">
          <button class="btn-edit" @click.stop="openEdit(article)">✏️</button>
          <button class="btn-delete" @click.stop="confirmDelete(article)">🗑️</button>
        </div>
      </div>
    </div>
    
    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>✏️ 编辑文章</h3>
          <button class="modal-close" @click="showEditModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>文章标题</label>
            <input v-model="editForm.title" class="input-field" placeholder="输入标题" />
          </div>
          <div class="form-group">
            <label>文章内容 (Markdown)</label>
            <textarea v-model="editForm.content" class="input-field" rows="15"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showEditModal = false">取消</button>
          <button class="btn btn-primary" @click="saveEdit">保存修改</button>
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
const clickLoading = ref(null)

function handleClick(id) {
  clickLoading.value = id
  emit('view', id)
}

const props = defineProps(['view', 'new'])

const emit = defineEmits(['view', 'new'])

// 点击加载状态

const articles = ref([])
const selectedIds = ref([])
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const editForm = ref({ id: '', title: '', content: '' })
const deleteTarget = ref(null)
const isBatchDelete = ref(false)
const deleteMessage = ref('')

async function loadArticles() {
  try {
    const res = await axios.get('/api/articles')
    articles.value = res.data.articles || []
  } catch (e) { console.error(e) }
}

function formatDate(str) {
  if (!str) return ''
  // 处理ISO格式时间，确保正确解析为本地时间
  const date = new Date(str)
  if (isNaN(date.getTime())) return str
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}/${month}/${day} ${hour}:${minute}`
}

function toggleSelect(id) {
  const idx = selectedIds.value.indexOf(id)
  if (idx > -1) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

function openEdit(article) {
  editForm.value = { id: article.id, title: article.title, content: article.content || '' }
  showEditModal.value = true
}

async function saveEdit() {
  try {
    await axios.put(`/api/articles/${editForm.value.id}`, { title: editForm.value.title, content: editForm.value.content })
    showEditModal.value = false
    loadArticles()
  } catch (e) { modal.error('保存失败: ' + (e.response?.data?.detail || e.message)) }
}

function confirmDelete(article) {
  deleteTarget.value = article
  isBatchDelete.value = false
  deleteMessage.value = `确定要删除文章「${article.title}」吗？此操作不可恢复。`
  showDeleteModal.value = true
}

function confirmBatchDelete() {
  isBatchDelete.value = true
  deleteMessage.value = `确定要删除选中的 ${selectedIds.value.length} 篇文章吗？此操作不可恢复。`
  showDeleteModal.value = true
}

async function doDelete() {
  try {
    if (isBatchDelete.value) {
      await axios.post('/api/articles/batch-delete', { ids: selectedIds.value })
      selectedIds.value = []
    } else {
      await axios.delete(`/api/articles/${deleteTarget.value.id}`)
    }
    showDeleteModal.value = false
    loadArticles()
  } catch (e) { modal.error('删除失败: ' + (e.response?.data?.detail || e.message)) }
}

onMounted(loadArticles)
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
  transform: translateY(-2px);
}

.content-card.selected { 
  border-color: #6366f1; 
  background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.15);
}

.content-card.loading {
  opacity: 0.7;
  pointer-events: none;
  position: relative;
}

.content-card.loading::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 24px;
  height: 24px;
  margin: -12px 0 0 -12px;
  border: 3px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  z-index: 10;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
.card-content { 
  flex: 1; 
  min-width: 0; 
  cursor: pointer; 
}

.card-content h3 {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
  transition: color 0.2s;
  text-decoration: none !important;
  text-decoration-line: none !important;
  text-decoration-style: none !important;
  border: none !important;
  border-bottom: none !important;
  box-shadow: none !important;
  background-image: none !important;
  background: transparent !important;
  -webkit-text-decoration: none !important;
  -webkit-text-decoration-line: none !important;
  outline: none !important;
  text-underline-offset: 0 !important;
  text-decoration-skip-ink: none !important;
}

.content-card:hover .card-content h3 {
  color: #6366f1;
}

.card-content p {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.content-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #94a3b8;
}

.tag {
  padding: 4px 10px;
  background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
  color: #6366f1;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

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

.btn-edit { 
  background: #eef2ff; 
  color: #6366f1; 
}

.btn-edit:hover { 
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
  
  .card-content h3 {
    font-size: 15px;
    text-decoration: none !important;
    border: none !important;
    border-bottom: none !important;
    box-shadow: none !important;
    background-image: none !important;
  }
  
  .card-content p {
    font-size: 13px;
    margin-bottom: 10px;
  }
  
  .content-meta {
    flex-wrap: wrap;
    gap: 8px;
    font-size: 12px;
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
}
</style>
