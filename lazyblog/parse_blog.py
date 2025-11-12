import os
import json
import re
from datetime import datetime

def parse_filename(filename):
    """解析文件名，提取日期和标题"""
    # 移除 .md 后缀
    name = filename.replace('.md', '')
    
    # 尝试匹配日期格式 YYYYMMDD
    date_match = re.match(r'^(\d{8})', name)
    if date_match:
        date_str = date_match.group(1)
        # 转换为 YYYY-MM-DD 格式
        date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        # 标题是剩余部分
        title = name[8:]
        return date, title
    
    # 尝试匹配日期格式 YYMMDD
    date_match = re.match(r'^(\d{6})', name)
    if date_match:
        date_str = date_match.group(1)
        # 转换为 20YY-MM-DD 格式
        date = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}"
        # 标题是剩余部分
        title = name[6:]
        return date, title
    
    # 如果没有日期，使用文件名作为标题
    return None, name

def read_markdown_content(filepath):
    """读取 markdown 文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"读取文件 {filepath} 失败: {e}")
        return ""

def generate_blog_json():
    """生成博客文章 JSON 数据"""
    files_dir = 'files'
    articles = []
    
    # 获取所有 markdown 文件
    md_files = [f for f in os.listdir(files_dir) if f.endswith('.md')]
    
    for filename in md_files:
        filepath = os.path.join(files_dir, filename)
        date, title = parse_filename(filename)
        content = read_markdown_content(filepath)
        
        # 提取摘要（前200个字符）
        summary = content[:200].replace('\n', ' ').strip() + '...' if len(content) > 200 else content
        
        article = {
            'id': filename.replace('.md', ''),
            'filename': filename,
            'date': date or '未知日期',
            'title': title,
            'content': content,
            'summary': summary
        }
        articles.append(article)
    
    # 按日期排序（新的在前面）
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    # 保存为 JSON
    with open('articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"成功生成 {len(articles)} 篇文章的 JSON 数据")
    return articles

if __name__ == '__main__':
    generate_blog_json()
