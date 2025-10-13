#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript分析器 - 分析storynook.cn的JavaScript文件
找到数据获取的方法和API端点
"""

import requests
import re
import json
from urllib.parse import urljoin

def analyze_js_files():
    """分析JavaScript文件"""
    base_url = "https://storynook.cn/"
    
    # 从分析结果中获取JS文件列表
    js_files = [
        "https://storynook.cn/js/supabase-client.js",
        "https://storynook.cn/js/app.js"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': base_url
    }
    
    analysis_results = {}
    
    for js_url in js_files:
        try:
            print(f"🔍 分析JavaScript文件: {js_url}")
            response = requests.get(js_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            js_content = response.text
            print(f"📄 文件大小: {len(js_content)} 字符")
            
            # 保存JS文件内容
            filename = js_url.split('/')[-1]
            with open(f'js_analysis_{filename}', 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            # 分析JS内容
            analysis = analyze_js_content(js_content, js_url)
            analysis_results[js_url] = analysis
            
            print(f"✅ 分析完成: {filename}")
            
        except Exception as e:
            print(f"❌ 分析失败 {js_url}: {e}")
            continue
    
    # 保存分析结果
    with open('js_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    return analysis_results

def analyze_js_content(js_content, js_url):
    """分析JavaScript内容"""
    analysis = {
        "url": js_url,
        "size": len(js_content),
        "findings": {}
    }
    
    # 1. 查找API端点
    api_patterns = [
        r'["\']https?://[^"\']+["\']',  # HTTP URLs
        r'["\'][^"\']*\.php[^"\']*["\']',  # PHP files
        r'["\'][^"\']*api[^"\']*["\']',  # API paths
        r'["\'][^"\']*ajax[^"\']*["\']',  # AJAX paths
    ]
    
    api_endpoints = []
    for pattern in api_patterns:
        matches = re.findall(pattern, js_content)
        for match in matches:
            clean_match = match.strip('"\'')
            if clean_match and clean_match not in api_endpoints:
                api_endpoints.append(clean_match)
    
    analysis["findings"]["api_endpoints"] = api_endpoints
    print(f"   🔌 发现 {len(api_endpoints)} 个API端点")
    
    # 2. 查找函数定义
    function_patterns = [
        r'function\s+(\w+)\s*\(',  # function declarations
        r'(\w+)\s*:\s*function\s*\(',  # object methods
        r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',  # arrow functions
        r'let\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',  # arrow functions
        r'var\s+(\w+)\s*=\s*function\s*\(',  # var functions
    ]
    
    functions = []
    for pattern in function_patterns:
        matches = re.findall(pattern, js_content)
        functions.extend(matches)
    
    analysis["findings"]["functions"] = list(set(functions))
    print(f"   🔧 发现 {len(set(functions))} 个函数")
    
    # 3. 查找Supabase相关代码
    supabase_patterns = [
        r'supabase\.[^(]+\([^)]*\)',  # supabase method calls
        r'\.from\(["\']([^"\']+)["\']\)',  # table names
        r'\.select\(["\']([^"\']+)["\']\)',  # select queries
        r'\.eq\(["\']([^"\']+)["\']\s*,\s*[^)]+\)',  # equality filters
    ]
    
    supabase_calls = []
    table_names = []
    
    for pattern in supabase_patterns:
        matches = re.findall(pattern, js_content)
        if 'from' in pattern:
            table_names.extend(matches)
        else:
            supabase_calls.extend(matches)
    
    analysis["findings"]["supabase_calls"] = supabase_calls
    analysis["findings"]["table_names"] = list(set(table_names))
    print(f"   📊 发现 {len(supabase_calls)} 个Supabase调用")
    print(f"   📋 发现 {len(set(table_names))} 个数据表")
    
    # 4. 查找故事相关的代码
    story_patterns = [
        r'story[A-Z]\w*',  # camelCase story variables
        r'["\']story[^"\']*["\']',  # story strings
        r'showStory\s*\([^)]*\)',  # showStory function calls
        r'loadStory\s*\([^)]*\)',  # loadStory function calls
        r'getStory\s*\([^)]*\)',  # getStory function calls
    ]
    
    story_related = []
    for pattern in story_patterns:
        matches = re.findall(pattern, js_content)
        story_related.extend(matches)
    
    analysis["findings"]["story_related"] = list(set(story_related))
    print(f"   📚 发现 {len(set(story_related))} 个故事相关代码")
    
    # 5. 查找配置和常量
    config_patterns = [
        r'const\s+(\w+)\s*=\s*["\'][^"\']+["\']',  # string constants
        r'const\s+(\w+)\s*=\s*\{[^}]+\}',  # object constants
        r'["\']([A-Z_]+)["\']',  # uppercase constants
    ]
    
    configs = []
    for pattern in config_patterns:
        matches = re.findall(pattern, js_content)
        configs.extend(matches)
    
    analysis["findings"]["configs"] = list(set(configs))
    print(f"   ⚙️ 发现 {len(set(configs))} 个配置项")
    
    return analysis

def extract_key_info(analysis_results):
    """提取关键信息"""
    print("\n" + "="*60)
    print("🔍 关键信息提取:")
    print("="*60)
    
    all_tables = []
    all_apis = []
    all_functions = []
    
    for js_url, analysis in analysis_results.items():
        print(f"\n📄 {js_url.split('/')[-1]}:")
        
        # 数据表
        tables = analysis["findings"].get("table_names", [])
        if tables:
            print(f"   📋 数据表: {', '.join(tables)}")
            all_tables.extend(tables)
        
        # API端点
        apis = analysis["findings"].get("api_endpoints", [])
        if apis:
            print(f"   🔌 API端点: {len(apis)} 个")
            for api in apis[:5]:  # 显示前5个
                print(f"      - {api}")
            all_apis.extend(apis)
        
        # 故事相关函数
        story_funcs = analysis["findings"].get("story_related", [])
        if story_funcs:
            print(f"   📚 故事函数: {', '.join(story_funcs[:5])}")
        
        # 重要函数
        functions = analysis["findings"].get("functions", [])
        important_funcs = [f for f in functions if any(keyword in f.lower() 
                          for keyword in ['story', 'load', 'get', 'fetch', 'show'])]
        if important_funcs:
            print(f"   🔧 重要函数: {', '.join(important_funcs[:5])}")
            all_functions.extend(important_funcs)
    
    print(f"\n📊 总结:")
    print(f"   - 数据表: {len(set(all_tables))} 个")
    print(f"   - API端点: {len(set(all_apis))} 个")
    print(f"   - 重要函数: {len(set(all_functions))} 个")
    
    return {
        "tables": list(set(all_tables)),
        "apis": list(set(all_apis)),
        "functions": list(set(all_functions))
    }

if __name__ == "__main__":
    print("🚀 开始分析JavaScript文件...")
    results = analyze_js_files()
    
    if results:
        key_info = extract_key_info(results)
        
        # 保存关键信息
        with open('key_info_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(key_info, f, ensure_ascii=False, indent=2)
        
        print("\n✅ JavaScript分析完成！")
        print("📁 生成文件:")
        print("   - js_analysis_*.js (JavaScript文件内容)")
        print("   - js_analysis_results.json (详细分析结果)")
        print("   - key_info_extracted.json (关键信息)")
    else:
        print("\n❌ JavaScript分析失败！")