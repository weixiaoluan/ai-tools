<template>
  <div class="public-article">
    <!-- SEO Header -->
    <Teleport to="head">
      <title>{{ article?.title }} - LearnFlow AI</title>
      <meta name="description" :content="seoDescription" />
      <meta name="keywords" :content="seoKeywords" />
      <meta property="og:title" :content="article?.title" />
      <meta property="og:description" :content="seoDescription" />
      <meta property="og:type" content="article" />
      <meta property="og:url" :content="currentUrl" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" :content="article?.title" />
      <meta name="twitter:description" :content="seoDescription" />
    </Teleport>
    
    <!-- 顶部导航 -->
    <header class="public-header">
      <div class="header-content">
        <a href="/" class="header-logo">
          <svg viewBox="0 0 24 24" fill="none" class="header-logo-svg">
            <path d="M12 2L2 7l10 5 10-5-10-5z" fill="#4F46E5"/>
            <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="#6366F1" stroke-width="2" fill="none"/>
          </svg>
          <span>LearnFlow AI</span>
        </a>
        <button class="btn btn-primary btn-sm" @click="$emit('login')">登录使用</button>
      </div>
    </header>
    
    <main class="public-main" v-if="article">
      <article class="article-container" itemscope itemtype="https://schema.org/Article">
        <header class="article-header">
          <h1 itemprop="headline">{{ article.title }}</h1>
          <div class="article-meta">
            <time :datetime="article.created_at" itemprop="datePublished">📅 {{ formatDate(article.created_at) }}</time>
            <span class="tag" itemprop="articleSection">{{ article.type === 'chapter' ? '章节' : '文章' }}</span>
          </div>
        </header>
        
        <div class="article-body markdown-body" itemprop="articleBody" v-html="renderedContent"></div>
        
        <!-- 分享栏 -->
        <div class="share-bar">
          <span class="share-label">分享到：</span>
          <div class="share-buttons">
            <button class="share-btn wechat" @click="shareToWechat" title="分享到微信">
              <svg viewBox="0 0 24 24"><path d="M8.5 11a1.5 1.5 0 100-3 1.5 1.5 0 000 3zm5 0a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" fill="currentColor"/><path d="M12 2C6.48 2 2 6.03 2 11c0 2.76 1.36 5.22 3.5 6.87V22l3.5-2c.97.27 2 .42 3 .42 5.52 0 10-4.03 10-9S17.52 2 12 2z" fill="currentColor"/></svg>
              微信
            </button>
            <button class="share-btn qq" @click="shareToQQ" title="分享到QQ">
              <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 13.19c-.18.52-.54.96-1.01 1.26-.47.3-1.02.45-1.63.45-.61 0-1.16-.15-1.63-.45-.47-.3-.83-.74-1.01-1.26-.18-.52-.18-1.08 0-1.6.18-.52.54-.96 1.01-1.26.47-.3 1.02-.45 1.63-.45.61 0 1.16.15 1.63.45.47.3.83.74 1.01 1.26.18.52.18 1.08 0 1.6z" fill="currentColor"/></svg>
              QQ
            </button>
            <button class="share-btn wecom" @click="shareToWecom" title="分享到企业微信">
              <svg viewBox="0 0 24 24"><path d="M20 6h-4V4c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-6 0h-4V4h4v2z" fill="currentColor"/></svg>
              企业微信
            </button>
            <button class="share-btn dingtalk" @click="shareToDingtalk" title="分享到钉钉">
              <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="currentColor"/></svg>
              钉钉
            </button>
            <button class="share-btn copy" @click="copyLink" title="复制链接">
              <svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z" fill="currentColor"/></svg>
              复制链接
            </button>
          </div>
        </div>
      </article>
    </main>
    
    <div v-else class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 微信分享二维码弹窗 -->
    <div v-if="showQrcode" class="modal-overlay" @click.self="showQrcode = false">
      <div class="modal-content qrcode-modal">
        <div class="modal-header">
          <h3>微信扫码分享</h3>
          <button class="modal-close" @click="showQrcode = false">✕</button>
        </div>
        <div class="qrcode-container">
          <div ref="qrcodeRef" class="qrcode"></div>
          <p>打开微信扫一扫，分享给好友</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import axios from 'axios'
import { useModal } from '../composables/useModal'

const modal = useModal()
const props = defineProps({ articleId: String })
defineEmits(['login'])

const article = ref(null)
const showQrcode = ref(false)
const qrcodeRef = ref(null)

const currentUrl = computed(() => window.location.href)
const seoDescription = computed(() => {
  if (!article.value?.content) return ''
  return article.value.content.replace(/[#*`\[\]]/g, '').substring(0, 160)
})
const seoKeywords = computed(() => {
  if (!article.value) return ''
  return `${article.value.topic || ''}, ${article.value.title}, AI学习, 教程`
})

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return marked(article.value.content)
})

function formatDate(str) {
  if (!str) return ''
  return new Date(str).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function loadArticle() {
  try {
    const res = await axios.get(`/api/public/articles/${props.articleId}`)
    article.value = res.data.article
  } catch (e) { console.error('加载失败', e) }
}

function shareToWechat() {
  showQrcode.value = true
  nextTick(() => {
    // 简单的二维码生成（实际项目中可使用 qrcode.js）
    if (qrcodeRef.value) {
      qrcodeRef.value.innerHTML = `<div style="padding:40px;text-align:center;background:#f5f5f5;border-radius:8px;">
        <p style="font-size:14px;color:#666;">请复制链接后在微信中打开分享</p>
        <p style="font-size:12px;color:#999;margin-top:8px;word-break:break-all;">${currentUrl.value}</p>
      </div>`
    }
  })
}

function shareToQQ() {
  const url = `https://connect.qq.com/widget/shareqq/index.html?url=${encodeURIComponent(currentUrl.value)}&title=${encodeURIComponent(article.value?.title || '')}`
  window.open(url, '_blank', 'width=600,height=500')
}

async function shareToWecom() {
  await copyLink()
  modal.success('链接已复制，请在企业微信中粘贴分享', '分享')
}

function shareToDingtalk() {
  const url = `https://page.dingtalk.com/wow/dingtalk/act/share?url=${encodeURIComponent(currentUrl.value)}&title=${encodeURIComponent(article.value?.title || '')}`
  window.open(url, '_blank', 'width=600,height=500')
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(currentUrl.value)
    modal.success('链接已复制到剪贴板', '复制成功')
  } catch {
    await modal.prompt('请手动复制链接：', currentUrl.value, '复制链接')
  }
}

onMounted(loadArticle)
</script>

<style scoped>
.public-article { min-height: 100vh; background: var(--bg-main); }

.public-header { background: white; border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
.header-content { max-width: 900px; margin: 0 auto; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
.header-logo { display: flex; align-items: center; gap: 10px; text-decoration: none; color: var(--text-primary); font-weight: 700; font-size: 18px; }
.header-logo-svg { width: 32px; height: 32px; }

.public-main { max-width: 900px; margin: 0 auto; padding: 40px 24px; }

.article-container { background: white; border-radius: var(--radius-lg); padding: 48px; box-shadow: var(--shadow-md); }
.article-header { margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid var(--border); }
.article-header h1 { font-size: 2rem; font-weight: 700; line-height: 1.3; margin-bottom: 16px; color: var(--text-primary); }
.article-meta { display: flex; gap: 16px; align-items: center; color: var(--text-muted); font-size: 14px; }

.share-bar { margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--border); }
.share-label { font-size: 14px; color: var(--text-secondary); margin-bottom: 12px; display: block; }
.share-buttons { display: flex; gap: 12px; flex-wrap: wrap; }

.share-btn { display: flex; align-items: center; gap: 6px; padding: 10px 16px; border: 1px solid var(--border); border-radius: 8px; background: white; color: var(--text-secondary); font-size: 13px; cursor: pointer; transition: all 0.2s; }
.share-btn svg { width: 18px; height: 18px; }
.share-btn:hover { border-color: var(--primary); color: var(--primary); }
.share-btn.wechat:hover { border-color: #07C160; color: #07C160; }
.share-btn.qq:hover { border-color: #12B7F5; color: #12B7F5; }
.share-btn.wecom:hover { border-color: #2BAD13; color: #2BAD13; }
.share-btn.dingtalk:hover { border-color: #0089FF; color: #0089FF; }

.loading-state { text-align: center; padding: 100px 20px; color: var(--text-muted); }

.qrcode-modal { max-width: 360px; text-align: center; }
.qrcode-container { padding: 20px; }
.qrcode { margin-bottom: 16px; }
.qrcode-container p { font-size: 14px; color: var(--text-secondary); }

@media (max-width: 768px) {
  .article-container { padding: 24px; border-radius: var(--radius-md); }
  .article-header h1 { font-size: 1.5rem; }
  .share-buttons { gap: 8px; }
  .share-btn { padding: 8px 12px; font-size: 12px; }
  .share-btn span { display: none; }
}
</style>
