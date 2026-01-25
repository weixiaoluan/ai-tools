<template>
  <div class="auth-container">
    <div class="auth-card glass-card">
      <div class="auth-header">
        <div class="auth-logo">
          <div class="logo-icon-box">
            <svg viewBox="0 0 24 24" fill="none" class="auth-logo-svg">
              <path d="M12 2L2 7l10 5 10-5-10-5z" fill="url(#rgrad1)"/>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="url(#rgrad2)" stroke-width="2" fill="none"/>
              <defs>
                <linearGradient id="rgrad1" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#6366F1"/><stop offset="100%" style="stop-color:#8B5CF6"/>
                </linearGradient>
                <linearGradient id="rgrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#818CF8"/><stop offset="100%" style="stop-color:#A78BFA"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
        <h1>AI Tools</h1>
        <p>创建新账户</p>
      </div>
      
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="username" type="text" class="input-field" placeholder="请输入用户名" required />
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="email" type="email" class="input-field" placeholder="请输入邮箱" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" class="input-field" placeholder="请输入密码（至少6位）" required />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input v-model="confirmPassword" type="password" class="input-field" placeholder="请再次输入密码" required />
        </div>
        <div v-if="error" class="auth-error">{{ error }}</div>
        <div v-if="success" class="auth-success">{{ success }}</div>
        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="auth-footer">
        <p>已有账户？<a @click="$emit('login')">立即登录</a></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['registered', 'login'])

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleRegister() {
  error.value = ''; success.value = ''
  
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = '请填写完整信息'; return
  }
  if (password.value !== confirmPassword.value) {
    error.value = '两次密码输入不一致'; return
  }
  if (password.value.length < 6) {
    error.value = '密码至少6位'; return
  }
  
  loading.value = true
  try {
    const res = await axios.post('/api/auth/register', {
      username: username.value,
      email: email.value,
      password: password.value
    })
    if (res.data.success) {
      success.value = '注册成功，即将跳转登录...'
      setTimeout(() => emit('registered'), 1500)
    } else {
      error.value = res.data.message || '注册失败'
    }
  } catch (e) {
    if (e.code === 'ERR_NETWORK' || !e.response) {
      error.value = '网络连接失败，请检查后端服务是否启动'
    } else if (e.response?.status === 500) {
      error.value = '服务器错误：数据库可能未连接，请联系管理员'
    } else if (e.response?.status === 400) {
      error.value = e.response?.data?.detail || '用户名已存在或信息不合法'
    } else {
      error.value = e.response?.data?.detail || e.response?.data?.message || '注册失败，请稍后重试'
    }
  }
  loading.value = false
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 48px;
}

.auth-header {
  text-align: center;
  margin-bottom: 36px;
}

.auth-logo { margin-bottom: 20px; }

.logo-icon-box {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, var(--primary-bg), rgba(139, 92, 246, 0.1));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.auth-logo-svg { width: 40px; height: 40px; }

.auth-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.auth-header p { color: var(--text-secondary); }

.auth-form { margin-bottom: 24px; }

.auth-error {
  background: #FEE2E2;
  color: #991B1B;
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  margin-bottom: 16px;
  border: 1px solid #FECACA;
}

.auth-success {
  background: #D1FAE5;
  color: #065F46;
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  margin-bottom: 16px;
  border: 1px solid #A7F3D0;
}

.auth-footer {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
}

.auth-footer a {
  color: var(--primary);
  cursor: pointer;
  font-weight: 500;
}

.auth-footer a:hover { text-decoration: underline; }

@media (max-width: 480px) {
  .auth-card { padding: 32px 24px; }
  .auth-header h1 { font-size: 1.5rem; }
}
</style>
