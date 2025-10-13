#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版Selenium爬虫 - 使用最新的webdriver-manager
处理JavaScript渲染的故事网站，自动匹配Chrome版本
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
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

class FinalSeleniumCrawler:
    def __init__(self, headless=False):
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
                logging.FileHandler('final_selenium.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 初始化数据库
        self.init_database()
        
    def create_driver(self):
        """创建Chrome WebDriver实例"""
        chrome_options = Options()
        
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
            # 使用webdriver-manager自动下载匹配的ChromeDriver
            self.logger.info("正在初始化ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 执行反检测脚本
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ WebDriver创建成功")
            return driver
        except Exception as e:
            self.logger.error(f"❌ 创建WebDriver失败: {e}")
            return None
    
    def init_database(self):
        """初始化SQLite数据库"""
        self.conn = sqlite3.connect('final_selenium_stories.db', check_same_thread=False)
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
        self.logger.info("✅ 数据库初始化完成")
    
    def wait_for_content_load(self, driver, timeout=30):
        """等待页面内容加载完成"""
        try:
            # 等待页面基本结构加载
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待JavaScript执行
            self.logger.info("⏳ 等待JavaScript执行...")
            time.sleep(8)  # 等待JavaScript完全执行
            
            # 检查页面加载状态
            try:
                ready_state = driver.execute_script("return document.readyState")
                self.logger.info(f"📄 页面状态: {ready_state}")
                
                # 等待可能的动态内容加载
                for i in range(3):
                    time.sleep(3)
                    current_length = len(driver.page_source)
                    self.logger.info(f"📏 页面源码长度: {current_length}")
                    
                    # 检查是否有故事相关内容
                    page_text = driver.execute_script("return document.body.innerText")
                    if '故事' in page_text and len(page_text) > 500:
                        self.logger.info("✅ 检测到故事内容")
                        break
                
            except Exception as e:
                self.logger.debug(f"JavaScript执行检查失败: {e}")
            
            return True
        except TimeoutException:
            self.logger.warning(f"⚠️ 页面加载超时: {driver.current_url}")
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
            with open(f'final_debug_{story_id}.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            self.logger.info(f"📖 页面标题: {driver.title}")
            self.logger.info(f"🔗 页面URL: {driver.current_url}")
            self.logger.info(f"📏 页面源码长度: {len(page_source)}")
            
            # 检查页面是否包含有效内容
            page_text = soup.get_text()
            if '404' in page_text or 'Not Found' in page_text:
                self.logger.warning(f"⚠️ 故事 {story_id} 页面返回404")
                return None
            
            # 尝试多种方式提取标题
            title = None
            
            # 1. 从页面标题提取
            page_title = driver.title.strip()
            if page_title and '小故事铺' not in page_title and len(page_title) < 200:
                title = page_title
                self.logger.info(f"📝 从页面标题提取: {title}")
            
            # 2. 使用JavaScript查找标题
            if not title:
                try:
                    js_title = driver.execute_script("""
                        // 查找可能的标题元素
                        var titleSelectors = [
                            'h1', 'h2', 'h3', '.title', '.story-title', '.post-title',
                            '.article-title', '.content-title', '[class*="title"]',
                            '[id*="title"]', '.story-name', '.article-name'
                        ];
                        
                        for (var i = 0; i < titleSelectors.length; i++) {
                            var elements = document.querySelectorAll(titleSelectors[i]);
                            for (var j = 0; j < elements.length; j++) {
                                var text = elements[j].innerText || elements[j].textContent;
                                if (text && text.length > 2 && text.length < 200 && 
                                    !text.includes('小故事铺') && 
                                    !text.includes('首页') &&
                                    !text.includes('导航') &&
                                    !text.includes('菜单')) {
                                    return text.trim();
                                }
                            }
                        }
                        return null;
                    """)
                    
                    if js_title:
                        title = js_title
                        self.logger.info(f"🔍 从JavaScript提取标题: {title}")
                except Exception as e:
                    self.logger.debug(f"JavaScript标题提取失败: {e}")
            
            # 提取内容
            content = None
            
            # 1. 使用JavaScript查找内容
            try:
                js_content = driver.execute_script("""
                    // 查找可能包含故事内容的元素
                    var contentSelectors = [
                        '.story-content', '.post-content', '.article-content',
                        '.content', '#content', 'article', '.main-content',
                        '.story-body', '.text-content', 'main', '.story-text',
                        '.article-body', '.post-body', '[class*="content"]',
                        '[id*="content"]', '.story-detail', '.article-detail'
                    ];
                    
                    for (var i = 0; i < contentSelectors.length; i++) {
                        var elements = document.querySelectorAll(contentSelectors[i]);
                        for (var j = 0; j < elements.length; j++) {
                            var text = elements[j].innerText || elements[j].textContent;
                            if (text && text.length > 200 && 
                                !text.includes('小故事铺汇集了各种类型') &&
                                !text.includes('版权所有') &&
                                !text.includes('联系我们')) {
                                return text.trim();
                            }
                        }
                    }
                    
                    // 如果没找到，尝试查找最长的文本块
                    var allElements = document.querySelectorAll('div, p, section, article, span');
                    var longestText = '';
                    
                    for (var k = 0; k < allElements.length; k++) {
                        var element = allElements[k];
                        // 跳过导航、菜单等元素
                        if (element.className && (
                            element.className.includes('nav') ||
                            element.className.includes('menu') ||
                            element.className.includes('header') ||
                            element.className.includes('footer') ||
                            element.className.includes('sidebar')
                        )) {
                            continue;
                        }
                        
                        var text = element.innerText || element.textContent;
                        if (text && text.length > longestText.length && text.length > 200) {
                            longestText = text;
                        }
                    }
                    
                    return longestText || null;
                """)
                
                if js_content and len(js_content) > 200:
                    content = js_content
                    self.logger.info(f"📄 从JavaScript提取内容: {len(content)}字符")
            except Exception as e:
                self.logger.debug(f"JavaScript内容提取失败: {e}")
            
            # 2. 从HTML元素提取（备用方法）
            if not content:
                content_selectors = [
                    '.story-content', '.post-content', '.article-content',
                    '.content', '#content', 'article', '.main-content',
                    '.story-body', '.text-content', 'main', '.story-text',
                    '.article-body', '.post-body'
                ]
                
                for selector in content_selectors:
                    elements = soup.select(selector)
                    for elem in elements:
                        text = elem.get_text(strip=True)
                        if text and len(text) > 200 and '小故事铺汇集了各种类型' not in text:
                            content = text
                            self.logger.info(f"🔍 从{selector}提取内容: {len(text)}字符")
                            break
                    if content:
                        break
            
            # 3. 从页面所有文本中提取最长的段落（最后的备用方法）
            if not content:
                all_text = soup.get_text()
                paragraphs = [p.strip() for p in all_text.split('\n') if p.strip()]
                long_paragraphs = [p for p in paragraphs if len(p) > 200]
                if long_paragraphs:
                    content = max(long_paragraphs, key=len)
                    self.logger.info(f"📝 从最长段落提取内容: {len(content)}字符")
            
            # 验证提取的内容
            if not title:
                title = f"故事 {story_id}"
            
            if not content or len(content) < 100:
                self.logger.warning(f"⚠️ 故事 {story_id} 内容太短或为空: {len(content) if content else 0}字符")
                # 保存页面截图用于调试
                try:
                    driver.save_screenshot(f'final_debug_screenshot_{story_id}.png')
                    self.logger.info(f"📸 已保存调试截图: final_debug_screenshot_{story_id}.png")
                except:
                    pass
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
            '爱情故事': ['爱情', '恋爱', '情侣', '男友', '女友', '结婚', '婚姻', '浪漫', '约会', '表白'],
            '恐怖故事': ['恐怖', '鬼', '灵异', '惊悚', '可怕', '阴森', '诡异', '血腥', '死亡'],
            '励志故事': ['励志', '成功', '奋斗', '坚持', '梦想', '努力', '拼搏', '成长', '进步'],
            '儿童故事': ['小朋友', '孩子', '童话', '动物', '森林', '王子', '公主', '小熊', '小兔'],
            '历史故事': ['古代', '历史', '朝代', '皇帝', '将军', '战争', '传说', '古时'],
            '神话故事': ['神话', '仙人', '神仙', '龙', '凤凰', '传说', '神', '仙女', '天宫'],
            '寓言故事': ['寓言', '道理', '启示', '智慧', '哲理', '教训', '明白'],
            '民间故事': ['民间', '传说', '老人', '村庄', '乡村', '农夫', '老奶奶'],
            '科幻故事': ['科幻', '未来', '机器人', '太空', '外星人', '科技', '宇宙'],
            '悬疑故事': ['悬疑', '推理', '侦探', '谜团', '破案', '线索', '调查', '真相']
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
                self.logger.error(f"❌ 无法创建WebDriver，跳过故事 {story_id}")
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
            self.logger.error(f"❌ 保存故事到数据库失败: {e}")
    
    def crawl_stories(self, start_id=1, end_id=5):
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
                time.sleep(3)
                
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
            'stories_sample': self.stories  # 保存所有故事
        }
        
        # 保存JSON报告
        with open('final_selenium_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存所有故事到JSON
        with open('final_selenium_stories.json', 'w', encoding='utf-8') as f:
            json.dump(self.stories, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"""
=== 🎉 爬取完成 ===
总计故事: {self.total_count}
成功爬取: {self.success_count}
失败数量: {len(self.failed_ids)}
成功率: {success_rate:.2f}%
报告已保存到: final_selenium_report.json
故事数据已保存到: final_selenium_stories.json
数据库: final_selenium_stories.db
        """)
    
    def analyze_content_uniqueness(self):
        """分析内容唯一性"""
        if not self.stories:
            self.logger.warning("⚠️ 没有故事数据可分析")
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
                    'content_preview': story['content'][:300] + '...',
                    'category': story['category'],
                    'word_count': story['word_count']
                }
                for story in self.stories
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
        with open('final_selenium_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        return analysis
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    # 创建爬虫实例
    crawler = FinalSeleniumCrawler(headless=False)  # 非无头模式便于观察
    
    try:
        # 爬取前5个故事进行测试
        crawler.crawl_stories(start_id=1, end_id=5)
        
        # 分析内容唯一性
        crawler.analyze_content_uniqueness()
        
    except KeyboardInterrupt:
        crawler.logger.info("⚠️ 用户中断爬取")
    except Exception as e:
        crawler.logger.error(f"❌ 爬取过程中发生错误: {e}")
    finally:
        crawler.close()

if __name__ == "__main__":
    main()