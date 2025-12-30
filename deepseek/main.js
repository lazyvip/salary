// 加载 New_prompts.json 并初始化页面
fetch('New_prompts.json')
  .then(res => res.json())
  .then(data => {
    window.promptsData = data.prompt_templates;
    renderCategories();
    renderPrompts();
  });

const categoryListEl = document.getElementById('category-list');
const promptListEl = document.getElementById('prompt-list');
const searchInputEl = document.getElementById('search-input');
const modalEl = document.getElementById('modal');
const modalBodyEl = document.getElementById('modal-body');
const closeModalBtn = document.getElementById('close-modal');

let currentCategory = '全部';
let searchKeyword = '';

const categoryMap = {
  "business": "商业",
  "consulting": "咨询",
  "programming": "编程",
  "language": "语言",
  "writing": "写作",
  "brainstorming": "发散思维",
  "tools": "工具",
  "ai": "AI",
  "medical": "医疗",
  "debate": "辩论",
  "academic": "学术",
  "trivia": "趣味",
  "article": "文章",
  "psychology": "心理",
  "review": "点评",
  "reference": "参考",
  "education": "教育",
  "lifestyle": "生活",
  "philosophy": "哲学",
  "seo": "SEO"
};

function getCategoryName(key) {
  return categoryMap[key?.toLowerCase()] || key || '未分类';
}

function getAllCategories() {
  const cats = window.promptsData.map(p => getCategoryName(p.category?.trim()));
  return ['全部', ...Array.from(new Set(cats))];
}

function renderCategories() {
  const cats = getAllCategories();
  categoryListEl.innerHTML = '';
  cats.forEach(cat => {
    const btn = document.createElement('button');
    btn.className = 'category-btn' + (cat === currentCategory ? ' active' : '');
    btn.textContent = cat;
    btn.onclick = () => {
      currentCategory = cat;
      renderCategories();
      renderPrompts();
    };
    categoryListEl.appendChild(btn);
  });
}

function renderPrompts() {
  let list = window.promptsData;
  if (currentCategory !== '全部') {
    list = list.filter(p => (p.category?.trim() || '未分类') === currentCategory);
  }
  if (searchKeyword.trim()) {
    list = list.filter(p =>
      p.name?.includes(searchKeyword) ||
      p.description?.includes(searchKeyword) ||
      p.content?.includes(searchKeyword)
    );
  }
  promptListEl.innerHTML = '';
  list.forEach((p, idx) => {
    // 获取当前项在原始数据中的真实索引
    const originalIdx = window.promptsData.indexOf(p);
    const card = document.createElement('div');
    card.className = 'prompt-card';
    card.innerHTML = `
      <div class="prompt-title">${p.name?.trim() || ''}</div>
      <div class="prompt-category">${p.category?.trim() || '未分类'}</div>
      <div class="prompt-desc">${p.description?.trim() || ''}</div>
      <div class="card-actions">
        <button class="action-btn" onclick="showPromptDetail(${originalIdx})">使用</button>
      </div>
    `;
    promptListEl.appendChild(card);
  });
}

window.showPromptDetail = function(idx) {
  const p = window.promptsData[idx];
  // 标签区支持多个标签
  let tags = '';
  if (p.category) tags += `<span class="prompt-tag">${getCategoryName(p.category.trim())}</span>`;
  
  // 详情弹窗内容
  modalBodyEl.innerHTML = `
    <div style="font-size:20px;font-weight:700;margin-bottom:6px;">${p.name?.trim() || ''}</div>
    <div style="margin-bottom:10px;">${tags}</div>
    <div style="color:#555;font-size:15px;margin-bottom:10px;"> <b>描述：</b> ${p.description?.trim() || ''}</div>
    <hr class="modal-divider">
    <div style="font-weight:600;font-size:16px;margin-bottom:8px;">模板内容预览</div>
    <pre style="background:#f7f8fa;padding:12px 14px;border-radius:8px;white-space:pre-wrap;font-size:15px;line-height:1.7;">${p.content?.trim() || ''}</pre>
    <div style="display:flex;justify-content:flex-end;gap:12px;margin-top:18px;">
      <button class="copy-btn" onclick="copyPromptContent('${encodeURIComponent(p.content?.replace(/'/g, "\'") || '')}')">复制</button>
      <button class="action-btn" style="min-width:90px;" onclick="document.getElementById('modal').classList.add('hidden')">关闭</button>
    </div>
  `;
  modalEl.classList.remove('hidden');
}

window.copyPromptContent = function(encodedContent) {
  const content = decodeURIComponent(encodedContent);
  navigator.clipboard.writeText(content);
  showCopyToast();
}

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

closeModalBtn.onclick = () => modalEl.classList.add('hidden');
modalEl.onclick = e => { if (e.target === modalEl) modalEl.classList.add('hidden'); };

searchInputEl.addEventListener('input', e => {
  searchKeyword = e.target.value;
  renderPrompts();
});