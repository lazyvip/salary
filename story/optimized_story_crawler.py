#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版故事网站爬虫
增加更长的等待时间和更好的页面加载检测
"""

import os
import sys
import json
import time
import sqlite3
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 配置
CHROMEDRIVER_PATH = r"F:\个人文档\website\salary\story\chromedriver_exe\chromedriver.exe"
BASE_URL = "https://storynook.cn/"
DATABASE_FILE = "optimized_stories.db"
STORIES_JSON_FILE = "optimized_stories.json"
CONTENT_JSON_FILE = "optimized_story_contents.json"
REPORT_FILE = "optimized_crawling_report.json"
LOG_FILE = "optimized_crawler.log"

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OptimizedStoryNookCrawler:
    def __init__(self):
        self.driver = None
        self.stories = []
        self.story_contents = {}
        self.categories = []
        self.crawl_stats = {
            'start_time': datetime.now().isoformat(),
            'stories_found': 0,
            'stories_crawled': 0,
            'categories_found': 0,
            'errors': [],
            'success_rate': 0
        }
        
    def setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            if not os.path.exists(CHROMEDRIVER_PATH):
                raise FileNotFoundError(f"ChromeDriver not found at {CHROMEDRIVER_PATH}")
            
            chrome_options = Options()
            # 不使用无头模式，便于调试
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(CHROMEDRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 执行脚本隐藏webdriver属性
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(20)
            
            logger.info("WebDriver setup successful")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            self.crawl_stats['errors'].append(f"WebDriver setup failed: {str(e)}")
            return False
    
    def wait_for_page_load(self, timeout=60):
        """等待页面完全加载，增加更长的超时时间"""
        try:
            logger.info("Waiting for page to load...")
            
            # 等待页面基本加载完成
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            logger.info("Document ready state: complete")
            
            # 等待jQuery加载完成
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.execute_script("return typeof jQuery !== 'undefined'")
                )
                logger.info("jQuery loaded")
            except TimeoutException:
                logger.warning("jQuery not found, continuing anyway")
            
            # 等待页面标题加载
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda driver: "小故事铺" in driver.title
                )
                logger.info(f"Page title loaded: {self.driver.title}")
            except TimeoutException:
                logger.warning("Expected page title not found")
            
            # 等待主要内容容器出现
            containers_to_wait = ["#story-grid", ".content-card", ".filter-tag"]
            for container in containers_to_wait:
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, container))
                    )
                    logger.info(f"Container {container} found")
                    break
                except TimeoutException:
                    logger.warning(f"Container {container} not found")
                    continue
            
            # 额外等待确保动态内容加载完成
            logger.info("Waiting for dynamic content...")
            time.sleep(10)
            
            # 检查页面是否有内容
            page_source_length = len(self.driver.page_source)
            logger.info(f"Page source length: {page_source_length}")
            
            if page_source_length < 1000:
                logger.warning("Page seems to have very little content")
                return False
            
            logger.info("Page loaded successfully")
            return True
            
        except TimeoutException as e:
            logger.warning(f"Page load timeout: {e}, but continuing anyway")
            return True  # 即使超时也继续尝试
        except Exception as e:
            logger.error(f"Error waiting for page load: {e}")
            return False
    
    def extract_stories_from_current_view(self):
        """从当前视图提取故事信息"""
        try:
            logger.info("Extracting stories from current view...")
            
            # 方法1: 通过onclick属性提取
            stories_script = """
            var stories = [];
            var storyCards = document.querySelectorAll('.content-card, [onclick*="loadStoryDetail"]');
            
            storyCards.forEach(function(card) {
                var onclickAttr = card.getAttribute('onclick');
                if (onclickAttr && onclickAttr.includes('loadStoryDetail')) {
                    try {
                        // 提取JSON数据
                        var jsonStart = onclickAttr.indexOf('{');
                        var jsonEnd = onclickAttr.lastIndexOf('}') + 1;
                        if (jsonStart >= 0 && jsonEnd > jsonStart) {
                            var jsonStr = onclickAttr.substring(jsonStart, jsonEnd);
                            var storyData = JSON.parse(jsonStr);
                            stories.push(storyData);
                        }
                    } catch (e) {
                        console.log('Failed to parse story data:', e);
                    }
                }
            });
            
            return {
                stories: stories,
                cardCount: storyCards.length,
                pageSource: document.body.innerHTML.length
            };
            """
            
            result = self.driver.execute_script(stories_script)
            
            if result and result['stories']:
                logger.info(f"Found {len(result['stories'])} stories from {result['cardCount']} cards")
                
                # 去重并添加到总列表
                existing_ids = {story['id'] for story in self.stories}
                new_stories = [story for story in result['stories'] if story['id'] not in existing_ids]
                
                self.stories.extend(new_stories)
                logger.info(f"Added {len(new_stories)} new stories, total: {len(self.stories)}")
                
                return len(new_stories)
            else:
                logger.warning("No stories found in current view")
                logger.info(f"Page source length: {result.get('pageSource', 0) if result else 'unknown'}")
                return 0
                
        except Exception as e:
            logger.error(f"Failed to extract stories: {e}")
            self.crawl_stats['errors'].append(f"Story extraction failed: {str(e)}")
            return 0
    
    def get_categories(self):
        """获取所有分类"""
        try:
            logger.info("Getting categories...")
            
            # 方法1: 从JavaScript状态获取
            categories_script = """
            if (window.currentState && window.currentState.categories) {
                return window.currentState.categories;
            }
            return null;
            """
            
            categories = self.driver.execute_script(categories_script)
            
            if not categories:
                logger.info("Trying to get categories from DOM...")
                # 方法2: 从DOM获取
                try:
                    category_elements = self.driver.find_elements(By.CSS_SELECTOR, ".filter-tag[data-id]")
                    categories = []
                    for elem in category_elements:
                        try:
                            category_id = elem.get_attribute("data-id")
                            category_name = elem.text.strip()
                            if category_id and category_name:
                                categories.append({
                                    'id': int(category_id),
                                    'name': category_name
                                })
                        except Exception as e:
                            logger.warning(f"Error parsing category element: {e}")
                            continue
                except Exception as e:
                    logger.warning(f"Error finding category elements: {e}")
                    categories = []
            
            if categories:
                self.categories = categories
                logger.info(f"Found {len(categories)} categories: {[c['name'] for c in categories]}")
                self.crawl_stats['categories_found'] = len(categories)
                return True
            else:
                logger.warning("No categories found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return False
    
    def click_category(self, category_id):
        """点击指定分类"""
        try:
            logger.info(f"Clicking category {category_id}")
            
            # 方法1: 通过JavaScript点击
            click_script = f"""
            var categoryTag = document.querySelector('.filter-tag[data-id="{category_id}"]');
            if (categoryTag) {{
                categoryTag.click();
                return true;
            }}
            return false;
            """
            
            success = self.driver.execute_script(click_script)
            
            if success:
                logger.info(f"Successfully clicked category {category_id}")
                time.sleep(5)  # 等待内容加载
                return True
            else:
                logger.warning(f"Failed to click category {category_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error clicking category {category_id}: {e}")
            return False
    
    def crawl_basic_stories(self):
        """爬取基本故事信息"""
        try:
            logger.info("Starting to crawl basic stories...")
            
            # 访问主页
            logger.info(f"Navigating to {BASE_URL}")
            self.driver.get(BASE_URL)
            
            # 等待页面加载
            if not self.wait_for_page_load():
                logger.error("Failed to load main page properly")
                # 但继续尝试
            
            # 获取分类
            self.get_categories()
            
            # 提取默认页面的故事
            logger.info("Extracting stories from default view...")
            self.extract_stories_from_current_view()
            
            # 如果有分类，遍历每个分类
            if self.categories:
                for category in self.categories:
                    logger.info(f"Processing category: {category['name']} (ID: {category['id']})")
                    
                    if self.click_category(category['id']):
                        # 提取当前分类的故事
                        new_stories = self.extract_stories_from_current_view()
                        logger.info(f"Found {new_stories} new stories in category {category['name']}")
                        
                        # 尝试滚动加载更多
                        self.scroll_and_load_more()
                    
                    time.sleep(3)  # 避免请求过快
            
            # 去重
            unique_stories = {}
            for story in self.stories:
                unique_stories[story['id']] = story
            
            self.stories = list(unique_stories.values())
            self.crawl_stats['stories_found'] = len(self.stories)
            
            logger.info(f"Total unique stories found: {len(self.stories)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to crawl basic stories: {e}")
            self.crawl_stats['errors'].append(f"Basic crawling failed: {str(e)}")
            return False
    
    def scroll_and_load_more(self):
        """滚动页面并尝试加载更多内容"""
        try:
            logger.info("Scrolling to load more content...")
            
            for i in range(3):  # 最多滚动3次
                # 滚动到页面底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # 检查是否有新内容
                new_stories = self.extract_stories_from_current_view()
                if new_stories > 0:
                    logger.info(f"Scroll {i+1}: Found {new_stories} new stories")
                else:
                    logger.info(f"Scroll {i+1}: No new stories found")
                    break
                    
        except Exception as e:
            logger.error(f"Error during scrolling: {e}")
    
    def get_sample_story_content(self, max_samples=5):
        """获取少量故事内容作为样本"""
        try:
            logger.info(f"Getting content for {max_samples} sample stories...")
            
            sample_stories = self.stories[:max_samples]
            success_count = 0
            
            for i, story in enumerate(sample_stories, 1):
                logger.info(f"Getting content for sample story {i}/{len(sample_stories)}: {story['title']}")
                
                try:
                    # 使用简化的内容获取方法
                    content_script = f"""
                    // 模拟点击故事
                    var story = {json.dumps(story)};
                    
                    // 检查loadStoryDetail函数是否存在
                    if (typeof loadStoryDetail === 'function') {{
                        try {{
                            loadStoryDetail(story);
                            return 'Function called successfully';
                        }} catch (e) {{
                            return 'Error calling function: ' + e.message;
                        }}
                    }} else {{
                        return 'loadStoryDetail function not found';
                    }}
                    """
                    
                    result = self.driver.execute_script(content_script)
                    logger.info(f"Content script result: {result}")
                    
                    # 等待内容加载
                    time.sleep(5)
                    
                    # 尝试获取内容
                    content_selectors = ["#story-content", ".story-content", ".article-content"]
                    content = None
                    
                    for selector in content_selectors:
                        try:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            content = element.text.strip()
                            if content:
                                break
                        except:
                            continue
                    
                    if content and len(content) > 50:
                        self.story_contents[story['id']] = {
                            'id': story['id'],
                            'title': story['title'],
                            'category_name': story.get('category_name', ''),
                            'content': content,
                            'length': len(content),
                            'crawled_at': datetime.now().isoformat()
                        }
                        success_count += 1
                        logger.info(f"Successfully got content for story {story['id']} ({len(content)} characters)")
                    else:
                        logger.warning(f"No valid content found for story {story['id']}")
                    
                    # 返回主页
                    self.driver.get(BASE_URL)
                    time.sleep(3)
                    
                except Exception as e:
                    logger.error(f"Error getting content for story {story['id']}: {e}")
                    continue
            
            self.crawl_stats['stories_crawled'] = success_count
            logger.info(f"Successfully got content for {success_count}/{len(sample_stories)} sample stories")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to get sample story content: {e}")
            return False
    
    def save_data(self):
        """保存数据到文件"""
        try:
            # 保存到JSON
            with open(STORIES_JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.stories, f, ensure_ascii=False, indent=2)
            
            with open(CONTENT_JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.story_contents, f, ensure_ascii=False, indent=2)
            
            # 保存到数据库
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    category_id INTEGER,
                    category_name TEXT,
                    excerpt TEXT,
                    length INTEGER,
                    crawled_at TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS story_contents (
                    story_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    category_name TEXT,
                    content TEXT NOT NULL,
                    content_length INTEGER,
                    crawled_at TEXT
                )
            ''')
            
            # 插入数据
            for story in self.stories:
                cursor.execute('''
                    INSERT OR REPLACE INTO stories 
                    (id, title, category_id, category_name, excerpt, length, crawled_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    story['id'],
                    story['title'],
                    story.get('category_id'),
                    story.get('category_name'),
                    story.get('excerpt', ''),
                    story.get('length', 0),
                    datetime.now().isoformat()
                ))
            
            for content in self.story_contents.values():
                cursor.execute('''
                    INSERT OR REPLACE INTO story_contents 
                    (story_id, title, category_name, content, content_length, crawled_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    content['id'],
                    content['title'],
                    content['category_name'],
                    content['content'],
                    content['length'],
                    content['crawled_at']
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Data saved to {STORIES_JSON_FILE}, {CONTENT_JSON_FILE}, and {DATABASE_FILE}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False
    
    def generate_report(self):
        """生成爬取报告"""
        try:
            self.crawl_stats['end_time'] = datetime.now().isoformat()
            self.crawl_stats['duration'] = str(datetime.fromisoformat(self.crawl_stats['end_time']) - 
                                             datetime.fromisoformat(self.crawl_stats['start_time']))
            
            self.crawl_stats['success_rate'] = (self.crawl_stats['stories_crawled'] / 
                                               max(self.crawl_stats['stories_found'], 1)) * 100
            
            # 添加详细统计
            self.crawl_stats['categories'] = self.categories
            self.crawl_stats['sample_stories'] = self.stories[:10] if self.stories else []
            
            if self.story_contents:
                content_lengths = [c['length'] for c in self.story_contents.values()]
                self.crawl_stats['content_stats'] = {
                    'total_contents': len(self.story_contents),
                    'avg_content_length': sum(content_lengths) / len(content_lengths),
                    'max_content_length': max(content_lengths),
                    'min_content_length': min(content_lengths)
                }
            
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.crawl_stats, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Report saved to: {REPORT_FILE}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    def run(self):
        """运行爬虫"""
        try:
            logger.info("Starting Optimized StoryNook crawler...")
            
            # 设置WebDriver
            if not self.setup_driver():
                return False
            
            # 爬取基本故事信息
            if not self.crawl_basic_stories():
                logger.error("Failed to crawl basic stories")
                return False
            
            # 获取少量故事内容作为样本
            self.get_sample_story_content(max_samples=3)
            
            # 保存数据
            self.save_data()
            
            # 生成报告
            self.generate_report()
            
            logger.info("Crawling completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Crawler failed: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """主函数"""
    crawler = OptimizedStoryNookCrawler()
    success = crawler.run()
    
    if success:
        print("\n" + "="*50)
        print("爬取完成！")
        print(f"故事总数: {crawler.crawl_stats['stories_found']}")
        print(f"成功爬取内容: {crawler.crawl_stats['stories_crawled']}")
        print(f"成功率: {crawler.crawl_stats['success_rate']:.2f}%")
        print(f"分类数量: {crawler.crawl_stats['categories_found']}")
        print(f"数据库文件: {DATABASE_FILE}")
        print(f"JSON文件: {STORIES_JSON_FILE}, {CONTENT_JSON_FILE}")
        print(f"报告文件: {REPORT_FILE}")
        print("="*50)
    else:
        print("爬取失败，请查看日志文件获取详细信息")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())