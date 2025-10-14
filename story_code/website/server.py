#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import os
import json
import sqlite3
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
import time

class StoryHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API路由
        if parsed_path.path.startswith('/api/'):
            self.handle_api_request(parsed_path)
        else:
            # 静态文件服务
            super().do_GET()
    
    def handle_api_request(self, parsed_path):
        """处理API请求"""
        try:
            if parsed_path.path == '/api/stories':
                self.get_stories()
            elif parsed_path.path == '/api/story':
                query_params = parse_qs(parsed_path.query)
                story_id = query_params.get('id', [None])[0]
                if story_id:
                    self.get_story_detail(int(story_id))
                else:
                    self.send_error(400, "Missing story ID")
            elif parsed_path.path == '/api/categories':
                self.get_categories()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            print(f"API错误: {e}")
            self.send_error(500, str(e))
    
    def get_stories(self):
        """获取所有故事"""
        stories = self.load_stories_data()
        self.send_json_response(stories)
    
    def get_story_detail(self, story_id):
        """获取故事详情"""
        stories = self.load_stories_data()
        story = next((s for s in stories if s.get('id') == story_id), None)
        
        if story:
            # 尝试从数据库获取完整内容
            content = self.get_story_content_from_db(story_id)
            if content:
                story['content'] = content
            self.send_json_response(story)
        else:
            self.send_error(404, "Story not found")
    
    def get_categories(self):
        """获取所有分类"""
        stories = self.load_stories_data()
        categories = list(set(story.get('category_name', '未分类') for story in stories))
        self.send_json_response(categories)
    
    def load_stories_data(self):
        """加载故事数据"""
        # 尝试加载不同的数据文件
        data_files = [
            '../enhanced_stories.json',
            '../quick_stories.json',
            'sample_stories.json'
        ]
        
        for file_path in data_files:
            try:
                full_path = os.path.join(os.path.dirname(__file__), file_path)
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"✅ 加载数据文件: {file_path} ({len(data)} 个故事)")
                        return data
            except Exception as e:
                print(f"❌ 加载 {file_path} 失败: {e}")
                continue
        
        # 如果都失败了，返回示例数据
        print("📝 使用示例数据")
        return self.get_sample_stories()
    
    def get_story_content_from_db(self, story_id):
        """从数据库获取故事内容"""
        db_files = [
            '../enhanced_stories.db',
            '../quick_stories.db'
        ]
        
        for db_file in db_files:
            try:
                full_path = os.path.join(os.path.dirname(__file__), db_file)
                if os.path.exists(full_path):
                    conn = sqlite3.connect(full_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT content FROM stories WHERE id = ?", (story_id,))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result and result[0]:
                        return result[0]
            except Exception as e:
                print(f"数据库查询失败 {db_file}: {e}")
                continue
        
        return None
    
    def get_sample_stories(self):
        """获取示例故事数据"""
        return [
            {
                "id": 1,
                "title": "小红帽",
                "category_name": "童话故事",
                "excerpt": "从前有个可爱的小姑娘，她总是戴着一顶红色的帽子，所以大家都叫她小红帽。",
                "length": 1200,
                "content": "从前有个可爱的小姑娘，她总是戴着一顶红色的帽子，所以大家都叫她小红帽。\n\n有一天，妈妈让小红帽去看望生病的奶奶，并给她带去一些好吃的食物。小红帽高高兴兴地出发了。\n\n在去奶奶家的路上，小红帽遇到了一只大灰狼。大灰狼问她要去哪里，小红帽天真地告诉了它。\n\n大灰狼听后，眼珠一转，想出了一个坏主意。它抄近路先到了奶奶家，把奶奶吞进了肚子里，然后穿上奶奶的衣服躺在床上等小红帽。\n\n小红帽到了奶奶家，发现奶奶的样子很奇怪。她问：'奶奶，您的耳朵怎么这么大？''为了更好地听你说话，我的孩子。'\n\n'奶奶，您的眼睛怎么这么大？''为了更好地看你，我的孩子。'\n\n'奶奶，您的嘴巴怎么这么大？''为了更好地吃掉你！'说完，大灰狼就扑向了小红帽。\n\n幸好这时候猎人路过，听到了呼救声，赶紧冲进屋里救出了小红帽和奶奶。从此以后，小红帽再也不随便和陌生人说话了。"
            },
            {
                "id": 2,
                "title": "三只小猪",
                "category_name": "童话故事",
                "excerpt": "三只小猪要盖房子，老大用稻草，老二用木头，老三用砖头。",
                "length": 1500,
                "content": "从前有三只小猪，他们要离开妈妈独自生活。\n\n老大很懒，用稻草盖了一座房子。老二也不太勤快，用木头盖了一座房子。只有老三很勤劳，用砖头盖了一座结实的房子。\n\n有一天，大灰狼来了。它先到了老大的稻草房子前，用力一吹，房子就倒了。老大赶紧跑到老二家。\n\n大灰狼又来到老二的木头房子前，用力一撞，房子也倒了。两只小猪赶紧跑到老三家。\n\n大灰狼来到老三的砖头房子前，又吹又撞，房子纹丝不动。大灰狼气得要从烟囱爬进去。\n\n聪明的老三早就在烟囱下面放了一口大锅，锅里装满了开水。大灰狼掉进锅里，被烫得哇哇叫着逃跑了。\n\n从此以后，三只小猪快快乐乐地生活在一起，老大和老二也学会了要勤劳。"
            },
            {
                "id": 3,
                "title": "龟兔赛跑",
                "category_name": "寓言故事",
                "excerpt": "骄傲的兔子和坚持不懈的乌龟进行了一场赛跑。",
                "length": 800,
                "content": "从前，有一只跑得很快的兔子和一只爬得很慢的乌龟。\n\n兔子总是嘲笑乌龟爬得慢，乌龟很不服气，就向兔子挑战赛跑。\n\n比赛开始了，兔子一下子就跑得很远，回头看看，乌龟还在后面慢慢地爬着。\n\n兔子想：'乌龟爬得这么慢，我先睡一觉也不会输。'于是它在路边睡着了。\n\n乌龟虽然爬得慢，但是它一直坚持不懈地向前爬，一步一步地超过了睡觉的兔子。\n\n等兔子醒来的时候，乌龟已经到达了终点。兔子后悔极了。\n\n这个故事告诉我们：坚持不懈的努力比天赋更重要，骄傲使人落后。"
            }
        ]
    
    def send_json_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def start_server(port=8000):
    """启动服务器"""
    try:
        with socketserver.TCPServer(("", port), StoryHandler) as httpd:
            print(f"🚀 故事网站服务器启动成功!")
            print(f"📱 本地访问地址: http://localhost:{port}")
            print(f"🌐 网络访问地址: http://127.0.0.1:{port}")
            print(f"⏹️  按 Ctrl+C 停止服务器")
            print("-" * 50)
            
            # 延迟打开浏览器
            def open_browser():
                time.sleep(2)
                try:
                    webbrowser.open(f'http://localhost:{port}')
                    print(f"🌐 已自动打开浏览器")
                except:
                    pass
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 10048:  # Windows端口被占用
            print(f"❌ 端口 {port} 被占用，尝试使用端口 {port + 1}")
            start_server(port + 1)
        else:
            print(f"❌ 服务器启动失败: {e}")
    except KeyboardInterrupt:
        print(f"\n⏹️  服务器已停止")

if __name__ == "__main__":
    # 确保在正确的目录中运行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=" * 50)
    print("🏠 小故事铺 - 本地服务器")
    print("=" * 50)
    
    start_server()