import requests
from bs4 import BeautifulSoup
import json
import time
import re

def get_page_content(url):
    """获取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        print(f"获取网页内容失败: {e}")
        return None

def analyze_page_structure(html_content):
    """分析网页结构，找到提示词卡片和分类"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 保存格式化的HTML到文件以便分析
    with open('f:\\个人文档\\website\\salary\\gpt_prompt\\actual_page_formatted.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print("格式化的网页内容已保存到 actual_page_formatted.html")
    
    # 查找所有包含中文的div元素，这些可能是分类或提示词
    all_divs = soup.find_all('div')
    categories = []
    cards = []
    
    for div in all_divs:
        text = div.get_text(strip=True)
        if not text:
            continue
            
        # 查找可能的分类（短文本，包含特定关键词）
        if len(text) < 50 and any(keyword in text for keyword in 
                                 ['求职', '面试', '写作', '学习', '教育', '营销', '编程', '翻译', '创意', '分析', '全部']):
            categories.append({
                'text': text,
                'class': div.get('class', []),
                'parent_class': div.parent.get('class', []) if div.parent else [],
                'html': str(div)[:300]
            })
        
        # 查找可能的提示词卡片（较长文本，包含"复制"等关键词）
        elif len(text) > 30 and ('复制' in text or '已复制' in text or len(text) > 100):
            cards.append({
                'text': text[:300] + '...' if len(text) > 300 else text,
                'class': div.get('class', []),
                'parent_class': div.parent.get('class', []) if div.parent else [],
                'html': str(div)[:500] + '...' if len(str(div)) > 500 else str(div)
            })
    
    # 查找按钮元素（可能是分类按钮）
    buttons = soup.find_all('button')
    for button in buttons:
        text = button.get_text(strip=True)
        if text and len(text) < 50:
            categories.append({
                'text': text,
                'class': button.get('class', []),
                'parent_class': button.parent.get('class', []) if button.parent else [],
                'html': str(button)[:300],
                'type': 'button'
            })
    
    return categories, cards

def main():
    url = 'https://www.explainthis.io/zh-hans/chatgpt'
    print(f"正在获取网页内容: {url}")
    
    html_content = get_page_content(url)
    if not html_content:
        print("无法获取网页内容")
        return
    
    print("正在分析网页结构...")
    categories, cards = analyze_page_structure(html_content)
    
    print(f"\n找到 {len(categories)} 个可能的分类元素:")
    for i, cat in enumerate(categories[:10]):  # 只显示前10个
        print(f"{i+1}. 文本: {cat['text']}")
        print(f"   类名: {cat['class']}")
        print(f"   类型: {cat.get('type', 'div')}")
        print()
    
    print(f"\n找到 {len(cards)} 个可能的提示词卡片:")
    for i, card in enumerate(cards[:5]):  # 只显示前5个
        print(f"{i+1}. 文本预览: {card['text']}")
        print(f"   类名: {card['class']}")
        print(f"   HTML预览: {card['html']}")
        print("-" * 50)

if __name__ == "__main__":
    main()