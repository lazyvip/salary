#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase直接API爬虫 - 直接从Supabase数据库获取所有故事
"""

import requests
import json
import sqlite3
import time
from datetime import datetime

class SupabaseDirectCrawler:
    def __init__(self):
        # Supabase配置（从JS文件中提取）
        self.supabase_url = "https://cxtvmolpayeplvdxcjvf.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN4dHZtb2xwYXllcGx2ZHhjanZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NTE0NTgsImV4cCI6MjA2MTEyNzQ1OH0.LIBg-OUlZHE6jtct1hRBFn1uOw6upqyDOCK-qBqaXic"
        
        # API端点
        self.rest_url = f"{self.supabase_url}/rest/v1"
        
        # 请求头
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # 数据存储
        self.stories = []
        self.story_contents = []
        self.categories = []
        
        print("🚀 Supabase直接API爬虫初始化完成")
        print(f"📡 API端点: {self.rest_url}")

    def fetch_table_data(self, table_name, limit=1000, offset=0, order_by=None):
        """从Supabase表中获取数据"""
        try:
            url = f"{self.rest_url}/{table_name}"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            if order_by:
                params['order'] = order_by
            
            print(f"🔍 获取表 {table_name} 数据 (limit={limit}, offset={offset})")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ 成功获取 {len(data)} 条记录")
            
            return data
            
        except Exception as e:
            print(f"❌ 获取表 {table_name} 失败: {e}")
            return []

    def get_all_table_data(self, table_name, order_by=None):
        """获取表的所有数据（处理分页）"""
        all_data = []
        offset = 0
        limit = 1000
        
        print(f"📊 开始获取表 {table_name} 的所有数据...")
        
        while True:
            batch_data = self.fetch_table_data(table_name, limit, offset, order_by)
            
            if not batch_data:
                break
                
            all_data.extend(batch_data)
            
            if len(batch_data) < limit:
                # 已经获取完所有数据
                break
                
            offset += limit
            time.sleep(0.5)  # 避免请求过快
        
        print(f"🎉 表 {table_name} 总共获取 {len(all_data)} 条记录")
        return all_data

    def crawl_categories(self):
        """获取所有分类"""
        print("\n" + "="*50)
        print("📂 开始获取故事分类...")
        print("="*50)
        
        self.categories = self.get_all_table_data('story_category', 'id')
        
        if self.categories:
            print(f"📋 分类列表:")
            for category in self.categories[:10]:  # 显示前10个
                print(f"   - ID: {category.get('id')}, 名称: {category.get('name', 'N/A')}")
            
            if len(self.categories) > 10:
                print(f"   ... 还有 {len(self.categories) - 10} 个分类")
        
        return self.categories

    def crawl_stories(self):
        """获取所有故事主要信息"""
        print("\n" + "="*50)
        print("📚 开始获取故事主要信息...")
        print("="*50)
        
        self.stories = self.get_all_table_data('story_main', 'id')
        
        if self.stories:
            print(f"📖 故事列表预览:")
            for story in self.stories[:5]:  # 显示前5个
                print(f"   - ID: {story.get('id')}")
                print(f"     标题: {story.get('title', 'N/A')}")
                print(f"     分类ID: {story.get('category_id', 'N/A')}")
                print(f"     创建时间: {story.get('created_at', 'N/A')}")
                print()
            
            if len(self.stories) > 5:
                print(f"   ... 还有 {len(self.stories) - 5} 个故事")
        
        return self.stories

    def crawl_story_contents(self):
        """获取所有故事内容"""
        print("\n" + "="*50)
        print("📝 开始获取故事内容...")
        print("="*50)
        
        self.story_contents = self.get_all_table_data('story_content', 'story_id')
        
        if self.story_contents:
            print(f"📄 内容列表预览:")
            for content in self.story_contents[:3]:  # 显示前3个
                story_id = content.get('story_id')
                content_text = content.get('content', '')
                print(f"   - 故事ID: {story_id}")
                print(f"     内容长度: {len(content_text)} 字符")
                print(f"     内容预览: {content_text[:100]}...")
                print()
            
            if len(self.story_contents) > 3:
                print(f"   ... 还有 {len(self.story_contents) - 3} 个故事内容")
        
        return self.story_contents

    def save_to_json(self):
        """保存数据到JSON文件"""
        print("\n💾 保存数据到JSON文件...")
        
        # 保存分类
        with open('supabase_categories.json', 'w', encoding='utf-8') as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)
        print(f"✅ 分类数据已保存: supabase_categories.json ({len(self.categories)} 条)")
        
        # 保存故事主要信息
        with open('supabase_stories.json', 'w', encoding='utf-8') as f:
            json.dump(self.stories, f, ensure_ascii=False, indent=2)
        print(f"✅ 故事数据已保存: supabase_stories.json ({len(self.stories)} 条)")
        
        # 保存故事内容
        with open('supabase_story_contents.json', 'w', encoding='utf-8') as f:
            json.dump(self.story_contents, f, ensure_ascii=False, indent=2)
        print(f"✅ 故事内容已保存: supabase_story_contents.json ({len(self.story_contents)} 条)")

    def save_to_sqlite(self):
        """保存数据到SQLite数据库"""
        print("\n💾 保存数据到SQLite数据库...")
        
        conn = sqlite3.connect('supabase_complete_stories.db')
        cursor = conn.cursor()
        
        try:
            # 创建分类表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 创建故事表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    category_id INTEGER,
                    excerpt TEXT,
                    reading_time INTEGER,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            
            # 创建故事内容表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS story_contents (
                    id INTEGER PRIMARY KEY,
                    story_id INTEGER,
                    content TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (story_id) REFERENCES stories (id)
                )
            ''')
            
            # 插入分类数据
            if self.categories:
                cursor.execute('DELETE FROM categories')  # 清空旧数据
                for category in self.categories:
                    cursor.execute('''
                        INSERT INTO categories (id, name, description, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        category.get('id'),
                        category.get('name'),
                        category.get('description'),
                        category.get('created_at'),
                        category.get('updated_at')
                    ))
                print(f"✅ 分类数据已插入: {len(self.categories)} 条")
            
            # 插入故事数据
            if self.stories:
                cursor.execute('DELETE FROM stories')  # 清空旧数据
                for story in self.stories:
                    cursor.execute('''
                        INSERT INTO stories (id, title, category_id, excerpt, reading_time, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        story.get('id'),
                        story.get('title'),
                        story.get('category_id'),
                        story.get('excerpt'),
                        story.get('reading_time'),
                        story.get('created_at'),
                        story.get('updated_at')
                    ))
                print(f"✅ 故事数据已插入: {len(self.stories)} 条")
            
            # 插入故事内容数据
            if self.story_contents:
                cursor.execute('DELETE FROM story_contents')  # 清空旧数据
                for content in self.story_contents:
                    cursor.execute('''
                        INSERT INTO story_contents (id, story_id, content, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        content.get('id'),
                        content.get('story_id'),
                        content.get('content'),
                        content.get('created_at'),
                        content.get('updated_at')
                    ))
                print(f"✅ 故事内容已插入: {len(self.story_contents)} 条")
            
            conn.commit()
            print("✅ SQLite数据库保存完成: supabase_complete_stories.db")
            
        except Exception as e:
            print(f"❌ SQLite保存失败: {e}")
            conn.rollback()
        finally:
            conn.close()

    def generate_report(self):
        """生成爬取报告"""
        report = {
            "crawl_time": datetime.now().isoformat(),
            "supabase_url": self.supabase_url,
            "tables_crawled": {
                "story_category": len(self.categories),
                "story_main": len(self.stories),
                "story_content": len(self.story_contents)
            },
            "total_records": len(self.categories) + len(self.stories) + len(self.story_contents),
            "files_generated": [
                "supabase_categories.json",
                "supabase_stories.json", 
                "supabase_story_contents.json",
                "supabase_complete_stories.db",
                "supabase_crawl_report.json"
            ]
        }
        
        # 添加分类统计
        if self.categories:
            report["category_stats"] = {
                "total_categories": len(self.categories),
                "category_names": [cat.get('name') for cat in self.categories[:10]]
            }
        
        # 添加故事统计
        if self.stories:
            category_counts = {}
            for story in self.stories:
                cat_id = story.get('category_id')
                category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
            
            report["story_stats"] = {
                "total_stories": len(self.stories),
                "stories_by_category": category_counts,
                "avg_reading_time": sum(s.get('reading_time', 0) for s in self.stories) / len(self.stories) if self.stories else 0
            }
        
        # 保存报告
        with open('supabase_crawl_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report

    def run_full_crawl(self):
        """执行完整爬取"""
        print("🚀 开始Supabase完整数据爬取...")
        print("="*60)
        
        start_time = time.time()
        
        try:
            # 1. 获取分类
            self.crawl_categories()
            
            # 2. 获取故事
            self.crawl_stories()
            
            # 3. 获取故事内容
            self.crawl_story_contents()
            
            # 4. 保存数据
            self.save_to_json()
            self.save_to_sqlite()
            
            # 5. 生成报告
            report = self.generate_report()
            
            end_time = time.time()
            duration = end_time - start_time
            
            print("\n" + "="*60)
            print("🎉 Supabase数据爬取完成！")
            print("="*60)
            print(f"⏱️  总耗时: {duration:.2f} 秒")
            print(f"📊 总记录数: {report['total_records']}")
            print(f"📂 分类数: {len(self.categories)}")
            print(f"📚 故事数: {len(self.stories)}")
            print(f"📝 内容数: {len(self.story_contents)}")
            print("\n📁 生成的文件:")
            for file in report['files_generated']:
                print(f"   - {file}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 爬取过程中出现错误: {e}")
            return False

if __name__ == "__main__":
    crawler = SupabaseDirectCrawler()
    success = crawler.run_full_crawl()
    
    if success:
        print("\n✅ 所有故事数据已成功获取！")
    else:
        print("\n❌ 爬取失败，请检查网络连接和API配置。")