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
        
        <div class="agreement-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="agreeTerms" />
            <span class="checkmark"></span>
            <span class="agreement-text">我已阅读并同意 <a @click.prevent="showTerms = true">《用户服务协议》</a> 和 <a @click.prevent="showPrivacy = true">《隐私政策》</a></span>
          </label>
        </div>
        
        <div v-if="error" class="auth-error">{{ error }}</div>
        <button type="submit" class="btn btn-primary btn-block" :disabled="loading || !agreeTerms">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <div class="auth-footer">
        <p>还没有账户？<a @click="$emit('register')">立即注册</a></p>
      </div>
    </div>
    
    <!-- 用户协议弹窗 -->
    <div v-if="showTerms" class="modal-overlay" @click.self="showTerms = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>用户服务协议</h3>
          <button class="modal-close" @click="showTerms = false">✕</button>
        </div>
        <div class="modal-body terms-content">
          <h4>1. 服务条款</h4>
          <p>欢迎使用 AI Tools 平台。使用本服务即表示您同意遵守以下条款。</p>
          <h4>2. 账户安全</h4>
          <p>您有责任保护您的账户信息安全，不得将账户借给他人使用。</p>
          <h4>3. 使用规范</h4>
          <p>您同意不会使用本服务进行任何违法或不当行为，包括但不限于：发布违法内容、侵犯他人权益、干扰服务正常运行等。</p>
          <h4>4. 知识产权</h4>
          <p>本平台生成的内容仅供学习参考，您对使用生成内容的行为负责。</p>
          <h4>5. 免责声明</h4>
          <p>AI生成的内容可能存在错误或不准确之处，请自行核实。本平台不对内容的准确性承担责任。</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary btn-block" @click="showTerms = false; agreeTerms = true">我已阅读并同意</button>
        </div>
      </div>
    </div>
    
    <!-- 隐私政策弹窗 -->
    <div v-if="showPrivacy" class="modal-overlay" @click.self="showPrivacy = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>隐私政策</h3>
          <button class="modal-close" @click="showPrivacy = false">✕</button>
        </div>
        <div class="modal-body terms-content">
          <h4>1. 信息收集</h4>
          <p>我们收集您的用户名、邮箱等注册信息，以及使用服务时产生的数据。</p>
          <h4>2. 信息使用</h4>
          <p>收集的信息仅用于提供和改进服务，不会出售给第三方。</p>
          <h4>3. 信息保护</h4>
          <p>我们采取合理的安全措施保护您的个人信息。</p>
          <h4>4. Cookie使用</h4>
          <p>我们使用Cookie来保持您的登录状态和改善用户体验。</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary btn-block" @click="showPrivacy = false; agreeTerms = true">我已阅读并同意</button>
        </div>
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
const agreeTerms = ref(false)
const showTerms = ref(false)
const showPrivacy = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) { error.value = '请填写完整信息'; return }
  if (!agreeTerms.value) { error.value = '请先同意用户协议和隐私政策'; return }
  loading.value = true; error.value = ''
  try {
    const res = await axios.post('/api/auth/login', { username: username.value, password: password.value })
    if (res.data.success) {
      // 保存登录时间和过期时间（30天）
      const loginData = {
        ...res.data.user,
        loginTime: Date.now(),
        expireTime: Date.now() + 30 * 24 * 60 * 60 * 1000 // 30天
      }
      emit('login', loginData)
    }
    else error.value = res.data.message || '登录失败'
  } catch (e) { error.value = e.response?.data?.detail || '登录失败' }
  loading.value = false
}
</script>

<style scoped>
.auth-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%); }
.auth-card { width: 100%; max-width: 420px; padding: 48px; }
.auth-header { text-align: center; margin-bottom: 36px; }
.auth-logo { margin-bottom: 20px; }
.logo-icon-box { width: 64px; height: 64px; background: linear-gradient(135deg, var(--primary-bg), rgba(139, 92, 246, 0.1)); border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
.auth-logo-svg { width: 40px; height: 40px; }
.auth-header h1 { font-size: 1.75rem; font-weight: 700; background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
.auth-header p { color: var(--text-secondary); }
.auth-form { margin-bottom: 24px; }
.auth-error { background: #FEE2E2; color: #991B1B; padding: 12px 16px; border-radius: var(--radius-sm); font-size: 14px; margin-bottom: 16px; border: 1px solid #FECACA; }
.auth-footer { text-align: center; color: var(--text-secondary); font-size: 14px; }
.auth-footer a { color: var(--primary); cursor: pointer; font-weight: 500; }
.auth-footer a:hover { text-decoration: underline; }

.agreement-group { margin-bottom: 20px; }
.checkbox-label { display: flex; align-items: flex-start; gap: 10px; cursor: pointer; font-size: 13px; line-height: 1.5; }
.checkbox-label input { display: none; }
.checkmark { width: 18px; height: 18px; border: 2px solid var(--border); border-radius: 4px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; transition: all 0.2s; margin-top: 2px; }
.checkbox-label input:checked + .checkmark { background: var(--primary); border-color: var(--primary); }
.checkbox-label input:checked + .checkmark::after { content: '✓'; color: white; font-size: 12px; font-weight: bold; }
.agreement-text { color: var(--text-secondary); }
.agreement-text a { color: var(--primary); text-decoration: none; }
.agreement-text a:hover { text-decoration: underline; }

.terms-content { max-height: 400px; overflow-y: auto; }
.terms-content h4 { font-size: 15px; font-weight: 600; color: var(--text-primary); margin: 16px 0 8px; }
.terms-content h4:first-child { margin-top: 0; }
.terms-content p { font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 12px; }

@media (max-width: 480px) {
  .auth-container { padding: 16px; align-items: flex-start; padding-top: calc(60px + env(safe-area-inset-top, 0px)); }
  .auth-card { padding: 28px 20px; border-radius: var(--radius-lg); }
  .auth-header { margin-bottom: 28px; }
  .logo-icon-box { width: 56px; height: 56px; border-radius: 14px; }
  .auth-logo-svg { width: 36px; height: 36px; }
  .auth-header h1 { font-size: 1.5rem; }
  .checkbox-label { font-size: 12px; }
}
</style>
