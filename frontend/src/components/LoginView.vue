<template>
  <div class="auth-container">
    <div class="auth-card glass-card">
      <div class="auth-header">
        <div class="auth-logo">
          <div class="logo-icon-box">
            <svg viewBox="0 0 24 24" fill="none" class="auth-logo-svg">
              <path d="M12 2L2 7l10 5 10-5-10-5z" fill="url(#grad1)"/>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="url(#grad2)" stroke-width="2" fill="none"/>
              <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#6366F1"/><stop offset="100%" style="stop-color:#8B5CF6"/>
                </linearGradient>
                <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#818CF8"/><stop offset="100%" style="stop-color:#A78BFA"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
        <h1>AI Tools</h1>
        <p>登录您的账户</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="username" type="text" class="input-field" placeholder="请输入用户名" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" class="input-field" placeholder="请输入密码" required />
        </div>
        <div v-if="error" class="auth-error">{{ error }}</div>
        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <div class="auth-footer">
        <p>还没有账户？<a @click="$emit('register')">立即注册</a></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['login', 'register'])

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!username.value || !password.value) { error.value = '请填写完整信息'; return }
  loading.value = true; error.value = ''
  try {
    const res = await axios.post('/api/auth/login', { username: username.value, password: password.value })
    if (res.data.success) emit('login', res.data.user)
    else error.value = res.data.message || '登录失败'
  } catch (e) { error.value = e.response?.data?.detail || '登录失败' }
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
  .auth-container { padding: 16px; align-items: flex-start; padding-top: calc(60px + env(safe-area-inset-top, 0px)); }
  .auth-card { padding: 28px 20px; border-radius: var(--radius-lg); }
  .auth-header { margin-bottom: 28px; }
  .logo-icon-box { width: 56px; height: 56px; border-radius: 14px; }
  .auth-logo-svg { width: 36px; height: 36px; }
  .auth-header h1 { font-size: 1.5rem; }
  .auth-header p { font-size: 14px; }
  .form-group label { font-size: 13px; }
  .input-field { padding: 12px 14px; }
  .btn { padding: 14px 20px; }
}
</style>
