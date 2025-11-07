// 极简手绘风首页脚本：实现头部隐藏/显示与占位动态调整

document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('.site-header');
  if (!header) return;

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
  const threshold = 6;
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

