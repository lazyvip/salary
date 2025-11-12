"""
分析 main_refactored.pyc 字节码
找到授权验证逻辑
"""
import dis
import marshal
import types

print("="*80)
print("分析 main_refactored.pyc 字节码")
print("="*80)

pyc_file = "AI批量生图工具_2.0.14.exe_extracted/main_refactored.pyc"

# 读取 .pyc 文件
with open(pyc_file, 'rb') as f:
    # 跳过头部 (16 字节在 Python 3.7+)
    magic = f.read(4)
    print(f"\n[*] Magic number: {magic.hex()}")
    
    _ = f.read(4)  # Timestamp
    _ = f.read(4)  # Size
    _ = f.read(4)  # Additional field (Python 3.7+)
    
    # 加载代码对象
    try:
        code = marshal.load(f)
        print(f"[+] 成功加载代码对象")
        print(f"[*] 文件名: {code.co_filename}")
        print(f"[*] 名称: {code.co_name}")
        print(f"[*] 常量数量: {len(code.co_consts)}")
        print(f"[*] 变量名数量: {len(code.co_names)}")
        
        print("\n" + "="*80)
        print("搜索关键常量")
        print("="*80)
        
        # 搜索关键字符串
        keywords = ['卡密', '无效', 'error', 'status', 'message', 'license', 'auth', 'machine_code']
        
        found_consts = {}
        for i, const in enumerate(code.co_consts):
            if isinstance(const, str):
                for keyword in keywords:
                    if keyword in const:
                        if keyword not in found_consts:
                            found_consts[keyword] = []
                        found_consts[keyword].append((i, const))
        
        for keyword, consts in found_consts.items():
            print(f"\n[*] 关键词 '{keyword}':")
            for idx, const in consts[:5]:  # 只显示前5个
                print(f"    [{idx}] {const}")
        
        print("\n" + "="*80)
        print("搜索关键变量名")
        print("="*80)
        
        found_names = []
        for i, name in enumerate(code.co_names):
            for keyword in keywords:
                if keyword in name.lower():
                    found_names.append((i, name))
                    break
        
        for idx, name in found_names:
            print(f"  [{idx}] {name}")
        
        print("\n" + "="*80)
        print("分析嵌套的代码对象")
        print("="*80)
        
        # 查找嵌套的代码对象（函数定义）
        for i, const in enumerate(code.co_consts):
            if isinstance(const, types.CodeType):
                # 检查是否包含授权相关逻辑
                const_strs = [c for c in const.co_consts if isinstance(c, str)]
                const_names = list(const.co_names)
                
                # 检查是否包含关键字
                has_auth = any(kw in str(const_strs).lower() or kw in str(const_names).lower() 
                              for kw in ['卡密', 'license', 'auth', '无效'])
                
                if has_auth:
                    print(f"\n[*] 找到可疑函数: {const.co_name}")
                    print(f"    文件名: {const.co_filename}")
                    print(f"    行号: {const.co_firstlineno}")
                    print(f"    参数: {const.co_varnames[:const.co_argcount]}")
                    
                    # 显示常量
                    print(f"    常量:")
                    for c in const_strs[:10]:
                        if c and len(c) < 100:
                            print(f"      - {c}")
                    
                    # 显示变量名
                    print(f"    变量名:")
                    for name in const_names[:10]:
                        print(f"      - {name}")
                    
                    # 尝试反汇编
                    print(f"\n    字节码:")
                    try:
                        import io
                        import sys
                        old_stdout = sys.stdout
                        sys.stdout = buffer = io.StringIO()
                        dis.dis(const)
                        output = buffer.getvalue()
                        sys.stdout = old_stdout
                        
                        # 只显示前50行
                        lines = output.split('\n')[:50]
                        for line in lines:
                            print(f"      {line}")
                    except Exception as e:
                        print(f"      [!] 反汇编失败: {e}")
        
        print("\n" + "="*80)
        print("提取所有字符串常量")
        print("="*80)
        
        # 递归提取所有字符串
        def extract_strings(code_obj, depth=0):
            strings = []
            for const in code_obj.co_consts:
                if isinstance(const, str):
                    strings.append(const)
                elif isinstance(const, types.CodeType):
                    strings.extend(extract_strings(const, depth+1))
            return strings
        
        all_strings = extract_strings(code)
        
        # 查找包含授权相关的字符串
        auth_strings = []
        for s in all_strings:
            if any(kw in s for kw in ['卡密', 'license', 'auth', '机器码', 'error', 'status']):
                if len(s) < 200:  # 忽略太长的字符串
                    auth_strings.append(s)
        
        print(f"\n[*] 找到 {len(auth_strings)} 个授权相关字符串:")
        for s in set(auth_strings[:20]):  # 去重并只显示前20个
            print(f"  - {s}")
        
        # 保存所有字符串到文件
        with open("all_strings.txt", 'w', encoding='utf-8') as out:
            for s in sorted(set(all_strings)):
                if s and len(s) > 0:
                    out.write(f"{s}\n")
        
        print(f"\n[+] 所有字符串已保存到: all_strings.txt")
        
    except Exception as e:
        print(f"[!] 加载失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("分析完成")
print("="*80)
