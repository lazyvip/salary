"""
步骤3: 分析授权机制
查找机器码、授权码相关的代码
"""
import os
import re
import glob

def search_in_file(file_path, patterns):
    """
    在文件中搜索指定的模式
    
    Args:
        file_path: 文件路径
        patterns: 要搜索的正则表达式模式列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        matches = {}
        for pattern_name, pattern in patterns.items():
            found = re.findall(pattern, content, re.IGNORECASE)
            if found:
                matches[pattern_name] = found
        
        return matches
    except Exception as e:
        print(f"[!] 读取文件错误 {file_path}: {e}")
        return {}

def analyze_license_system(source_dir):
    """
    分析授权系统
    
    Args:
        source_dir: 反编译后的源代码目录
    """
    print("[*] 开始分析授权系统...")
    
    # 定义要搜索的模式
    patterns = {
        "机器码相关": r"(machine.*code|机器码|hwid|uuid|mac.*address|get.*machine)",
        "授权码相关": r"(license.*key|授权码|activation.*code|serial|key.*check|验证)",
        "加密解密": r"(encrypt|decrypt|md5|sha|base64|aes|rsa|加密|解密)",
        "验证函数": r"(def\s+.*verify|def\s+.*check|def\s+.*validate|def\s+.*auth)",
        "硬件信息": r"(uuid\.getnode|uuid\.UUID|subprocess.*wmic|platform\.)",
    }
    
    # 搜索所有 Python 文件
    py_files = glob.glob(os.path.join(source_dir, "**/*.py"), recursive=True)
    
    print(f"[*] 找到 {len(py_files)} 个 Python 文件")
    
    results = {}
    for py_file in py_files:
        matches = search_in_file(py_file, patterns)
        if matches:
            results[py_file] = matches
    
    # 输出结果
    print("\n" + "="*80)
    print("授权系统分析结果")
    print("="*80)
    
    for file_path, matches in results.items():
        print(f"\n文件: {os.path.relpath(file_path, source_dir)}")
        print("-" * 80)
        for pattern_name, found_items in matches.items():
            print(f"  [{pattern_name}]")
            for item in set(found_items[:5]):  # 只显示前5个不重复的
                print(f"    - {item}")
    
    # 保存分析结果
    report_path = os.path.join(source_dir, "license_analysis_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("授权系统分析报告\n")
        f.write("="*80 + "\n\n")
        for file_path, matches in results.items():
            f.write(f"\n文件: {os.path.relpath(file_path, source_dir)}\n")
            f.write("-" * 80 + "\n")
            for pattern_name, found_items in matches.items():
                f.write(f"  [{pattern_name}]\n")
                for item in set(found_items):
                    f.write(f"    - {item}\n")
    
    print(f"\n[+] 分析报告已保存到: {report_path}")
    
    return results

def extract_license_code(source_dir):
    """
    尝试提取授权相关的完整代码
    """
    print("\n[*] 提取授权相关代码...")
    
    py_files = glob.glob(os.path.join(source_dir, "**/*.py"), recursive=True)
    license_code = []
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 查找包含授权相关的函数定义
            if any(keyword in content.lower() for keyword in 
                   ['license', 'machine', 'verify', 'check', '授权', '机器码', '验证']):
                license_code.append((py_file, content))
        except Exception as e:
            continue
    
    # 保存提取的代码
    output_path = os.path.join(source_dir, "license_related_code.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        for file_path, content in license_code:
            f.write(f"\n{'='*80}\n")
            f.write(f"文件: {os.path.relpath(file_path, source_dir)}\n")
            f.write(f"{'='*80}\n")
            f.write(content)
            f.write("\n\n")
    
    print(f"[+] 授权相关代码已保存到: {output_path}")

if __name__ == "__main__":
    decompiled_dir = r"d:/github/salary/lazy_hack/exe_file/AI批量生图工具_2.0.14.exe_extracted/decompiled"
    
    if os.path.exists(decompiled_dir):
        analyze_license_system(decompiled_dir)
        extract_license_code(decompiled_dir)
    else:
        print(f"[!] 目录不存在: {decompiled_dir}")
        print(f"[!] 请先运行前面的步骤")
