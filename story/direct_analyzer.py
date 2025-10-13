#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接网站分析器 - 快速找到正确的故事URL模式
"""

import requests
import json
from bs4 import BeautifulSoup
import re
import time

def analyze_website():
    """分析网站结构"""
    base_url = "https://storynook.cn"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    
    print("🔍 分析网站结构...")
    
    try:
        # 1. 获取主页
        response = session.get(base_url, timeout=10)
        print(f"主页状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. 查找所有链接
            print("\n📋 发现的链接:")
            links = soup.find_all('a', href=True)
            story_links = []
            
            for link in links:
                href = link.get('href')
                text = link.get_text().strip()
                
                if href and ('story' in href.lower() or '故事' in text):
                    full_url = requests.compat.urljoin(base_url, href)
                    story_links.append((full_url, text))
                    print(f"  {full_url} - {text}")
            
            # 3. 分析JavaScript
            print("\n🔧 分析JavaScript代码:")
            scripts = soup.find_all('script')
            for i, script in enumerate(scripts):
                if script.string:
                    # 查找API端点
                    api_matches = re.findall(r'https?://[^\s"\']+\.supabase\.co[^\s"\']*', script.string)
                    if api_matches:
                        print(f"  发现API端点: {api_matches}")
                    
                    # 查找故事ID模式
                    id_matches = re.findall(r'story[_-]?id["\']?\s*[:=]\s*["\']?(\d+)', script.string, re.I)
                    if id_matches:
                        print(f"  发现故事ID: {id_matches}")
                    
                    # 查找数据结构
                    if 'stories' in script.string.lower():
                        print(f"  脚本 {i} 包含stories相关代码")
            
            # 4. 查找表单和输入
            print("\n📝 表单和输入:")
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '')
                method = form.get('method', 'GET')
                print(f"  表单: {action} ({method})")
            
            # 5. 查找数据属性
            print("\n📊 数据属性:")
            elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
            for elem in elements_with_data[:10]:  # 只显示前10个
                data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
                print(f"  {elem.name}: {data_attrs}")
            
            # 6. 尝试常见的故事URL模式
            print("\n🎯 测试常见URL模式:")
            test_patterns = [
                f"{base_url}/story/1",
                f"{base_url}/stories/1", 
                f"{base_url}/post/1",
                f"{base_url}/article/1",
                f"{base_url}/content/1",
                f"{base_url}/read/1",
                f"{base_url}/?id=1",
                f"{base_url}/?story=1",
                f"{base_url}/index.html?id=1"
            ]
            
            for pattern in test_patterns:
                try:
                    test_response = session.head(pattern, timeout=5)
                    print(f"  {pattern}: {test_response.status_code}")
                    if test_response.status_code == 200:
                        print(f"    ✅ 找到有效模式!")
                        return pattern
                except:
                    print(f"  {pattern}: 连接失败")
                
                time.sleep(0.5)
            
            # 7. 检查robots.txt
            print("\n🤖 检查robots.txt:")
            try:
                robots_response = session.get(f"{base_url}/robots.txt", timeout=5)
                if robots_response.status_code == 200:
                    print("robots.txt内容:")
                    print(robots_response.text[:500])
            except:
                print("无法获取robots.txt")
            
            # 8. 检查sitemap
            print("\n🗺️ 检查sitemap:")
            sitemap_urls = [
                f"{base_url}/sitemap.xml",
                f"{base_url}/sitemap.txt",
                f"{base_url}/sitemap_index.xml"
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    sitemap_response = session.get(sitemap_url, timeout=5)
                    if sitemap_response.status_code == 200:
                        print(f"找到sitemap: {sitemap_url}")
                        print(sitemap_response.text[:500])
                        break
                except:
                    continue
            
            return story_links
            
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return []

def test_story_access():
    """测试故事访问"""
    print("\n🧪 测试故事访问...")
    
    base_url = "https://storynook.cn"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # 测试不同的ID范围
    test_ranges = [
        range(1, 11),      # 1-10
        range(100, 111),   # 100-110
        range(1000, 1011), # 1000-1010
    ]
    
    patterns = [
        "{}/story/{}",
        "{}/stories/{}",
        "{}/?id={}",
        "{}/read/{}",
        "{}/post/{}"
    ]
    
    found_stories = []
    
    for pattern in patterns:
        print(f"\n测试模式: {pattern}")
        for test_range in test_ranges:
            for story_id in test_range:
                url = pattern.format(base_url, story_id)
                try:
                    response = session.head(url, timeout=3)
                    if response.status_code == 200:
                        print(f"  ✅ 找到故事: {url}")
                        found_stories.append(url)
                        
                        # 获取内容验证
                        content_response = session.get(url, timeout=5)
                        if content_response.status_code == 200:
                            soup = BeautifulSoup(content_response.text, 'html.parser')
                            title = soup.find('title')
                            if title:
                                print(f"    标题: {title.get_text()}")
                    
                except:
                    pass
                
                time.sleep(0.1)
            
            if found_stories:
                break
        
        if found_stories:
            break
    
    return found_stories

def main():
    """主函数"""
    print("🚀 开始网站分析...")
    
    # 分析网站结构
    story_links = analyze_website()
    
    # 测试故事访问
    found_stories = test_story_access()
    
    print("\n" + "="*50)
    print("📊 分析结果总结")
    print("="*50)
    
    if story_links:
        print(f"从主页发现 {len(story_links)} 个故事链接")
        for link, text in story_links[:5]:
            print(f"  {link} - {text}")
    
    if found_stories:
        print(f"通过测试发现 {len(found_stories)} 个有效故事URL")
        for url in found_stories[:5]:
            print(f"  {url}")
    else:
        print("❌ 未找到有效的故事URL模式")
    
    print("\n💡 建议:")
    if found_stories:
        print("- 使用发现的URL模式进行批量爬取")
        print("- 可以尝试更大的ID范围")
    else:
        print("- 网站可能使用动态加载")
        print("- 需要分析JavaScript或API调用")
        print("- 考虑使用浏览器自动化工具")

if __name__ == "__main__":
    main()