#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的SPA网站分析器
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
from bs4 import BeautifulSoup

class SimpleSPAAnalyzer:
    def __init__(self):
        self.base_url = "https://storynook.cn"
        self.chromedriver_path = os.path.join(os.path.dirname(__file__), 'chromedriver_exe', 'chromedriver.exe')
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('simple_spa_analyzer.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 验证ChromeDriver
        if not os.path.exists(self.chromedriver_path):
            raise FileNotFoundError(f"ChromeDriver未找到: {self.chromedriver_path}")
        
    def create_driver(self):
        """创建简单的Chrome WebDriver"""
        chrome_options = Options()
        
        # 基本选项
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
            service = Service(self.chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 反检测
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ WebDriver创建成功")
            return driver
        except Exception as e:
            self.logger.error(f"❌ 创建WebDriver失败: {e}")
            return None
    
    def analyze_homepage(self):
        """分析主页结构"""
        driver = None
        try:
            driver = self.create_driver()
            if not driver:
                return None
            
            self.logger.info("🔍 开始分析主页...")
            
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
            with open('simple_homepage_original.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            
            # 等待JavaScript执行
            self.logger.info("⏳ 等待JavaScript执行...")
            time.sleep(10)
            
            # 再次获取页面源码
            updated_source = driver.page_source
            with open('simple_homepage_after_js.html', 'w', encoding='utf-8') as f:
                f.write(updated_source)
            
            # 检查页面变化
            source_changed = len(updated_source) != page_info['page_source_length']
            self.logger.info(f"📄 JavaScript执行后页面长度: {len(updated_source)}")
            self.logger.info(f"🔄 页面内容是否变化: {source_changed}")
            
            # 分析JavaScript文件
            js_files = self.extract_javascript_files(driver)
            
            # 查找可能的导航元素
            navigation = self.find_navigation_elements(driver)
            
            # 分析页面结构
            page_structure = self.analyze_page_structure(driver)
            
            return {
                'page_info': page_info,
                'source_changed': source_changed,
                'updated_length': len(updated_source),
                'javascript_files': js_files,
                'navigation': navigation,
                'page_structure': page_structure
            }
            
        except Exception as e:
            self.logger.error(f"❌ 分析主页失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def extract_javascript_files(self, driver):
        """提取JavaScript文件"""
        try:
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
            
            external_js = [s for s in scripts if s['src']]
            inline_js = [s for s in scripts if not s['src']]
            
            self.logger.info(f"  外部JS文件: {len(external_js)} 个")
            self.logger.info(f"  内联JS脚本: {len(inline_js)} 个")
            
            for js in external_js:
                self.logger.info(f"    外部: {js['src']}")
            
            return {
                'total': len(scripts),
                'external': external_js,
                'inline': inline_js
            }
            
        except Exception as e:
            self.logger.error(f"❌ 提取JavaScript文件失败: {e}")
            return {'total': 0, 'external': [], 'inline': []}
    
    def find_navigation_elements(self, driver):
        """查找导航元素"""
        try:
            # 查找可能的导航和故事相关元素
            elements = driver.execute_script("""
                var selectors = [
                    'nav', '.nav', '.navigation', '.menu', '.sidebar',
                    '.story-list', '.story-nav', '.category', '.categories',
                    'a[href*="story"]', 'button[onclick*="story"]',
                    '[class*="story"]', '[id*="story"]',
                    'ul li a', '.list-item', '.nav-item'
                ];
                
                var result = [];
                for (var i = 0; i < selectors.length; i++) {
                    var elements = document.querySelectorAll(selectors[i]);
                    for (var j = 0; j < elements.length && j < 5; j++) {
                        var elem = elements[j];
                        var text = (elem.innerText || elem.textContent || '').trim();
                        if (text.length > 0 && text.length < 200) {
                            result.push({
                                selector: selectors[i],
                                tag: elem.tagName,
                                text: text,
                                href: elem.href || null,
                                className: elem.className || null,
                                id: elem.id || null
                            });
                        }
                    }
                }
                return result;
            """)
            
            self.logger.info(f"🧭 发现 {len(elements)} 个导航相关元素")
            
            # 查找包含数字的元素（可能是故事ID）
            story_elements = []
            for elem in elements:
                if elem['text'] and re.search(r'\d+', elem['text']):
                    story_elements.append(elem)
                    self.logger.info(f"  可能的故事元素: {elem['text'][:50]}")
            
            return {
                'all_elements': elements,
                'story_elements': story_elements
            }
            
        except Exception as e:
            self.logger.error(f"❌ 查找导航元素失败: {e}")
            return {'all_elements': [], 'story_elements': []}
    
    def analyze_page_structure(self, driver):
        """分析页面结构"""
        try:
            structure = driver.execute_script("""
                var analysis = {
                    frameworks: {},
                    containers: [],
                    global_vars: []
                };
                
                // 检查前端框架
                if (window.Vue) {
                    analysis.frameworks.vue = {
                        exists: true,
                        version: window.Vue.version || 'unknown'
                    };
                }
                
                if (window.React) {
                    analysis.frameworks.react = {
                        exists: true
                    };
                }
                
                if (window.angular) {
                    analysis.frameworks.angular = {
                        exists: true
                    };
                }
                
                // 检查jQuery
                if (window.jQuery || window.$) {
                    analysis.frameworks.jquery = {
                        exists: true,
                        version: window.jQuery ? window.jQuery.fn.jquery : 'unknown'
                    };
                }
                
                // 查找主要容器
                var containerSelectors = ['#app', '#root', '#main', '.app', '.main', '.container'];
                for (var i = 0; i < containerSelectors.length; i++) {
                    var elem = document.querySelector(containerSelectors[i]);
                    if (elem) {
                        analysis.containers.push({
                            selector: containerSelectors[i],
                            tag: elem.tagName,
                            id: elem.id || null,
                            className: elem.className || null,
                            children_count: elem.children.length,
                            innerHTML_length: elem.innerHTML.length
                        });
                    }
                }
                
                // 检查全局变量
                var globalKeys = Object.keys(window);
                for (var j = 0; j < globalKeys.length; j++) {
                    var key = globalKeys[j];
                    if (key.toLowerCase().includes('story') || 
                        key.toLowerCase().includes('router') || 
                        key.toLowerCase().includes('app')) {
                        analysis.global_vars.push({
                            name: key,
                            type: typeof window[key]
                        });
                    }
                }
                
                return analysis;
            """)
            
            self.logger.info("🏗️ 页面结构分析:")
            self.logger.info(f"  前端框架: {structure['frameworks']}")
            self.logger.info(f"  主要容器: {len(structure['containers'])} 个")
            self.logger.info(f"  相关全局变量: {len(structure['global_vars'])} 个")
            
            for var in structure['global_vars']:
                self.logger.info(f"    {var['name']}: {var['type']}")
            
            return structure
            
        except Exception as e:
            self.logger.error(f"❌ 分析页面结构失败: {e}")
            return {'frameworks': {}, 'containers': [], 'global_vars': []}
    
    def test_url_routing(self):
        """测试URL路由机制"""
        driver = None
        try:
            driver = self.create_driver()
            if not driver:
                return None
            
            self.logger.info("🔬 开始测试URL路由机制...")
            
            # 访问主页
            driver.get(self.base_url)
            time.sleep(5)
            
            # 测试不同的URL模式
            test_patterns = [
                "#story/1", "#story/2", "#story/3",
                "#/story/1", "#/story/2", "#/story/3",
                "#!/story/1", "#!/story/2", "#!/story/3",
                "#story-1", "#story-2", "#story-3"
            ]
            
            results = []
            
            for pattern in test_patterns:
                try:
                    self.logger.info(f"🔍 测试路由模式: {pattern}")
                    
                    # 修改URL hash
                    driver.execute_script(f"window.location.hash = '{pattern}';")
                    time.sleep(5)  # 等待路由变化
                    
                    # 检查页面变化
                    current_url = driver.current_url
                    page_text = driver.execute_script("return document.body.innerText;")
                    page_html = driver.page_source
                    
                    # 检查是否有新内容加载
                    has_story_content = any(keyword in page_text.lower() for keyword in 
                                          ['故事', 'story', '内容', 'content', '章节', 'chapter'])
                    
                    content_length = len(page_text)
                    
                    result = {
                        'pattern': pattern,
                        'current_url': current_url,
                        'content_length': content_length,
                        'has_story_content': has_story_content,
                        'content_preview': page_text[:300] if page_text else '',
                        'success': content_length > 1000 and has_story_content
                    }
                    
                    results.append(result)
                    
                    if result['success']:
                        self.logger.info(f"✅ 路由模式 {pattern} 成功加载内容 ({content_length} 字符)")
                        # 保存成功的页面
                        filename = f'simple_success_{pattern.replace("/", "_").replace("#", "hash_")}.html'
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(page_html)
                        self.logger.info(f"📄 已保存成功页面: {filename}")
                    else:
                        self.logger.info(f"❌ 路由模式 {pattern} 未加载有效内容 ({content_length} 字符)")
                    
                    # 重置到主页
                    driver.execute_script("window.location.hash = '';")
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"❌ 测试路由模式 {pattern} 失败: {e}")
                    results.append({
                        'pattern': pattern,
                        'error': str(e),
                        'success': False
                    })
            
            successful_patterns = [r for r in results if r.get('success', False)]
            
            self.logger.info(f"🎯 测试完成，成功的路由模式: {len(successful_patterns)} 个")
            for pattern in successful_patterns:
                self.logger.info(f"  ✅ {pattern['pattern']} - {pattern['content_length']} 字符")
            
            return {
                'test_results': results,
                'successful_patterns': successful_patterns,
                'total_tested': len(test_patterns),
                'success_count': len(successful_patterns)
            }
            
        except Exception as e:
            self.logger.error(f"❌ 测试URL路由失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def generate_complete_analysis(self):
        """生成完整分析报告"""
        self.logger.info("🚀 开始完整的SPA网站分析...")
        
        # 1. 分析主页
        homepage_analysis = self.analyze_homepage()
        
        # 2. 测试URL路由
        routing_analysis = self.test_url_routing()
        
        # 生成报告
        report = {
            'analysis_time': datetime.now().isoformat(),
            'website_url': self.base_url,
            'homepage_analysis': homepage_analysis,
            'routing_analysis': routing_analysis,
            'recommendations': self.generate_recommendations(homepage_analysis, routing_analysis)
        }
        
        # 保存报告
        with open('simple_spa_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info("📋 分析报告已保存到: simple_spa_analysis_report.json")
        
        # 打印关键发现
        self.print_summary(report)
        
        return report
    
    def generate_recommendations(self, homepage, routing):
        """生成爬取建议"""
        recommendations = []
        
        if routing and routing.get('successful_patterns'):
            recommendations.append({
                'type': 'url_hash_routing',
                'description': '发现有效的URL hash路由机制',
                'successful_patterns': [p['pattern'] for p in routing['successful_patterns']],
                'implementation': '使用Selenium修改window.location.hash来加载不同故事'
            })
        
        if homepage and homepage.get('page_structure', {}).get('frameworks'):
            frameworks = homepage['page_structure']['frameworks']
            if frameworks.get('vue', {}).get('exists'):
                recommendations.append({
                    'type': 'vue_spa',
                    'description': f"检测到Vue.js应用 (版本: {frameworks['vue'].get('version', 'unknown')})",
                    'implementation': '等待Vue组件渲染完成后提取内容'
                })
            
            if frameworks.get('react', {}).get('exists'):
                recommendations.append({
                    'type': 'react_spa',
                    'description': '检测到React应用',
                    'implementation': '等待React组件渲染完成后提取内容'
                })
            
            if frameworks.get('jquery', {}).get('exists'):
                recommendations.append({
                    'type': 'jquery_app',
                    'description': f"检测到jQuery应用 (版本: {frameworks['jquery'].get('version', 'unknown')})",
                    'implementation': '等待jQuery操作完成后提取内容'
                })
        
        if not recommendations:
            recommendations.append({
                'type': 'manual_investigation',
                'description': '需要进一步手动调查',
                'implementation': '检查浏览器开发者工具的网络请求和JavaScript控制台'
            })
        
        return recommendations
    
    def print_summary(self, report):
        """打印分析总结"""
        self.logger.info("\n" + "="*60)
        self.logger.info("🎯 SPA网站分析总结")
        self.logger.info("="*60)
        
        if report.get('homepage_analysis'):
            homepage = report['homepage_analysis']
            self.logger.info(f"📖 网站标题: {homepage.get('page_info', {}).get('title', 'N/A')}")
            self.logger.info(f"🔄 JavaScript动态加载: {'是' if homepage.get('source_changed', False) else '否'}")
            
            js_info = homepage.get('javascript_files', {})
            self.logger.info(f"📜 JavaScript文件: {js_info.get('total', 0)} 个 (外部: {len(js_info.get('external', []))}, 内联: {len(js_info.get('inline', []))})")
            
            frameworks = homepage.get('page_structure', {}).get('frameworks', {})
            detected_frameworks = [name for name, info in frameworks.items() if info.get('exists')]
            self.logger.info(f"🛠️ 检测到的框架: {', '.join(detected_frameworks) if detected_frameworks else '无'}")
        
        if report.get('routing_analysis'):
            routing = report['routing_analysis']
            success_count = routing.get('success_count', 0)
            total_tested = routing.get('total_tested', 0)
            self.logger.info(f"🔍 路由测试: {success_count}/{total_tested} 个模式成功")
            
            if routing.get('successful_patterns'):
                self.logger.info("✅ 成功的路由模式:")
                for pattern in routing['successful_patterns']:
                    self.logger.info(f"   {pattern['pattern']} - {pattern['content_length']} 字符")
        
        if report.get('recommendations'):
            self.logger.info("💡 爬取建议:")
            for i, rec in enumerate(report['recommendations'], 1):
                self.logger.info(f"   {i}. {rec['type']}: {rec['description']}")
        
        self.logger.info("="*60)

def main():
    analyzer = SimpleSPAAnalyzer()
    
    try:
        # 生成完整分析报告
        report = analyzer.generate_complete_analysis()
        
        print("\n🎉 SPA网站分析完成！")
        print("📋 详细报告已保存到: simple_spa_analysis_report.json")
        print("📜 日志文件: simple_spa_analyzer.log")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断分析")
    except Exception as e:
        print(f"\n❌ 分析过程中发生错误: {e}")

if __name__ == "__main__":
    main()