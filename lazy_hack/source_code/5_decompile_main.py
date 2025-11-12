"""
反编译主程序文件
使用多种工具尝试反编译 main_refactored.pyc
"""
import os
import subprocess
import sys

def try_decompile_with_uncompyle6(pyc_path, output_path):
    """尝试使用 uncompyle6"""
    print("[*] 尝试 uncompyle6...")
    try:
        cmd = f'uncompyle6 "{pyc_path}" > "{output_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            print(f"[+] uncompyle6 成功！输出: {output_path}")
            return True
        print(f"[!] uncompyle6 失败")
    except Exception as e:
        print(f"[!] uncompyle6 错误: {e}")
    return False

def try_decompile_with_decompyle3(pyc_path, output_path):
    """尝试使用 decompyle3"""
    print("[*] 尝试 decompyle3...")
    try:
        cmd = f'decompyle3 "{pyc_path}" > "{output_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            print(f"[+] decompyle3 成功！输出: {output_path}")
            return True
        print(f"[!] decompyle3 失败")
    except Exception as e:
        print(f"[!] decompyle3 错误: {e}")
    return False

def try_decompile_with_pycdc(pyc_path, output_path):
    """尝试使用 pycdc (需要单独下载)"""
    print("[*] 尝试 pycdc...")
    try:
        # pycdc 需要从 GitHub 下载编译好的版本
        # https://github.com/zrax/pycdc/releases
        cmd = f'pycdc "{pyc_path}" > "{output_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            print(f"[+] pycdc 成功！输出: {output_path}")
            return True
        print(f"[!] pycdc 失败或未安装")
    except Exception as e:
        print(f"[!] pycdc 错误: {e}")
    return False

def analyze_pyc_bytecode(pyc_path):
    """分析字节码 - 如果反编译失败"""
    print("\n[*] 分析字节码...")
    try:
        import dis
        import marshal
        
        with open(pyc_path, 'rb') as f:
            # 跳过 magic number 和 timestamp (Python 3.6+)
            f.read(16)  # Python 3.7+ 使用 16 字节头部
            code = marshal.load(f)
        
        output_path = pyc_path.replace('.pyc', '_bytecode_analysis.txt')
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write("=" * 80 + "\n")
            out.write("字节码反汇编分析\n")
            out.write("=" * 80 + "\n\n")
            
            # 获取反汇编内容
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                dis.dis(code)
            
            out.write(f.getvalue())
            
            out.write("\n\n" + "=" * 80 + "\n")
            out.write("代码对象信息\n")
            out.write("=" * 80 + "\n")
            out.write(f"参数数量: {code.co_argcount}\n")
            out.write(f"局部变量: {code.co_nlocals}\n")
            out.write(f"栈大小: {code.co_stacksize}\n")
            out.write(f"常量: {code.co_consts}\n")
            out.write(f"变量名: {code.co_varnames}\n")
            out.write(f"名称: {code.co_names}\n")
        
        print(f"[+] 字节码分析已保存到: {output_path}")
        return output_path
    except Exception as e:
        print(f"[!] 字节码分析失败: {e}")
        return None

def extract_strings_from_pyc(pyc_path):
    """从 pyc 文件提取字符串常量"""
    print("\n[*] 提取字符串常量...")
    try:
        import marshal
        
        with open(pyc_path, 'rb') as f:
            f.read(16)  # 跳过头部
            code = marshal.load(f)
        
        strings = []
        
        def extract_from_code(c):
            if hasattr(c, 'co_consts'):
                for const in c.co_consts:
                    if isinstance(const, str):
                        strings.append(const)
                    elif hasattr(const, 'co_consts'):
                        extract_from_code(const)
        
        extract_from_code(code)
        
        output_path = pyc_path.replace('.pyc', '_strings.txt')
        with open(output_path, 'w', encoding='utf-8', errors='ignore') as out:
            out.write("提取的字符串常量\n")
            out.write("=" * 80 + "\n\n")
            for s in strings:
                if len(s) > 2 and len(s) < 1000:  # 过滤太短和太长的
                    out.write(f"{s}\n")
        
        print(f"[+] 字符串提取完成: {output_path}")
        
        # 查找授权相关的字符串
        license_keywords = ['license', 'key', 'machine', 'code', '授权', '机器码', '验证', 'verify', 'check']
        license_strings = [s for s in strings if any(kw in s.lower() for kw in license_keywords)]
        
        if license_strings:
            print("\n[!] 发现授权相关字符串:")
            for s in license_strings[:20]:  # 只显示前20个
                print(f"    {s}")
        
        return strings
    except Exception as e:
        print(f"[!] 字符串提取失败: {e}")
        return []

def main():
    print("=" * 80)
    print("反编译 main_refactored.pyc")
    print("=" * 80)
    
    pyc_path = r"d:\github\salary\lazy_hack\source_code\AI批量生图工具_2.0.14.exe_extracted\main_refactored.pyc"
    
    if not os.path.exists(pyc_path):
        print(f"[!] 文件不存在: {pyc_path}")
        return
    
    # 尝试各种反编译方法
    output_path = pyc_path.replace('.pyc', '_decompiled.py')
    
    success = False
    success = success or try_decompile_with_uncompyle6(pyc_path, output_path)
    success = success or try_decompile_with_decompyle3(pyc_path, output_path)
    success = success or try_decompile_with_pycdc(pyc_path, output_path)
    
    if not success:
        print("\n[!] 所有反编译工具都失败了")
        print("[*] 使用备用方法: 字节码分析和字符串提取")
        
        # 字节码分析
        analyze_pyc_bytecode(pyc_path)
        
        # 提取字符串
        strings = extract_strings_from_pyc(pyc_path)
        
        print("\n[*] 建议:")
        print("    1. 下载 pycdc: https://github.com/zrax/pycdc/releases")
        print("    2. 使用 Python 3.12 环境运行反编译")
        print("    3. 查看字节码分析文件了解程序逻辑")
        print("    4. 查看字符串提取文件寻找授权相关信息")
    else:
        print(f"\n[+] 反编译成功！查看文件: {output_path}")
        
        # 即使成功也提取字符串
        extract_strings_from_pyc(pyc_path)

if __name__ == "__main__":
    main()
