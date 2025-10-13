#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度JavaScript分析器
专门分析网站的JavaScript代码和AJAX请求
"""

import time
import json
import logging
import os
import re
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

class DeepJSAnalyzer:
    def __init__(self):
        self.base_url = "https://storynook.cn"
        self.chromedriver_path = os.path.join(os.path.dirname(__file__), 'chromedriver_exe', 'chromedriver.exe')
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('deep_js_analyzer.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 验证ChromeDriver
        if not os.path.exists(self.chromedriver_path):
            raise FileNotFoundError(f"ChromeDriver未找到: {self.chromedriver_path}")
    
    def create_driver(self):
        """创建Chrome WebDriver"""
        chrome_options = Options()
        
        # 基本选项
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 启用网络日志
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
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
    
    def download_and_analyze_js(self):
        """下载并分析JavaScript文件"""
        js_files = [
            "https://storynook.cn/js/supabase-client.js",
            "https://storynook.cn/js/app.js"
        ]
        
        analysis_results = {}
        
        for js_url in js_files:
            try:
                self.logger.info(f"📥 下载JavaScript文件: {js_url}")
                
                response = requests.get(js_url, timeout=10)
                response.raise_for_status()
                
                js_content = response.text
                filename = os.path.basename(js_url)
                
                # 保存JS文件
                with open(f"downloaded_{filename}", 'w', encoding='utf-8') as f:
                    f.write(js_content)
                
                # 分析JS内容
                analysis = self.analyze_js_content(js_content, filename)
                analysis_results[filename] = analysis
                
                self.logger.info(f"✅ 分析完成: {filename}")
                
            except Exception as e:
                self.logger.error(f"❌ 下载/分析 {js_url} 失败: {e}")
                analysis_results[os.path.basename(js_url)] = {'error': str(e)}
        
        return analysis_results
    
    def analyze_js_content(self, js_content, filename):
        """分析JavaScript内容"""
        analysis = {
            'file_size': len(js_content),
            'functions': [],
            'ajax_calls': [],
            'api_endpoints': [],
            'story_related': [],
            'routing_logic': [],
            'database_operations': []
        }
        
        # 查找函数定义
        function_patterns = [
            r'function\s+(\w+)\s*\(',
            r'(\w+)\s*:\s*function\s*\(',
            r'const\s+(\w+)\s*=\s*\(',
            r'let\s+(\w+)\s*=\s*\(',
            r'var\s+(\w+)\s*=\s*function'
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            analysis['functions'].extend(matches)
        
        # 查找AJAX调用
        ajax_patterns = [
            r'\.ajax\s*\(',
            r'fetch\s*\(',
            r'XMLHttpRequest',
            r'\.get\s*\(',
            r'\.post\s*\(',
            r'\.put\s*\(',
            r'\.delete\s*\('
        ]
        
        for pattern in ajax_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            if matches:
                analysis['ajax_calls'].extend(matches)
        
        # 查找API端点
        api_patterns = [
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*\/[^"\']*\.php[^"\']*)["\']',
            r'["\']([^"\']*\/[^"\']*\.json[^"\']*)["\']',
            r'["\']([^"\']*supabase[^"\']*)["\']'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            analysis['api_endpoints'].extend(matches)
        
        # 查找故事相关的代码
        story_patterns = [
            r'story[^a-zA-Z].*',
            r'loadStory.*',
            r'getStory.*',
            r'showStory.*',
            r'storyId.*',
            r'story_id.*'
        ]
        
        for pattern in story_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            analysis['story_related'].extend(matches[:10])  # 限制数量
        
        # 查找路由逻辑
        routing_patterns = [
            r'location\.hash.*',
            r'window\.location.*',
            r'hashchange.*',
            r'router.*',
            r'route.*'
        ]
        
        for pattern in routing_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            analysis['routing_logic'].extend(matches[:10])
        
        # 查找数据库操作
        db_patterns = [
            r'supabase.*',
            r'\.from\s*\(',
            r'\.select\s*\(',
            r'\.insert\s*\(',
            r'\.update\s*\(',
            r'\.eq\s*\('
        ]
        
        for pattern in db_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            analysis['database_operations'].extend(matches[:10])
        
        # 去重
        for key in analysis:
            if isinstance(analysis[key], list):
                analysis[key] = list(set(analysis[key]))
        
        return analysis
    
    def monitor_network_requests(self):
        """监控网络请求"""
        driver = None
        try:
            driver = self.create_driver()
            if not driver:
                return None
            
            self.logger.info("🔍 开始监控网络请求...")
            
            # 访问主页
            driver.get(self.base_url)
            time.sleep(3)
            
            # 获取初始网络日志
            initial_logs = driver.get_log('performance')
            
            # 测试不同的故事ID
            story_ids = [1, 2, 3, 5, 10, 100]
            network_analysis = {}
            
            for story_id in story_ids:
                self.logger.info(f"🔍 测试故事ID: {story_id}")
                
                # 清除之前的日志
                driver.get_log('performance')
                
                # 修改hash
                driver.execute_script(f"window.location.hash = '#story/{story_id}';")
                time.sleep(5)
                
                # 获取网络日志
                logs = driver.get_log('performance')
                
                # 分析网络请求
                requests_made = []
                for log in logs:
                    message = json.loads(log['message'])
                    if message['message']['method'] == 'Network.requestWillBeSent':
                        request_url = message['message']['params']['request']['url']
                        if 'storynook.cn' in request_url or 'supabase' in request_url:
                            requests_made.append({
                                'url': request_url,
                                'method': message['message']['params']['request']['method'],
                                'timestamp': log['timestamp']
                            })
                
                # 检查页面内容变化
                page_text = driver.execute_script("return document.body.innerText;")
                
                network_analysis[f"story_{story_id}"] = {
                    'requests': requests_made,
                    'page_text_length': len(page_text),
                    'current_url': driver.current_url,
                    'page_title': driver.title
                }
                
                self.logger.info(f"  发现 {len(requests_made)} 个相关网络请求")
                for req in requests_made:
                    self.logger.info(f"    {req['method']} {req['url']}")
            
            return network_analysis
            
        except Exception as e:
            self.logger.error(f"❌ 监控网络请求失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def test_direct_api_calls(self):
        """直接测试API调用"""
        self.logger.info("🔬 开始直接API测试...")
        
        # 可能的API端点
        api_endpoints = [
            f"{self.base_url}/api/story/1",
            f"{self.base_url}/api/story/2",
            f"{self.base_url}/api/stories",
            f"{self.base_url}/story/1.json",
            f"{self.base_url}/story/2.json",
            f"{self.base_url}/data/story/1",
            f"{self.base_url}/data/story/2"
        ]
        
        api_results = {}
        
        for endpoint in api_endpoints:
            try:
                self.logger.info(f"🔍 测试API端点: {endpoint}")
                
                response = requests.get(endpoint, timeout=10)
                
                api_results[endpoint] = {
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'content_length': len(response.content),
                    'success': response.status_code == 200
                }
                
                if response.status_code == 200:
                    self.logger.info(f"✅ API端点有效: {endpoint}")
                    # 保存响应内容
                    filename = endpoint.replace('/', '_').replace(':', '').replace('.', '_') + '.txt'
                    with open(f"api_response_{filename}", 'w', encoding='utf-8') as f:
                        f.write(response.text)
                else:
                    self.logger.info(f"❌ API端点无效: {endpoint} (状态码: {response.status_code})")
                
            except Exception as e:
                self.logger.error(f"❌ 测试API端点 {endpoint} 失败: {e}")
                api_results[endpoint] = {'error': str(e), 'success': False}
        
        return api_results
    
    def analyze_supabase_integration(self):
        """分析Supabase集成"""
        driver = None
        try:
            driver = self.create_driver()
            if not driver:
                return None
            
            self.logger.info("🔍 分析Supabase集成...")
            
            # 访问主页
            driver.get(self.base_url)
            time.sleep(5)
            
            # 检查Supabase配置
            supabase_info = driver.execute_script("""
                var info = {
                    supabase_exists: typeof window.supabase !== 'undefined',
                    supabase_client_exists: typeof window.supabaseClient !== 'undefined',
                    global_vars: []
                };
                
                // 检查全局变量
                for (var key in window) {
                    if (key.toLowerCase().includes('supabase') || 
                        key.toLowerCase().includes('client') ||
                        key.toLowerCase().includes('database') ||
                        key.toLowerCase().includes('db')) {
                        info.global_vars.push({
                            name: key,
                            type: typeof window[key],
                            value_preview: typeof window[key] === 'object' ? 
                                Object.keys(window[key] || {}).slice(0, 5) : 
                                String(window[key]).substring(0, 100)
                        });
                    }
                }
                
                return info;
            """)
            
            self.logger.info(f"Supabase存在: {supabase_info.get('supabase_exists', False)}")
            self.logger.info(f"Supabase客户端存在: {supabase_info.get('supabase_client_exists', False)}")
            
            # 尝试调用故事加载函数
            story_load_test = driver.execute_script("""
                var result = {
                    loadStoryDetail_exists: typeof loadStoryDetail === 'function',
                    test_results: []
                };
                
                if (typeof loadStoryDetail === 'function') {
                    try {
                        // 尝试调用loadStoryDetail函数
                        var testResult = loadStoryDetail(1);
                        result.test_results.push({
                            story_id: 1,
                            result: testResult,
                            success: true
                        });
                    } catch (e) {
                        result.test_results.push({
                            story_id: 1,
                            error: e.toString(),
                            success: false
                        });
                    }
                }
                
                return result;
            """)
            
            return {
                'supabase_info': supabase_info,
                'story_load_test': story_load_test
            }
            
        except Exception as e:
            self.logger.error(f"❌ 分析Supabase集成失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def generate_complete_analysis(self):
        """生成完整的深度分析报告"""
        self.logger.info("🚀 开始深度JavaScript分析...")
        
        # 1. 下载并分析JS文件
        js_analysis = self.download_and_analyze_js()
        
        # 2. 监控网络请求
        network_analysis = self.monitor_network_requests()
        
        # 3. 测试直接API调用
        api_analysis = self.test_direct_api_calls()
        
        # 4. 分析Supabase集成
        supabase_analysis = self.analyze_supabase_integration()
        
        # 生成报告
        report = {
            'analysis_time': datetime.now().isoformat(),
            'website_url': self.base_url,
            'javascript_analysis': js_analysis,
            'network_analysis': network_analysis,
            'api_analysis': api_analysis,
            'supabase_analysis': supabase_analysis,
            'recommendations': self.generate_crawling_strategy(js_analysis, network_analysis, api_analysis, supabase_analysis)
        }
        
        # 保存报告
        with open('deep_js_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info("📋 深度分析报告已保存到: deep_js_analysis_report.json")
        
        # 打印关键发现
        self.print_analysis_summary(report)
        
        return report
    
    def generate_crawling_strategy(self, js_analysis, network_analysis, api_analysis, supabase_analysis):
        """生成爬取策略"""
        strategies = []
        
        # 基于JavaScript分析的策略
        if js_analysis:
            for filename, analysis in js_analysis.items():
                if 'error' not in analysis:
                    if analysis.get('story_related'):
                        strategies.append({
                            'type': 'javascript_function_call',
                            'description': f'在{filename}中发现故事相关函数',
                            'functions': analysis['story_related'][:5],
                            'implementation': '使用Selenium执行JavaScript函数来加载故事'
                        })
                    
                    if analysis.get('database_operations'):
                        strategies.append({
                            'type': 'supabase_database',
                            'description': f'在{filename}中发现数据库操作',
                            'operations': analysis['database_operations'][:5],
                            'implementation': '模拟Supabase数据库查询'
                        })
        
        # 基于网络分析的策略
        if network_analysis:
            unique_requests = set()
            for story_key, data in network_analysis.items():
                for req in data.get('requests', []):
                    unique_requests.add(req['url'])
            
            if unique_requests:
                strategies.append({
                    'type': 'network_request_monitoring',
                    'description': '发现动态网络请求',
                    'unique_requests': list(unique_requests),
                    'implementation': '监控并复制网络请求模式'
                })
        
        # 基于API分析的策略
        if api_analysis:
            working_apis = [endpoint for endpoint, data in api_analysis.items() 
                          if data.get('success', False)]
            if working_apis:
                strategies.append({
                    'type': 'direct_api_access',
                    'description': '发现可用的API端点',
                    'endpoints': working_apis,
                    'implementation': '直接调用API端点获取数据'
                })
        
        # 基于Supabase分析的策略
        if supabase_analysis:
            if supabase_analysis.get('supabase_info', {}).get('supabase_exists'):
                strategies.append({
                    'type': 'supabase_client_simulation',
                    'description': '检测到Supabase客户端',
                    'implementation': '模拟Supabase客户端调用'
                })
        
        return strategies
    
    def print_analysis_summary(self, report):
        """打印分析总结"""
        self.logger.info("\n" + "="*60)
        self.logger.info("🔬 深度JavaScript分析总结")
        self.logger.info("="*60)
        
        # JavaScript文件分析
        if report.get('javascript_analysis'):
            self.logger.info("📜 JavaScript文件分析:")
            for filename, analysis in report['javascript_analysis'].items():
                if 'error' not in analysis:
                    self.logger.info(f"  {filename}:")
                    self.logger.info(f"    函数数量: {len(analysis.get('functions', []))}")
                    self.logger.info(f"    AJAX调用: {len(analysis.get('ajax_calls', []))}")
                    self.logger.info(f"    故事相关代码: {len(analysis.get('story_related', []))}")
                    self.logger.info(f"    数据库操作: {len(analysis.get('database_operations', []))}")
        
        # 网络请求分析
        if report.get('network_analysis'):
            total_requests = sum(len(data.get('requests', [])) 
                               for data in report['network_analysis'].values())
            self.logger.info(f"🌐 网络请求监控: 总共发现 {total_requests} 个请求")
        
        # API测试结果
        if report.get('api_analysis'):
            working_apis = sum(1 for data in report['api_analysis'].values() 
                             if data.get('success', False))
            total_apis = len(report['api_analysis'])
            self.logger.info(f"🔌 API测试: {working_apis}/{total_apis} 个端点可用")
        
        # Supabase分析
        if report.get('supabase_analysis'):
            supabase_exists = report['supabase_analysis'].get('supabase_info', {}).get('supabase_exists', False)
            self.logger.info(f"🗄️ Supabase集成: {'检测到' if supabase_exists else '未检测到'}")
        
        # 爬取策略
        if report.get('recommendations'):
            self.logger.info("💡 推荐的爬取策略:")
            for i, strategy in enumerate(report['recommendations'], 1):
                self.logger.info(f"  {i}. {strategy['type']}: {strategy['description']}")
        
        self.logger.info("="*60)

def main():
    analyzer = DeepJSAnalyzer()
    
    try:
        # 生成完整分析报告
        report = analyzer.generate_complete_analysis()
        
        print("\n🎉 深度JavaScript分析完成！")
        print("📋 详细报告已保存到: deep_js_analysis_report.json")
        print("📜 日志文件: deep_js_analyzer.log")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断分析")
    except Exception as e:
        print(f"\n❌ 分析过程中发生错误: {e}")

if __name__ == "__main__":
    main()