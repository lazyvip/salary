# 懒人日报网页版

📰 每日新闻早报，60秒读懂世界

## 项目简介

懒人日报网页版是基于微信小程序版本开发的响应式网站，提供每日新闻早报和历史早报查看功能。采用现代化的设计风格，支持多种设备访问。

## 功能特性

### 核心功能
- 📱 **每日早报**: 自动获取最新的每日新闻早报
- 📚 **历史早报**: 查看历史新闻记录，支持本地存储
- 🎨 **响应式设计**: 适配手机、平板、桌面等多种设备
- 💾 **本地存储**: 自动保存历史记录，离线也能查看

### 交互功能
- 🖼️ **图片预览**: 点击图片可全屏查看
- 📋 **一键复制**: 复制新闻文本到剪贴板
- 💾 **图片保存**: 下载新闻图片到本地
- 📤 **分享功能**: 支持多种分享方式
- 🔄 **自动刷新**: 定时获取最新新闻内容

### 用户体验
- ⚡ **快速加载**: 优化的加载速度和缓存策略
- 🎯 **直观导航**: 简洁明了的标签页切换
- 🌈 **美观界面**: 渐变背景和卡片式设计
- 📱 **移动优先**: 针对移动设备优化的交互体验

## 技术栈

- **前端**: HTML5 + CSS3 + JavaScript (ES6+)
- **样式**: CSS Grid + Flexbox + CSS动画
- **数据**: LocalStorage + REST API
- **部署**: 静态网站托管 (Netlify/Vercel)

## 项目结构

```
懒人日报网页版/
├── index.html          # 主页面
├── styles.css          # 样式文件
├── script.js           # 脚本文件
├── package.json        # 项目配置
└── README.md          # 项目说明
```

## 快速开始

### 本地开发

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd 懒人日报网页版
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **启动开发服务器**
   ```bash
   npm run dev
   ```

4. **访问网站**
   打开浏览器访问 `http://localhost:3000`

### 直接使用

也可以直接打开 `index.html` 文件在浏览器中运行。

## 部署指南

### Netlify 部署

1. **方式一：拖拽部署**
   - 访问 [Netlify](https://netlify.com)
   - 将项目文件夹拖拽到部署区域
   - 等待部署完成

2. **方式二：Git 部署**
   - 将代码推送到 GitHub/GitLab
   - 在 Netlify 中连接仓库
   - 设置构建命令：`npm run build`
   - 设置发布目录：`./`

### Vercel 部署

1. **安装 Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **部署项目**
   ```bash
   vercel
   ```

3. **跟随提示完成部署**

### GitHub Pages 部署

1. **推送到 GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **启用 GitHub Pages**
   - 进入仓库设置
   - 找到 Pages 选项
   - 选择 main 分支作为源

## 配置说明

### API 配置

项目使用阿里云API获取新闻数据，如需修改API配置，请编辑 `script.js` 文件中的相关参数：

```javascript
// API配置
const API_CONFIG = {
    url: 'https://v3.alapi.cn/api/zaobao',
    token: 'your-api-token',
    format: 'json'
};
```

### 本地存储

- 历史记录存储在浏览器的 LocalStorage 中
- 默认保存最近30天的记录
- 可在 `script.js` 中修改存储天数

## 浏览器支持

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ 移动端浏览器

## 更新日志

### v1.0.0 (2024-12-20)
- 🎉 初始版本发布
- ✨ 实现每日早报功能
- ✨ 实现历史早报功能
- ✨ 响应式设计
- ✨ 本地存储支持

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 📱 公众号：懒人搜索
- 📧 邮箱：contact@lazy-search.com
- 🌐 网站：https://lazy-search.com

## 致谢

- 感谢阿里云提供的新闻API服务
- 感谢所有贡献者的支持

---

⭐ 如果这个项目对你有帮助，请给个星标支持一下！