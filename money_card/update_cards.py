#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息差卡片合集自动更新脚本

功能：
1. 扫描历史html备份文件夹中的所有HTML文件
2. 自动更新index.html中的htmlFiles数组
3. 保持原有的JavaScript代码结构不变

使用方法：
在money_card目录下运行：python update_cards.py
"""

import os
import re
import sys
from pathlib import Path

def get_html_files(backup_dir):
    """获取历史备份文件夹中的所有HTML文件"""
    html_files = []
    
    if not os.path.exists(backup_dir):
        print(f"错误：备份文件夹不存在 - {backup_dir}")
        return html_files
    
    for file in os.listdir(backup_dir):
        if file.endswith('.html'):
            html_files.append(file)
    
    # 按文件名排序
    html_files.sort()
    return html_files

def update_index_html(index_file, html_files):
    """更新index.html文件中的htmlFiles数组"""
    if not os.path.exists(index_file):
        print(f"错误：index.html文件不存在 - {index_file}")
        return False
    
    # 读取原文件内容
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成新的htmlFiles数组内容
    files_array = "const htmlFiles = [\n"
    for file in html_files:
        files_array += f"            '{file}',\n"
    files_array += "        ];"
    
    # 使用正则表达式替换htmlFiles数组
    # 匹配从 "const htmlFiles = [" 到对应的 "];" 的内容
    pattern = r'const htmlFiles = \[.*?\];'
    
    if re.search(pattern, content, re.DOTALL):
        # 替换现有的htmlFiles数组
        new_content = re.sub(pattern, files_array, content, flags=re.DOTALL)
    else:
        print("警告：未找到htmlFiles数组，请检查index.html文件格式")
        return False
    
    # 写入更新后的内容
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    """主函数"""
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent
    
    # 定义文件路径
    backup_dir = script_dir / "历史html备份"
    index_file = script_dir / "index.html"
    
    print("=" * 50)
    print("信息差卡片合集自动更新脚本")
    print("=" * 50)
    
    # 获取HTML文件列表
    print(f"正在扫描备份文件夹：{backup_dir}")
    html_files = get_html_files(backup_dir)
    
    if not html_files:
        print("未找到任何HTML文件")
        return
    
    print(f"找到 {len(html_files)} 个HTML文件：")
    for i, file in enumerate(html_files, 1):
        print(f"  {i:2d}. {file}")
    
    # 更新index.html文件
    print(f"\n正在更新：{index_file}")
    if update_index_html(index_file, html_files):
        print("✅ 更新成功！")
        print(f"\n📊 统计信息：")
        print(f"   - 总卡片数量：{len(html_files)}")
        print(f"   - 备份文件夹：{backup_dir.name}")
        print(f"   - 更新时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ 更新失败！")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("更新完成！现在可以刷新浏览器查看最新的卡片列表。")
    print("=" * 50)

if __name__ == "__main__":
    main()