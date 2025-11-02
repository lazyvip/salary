import json

# 验证JSON文件
with open('prompts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ 总提示词数: {len(data['prompts'])}")
print("\n📝 前5个提示词示例:")
for i, prompt in enumerate(data['prompts'][:5]):
    print(f"{i+1}. {prompt['提示词名称']} - {prompt['提示词分类']}")

print(f"\n📂 分类统计:")
categories = {}
for prompt in data['prompts']:
    cat = prompt['提示词分类']
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}个")