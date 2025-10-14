#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能故事爬虫 - 让requests自动处理压缩
"""

import requests
import sqlite3
import json
import time
import random
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import re
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartStoryCrawler:
    def __init__(self, base_url="https://storynook.cn", max_stories=100):
        self.base_url = base_url
        self.max_stories = max_stories
        self.db_path = "smart_stories.db"
        self.json_path = "smart_stories.json"
        
        # 创建session，让requests自动处理压缩
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': time.time()
        }
        
        self.lock = threading.Lock()
        
        # 初始化数据库
        self.init_database()
        
    def init_database(self):
        """初始化SQLite数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建故事表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT,
                    word_count INTEGER,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id)
                )
            ''')
            
            # 创建分类表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("数据库初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def fetch_story(self, story_id):
        """获取单个故事内容"""
        url = f"{self.base_url}/?id={story_id}"
        
        try:
            # 随机延迟
            time.sleep(random.uniform(0.5, 2.0))
            
            # 让requests自动处理解压
            response = self.session.get(url, timeout=30)
            
            # 检查响应状态
            if response.status_code != 200:
                logger.warning(f"故事 {story_id}: HTTP {response.status_code}")
                return None
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"故事 {story_id}: 非HTML内容 - {content_type}")
                return None
            
            # 获取解压后的文本内容
            html_content = response.text
            
            # 检查内容长度
            if len(html_content) < 100:
                logger.warning(f"故事 {story_id}: 内容太短 ({len(html_content)} 字符)")
                return None
            
            # 保存原始HTML用于调试
            if story_id <= 5:  # 只保存前5个用于调试
                debug_file = f"smart_debug_{story_id}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"调试文件已保存: {debug_file}")
            
            # 解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取故事数据
            story_data = self.extract_story_data(soup, story_id)
            
            if story_data:
                logger.info(f"✅ 故事 {story_id}: {story_data['title'][:30]}...")
                return story_data
            else:
                logger.warning(f"❌ 故事 {story_id}: 无法提取内容")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"故事 {story_id}: 请求失败 - {e}")
            return None
        except Exception as e:
            logger.error(f"故事 {story_id}: 处理失败 - {e}")
            return None
    
    def extract_story_data(self, soup, story_id):
        """从HTML中提取故事数据"""
        try:
            # 移除script和style标签
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # 尝试多种标题提取方法
            title = None
            
            # 方法1: 常见标题标签
            title_selectors = ['h1', 'h2', '.title', '.story-title', 'title']
            for selector in title_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and 5 <= len(text) <= 100:
                        title = text
                        break
                if title:
                    break
            
            # 方法2: 从页面标题提取
            if not title:
                page_title = soup.find('title')
                if page_title:
                    title_text = page_title.get_text(strip=True)
                    # 移除网站名称
                    title = title_text.split(' - ')[0].split(' | ')[0]
            
            # 尝试多种内容提取方法
            content = None
            
            # 方法1: 常见内容容器
            content_selectors = [
                '.content', '.story-content', '.post-content', '.entry-content',
                'article', '.article', 'main', '.main'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 200:  # 内容应该足够长
                        content = text
                        break
                if content:
                    break
            
            # 方法2: 查找最长的文本块
            if not content:
                all_elements = soup.find_all(['p', 'div', 'span'])
                longest_text = ""
                for element in all_elements:
                    text = element.get_text(strip=True)
                    if len(text) > len(longest_text):
                        longest_text = text
                
                if len(longest_text) > 200:
                    content = longest_text
            
            # 方法3: 获取所有可见文本
            if not content:
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.splitlines() if line.strip()]
                # 过滤掉导航、菜单等短行
                content_lines = [line for line in lines if len(line) > 20]
                if content_lines:
                    content = '\n'.join(content_lines)
            
            # 验证提取的数据
            if not title:
                title = f"故事 {story_id}"
            
            if not content or len(content) < 100:
                logger.warning(f"故事 {story_id}: 内容提取失败或太短")
                # 输出调试信息
                logger.debug(f"故事 {story_id}: HTML长度 = {len(soup.get_text())}")
                logger.debug(f"故事 {story_id}: 提取的内容长度 = {len(content) if content else 0}")
                return None
            
            # 清理内容
            content = self.clean_content(content)
            
            # 推断分类
            category = self.infer_category(title, content)
            
            return {
                'id': story_id,
                'title': title,
                'content': content,
                'category': category,
                'word_count': len(content)
            }
            
        except Exception as e:
            logger.error(f"故事 {story_id}: 数据提取失败 - {e}")
            return None
    
    def clean_content(self, content):
        """清理内容"""
        if not content:
            return ""
        
        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 移除一些常见的网站元素
        content = re.sub(r'(首页|导航|菜单|登录|注册|搜索|版权|联系我们)', '', content)
        
        return content.strip()
    
    def infer_category(self, title, content):
        """根据标题和内容推断分类"""
        text = (title + " " + content).lower()
        
        categories = {
            '爱情故事': ['爱情', '恋爱', '情侣', '男友', '女友', '结婚', '婚姻', '约会'],
            '冒险故事': ['冒险', '探险', '旅行', '发现', '寻找', '神秘', '未知'],
            '童话故事': ['公主', '王子', '魔法', '仙女', '巫师', '城堡', '森林'],
            '科幻故事': ['科幻', '未来', '机器人', '太空', '外星', '时间', '穿越'],
            '恐怖故事': ['恐怖', '鬼', '怪物', '黑暗', '死亡', '血', '尖叫'],
            '励志故事': ['励志', '成功', '努力', '坚持', '梦想', '奋斗', '成长'],
            '友情故事': ['朋友', '友谊', '同学', '伙伴', '帮助', '支持'],
            '家庭故事': ['家庭', '父母', '孩子', '兄弟', '姐妹', '亲情']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return '其他故事'
    
    def save_to_database(self, story_data):
        """保存故事到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 插入故事
            cursor.execute('''
                INSERT OR REPLACE INTO stories 
                (id, title, content, category, word_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                story_data['id'],
                story_data['title'],
                story_data['content'],
                story_data['category'],
                story_data['word_count']
            ))
            
            # 更新分类统计
            cursor.execute('''
                INSERT OR REPLACE INTO categories (name, count)
                VALUES (?, (
                    SELECT COUNT(*) FROM stories WHERE category = ?
                ))
            ''', (story_data['category'], story_data['category']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"保存数据库失败: {e}")
    
    def process_story(self, story_id):
        """处理单个故事"""
        with self.lock:
            self.stats['total_processed'] += 1
        
        story_data = self.fetch_story(story_id)
        
        if story_data:
            self.save_to_database(story_data)
            with self.lock:
                self.stats['successful'] += 1
            return story_data
        else:
            with self.lock:
                self.stats['failed'] += 1
            return None
    
    def crawl_stories(self, start_id=1, end_id=None, max_workers=4):
        """爬取故事"""
        if end_id is None:
            end_id = self.max_stories
        
        logger.info(f"开始爬取故事 {start_id} 到 {end_id}")
        logger.info(f"使用 {max_workers} 个线程")
        
        story_ids = list(range(start_id, end_id + 1))
        stories = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_id = {
                executor.submit(self.process_story, story_id): story_id 
                for story_id in story_ids
            }
            
            # 处理结果
            for future in as_completed(future_to_id):
                story_id = future_to_id[future]
                try:
                    result = future.result()
                    if result:
                        stories.append(result)
                    
                    # 每10个故事显示一次进度
                    if self.stats['total_processed'] % 10 == 0:
                        self.print_progress()
                        
                except Exception as e:
                    logger.error(f"处理故事 {story_id} 时出错: {e}")
                    with self.lock:
                        self.stats['failed'] += 1
        
        # 保存到JSON
        self.save_to_json(stories)
        
        # 最终统计
        self.print_final_stats()
        
        return stories
    
    def save_to_json(self, stories):
        """保存故事到JSON文件"""
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(stories, f, ensure_ascii=False, indent=2)
            logger.info(f"故事已保存到 {self.json_path}")
        except Exception as e:
            logger.error(f"保存JSON失败: {e}")
    
    def print_progress(self):
        """显示进度"""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['total_processed'] / elapsed if elapsed > 0 else 0
        
        logger.info(f"进度: {self.stats['total_processed']}/{self.max_stories} "
                   f"成功: {self.stats['successful']} "
                   f"失败: {self.stats['failed']} "
                   f"速度: {rate:.1f}/秒")
    
    def print_final_stats(self):
        """显示最终统计"""
        elapsed = time.time() - self.stats['start_time']
        
        logger.info("=" * 60)
        logger.info("爬取完成！")
        logger.info(f"总处理: {self.stats['total_processed']}")
        logger.info(f"成功: {self.stats['successful']}")
        logger.info(f"失败: {self.stats['failed']}")
        logger.info(f"成功率: {self.stats['successful']/self.stats['total_processed']*100:.1f}%")
        logger.info(f"总耗时: {elapsed:.1f}秒")
        logger.info(f"平均速度: {self.stats['total_processed']/elapsed:.1f}故事/秒")
        logger.info("=" * 60)

def main():
    """主函数"""
    logger.info("启动智能故事爬虫")
    
    crawler = SmartStoryCrawler(max_stories=20)  # 先测试20个故事
    
    # 开始爬取
    stories = crawler.crawl_stories(start_id=1, end_id=20, max_workers=2)
    
    logger.info(f"爬取完成，共获得 {len(stories)} 个故事")

if __name__ == "__main__":
    main()