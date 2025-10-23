# ChatGPT 提示词爬虫项目

本项目用于从 [ExplainThis ChatGPT 指令大全](https://www.explainthis.io/zh-hans/chatgpt) 网站爬取 ChatGPT 提示词和分类信息，并将数据组织成 JSON 格式供后续使用。

## 项目文件说明

### 核心文件
- `chatgpt_prompt_crawler.py` - 主要的爬虫程序
- `chatgpt_prompts.json` - 爬取的数据文件（JSON格式）
- `validate_data.py` - 数据验证脚本
- `usage_example.py` - 使用示例和交互式管理器

### 辅助文件
- `crawler.py` - 初期的网页结构分析脚本
- `actual_page.html` - 爬取的原始网页内容
- `actual_page_formatted.html` - 格式化后的网页内容
- `sour.html` - 用户提供的页面源码（用于对比）

## 数据结构

爬取的 JSON 数据包含以下结构：

```json
{
  "metadata": {
    "source_url": "https://www.explainthis.io/zh-hans/chatgpt",
    "crawl_time": "2025-10-22 19:14:09",
    "total_categories": 19,
    "total_prompts": 94,
    "category_stats": {
      "求职与面试": 11,
      "程式开发": 6,
      // ... 其他分类统计
    }
  },
  "categories": [
    "全部", "求职与面试", "职涯发展", "写报告", 
    // ... 所有分类列表
  ],
  "prompts_by_category": {
    "求职与面试": [
      {
        "title": "寻求履历的反馈",
        "content": "这份职位的履历，有哪边可以写更好? ...",
        "parameters": ["职位", "附上履历"],
        "category": "求职与面试"
      }
      // ... 更多提示词
    ]
    // ... 其他分类的提示词
  },
  "all_prompts": [
    // 所有提示词的完整列表
  ]
}
```

## 使用方法

### 1. 运行爬虫

```bash
python chatgpt_prompt_crawler.py
```

这将：
- 从目标网站爬取最新的提示词数据
- 自动解析分类和提示词内容
- 提取参数占位符
- 保存为 `chatgpt_prompts.json` 文件

### 2. 验证数据

```bash
python validate_data.py
```

这将验证：
- JSON 文件格式正确性
- 数据结构完整性
- 提示词字段完整性
- 分类分布统计

### 3. 使用数据

#### 方式一：直接使用 JSON 文件
```python
import json

with open('chatgpt_prompts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 获取所有分类
categories = data['categories']

# 获取特定分类的提示词
dev_prompts = data['prompts_by_category']['程式开发']

# 获取所有提示词
all_prompts = data['all_prompts']
```

#### 方式二：使用提供的管理器
```bash
python usage_example.py
```

选择演示模式或交互模式来浏览和管理提示词。

#### 方式三：在代码中使用管理器
```python
from usage_example import PromptManager

# 初始化管理器
manager = PromptManager()

# 获取分类
categories = manager.get_categories()

# 按分类获取提示词
prompts = manager.get_prompts_by_category('程式开发')

# 搜索提示词
results = manager.search_prompts('面试')

# 获取随机提示词
random_prompt = manager.get_random_prompt()

# 格式化提示词
formatted = manager.format_prompt(random_prompt)
```

## 数据统计

截至最后一次爬取（2025-10-22 19:14:09）：

- **总分类数**: 19 个
- **总提示词数**: 94 个

### 分类分布
- 求职与面试: 11 个
- 写报告: 8 个
- 英语学习: 8 个
- 写作帮手: 7 个
- 程式开发: 6 个
- HR 与招募: 6 个
- 知识学习: 5 个
- 销售: 5 个
- 行销与 SEO: 5 个
- 投资与交易: 5 个
- 日常生活: 5 个
- 社群媒体: 4 个
- 产品管理: 4 个
- 职涯发展: 3 个
- 资料整理: 3 个
- 工作生产力: 3 个
- 有趣好玩: 3 个
- 角色扮演: 3 个

## 特性

### 爬虫特性
- ✅ 自动识别网页结构
- ✅ 提取完整的提示词内容
- ✅ 自动识别参数占位符
- ✅ 按分类组织数据
- ✅ 错误处理和重试机制
- ✅ 详细的爬取日志

### 数据特性
- ✅ 结构化 JSON 格式
- ✅ 包含元数据和统计信息
- ✅ 支持按分类和全局访问
- ✅ 参数占位符提取
- ✅ 分类归属信息

### 使用特性
- ✅ 数据验证工具
- ✅ 交互式管理器
- ✅ 搜索功能
- ✅ 随机提示词获取
- ✅ 参数填入示例

## 依赖要求

```
requests
beautifulsoup4
```

安装依赖：
```bash
pip install requests beautifulsoup4
```

## 注意事项

1. **网站结构变化**: 如果目标网站的 HTML 结构发生变化，可能需要更新爬虫代码
2. **访问频率**: 请合理控制爬取频率，避免对目标网站造成过大负担
3. **数据更新**: 建议定期运行爬虫以获取最新的提示词数据
4. **编码问题**: 所有文件都使用 UTF-8 编码，确保正确显示中文内容

## 许可证

本项目仅用于学习和研究目的。爬取的数据版权归原网站所有。

## 更新日志

- **2025-10-22**: 初始版本，成功爬取 94 个提示词，19 个分类
- 完整的数据验证和使用示例
- 交互式管理器功能