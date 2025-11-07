// 手绘风导航站脚本
// 功能：加载本地 data.json，支持分类切换、关键字搜索、折叠展开

const state = {
  data: null,
  category: '全部',
  keyword: ''
};

document.addEventListener('DOMContentLoaded', init);

async function init() {
  // 根据头部高度为内容区预留空间，避免固定头部遮挡
  const header = document.querySelector('.site-header');
  const updateHeaderOffset = () => {
    if (!header) return;
    // 隐藏时减少占位，避免出现大面积空白
    if (header.classList.contains('hidden')) {
      document.documentElement.style.setProperty('--header-h', '8px');
      return;
    }
    const h = header.offsetHeight || 140;
    document.documentElement.style.setProperty('--header-h', h + 'px');
  };
  updateHeaderOffset();
  window.addEventListener('resize', updateHeaderOffset);

  // 滚动交互：下滑隐藏，上滑显示（苹果风格的平滑过渡）
  if (header) {
    let lastY = window.pageYOffset || document.documentElement.scrollTop || 0;
    let hidden = false;
    let ticking = false;
    const threshold = 6; // 防抖阈值，避免细微滚动抖动
    // 若初始并非顶部，进入紧凑模式
    if (lastY > 0) {
      header.classList.add('compact');
      updateHeaderOffset();
    }

    const showHeader = () => {
      if (hidden) {
        header.classList.remove('hidden');
        hidden = false;
      }
    };
    const hideHeader = () => {
      if (!hidden) {
        header.classList.add('hidden');
        hidden = true;
      }
    };

    const onScroll = () => {
      const currentY = window.pageYOffset || document.documentElement.scrollTop || 0;
      const delta = currentY - lastY;
      if (!ticking) {
        window.requestAnimationFrame(() => {
          // 顶部始终显示（并恢复完整头部）
          if (currentY <= 0) {
            showHeader();
            header.classList.remove('compact');
            updateHeaderOffset();
          } else if (delta > threshold) {
            // 向下滚动：隐藏头部
            hideHeader();
            updateHeaderOffset();
          } else if (delta < -threshold) {
            // 向上滚动：显示头部（紧凑模式，仅保留 h1 与 p）
            showHeader();
            header.classList.add('compact');
            updateHeaderOffset();
          }
          lastY = currentY;
          ticking = false;
        });
        ticking = true;
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  bindControls();
  try {
    const res = await fetch('data.json');
    if (!res.ok) throw new Error('数据加载失败: ' + res.status);
    state.data = await res.json();
    buildCategoryOptions();
    render();
  } catch (err) {
    console.error(err);
    document.getElementById('content').innerHTML = `<div class="category"><h2>加载失败</h2><p>${err.message}</p></div>`;
  }
}

function bindControls() {
  const sel = document.getElementById('categorySelect');
  const input = document.getElementById('searchInput');
  sel.addEventListener('change', () => {
    state.category = sel.value;
    render();
  });
  input.addEventListener('input', () => {
    state.keyword = input.value.trim();
    render();
  });
}

function buildCategoryOptions() {
  const sel = document.getElementById('categorySelect');
  sel.innerHTML = '';
  const allOpt = new Option('全部', '全部');
  sel.appendChild(allOpt);
  for (const cat of state.data.categories) {
    const opt = new Option(`${cat.name} (${cat.items.length})`, cat.name);
    sel.appendChild(opt);
  }
  sel.value = '全部';
}

function render() {
  const root = document.getElementById('content');
  root.innerHTML = '';
  if (!state.data) return;

  const kw = state.keyword.toLowerCase();
  const isAll = state.category === '全部';

  for (const cat of state.data.categories) {
    if (!isAll && cat.name !== state.category) continue;

    const matchedItems = cat.items.filter(it => matchItem(it, kw));
    if (matchedItems.length === 0) continue;

    root.appendChild(renderCategorySection(cat.name, matchedItems));
  }

  if (!root.children.length) {
    root.innerHTML = `<div class="category"><h2>没有匹配的结果</h2><p>试试更短的关键词，或切换到“全部”分类。</p></div>`;
  }
}

function matchItem(item, kw) {
  if (!kw) return true;
  const name = (item.name || '').toLowerCase();
  const desc = (item.description || '').toLowerCase();
  const url = (item.url || '').toLowerCase();
  return name.includes(kw) || desc.includes(kw) || url.includes(kw);
}

function renderCategorySection(name, items) {
  const sec = el('section', { className: 'category' });
  const h2 = el('h2');
  h2.textContent = name + ' ';
  const badge = el('span', { className: 'badge' });
  badge.textContent = items.length;
  h2.appendChild(badge);
  h2.title = '点击折叠/展开';
  h2.addEventListener('click', () => sec.classList.toggle('collapsed'));
  sec.appendChild(h2);

  const grid = el('div', { className: 'grid' });
  for (const item of items) grid.appendChild(renderCard(item));
  sec.appendChild(grid);
  return sec;
}

function renderCard(item) {
  const link = normalizeUrl(item.url, item.name);
  const card = el('a', { className: 'card', href: link, target: '_blank', rel: 'noopener' });

  // 语言徽标（EN/CH）
  const lang = getLang(item);
  if (lang) {
    const langClass = lang === 'EN' ? 'en' : 'ch';
    const langBadge = el('span', { className: `lang-badge ${langClass}`, title: lang === 'EN' ? '英文网站' : '中文网站' });
    langBadge.textContent = lang;
    card.appendChild(langBadge);
  }

  const title = el('h3');
  title.textContent = item.name || '(未命名)';
  card.appendChild(title);

  const desc = el('p');
  desc.textContent = item.description || '';
  card.appendChild(desc);

  const fee = getFee(item);
  if (fee) {
    const feeMap = { '免费': 'free', '半付费': 'semi', '付费': 'paid' };
    const badge = el('span', { className: `fee-badge ${feeMap[fee] || ''}` });
    badge.textContent = fee;
    card.appendChild(badge);
  }

  return card;
}

function normalizeUrl(url, name) {
  if (!url || url === '#') {
    return `https://www.google.com/search?q=${encodeURIComponent(name || '')}`;
  }
  if (url.startsWith('/')) return 'https://www.aewz.com' + url;
  return url;
}

function el(tag, props = {}) {
  const node = document.createElement(tag);
  Object.assign(node, props);
  return node;
}

// 根据描述或预置信息标注收费类型（免费/半付费/付费）
function getFee(item) {
  if (item.fee) return item.fee; // 若后续在数据中补充 fee 字段，优先使用
  const text = `${item.name || ''} ${item.description || ''}`;
  if (/免费/i.test(text)) return '免费';
  if (/半付费/.test(text)) return '半付费';
  if (/付费/.test(text)) return '付费';
  return null;
}

// 仅使用数据中的 item.lang 显示语言徽标；不再在前端进行启发式判断
function getLang(item) {
  const v = String(item.lang || '').toUpperCase();
  if (v === 'CN') return 'CH';
  if (v === 'CH' || v === 'EN') return v;
  return null; // 未提供则不显示徽标
}
