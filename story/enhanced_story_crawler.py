#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import re
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

class EnhancedStoryCrawler:
    def __init__(self):
        self.base_url = "https://storynook.cn/"
        self.driver = None
        self.all_stories = []
        self.story_contents = {}
        self.categories_found = set()
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enhanced_crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = Service('./chromedriver_exe/chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.logger.info("✅ WebDriver设置成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ WebDriver设置失败: {e}")
            return False
    
    def wait_for_page_ready(self, timeout=30):
        """等待页面完全加载"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return typeof jQuery !== 'undefined'")
            )
            
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return typeof loadStoryDetail === 'function'")
            )
            
            time.sleep(3)
            self.logger.info("✅ 页面完全加载完成")
            return True
            
        except TimeoutException:
            self.logger.warning("⚠️ 页面加载超时，但继续执行")
            return False
    
    def extract_story_data_from_onclick(self, onclick_attr):
        """从onclick属性提取故事数据"""
        try:
            pattern = r"loadStoryDetail\(\s*\{\s*'id'\s*:\s*(\d+)\s*,\s*'category_id'\s*:\s*(\d+)\s*,\s*'title'\s*:\s*'([^']*?)'\s*,\s*'excerpt'\s*:\s*'([^']*?)'\s*,\s*'category_name'\s*:\s*'([^']*?)'\s*,\s*'length'\s*:\s*(\d+)\s*\}\s*\)"
            
            match = re.search(pattern, onclick_attr)
            if match:
                story_data = {
                    'id': int(match.group(1)),
                    'category_id': int(match.group(2)),
                    'title': match.group(3),
                    'excerpt': match.group(4),
                    'category_name': match.group(5),
                    'length': int(match.group(6)),
                    'extracted_at': datetime.now().isoformat()
                }
                
                # 记录发现的分类
                self.categories_found.add(story_data['category_name'])
                return story_data
                
        except Exception as e:
            self.logger.warning(f"⚠️ 提取故事数据失败: {e}")
        
        return None
    
    def get_story_content(self, story_data, timeout=10):
        """获取故事的完整内容"""
        try:
            story_id = story_data['id']
            self.logger.info(f"📖 获取故事内容: {story_data['title']} (ID: {story_id})")
            
            # 构建JavaScript调用
            js_script = f"""
            return new Promise((resolve, reject) => {{
                try {{
                    // 调用loadStoryDetail函数
                    loadStoryDetail({{
                        'id': {story_data['id']},
                        'category_id': {story_data['category_id']},
                        'title': '{story_data['title']}',
                        'excerpt': '{story_data['excerpt']}',
                        'category_name': '{story_data['category_name']}',
                        'length': {story_data['length']}
                    }});
                    
                    // 等待内容加载
                    setTimeout(() => {{
                        // 尝试多种方式获取故事内容
                        var content = '';
                        
                        // 方法1: 查找故事内容容器
                        var contentElement = document.querySelector('.story-content, .content, .story-text, #story-content');
                        if (contentElement) {{
                            content = contentElement.innerText || contentElement.textContent;
                        }}
                        
                        // 方法2: 查找模态框内容
                        if (!content) {{
                            var modal = document.querySelector('.modal-body, .modal-content, .popup-content');
                            if (modal) {{
                                content = modal.innerText || modal.textContent;
                            }}
                        }}
                        
                        // 方法3: 查找任何包含大量文本的元素
                        if (!content) {{
                            var allElements = document.querySelectorAll('div, p, article');
                            for (var elem of allElements) {{
                                var text = elem.innerText || elem.textContent;
                                if (text && text.length > 200 && text.includes('{story_data['title']}')) {{
                                    content = text;
                                    break;
                                }}
                            }}
                        }}
                        
                        resolve({{
                            success: content.length > 0,
                            content: content,
                            length: content.length,
                            title: '{story_data['title']}'
                        }});
                    }}, 3000);
                    
                }} catch (error) {{
                    reject(error);
                }}
            }});
            """
            
            # 执行JavaScript并等待结果
            result = self.driver.execute_async_script(js_script)
            
            if result and result.get('success'):
                content = result['content'].strip()
                if content and len(content) > 100:  # 确保内容足够长
                    self.story_contents[story_id] = {
                        'id': story_id,
                        'title': story_data['title'],
                        'content': content,
                        'content_length': len(content),
                        'extracted_at': datetime.now().isoformat()
                    }
                    self.logger.info(f"✅ 成功获取故事内容: {story_data['title']} ({len(content)}字)")
                    return content
                else:
                    self.logger.warning(f"⚠️ 故事内容太短或为空: {story_data['title']}")
            else:
                self.logger.warning(f"⚠️ 未能获取故事内容: {story_data['title']}")
                
        except Exception as e:
            self.logger.error(f"❌ 获取故事内容失败 {story_data['title']}: {e}")
        
        return None
    
    def crawl_stories_from_page(self, get_content=True):
        """从当前页面爬取故事"""
        try:
            self.logger.info("🔍 开始爬取当前页面的故事...")
            
            # 查找故事卡片
            story_cards = self.driver.find_elements(By.CSS_SELECTOR, ".content-card")
            self.logger.info(f"📚 发现 {len(story_cards)} 个故事卡片")
            
            page_stories = []
            for i, card in enumerate(story_cards):
                try:
                    onclick = card.get_attribute('onclick') or ''
                    if 'loadStoryDetail' in onclick:
                        story_data = self.extract_story_data_from_onclick(onclick)
                        if story_data:
                            page_stories.append(story_data)
                            self.logger.info(f"📖 提取故事 {i+1}: {story_data['title']} ({story_data['category_name']})")
                            
                            # 获取完整内容
                            if get_content:
                                self.get_story_content(story_data)
                                time.sleep(1)  # 避免请求过快
                                
                except Exception as e:
                    self.logger.warning(f"⚠️ 处理故事卡片 {i+1} 失败: {e}")
                    continue
            
            self.all_stories.extend(page_stories)
            self.logger.info(f"✅ 本页成功提取 {len(page_stories)} 个故事")
            return page_stories
            
        except Exception as e:
            self.logger.error(f"❌ 爬取页面故事失败: {e}")
            return []
    
    def try_navigate_categories(self):
        """尝试导航到不同分类"""
        try:
            self.logger.info("🔍 尝试探索不同分类...")
            
            # 查找可能的分类链接或按钮
            category_selectors = [
                "a[href*='category']",
                ".category-link",
                ".nav-item",
                ".menu-item",
                "[data-category]",
                "[onclick*='category']"
            ]
            
            category_elements = []
            for selector in category_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                category_elements.extend(elements)
            
            self.logger.info(f"🔍 发现 {len(category_elements)} 个可能的分类元素")
            
            # 尝试点击不同的分类
            for i, element in enumerate(category_elements[:5]):  # 限制前5个
                try:
                    text = element.text.strip()
                    if text and len(text) < 20:
                        self.logger.info(f"🔗 尝试点击分类: {text}")
                        
                        # 保存当前URL
                        current_url = self.driver.current_url
                        
                        # 点击元素
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(3)
                        
                        # 等待页面加载
                        self.wait_for_page_ready(timeout=10)
                        
                        # 爬取这个分类的故事
                        category_stories = self.crawl_stories_from_page(get_content=False)
                        
                        if category_stories:
                            self.logger.info(f"✅ 分类 '{text}' 发现 {len(category_stories)} 个故事")
                        
                        # 返回原页面
                        if self.driver.current_url != current_url:
                            self.driver.get(self.base_url)
                            self.wait_for_page_ready()
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ 点击分类元素失败: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"❌ 分类导航失败: {e}")
    
    def try_load_more_content(self):
        """尝试加载更多内容"""
        try:
            self.logger.info("🔍 尝试加载更多内容...")
            
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 查找加载更多按钮
            load_more_selectors = [
                "button[onclick*='loadMore']",
                ".load-more",
                ".btn-load-more",
                "[data-action='load-more']",
                ".pagination a"
            ]
            
            for selector in load_more_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            self.logger.info(f"🔗 尝试点击加载更多: {element.text}")
                            self.driver.execute_script("arguments[0].click();", element)
                            time.sleep(3)
                            
                            # 检查是否有新内容
                            new_cards = self.driver.find_elements(By.CSS_SELECTOR, ".content-card")
                            self.logger.info(f"📚 加载更多后发现 {len(new_cards)} 个故事卡片")
                            break
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"❌ 加载更多内容失败: {e}")
    
    def save_data(self):
        """保存爬取的数据"""
        try:
            # 保存故事列表
            with open('enhanced_stories.json', 'w', encoding='utf-8') as f:
                json.dump(self.all_stories, f, ensure_ascii=False, indent=2)
            
            # 保存故事内容
            with open('enhanced_story_contents.json', 'w', encoding='utf-8') as f:
                json.dump(self.story_contents, f, ensure_ascii=False, indent=2)
            
            # 保存到数据库
            self.save_to_database()
            
            # 生成报告
            self.generate_report()
            
            self.logger.info("✅ 数据保存完成")
            
        except Exception as e:
            self.logger.error(f"❌ 保存数据失败: {e}")
    
    def save_to_database(self):
        """保存到SQLite数据库"""
        try:
            conn = sqlite3.connect('enhanced_stories.db')
            cursor = conn.cursor()
            
            # 创建故事表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    category_id INTEGER,
                    category_name TEXT,
                    excerpt TEXT,
                    length INTEGER,
                    extracted_at TEXT
                )
            ''')
            
            # 创建故事内容表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS story_contents (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    content_length INTEGER,
                    extracted_at TEXT
                )
            ''')
            
            # 插入故事数据
            for story in self.all_stories:
                cursor.execute('''
                    INSERT OR REPLACE INTO stories 
                    (id, title, category_id, category_name, excerpt, length, extracted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    story['id'], story['title'], story['category_id'],
                    story['category_name'], story['excerpt'], 
                    story['length'], story['extracted_at']
                ))
            
            # 插入故事内容
            for content_data in self.story_contents.values():
                cursor.execute('''
                    INSERT OR REPLACE INTO story_contents 
                    (id, title, content, content_length, extracted_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    content_data['id'], content_data['title'],
                    content_data['content'], content_data['content_length'],
                    content_data['extracted_at']
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info("✅ 数据库保存完成")
            
        except Exception as e:
            self.logger.error(f"❌ 数据库保存失败: {e}")
    
    def generate_report(self):
        """生成爬取报告"""
        try:
            # 统计分类
            category_stats = {}
            for story in self.all_stories:
                category = story['category_name']
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += 1
            
            # 统计字数
            lengths = [story['length'] for story in self.all_stories]
            
            report = {
                "crawl_time": datetime.now().isoformat(),
                "total_stories": len(self.all_stories),
                "total_contents": len(self.story_contents),
                "categories_found": list(self.categories_found),
                "category_stats": category_stats,
                "length_stats": {
                    "min": min(lengths) if lengths else 0,
                    "max": max(lengths) if lengths else 0,
                    "avg": sum(lengths) / len(lengths) if lengths else 0
                },
                "content_success_rate": len(self.story_contents) / len(self.all_stories) if self.all_stories else 0
            }
            
            with open('enhanced_crawl_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 爬取报告生成完成")
            self.logger.info(f"📊 总计: {len(self.all_stories)} 个故事, {len(self.story_contents)} 个完整内容")
            self.logger.info(f"📊 分类: {list(self.categories_found)}")
            
        except Exception as e:
            self.logger.error(f"❌ 生成报告失败: {e}")
    
    def run_enhanced_crawl(self):
        """运行增强版爬取"""
        try:
            self.logger.info("🚀 开始增强版故事爬取...")
            
            if not self.setup_driver():
                return False
            
            # 访问网站
            self.logger.info(f"🌐 访问网站: {self.base_url}")
            self.driver.get(self.base_url)
            self.wait_for_page_ready()
            
            # 爬取首页故事
            self.crawl_stories_from_page(get_content=True)
            
            # 尝试导航到不同分类
            self.try_navigate_categories()
            
            # 尝试加载更多内容
            self.try_load_more_content()
            
            # 再次爬取（可能有新内容）
            self.crawl_stories_from_page(get_content=True)
            
            # 保存数据
            self.save_data()
            
            self.logger.info("✅ 增强版爬取完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 增强版爬取失败: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    crawler = EnhancedStoryCrawler()
    crawler.run_enhanced_crawl()