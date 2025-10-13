#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能网站分析器 - 分析 storynook.cn 的实际结构
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
import time

def analyze_website():
    """分析网站结构"""
    base_url = "https://storynook.cn/"
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print("🔍 正在分析网站结构...")
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        print(f"✅ 成功获取主页，状态码: {response.status_code}")
        print(f"📄 页面大小: {len(response.text)} 字符")
        
        # 保存原始HTML用于分析
        with open('website_analysis.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        analysis_result = {
            "url": base_url,
            "status_code": response.status_code,
            "page_size": len(response.text),
            "title": soup.title.string if soup.title else "无标题",
            "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "findings": {}
        }
        
        print(f"📝 页面标题: {analysis_result['title']}")
        
        # 1. 查找所有JavaScript文件
        scripts = soup.find_all('script', src=True)
        js_files = [urljoin(base_url, script['src']) for script in scripts]
        analysis_result["findings"]["js_files"] = js_files
        print(f"🔧 发现 {len(js_files)} 个JavaScript文件")
        
        # 2. 查找所有链接
        links = soup.find_all('a', href=True)
        all_links = [urljoin(base_url, link['href']) for link in links]
        analysis_result["findings"]["all_links"] = all_links
        print(f"🔗 发现 {len(all_links)} 个链接")
        
        # 3. 查找包含"story"或"故事"的元素
        story_elements = []
        
        # 查找onclick事件
        onclick_elements = soup.find_all(attrs={"onclick": True})
        for elem in onclick_elements:
            onclick = elem.get('onclick', '')
            if 'story' in onclick.lower() or '故事' in onclick:
                story_elements.append({
                    "type": "onclick",
                    "onclick": onclick,
                    "text": elem.get_text(strip=True)[:100],
                    "tag": elem.name
                })
        
        analysis_result["findings"]["story_elements"] = story_elements
        print(f"📚 发现 {len(story_elements)} 个故事相关元素")
        
        # 4. 查找所有表单
        forms = soup.find_all('form')
        form_info = []
        for form in forms:
            form_info.append({
                "action": form.get('action', ''),
                "method": form.get('method', 'GET'),
                "inputs": [{"name": inp.get('name', ''), "type": inp.get('type', '')} 
                          for inp in form.find_all('input')]
            })
        analysis_result["findings"]["forms"] = form_info
        print(f"📋 发现 {len(forms)} 个表单")
        
        # 5. 查找可能的API端点
        api_patterns = [
            r'/api/[^"\s]+',
            r'\.php[^"\s]*',
            r'\.json[^"\s]*',
            r'/ajax/[^"\s]+',
        ]
        
        potential_apis = []
        page_text = response.text
        for pattern in api_patterns:
            matches = re.findall(pattern, page_text)
            for match in matches:
                full_url = urljoin(base_url, match)
                if full_url not in potential_apis:
                    potential_apis.append(full_url)
        
        analysis_result["findings"]["potential_apis"] = potential_apis
        print(f"🔌 发现 {len(potential_apis)} 个潜在API端点")
        
        # 6. 查找所有ID和Class
        all_ids = [elem.get('id') for elem in soup.find_all(id=True)]
        all_classes = []
        for elem in soup.find_all(class_=True):
            classes = elem.get('class', [])
            if isinstance(classes, list):
                all_classes.extend(classes)
            else:
                all_classes.append(classes)
        
        analysis_result["findings"]["ids"] = list(set(all_ids))
        analysis_result["findings"]["classes"] = list(set(all_classes))
        print(f"🏷️ 发现 {len(set(all_ids))} 个ID，{len(set(all_classes))} 个Class")
        
        # 7. 查找可能的数据容器
        data_containers = []
        container_selectors = [
            '[data-story]', '[data-id]', '.story', '.tale', 
            '#stories', '#content', '.content', '.list',
            '.card', '.item', '.post'
        ]
        
        for selector in container_selectors:
            elements = soup.select(selector)
            if elements:
                data_containers.append({
                    "selector": selector,
                    "count": len(elements),
                    "sample_text": elements[0].get_text(strip=True)[:100] if elements else ""
                })
        
        analysis_result["findings"]["data_containers"] = data_containers
        print(f"📦 发现 {len(data_containers)} 种数据容器")
        
        # 8. 检查是否有动态加载的迹象
        dynamic_indicators = []
        dynamic_keywords = ['ajax', 'fetch', 'xhr', 'loadmore', 'infinite', 'scroll']
        
        for keyword in dynamic_keywords:
            if keyword in page_text.lower():
                dynamic_indicators.append(keyword)
        
        analysis_result["findings"]["dynamic_indicators"] = dynamic_indicators
        print(f"⚡ 发现动态加载指示器: {dynamic_indicators}")
        
        # 保存分析结果
        with open('website_analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*50)
        print("📊 分析完成！生成文件:")
        print("   - website_analysis.html (原始HTML)")
        print("   - website_analysis_result.json (分析结果)")
        print("="*50)
        
        # 输出关键发现
        print("\n🔍 关键发现:")
        if story_elements:
            print(f"   ✅ 发现 {len(story_elements)} 个故事元素")
            for elem in story_elements[:3]:
                print(f"      - {elem['onclick'][:50]}...")
        
        if potential_apis:
            print(f"   ✅ 发现 {len(potential_apis)} 个潜在API")
            for api in potential_apis[:3]:
                print(f"      - {api}")
        
        if dynamic_indicators:
            print(f"   ⚡ 动态加载指示器: {', '.join(dynamic_indicators)}")
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return None

if __name__ == "__main__":
    result = analyze_website()
    if result:
        print("\n✅ 网站分析完成！")
    else:
        print("\n❌ 网站分析失败！")