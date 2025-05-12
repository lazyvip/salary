import { useState, useRef } from 'react'
import 'markdown-to-image/dist/style.css'
import { Md2Poster, Md2PosterContent, Md2PosterHeader, Md2PosterFooter } from 'markdown-to-image'
import './App.css'

function App() {
  const [markdown, setMarkdown] = useState(`# Markdown转图片示例

> 这是一个简单的Markdown转图片工具示例

## 功能特点

- 支持Markdown语法渲染
- 多种主题可选
- 一键导出为图片
- 实时预览效果

![示例图片](https://picsum.photos/600/300)

## 代码示例

\`\`\`javascript
const hello = () => {
  console.log("Hello, Markdown!");
};
\`\`\`

## 表格支持

| 功能 | 状态 |
| ---- | ---- |
| Markdown渲染 | ✅ |
| 主题切换 | ✅ |
| 导出图片 | ✅ |
| 实时预览 | ✅ |
`)
  const [theme, setTheme] = useState('default')
  const [header, setHeader] = useState('Markdown转图片工具')
  const [footer, setFooter] = useState('Powered by markdown-to-image')
  const posterRef = useRef(null)

  const themes = [
    { id: 'default', name: '默认主题' },
    { id: 'dark', name: '暗色主题' },
    { id: 'light', name: '亮色主题' },
    { id: 'elegant', name: '优雅主题' },
    { id: 'minimal', name: '简约主题' },
    { id: 'vibrant', name: '活力主题' },
    { id: 'professional', name: '专业主题' },
    { id: 'creative', name: '创意主题' },
    { id: 'modern', name: '现代主题' }
  ]

  const exportAsImage = async () => {
    if (!posterRef.current) return
    
    try {
      const posterElement = posterRef.current
      
      // 使用html2canvas或其他库将DOM元素转换为图片
      // 这里使用简单的方法：复制到剪贴板
      const selection = window.getSelection()
      const range = document.createRange()
      range.selectNodeContents(posterElement)
      selection.removeAllRanges()
      selection.addRange(range)
      document.execCommand('copy')
      selection.removeAllRanges()
      
      alert('海报已复制到剪贴板，可以粘贴到图片编辑器中保存')
    } catch (error) {
      console.error('导出图片失败:', error)
      alert('导出图片失败，请重试')
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Markdown转图片工具</h1>
        <p>将你的Markdown文本转换为精美的图片海报</p>
      </header>

      <main className="app-main">
        <div className="editor-section">
          <div className="editor-header">
            <h2>编辑器</h2>
            <div className="editor-controls">
              <div className="control-group">
                <label htmlFor="header-input">页眉:</label>
                <input
                  id="header-input"
                  type="text"
                  value={header}
                  onChange={(e) => setHeader(e.target.value)}
                  placeholder="输入页眉文本"
                />
              </div>
              <div className="control-group">
                <label htmlFor="footer-input">页脚:</label>
                <input
                  id="footer-input"
                  type="text"
                  value={footer}
                  onChange={(e) => setFooter(e.target.value)}
                  placeholder="输入页脚文本"
                />
              </div>
              <div className="control-group">
                <label htmlFor="theme-select">主题:</label>
                <select
                  id="theme-select"
                  value={theme}
                  onChange={(e) => setTheme(e.target.value)}
                >
                  {themes.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          <textarea
            className="markdown-editor"
            value={markdown}
            onChange={(e) => setMarkdown(e.target.value)}
            placeholder="在这里输入Markdown文本..."
          />
        </div>

        <div className="preview-section">
          <div className="preview-header">
            <h2>预览</h2>
            <button className="export-button" onClick={exportAsImage}>
              导出图片
            </button>
          </div>
          <div className="preview-container" ref={posterRef}>
            <Md2Poster theme={theme}>
              {header && <Md2PosterHeader>{header}</Md2PosterHeader>}
              <Md2PosterContent>{markdown}</Md2PosterContent>
              {footer && <Md2PosterFooter>{footer}</Md2PosterFooter>}
            </Md2Poster>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>基于 <a href="https://github.com/gcui-art/markdown-to-image" target="_blank" rel="noopener noreferrer">markdown-to-image</a> 开源项目</p>
      </footer>
    </div>
  )
}

export default App
// Add custom styling and margin options
// Implement image download functionality
