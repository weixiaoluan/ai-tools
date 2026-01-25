<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="global-modal-overlay" @click.self="handleOverlayClick">
        <div class="global-modal" :class="modalClass">
          <!-- 标题栏 -->
          <div class="global-modal-header" v-if="title">
            <div class="global-modal-icon" :class="iconClass">
              <svg v-if="type === 'success'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              <svg v-else-if="type === 'error'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
              <svg v-else-if="type === 'warning' || type === 'confirm'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
            </div>
            <h3 class="global-modal-title">{{ title }}</h3>
          </div>
          
          <!-- 内容 -->
          <div class="global-modal-body">
            <p v-if="message" class="global-modal-message">{{ message }}</p>
            <input 
              v-if="showInput" 
              ref="inputRef"
              v-model="inputValue" 
              class="global-modal-input" 
              :placeholder="inputPlaceholder"
              @keyup.enter="handleConfirm"
            />
          </div>
          
          <!-- 按钮 -->
          <div class="global-modal-footer">
            <button v-if="showCancel" class="global-modal-btn global-modal-btn-cancel" @click="handleCancel">
              {{ cancelText }}
            </button>
            <button class="global-modal-btn global-modal-btn-confirm" :class="confirmBtnClass" @click="handleConfirm">
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  type: { type: String, default: 'info' }, // info, success, error, warning, confirm
  title: { type: String, default: '' },
  message: { type: String, default: '' },
  showInput: { type: Boolean, default: false },
  inputPlaceholder: { type: String, default: '' },
  inputDefault: { type: String, default: '' },
  showCancel: { type: Boolean, default: false },
  confirmText: { type: String, default: '确定' },
  cancelText: { type: String, default: '取消' },
  closeOnOverlay: { type: Boolean, default: true }
})

const emit = defineEmits(['confirm', 'cancel', 'update:visible'])

const inputValue = ref('')
const inputRef = ref(null)

const modalClass = computed(() => `global-modal-${props.type}`)
const iconClass = computed(() => `icon-${props.type}`)
const confirmBtnClass = computed(() => {
  if (props.type === 'error' || props.type === 'warning' || props.type === 'confirm') {
    return 'btn-danger'
  }
  return ''
})

watch(() => props.visible, (val) => {
  if (val) {
    inputValue.value = props.inputDefault
    if (props.showInput) {
      nextTick(() => inputRef.value?.focus())
    }
  }
})

function handleConfirm() {
  emit('confirm', inputValue.value)
  emit('update:visible', false)
}

function handleCancel() {
  emit('cancel')
  emit('update:visible', false)
}

function handleOverlayClick() {
  if (props.closeOnOverlay && !props.showCancel) {
    handleConfirm()
  }
}
</script>

<style scoped>
.global-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.global-modal {
  background: var(--bg-white, #fff);
  border-radius: var(--radius-lg, 16px);
  box-shadow: var(--shadow-xl, 0 20px 25px -5px rgba(0,0,0,0.1));
  width: 100%;
  max-width: 400px;
  overflow: hidden;
  animation: modal-scale 0.2s ease;
}

@keyframes modal-scale {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.global-modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px 0;
}

.global-modal-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.global-modal-icon.icon-info {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary, #6366F1);
}

.global-modal-icon.icon-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success, #10B981);
}

.global-modal-icon.icon-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error, #EF4444);
}

.global-modal-icon.icon-warning,
.global-modal-icon.icon-confirm {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning, #F59E0B);
}

.global-modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #0F172A);
  margin: 0;
}

.global-modal-body {
  padding: 16px 24px 20px;
}

.global-modal-message {
  font-size: 14px;
  color: var(--text-secondary, #475569);
  line-height: 1.6;
  margin: 0;
  word-break: break-word;
}

.global-modal-input {
  width: 100%;
  margin-top: 16px;
  padding: 12px 16px;
  border: 1px solid var(--border, #E2E8F0);
  border-radius: var(--radius-sm, 8px);
  font-size: 14px;
  color: var(--text-primary, #0F172A);
  background: var(--bg-main, #F8FAFC);
  transition: all 0.2s;
}

.global-modal-input:focus {
  outline: none;
  border-color: var(--primary, #6366F1);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.global-modal-footer {
  display: flex;
  gap: 12px;
  padding: 0 24px 20px;
  justify-content: flex-end;
}

.global-modal-btn {
  padding: 10px 20px;
  border-radius: var(--radius-sm, 8px);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.global-modal-btn-cancel {
  background: var(--bg-main, #F8FAFC);
  color: var(--text-secondary, #475569);
  border: 1px solid var(--border, #E2E8F0);
}

.global-modal-btn-cancel:hover {
  background: var(--border-light, #F1F5F9);
}

.global-modal-btn-confirm {
  background: linear-gradient(135deg, var(--primary, #6366F1), var(--primary-dark, #4F46E5));
  color: #fff;
}

.global-modal-btn-confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.global-modal-btn-confirm.btn-danger {
  background: linear-gradient(135deg, var(--error, #EF4444), #DC2626);
}

.global-modal-btn-confirm.btn-danger:hover {
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

/* 动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .global-modal {
    max-width: calc(100% - 40px);
  }
  
  .global-modal-footer {
    flex-direction: column-reverse;
  }
  
  .global-modal-btn {
    width: 100%;
    padding: 12px;
  }
}
</style>
