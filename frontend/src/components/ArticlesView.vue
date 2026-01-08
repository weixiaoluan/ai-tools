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
      
      <div v-for="article in articles" :key="article.id" :class="['content-card', { selected: selectedIds.includes(article.id) }]">
        <label class="checkbox-wrapper" @click.stop>
          <input type="checkbox" :checked="selectedIds.includes(article.id)" @change="toggleSelect(article.id)" />
          <span class="checkmark"></span>
        </label>
        <div class="card-content" @click="$emit('view', article.id)">
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
      <div class="modal-content">
        <div class="modal-header">
          <h3>⚠️ 确认删除</h3>
          <button class="modal-close" @click="showDeleteModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="modal-desc">{{ deleteMessage }}</p>
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

const emit = defineEmits(['view', 'new'])

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
  return new Date(str).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
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
  } catch (e) { alert('保存失败: ' + (e.response?.data?.detail || e.message)) }
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
  } catch (e) { alert('删除失败: ' + (e.response?.data?.detail || e.message)) }
}

onMounted(loadArticles)
</script>

<style scoped>
.header-actions { display: flex; gap: 12px; }

.content-card { display: flex; align-items: flex-start; gap: 12px; }
.content-card.selected { border-color: var(--primary); background: var(--primary-bg); }

.checkbox-wrapper { position: relative; width: 20px; height: 20px; flex-shrink: 0; margin-top: 4px; }
.checkbox-wrapper input { opacity: 0; width: 0; height: 0; }
.checkmark { position: absolute; top: 0; left: 0; width: 20px; height: 20px; background: var(--bg-main); border: 2px solid var(--border); border-radius: 4px; cursor: pointer; }
.checkbox-wrapper input:checked ~ .checkmark { background: var(--primary); border-color: var(--primary); }
.checkmark:after { content: ""; position: absolute; display: none; left: 6px; top: 2px; width: 5px; height: 10px; border: solid white; border-width: 0 2px 2px 0; transform: rotate(45deg); }
.checkbox-wrapper input:checked ~ .checkmark:after { display: block; }

.card-content { flex: 1; min-width: 0; cursor: pointer; }
.card-actions { display: flex; gap: 8px; flex-shrink: 0; }
.card-actions button { padding: 8px; border-radius: 6px; border: none; cursor: pointer; font-size: 14px; }
.btn-edit { background: var(--primary-bg); color: var(--primary); }
.btn-edit:hover { background: var(--primary); color: white; }
.btn-delete { background: #FEE2E2; color: var(--error); }
.btn-delete:hover { background: var(--error); color: white; }

@media (max-width: 768px) {
  .header-actions { flex-direction: column; width: 100%; }
  .header-actions .btn { width: 100%; }
}
</style>
