#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import logging
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
        logging.FileHandler('page_analyzer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class PageStructureAnalyzer:
    def __init__(self):
        self.driver = None
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
            
            # 等待页面标题
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.title and driver.title != ""
            )
            logging.info(f"Page title loaded: {self.driver.title}")
            
            # 额外等待动态内容
            time.sleep(5)
            
        except TimeoutException as e:
            logging.warning(f"Page load timeout: {e}")
    
    def analyze_page_structure(self):
        """分析页面结构"""
        try:
            logging.info("Navigating to https://storynook.cn/")
            self.driver.get("https://storynook.cn/")
            
            self.wait_for_page_load()
            
            # 获取页面源码长度
            page_source_length = len(self.driver.page_source)
            logging.info(f"Page source length: {page_source_length}")
            
            # 分析页面结构
            structure_info = {
                "page_title": self.driver.title,
                "page_url": self.driver.current_url,
                "page_source_length": page_source_length,
                "elements_analysis": {}
            }
            
            # 检查各种可能的容器元素
            containers_to_check = [
                "#story-grid",
                ".story-grid", 
                ".content-card",
                ".story-card",
                ".story-item",
                ".story-list",
                "#main-content",
                ".main-content",
                "#content",
                ".content",
                "main",
                ".container",
                "#app",
                ".app"
            ]
            
            for selector in containers_to_check:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        element = elements[0]
                        structure_info["elements_analysis"][selector] = {
                            "found": True,
                            "count": len(elements),
                            "tag_name": element.tag_name,
                            "class_name": element.get_attribute("class"),
                            "id": element.get_attribute("id"),
                            "text_length": len(element.text),
                            "inner_html_length": len(element.get_attribute("innerHTML") or ""),
                            "children_count": len(element.find_elements(By.XPATH, "./*"))
                        }
                        logging.info(f"Found {selector}: {len(elements)} elements")
                    else:
                        structure_info["elements_analysis"][selector] = {"found": False}
                        logging.info(f"Not found: {selector}")
                except Exception as e:
                    structure_info["elements_analysis"][selector] = {"found": False, "error": str(e)}
                    logging.warning(f"Error checking {selector}: {e}")
            
            # 检查是否有onclick属性的元素
            onclick_elements = self.driver.find_elements(By.XPATH, "//*[@onclick]")
            structure_info["onclick_elements_count"] = len(onclick_elements)
            logging.info(f"Found {len(onclick_elements)} elements with onclick attributes")
            
            # 获取前几个onclick元素的信息
            onclick_samples = []
            for i, element in enumerate(onclick_elements[:5]):
                try:
                    onclick_samples.append({
                        "tag_name": element.tag_name,
                        "onclick": element.get_attribute("onclick"),
                        "class_name": element.get_attribute("class"),
                        "text": element.text[:100] if element.text else ""
                    })
                except Exception as e:
                    onclick_samples.append({"error": str(e)})
            
            structure_info["onclick_samples"] = onclick_samples
            
            # 检查JavaScript变量
            js_variables = {}
            js_checks = [
                "typeof window.currentState",
                "typeof window.supabaseClient", 
                "typeof loadStoryDetail",
                "typeof jQuery",
                "document.readyState"
            ]
            
            for check in js_checks:
                try:
                    result = self.driver.execute_script(f"return {check}")
                    js_variables[check] = result
                except Exception as e:
                    js_variables[check] = f"Error: {e}"
            
            structure_info["javascript_variables"] = js_variables
            
            # 尝试获取当前状态
            try:
                current_state = self.driver.execute_script("return window.currentState")
                structure_info["current_state"] = current_state
                logging.info(f"Current state: {current_state}")
            except Exception as e:
                structure_info["current_state"] = f"Error: {e}"
                logging.warning(f"Could not get current state: {e}")
            
            # 保存分析结果
            with open('page_structure_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(structure_info, f, ensure_ascii=False, indent=2)
            
            logging.info("Page structure analysis completed")
            return structure_info
            
        except Exception as e:
            logging.error(f"Error analyzing page structure: {e}")
            raise
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver closed")

def main():
    analyzer = None
    try:
        logging.info("Starting page structure analysis...")
        analyzer = PageStructureAnalyzer()
        
        structure_info = analyzer.analyze_page_structure()
        
        print("\n=== 页面结构分析结果 ===")
        print(f"页面标题: {structure_info['page_title']}")
        print(f"页面URL: {structure_info['page_url']}")
        print(f"页面源码长度: {structure_info['page_source_length']}")
        print(f"带onclick属性的元素数量: {structure_info['onclick_elements_count']}")
        
        print("\n=== 找到的容器元素 ===")
        for selector, info in structure_info['elements_analysis'].items():
            if info.get('found'):
                print(f"{selector}: {info['count']} 个元素, 子元素: {info['children_count']}")
        
        print("\n=== JavaScript变量检查 ===")
        for var, value in structure_info['javascript_variables'].items():
            print(f"{var}: {value}")
        
        if structure_info['onclick_samples']:
            print("\n=== onclick元素示例 ===")
            for i, sample in enumerate(structure_info['onclick_samples']):
                if 'error' not in sample:
                    print(f"{i+1}. {sample['tag_name']} - {sample['onclick'][:100]}...")
        
        logging.info("Analysis completed successfully")
        
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        print(f"分析失败: {e}")
    
    finally:
        if analyzer:
            analyzer.close()

if __name__ == "__main__":
    main()