#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT 提示词爬虫
从 https://www.explainthis.io/zh-hans/chatgpt 爬取提示词和分类信息
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import List, Dict, Any

class ChatGPTPromptCrawler:
    def __init__(self):
        self.base_url = "https://www.explainthis.io/zh-hans/chatgpt"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def fetch_page(self) -> BeautifulSoup:
        """获取网页内容"""
        try:
            print(f"正在获取页面: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            print("页面获取成功")
            return soup
            
        except requests.RequestException as e:
            print(f"获取页面失败: {e}")
            raise
    
    def extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """提取所有分类"""
        categories = []
        
        # 查找分类按钮容器
        category_container = soup.find('div', class_='mb-10 flex w-full flex-wrap justify-start gap-2 md:gap-4')
        
        if category_container:
            # 查找所有分类按钮
            category_buttons = category_container.find_all('div', class_=re.compile(r'border.*cursor-pointer.*rounded-xl'))
            
            for button in category_buttons:
                category_text = button.get_text(strip=True)
                if category_text and category_text not in categories:
                    categories.append(category_text)
                    
        print(f"找到 {len(categories)} 个分类: {categories}")
        return categories
    
    def extract_prompts(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """提取所有提示词卡片"""
        prompts = []
        
        # 查找所有提示词卡片
        prompt_cards = soup.find_all('div', class_='flex w-full flex-col rounded-xl border border-slate-200 bg-white shadow md:w-[48%] lg:w-[32%]')
        
        print(f"找到 {len(prompt_cards)} 个提示词卡片")
        
        for i, card in enumerate(prompt_cards):
            try:
                prompt_data = self.parse_prompt_card(card)
                if prompt_data:
                    prompts.append(prompt_data)
                    print(f"已解析第 {i+1} 个提示词: {prompt_data['title']}")
                    
            except Exception as e:
                print(f"解析第 {i+1} 个提示词卡片时出错: {e}")
                continue
                
        return prompts
    
    def parse_prompt_card(self, card) -> Dict[str, Any]:
        """解析单个提示词卡片"""
        prompt_data = {}
        
        # 提取标题
        title_element = card.find('h5', class_='mb-2 text-lg font-bold tracking-tight text-slate-900 md:text-xl')
        if title_element:
            prompt_data['title'] = title_element.get_text(strip=True)
        else:
            prompt_data['title'] = ""
            
        # 提取内容描述
        content_element = card.find('p', class_='mb-2 font-normal leading-8 text-slate-800 md:mb-4')
        if content_element:
            # 获取完整文本内容
            content_text = content_element.get_text(strip=True)
            prompt_data['content'] = content_text
            
            # 提取参数占位符（被高亮的部分）
            highlighted_spans = content_element.find_all('span', class_='rounded bg-sky-100 px-[4px] py-[2px] font-medium text-slate-800 md:px-[6px]')
            parameters = []
            for span in highlighted_spans:
                param_text = span.get_text(strip=True)
                if param_text:
                    parameters.append(param_text)
            prompt_data['parameters'] = parameters
        else:
            prompt_data['content'] = ""
            prompt_data['parameters'] = []
        
        # 查找所属分类（通过查找上级分类标题）
        category = self.find_prompt_category(card)
        prompt_data['category'] = category
        
        return prompt_data
    
    def find_prompt_category(self, card) -> str:
        """查找提示词所属的分类"""
        # 向上查找分类标题
        current = card
        while current:
            current = current.find_previous_sibling()
            if current and current.name == 'div':
                # 查找分类标题
                if 'mb-5 border-b-2 border-[#4aa181]' in current.get('class', []):
                    category_text = current.get_text(strip=True)
                    if category_text:
                        return category_text
                        
        # 如果没找到，继续向上查找
        parent = card.parent
        while parent:
            category_div = parent.find_previous('div', class_='mb-5 border-b-2 border-[#4aa181] px-10 pb-3 text-lg md:mb-10')
            if category_div:
                return category_div.get_text(strip=True)
            parent = parent.parent
            
        return "未分类"
    
    def organize_data(self, categories: List[str], prompts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """组织数据为JSON格式"""
        # 按分类组织提示词
        prompts_by_category = {}
        
        for category in categories:
            prompts_by_category[category] = []
            
        for prompt in prompts:
            category = prompt.get('category', '未分类')
            if category not in prompts_by_category:
                prompts_by_category[category] = []
            prompts_by_category[category].append(prompt)
        
        # 统计信息
        total_prompts = len(prompts)
        category_stats = {}
        for category, category_prompts in prompts_by_category.items():
            category_stats[category] = len(category_prompts)
        
        organized_data = {
            "metadata": {
                "source_url": self.base_url,
                "crawl_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_categories": len(categories),
                "total_prompts": total_prompts,
                "category_stats": category_stats
            },
            "categories": categories,
            "prompts_by_category": prompts_by_category,
            "all_prompts": prompts
        }
        
        return organized_data
    
    def save_to_json(self, data: Dict[str, Any], filename: str = "chatgpt_prompts.json"):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到: {filename}")
            
        except Exception as e:
            print(f"保存文件失败: {e}")
            raise
    
    def crawl(self) -> Dict[str, Any]:
        """执行完整的爬取流程"""
        print("开始爬取 ChatGPT 提示词...")
        
        # 获取页面
        soup = self.fetch_page()
        
        # 提取分类
        categories = self.extract_categories(soup)
        
        # 提取提示词
        prompts = self.extract_prompts(soup)
        
        # 组织数据
        organized_data = self.organize_data(categories, prompts)
        
        # 保存数据
        self.save_to_json(organized_data)
        
        # 打印统计信息
        print("\n=== 爬取完成 ===")
        print(f"总分类数: {organized_data['metadata']['total_categories']}")
        print(f"总提示词数: {organized_data['metadata']['total_prompts']}")
        print("\n各分类提示词数量:")
        for category, count in organized_data['metadata']['category_stats'].items():
            print(f"  {category}: {count} 个")
        
        return organized_data

def main():
    """主函数"""
    crawler = ChatGPTPromptCrawler()
    
    try:
        data = crawler.crawl()
        print("\n爬取成功完成！")
        
    except Exception as e:
        print(f"\n爬取过程中出现错误: {e}")
        return False
        
    return True

if __name__ == "__main__":
    main()