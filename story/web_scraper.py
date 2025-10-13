#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页抓取器 - 直接从storynook.cn网页抓取故事内容
当API无法访问时的备用方案
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
import sqlite3
from datetime import datetime
import logging
import random
from urllib.parse import urljoin, urlparse
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        """初始化网页抓取器"""
        self.base_url = "https://storynook.cn/"
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 创建数据目录
        self.data_dir = "scraped_stories"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # 初始化数据库
        self.init_database()
        
        # 故事分类
        self.categories = {
            "睡前故事": "bedtime",
            "儿童故事": "children", 
            "历史故事": "history",
            "恐怖故事": "horror",
            "爱情故事": "love",
            "励志故事": "inspirational",
            "神话故事": "mythology",
            "寓言故事": "fable",
            "童话故事": "fairy",
            "民间故事": "folk"
        }
        
    def init_database(self):
        """初始化数据库"""
        self.db_path = os.path.join(self.data_dir, "scraped_stories.db")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                content TEXT,
                word_count INTEGER,
                url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def get_page_content(self, url: str, max_retries: int = 3) -> BeautifulSoup:
        """获取页面内容"""
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(1, 3))  # 随机延迟
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # 尝试检测编码
                response.encoding = response.apparent_encoding or 'utf-8'
                
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup
                
            except Exception as e:
                logger.warning(f"获取页面失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
        return None
    
    def extract_stories_from_homepage(self) -> list:
        """从首页提取故事链接"""
        logger.info("从首页提取故事链接...")
        
        soup = self.get_page_content(self.base_url)
        if not soup:
            logger.error("无法获取首页内容")
            return []
        
        stories = []
        
        # 查找故事链接的多种模式
        link_selectors = [
            'a[href*="story"]',
            'a[href*="tale"]',
            'a[href*="read"]',
            '.story-item a',
            '.story-link',
            'a[title*="故事"]'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                title = link.get_text(strip=True) or link.get('title', '')
                
                if href and title and len(title) > 2:
                    full_url = urljoin(self.base_url, href)
                    stories.append({
                        'title': title,
                        'url': full_url,
                        'category': self.guess_category(title)
                    })
        
        # 去重
        seen_urls = set()
        unique_stories = []
        for story in stories:
            if story['url'] not in seen_urls:
                seen_urls.add(story['url'])
                unique_stories.append(story)
        
        logger.info(f"从首页提取到 {len(unique_stories)} 个故事链接")
        return unique_stories
    
    def guess_category(self, title: str) -> str:
        """根据标题猜测故事分类"""
        title_lower = title.lower()
        
        category_keywords = {
            "睡前故事": ["睡前", "晚安", "梦", "月亮", "星星"],
            "儿童故事": ["小", "宝宝", "孩子", "儿童"],
            "童话故事": ["公主", "王子", "魔法", "仙女", "巫师"],
            "动物故事": ["小猫", "小狗", "小兔", "小鸟", "动物"],
            "寓言故事": ["狐狸", "乌鸦", "寓言", "道理"],
            "神话故事": ["神", "仙", "龙", "凤凰", "传说"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in title for keyword in keywords):
                return category
                
        return "其他故事"
    
    def extract_story_content(self, story_url: str) -> dict:
        """提取单个故事的内容"""
        logger.info(f"提取故事内容: {story_url}")
        
        soup = self.get_page_content(story_url)
        if not soup:
            return None
        
        story_data = {
            'url': story_url,
            'title': '',
            'content': '',
            'word_count': 0
        }
        
        # 提取标题的多种方式
        title_selectors = [
            'h1',
            '.story-title',
            '.title',
            'title',
            '.post-title',
            '.article-title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                story_data['title'] = title_elem.get_text(strip=True)
                break
        
        # 提取内容的多种方式
        content_selectors = [
            '.story-content',
            '.content',
            '.post-content',
            '.article-content',
            '.story-text',
            'main',
            '.main-content'
        ]
        
        content_text = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 移除脚本和样式标签
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                content_text = content_elem.get_text(separator='\n', strip=True)
                if len(content_text) > 100:  # 确保内容足够长
                    break
        
        # 如果没有找到专门的内容区域，尝试从整个页面提取
        if len(content_text) < 100:
            # 移除导航、页脚等无关内容
            for unwanted in soup(["nav", "footer", "header", "aside", "script", "style"]):
                unwanted.decompose()
            
            # 查找包含故事内容的段落
            paragraphs = soup.find_all('p')
            content_paragraphs = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 20 and not any(keyword in text.lower() for keyword in 
                    ['copyright', '版权', '联系', 'contact', '导航', 'menu']):
                    content_paragraphs.append(text)
            
            content_text = '\n\n'.join(content_paragraphs)
        
        story_data['content'] = content_text
        story_data['word_count'] = len(content_text)
        
        return story_data
    
    def save_story(self, story_data: dict):
        """保存故事到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO stories (title, category, content, word_count, url)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                story_data.get('title', ''),
                story_data.get('category', ''),
                story_data.get('content', ''),
                story_data.get('word_count', 0),
                story_data.get('url', '')
            ))
            conn.commit()
            logger.info(f"保存故事: {story_data.get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"保存故事失败: {e}")
        finally:
            conn.close()
    
    def scrape_all_stories(self):
        """抓取所有故事"""
        # 1. 从首页获取故事链接
        story_links = self.extract_stories_from_homepage()
        
        if not story_links:
            logger.error("未找到任何故事链接")
            return
        
        # 2. 逐个抓取故事内容
        successful_count = 0
        failed_count = 0
        
        for i, story_info in enumerate(story_links, 1):
            logger.info(f"处理故事 {i}/{len(story_links)}: {story_info['title']}")
            
            try:
                story_data = self.extract_story_content(story_info['url'])
                
                if story_data and story_data['content']:
                    story_data['category'] = story_info['category']
                    self.save_story(story_data)
                    successful_count += 1
                else:
                    logger.warning(f"无法提取故事内容: {story_info['title']}")
                    failed_count += 1
                
                # 添加延迟
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"处理故事失败: {e}")
                failed_count += 1
        
        logger.info(f"抓取完成！成功: {successful_count}, 失败: {failed_count}")
        
        # 3. 保存为JSON文件
        self.export_to_json()
    
    def export_to_json(self):
        """导出数据为JSON格式"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM stories')
        stories = cursor.fetchall()
        
        # 转换为字典格式
        story_list = []
        for story in stories:
            story_dict = {
                'id': story[0],
                'title': story[1],
                'category': story[2],
                'content': story[3],
                'word_count': story[4],
                'url': story[5],
                'scraped_at': story[6]
            }
            story_list.append(story_dict)
        
        # 按分类分组
        categorized_stories = {}
        for story in story_list:
            category = story['category']
            if category not in categorized_stories:
                categorized_stories[category] = []
            categorized_stories[category].append(story)
        
        # 保存文件
        json_file = os.path.join(self.data_dir, "all_stories.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(categorized_stories, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已导出到: {json_file}")
        
        conn.close()
    
    def get_statistics(self):
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, COUNT(*) as count, AVG(word_count) as avg_words
            FROM stories
            GROUP BY category
            ORDER BY count DESC
        ''')
        
        results = cursor.fetchall()
        
        print("\n=== 抓取统计 ===")
        total_stories = 0
        for category, count, avg_words in results:
            print(f"{category}: {count} 个故事, 平均 {avg_words:.0f} 字")
            total_stories += count
        
        print(f"\n总计: {total_stories} 个故事")
        
        conn.close()

def main():
    """主函数"""
    scraper = WebScraper()
    
    try:
        print("开始网页抓取...")
        scraper.scrape_all_stories()
        scraper.get_statistics()
        
        print(f"\n数据已保存到: {scraper.data_dir}")
        print(f"数据库文件: {scraper.db_path}")
        
    except KeyboardInterrupt:
        logger.info("用户中断抓取")
    except Exception as e:
        logger.error(f"抓取过程中出现错误: {e}")

if __name__ == "__main__":
    main()