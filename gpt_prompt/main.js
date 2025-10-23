// 全局变量
let allPrompts = [];
let currentCategory = '全部';
let searchKeyword = '';

// 加载数据
fetch('chatgpt_prompts.json')
  .then(response => response.json())
  .then(data => {
    window.promptsData = convertDataToArray(data);
    allPrompts = window.promptsData;
    updateStats();
    renderCategories();
    renderPrompts();
  })
  .catch(error => {
    console.error('Error loading prompts:', error);
    showError('加载数据失败，请刷新页面重试');
  });

// DOM 元素
const categoryListEl = document.getElementById('category-list');
const promptListEl = document.getElementById('prompt-list');
const searchInputEl = document.getElementById('search-input');
const modalEl = document.getElementById('prompt-modal');
const modalBodyEl = document.getElementById('modal-body');
const closeModalBtn = document.getElementById('close-modal-btn');

// 转换数据格式
function convertDataToArray(data) {
    const prompts = [];
    
    if (data.prompts_by_category) {
        Object.entries(data.prompts_by_category).forEach(([category, categoryPrompts]) => {
            categoryPrompts.forEach(prompt => {
                prompts.push({
                    title: prompt.title,
                    content: prompt.content,
                    category: prompt.category || category,
                    parameters: prompt.parameters || []
                });
            });
        });
    }
    
    return prompts;
}

// 更新统计信息
function updateStats() {
    const totalPrompts = allPrompts.length;
    const totalCategories = [...new Set(allPrompts.map(p => p.category))].length;
    
    document.getElementById('total-prompts').textContent = totalPrompts;
    document.getElementById('total-categories').textContent = totalCategories;
}

// 获取所有分类
function getAllCategories() {
    return ['全部', ...new Set(allPrompts.map(p => p.category))];
}

// 渲染分类按钮
function renderCategories() {
    const categories = getAllCategories();
    categoryListEl.innerHTML = '';
    
    categories.forEach(category => {
        const btn = document.createElement('button');
        btn.className = 'category-btn';
        btn.textContent = category;
        if (category === currentCategory) {
            btn.classList.add('active');
        }
        btn.onclick = () => {
            currentCategory = category;
            renderCategories();
            renderPrompts();
        };
        categoryListEl.appendChild(btn);
    });
}

// 渲染提示词卡片
function renderPrompts() {
    let list = window.promptsData;
    if (currentCategory !== '全部') {
        list = list.filter(p => p.category === currentCategory);
    }
    if (searchKeyword.trim()) {
        list = list.filter(p =>
            p.title?.includes(searchKeyword) ||
            p.content?.includes(searchKeyword) ||
            p.category?.includes(searchKeyword)
        );
    }
    
    const noResults = document.getElementById('no-results');
    
    if (list.length === 0) {
        promptListEl.innerHTML = '';
        noResults.classList.remove('hidden');
        return;
    }
    
    noResults.classList.add('hidden');
    promptListEl.innerHTML = '';
    
    list.forEach((p, idx) => {
        // 获取当前项在原始数据中的真实索引
        const originalIdx = window.promptsData.indexOf(p);
        const card = document.createElement('div');
        card.className = 'prompt-card';
        card.innerHTML = `
            <div class="prompt-title">${p.title || ''}</div>
            <div class="prompt-content">${p.content || ''}</div>
            <div class="prompt-category">${p.category || '未分类'}</div>
            ${p.parameters && p.parameters.length > 0 ? `
                <div class="prompt-parameters">
                    ${p.parameters.map(param => `<span class="param-tag">${param}</span>`).join('')}
                </div>
            ` : ''}
            <div class="card-actions">
                <button class="copy-btn" onclick="copyPromptContent('${encodeURIComponent(p.content?.replace(/'/g, "\\'") || '')}')">复制</button>
                <button class="action-btn" onclick="showPromptDetail(${originalIdx})">查看详情</button>
            </div>
        `;
        promptListEl.appendChild(card);
    });
}

// 显示提示词详情
window.showPromptDetail = function(idx) {
    const p = window.promptsData[idx];
    
    // 详情弹窗内容
    modalBodyEl.innerHTML = `
        <div style="font-size:20px;font-weight:700;margin-bottom:6px;">${p.title || ''}</div>
        <div style="margin-bottom:10px;"><span class="prompt-tag">${p.category || '未分类'}</span></div>
        ${p.parameters && p.parameters.length > 0 ? `
            <div style="margin-bottom:10px;">
                <strong>参数：</strong>
                ${p.parameters.map(param => `<span class="prompt-tag" style="background:#f3f4f6;color:#888;">${param}</span>`).join('')}
            </div>
        ` : ''}
        <hr class="modal-divider">
        <div style="font-weight:600;font-size:16px;margin-bottom:8px;">模板内容预览</div>
        <pre style="background:#f7f8fa;padding:12px 14px;border-radius:8px;white-space:pre-wrap;font-size:15px;line-height:1.7;">${p.content || ''}</pre>
        <div style="display:flex;justify-content:flex-end;gap:12px;margin-top:18px;">
            <button class="copy-btn" onclick="copyPromptContent('${encodeURIComponent(p.content?.replace(/'/g, "\\'") || '')}')">复制</button>
            <button class="action-btn" style="min-width:90px;" onclick="document.getElementById('prompt-modal').classList.add('hidden')">关闭</button>
        </div>
    `;
    modalEl.classList.remove('hidden');
}

// 复制提示词内容
window.copyPromptContent = function(encodedContent) {
    const content = decodeURIComponent(encodedContent);
    navigator.clipboard.writeText(content).then(() => {
        showCopyToast();
    }).catch(() => {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = content;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showCopyToast();
    });
}

// 显示复制提示
function showCopyToast() {
    let toast = document.getElementById('copy-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'copy-toast';
        toast.style.position = 'fixed';
        toast.style.right = '32px';
        toast.style.bottom = '32px';
        toast.style.background = 'rgba(60,60,60,0.95)';
        toast.style.color = '#fff';
        toast.style.padding = '10px 22px';
        toast.style.borderRadius = '8px';
        toast.style.fontSize = '16px';
        toast.style.zIndex = '2000';
        toast.style.boxShadow = '0 2px 8px #8882';
        document.body.appendChild(toast);
    }
    toast.textContent = '已复制到剪贴板！';
    toast.style.display = 'block';
    clearTimeout(window._copyToastTimer);
    window._copyToastTimer = setTimeout(() => {
        toast.style.display = 'none';
    }, 1200);
}

// 显示错误信息
function showError(message) {
    const promptList = document.getElementById('prompt-list');
    promptList.innerHTML = `
        <div style="text-align: center; padding: 60px 20px; color: #6b7280;">
            <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
            <div style="font-size: 18px; font-weight: 600; margin-bottom: 8px; color: #374151;">加载失败</div>
            <div style="font-size: 14px;">${message}</div>
        </div>
    `;
}

// 绑定事件监听器
function bindEventListeners() {
    // 搜索功能
    if (searchInputEl) {
        searchInputEl.addEventListener('input', e => {
            searchKeyword = e.target.value;
            renderPrompts();
        });
        
        searchInputEl.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchKeyword = e.target.value;
                renderPrompts();
            }
        });
    }
    
    // 关闭模态框
    if (closeModalBtn) {
        closeModalBtn.onclick = () => modalEl.classList.add('hidden');
    }
    
    if (modalEl) {
        modalEl.onclick = e => { 
            if (e.target === modalEl) modalEl.classList.add('hidden'); 
        };
    }
    
    // ESC 键关闭模态框
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modalEl && !modalEl.classList.contains('hidden')) {
            modalEl.classList.add('hidden');
        }
    });
}

// 页面加载完成后绑定事件
document.addEventListener('DOMContentLoaded', function() {
    bindEventListeners();
});