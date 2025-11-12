// 全局变量
let articles = [];

// DOM 元素
const articlesList = document.getElementById('articlesList');
const loading = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');
const modal = document.getElementById('articleModal');
const modalOverlay = document.getElementById('modalOverlay');
const modalClose = document.getElementById('modalClose');
const articleTitle = document.getElementById('articleTitle');
const articleDate = document.getElementById('articleDate');
const articleContent = document.getElementById('articleContent');
const backToTop = document.getElementById('backToTop');

// 加载文章数据
async function loadArticles() {
    try {
        const response = await fetch('articles.json');
        articles = await response.json();
        renderArticles();
    } catch (error) {
        console.error('加载文章失败:', error);
        showEmptyState();
    } finally {
        hideLoading();
    }
}

// 渲染文章列表
function renderArticles() {
    if (articles.length === 0) {
        showEmptyState();
        return;
    }

    articlesList.innerHTML = articles.map((article, index) => `
        <div class="article-card" data-index="${index}" style="animation-delay: ${index * 0.05}s">
            <div class="article-card-date">${article.date}</div>
            <h2 class="article-card-title">${article.title}</h2>
            <p class="article-card-summary">${article.summary}</p>
            <div class="article-card-footer">
                阅读全文
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M6 12l4-4-4-4"/>
                </svg>
            </div>
        </div>
    `).join('');

    // 添加点击事件
    document.querySelectorAll('.article-card').forEach(card => {
        card.addEventListener('click', () => {
            const index = parseInt(card.dataset.index);
            showArticle(index);
        });

        // 添加入场动画
        card.style.animation = 'fadeInUp 0.6s ease-out forwards';
    });
}

// 显示文章详情
function showArticle(index) {
    const article = articles[index];
    articleTitle.textContent = article.title;
    articleDate.textContent = article.date;
    
    // 简单的 Markdown 渲染（处理基本格式）
    let content = article.content;
    
    // 处理图片
    content = content.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');
    
    // 处理链接
    content = content.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // 处理标题
    content = content.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    content = content.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    content = content.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // 处理粗体
    content = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // 处理换行
    content = content.replace(/\n\n/g, '</p><p>');
    content = '<p>' + content + '</p>';
    
    articleContent.innerHTML = content;
    
    // 显示模态框
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// 关闭模态框
function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// 隐藏加载状态
function hideLoading() {
    loading.style.display = 'none';
}

// 显示空状态
function showEmptyState() {
    emptyState.style.display = 'block';
}

// 返回顶部
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// 监听滚动事件
window.addEventListener('scroll', () => {
    if (window.pageYOffset > 300) {
        backToTop.classList.add('visible');
    } else {
        backToTop.classList.remove('visible');
    }
});

// 事件监听
modalClose.addEventListener('click', closeModal);
modalOverlay.addEventListener('click', closeModal);
backToTop.addEventListener('click', scrollToTop);

// 键盘事件
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
        closeModal();
    }
});

// 页面加载完成后加载文章
document.addEventListener('DOMContentLoaded', loadArticles);
