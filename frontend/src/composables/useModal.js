import { ref, createApp, h } from 'vue'
import GlobalModal from '../components/GlobalModal.vue'

let modalContainer = null

function ensureContainer() {
  if (!modalContainer) {
    modalContainer = document.createElement('div')
    modalContainer.id = 'global-modal-container'
    document.body.appendChild(modalContainer)
  }
  return modalContainer
}

function showModal(options) {
  return new Promise((resolve) => {
    const container = ensureContainer()
    const wrapper = document.createElement('div')
    container.appendChild(wrapper)

    const visible = ref(true)

    const app = createApp({
      render() {
        return h(GlobalModal, {
          visible: visible.value,
          'onUpdate:visible': (val) => {
            visible.value = val
            if (!val) {
              setTimeout(() => {
                app.unmount()
                wrapper.remove()
              }, 200)
            }
          },
          type: options.type || 'info',
          title: options.title || '',
          message: options.message || '',
          showInput: options.showInput || false,
          inputPlaceholder: options.inputPlaceholder || '',
          inputDefault: options.inputDefault || '',
          showCancel: options.showCancel || false,
          confirmText: options.confirmText || '确定',
          cancelText: options.cancelText || '取消',
          closeOnOverlay: options.closeOnOverlay !== false,
          onConfirm: (value) => {
            resolve({ confirmed: true, value })
          },
          onCancel: () => {
            resolve({ confirmed: false, value: null })
          }
        })
      }
    })

    app.mount(wrapper)
  })
}

export function useModal() {
  const alert = (message, title = '提示') => {
    return showModal({
      type: 'info',
      title,
      message,
      showCancel: false,
      confirmText: '确定'
    })
  }

  const success = (message, title = '成功') => {
    return showModal({
      type: 'success',
      title,
      message,
      showCancel: false,
      confirmText: '确定'
    })
  }

  const error = (message, title = '错误') => {
    return showModal({
      type: 'error',
      title,
      message,
      showCancel: false,
      confirmText: '确定'
    })
  }

  const warning = (message, title = '警告') => {
    return showModal({
      type: 'warning',
      title,
      message,
      showCancel: false,
      confirmText: '确定'
    })
  }

  const confirm = (message, title = '确认') => {
    return showModal({
      type: 'confirm',
      title,
      message,
      showCancel: true,
      confirmText: '确定',
      cancelText: '取消',
      closeOnOverlay: false
    }).then(res => res.confirmed)
  }

  const prompt = (message, defaultValue = '', title = '请输入') => {
    return showModal({
      type: 'info',
      title,
      message,
      showInput: true,
      inputDefault: defaultValue,
      inputPlaceholder: '请输入...',
      showCancel: true,
      confirmText: '确定',
      cancelText: '取消',
      closeOnOverlay: false
    }).then(res => res.confirmed ? res.value : null)
  }

  return {
    alert,
    success,
    error,
    warning,
    confirm,
    prompt,
    showModal
  }
}

// 全局单例
let modalInstance = null

export function getModal() {
  if (!modalInstance) {
    modalInstance = useModal()
  }
  return modalInstance
}

export default useModal
