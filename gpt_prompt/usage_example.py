#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT 提示词数据使用示例
展示如何使用爬取的提示词数据
"""

import json
import random

class PromptManager:
    def __init__(self, json_file="chatgpt_prompts.json"):
        """初始化提示词管理器"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.categories = self.data['categories']
        self.prompts_by_category = self.data['prompts_by_category']
        self.all_prompts = self.data['all_prompts']
    
    def get_categories(self):
        """获取所有分类"""
        return [cat for cat in self.categories if cat != '全部']
    
    def get_prompts_by_category(self, category):
        """根据分类获取提示词"""
        return self.prompts_by_category.get(category, [])
    
    def search_prompts(self, keyword):
        """搜索包含关键词的提示词"""
        results = []
        for prompt in self.all_prompts:
            if (keyword.lower() in prompt['title'].lower() or 
                keyword.lower() in prompt['content'].lower()):
                results.append(prompt)
        return results
    
    def get_random_prompt(self, category=None):
        """获取随机提示词"""
        if category and category in self.prompts_by_category:
            prompts = self.prompts_by_category[category]
        else:
            prompts = self.all_prompts
        
        if prompts:
            return random.choice(prompts)
        return None
    
    def format_prompt(self, prompt, fill_parameters=None):
        """格式化提示词，可选择填入参数"""
        title = prompt['title']
        content = prompt['content']
        parameters = prompt['parameters']
        category = prompt['category']
        
        formatted = f"【{category}】{title}\n"
        formatted += "=" * 50 + "\n"
        formatted += f"提示词内容：\n{content}\n\n"
        
        if parameters:
            formatted += "需要填入的参数：\n"
            for i, param in enumerate(parameters, 1):
                if fill_parameters and i <= len(fill_parameters):
                    formatted += f"  {i}. {param} → {fill_parameters[i-1]}\n"
                else:
                    formatted += f"  {i}. {param}\n"
            formatted += "\n"
        
        if fill_parameters and len(fill_parameters) >= len(parameters):
            formatted += "填入参数后的提示词：\n"
            filled_content = content
            for i, param in enumerate(parameters):
                if i < len(fill_parameters):
                    filled_content = filled_content.replace(param, fill_parameters[i])
            formatted += filled_content + "\n"
        
        return formatted

def demo():
    """演示功能"""
    print("🤖 ChatGPT 提示词管理器演示")
    print("=" * 50)
    
    # 初始化管理器
    manager = PromptManager()
    
    # 显示统计信息
    print(f"📊 数据统计：")
    print(f"   总分类数：{len(manager.get_categories())}")
    print(f"   总提示词数：{len(manager.all_prompts)}")
    print()
    
    # 显示所有分类
    print("📂 可用分类：")
    for i, category in enumerate(manager.get_categories(), 1):
        count = len(manager.get_prompts_by_category(category))
        print(f"   {i:2d}. {category} ({count} 个提示词)")
    print()
    
    # 演示按分类获取提示词
    print("🔍 演示：获取'程式开发'分类的提示词")
    dev_prompts = manager.get_prompts_by_category('程式开发')
    for i, prompt in enumerate(dev_prompts[:3], 1):
        print(f"   {i}. {prompt['title']}")
    print()
    
    # 演示搜索功能
    print("🔍 演示：搜索包含'面试'的提示词")
    search_results = manager.search_prompts('面试')
    for i, prompt in enumerate(search_results[:3], 1):
        print(f"   {i}. {prompt['title']} ({prompt['category']})")
    print()
    
    # 演示随机提示词
    print("🎲 演示：随机提示词")
    random_prompt = manager.get_random_prompt()
    if random_prompt:
        print(manager.format_prompt(random_prompt))
    
    # 演示参数填入
    print("📝 演示：参数填入示例")
    # 找一个有参数的提示词
    prompt_with_params = None
    for prompt in manager.all_prompts:
        if prompt['parameters']:
            prompt_with_params = prompt
            break
    
    if prompt_with_params:
        print("原始提示词：")
        print(manager.format_prompt(prompt_with_params))
        
        # 填入示例参数
        if prompt_with_params['title'] == '寻求履历的反馈':
            example_params = ['软件工程师', '我的技术履历内容...']
            print("填入参数后：")
            print(manager.format_prompt(prompt_with_params, example_params))

def interactive_mode():
    """交互模式"""
    manager = PromptManager()
    
    while True:
        print("\n" + "=" * 50)
        print("🤖 ChatGPT 提示词管理器")
        print("=" * 50)
        print("1. 查看所有分类")
        print("2. 按分类浏览提示词")
        print("3. 搜索提示词")
        print("4. 获取随机提示词")
        print("5. 退出")
        
        choice = input("\n请选择功能 (1-5): ").strip()
        
        if choice == '1':
            print("\n📂 所有分类：")
            for i, category in enumerate(manager.get_categories(), 1):
                count = len(manager.get_prompts_by_category(category))
                print(f"   {i:2d}. {category} ({count} 个提示词)")
        
        elif choice == '2':
            print("\n📂 选择分类：")
            categories = manager.get_categories()
            for i, category in enumerate(categories, 1):
                print(f"   {i}. {category}")
            
            try:
                cat_choice = int(input("\n请输入分类编号: ")) - 1
                if 0 <= cat_choice < len(categories):
                    selected_category = categories[cat_choice]
                    prompts = manager.get_prompts_by_category(selected_category)
                    
                    print(f"\n📝 {selected_category} 分类的提示词：")
                    for i, prompt in enumerate(prompts, 1):
                        print(f"   {i}. {prompt['title']}")
                    
                    try:
                        prompt_choice = int(input("\n请输入提示词编号查看详情 (0跳过): "))
                        if 1 <= prompt_choice <= len(prompts):
                            selected_prompt = prompts[prompt_choice - 1]
                            print("\n" + manager.format_prompt(selected_prompt))
                    except ValueError:
                        pass
                else:
                    print("❌ 无效的分类编号")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        elif choice == '3':
            keyword = input("\n🔍 请输入搜索关键词: ").strip()
            if keyword:
                results = manager.search_prompts(keyword)
                if results:
                    print(f"\n找到 {len(results)} 个相关提示词：")
                    for i, prompt in enumerate(results, 1):
                        print(f"   {i}. {prompt['title']} ({prompt['category']})")
                    
                    try:
                        choice_num = int(input("\n请输入编号查看详情 (0跳过): "))
                        if 1 <= choice_num <= len(results):
                            selected_prompt = results[choice_num - 1]
                            print("\n" + manager.format_prompt(selected_prompt))
                    except ValueError:
                        pass
                else:
                    print("❌ 没有找到相关提示词")
        
        elif choice == '4':
            random_prompt = manager.get_random_prompt()
            if random_prompt:
                print("\n🎲 随机提示词：")
                print(manager.format_prompt(random_prompt))
        
        elif choice == '5':
            print("\n👋 再见！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

def main():
    """主函数"""
    print("选择运行模式：")
    print("1. 演示模式")
    print("2. 交互模式")
    
    choice = input("请选择 (1-2): ").strip()
    
    if choice == '1':
        demo()
    elif choice == '2':
        interactive_mode()
    else:
        print("运行演示模式...")
        demo()

if __name__ == "__main__":
    main()