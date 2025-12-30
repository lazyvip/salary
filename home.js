// 极简手绘风首页脚本：实现头部隐藏/显示与占位动态调整

document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('.site-header');
  const grid = document.querySelector('.grid');
  if (!header || !grid) return;

  const cards = [
    { href: 'lazyblog/site/index.html', icon: '📔', title: '懒人收藏夹', desc: '极简手绘风文章收藏与阅读' },
    { href: 'money_card/index.html', icon: '💡', title: '信息差卡片合集', desc: '精选优质商业案例，深度解析成功模式' },
    { href: 'https://lazytool.top/free/index.html', icon: '📚', title: '懒人知识库（粉丝体验版）', desc: '粉丝免费体验专属群部分知识库', external: true },
    { href: 'salary_count/index.html', icon: '💰', title: '工资计算器', desc: '实时计算你的工资收入' },
    { href: 'news/index.html', icon: '📰', title: '懒人日报', desc: '每日新闻早报，60秒读懂世界' },
    { href: 'https://lazypic.lazytool.top/', icon: '🖼️', title: '图片工具', desc: '专业的图片压缩与合并功能', external: true },
    { href: 'hacker_simulator/index.html', icon: '🖥️', title: '黑客模拟器', desc: '体验电影级黑客效果' },
    { href: 'fake_update/index.html', icon: '🔄', title: '假装系统更新', desc: '模拟各种系统更新界面' },
    { href: 'deepseek/index.html', icon: '🤖', title: 'AI提示词大全', desc: 'DeepSeek常用提示词集合' },
    { href: 'doubao/index.html', icon: '🧠', title: '豆包提示词', desc: '豆包常用提示词大全，助力高效创作' },
    { href: 'https://logo.lazytool.top/', icon: '🎨', title: 'P站Logo生成器', desc: '一键生成P站风格Logo', external: true },
    { href: 'story/index.html', icon: '📖', title: '故事阅读网站', desc: '精选优质故事，支持分类浏览和搜索' },
    { href: 'xifeng/index.html', icon: '📚', title: '记忆承载付费文AI解读', desc: 'AI智能解读付费文章内容' },
    { href: 'https://cook.lazytool.top/', icon: '👨‍🍳', title: '懒人厨房助手', desc: '智能菜谱推荐，轻松下厨房', external: true },
    { href: 'blog/secret.html', icon: '🔐', title: '歪比巴卜密文转换器', desc: '安全的AES加密解密工具' },
    { href: 'https://worthjob.lazytool.top/', icon: '💼', title: '工作价值评估（趣味）', desc: '这B班，到底值得不得上！', external: true },
    { href: 'video_nav/index.html', icon: '🎬', title: '懒人视频制作导航', desc: '视频素材、字幕配音、制作工具、音乐等资源合集' },
    { href: 'art/index.html', icon: '🎨', title: 'AI绘画提示词', desc: '精选高质量AI绘画提示词，激发无限灵感' },
    {
      href: 'https://lazybook.fun', icon: '📖', title: '懒人手册', desc: '多域名访问，选择最适合的入口', external: true,
      domains: [
        { href: 'https://lazybook.fun', label: '主域名: lazybook.fun', primary: true },
        { href: 'https://lazy2024.top/', label: '备用域名1: lazy2024.top' },
        { href: 'https://lazy2025.top/', label: '备用域名2: lazy2025.top' },
      ]
    },
  ];

  const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
  const createCard = (cfg) => {
    const tag = cfg.domains && Array.isArray(cfg.domains) ? 'div' : 'a';
    const a = document.createElement(tag);
    a.className = 'card';
    if (tag === 'a') {
      a.href = cfg.href;
      if (cfg.external) {
        a.target = '_blank';
        a.rel = 'noopener';
      }
    } else {
      a.setAttribute('role', 'link');
      a.setAttribute('tabindex', '0');
      a.addEventListener('click', () => {
        const target = cfg.external ? '_blank' : '_self';
        window.open(cfg.href, target);
      });
      a.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          const target = cfg.external ? '_blank' : '_self';
          window.open(cfg.href, target);
        }
      });
    }
    const angle = (Math.random() - 0.5) * 1.6; // -0.8deg ~ 0.8deg
    a.style.setProperty('--tilt', angle.toFixed(2) + 'deg');
    a.style.setProperty('--r1', rand(6, 18) + 'px');
    a.style.setProperty('--r2', rand(6, 22) + 'px');
    a.style.setProperty('--r3', rand(6, 18) + 'px');
    a.style.setProperty('--r4', rand(6, 22) + 'px');

    const icon = document.createElement('div');
    icon.className = 'icon';
    icon.textContent = cfg.icon || '📎';
    const h3 = document.createElement('h3');
    h3.textContent = cfg.title;
    const p = document.createElement('p');
    p.textContent = cfg.desc;

    a.appendChild(icon);
    a.appendChild(h3);
    a.appendChild(p);

    if (cfg.domains && Array.isArray(cfg.domains)) {
      const links = document.createElement('div');
      links.className = 'domain-links';
      cfg.domains.forEach(d => {
        const dl = document.createElement('a');
        dl.href = d.href;
        dl.target = '_blank';
        dl.className = 'domain-link' + (d.primary ? ' primary' : '');
        dl.textContent = d.label;
        links.appendChild(dl);
      });
      a.appendChild(links);
    }

    return a;
  };

  grid.innerHTML = '';
  cards.forEach(c => grid.appendChild(createCard(c)));

  const updateHeaderOffset = () => {
    if (header.classList.contains('hidden')) {
      document.documentElement.style.setProperty('--header-h', '8px');
      return;
    }
    const h = header.offsetHeight || 120;
    document.documentElement.style.setProperty('--header-h', h + 'px');
  };

  updateHeaderOffset();
  window.addEventListener('resize', updateHeaderOffset);

  let lastY = window.pageYOffset || document.documentElement.scrollTop || 0;
  let hidden = false;
  let ticking = false;
  const threshold = 10;
  if (lastY > 0) {
    header.classList.add('compact');
    updateHeaderOffset();
  }

  const showHeader = () => {
    if (hidden) { header.classList.remove('hidden'); hidden = false; }
  };
  const hideHeader = () => {
    if (!hidden) { header.classList.add('hidden'); hidden = true; }
  };

  const onScroll = () => {
    const currentY = window.pageYOffset || document.documentElement.scrollTop || 0;
    const delta = currentY - lastY;
    if (!ticking) {
      window.requestAnimationFrame(() => {
        if (currentY <= 0) {
          showHeader();
          header.classList.remove('compact');
          updateHeaderOffset();
        } else if (delta > threshold) {
          hideHeader();
          updateHeaderOffset();
        } else if (delta < -threshold) {
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
});

