#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版大规模爬虫 - 专门爬取 storynook.cn 的所有故事
使用现有ChromeDriver，支持深度滚动和多策略抓取
"""

import time
import json
import re
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import requests
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_mass_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedMassCrawler:
    def __init__(self):
        self.base_url = "https://storynook.cn/"
        self.driver = None
        self.all_stories = {}  # 使用字典去重
        self.story_contents = {}
        self.crawl_stats = {
            "start_time": datetime.now().isoformat(),
            "stories_found": 0,
            "stories_with_content": 0,
            "scroll_attempts": 0,
            "errors": 0
        }
        self.max_scroll_attempts = 50  # 增加滚动次数
        self.max_stories_target = 500  # 目标故事数量
        
    def setup_driver(self):
        """设置Chrome WebDriver - 使用现有驱动"""
        try:
            chrome_options = Options()
            # 不使用headless模式，便于调试
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 尝试使用现有的ChromeDriver
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                logger.warning(f"使用默认ChromeDriver失败: {e}")
                # 尝试使用本地ChromeDriver
                chrome_options.add_argument('--remote-debugging-port=9222')
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(30)
            logger.info("WebDriver 设置成功")
            return True
        except Exception as e:
            logger.error(f"WebDriver 设置失败: {e}")
            return False
    
    def extract_stories_from_current_page(self):
        """从当前页面提取所有故事"""
        try:
            # 等待页面加载完成
            time.sleep(2)
            
            # 方法1: 通过onclick属性提取
            story_elements = self.driver.find_elements(By.CSS_SELECTOR, "[onclick*='showStory']")
            new_stories_count = 0
            
            for element in story_elements:
                try:
                    onclick = element.get_attribute('onclick')
                    if onclick and 'showStory' in onclick:
                        story_id_match = re.search(r'showStory\((\d+)\)', onclick)
                        if story_id_match:
                            story_id = int(story_id_match.group(1))
                            title = element.text.strip()
                            
                            if story_id not in self.all_stories and title:
                                self.all_stories[story_id] = {
                                    "id": story_id,
                                    "title": title,
                                    "category_name": "睡前故事",
                                    "extracted_at": datetime.now().isoformat(),
                                    "source": "selenium_onclick"
                                }
                                new_stories_count += 1
                except Exception as e:
                    continue
            
            # 方法2: 通过页面源码正则提取
            try:
                page_source = self.driver.page_source
                onclick_pattern = r'onclick=["\']showStory\((\d+)\)["\'][^>]*>([^<]+)'
                matches = re.findall(onclick_pattern, page_source)
                
                for story_id, title in matches:
                    story_id = int(story_id)
                    title = title.strip()
                    if story_id not in self.all_stories and title:
                        self.all_stories[story_id] = {
                            "id": story_id,
                            "title": title,
                            "category_name": "睡前故事",
                            "extracted_at": datetime.now().isoformat(),
                            "source": "regex_page_source"
                        }
                        new_stories_count += 1
            except Exception as e:
                logger.warning(f"正则提取失败: {e}")
            
            logger.info(f"本次提取新增 {new_stories_count} 个故事，总计 {len(self.all_stories)} 个")
            return new_stories_count
            
        except Exception as e:
            logger.error(f"提取故事失败: {e}")
            return 0
    
    def aggressive_scroll_and_load(self):
        """激进的滚动和加载策略"""
        try:
            logger.info("开始激进滚动策略...")
            
            scroll_count = 0
            consecutive_no_new = 0
            last_story_count = 0
            
            while (scroll_count < self.max_scroll_attempts and 
                   len(self.all_stories) < self.max_stories_target and 
                   consecutive_no_new < 5):
                
                # 记录滚动前的故事数量
                before_count = len(self.all_stories)
                
                # 多种滚动策略
                if scroll_count % 3 == 0:
                    # 滚动到底部
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                elif scroll_count % 3 == 1:
                    # 分段滚动
                    self.driver.execute_script("window.scrollBy(0, 1000);")
                else:
                    # 滚动到特定位置
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_count * 500});")
                
                time.sleep(1.5)
                
                # 尝试点击各种可能的加载按钮
                load_buttons = [
                    "button:contains('更多')",
                    "button:contains('加载')", 
                    ".load-more",
                    ".more-btn",
                    "[onclick*='loadMore']",
                    "[onclick*='more']",
                    "a:contains('更多')",
                    ".btn-more"
                ]
                
                for selector in load_buttons:
                    try:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for button in buttons:
                            if button.is_displayed() and button.is_enabled():
                                self.driver.execute_script("arguments[0].click();", button)
                                time.sleep(2)
                                logger.info(f"点击了加载按钮: {selector}")
                                break
                    except:
                        continue
                
                # 尝试触发JavaScript事件
                try:
                    self.driver.execute_script("""
                        // 尝试触发滚动事件
                        window.dispatchEvent(new Event('scroll'));
                        window.dispatchEvent(new Event('resize'));
                        
                        // 尝试调用可能的加载函数
                        if(typeof loadMore === 'function') loadMore();
                        if(typeof loadMoreStories === 'function') loadMoreStories();
                        if(typeof showMore === 'function') showMore();
                    """)
                except:
                    pass
                
                # 提取当前页面的故事
                new_stories = self.extract_stories_from_current_page()
                
                # 检查是否有新故事
                after_count = len(self.all_stories)
                if after_count == before_count:
                    consecutive_no_new += 1
                else:
                    consecutive_no_new = 0
                
                scroll_count += 1
                self.crawl_stats["scroll_attempts"] = scroll_count
                
                logger.info(f"滚动 {scroll_count}/{self.max_scroll_attempts}, "
                          f"故事总数: {after_count}, "
                          f"连续无新故事: {consecutive_no_new}")
                
                # 等待页面稳定
                time.sleep(1)
            
            logger.info(f"滚动完成，共发现 {len(self.all_stories)} 个故事")
            return True
            
        except Exception as e:
            logger.error(f"滚动策略失败: {e}")
            return False
    
    def get_story_content_batch(self, story_ids, max_attempts=3):
        """批量获取故事内容"""
        try:
            logger.info(f"开始批量获取 {len(story_ids)} 个故事的内容...")
            success_count = 0
            
            for i, story_id in enumerate(story_ids):
                attempts = 0
                content = None
                
                while attempts < max_attempts and not content:
                    try:
                        # 尝试通过JavaScript获取内容
                        content = self.driver.execute_script(f"""
                            return new Promise((resolve) => {{
                                try {{
                                    if(typeof showStory === 'function') {{
                                        showStory({story_id});
                                        
                                        setTimeout(() => {{
                                            var selectors = [
                                                '#storyModal .modal-body',
                                                '.story-content',
                                                '.modal-content',
                                                '#story-content',
                                                '.story-text'
                                            ];
                                            
                                            for(var sel of selectors) {{
                                                var modal = document.querySelector(sel);
                                                if(modal && modal.textContent.trim().length > 50) {{
                                                    resolve(modal.textContent.trim());
                                                    return;
                                                }}
                                            }}
                                            resolve(null);
                                        }}, 2000);
                                    }} else {{
                                        resolve(null);
                                    }}
                                }} catch(e) {{
                                    resolve(null);
                                }}
                            }});
                        """)
                        
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
                            break
                        
                    except Exception as e:
                        logger.warning(f"获取故事 {story_id} 内容失败 (尝试 {attempts + 1}): {e}")
                    
                    attempts += 1
                    time.sleep(1)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"已处理 {i + 1}/{len(story_ids)} 个故事，成功: {success_count}")
                
                time.sleep(0.5)  # 避免请求过快
            
            logger.info(f"批量获取完成，成功获取 {success_count} 个故事内容")
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
            with open('mass_crawled_stories.json', 'w', encoding='utf-8') as f:
                json.dump(stories_list, f, ensure_ascii=False, indent=2)
            
            # 保存故事内容
            if self.story_contents:
                contents_list = list(self.story_contents.values())
                with open('mass_story_contents.json', 'w', encoding='utf-8') as f:
                    json.dump(contents_list, f, ensure_ascii=False, indent=2)
            
            # 保存到SQLite数据库
            self.save_to_database()
            
            # 保存爬取报告
            with open('mass_crawl_report.json', 'w', encoding='utf-8') as f:
                json.dump(self.crawl_stats, f, ensure_ascii=False, indent=2)
            
            logger.info("所有数据保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            return False
    
    def save_to_database(self):
        """保存到SQLite数据库"""
        try:
            conn = sqlite3.connect('mass_crawled_stories.db')
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
            logger.info("开始大规模故事爬取...")
            
            if not self.setup_driver():
                return False
            
            # 访问主页
            logger.info("访问主页...")
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # 执行激进滚动策略
            self.aggressive_scroll_and_load()
            
            # 如果发现了故事，尝试获取内容
            if self.all_stories:
                story_ids = list(self.all_stories.keys())[:100]  # 获取前100个故事的内容
                self.get_story_content_batch(story_ids)
            
            # 保存所有数据
            self.save_all_data()
            
            logger.info("大规模爬取完成！")
            logger.info(f"总共发现 {len(self.all_stories)} 个故事")
            logger.info(f"获取到 {len(self.story_contents)} 个故事的完整内容")
            
            return True
            
        except Exception as e:
            logger.error(f"大规模爬取失败: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    crawler = EnhancedMassCrawler()
    success = crawler.run_mass_crawl()
    
    if success:
        print("✅ 大规模爬取完成！")
        print("📊 爬取结果:")
        print(f"   - 发现故事: {len(crawler.all_stories)} 个")
        print(f"   - 获取内容: {len(crawler.story_contents)} 个")
        print("📁 生成文件:")
        print("   - mass_crawled_stories.json (所有故事列表)")
        print("   - mass_story_contents.json (故事内容)")
        print("   - mass_crawled_stories.db (SQLite数据库)")
        print("   - mass_crawl_report.json (爬取报告)")
    else:
        print("❌ 大规模爬取失败，请查看日志文件")

if __name__ == "__main__":
    main()