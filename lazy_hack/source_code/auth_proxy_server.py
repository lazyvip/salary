"""
本地授权代理服务器
拦截授权请求并返回成功响应
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class AuthProxyHandler(BaseHTTPRequestHandler):
    """授权代理处理器"""
    
    def do_GET(self):
        """处理 GET 请求"""
        self.send_success_response()
    
    def do_POST(self):
        """处理 POST 请求"""
        # 读取请求数据
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        print(f"[*] 收到授权请求: {body.decode('utf-8', errors='ignore')}")
        
        self.send_success_response()
    
    def send_success_response(self):
        """发送成功响应"""
        response = {
            "status": "success",
            "message": "授权验证成功",
            "activated": True,
            "license": "cracked"
        }
        
        response_data = json.dumps(response).encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.end_headers()
        self.wfile.write(response_data)
        
        print(f"[+] 已返回成功响应")
    
    def log_message(self, format, *args):
        """自定义日志"""
        print(f"[*] {format % args}")

def start_proxy_server(host='127.0.0.1', port=8888):
    """启动代理服务器"""
    server = HTTPServer((host, port), AuthProxyHandler)
    print(f"[*] 授权代理服务器启动: http://{host}:{port}")
    print(f"[*] 请修改软件配置使用此代理")
    print(f"[*] 或修改 hosts 文件将授权域名指向 127.0.0.1")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] 服务器已停止")
        server.shutdown()

if __name__ == "__main__":
    start_proxy_server()
