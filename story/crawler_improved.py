import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class StoryNookCrawler:
    def __init__(self):
        self.base_url = "https://storynook.cn"
        self.driver = None
        self.stories = []
        self.categories = set()
        self.seen_titles = set()  # 用于去重
        self.stories_data = {
            'crawl_info': {
                'start_time': datetime.now().isoformat(),
                'end_time': '',
                'total_stories': 0,
                'total_categories': 0
            },
            'categories': {},
            'stories': []
        }
        
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("Chrome驱动初始化成功")
        except Exception as e:
            print(f"Chrome驱动初始化失败: {e}")
            raise
    
    def wait_for_page_load(self, timeout=15):
        """等待页面加载完成"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(3)
        except TimeoutException:
            print("页面加载超时")
    
    def scroll_and_load_more(self):
        """滚动页面并加载更多内容"""
        print("开始滚动加载更多内容...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10  # 增加滚动次数
        
        while scroll_attempts < max_scrolls:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)  # 增加等待时间
            
            # 检查页面高度是否有变化
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                print(f"页面高度未变化，尝试次数: {scroll_attempts}")
                # 尝试点击"加载更多"按钮
                try:
                    load_more_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                        'button[class*="load"], button[class*="more"], .load-more, .btn-load')
                    for btn in load_more_buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            btn.click()
                            time.sleep(3)
                            break
                except:
                    pass
            else:
                scroll_attempts = 0
                last_height = new_height
                print(f"页面高度变化: {new_height}")
            
            time.sleep(2)
        
        print("滚动加载完成")
    
    def get_story_cards(self):
        """获取页面上的所有故事卡片"""
        print("开始获取故事卡片...")
        
        try:
            # 使用正确的选择器
            story_cards = self.driver.find_elements(By.CSS_SELECTOR, '.content-card')
            print(f"找到 {len(story_cards)} 个故事卡片")
            return story_cards
            
        except Exception as e:
            print(f"获取故事卡片失败: {e}")
            return []
    
    def extract_story_info(self, card):
        """从故事卡片中提取信息"""
        story = {
            'title': '',
            'content': '',
            'category': '',
            'word_count': '',
            'author': '',
            'publish_date': ''
        }
        
        try:
            # 提取分类
            try:
                category_element = card.find_element(By.CSS_SELECTOR, '.card-category')
                story['category'] = category_element.text.strip()
                self.categories.add(story['category'])
            except:
                story['category'] = '睡前故事'  # 默认分类
                self.categories.add(story['category'])
            
            # 提取标题
            try:
                title_element = card.find_element(By.CSS_SELECTOR, '.card-title')
                story['title'] = title_element.text.strip()
            except:
                # 如果没有找到标题元素，尝试从卡片文本中提取
                card_text = card.text.strip()
                lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                if len(lines) >= 2:
                    story['title'] = lines[1]  # 通常第二行是标题
            
            # 提取内容摘要
            try:
                excerpt_element = card.find_element(By.CSS_SELECTOR, '.card-excerpt')
                story['content'] = excerpt_element.text.strip()
            except:
                # 如果没有找到摘要元素，尝试从卡片文本中提取
                card_text = card.text.strip()
                lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                if len(lines) >= 3:
                    story['content'] = lines[2]  # 通常第三行是内容摘要
            
            # 去重检查
            if story['title'] in self.seen_titles:
                return None
            
            self.seen_titles.add(story['title'])
            
        except Exception as e:
            print(f"提取故事信息失败: {e}")
        
        return story if story['title'] and story['content'] else None
        
    def crawl_all_stories(self):
        """爬取所有故事"""
        try:
            self.setup_driver()
            
            print(f"开始访问: {self.base_url}")
            self.driver.get(self.base_url)
            self.wait_for_page_load()
            
            # 滚动加载更多内容
            self.scroll_and_load_more()
            
            print("开始提取故事卡片...")
            story_cards = self.get_story_cards()
            
            if not story_cards:
                print("未找到故事卡片")
                return
            
            print(f"开始处理 {len(story_cards)} 个故事卡片...")
            
            # 处理所有找到的卡片
            for i, card in enumerate(story_cards):
                try:
                    print(f"处理第 {i+1}/{len(story_cards)} 个故事...")
                    story = self.extract_story_info(card)
                    
                    if story and story['title']:
                        self.stories.append(story)
                        print(f"成功提取故事: {story['title'][:50]}... (分类: {story['category']})")
                    
                    # 每处理20个故事休息一下
                    if (i + 1) % 20 == 0:
                        print(f"已处理 {i+1} 个故事，休息2秒...")
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"处理故事卡片时出错: {e}")
                    continue
            
            print(f"爬取完成，共获得 {len(self.stories)} 个唯一故事")
            print(f"涵盖分类: {list(self.categories)}")
            
        except Exception as e:
            print(f"爬取过程中出现错误: {e}")
        
    def update_stories_data(self):
        """更新故事数据结构"""
        # 按分类组织故事
        for story in self.stories:
            category = story.get('category', '未分类')
            if category not in self.stories_data['categories']:
                self.stories_data['categories'][category] = {
                    'name': category,
                    'story_count': 0,
                    'stories': []
                }
            
            self.stories_data['categories'][category]['stories'].append(story)
            self.stories_data['categories'][category]['story_count'] += 1
        
        self.stories_data['stories'] = self.stories
        
        # 更新爬取信息
        self.stories_data['crawl_info'].update({
            'end_time': datetime.now().isoformat(),
            'total_stories': len(self.stories),
            'total_categories': len(self.stories_data['categories'])
        })
        
        print(f"\n爬取完成！")
        print(f"总共获得 {self.stories_data['crawl_info']['total_stories']} 个故事")
        print(f"涵盖 {self.stories_data['crawl_info']['total_categories']} 个分类")
        
    def save_data(self, filename='stories_data.json'):
        """保存爬取的数据到JSON文件"""
        try:
            # 更新数据结构
            self.update_stories_data()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.stories_data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到: {filename}")
            
            # 同时生成一个爬取报告
            report_filename = 'crawl_report.txt'
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write("小故事铺网站爬取报告\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"爬取开始时间: {self.stories_data['crawl_info']['start_time']}\n")
                f.write(f"爬取结束时间: {self.stories_data['crawl_info']['end_time']}\n")
                f.write(f"总故事数量: {self.stories_data['crawl_info']['total_stories']}\n")
                f.write(f"总分类数量: {self.stories_data['crawl_info']['total_categories']}\n\n")
                
                f.write("各分类故事数量:\n")
                f.write("-" * 30 + "\n")
                for category_name, category_data in self.stories_data['categories'].items():
                    f.write(f"{category_name}: {category_data['story_count']} 个故事\n")
                
                f.write("\n故事详情:\n")
                f.write("-" * 30 + "\n")
                for i, story in enumerate(self.stories, 1):
                    f.write(f"{i}. {story['title']} ({story['category']})\n")
                    if story['content']:
                        f.write(f"   内容预览: {story['content'][:100]}...\n")
                    f.write("\n")
                    
            print(f"爬取报告已保存到: {report_filename}")
            
        except Exception as e:
            print(f"保存数据时出错: {e}")

def main():
    """主函数"""
    crawler = StoryNookCrawler()
    
    try:
        # 开始爬取
        crawler.crawl_all_stories()
        
        # 保存数据
        crawler.save_data()
        
    except KeyboardInterrupt:
        print("\n用户中断爬取...")
        crawler.save_data()
    except Exception as e:
        print(f"爬取过程中出现错误: {e}")
        crawler.save_data()
    finally:
        if crawler.driver:
            crawler.driver.quit()

if __name__ == "__main__":
    main()