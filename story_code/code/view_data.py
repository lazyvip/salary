#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json

def view_database_sample():
    """查看数据库中的故事样本"""
    try:
        conn = sqlite3.connect('quick_stories.db')
        cursor = conn.cursor()
        
        # 获取总数
        cursor.execute('SELECT COUNT(*) FROM stories')
        total_count = cursor.fetchone()[0]
        print(f"数据库中共有 {total_count} 个故事")
        print("-" * 50)
        
        # 获取前10个故事
        cursor.execute('SELECT title, category_name, length FROM stories LIMIT 10')
        print("前10个故事:")
        for i, row in enumerate(cursor.fetchall(), 1):
            print(f"{i:2d}. {row[0]} ({row[1]}, {row[2]}字)")
        
        print("-" * 50)
        
        # 统计信息
        cursor.execute('SELECT MIN(length), MAX(length), AVG(length) FROM stories')
        min_len, max_len, avg_len = cursor.fetchone()
        print(f"字数统计:")
        print(f"  最短: {min_len}字")
        print(f"  最长: {max_len}字")
        print(f"  平均: {avg_len:.1f}字")
        
        conn.close()
        
    except Exception as e:
        print(f"查看数据库时出错: {e}")

def view_json_sample():
    """查看JSON文件样本"""
    try:
        with open('quick_stories.json', 'r', encoding='utf-8') as f:
            stories = json.load(f)
        
        print(f"\nJSON文件中共有 {len(stories)} 个故事")
        print("-" * 50)
        print("第一个故事的完整信息:")
        if stories:
            first_story = stories[0]
            for key, value in first_story.items():
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"查看JSON文件时出错: {e}")

if __name__ == "__main__":
    print("=== 小故事铺爬虫数据查看 ===")
    view_database_sample()
    view_json_sample()
    print("\n=== 数据查看完成 ===")