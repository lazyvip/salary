"""
步骤1: 从 PyInstaller 打包的 exe 中提取 Python 文件
需要: 
  方法1: pip install pyinstaller-extractor (推荐)
  方法2: 下载 pyinstxtractor.py 脚本
"""
import os
import subprocess
import sys
import struct

def extract_pyinstaller_exe(exe_path, output_dir):
    """
    使用 pyinstaller-extractor 提取 PyInstaller 打包的 exe
    
    Args:
        exe_path: exe文件路径
        output_dir: 输出目录
    """
    print(f"[*] 开始提取 exe: {exe_path}")
    
    # 方法1: 尝试使用 pyinstaller-extractor
    try:
        cmd = f'pyinstxtractor "{exe_path}"'
        print(f"[*] 执行命令: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.path.dirname(exe_path))
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("[+] 提取完成！")
            extracted_path = f"{exe_path}_extracted"
            print(f"[*] 提取的文件应该在: {extracted_path}/")
            return extracted_path
    except Exception as e:
        print(f"[!] pyinstxtractor 方法失败: {e}")
    
    # 方法2: 尝试使用 Python 脚本
    print("\n[*] 尝试下载并使用 pyinstxtractor.py 脚本...")
    try:
        import urllib.request
        script_url = "https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py"
        script_path = os.path.join(os.path.dirname(__file__), "pyinstxtractor_download.py")
        
        print(f"[*] 下载脚本: {script_url}")
        urllib.request.urlretrieve(script_url, script_path)
        
        print(f"[*] 运行提取脚本...")
        cmd = f'python "{script_path}" "{exe_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode == 0:
            print("[+] 提取完成！")
            extracted_path = f"{exe_path}_extracted"
            return extracted_path
    except Exception as e:
        print(f"[!] 下载脚本方法失败: {e}")
    
    # 方法3: 手动提取 (基础实现)
    print("\n[*] 尝试手动提取 (基础方法)...")
    try:
        extracted_path = exe_path + "_extracted"
        os.makedirs(extracted_path, exist_ok=True)
        
        with open(exe_path, 'rb') as f:
            data = f.read()
        
        # 查找 PyInstaller magic number
        magic = b'MEI\014\013\012\013\016'
        if magic in data:
            print("[+] 检测到 PyInstaller 打包文件")
            print(f"[*] 请手动使用以下命令:")
            print(f"    1. 安装: pip install pyinstaller")
            print(f"    2. 下载 pyinstxtractor: git clone https://github.com/extremecoders-re/pyinstxtractor")
            print(f"    3. 运行: python pyinstxtractor/pyinstxtractor.py \"{exe_path}\"")
        else:
            print("[!] 未检测到标准的 PyInstaller 特征")
            print("[*] 这可能是:")
            print("    - 使用其他工具打包 (py2exe, cx_Freeze)")
            print("    - 经过加壳或混淆")
            print("    - 自定义打包")
        
        return extracted_path
    except Exception as e:
        print(f"[!] 手动提取失败: {e}")
        return None

if __name__ == "__main__":
    exe_path = r"d:/github/salary/lazy_hack/exe_file/AI批量生图工具_2.0.14.exe"
    output_dir = r"d:/github/salary/lazy_hack/source_code/extracted"
    
    extracted_path = extract_pyinstaller_exe(exe_path, output_dir)
    print(f"\n[+] 下一步: 查看提取的文件，找到主程序的 .pyc 文件")
    print(f"[+] 通常主文件名为: AI批量生图工具_2.0.14.pyc 或 __main__.pyc")
