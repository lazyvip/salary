import json
import os
import random
import requests
import re
from PIL import Image
from io import BytesIO
import time

# Configuration
JSON_URL = "https://opennana.com/awesome-prompt-gallery/data/prompts.json"
BASE_IMG_URL = "https://opennana.com/awesome-prompt-gallery/"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")
DATA_JS_PATH = os.path.join(os.path.dirname(__file__), "data.js")
SAMPLE_SIZE = 50

# 🧠 懒人智能：优先抓取包含这些词的“大片”，保证视觉冲击力
# 这些词通常代表了高质量的生成参数
HOT_KEYWORDS = [
    "cyberpunk", "lighting", "realistic", "8k", "masterpiece", 
    "portrait", "landscape", "anime", "neon", "texture", 
    "detailed", "cinematic", "rendering", "unreal engine"
]

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_filename(text):
    """
    SEO 核心：把提示词变成文件名
    例如: "A beautiful cyberpunk girl..." -> "a-beautiful-cyberpunk-girl"
    """
    if not text:
        return "ai-generated-image"
    
    # 1. 取前 8 个单词 (Google 通常只看前几个词)
    words = text.split()[:8]
    short_text = " ".join(words)
    
    # 2. 只保留字母数字，空格变横杠
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', short_text)
    slug = re.sub(r'\s+', '-', cleaned).strip().lower()
    
    # 3. 防止文件名为空或过长
    if len(slug) < 3:
        return f"ai-art-{int(time.time())}"
    return slug[:100]  # 限制长度

def fetch_data():
    print(f"Fetching data from {JSON_URL}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
        }
        resp = requests.get(JSON_URL, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("items", [])
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def smart_select_items(items, limit):
    """
    智能筛选逻辑：优先选含“热词”的，不够的再随机补
    """
    print("🤖 Running Smart Selection...")
    high_quality_items = []
    other_items = []
    
    for item in items:
        # 获取提示词文本
        prompts = item.get("prompts", [])
        p_text = str(prompts[0]).lower() if prompts else ""
        
        # 检查是否包含热词
        if any(kw in p_text for kw in HOT_KEYWORDS):
            high_quality_items.append(item)
        else:
            other_items.append(item)
            
    print(f"Found {len(high_quality_items)} high-quality items based on keywords.")
    
    # 优先取高质量的
    selected = high_quality_items[:limit]
    
    # 如果不够 50 个，从剩下的里面随机补
    if len(selected) < limit:
        needed = limit - len(selected)
        if len(other_items) >= needed:
            selected.extend(random.sample(other_items, needed))
        else:
            selected.extend(other_items)
            
    # 打乱顺序，防止同类风格扎堆
    random.shuffle(selected)
    return selected[:limit]

def download_and_process_image(url, save_path):
    # (保持原有的下载逻辑不变)
    try:
        headers = {'User-Agent': 'Mozilla/5.0...'}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            # 压缩尺寸和质量
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            img.save(save_path, "WEBP", quality=75)
            return True
        return False
    except Exception:
        return False

def main():
    ensure_dir(OUTPUT_DIR)
    
    # 1. Fetch
    items = fetch_data()
    if not items: return

    # 2. Smart Select (代替原来的 random)
    selected_items = smart_select_items(items, SAMPLE_SIZE)
    print(f"Selected {len(selected_items)} items for processing.")
    
    final_data = []
    
    # 3. Process
    for index, item in enumerate(selected_items):
        item_id = item.get("id", index)
        
        # 获取图片路径
        image_path = item.get("coverImage") or (item.get("images")[0] if item.get("images") else None)
        if not image_path: continue
            
        # 获取提示词
        prompts = item.get("prompts", [])
        prompt_text = prompts[0] if prompts else "ai art"
        
        # --- 关键修改：生成 SEO 文件名 ---
        seo_name = clean_filename(prompt_text if isinstance(prompt_text, str) else "ai-art")
        # 加上 index 防止重名
        local_filename = f"{seo_name}-{index}.webp"
        # -----------------------------
        
        full_img_url = BASE_IMG_URL + image_path
        local_path = os.path.join(OUTPUT_DIR, local_filename)
        
        print(f"[{index+1}/{SAMPLE_SIZE}] Downloading: {local_filename}...")
        
        if download_and_process_image(full_img_url, local_path):
            final_data.append({
                "id": item_id,
                # 前端用相对路径
                "img": f"assets/images/{local_filename}",
                "prompt": prompt_text
            })
            time.sleep(0.1)
    
    # 4. Save JS
    js_content = f"window.SAMPLE_DATA = {json.dumps(final_data, indent=2, ensure_ascii=False)};"
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print(f"Done! SEO-friendly assets generated in {DATA_JS_PATH}")

if __name__ == "__main__":
    main()