#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPA网站动态加载分析器
专门分析单页应用的动态内容加载机制
"""

import time
import json
import logging
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

class SPAAnalyzer:
    def __init__(self):
        self.base_url = "https://storynook.cn"
        self.chromedriver_path = os.path.join(os.path.dirname(__file__), 'chromedriver_exe', 'chromedriver.exe')
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('spa_analyzer.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 验证ChromeDriver
        if not os.path.exists(self.chromedriver_path):
            raise FileNotFoundError(f"ChromeDriver未找到: {self.chromedriver_path}")
        
        self.network_logs = []
        self.api_requests = []
        
    def create_driver_with_logging(self):
        """创建带网络日志记录的Chrome WebDriver"""
        chrome_options = Options()
        
        # 启用网络日志
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        chrome_options.add_argument('--v=1')
        
        # 基本选项
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 启用性能日志以捕获网络请求
        chrome_options.add_experimental_option('perfLoggingPrefs', {
            'enableNetwork': True,
            'enablePage': True,
        })
        
        # 设置用户代理
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 启用开发者工具协议
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL', 'browser': 'ALL'}
        
        try:
            service = Service(self.chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options, desired_capabilities=caps)
            
            # 反检测
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ 带网络日志的WebDriver创建成功")
            return driver
        except Exception as e:
            self.logger.error(f"❌ 创建WebDriver失败: {e}")
            return None
    
    def analyze_homepage_structure(self):
        """分析主页结构和JavaScript文件"""
        driver = None
        try:
            driver = self.create_driver_with_logging()
            if not driver:
                return None
            
            self.logger.info("🔍 开始分析主页结构...")
            
            # 访问主页
            driver.get(self.base_url)
            time.sleep(5)
            
            # 获取页面基本信息
            page_info = {
                'title': driver.title,
                'url': driver.current_url,
                'page_source_length': len(driver.page_source)
            }
            
            self.logger.info(f"📖 页面标题: {page_info['title']}")
            self.logger.info(f"🔗 当前URL: {page_info['url']}")
            self.logger.info(f"📏 页面源码长度: {page_info['page_source_length']}")
            
            # 保存原始HTML
            with open('spa_homepage_original.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            
            # 分析JavaScript文件
            js_files = self.extract_javascript_files(driver)
            
            # 分析页面结构
            page_structure = self.analyze_page_elements(driver)
            
            # 等待动态内容加载
            self.logger.info("⏳ 等待动态内容加载...")
            time.sleep(10)
            
            # 再次获取页面源码，看是否有变化
            updated_source = driver.page_source
            with open('spa_homepage_after_js.html', 'w', encoding='utf-8') as f:
                f.write(updated_source)
            
            # 分析网络请求
            network_requests = self.capture_network_requests(driver)
            
            # 尝试查找故事列表或导航
            story_navigation = self.find_story_navigation(driver)
            
            analysis_result = {
                'page_info': page_info,
                'javascript_files': js_files,
                'page_structure': page_structure,
                'network_requests': network_requests,
                'story_navigation': story_navigation,
                'source_changed': len(updated_source) != len(driver.page_source)
            }
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"❌ 分析主页结构失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def extract_javascript_files(self, driver):
        """提取页面中的JavaScript文件"""
        try:
            # 使用JavaScript获取所有script标签
            scripts = driver.execute_script("""
                var scripts = document.querySelectorAll('script');
                var result = [];
                for (var i = 0; i < scripts.length; i++) {
                    var script = scripts[i];
                    result.push({
                        src: script.src || null,
                        inline: script.src ? false : true,
                        content_preview: script.src ? null : script.innerHTML.substring(0, 200),
                        type: script.type || 'text/javascript'
                    });
                }
                return result;
            """)
            
            self.logger.info(f"📜 发现 {len(scripts)} 个JavaScript文件/脚本")
            
            for i, script in enumerate(scripts):
                if script['src']:
                    self.logger.info(f"  外部JS {i+1}: {script['src']}")
                else:
                    self.logger.info(f"  内联JS {i+1}: {script['content_preview'][:100]}...")
            
            return scripts
            
        except Exception as e:
            self.logger.error(f"❌ 提取JavaScript文件失败: {e}")
            return []
    
    def analyze_page_elements(self, driver):
        """分析页面元素结构"""
        try:
            # 查找可能的容器元素
            containers = driver.execute_script("""
                var selectors = [
                    '#app', '#root', '#main', '.app', '.main', '.container',
                    '[id*="app"]', '[class*="app"]', '[id*="main"]', '[class*="main"]',
                    '[id*="content"]', '[class*="content"]', '[id*="story"]', '[class*="story"]'
                ];
                
                var result = [];
                for (var i = 0; i < selectors.length; i++) {
                    var elements = document.querySelectorAll(selectors[i]);
                    for (var j = 0; j < elements.length; j++) {
                        var elem = elements[j];
                        result.push({
                            selector: selectors[i],
                            tag: elem.tagName,
                            id: elem.id || null,
                            className: elem.className || null,
                            innerHTML_length: elem.innerHTML.length,
                            children_count: elem.children.length
                        });
                    }
                }
                return result;
            """)
            
            self.logger.info(f"🏗️ 发现 {len(containers)} 个可能的容器元素")
            
            return containers
            
        except Exception as e:
            self.logger.error(f"❌ 分析页面元素失败: {e}")
            return []
    
    def capture_network_requests(self, driver):
        """捕获网络请求"""
        try:
            # 获取性能日志
            logs = driver.get_log('performance')
            network_requests = []
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] in ['Network.requestWillBeSent', 'Network.responseReceived']:
                    network_requests.append({
                        'timestamp': log['timestamp'],
                        'method': message['message']['method'],
                        'params': message['message']['params']
                    })
            
            # 过滤出API请求
            api_requests = []
            for req in network_requests:
                if req['method'] == 'Network.requestWillBeSent':
                    url = req['params']['request']['url']
                    if any(keyword in url.lower() for keyword in ['api', 'ajax', 'json', 'story', 'data']):
                        api_requests.append({
                            'url': url,
                            'method': req['params']['request']['method'],
                            'headers': req['params']['request'].get('headers', {}),
                            'timestamp': req['timestamp']
                        })
            
            self.logger.info(f"🌐 捕获到 {len(network_requests)} 个网络请求")
            self.logger.info(f"🔌 发现 {len(api_requests)} 个可能的API请求")
            
            for api in api_requests:
                self.logger.info(f"  API: {api['method']} {api['url']}")
            
            return {
                'total_requests': len(network_requests),
                'api_requests': api_requests,
                'all_requests': network_requests[:50]  # 只保存前50个请求避免过大
            }
            
        except Exception as e:
            self.logger.error(f"❌ 捕获网络请求失败: {e}")
            return {'total_requests': 0, 'api_requests': [], 'all_requests': []}
    
    def find_story_navigation(self, driver):
        """查找故事导航或列表"""
        try:
            # 查找可能的导航元素
            navigation_elements = driver.execute_script("""
                var selectors = [
                    'nav', '.nav', '.navigation', '.menu', '.sidebar',
                    '.story-list', '.story-nav', '.category', '.categories',
                    'a[href*="story"]', 'button[onclick*="story"]',
                    '[class*="story"]', '[id*="story"]',
                    'ul li', '.list-item', '.nav-item'
                ];
                
                var result = [];
                for (var i = 0; i < selectors.length; i++) {
                    var elements = document.querySelectorAll(selectors[i]);
                    for (var j = 0; j < elements.length && j < 10; j++) {  // 限制每个选择器最多10个元素
                        var elem = elements[j];
                        var text = elem.innerText || elem.textContent || '';
                        if (text.length > 0 && text.length < 500) {
                            result.push({
                                selector: selectors[i],
                                tag: elem.tagName,
                                text: text.trim(),
                                href: elem.href || null,
                                onclick: elem.onclick ? elem.onclick.toString() : null,
                                className: elem.className || null,
                                id: elem.id || null
                            });
                        }
                    }
                }
                return result;
            """)
            
            self.logger.info(f"🧭 发现 {len(navigation_elements)} 个可能的导航元素")
            
            # 查找包含数字的链接或按钮（可能是故事ID）
            story_links = []
            for elem in navigation_elements:
                if elem['text'] and re.search(r'\d+', elem['text']):
                    story_links.append(elem)
            
            self.logger.info(f"📚 发现 {len(story_links)} 个可能的故事链接")
            
            return {
                'navigation_elements': navigation_elements[:20],  # 限制数量
                'story_links': story_links
            }
            
        except Exception as e:
            self.logger.error(f"❌ 查找故事导航失败: {e}")
            return {'navigation_elements': [], 'story_links': []}
    
    def test_story_loading_mechanism(self):
        """测试故事加载机制"""
        driver = None
        try:
            driver = self.create_driver_with_logging()
            if not driver:
                return None
            
            self.logger.info("🔬 开始测试故事加载机制...")
            
            # 访问主页
            driver.get(self.base_url)
            time.sleep(5)
            
            # 尝试不同的方式触发故事加载
            test_results = []
            
            # 1. 尝试URL hash变化
            test_cases = [
                "#story/1", "#story/2", "#story/3",
                "#/story/1", "#/story/2", "#/story/3",
                "#!/story/1", "#!/story/2", "#!/story/3"
            ]
            
            for hash_url in test_cases:
                try:
                    self.logger.info(f"🔍 测试URL hash: {hash_url}")
                    
                    # 修改URL hash
                    driver.execute_script(f"window.location.hash = '{hash_url}';")
                    time.sleep(3)
                    
                    # 检查页面变化
                    current_url = driver.current_url
                    page_text = driver.execute_script("return document.body.innerText;")
                    
                    test_results.append({
                        'test_type': 'url_hash',
                        'input': hash_url,
                        'current_url': current_url,
                        'page_text_length': len(page_text),
                        'page_text_preview': page_text[:300] if page_text else '',
                        'success': len(page_text) > 1000 and '故事' in page_text
                    })
                    
                    if test_results[-1]['success']:
                        self.logger.info(f"✅ URL hash {hash_url} 成功加载内容")
                        # 保存成功的页面
                        with open(f'spa_story_success_{hash_url.replace("/", "_").replace("#", "")}.html', 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                    else:
                        self.logger.info(f"❌ URL hash {hash_url} 未加载到有效内容")
                        
                except Exception as e:
                    self.logger.error(f"❌ 测试URL hash {hash_url} 失败: {e}")
            
            # 2. 尝试查找并点击可能的故事链接
            try:
                self.logger.info("🖱️ 尝试查找并点击故事链接...")
                
                # 查找可能的故事链接
                story_elements = driver.execute_script("""
                    var elements = document.querySelectorAll('a, button, div, span');
                    var storyElements = [];
                    
                    for (var i = 0; i < elements.length; i++) {
                        var elem = elements[i];
                        var text = elem.innerText || elem.textContent || '';
                        var onclick = elem.onclick ? elem.onclick.toString() : '';
                        
                        if ((text.includes('故事') || text.includes('Story') || /\\d+/.test(text)) ||
                            (onclick.includes('story') || onclick.includes('Story'))) {
                            storyElements.push({
                                tag: elem.tagName,
                                text: text.trim(),
                                onclick: onclick,
                                href: elem.href || null,
                                className: elem.className || null,
                                id: elem.id || null
                            });
                        }
                    }
                    
                    return storyElements.slice(0, 10);  // 只返回前10个
                """)
                
                self.logger.info(f"🔍 发现 {len(story_elements)} 个可能的故事元素")
                
                for i, elem in enumerate(story_elements):
                    self.logger.info(f"  元素 {i+1}: {elem['tag']} - {elem['text'][:50]}")
                
            except Exception as e:
                self.logger.error(f"❌ 查找故事链接失败: {e}")
            
            return {
                'test_results': test_results,
                'successful_hashes': [r for r in test_results if r['success']],
                'story_elements': story_elements if 'story_elements' in locals() else []
            }
            
        except Exception as e:
            self.logger.error(f"❌ 测试故事加载机制失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def analyze_javascript_execution(self):
        """分析JavaScript执行和路由机制"""
        driver = None
        try:
            driver = self.create_driver_with_logging()
            if not driver:
                return None
            
            self.logger.info("🔬 开始分析JavaScript执行和路由...")
            
            # 访问主页
            driver.get(self.base_url)
            time.sleep(5)
            
            # 分析全局JavaScript对象和函数
            js_analysis = driver.execute_script("""
                var analysis = {
                    global_objects: [],
                    router_info: {},
                    vue_info: {},
                    react_info: {},
                    custom_functions: []
                };
                
                // 检查全局对象
                var globalKeys = Object.keys(window);
                for (var i = 0; i < globalKeys.length; i++) {
                    var key = globalKeys[i];
                    if (key.includes('story') || key.includes('Story') || 
                        key.includes('router') || key.includes('Router') ||
                        key.includes('app') || key.includes('App')) {
                        analysis.global_objects.push({
                            name: key,
                            type: typeof window[key],
                            value_preview: window[key] ? window[key].toString().substring(0, 100) : null
                        });
                    }
                }
                
                // 检查Vue
                if (window.Vue || window.__VUE__) {
                    analysis.vue_info = {
                        exists: true,
                        version: window.Vue ? window.Vue.version : 'unknown',
                        devtools: !!window.__VUE_DEVTOOLS_GLOBAL_HOOK__
                    };
                }
                
                // 检查React
                if (window.React || window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
                    analysis.react_info = {
                        exists: true,
                        devtools: !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__
                    };
                }
                
                // 检查路由
                if (window.location.hash) {
                    analysis.router_info.current_hash = window.location.hash;
                }
                
                // 检查history API
                analysis.router_info.history_length = window.history.length;
                analysis.router_info.supports_pushstate = !!(window.history && window.history.pushState);
                
                return analysis;
            """)
            
            self.logger.info("📊 JavaScript分析结果:")
            self.logger.info(f"  全局对象: {len(js_analysis['global_objects'])} 个")
            self.logger.info(f"  Vue: {js_analysis['vue_info']}")
            self.logger.info(f"  React: {js_analysis['react_info']}")
            self.logger.info(f"  路由信息: {js_analysis['router_info']}")
            
            return js_analysis
            
        except Exception as e:
            self.logger.error(f"❌ 分析JavaScript执行失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def generate_analysis_report(self):
        """生成完整的分析报告"""
        self.logger.info("🚀 开始完整的SPA网站分析...")
        
        # 1. 分析主页结构
        homepage_analysis = self.analyze_homepage_structure()
        
        # 2. 测试故事加载机制
        loading_mechanism = self.test_story_loading_mechanism()
        
        # 3. 分析JavaScript执行
        js_analysis = self.analyze_javascript_execution()
        
        # 生成完整报告
        report = {
            'analysis_time': datetime.now().isoformat(),
            'website_url': self.base_url,
            'homepage_analysis': homepage_analysis,
            'loading_mechanism': loading_mechanism,
            'javascript_analysis': js_analysis,
            'recommendations': self.generate_recommendations(homepage_analysis, loading_mechanism, js_analysis)
        }
        
        # 保存报告
        with open('spa_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info("📋 分析报告已保存到: spa_analysis_report.json")
        
        # 打印关键发现
        self.print_key_findings(report)
        
        return report
    
    def generate_recommendations(self, homepage, loading, js_analysis):
        """生成爬取建议"""
        recommendations = []
        
        if loading and loading.get('successful_hashes'):
            recommendations.append({
                'type': 'url_hash_routing',
                'description': '发现URL hash路由机制有效',
                'successful_patterns': [h['input'] for h in loading['successful_hashes']],
                'implementation': '使用Selenium修改window.location.hash来加载不同故事'
            })
        
        if js_analysis and js_analysis.get('vue_info', {}).get('exists'):
            recommendations.append({
                'type': 'vue_spa',
                'description': '检测到Vue.js单页应用',
                'implementation': '等待Vue组件渲染完成，监听路由变化'
            })
        
        if js_analysis and js_analysis.get('react_info', {}).get('exists'):
            recommendations.append({
                'type': 'react_spa',
                'description': '检测到React单页应用',
                'implementation': '等待React组件渲染完成，监听状态变化'
            })
        
        if homepage and homepage.get('network_requests', {}).get('api_requests'):
            recommendations.append({
                'type': 'api_requests',
                'description': '发现API请求',
                'api_urls': [req['url'] for req in homepage['network_requests']['api_requests']],
                'implementation': '直接调用API接口获取数据'
            })
        
        return recommendations
    
    def print_key_findings(self, report):
        """打印关键发现"""
        self.logger.info("\n" + "="*50)
        self.logger.info("🎯 关键发现总结")
        self.logger.info("="*50)
        
        if report.get('recommendations'):
            for rec in report['recommendations']:
                self.logger.info(f"✅ {rec['type']}: {rec['description']}")
                if 'successful_patterns' in rec:
                    self.logger.info(f"   成功模式: {rec['successful_patterns']}")
                if 'api_urls' in rec:
                    self.logger.info(f"   API接口: {rec['api_urls']}")
        
        self.logger.info("="*50)

def main():
    analyzer = SPAAnalyzer()
    
    try:
        # 生成完整分析报告
        report = analyzer.generate_analysis_report()
        
        print("\n🎉 SPA网站分析完成！")
        print("📋 详细报告已保存到: spa_analysis_report.json")
        print("📜 日志文件: spa_analyzer.log")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断分析")
    except Exception as e:
        print(f"\n❌ 分析过程中发生错误: {e}")

if __name__ == "__main__":
    main()