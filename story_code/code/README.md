# 故事网站爬虫

这是一个用于爬取 https://storynook.cn/ 网站所有故事的Python爬虫工具。

## 功能特点

- 🚀 **多种爬取方式**：支持API爬虫和网页抓取两种方式
- 🔄 **智能切换**：API失败时自动切换到网页抓取
- 📊 **完整分类**：支持所有10个故事分类的爬取
- 💾 **多格式存储**：支持JSON和SQLite数据库存储
- 🛡️ **错误处理**：完善的重试机制和错误处理
- 📈 **进度显示**：实时显示爬取进度和统计信息

## 支持的故事分类

1. 睡前故事 - 温馨治愈的睡前小故事
2. 儿童故事 - 适合孩子的有趣故事
3. 历史故事 - 了解历史的精彩故事
4. 恐怖故事 - 惊险刺激的恐怖小说
5. 爱情故事 - 浪漫感人的爱情小说
6. 励志故事 - 激励人心的正能量故事
7. 神话故事 - 古代神话传说故事
8. 寓言故事 - 富含哲理的寓言故事
9. 童话故事 - 经典童话故事大全
10. 民间故事 - 传统民间故事集

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 快速开始（推荐）

```bash
python main_crawler.py
```

这将使用混合模式，自动选择最佳的爬取方式。

### 2. 指定爬取方式

```bash
# 仅使用API爬虫
python main_crawler.py --method api

# 仅使用网页抓取
python main_crawler.py --method web

# 使用混合模式（默认）
python main_crawler.py --method hybrid

# 仅探索API（不爬取数据）
python main_crawler.py --method explore
```

### 3. 高级选项

```bash
# 爬取完成后合并结果
python main_crawler.py --merge

# 生成详细报告
python main_crawler.py --report

# 组合使用
python main_crawler.py --method hybrid --merge --report
```

### 4. 单独运行各个模块

```bash
# 运行API爬虫
python story_crawler.py

# 运行网页抓取器
python web_scraper.py

# 运行API探索器
python api_explorer.py
```

## 输出文件说明

### 数据文件
- `story_data/` - API爬虫的数据目录
  - `all_stories.json` - 所有故事的JSON格式数据
  - `stories.db` - SQLite数据库文件
- `scraped_stories/` - 网页抓取的数据目录
  - `all_stories.json` - 所有故事的JSON格式数据
  - `scraped_stories.db` - SQLite数据库文件
- `merged_stories.json` - 合并后的完整数据

### 报告文件
- `crawl_report_YYYYMMDD_HHMMSS.json` - 详细的爬取报告

## 脚本文件说明

- `main_crawler.py` - 主控制器，整合所有功能
- `story_crawler.py` - API爬虫，通过Supabase API获取数据
- `web_scraper.py` - 网页抓取器，直接解析HTML页面
- `api_explorer.py` - API探索器，尝试发现API密钥和端点

## 数据结构

### JSON格式
```json
{
  "分类名称": [
    {
      "id": "故事ID",
      "title": "故事标题",
      "content": "故事内容",
      "category": "故事分类",
      "word_count": "字数",
      "created_at": "创建时间"
    }
  ]
}
```

### SQLite数据库
- `categories` 表：存储分类信息
- `stories` 表：存储故事详细信息

## 注意事项

1. **网络连接**：确保网络连接稳定
2. **爬取频率**：脚本已内置延迟机制，避免过于频繁的请求
3. **存储空间**：确保有足够的磁盘空间存储数据
4. **Chrome浏览器**：如果使用Selenium功能，需要安装Chrome浏览器

## 故障排除

### 常见问题

1. **导入模块失败**
   - 确保所有脚本文件在同一目录下
   - 检查Python路径设置

2. **网络请求失败**
   - 检查网络连接
   - 尝试使用代理

3. **API访问失败**
   - 脚本会自动切换到网页抓取模式
   - 可以手动指定使用网页抓取：`--method web`

4. **Chrome驱动问题**
   - 确保Chrome浏览器已安装
   - 脚本会自动下载对应的ChromeDriver

## 技术特点

- **智能重试**：网络请求失败时自动重试
- **随机延迟**：避免被反爬虫机制检测
- **多线程安全**：支持并发爬取（如需要）
- **内存优化**：大数据量时的内存管理
- **日志记录**：详细的运行日志

## 许可证

本项目仅供学习和研究使用，请遵守网站的robots.txt和使用条款。