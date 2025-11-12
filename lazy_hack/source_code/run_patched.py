"""
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
