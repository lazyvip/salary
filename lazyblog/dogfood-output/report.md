# 懒人收藏夹 性能分析报告

| 字段 | 值 |
|-------|-------|
| **日期** | 2026-05-08 |
| **应用 URL** | http://localhost:8080/site/ |
| **范围** | 页面加载性能全面分析 |

## 摘要

| 严重程度 | 数量 |
|----------|-------|
| 严重 | 2 |
| 高 | 3 |
| 中 | 2 |
| 低 | 1 |
| **总计** | **8** |

---

## 问题列表

### ISSUE-001: 4.9MB 自定义字体文件是最大性能杀手

| 字段 | 值 |
|-------|-------|
| **严重程度** | 严重 |
| **类别** | performance |
| **URL** | http://localhost:8080/site/ |

**描述**

`三极古拙楷书简.ttf` 是一个 4.9MB 的 TTF 字体文件。在当前网络环境下（尤其是移动端），下载近 5MB 的字体文件会导致极长的白屏/无样式文本闪烁时间。

**详细分析**

1. 字体通过 JavaScript `FontFace` API 在页面加载后 **延迟 1.5 秒** 才开始加载（[app.js:413-416](file:///Users/alexwu/code/salary/lazyblog/site/app.js#L413-L416)）
2. 这意味着用户至少等待 1.5s + 下载时间才能看到正确字体
3. TTF 格式未压缩，转换为 WOFF2 格式通常可减少 30-50% 体积
4. Python http.server 不支持 gzip/brotli 压缩，4.9MB 原样传输

**影响估算**

- 4G 网络 (10Mbps): ~4s 额外加载时间
- 3G 网络 (1Mbps): ~40s 额外加载时间
- WiFi (50Mbps): ~0.8s 额外加载时间

---

### ISSUE-002: Google Fonts 渲染阻塞导致首屏延迟 ~1.6s

| 字段 | 值 |
|-------|-------|
| **严重程度** | 严重 |
| **类别** | performance |
| **URL** | http://localhost:8080/site/ |

**描述**

[index.html:7-9](file:///Users/alexwu/code/salary/lazyblog/site/index.html#L7-L9) 中加载了 Google Fonts 的 Caveat 和 Patrick Hand 字体：

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Patrick+Hand&display=swap" rel="stylesheet">
```

**实测数据**

| 资源 | TTFB | 总时间 |
|------|------|--------|
| Google Fonts CSS | 1.62s | 1.62s |
| Caveat woff2 | 1.65s | 1.65s |
| Patrick Hand woff2 | 1.68s | 1.69s |

**问题**

1. Google Fonts CSS 是渲染阻塞资源，浏览器必须等它下载完才能继续解析页面
2. 虽然使用了 `display=swap`，但 CSS 本身的下载仍阻塞渲染
3. 这两个字体实际上只是 **备选字体**，最终会被 4.9MB 的自定义字体覆盖，等于白加载了
4. 在国内网络环境下，Google Fonts 访问不稳定，经常超时

---

### ISSUE-003: font.css 未被引用，@font-face 声明无效

| 字段 | 值 |
|-------|-------|
| **严重程度** | 高 |
| **类别** | performance |
| **URL** | http://localhost:8080/site/ |

**描述**

[font.css](file:///Users/alexwu/code/salary/lazyblog/site/font.css) 中定义了 `@font-face` 声明：

```css
@font-face {
  font-family: 'SanJiKai';
  src: url('../data/三极古拙楷书简.ttf') format('truetype');
  font-display: swap;
}
```

但是 [index.html](file:///Users/alexwu/code/salary/lazyblog/site/index.html) 中 **没有** `<link rel="stylesheet" href="font.css">` 引用。这意味着：

1. CSS 中的 `@font-face` 声明完全无效
2. 字体只能通过 JavaScript 的 `FontFace` API 加载
3. 丧失了 `font-display: swap` 的优化效果
4. 浏览器无法在解析 CSS 阶段就预加载字体

---

### ISSUE-004: Python http.server 无压缩、无缓存控制

| 字段 | 值 |
|-------|-------|
| **严重程度** | 高 |
| **类别** | performance |
| **URL** | http://localhost:8080/site/ |

**描述**

当前使用 `python3 -m http.server` 提供服务，存在以下问题：

1. **无 gzip/brotli 压缩** — 4.9MB 字体原样传输，如果启用 gzip 可减少到约 2.5MB
2. **无 Cache-Control 头** — 浏览器每次访问都可能重新下载所有资源
3. **无 ETag** — 无法进行条件请求，浪费带宽
4. 只有 `Last-Modified` 头，浏览器仍需发送验证请求

**实测**

```
Content-Encoding: (无)
Cache-Control: (无)
ETag: (无)
```

---

### ISSUE-005: 100/153 篇文章含微信图片，需通过第三方代理加载

| 字段 | 值 |
|-------|-------|
| **严重程度** | 高 |
| **类别** | performance |
| **URL** | http://localhost:8080/site/ |

**描述**

[app.js:52-61](file:///Users/alexwu/code/salary/lazyblog/site/app.js#L52-L61) 中，微信图片被重写为通过代理加载：

```javascript
if(h.includes('mmbiz.qpic.cn')||h.includes('wx.qlogo.cn')||h.includes('mp.weixin.qq.com')){
  return 'https://m.wbiao.cn/mallapi/wechat/picReverseUrl?url='+encodeURIComponent(url)
}
```

**问题**

1. 100 篇文章包含微信图片，部分文章多达 23 张图片
2. 每张图片需经过 `m.wbiao.cn` 代理，实测单张 TTFB ~0.57s
3. 一篇含 23 张图片的文章，仅图片加载就需要 ~13s（串行加载）
4. 代理服务稳定性不可控，可能随时失效
5. 图片未做本地缓存，每次打开文章都重新通过代理加载

---

### ISSUE-006: 字体加载策略导致严重 FOUT（无样式文本闪烁）

| 字段 | 值 |
|-------|-------|
| **严重程度** | 中 |
| **类别** | performance / ux |
| **URL** | http://localhost:8080/site/ |

**描述**

当前字体加载链路：

1. 页面加载 → 使用系统字体渲染
2. Google Fonts 下载完成 (~1.6s) → 切换到 Caveat/Patrick Hand → **第一次布局抖动**
3. 页面加载后 1.5s → JavaScript 开始下载 4.9MB TTF → **第二次布局抖动**
4. TTF 下载完成 → 切换到 SanJiKai → **第三次布局抖动**

用户会经历 **三次字体切换**，每次切换都会导致页面布局重排，体验极差。

---

### ISSUE-007: 无资源预加载（preload/prefetch）

| 字段 | 值 |
|-------|-------|
| **严重程度** | 中 |
| **类别** | performance |
| **URL** | http://localhost:8080/site/ |

**描述**

页面缺少关键资源的预加载提示：

1. 无 `<link rel="preload">` 告知浏览器提前下载字体文件
2. 无 `<link rel="preload">` 提前下载 posts.json
3. 无 `<link rel="dns-prefetch">` 预解析微信图片代理域名
4. posts.json 的加载依赖 JavaScript 执行，无法利用浏览器空闲时间预取

---

### ISSUE-008: 搜索功能全文扫描性能问题

| 字段 | 值 |
|-------|-------|
| **严重程度** | 低 |
| **类别** | performance |
| **URL** | http://localhost:8080/site/ |

**描述**

[app.js:193-217](file:///Users/alexwu/code/salary/lazyblog/site/app.js#L193-L217) 中，搜索功能在标题匹配不到时会逐篇下载并扫描全文：

1. 153 篇文章，每篇平均 33KB，总计约 5MB 文本需要下载
2. 搜索时逐篇 `fetch` + 全文匹配，无索引
3. 虽然有缓存机制，但首次搜索仍需下载所有文章
4. 搜索结果每 4 篇刷新一次列表，可能导致频繁 DOM 操作

---

## 加载时序瀑布图（估算）

```
时间轴 (秒)
0s    ┌─ index.html (6ms)
      │  ├─ style.css (2ms)
      │  ├─ app.js (1ms)
      │  └─ Google Fonts CSS ───────────────────────┐
0.5s  │                                               │
1.0s  │                                               │
1.5s  │  ┌─ posts.json (1ms)                         │
      │  │  └─ 渲染文章列表                            │
1.6s  │  ← Google Fonts CSS 返回 ────────────────────┘
      │  └─ Google Fonts woff2 × 2 ──────────────────┐
2.0s  │                                               │
2.5s  │  ┌─ JavaScript 延迟 1.5s 后开始加载字体        │
3.0s  │  │  └─ 三极古拙楷书简.ttf (4.9MB) ──────────┐ │
3.2s  │  ← Google Fonts woff2 返回 ─────────────────┘ │
      │                                               │
4.0s  │                                               │ (WiFi)
5.0s  │  ← TTF 字体下载完成 ──────────────────────────┘
      │  └─ 第三次字体切换，布局重排
      │
      │  (4G网络下字体需 ~8-10s 才能下载完)
```

---

## 优化建议优先级

| 优先级 | 建议 | 预估效果 |
|--------|------|----------|
| P0 | 将 TTF 字体转换为 WOFF2 格式 | 字体体积减少 40-60% (4.9MB → ~2MB) |
| P0 | 移除 Google Fonts 引用（它们只是备选，最终被覆盖） | 首屏加速 ~1.6s |
| P0 | 在 index.html 中引入 font.css，利用 @font-face + font-display: swap | 消除 JS 延迟加载的 1.5s 等待 |
| P1 | 添加 `<link rel="preload">` 预加载字体和 posts.json | 提前开始下载关键资源 |
| P1 | 使用支持压缩和缓存的 Web 服务器（如 Caddy/Nginx） | 传输体积减少 50%+ |
| P2 | 将微信图片下载到本地存储 | 消除代理延迟，图片加载加速 10x+ |
| P2 | 为微信图片代理域名添加 dns-prefetch | 减少 DNS 解析时间 |
| P3 | 构建搜索索引替代实时全文扫描 | 搜索响应从秒级降到毫秒级 |
