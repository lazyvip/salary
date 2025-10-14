#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终故事爬虫 - 使用正确的URL模式
专门针对 https://storynook.cn/?id={数字} 格式优化
"""

import requests
import json
import time
import sqlite3
import os
import logging
from bs4 import BeautifulSoup
import random
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinalStoryCrawler:
    def __init__(self, max_workers=5):
        self.base_url = "https://storynook.cn"
        self.session = requests.Session()
        self.max_workers = max_workers
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 创建数据目录
        self.data_dir = "final_stories"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化数据库
        self.db_path = os.path.join(self.data_dir, "all_stories.db")
        self.init_database()
        
        # 线程锁
        self.db_lock = threading.Lock()
        
        # 统计信息
        self.stats = {
            'total_attempted': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'empty_stories': 0,
            'categories_found': set()
        }
        
        self.story_data = {}
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY,
                story_id INTEGER UNIQUE,
                title TEXT NOT NULL,
                content TEXT,
                category TEXT,
                url TEXT,
                word_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                story_count INTEGER DEFAULT 0
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_story_id ON stories(story_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON stories(category)')
        
        conn.commit()
        conn.close()
        logger.info(f"数据库初始化完成: {self.db_path}")
    
    def make_request(self, url, **kwargs):
        """发送HTTP请求，带重试机制"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 随机延迟
                time.sleep(random.uniform(0.5, 1.5))
                
                response = self.session.get(url, timeout=10, **kwargs)
                response.raise_for_status()
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.warning(f"请求失败: {url} - {e}")
                    return None
                time.sleep(random.uniform(1, 3))
        
        return None
    
    def extract_story_from_html(self, html_content, story_id, url):
        """从HTML中提取故事信息"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 提取标题 - 尝试多种选择器
        title = None
        title_selectors = [
            'h1', 'h2', '.title', '.story-title', 
            '.content-title', '.article-title', '.post-title',
            '[class*="title"]', '[id*="title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title and len(title) > 2 and title != "小故事铺":
                    break
        
        # 如果没找到专门的标题，从页面内容中提取
        if not title or title == "小故事铺":
            # 查找可能的标题模式
            text_content = soup.get_text()
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            for line in lines:
                if (len(line) > 3 and len(line) < 50 and 
                    not any(skip in line for skip in ['小故事铺', '首页', '导航', '菜单', '版权'])):
                    title = line
                    break
        
        # 提取内容
        content = None
        content_selectors = [
            '.content', '.story-content', '.article-content',
            '.post-content', '.text', '.story-text',
            'main', '.main-content', '#content',
            '[class*="content"]', '[class*="story"]',
            '[class*="article"]', '[class*="text"]'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text().strip()
                if content and len(content) > 50:
                    break
        
        # 如果没找到专门的内容区域，提取所有段落
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # 如果还是没有内容，提取主要文本
        if not content:
            # 移除导航、菜单等元素
            for elem in soup(['nav', 'header', 'footer', 'aside', '.nav', '.menu', '.header', '.footer']):
                elem.decompose()
            
            content = soup.get_text()
            # 清理内容
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
        
        # 推断分类
        category = self.infer_category(title, content)
        
        # 验证数据质量
        if not title:
            title = f"故事 {story_id}"
        
        if not content or len(content) < 20:
            return None
        
        # 清理内容
        content = self.clean_content(content)
        
        return {
            'story_id': story_id,
            'title': title,
            'content': content,
            'category': category,
            'url': url,
            'word_count': len(content),
            'created_at': datetime.now().isoformat()
        }
    
    def infer_category(self, title, content):
        """根据标题和内容推断分类"""
        text_to_analyze = f"{title} {content[:200]}".lower()
        
        category_keywords = {
            '睡前故事': ['睡前', '晚安', '梦', '床', '夜晚', '月亮', '星星'],
            '儿童故事': ['小朋友', '孩子', '宝宝', '幼儿', '小学', '童年'],
            '童话故事': ['公主', '王子', '魔法', '仙女', '巫师', '城堡', '森林'],
            '寓言故事': ['寓言', '道理', '教训', '智慧', '哲理'],
            '历史故事': ['古代', '历史', '朝代', '皇帝', '将军', '战争'],
            '神话故事': ['神话', '神仙', '天神', '龙', '凤凰', '传说'],
            '民间故事': ['民间', '传说', '老百姓', '村庄', '乡村'],
            '爱情故事': ['爱情', '恋人', '情侣', '结婚', '婚礼', '浪漫'],
            '励志故事': ['励志', '奋斗', '成功', '坚持', '努力', '梦想'],
            '恐怖故事': ['恐怖', '鬼', '幽灵', '害怕', '黑暗', '诡异']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                return category
        
        return '其他故事'
    
    def clean_content(self, content):
        """清理内容"""
        # 移除多余的空白
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # 移除常见的无用文本
        unwanted_patterns = [
            r'小故事铺.*?首页',
            r'版权所有.*',
            r'Copyright.*',
            r'All rights reserved.*',
            r'网站导航.*',
            r'返回首页.*'
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def crawl_story(self, story_id):
        """爬取单个故事"""
        url = f"{self.base_url}/?id={story_id}"
        
        try:
            response = self.make_request(url)
            if not response:
                self.stats['failed_downloads'] += 1
                return None
            
            story_data = self.extract_story_from_html(response.text, story_id, url)
            
            if story_data:
                self.save_story_to_db(story_data)
                self.stats['successful_downloads'] += 1
                self.stats['categories_found'].add(story_data['category'])
                
                logger.info(f"✅ 故事 {story_id}: {story_data['title'][:30]}... ({story_data['category']})")
                return story_data
            else:
                self.stats['empty_stories'] += 1
                logger.debug(f"❌ 故事 {story_id}: 内容为空或无效")
                return None
                
        except Exception as e:
            self.stats['failed_downloads'] += 1
            logger.warning(f"❌ 故事 {story_id} 爬取失败: {e}")
            return None
    
    def save_story_to_db(self, story):
        """保存故事到数据库"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO stories 
                    (story_id, title, content, category, url, word_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    story['story_id'],
                    story['title'],
                    story['content'],
                    story['category'],
                    story['url'],
                    story['word_count']
                ))
                
                # 更新分类统计
                cursor.execute('''
                    INSERT OR REPLACE INTO categories (name, story_count)
                    VALUES (?, (
                        SELECT COUNT(*) FROM stories WHERE category = ?
                    ))
                ''', (story['category'], story['category']))
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"保存故事到数据库失败: {e}")
            finally:
                conn.close()
    
    def crawl_range(self, start_id, end_id):
        """爬取指定范围的故事"""
        logger.info(f"开始爬取故事 {start_id} 到 {end_id}")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_id = {
                executor.submit(self.crawl_story, story_id): story_id 
                for story_id in range(start_id, end_id + 1)
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_id):
                story_id = future_to_id[future]
                self.stats['total_attempted'] += 1
                
                try:
                    story_data = future.result()
                    if story_data:
                        # 按分类组织数据
                        category = story_data['category']
                        if category not in self.story_data:
                            self.story_data[category] = []
                        self.story_data[category].append(story_data)
                
                except Exception as e:
                    logger.error(f"处理故事 {story_id} 结果时出错: {e}")
                
                # 每100个故事显示一次进度
                if self.stats['total_attempted'] % 100 == 0:
                    self.show_progress()
    
    def show_progress(self):
        """显示进度"""
        total = self.stats['total_attempted']
        success = self.stats['successful_downloads']
        failed = self.stats['failed_downloads']
        empty = self.stats['empty_stories']
        
        success_rate = (success / total * 100) if total > 0 else 0
        
        logger.info(f"📊 进度: {total} 个已尝试, {success} 个成功 ({success_rate:.1f}%), {failed} 个失败, {empty} 个空内容")
        logger.info(f"📚 已发现 {len(self.stats['categories_found'])} 个分类: {', '.join(list(self.stats['categories_found'])[:5])}...")
    
    def save_to_json(self):
        """保存数据到JSON文件"""
        if self.story_data:
            json_file = os.path.join(self.data_dir, "all_stories.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.story_data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到: {json_file}")
            return json_file
        return None
    
    def get_statistics(self):
        """获取最终统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总故事数
        cursor.execute("SELECT COUNT(*) FROM stories")
        total_stories = cursor.fetchone()[0]
        
        # 按分类统计
        cursor.execute("SELECT category, COUNT(*) FROM stories GROUP BY category ORDER BY COUNT(*) DESC")
        category_stats = cursor.fetchall()
        
        # 平均字数
        cursor.execute("SELECT AVG(word_count) FROM stories WHERE word_count > 0")
        avg_words = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_stories': total_stories,
            'categories': dict(category_stats),
            'average_words': int(avg_words),
            'attempted': self.stats['total_attempted'],
            'successful': self.stats['successful_downloads'],
            'failed': self.stats['failed_downloads'],
            'empty': self.stats['empty_stories']
        }
    
    def run(self, max_story_id=2000):
        """运行完整的爬取流程"""
        logger.info("🚀 开始最终故事爬取任务...")
        logger.info(f"目标网站: {self.base_url}")
        logger.info(f"URL模式: {self.base_url}/?id={{数字}}")
        logger.info(f"最大故事ID: {max_story_id}")
        logger.info(f"并发线程数: {self.max_workers}")
        
        start_time = datetime.now()
        
        # 分批爬取，避免一次性创建太多线程
        batch_size = 500
        for start_id in range(1, max_story_id + 1, batch_size):
            end_id = min(start_id + batch_size - 1, max_story_id)
            
            logger.info(f"🔄 爬取批次: {start_id} - {end_id}")
            self.crawl_range(start_id, end_id)
            
            # 批次间休息
            time.sleep(2)
        
        # 保存数据
        json_file = self.save_to_json()
        
        # 显示最终统计
        stats = self.get_statistics()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("=" * 60)
        logger.info("🎉 爬取任务完成！")
        logger.info("=" * 60)
        logger.info(f"⏱️  总耗时: {duration}")
        logger.info(f"📊 尝试爬取: {stats['attempted']} 个故事")
        logger.info(f"✅ 成功获取: {stats['total_stories']} 个故事")
        logger.info(f"❌ 失败: {stats['failed']} 个")
        logger.info(f"📝 平均字数: {stats['average_words']} 字")
        logger.info(f"📚 分类数量: {len(stats['categories'])} 个")
        
        logger.info("\n📋 分类统计:")
        for category, count in list(stats['categories'].items())[:10]:
            logger.info(f"  {category}: {count} 个故事")
        
        logger.info(f"\n💾 数据库文件: {self.db_path}")
        if json_file:
            logger.info(f"📄 JSON文件: {json_file}")
        
        return stats

def main():
    """主函数"""
    print("🚀 启动最终故事爬虫...")
    
    # 创建爬虫实例
    crawler = FinalStoryCrawler(max_workers=8)  # 增加并发数
    
    try:
        # 运行爬取任务，尝试爬取前2000个故事
        stats = crawler.run(max_story_id=2000)
        
        print(f"\n🎉 任务完成！成功获取了 {stats['total_stories']} 个故事！")
        print(f"📊 成功率: {stats['total_stories']/stats['attempted']*100:.1f}%")
        
        return stats
        
    except KeyboardInterrupt:
        logger.info("用户中断爬取")
        return crawler.get_statistics()
    except Exception as e:
        logger.error(f"爬取过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()