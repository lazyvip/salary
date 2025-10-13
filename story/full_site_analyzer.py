#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全站深度分析器 - 分析 storynook.cn 的完整结构
分析分页机制、所有分类、故事总数等
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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('full_site_analyzer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FullSiteAnalyzer:
    def __init__(self):
        self.base_url = "https://storynook.cn/"
        self.driver = None
        self.analysis_data = {
            "analysis_time": datetime.now().isoformat(),
            "base_url": self.base_url,
            "categories": [],
            "pagination_info": {},
            "total_stories_found": 0,
            "sample_stories": [],
            "site_structure": {},
            "navigation_elements": [],
            "load_more_mechanism": None
        }
        
    def setup_driver(self):
        """设置Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("WebDriver 设置成功")
            return True
        except Exception as e:
            logger.error(f"WebDriver 设置失败: {e}")
            return False
    
    def analyze_homepage(self):
        """分析首页结构"""
        try:
            logger.info("开始分析首页...")
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # 分析导航结构
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav a, .nav a, .menu a, .category a")
            for nav in nav_elements:
                try:
                    text = nav.text.strip()
                    href = nav.get_attribute('href')
                    if text and href:
                        self.analysis_data["navigation_elements"].append({
                            "text": text,
                            "href": href,
                            "is_category": "category" in href.lower() or any(cat in text for cat in ["故事", "童话", "寓言", "成语"])
                        })
                except:
                    continue
            
            # 分析页面中的故事卡片
            story_cards = self.driver.find_elements(By.CSS_SELECTOR, "[onclick*='showStory'], .story-card, .story-item")
            logger.info(f"首页发现 {len(story_cards)} 个故事卡片")
            
            # 提取故事信息
            for i, card in enumerate(story_cards[:10]):  # 只分析前10个作为样本
                try:
                    onclick = card.get_attribute('onclick')
                    if onclick and 'showStory' in onclick:
                        story_id_match = re.search(r'showStory\((\d+)\)', onclick)
                        if story_id_match:
                            story_id = int(story_id_match.group(1))
                            title = card.text.strip()
                            self.analysis_data["sample_stories"].append({
                                "id": story_id,
                                "title": title,
                                "source": "homepage"
                            })
                except:
                    continue
            
            # 检查是否有"加载更多"按钮
            load_more_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button:contains('更多'), button:contains('加载'), .load-more, .more-btn")
            if load_more_buttons:
                self.analysis_data["load_more_mechanism"] = "button"
                logger.info("发现加载更多按钮")
            
            # 检查分页元素
            pagination_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".pagination, .page-nav, .pager, [class*='page']")
            if pagination_elements:
                self.analysis_data["pagination_info"]["has_pagination"] = True
                logger.info("发现分页元素")
            
            return True
            
        except Exception as e:
            logger.error(f"分析首页失败: {e}")
            return False
    
    def discover_categories(self):
        """发现所有分类"""
        try:
            logger.info("开始发现分类...")
            
            # 从导航元素中提取分类
            categories = []
            for nav in self.analysis_data["navigation_elements"]:
                if nav["is_category"]:
                    categories.append({
                        "name": nav["text"],
                        "url": nav["href"],
                        "stories_count": 0
                    })
            
            # 尝试通过JavaScript获取更多分类信息
            try:
                js_categories = self.driver.execute_script("""
                    var categories = [];
                    var links = document.querySelectorAll('a[href*="category"], a[href*="type"]');
                    for(var i = 0; i < links.length; i++) {
                        var link = links[i];
                        if(link.textContent.trim()) {
                            categories.push({
                                name: link.textContent.trim(),
                                url: link.href
                            });
                        }
                    }
                    return categories;
                """)
                
                for cat in js_categories:
                    if not any(c["name"] == cat["name"] for c in categories):
                        categories.append({
                            "name": cat["name"],
                            "url": cat["url"],
                            "stories_count": 0
                        })
                        
            except Exception as e:
                logger.warning(f"JavaScript分类发现失败: {e}")
            
            # 如果没有发现分类，使用默认分类
            if not categories:
                categories = [
                    {"name": "睡前故事", "url": self.base_url + "?category=1", "stories_count": 0},
                    {"name": "童话故事", "url": self.base_url + "?category=2", "stories_count": 0},
                    {"name": "寓言故事", "url": self.base_url + "?category=3", "stories_count": 0},
                    {"name": "成语故事", "url": self.base_url + "?category=4", "stories_count": 0}
                ]
            
            self.analysis_data["categories"] = categories
            logger.info(f"发现 {len(categories)} 个分类")
            
            return True
            
        except Exception as e:
            logger.error(f"发现分类失败: {e}")
            return False
    
    def analyze_pagination_mechanism(self):
        """分析分页机制"""
        try:
            logger.info("开始分析分页机制...")
            
            # 尝试滚动到页面底部，看是否有无限滚动
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 检查页面高度变化（无限滚动的标志）
            initial_height = self.driver.execute_script("return document.body.scrollHeight")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height > initial_height:
                self.analysis_data["pagination_info"]["type"] = "infinite_scroll"
                logger.info("检测到无限滚动机制")
            else:
                # 检查是否有分页按钮
                page_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "a:contains('下一页'), button:contains('下一页'), .next, .page-next")
                if page_buttons:
                    self.analysis_data["pagination_info"]["type"] = "button_pagination"
                    logger.info("检测到按钮分页机制")
                else:
                    self.analysis_data["pagination_info"]["type"] = "single_page"
                    logger.info("可能是单页面或动态加载")
            
            # 尝试通过JavaScript分析更多故事
            try:
                story_count = self.driver.execute_script("""
                    var stories = document.querySelectorAll('[onclick*="showStory"]');
                    return stories.length;
                """)
                self.analysis_data["total_stories_found"] = story_count
                logger.info(f"当前页面发现 {story_count} 个故事")
                
            except Exception as e:
                logger.warning(f"JavaScript故事计数失败: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"分析分页机制失败: {e}")
            return False
    
    def test_story_loading(self):
        """测试故事加载机制"""
        try:
            logger.info("测试故事加载机制...")
            
            # 尝试点击第一个故事
            story_cards = self.driver.find_elements(By.CSS_SELECTOR, "[onclick*='showStory']")
            if story_cards:
                first_story = story_cards[0]
                onclick = first_story.get_attribute('onclick')
                
                # 提取故事ID
                story_id_match = re.search(r'showStory\((\d+)\)', onclick)
                if story_id_match:
                    story_id = story_id_match.group(1)
                    
                    # 尝试通过JavaScript获取故事内容
                    try:
                        story_content = self.driver.execute_script(f"""
                            // 尝试调用showStory函数
                            if(typeof showStory === 'function') {{
                                showStory({story_id});
                                // 等待内容加载
                                setTimeout(function() {{
                                    var modal = document.querySelector('.modal-content, .story-content, #storyModal');
                                    if(modal) {{
                                        return modal.textContent;
                                    }}
                                }}, 1000);
                            }}
                            return null;
                        """)
                        
                        if story_content:
                            self.analysis_data["story_loading_test"] = {
                                "success": True,
                                "method": "javascript_function",
                                "sample_content_length": len(story_content)
                            }
                            logger.info("故事加载测试成功")
                        else:
                            self.analysis_data["story_loading_test"] = {
                                "success": False,
                                "method": "javascript_function",
                                "error": "无法获取故事内容"
                            }
                            
                    except Exception as e:
                        logger.warning(f"JavaScript故事加载测试失败: {e}")
                        self.analysis_data["story_loading_test"] = {
                            "success": False,
                            "method": "javascript_function",
                            "error": str(e)
                        }
            
            return True
            
        except Exception as e:
            logger.error(f"故事加载测试失败: {e}")
            return False
    
    def save_analysis_report(self):
        """保存分析报告"""
        try:
            # 保存详细分析报告
            with open('full_site_analysis_report.json', 'w', encoding='utf-8') as f:
                json.dump(self.analysis_data, f, ensure_ascii=False, indent=2)
            
            # 生成简要报告
            summary = {
                "分析时间": self.analysis_data["analysis_time"],
                "发现的分类数量": len(self.analysis_data["categories"]),
                "分类列表": [cat["name"] for cat in self.analysis_data["categories"]],
                "当前页面故事数量": self.analysis_data["total_stories_found"],
                "分页机制": self.analysis_data["pagination_info"].get("type", "未知"),
                "加载更多机制": self.analysis_data["load_more_mechanism"],
                "导航元素数量": len(self.analysis_data["navigation_elements"]),
                "样本故事数量": len(self.analysis_data["sample_stories"])
            }
            
            with open('site_analysis_summary.json', 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info("分析报告保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存分析报告失败: {e}")
            return False
    
    def run_analysis(self):
        """运行完整分析"""
        try:
            logger.info("开始全站分析...")
            
            if not self.setup_driver():
                return False
            
            # 执行各项分析
            self.analyze_homepage()
            self.discover_categories()
            self.analyze_pagination_mechanism()
            self.test_story_loading()
            
            # 保存报告
            self.save_analysis_report()
            
            logger.info("全站分析完成！")
            return True
            
        except Exception as e:
            logger.error(f"全站分析失败: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def main():
    analyzer = FullSiteAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("✅ 全站分析完成！")
        print("📊 查看分析报告:")
        print("   - full_site_analysis_report.json (详细报告)")
        print("   - site_analysis_summary.json (简要报告)")
    else:
        print("❌ 全站分析失败，请查看日志文件")

if __name__ == "__main__":
    main()