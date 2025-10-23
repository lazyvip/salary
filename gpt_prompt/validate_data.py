#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证脚本
验证爬取的ChatGPT提示词数据的完整性和质量
"""

import json
import os

def validate_json_data(filename="chatgpt_prompts.json"):
    """验证JSON数据的完整性"""
    
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False
    
    print("🔍 开始验证数据...")
    
    # 验证基本结构
    required_keys = ['metadata', 'categories', 'prompts_by_category', 'all_prompts']
    for key in required_keys:
        if key not in data:
            print(f"❌ 缺少必要字段: {key}")
            return False
    
    print("✅ JSON结构完整")
    
    # 验证元数据
    metadata = data['metadata']
    print(f"📊 数据统计:")
    print(f"   - 爬取时间: {metadata.get('crawl_time', 'N/A')}")
    print(f"   - 总分类数: {metadata.get('total_categories', 0)}")
    print(f"   - 总提示词数: {metadata.get('total_prompts', 0)}")
    
    # 验证分类
    categories = data['categories']
    print(f"📂 分类验证:")
    print(f"   - 分类列表长度: {len(categories)}")
    
    # 验证提示词
    all_prompts = data['all_prompts']
    print(f"📝 提示词验证:")
    print(f"   - 提示词总数: {len(all_prompts)}")
    
    # 检查提示词字段完整性
    required_prompt_fields = ['title', 'content', 'parameters', 'category']
    incomplete_prompts = 0
    empty_titles = 0
    empty_contents = 0
    
    for i, prompt in enumerate(all_prompts):
        # 检查必要字段
        for field in required_prompt_fields:
            if field not in prompt:
                print(f"⚠️  提示词 {i+1} 缺少字段: {field}")
                incomplete_prompts += 1
                break
        
        # 检查内容是否为空
        if not prompt.get('title', '').strip():
            empty_titles += 1
        
        if not prompt.get('content', '').strip():
            empty_contents += 1
    
    print(f"   - 字段不完整的提示词: {incomplete_prompts}")
    print(f"   - 标题为空的提示词: {empty_titles}")
    print(f"   - 内容为空的提示词: {empty_contents}")
    
    # 验证分类分布
    prompts_by_category = data['prompts_by_category']
    print(f"📈 分类分布验证:")
    
    total_in_categories = 0
    for category, prompts in prompts_by_category.items():
        count = len(prompts)
        total_in_categories += count
        print(f"   - {category}: {count} 个提示词")
    
    print(f"   - 分类中提示词总数: {total_in_categories}")
    print(f"   - all_prompts中提示词总数: {len(all_prompts)}")
    
    # 检查数量一致性
    if total_in_categories != len(all_prompts):
        print("⚠️  分类中的提示词总数与all_prompts不一致")
    else:
        print("✅ 提示词数量一致")
    
    # 显示示例提示词
    print(f"\n📋 示例提示词:")
    for i, prompt in enumerate(all_prompts[:3]):
        print(f"   {i+1}. 标题: {prompt.get('title', 'N/A')}")
        print(f"      分类: {prompt.get('category', 'N/A')}")
        print(f"      参数数量: {len(prompt.get('parameters', []))}")
        content_preview = prompt.get('content', '')[:50] + '...' if len(prompt.get('content', '')) > 50 else prompt.get('content', '')
        print(f"      内容预览: {content_preview}")
        print()
    
    # 总体评估
    if incomplete_prompts == 0 and empty_titles == 0 and empty_contents == 0:
        print("🎉 数据验证通过！所有提示词数据完整。")
        return True
    else:
        print("⚠️  数据存在一些问题，但基本可用。")
        return True

def main():
    """主函数"""
    print("=" * 50)
    print("ChatGPT 提示词数据验证")
    print("=" * 50)
    
    result = validate_json_data()
    
    if result:
        print("\n✅ 验证完成")
    else:
        print("\n❌ 验证失败")
    
    return result

if __name__ == "__main__":
    main()