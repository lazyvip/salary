#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地Selenium爬虫 - 使用系统已安装的Chrome浏览器
处理JavaScript渲染的故事网站
"""

import time
import json
import sqlite3
import logging
import re
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class LocalSeleniumCrawler:
    def __init__(self, max_workers=1, headless=False):
        self.max_workers = max_workers
        self.headless = headless
        self.base_url = "https://storynook.cn"
        self.stories = []
        self.failed_ids = []
        self.success_count = 0
        self.total_count = 0
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('local_selenium.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 初始化数据库
        self.init_database()
        
    def find_chrome_executable(self):
        """查找Chrome可执行文件路径"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
            r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
            r"C:\Program Files\Chromium\Application\chrome.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"找到Chrome: {path}")
                return path
        
        self.logger.error("未找到Chrome浏览器")
        return None
        
    def create_driver(self):
        """创建Chrome WebDriver实例"""
        chrome_options = Options()
        
        # 查找Chrome可执行文件
        chrome_path = self.find_chrome_executable()
        if chrome_path:
            chrome_options.binary_location = chrome_path
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # 优化选项
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置用户代理
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            # 尝试使用系统PATH中的chromedriver
            driver = webdriver.Chrome(options=chrome_options)
            
            # 执行反检测脚本
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            self.logger.error(f"创建WebDriver失败: {e}")
            self.logger.info("请确保已安装ChromeDriver并添加到系统PATH中")
            return None
    
    def init_database(self):
        """初始化SQLite数据库"""
        self.conn = sqlite3.connect('local_selenium_stories.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                word_count INTEGER,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                url TEXT
            )
        ''')
        self.conn.commit()
        self.logger.info("数据库初始化完成")
    
    def wait_for_content_load(self, driver, timeout=20):
        """等待页面内容加载完成"""
        try:
            # 等待页面基本结构加载
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待更长时间让JavaScript执行
            time.sleep(5)
            
            # 尝试等待特定元素加载
            try:
                # 等待可能的内容容器
                WebDriverWait(driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "content")),
                        EC.presence_of_element_located((By.CLASS_NAME, "story")),
                        EC.presence_of_element_located((By.TAG_NAME, "article")),
                        EC.presence_of_element_located((By.ID, "content"))
                    )
                )
            except TimeoutException:
                self.logger.debug("未找到特定内容容器，继续处理")
            
            return True
        except TimeoutException:
            self.logger.warning(f"页面加载超时: {driver.current_url}")
            return False
    
    def extract_story_content(self, driver, story_id):
        """从页面中提取故事内容"""
        try:
            # 等待内容加载
            if not self.wait_for_content_load(driver):
                return None
            
            # 获取页面源码
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 保存调试HTML
            with open(f'local_selenium_debug_{story_id}.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            self.logger.info(f"页面标题: {driver.title}")
            self.logger.info(f"页面URL: {driver.current_url}")
            
            # 检查页面是否包含故事内容
            page_text = soup.get_text()
            if '404' in page_text or 'Not Found' in page_text or len(page_text) < 100:
                self.logger.warning(f"故事 {story_id} 页面内容异常")
                return None
            
            # 尝试多种方式提取标题
            title = None
            
            # 1. 从页面标题提取
            page_title = driver.title
            if page_title and '小故事铺' not in page_title and len(page_title) < 200:
                title = page_title.strip()
            
            # 2. 从HTML元素提取
            if not title:
                title_selectors = [
                    'h1', 'h2', '.story-title', '.post-title', 
                    '.article-title', '.title', '#title'
                ]
                
                for selector in title_selectors:
                    elements = soup.select(selector)
                    for elem in elements:
                        text = elem.get_text(strip=True)
                        if text and len(text) < 200 and '小故事铺' not in text:
                            title = text
                            break
                    if title:
                        break
            
            # 3. 使用Selenium直接查找
            if not title:
                try:
                    title_elements = driver.find_elements(By.XPATH, "//h1 | //h2 | //*[contains(@class, 'title')]")
                    for elem in title_elements:
                        text = elem.text.strip()
                        if text and len(text) < 200 and '小故事铺' not in text:
                            title = text
                            break
                except Exception as e:
                    self.logger.debug(f"Selenium标题查找失败: {e}")
            
            # 提取内容
            content = None
            
            # 1. 从HTML元素提取
            content_selectors = [
                '.story-content', '.post-content', '.article-content',
                '.content', '#content', 'article', '.main-content',
                '.story-body', '.text-content', 'main'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 100 and '小故事铺汇集了各种类型' not in text:
                        content = text
                        break
                if content:
                    break
            
            # 2. 使用Selenium直接查找
            if not content:
                try:
                    content_elements = driver.find_elements(By.XPATH, 
                        "//div[contains(@class, 'content')] | //div[contains(@class, 'story')] | //article | //main")
                    for elem in content_elements:
                        text = elem.text.strip()
                        if text and len(text) > 100 and '小故事铺汇集了各种类型' not in text:
                            content = text
                            break
                except Exception as e:
                    self.logger.debug(f"Selenium内容查找失败: {e}")
            
            # 3. 从页面所有文本中提取
            if not content:
                all_text = soup.get_text()
                paragraphs = [p.strip() for p in all_text.split('\n') if p.strip()]
                long_paragraphs = [p for p in paragraphs if len(p) > 50]
                if long_paragraphs:
                    content = '\n'.join(long_paragraphs[:10])  # 取前10个长段落
            
            # 验证提取的内容
            if not title:
                title = f"故事 {story_id}"
            
            if not content or len(content) < 50:
                self.logger.warning(f"故事 {story_id} 内容太短或为空")
                return None
            
            # 清理内容
            content = re.sub(r'\s+', ' ', content).strip()
            
            # 推断分类
            category = self.infer_category(title, content)
            
            # 计算字数
            word_count = len(content)
            
            story_data = {
                'id': story_id,
                'title': title,
                'content': content,
                'category': category,
                'word_count': word_count,
                'url': driver.current_url
            }
            
            self.logger.info(f"✅ 成功提取故事 {story_id}: {title[:50]}... (字数: {word_count})")
            return story_data
            
        except Exception as e:
            self.logger.error(f"❌ 提取故事 {story_id} 内容失败: {e}")
            return None
    
    def infer_category(self, title, content):
        """根据标题和内容推断故事分类"""
        categories = {
            '爱情故事': ['爱情', '恋爱', '情侣', '男友', '女友', '结婚', '婚姻', '浪漫'],
            '恐怖故事': ['恐怖', '鬼', '灵异', '惊悚', '可怕', '阴森', '诡异'],
            '励志故事': ['励志', '成功', '奋斗', '坚持', '梦想', '努力', '拼搏'],
            '儿童故事': ['小朋友', '孩子', '童话', '动物', '森林', '王子', '公主'],
            '历史故事': ['古代', '历史', '朝代', '皇帝', '将军', '战争', '传说'],
            '神话故事': ['神话', '仙人', '神仙', '龙', '凤凰', '传说', '神'],
            '寓言故事': ['寓言', '道理', '启示', '智慧', '哲理'],
            '民间故事': ['民间', '传说', '老人', '村庄', '乡村'],
            '科幻故事': ['科幻', '未来', '机器人', '太空', '外星人', '科技'],
            '悬疑故事': ['悬疑', '推理', '侦探', '谜团', '破案', '线索']
        }
        
        text = (title + ' ' + content).lower()
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return '其他故事'
    
    def crawl_single_story(self, story_id):
        """爬取单个故事"""
        driver = None
        try:
            driver = self.create_driver()
            if not driver:
                self.logger.error(f"无法创建WebDriver，跳过故事 {story_id}")
                return None
            
            url = f"{self.base_url}/story/{story_id}"
            self.logger.info(f"🔍 正在爬取故事 {story_id}: {url}")
            
            driver.get(url)
            
            story_data = self.extract_story_content(driver, story_id)
            
            if story_data:
                # 保存到数据库
                self.save_story_to_db(story_data)
                return story_data
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ 爬取故事 {story_id} 失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def save_story_to_db(self, story_data):
        """保存故事到数据库"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO stories 
                (id, title, content, category, word_count, url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                story_data['id'],
                story_data['title'],
                story_data['content'],
                story_data['category'],
                story_data['word_count'],
                story_data['url']
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"保存故事到数据库失败: {e}")
    
    def crawl_stories(self, start_id=1, end_id=10):
        """批量爬取故事（单线程）"""
        self.logger.info(f"🚀 开始爬取故事 {start_id} 到 {end_id}")
        self.total_count = end_id - start_id + 1
        
        for story_id in range(start_id, end_id + 1):
            try:
                result = self.crawl_single_story(story_id)
                if result:
                    self.stories.append(result)
                    self.success_count += 1
                    self.logger.info(f"✅ 故事 {story_id} 爬取成功 ({self.success_count}/{self.total_count})")
                else:
                    self.failed_ids.append(story_id)
                    self.logger.warning(f"❌ 故事 {story_id} 爬取失败")
                    
                # 添加延迟避免过于频繁的请求
                time.sleep(2)
                
            except Exception as e:
                self.failed_ids.append(story_id)
                self.logger.error(f"❌ 故事 {story_id} 处理异常: {e}")
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成爬取报告"""
        success_rate = (self.success_count / self.total_count) * 100 if self.total_count > 0 else 0
        
        report = {
            'crawl_time': datetime.now().isoformat(),
            'total_stories': self.total_count,
            'successful_stories': self.success_count,
            'failed_stories': len(self.failed_ids),
            'success_rate': f"{success_rate:.2f}%",
            'failed_ids': self.failed_ids,
            'stories_sample': self.stories[:5]  # 保存前5个故事作为样本
        }
        
        # 保存JSON报告
        with open('local_selenium_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存所有故事到JSON
        with open('local_selenium_stories.json', 'w', encoding='utf-8') as f:
            json.dump(self.stories, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"""
=== 🎉 爬取完成 ===
总计故事: {self.total_count}
成功爬取: {self.success_count}
失败数量: {len(self.failed_ids)}
成功率: {success_rate:.2f}%
报告已保存到: local_selenium_report.json
故事数据已保存到: local_selenium_stories.json
数据库: local_selenium_stories.db
        """)
    
    def analyze_content_uniqueness(self):
        """分析内容唯一性"""
        if not self.stories:
            self.logger.warning("没有故事数据可分析")
            return
        
        # 统计唯一标题和内容
        unique_titles = set()
        unique_contents = set()
        content_groups = {}
        category_count = {}
        
        for story in self.stories:
            title = story['title']
            content = story['content']
            category = story['category']
            
            unique_titles.add(title)
            unique_contents.add(content)
            
            # 按内容分组
            if content not in content_groups:
                content_groups[content] = []
            content_groups[content].append(story['id'])
            
            # 统计分类
            category_count[category] = category_count.get(category, 0) + 1
        
        # 找出重复内容
        duplicate_groups = {content: ids for content, ids in content_groups.items() if len(ids) > 1}
        
        analysis = {
            'total_stories': len(self.stories),
            'unique_titles': len(unique_titles),
            'unique_contents': len(unique_contents),
            'duplicate_content_groups': len(duplicate_groups),
            'duplicate_story_count': sum(len(ids) for ids in duplicate_groups.values()),
            'category_distribution': category_count,
            'sample_stories': [
                {
                    'id': story['id'],
                    'title': story['title'][:100],
                    'content_preview': story['content'][:200] + '...',
                    'category': story['category'],
                    'word_count': story['word_count']
                }
                for story in self.stories[:3]
            ]
        }
        
        self.logger.info(f"""
=== 📊 内容唯一性分析 ===
总故事数: {analysis['total_stories']}
唯一标题数: {analysis['unique_titles']}
唯一内容数: {analysis['unique_contents']}
重复内容组数: {analysis['duplicate_content_groups']}
重复故事总数: {analysis['duplicate_story_count']}
分类分布: {analysis['category_distribution']}
        """)
        
        # 保存分析结果
        with open('local_selenium_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        return analysis
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    # 创建爬虫实例
    crawler = LocalSeleniumCrawler(max_workers=1, headless=False)  # 非无头模式便于观察
    
    try:
        # 爬取前10个故事进行测试
        crawler.crawl_stories(start_id=1, end_id=10)
        
        # 分析内容唯一性
        crawler.analyze_content_uniqueness()
        
    except KeyboardInterrupt:
        crawler.logger.info("用户中断爬取")
    except Exception as e:
        crawler.logger.error(f"爬取过程中发生错误: {e}")
    finally:
        crawler.close()

if __name__ == "__main__":
    main()