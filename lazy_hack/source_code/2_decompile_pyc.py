"""
步骤2: 反编译 .pyc 文件为 .py 源代码
需要安装: pip install uncompyle6 或 pip install decompyle3
"""
import os
import subprocess
import sys
import glob

def decompile_pyc(pyc_path, output_path=None):
    """
    反编译单个 .pyc 文件
    
    Args:
        pyc_path: .pyc 文件路径
        output_path: 输出的 .py 文件路径
    """
    if output_path is None:
        output_path = pyc_path.replace('.pyc', '_decompiled.py')
    
    print(f"[*] 反编译: {pyc_path}")
    
    # 尝试使用 uncompyle6
    try:
        cmd = f'uncompyle6 -o "{output_path}" "{pyc_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[+] 成功反编译到: {output_path}")
            return output_path
        else:
            print(f"[!] uncompyle6 失败: {result.stderr}")
    except Exception as e:
        print(f"[!] uncompyle6 错误: {e}")
    
    # 尝试使用 decompyle3
    try:
        cmd = f'decompyle3 "{pyc_path}" > "{output_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[+] 成功反编译到: {output_path}")
            return output_path
        else:
            print(f"[!] decompyle3 失败: {result.stderr}")
    except Exception as e:
        print(f"[!] decompyle3 错误: {e}")
    
    # 尝试使用 pycdc
    try:
        cmd = f'pycdc "{pyc_path}" > "{output_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"[+] 成功反编译到: {output_path}")
            return output_path
    except Exception as e:
        print(f"[!] pycdc 错误: {e}")
    
    print(f"[!] 所有反编译工具都失败了")
    return None

def decompile_all_pyc_in_dir(directory):
    """
    反编译目录下所有 .pyc 文件
    
    Args:
        directory: 包含 .pyc 文件的目录
    """
    pyc_files = glob.glob(os.path.join(directory, "**/*.pyc"), recursive=True)
    
    print(f"[*] 找到 {len(pyc_files)} 个 .pyc 文件")
    
    output_dir = os.path.join(directory, "decompiled")
    os.makedirs(output_dir, exist_ok=True)
    
    for pyc_file in pyc_files:
        rel_path = os.path.relpath(pyc_file, directory)
        output_path = os.path.join(output_dir, rel_path.replace('.pyc', '.py'))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        decompile_pyc(pyc_file, output_path)
    
    print(f"\n[+] 反编译完成！源代码在: {output_dir}")

if __name__ == "__main__":
    # 方式1: 反编译单个文件
    # pyc_path = r"d:/github/salary/lazy_hack/exe_file/AI批量生图工具_2.0.14.exe_extracted/AI批量生图工具_2.0.14.pyc"
    # decompile_pyc(pyc_path)
    
    # 方式2: 反编译整个目录
    extracted_dir = r"d:/github/salary/lazy_hack/exe_file/AI批量生图工具_2.0.14.exe_extracted"
    if os.path.exists(extracted_dir):
        decompile_all_pyc_in_dir(extracted_dir)
    else:
        print(f"[!] 目录不存在: {extracted_dir}")
        print(f"[!] 请先运行 1_extract_pyinstaller.py")
