# 懒人日报 - 部署指南

## 概述

这是一个静态新闻网站，支持多用户共享历史数据。使用云存储服务实现数据持久化，完全适合部署到 Vercel 等静态托管平台。

## 功能特性

- 📰 每日新闻早报展示
- 📚 历史数据查看和搜索
- 🔊 语音播报功能
- 💾 云端数据同步
- 📱 响应式设计
- 🚀 静态部署友好

## 部署到 Vercel

### 1. 准备工作

#### 选择云存储服务

**方案一：JSONBin.io（推荐）**
1. 访问 [JSONBin.io](https://jsonbin.io/)
2. 注册账号并获取 API Key
3. 创建一个新的 Bin，记录 Bin ID

**方案二：GitHub Gist**
1. 在 GitHub 创建 Personal Access Token
2. 创建一个新的 Gist，记录 Gist ID

### 2. 配置设置

编辑 `config.js` 文件：

```javascript
const CONFIG = {
    JSONBIN: {
        API_KEY: '$2a$10$YOUR_ACTUAL_API_KEY',  // 替换为真实的 API Key
        BIN_ID: 'YOUR_ACTUAL_BIN_ID',          // 替换为真实的 Bin ID
        BASE_URL: 'https://api.jsonbin.io/v3'
    },
    STORAGE: {
        TYPE: 'jsonbin',  // 使用 JSONBin.io
        CACHE_EXPIRE: 5 * 60 * 1000,
        MAX_RETRIES: 3,
        RETRY_DELAY: 1000
    }
};
```

### 3. 部署步骤

1. **Fork 或下载项目**
   ```bash
   git clone <your-repo-url>
   cd salary/news
   ```

2. **配置云存储**
   - 按照上述步骤配置 `config.js`

3. **部署到 Vercel**
   - 方法一：通过 Vercel CLI
     ```bash
     npm i -g vercel
     vercel --prod
     ```
   
   - 方法二：通过 Vercel 网站
     1. 访问 [vercel.com](https://vercel.com)
     2. 连接你的 Git 仓库
     3. 设置项目根目录为 `salary/news`
     4. 点击部署

### 4. 环境变量（可选）

为了安全起见，可以将敏感信息设置为环境变量：

在 Vercel 项目设置中添加：
- `JSONBIN_API_KEY`: 你的 JSONBin API Key
- `JSONBIN_BIN_ID`: 你的 Bin ID

然后修改 `config.js` 使用环境变量：
```javascript
const CONFIG = {
    JSONBIN: {
        API_KEY: process.env.JSONBIN_API_KEY || '$2a$10$fallback_key',
        BIN_ID: process.env.JSONBIN_BIN_ID || 'fallback_bin_id',
        BASE_URL: 'https://api.jsonbin.io/v3'
    }
};
```

## 本地开发

1. **启动本地服务器**
   ```bash
   # 使用 Python
   python -m http.server 8000
   
   # 或使用 Node.js
   npx serve .
   ```

2. **访问应用**
   打开浏览器访问 `http://localhost:8000`

## 数据存储说明

### 存储架构
- **云存储**: 主要数据存储，支持多用户共享
- **本地存储**: 缓存和备份，离线时可用
- **双重保障**: 云存储失败时自动降级到本地存储

### 数据格式
```javascript
{
    "date": "2024-01-15",
    "news": [
        {
            "title": "新闻标题",
            "content": "新闻内容",
            "source": "来源"
        }
    ],
    "image": "base64_image_data",
    "source": "api"
}
```

## 故障排除

### 常见问题

1. **云存储连接失败**
   - 检查 API Key 是否正确
   - 确认网络连接正常
   - 查看浏览器控制台错误信息

2. **数据不同步**
   - 清除浏览器缓存
   - 检查云存储服务状态
   - 验证配置文件设置

3. **部署失败**
   - 确认所有文件都已上传
   - 检查 Vercel 构建日志
   - 验证项目结构正确

### 调试模式

在浏览器控制台中启用详细日志：
```javascript
localStorage.setItem('debug', 'true');
```

## 技术栈

- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **存储**: JSONBin.io / GitHub Gist
- **部署**: Vercel / Netlify / GitHub Pages
- **样式**: 原生 CSS + Flexbox/Grid
- **API**: Fetch API + Async/Await

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