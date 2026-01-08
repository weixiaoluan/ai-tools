<template>
  <div class="platform-container">
    <!-- 顶部导航 -->
    <header class="platform-header">
      <div class="header-content">
        <div class="platform-logo">
          <div class="logo-icon-box">
            <svg viewBox="0 0 24 24" fill="none" class="logo-svg">
              <path d="M12 2L2 7l10 5 10-5-10-5z" fill="url(#pgrad1)"/>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="url(#pgrad2)" stroke-width="2" fill="none"/>
              <defs>
                <linearGradient id="pgrad1" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#6366F1"/><stop offset="100%" style="stop-color:#8B5CF6"/>
                </linearGradient>
                <linearGradient id="pgrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#818CF8"/><stop offset="100%" style="stop-color:#A78BFA"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div class="logo-text">
            <h1>AI Tools</h1>
            <p>智能工具平台</p>
          </div>
        </div>
        <div class="header-user" v-if="user">
          <span class="user-avatar">{{ user.username.charAt(0).toUpperCase() }}</span>
          <span class="user-name">{{ user.username }}</span>
          <button class="btn-logout" @click="$emit('logout')">退出登录</button>
        </div>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="platform-main">
      <div class="hero-section">
        <h1>🚀 AI 智能工具平台</h1>
        <p>探索强大的AI工具，提升您的工作与学习效率</p>
      </div>

      <div class="tools-section">
        <div class="section-header">
          <h2>🛠️ 工具中心</h2>
          <p>选择您需要的AI工具开始使用</p>
        </div>
        
        <div class="tools-grid">
          <!-- AI快速学 -->
          <div class="tool-card featured" @click="$emit('enter-tool', 'learnflow')">
            <div class="tool-header">
              <div class="tool-icon">📚</div>
              <span class="tool-badge hot">热门</span>
            </div>
            <h3>AI 快速学</h3>
            <p>智能生成学习文档和文章，快速掌握任何知识领域</p>
            <div class="tool-features">
              <span>✓ 智能大纲</span>
              <span>✓ 多章节文档</span>
              <span>✓ AI问答</span>
            </div>
            <button class="btn btn-primary btn-block">进入工具 →</button>
          </div>

          <!-- 更多工具占位 -->
          <div class="tool-card disabled">
            <div class="tool-header">
              <div class="tool-icon">🎨</div>
              <span class="tool-badge soon">即将上线</span>
            </div>
            <h3>AI 绘图</h3>
            <p>文字描述生成精美图片，释放您的创意想象</p>
            <div class="tool-features">
              <span>✓ 多种风格</span>
              <span>✓ 高清输出</span>
            </div>
            <button class="btn btn-secondary btn-block" disabled>敬请期待</button>
          </div>

          <div class="tool-card disabled">
            <div class="tool-header">
              <div class="tool-icon">💬</div>
              <span class="tool-badge soon">即将上线</span>
            </div>
            <h3>AI 对话</h3>
            <p>智能对话助手，解答各类问题与疑惑</p>
            <div class="tool-features">
              <span>✓ 多轮对话</span>
              <span>✓ 知识问答</span>
            </div>
            <button class="btn btn-secondary btn-block" disabled>敬请期待</button>
          </div>


        </div>
      </div>
    </main>

    <!-- 底部 -->
    <footer class="platform-footer">
      <p>© 2025 AI Tools Platform. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup>
defineProps({ user: Object })
defineEmits(['enter-tool', 'logout'])
</script>

<style scoped>
.platform-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
  display: flex;
  flex-direction: column;
}

.platform-header {
  background: var(--bg-white);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon-box {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--primary-bg), rgba(139, 92, 246, 0.1));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-svg { width: 28px; height: 28px; }

.logo-text h1 {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-text p { font-size: 11px; color: var(--text-muted); }

.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.user-name {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
}

.btn-logout {
  background: var(--bg-main);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #FEE2E2;
  border-color: #FECACA;
  color: var(--error);
}

.platform-main {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px;
  width: 100%;
}

.hero-section {
  text-align: center;
  margin-bottom: 48px;
}

.hero-section h1 {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary), var(--accent), #EC4899);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.hero-section p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.section-header {
  margin-bottom: 32px;
}

.section-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.section-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.tool-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 28px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tool-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  opacity: 0;
  transition: opacity 0.3s;
}

.tool-card:hover {
  transform: translateY(-6px);
  border-color: var(--primary-light);
  box-shadow: var(--shadow-xl);
}

.tool-card:hover::before { opacity: 1; }

.tool-card.featured {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.05));
  border-color: rgba(99, 102, 241, 0.2);
}

.tool-card.featured::before { opacity: 1; }

.tool-card.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.tool-card.disabled:hover {
  transform: none;
  box-shadow: none;
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.tool-icon { font-size: 2.5rem; }

.tool-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
}

.tool-badge.hot {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: white;
}

.tool-badge.soon {
  background: var(--bg-main);
  color: var(--text-muted);
  border: 1px solid var(--border);
}

.tool-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.tool-card p {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.tool-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.tool-features span {
  font-size: 12px;
  color: var(--primary);
  background: var(--primary-bg);
  padding: 4px 10px;
  border-radius: 6px;
}

.platform-footer {
  text-align: center;
  padding: 24px;
  border-top: 1px solid var(--border);
  background: var(--bg-white);
}

.platform-footer p {
  color: var(--text-muted);
  font-size: 13px;
}

@media (max-width: 768px) {
  .hero-section h1 { font-size: 1.75rem; }
  .hero-section p { font-size: 1rem; }
  .tools-grid { grid-template-columns: 1fr; }
  .platform-main { padding: 32px 16px; }
  .header-content { padding: 12px 16px; }
  .user-name { display: none; }
  .logo-text h1 { font-size: 1.1rem; }
}
</style>
