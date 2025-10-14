#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import sqlite3
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_working_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class FinalWorkingCrawler:
    def __init__(self):
        self.driver = None
        self.stories = []
        self.story_contents = {}
        self.setup_driver()
    
    def setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # 使用本地ChromeDriver
            chromedriver_path = r"F:\个人文档\website\salary\story\chromedriver_exe\chromedriver.exe"
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(60)
            logging.info("WebDriver setup successful with local ChromeDriver")
            
        except Exception as e:
            logging.error(f"Failed to setup WebDriver: {e}")
            raise
    
    def wait_for_page_load(self):
        """等待页面完全加载"""
        try:
            # 等待document.readyState为complete
            WebDriverWait(self.driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            logging.info("Document ready state: complete")
            
            # 等待jQuery加载
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return typeof jQuery !== 'undefined'")
            )
            logging.info("jQuery loaded")
            
            # 等待loadStoryDetail函数加载
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return typeof loadStoryDetail === 'function'")
            )
            logging.info("loadStoryDetail function loaded")
            
            # 额外等待动态内容
            time.sleep(3)
            
        except TimeoutException as e:
            logging.warning(f"Page load timeout: {e}")
    
    def extract_stories_from_onclick(self):
        """从onclick属性中提取故事信息"""
        stories = []
        try:
            # 查找所有带onclick属性的content-card元素
            onclick_elements = self.driver.find_elements(By.CSS_SELECTOR, ".content-card[onclick]")
            logging.info(f"Found {len(onclick_elements)} story cards with onclick")
            
            for element in onclick_elements:
                try:
                    onclick_attr = element.get_attribute("onclick")
                    if onclick_attr and "loadStoryDetail" in onclick_attr:
                        # 使用正则表达式提取JSON数据
                        match = re.search(r"loadStoryDetail\((\{.*?\})\)", onclick_attr)
                        if match:
                            json_str = match.group(1)
                            # 修复JSON格式（将单引号替换为双引号）
                            json_str = json_str.replace("'", '"')
                            story_data = json.loads(json_str)
                            stories.append(story_data)
                            logging.info(f"Extracted story: {story_data['title']}")
                        
                except Exception as e:
                    logging.warning(f"Error extracting story from onclick: {e}")
                    continue
            
            logging.info(f"Successfully extracted {len(stories)} stories")
            return stories
            
        except Exception as e:
            logging.error(f"Error extracting stories from onclick: {e}")
            return []
    
    def get_story_content(self, story_id):
        """获取单个故事的详细内容"""
        try:
            logging.info(f"Getting content for story ID: {story_id}")
            
            # 使用JavaScript调用loadStoryDetail函数
            script = f"""
            return new Promise((resolve, reject) => {{
                // 创建一个临时的故事对象
                const tempStory = {{id: {story_id}}};
                
                // 调用loadStoryDetail
                loadStoryDetail(tempStory);
                
                // 等待内容加载
                setTimeout(() => {{
                    try {{
                        // 获取故事标题
                        const titleElement = document.querySelector('#story-title');
                        const title = titleElement ? titleElement.textContent : '';
                        
                        // 获取故事内容
                        const contentElement = document.querySelector('#story-content');
                        const content = contentElement ? contentElement.textContent : '';
                        
                        resolve({{
                            title: title,
                            content: content,
                            success: true
                        }});
                    }} catch (error) {{
                        resolve({{
                            error: error.message,
                            success: false
                        }});
                    }}
                }}, 3000);
            }});
            """
            
            result = self.driver.execute_async_script(script)
            
            if result.get('success'):
                logging.info(f"Successfully got content for story {story_id}")
                return {
                    'title': result['title'],
                    'content': result['content']
                }
            else:
                logging.warning(f"Failed to get content for story {story_id}: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting story content for ID {story_id}: {e}")
            return None
    
    def crawl_all_stories(self):
        """爬取所有故事"""
        try:
            logging.info("Starting to crawl all stories...")
            
            # 导航到网站
            logging.info("Navigating to https://storynook.cn/")
            self.driver.get("https://storynook.cn/")
            
            # 等待页面加载
            self.wait_for_page_load()
            
            # 提取故事列表
            logging.info("Extracting story list...")
            self.stories = self.extract_stories_from_onclick()
            
            if not self.stories:
                logging.error("No stories found!")
                return
            
            logging.info(f"Found {len(self.stories)} stories, now getting content...")
            
            # 获取前10个故事的详细内容作为示例
            sample_count = min(10, len(self.stories))
            for i, story in enumerate(self.stories[:sample_count]):
                try:
                    story_id = story['id']
                    logging.info(f"Processing story {i+1}/{sample_count}: {story['title']}")
                    
                    content = self.get_story_content(story_id)
                    if content:
                        self.story_contents[story_id] = content
                    
                    # 添加延迟避免请求过快
                    time.sleep(2)
                    
                except Exception as e:
                    logging.error(f"Error processing story {story.get('title', 'Unknown')}: {e}")
                    continue
            
            logging.info(f"Successfully crawled {len(self.story_contents)} story contents")
            
        except Exception as e:
            logging.error(f"Error crawling stories: {e}")
            raise
    
    def save_to_database(self):
        """保存数据到SQLite数据库"""
        try:
            conn = sqlite3.connect('final_working_stories.db')
            cursor = conn.cursor()
            
            # 创建故事表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY,
                    category_id INTEGER,
                    title TEXT,
                    excerpt TEXT,
                    category_name TEXT,
                    length INTEGER,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 插入故事数据
            for story in self.stories:
                story_id = story['id']
                content_data = self.story_contents.get(story_id, {})
                full_content = content_data.get('content', '')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO stories 
                    (id, category_id, title, excerpt, category_name, length, content)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    story['id'],
                    story['category_id'],
                    story['title'],
                    story['excerpt'],
                    story['category_name'],
                    story['length'],
                    full_content
                ))
            
            conn.commit()
            conn.close()
            logging.info(f"Saved {len(self.stories)} stories to database")
            
        except Exception as e:
            logging.error(f"Error saving to database: {e}")
    
    def save_to_json(self):
        """保存数据到JSON文件"""
        try:
            # 保存故事列表
            with open('final_working_stories.json', 'w', encoding='utf-8') as f:
                json.dump(self.stories, f, ensure_ascii=False, indent=2)
            
            # 保存故事内容
            with open('final_working_story_contents.json', 'w', encoding='utf-8') as f:
                json.dump(self.story_contents, f, ensure_ascii=False, indent=2)
            
            logging.info("Saved data to JSON files")
            
        except Exception as e:
            logging.error(f"Error saving to JSON: {e}")
    
    def generate_report(self):
        """生成爬取报告"""
        report = {
            "crawl_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_stories_found": len(self.stories),
            "stories_with_content": len(self.story_contents),
            "categories": {},
            "sample_stories": self.stories[:5] if self.stories else []
        }
        
        # 统计分类
        for story in self.stories:
            category = story['category_name']
            if category not in report["categories"]:
                report["categories"][category] = 0
            report["categories"][category] += 1
        
        # 保存报告
        with open('final_working_crawl_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logging.info("Generated crawl report")
        return report
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver closed")

def main():
    crawler = None
    try:
        logging.info("Starting Final Working Crawler...")
        crawler = FinalWorkingCrawler()
        
        # 爬取所有故事
        crawler.crawl_all_stories()
        
        # 保存数据
        crawler.save_to_database()
        crawler.save_to_json()
        
        # 生成报告
        report = crawler.generate_report()
        
        print("\n=== 爬取完成 ===")
        print(f"总共找到故事: {report['total_stories_found']}")
        print(f"获取内容的故事: {report['stories_with_content']}")
        print(f"故事分类: {list(report['categories'].keys())}")
        
        for category, count in report['categories'].items():
            print(f"  {category}: {count} 个故事")
        
        logging.info("Crawling completed successfully")
        
    except Exception as e:
        logging.error(f"Crawling failed: {e}")
        print(f"爬取失败: {e}")
    
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    main()