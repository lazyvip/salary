#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于requests的大规模爬虫 - 专门爬取 storynook.cn 的所有故事
避免ChromeDriver版本问题，使用HTTP请求直接获取数据
"""

import time
import json
import re
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('requests_mass_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RequestsMassCrawler:
    def __init__(self):
        self.base_url = "https://storynook.cn/"
        self.session = requests.Session()
        self.all_stories = {}  # 使用字典去重
        self.story_contents = {}
        self.crawl_stats = {
            "start_time": datetime.now().isoformat(),
            "stories_found": 0,
            "stories_with_content": 0,
            "pages_crawled": 0,
            "errors": 0
        }
        
        # 设置请求头，模拟真实浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_page_content(self, url, max_retries=3):
        """获取页面内容"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                response.encoding = 'utf-8'
                return response.text
            except Exception as e:
                logger.warning(f"获取页面失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(1, 3))
                else:
                    self.crawl_stats["errors"] += 1
                    return None
        return None
    
    def extract_stories_from_html(self, html_content):
        """从HTML内容中提取故事信息"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            new_stories_count = 0
            
            # 方法1: 查找包含showStory的onclick属性
            elements_with_onclick = soup.find_all(attrs={"onclick": re.compile(r'showStory\(\d+\)')})
            
            for element in elements_with_onclick:
                try:
                    onclick = element.get('onclick', '')
                    story_id_match = re.search(r'showStory\((\d+)\)', onclick)
                    if story_id_match:
                        story_id = int(story_id_match.group(1))
                        title = element.get_text(strip=True)
                        
                        if story_id not in self.all_stories and title:
                            self.all_stories[story_id] = {
                                "id": story_id,
                                "title": title,
                                "category_name": "睡前故事",
                                "extracted_at": datetime.now().isoformat(),
                                "source": "requests_onclick"
                            }
                            new_stories_count += 1
                except Exception as e:
                    continue
            
            # 方法2: 直接从HTML源码中正则提取
            onclick_pattern = r'onclick=["\']showStory\((\d+)\)["\'][^>]*>([^<]+)'
            matches = re.findall(onclick_pattern, html_content)
            
            for story_id, title in matches:
                try:
                    story_id = int(story_id)
                    title = title.strip()
                    if story_id not in self.all_stories and title:
                        self.all_stories[story_id] = {
                            "id": story_id,
                            "title": title,
                            "category_name": "睡前故事",
                            "extracted_at": datetime.now().isoformat(),
                            "source": "requests_regex"
                        }
                        new_stories_count += 1
                except:
                    continue
            
            # 方法3: 查找可能的故事链接
            story_links = soup.find_all('a', href=re.compile(r'story|tale'))
            for link in story_links:
                try:
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # 尝试从href中提取ID
                    id_match = re.search(r'(\d+)', href)
                    if id_match and title:
                        story_id = int(id_match.group(1))
                        if story_id not in self.all_stories:
                            self.all_stories[story_id] = {
                                "id": story_id,
                                "title": title,
                                "category_name": "睡前故事",
                                "extracted_at": datetime.now().isoformat(),
                                "source": "requests_link"
                            }
                            new_stories_count += 1
                except:
                    continue
            
            logger.info(f"从HTML提取到 {new_stories_count} 个新故事，总计 {len(self.all_stories)} 个")
            return new_stories_count
            
        except Exception as e:
            logger.error(f"HTML解析失败: {e}")
            return 0
    
    def try_get_story_content_api(self, story_id):
        """尝试通过API获取故事内容"""
        api_urls = [
            f"{self.base_url}api/story/{story_id}",
            f"{self.base_url}story/{story_id}",
            f"{self.base_url}get_story.php?id={story_id}",
            f"{self.base_url}story.php?id={story_id}",
        ]
        
        for api_url in api_urls:
            try:
                response = self.session.get(api_url, timeout=10)
                if response.status_code == 200:
                    # 尝试JSON解析
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'content' in data:
                            return data['content']
                        elif isinstance(data, dict) and 'story' in data:
                            return data['story']
                    except:
                        pass
                    
                    # 尝试HTML解析
                    if len(response.text) > 100:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # 查找可能的内容容器
                        content_selectors = [
                            '.story-content',
                            '.content',
                            '#content',
                            '.story-text',
                            '.text',
                            'p'
                        ]
                        
                        for selector in content_selectors:
                            elements = soup.select(selector)
                            if elements:
                                content = ' '.join([elem.get_text(strip=True) for elem in elements])
                                if len(content) > 50:
                                    return content
                        
                        # 如果没有找到特定容器，尝试获取所有文本
                        all_text = soup.get_text(strip=True)
                        if len(all_text) > 100:
                            return all_text
                            
            except Exception as e:
                continue
        
        return None
    
    def crawl_main_page_variations(self):
        """爬取主页的各种变体"""
        urls_to_try = [
            self.base_url,
            f"{self.base_url}index.html",
            f"{self.base_url}index.php",
            f"{self.base_url}stories",
            f"{self.base_url}stories.html",
            f"{self.base_url}list",
            f"{self.base_url}list.html",
        ]
        
        total_new_stories = 0
        
        for url in urls_to_try:
            try:
                logger.info(f"正在爬取: {url}")
                html_content = self.get_page_content(url)
                
                if html_content:
                    new_stories = self.extract_stories_from_html(html_content)
                    total_new_stories += new_stories
                    self.crawl_stats["pages_crawled"] += 1
                    
                    # 随机延迟，避免被封
                    time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"爬取 {url} 失败: {e}")
                continue
        
        return total_new_stories
    
    def try_pagination_discovery(self):
        """尝试发现分页"""
        try:
            html_content = self.get_page_content(self.base_url)
            if not html_content:
                return []
            
            soup = BeautifulSoup(html_content, 'html.parser')
            pagination_urls = []
            
            # 查找分页链接
            pagination_patterns = [
                r'page=(\d+)',
                r'p=(\d+)',
                r'/(\d+)\.html',
                r'/page/(\d+)',
            ]
            
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                for pattern in pagination_patterns:
                    matches = re.findall(pattern, href)
                    if matches:
                        for page_num in matches:
                            try:
                                page_num = int(page_num)
                                if 1 <= page_num <= 50:  # 限制页数范围
                                    full_url = urljoin(self.base_url, href)
                                    if full_url not in pagination_urls:
                                        pagination_urls.append(full_url)
                            except:
                                continue
            
            # 尝试构造可能的分页URL
            for page in range(2, 21):  # 尝试2-20页
                possible_urls = [
                    f"{self.base_url}?page={page}",
                    f"{self.base_url}?p={page}",
                    f"{self.base_url}page/{page}",
                    f"{self.base_url}{page}.html",
                    f"{self.base_url}list?page={page}",
                ]
                
                for url in possible_urls:
                    if url not in pagination_urls:
                        pagination_urls.append(url)
            
            logger.info(f"发现 {len(pagination_urls)} 个可能的分页URL")
            return pagination_urls[:30]  # 限制数量
            
        except Exception as e:
            logger.error(f"分页发现失败: {e}")
            return []
    
    def crawl_pagination_pages(self, pagination_urls):
        """爬取分页页面"""
        total_new_stories = 0
        
        for i, url in enumerate(pagination_urls):
            try:
                logger.info(f"正在爬取分页 {i+1}/{len(pagination_urls)}: {url}")
                html_content = self.get_page_content(url)
                
                if html_content:
                    new_stories = self.extract_stories_from_html(html_content)
                    total_new_stories += new_stories
                    self.crawl_stats["pages_crawled"] += 1
                    
                    # 如果连续几页都没有新故事，可能已经到底了
                    if new_stories == 0 and i > 5:
                        consecutive_empty = 0
                        for j in range(max(0, i-3), i):
                            if j < len(pagination_urls):
                                consecutive_empty += 1
                        if consecutive_empty >= 3:
                            logger.info("连续多页无新故事，停止分页爬取")
                            break
                    
                    # 随机延迟
                    time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"爬取分页 {url} 失败: {e}")
                continue
        
        return total_new_stories
    
    def get_stories_content_batch(self, max_stories=100):
        """批量获取故事内容"""
        try:
            story_ids = list(self.all_stories.keys())[:max_stories]
            logger.info(f"开始获取 {len(story_ids)} 个故事的内容...")
            
            success_count = 0
            
            for i, story_id in enumerate(story_ids):
                try:
                    content = self.try_get_story_content_api(story_id)
                    
                    if content and len(content) > 50:
                        self.story_contents[story_id] = {
                            "id": story_id,
                            "content": content,
                            "length": len(content),
                            "extracted_at": datetime.now().isoformat()
                        }
                        
                        # 更新故事信息
                        if story_id in self.all_stories:
                            self.all_stories[story_id]["content_length"] = len(content)
                            self.all_stories[story_id]["has_content"] = True
                        
                        success_count += 1
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"已处理 {i + 1}/{len(story_ids)} 个故事，成功: {success_count}")
                    
                    # 随机延迟
                    time.sleep(random.uniform(0.5, 2))
                    
                except Exception as e:
                    logger.warning(f"获取故事 {story_id} 内容失败: {e}")
                    continue
            
            logger.info(f"内容获取完成，成功获取 {success_count} 个故事内容")
            self.crawl_stats["stories_with_content"] = success_count
            return success_count
            
        except Exception as e:
            logger.error(f"批量获取故事内容失败: {e}")
            return 0
    
    def save_all_data(self):
        """保存所有数据"""
        try:
            # 更新统计信息
            self.crawl_stats["end_time"] = datetime.now().isoformat()
            self.crawl_stats["stories_found"] = len(self.all_stories)
            
            # 保存故事列表
            stories_list = list(self.all_stories.values())
            with open('requests_crawled_stories.json', 'w', encoding='utf-8') as f:
                json.dump(stories_list, f, ensure_ascii=False, indent=2)
            
            # 保存故事内容
            if self.story_contents:
                contents_list = list(self.story_contents.values())
                with open('requests_story_contents.json', 'w', encoding='utf-8') as f:
                    json.dump(contents_list, f, ensure_ascii=False, indent=2)
            
            # 保存到SQLite数据库
            self.save_to_database()
            
            # 保存爬取报告
            with open('requests_crawl_report.json', 'w', encoding='utf-8') as f:
                json.dump(self.crawl_stats, f, ensure_ascii=False, indent=2)
            
            logger.info("所有数据保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return False
    
    def save_to_database(self):
        """保存到SQLite数据库"""
        try:
            conn = sqlite3.connect('requests_crawled_stories.db')
            cursor = conn.cursor()
            
            # 创建故事表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    category_name TEXT,
                    content_length INTEGER DEFAULT 0,
                    has_content BOOLEAN DEFAULT FALSE,
                    extracted_at TEXT,
                    source TEXT
                )
            ''')
            
            # 创建故事内容表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS story_contents (
                    id INTEGER PRIMARY KEY,
                    content TEXT NOT NULL,
                    length INTEGER,
                    extracted_at TEXT
                )
            ''')
            
            # 插入故事数据
            for story in self.all_stories.values():
                cursor.execute('''
                    INSERT OR REPLACE INTO stories 
                    (id, title, category_name, content_length, has_content, extracted_at, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    story["id"],
                    story["title"],
                    story.get("category_name", "睡前故事"),
                    story.get("content_length", 0),
                    story.get("has_content", False),
                    story["extracted_at"],
                    story.get("source", "unknown")
                ))
            
            # 插入故事内容
            for content in self.story_contents.values():
                cursor.execute('''
                    INSERT OR REPLACE INTO story_contents 
                    (id, content, length, extracted_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    content["id"],
                    content["content"],
                    content["length"],
                    content["extracted_at"]
                ))
            
            conn.commit()
            conn.close()
            
            logger.info("数据库保存成功")
            return True
            
        except Exception as e:
            logger.error(f"数据库保存失败: {e}")
            return False
    
    def run_mass_crawl(self):
        """运行大规模爬取"""
        try:
            logger.info("开始基于requests的大规模故事爬取...")
            
            # 1. 爬取主页及其变体
            logger.info("步骤1: 爬取主页及变体...")
            main_stories = self.crawl_main_page_variations()
            logger.info(f"主页爬取完成，发现 {main_stories} 个新故事")
            
            # 2. 发现并爬取分页
            logger.info("步骤2: 发现分页...")
            pagination_urls = self.try_pagination_discovery()
            
            if pagination_urls:
                logger.info("步骤3: 爬取分页...")
                pagination_stories = self.crawl_pagination_pages(pagination_urls)
                logger.info(f"分页爬取完成，发现 {pagination_stories} 个新故事")
            
            # 3. 获取故事内容
            if self.all_stories:
                logger.info("步骤4: 获取故事内容...")
                self.get_stories_content_batch(min(100, len(self.all_stories)))
            
            # 4. 保存所有数据
            logger.info("步骤5: 保存数据...")
            self.save_all_data()
            
            logger.info("大规模爬取完成！")
            logger.info(f"总共发现 {len(self.all_stories)} 个故事")
            logger.info(f"获取到 {len(self.story_contents)} 个故事的完整内容")
            logger.info(f"爬取了 {self.crawl_stats['pages_crawled']} 个页面")
            
            return True
            
        except Exception as e:
            logger.error(f"大规模爬取失败: {e}")
            return False

def main():
    crawler = RequestsMassCrawler()
    success = crawler.run_mass_crawl()
    
    if success:
        print("✅ 基于requests的大规模爬取完成！")
        print("📊 爬取结果:")
        print(f"   - 发现故事: {len(crawler.all_stories)} 个")
        print(f"   - 获取内容: {len(crawler.story_contents)} 个")
        print(f"   - 爬取页面: {crawler.crawl_stats['pages_crawled']} 个")
        print("📁 生成文件:")
        print("   - requests_crawled_stories.json (所有故事列表)")
        print("   - requests_story_contents.json (故事内容)")
        print("   - requests_crawled_stories.db (SQLite数据库)")
        print("   - requests_crawl_report.json (爬取报告)")
    else:
        print("❌ 大规模爬取失败，请查看日志文件")

if __name__ == "__main__":
    main()