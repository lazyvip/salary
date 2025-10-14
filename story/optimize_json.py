import json
import os

# 读取原始数据
with open('supabase_stories.json', 'r', encoding='utf-8') as f:
    stories = json.load(f)

with open('supabase_story_contents.json', 'r', encoding='utf-8') as f:
    story_contents = json.load(f)

# 创建内容目录
if not os.path.exists('contents'):
    os.makedirs('contents')

# 创建优化的故事列表（不包含详细内容）
optimized_stories = []
for story in stories:
    optimized_story = {
        'id': story['id'],
        'title': story['title'],
        'excerpt': story['excerpt'],
        'category_id': story['category_id'],
        'category_name': story['category_name'],
        'length': story['length']
    }
    optimized_stories.append(optimized_story)

# 保存优化的故事列表
with open('stories_optimized.json', 'w', encoding='utf-8') as f:
    json.dump(optimized_stories, f, ensure_ascii=False, indent=2)

# 将故事内容分批保存到单独文件
batch_size = 100
for i in range(0, len(story_contents), batch_size):
    batch = story_contents[i:i+batch_size]
    batch_num = i // batch_size + 1
    
    with open(f'contents/batch_{batch_num}.json', 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)

print('优化完成！')
print(f'原始故事文件大小: {os.path.getsize("supabase_stories.json")} bytes')
print(f'优化后故事文件大小: {os.path.getsize("stories_optimized.json")} bytes')
print(f'故事内容分为 {(len(story_contents) + batch_size - 1) // batch_size} 个批次文件')

# 显示各批次文件大小
for i in range(1, (len(story_contents) + batch_size - 1) // batch_size + 1):
    file_path = f'contents/batch_{i}.json'
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f'批次 {i} 文件大小: {size} bytes ({size/1024:.1f} KB)')