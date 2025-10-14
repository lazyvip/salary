#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Story Extractor - 快速故事提取器
只提取故事的基本信息，不获取详细内容，避免超时问题
"""

import json
import sqlite3
import logging
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quick_extractor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class QuickStoryExtractor:
    def __init__(self):
        self.driver = None
        self.stories = []
        
    def setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            # 使用本地ChromeDriver
            service = Service(r'F:\个人文档\website\salary\story\chromedriver_exe\chromedriver.exe')
            
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            logging.info("WebDriver setup successful with local ChromeDriver")
            return True
            
        except Exception as e:
            logging.error(f"Failed to setup WebDriver: {e}")
            return False
    
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
            
            return True
            
        except Exception as e:
            logging.error(f"Page load timeout: {e}")
            return False
    
    def extract_stories(self):
        """提取故事基本信息"""
        try:
            logging.info("Extracting story list...")
            
            # 等待页面稳定
            time.sleep(3)
            
            # 查找所有带有onclick的content-card元素
            story_cards = self.driver.find_elements(By.CSS_SELECTOR, ".content-card[onclick]")
            logging.info(f"Found {len(story_cards)} story cards with onclick")
            
            if not story_cards:
                logging.warning("No story cards found")
                return []
            
            stories = []
            
            for i, card in enumerate(story_cards):
                try:
                    onclick_attr = card.get_attribute('onclick')
                    if not onclick_attr:
                        continue
                    
                    # 使用正则表达式提取故事信息
                    # onclick="loadStoryDetail({'id':1,'category_id':1,'title':'小老鼠打电话','excerpt':'小老鼠要给奶奶打电话...','category_name':'睡前故事','length':467})"
                    pattern = r"loadStoryDetail\(\{([^}]+)\}\)"
                    match = re.search(pattern, onclick_attr)
                    
                    if match:
                        story_data_str = match.group(1)
                        
                        # 提取各个字段 - 注意实际格式使用单引号
                        id_match = re.search(r"'id':(\d+)", story_data_str)
                        category_id_match = re.search(r"'category_id':(\d+)", story_data_str)
                        title_match = re.search(r"'title':'([^']+)'", story_data_str)
                        excerpt_match = re.search(r"'excerpt':'([^']*)'", story_data_str)  # 允许空内容
                        category_name_match = re.search(r"'category_name':'([^']+)'", story_data_str)
                        length_match = re.search(r"'length':(\d+)", story_data_str)  # length是数字，不是字符串
                        
                        if all([id_match, title_match]):
                            story = {
                                'id': int(id_match.group(1)),
                                'title': title_match.group(1),
                                'category_id': int(category_id_match.group(1)) if category_id_match else None,
                                'excerpt': excerpt_match.group(1) if excerpt_match else '',
                                'category_name': category_name_match.group(1) if category_name_match else '',
                                'length': int(length_match.group(1)) if length_match else 0,
                                'extracted_at': datetime.now().isoformat()
                            }
                            
                            stories.append(story)
                            logging.info(f"Extracted story: {story['title']}")
                        
                except Exception as e:
                    logging.error(f"Error extracting story {i}: {e}")
                    continue
            
            logging.info(f"Successfully extracted {len(stories)} stories")
            return stories
            
        except Exception as e:
            logging.error(f"Error extracting stories: {e}")
            return []
    
    def save_to_json(self, stories, filename='quick_stories.json'):
        """保存到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stories, f, ensure_ascii=False, indent=2)
            logging.info(f"Saved {len(stories)} stories to {filename}")
        except Exception as e:
            logging.error(f"Error saving to JSON: {e}")
    
    def save_to_database(self, stories, db_name='quick_stories.db'):
        """保存到SQLite数据库"""
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    category_id INTEGER,
                    excerpt TEXT,
                    category_name TEXT,
                    length TEXT,
                    extracted_at TEXT
                )
            ''')
            
            # 插入数据
            for story in stories:
                cursor.execute('''
                    INSERT OR REPLACE INTO stories 
                    (id, title, category_id, excerpt, category_name, length, extracted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    story['id'],
                    story['title'],
                    story['category_id'],
                    story['excerpt'],
                    story['category_name'],
                    story['length'],
                    story['extracted_at']
                ))
            
            conn.commit()
            conn.close()
            logging.info(f"Saved {len(stories)} stories to database {db_name}")
            
        except Exception as e:
            logging.error(f"Error saving to database: {e}")
    
    def generate_report(self, stories):
        """生成爬取报告"""
        report = {
            'crawl_time': datetime.now().isoformat(),
            'total_stories': len(stories),
            'categories': {},
            'lengths': {},
            'sample_stories': stories[:5] if stories else []
        }
        
        # 统计分类
        for story in stories:
            category = story.get('category_name', 'Unknown')
            report['categories'][category] = report['categories'].get(category, 0) + 1
        
        # 统计长度
        for story in stories:
            length = story.get('length', 'Unknown')
            report['lengths'][length] = report['lengths'].get(length, 0) + 1
        
        # 保存报告
        with open('quick_crawl_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Generated crawl report: {report['total_stories']} stories")
        return report
    
    def run(self):
        """运行快速提取器"""
        try:
            logging.info("Starting Quick Story Extractor...")
            
            if not self.setup_driver():
                return False
            
            # 导航到网站
            logging.info("Navigating to https://storynook.cn/")
            self.driver.get("https://storynook.cn/")
            
            # 等待页面加载
            if not self.wait_for_page_load():
                return False
            
            # 提取故事
            stories = self.extract_stories()
            
            if stories:
                # 保存数据
                self.save_to_json(stories)
                self.save_to_database(stories)
                
                # 生成报告
                report = self.generate_report(stories)
                
                logging.info(f"Quick extraction completed successfully!")
                logging.info(f"Total stories extracted: {len(stories)}")
                logging.info(f"Categories found: {list(report['categories'].keys())}")
                
                return True
            else:
                logging.error("No stories extracted")
                return False
                
        except Exception as e:
            logging.error(f"Error in quick extractor: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("WebDriver closed")

if __name__ == "__main__":
    extractor = QuickStoryExtractor()
    success = extractor.run()
    
    if success:
        print("✅ Quick story extraction completed successfully!")
        print("📁 Check the following files:")
        print("   - quick_stories.json (JSON data)")
        print("   - quick_stories.db (SQLite database)")
        print("   - quick_crawl_report.json (Crawl report)")
        print("   - quick_extractor.log (Log file)")
    else:
        print("❌ Quick story extraction failed. Check quick_extractor.log for details.")