"""
离线破解补丁 - 绕过授权验证
适用于 AI批量生图工具 v2.0.14

使用方法:
1. 运行此脚本
2. 重新打包 exe
3. 或者使用 Hook 方式运行
"""

import os
import sys

def create_fake_auth_module():
    """创建假的授权模块，始终返回成功"""
    
    fake_auth = '''"""
假的授权模块 - 始终返回成功
"""

def ensure_license(*args, **kwargs):
    """确保授权 - 始终返回成功"""
    return "success"

def setup_periodic_license_check(*args, **kwargs):
    """设置定期检查 - 不执行任何操作"""
    pass

class LicenseChecker:
    """假的授权检查器"""
    
    def __init__(self):
        self.status = "success"
    
    def check(self, *args, **kwargs):
        return "success"
    
    def verify(self, *args, **kwargs):
        return True
    
    def validate(self, *args, **kwargs):
        return True

def ensure_license_with_loading(*args, **kwargs):
    """带加载的授权检查 - 始终成功"""
    return "success"

def ensure_license_with_progress(*args, **kwargs):
    """带进度的授权检查 - 始终成功"""
    return "success"
'''
    
    # 保存假的 auth.py
    output_dir = "./patched_modules"
    os.makedirs(output_dir, exist_ok=True)
    
    auth_file = os.path.join(output_dir, "auth.py")
    with open(auth_file, 'w', encoding='utf-8') as f:
        f.write(fake_auth)
    
    print(f"[+] 假授权模块已创建: {auth_file}")
    
    # 创建 license_check.py
    license_check_file = os.path.join(output_dir, "license_check.py")
    with open(license_check_file, 'w', encoding='utf-8') as f:
        f.write(fake_auth)
    
    print(f"[+] 假授权检查模块已创建: {license_check_file}")
    
    return output_dir

def create_hook_script():
    """创建 Hook 启动脚本"""
    
    hook_script = '''"""
Hook 启动脚本
使用假的授权模块替换真实模块
"""

import sys
import os

# 添加假模块路径到最前面
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patched_modules'))

print("[*] 已加载破解补丁")
print("[*] 授权验证已绕过")

# 导入主程序
if __name__ == "__main__":
    # 这里需要根据实际情况调整
    # 如果能直接运行 pyc
    import main_refactored
'''
    
    with open("./run_patched.py", 'w', encoding='utf-8') as f:
        f.write(hook_script)
    
    print("[+] Hook 脚本已创建: run_patched.py")

def create_hosts_blocker():
    """创建 hosts 文件阻止规则"""
    
    print("\n" + "="*80)
    print("方法 1: 修改 hosts 文件阻止授权服务器")
    print("="*80)
    print("\n将以下内容添加到 C:\\Windows\\System32\\drivers\\etc\\hosts 文件:")
    print("\n# 阻止 AI批量生图工具授权服务器")
    print("127.0.0.1 license.example.com")
    print("127.0.0.1 auth.example.com")
    print("127.0.0.1 api.example.com")
    print("\n注意: 需要管理员权限编辑 hosts 文件")

def create_firewall_rules():
    """创建防火墙规则"""
    
    print("\n" + "="*80)
    print("方法 2: 使用防火墙阻止软件联网")
    print("="*80)
    print("\nWindows 防火墙规则:")
    print("1. 打开 Windows Defender 防火墙")
    print("2. 点击'高级设置'")
    print("3. 选择'出站规则' -> '新建规则'")
    print("4. 选择'程序' -> 浏览选择 AI批量生图工具.exe")
    print("5. 选择'阻止连接'")
    print("6. 应用到所有配置文件")
    print("7. 完成")

def create_proxy_script():
    """创建本地代理服务器脚本"""
    
    proxy_script = '''"""
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
        print("\\n[*] 服务器已停止")
        server.shutdown()

if __name__ == "__main__":
    start_proxy_server()
'''
    
    with open("./auth_proxy_server.py", 'w', encoding='utf-8') as f:
        f.write(proxy_script)
    
    print("\n[+] 本地代理服务器脚本已创建: auth_proxy_server.py")

def main():
    """主函数"""
    print("="*80)
    print("AI批量生图工具 v2.0.14 - 离线破解补丁生成器")
    print("="*80)
    print("\n检测到 403 错误 - 软件正在联网验证授权")
    print("现在生成离线破解方案...\n")
    
    # 1. 创建假的授权模块
    patched_dir = create_fake_auth_module()
    
    # 2. 创建 Hook 脚本
    create_hook_script()
    
    # 3. 创建代理服务器
    create_proxy_script()
    
    # 4. 提供 hosts 阻止方案
    create_hosts_blocker()
    
    # 5. 提供防火墙方案
    create_firewall_rules()
    
    print("\n" + "="*80)
    print("破解方案总结")
    print("="*80)
    
    print("\n🔥 推荐方案 (按优先级):")
    print("\n1️⃣ 方法一: 防火墙阻止 (最简单)")
    print("   - 打开防火墙设置")
    print("   - 阻止软件联网")
    print("   - 重启软件")
    print("   - 优点: 简单，不修改文件")
    
    print("\n2️⃣ 方法二: 修改 hosts 文件")
    print("   - 编辑 C:\\Windows\\System32\\drivers\\etc\\hosts")
    print("   - 添加阻止规则")
    print("   - 重启软件")
    print("   - 优点: 阻止特定域名")
    
    print("\n3️⃣ 方法三: 本地代理服务器 (高级)")
    print("   - 运行: python auth_proxy_server.py")
    print("   - 修改 hosts 指向 127.0.0.1")
    print("   - 拦截并伪造授权响应")
    print("   - 优点: 可以查看具体请求")
    
    print("\n4️⃣ 方法四: Hook 模块替换 (需要源码)")
    print("   - 使用生成的假授权模块")
    print("   - 替换原始授权模块")
    print("   - 重新打包或 Hook 运行")
    print("   - 优点: 永久破解")
    
    print("\n" + "="*80)
    print("生成的文件:")
    print("="*80)
    print(f"  ✅ {patched_dir}/auth.py")
    print(f"  ✅ {patched_dir}/license_check.py")
    print(f"  ✅ run_patched.py")
    print(f"  ✅ auth_proxy_server.py")
    
    print("\n" + "="*80)
    print("立即可用的方案:")
    print("="*80)
    print("\n⚡ 快速方案: 断网使用")
    print("   1. 断开网络连接")
    print("   2. 运行软件")
    print("   3. 查看是否有离线模式")
    
    print("\n⚡ 简单方案: 防火墙阻止")
    print("   1. Win + R 输入 wf.msc")
    print("   2. 新建出站规则")
    print("   3. 阻止 AI批量生图工具.exe")
    print("   4. 重启软件")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
