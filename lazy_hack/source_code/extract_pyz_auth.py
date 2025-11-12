"""
从 PYZ.pyz 中提取 auth 相关模块
"""
import os
import sys
import marshal

# 读取 PYZ.pyz 文件
pyz_file = "AI批量生图工具_2.0.14.exe_extracted/PYZ.pyz"

print("="*80)
print("从 PYZ.pyz 提取 auth 模块")
print("="*80)

# PYZ 文件格式:
# - 前4字节: 'PYZ\0'
# - 然后是 marshal 序列化的字典

try:
    with open(pyz_file, 'rb') as f:
        # 跳过头部
        magic = f.read(4)
        print(f"\n[*] Magic: {magic}")
        
        # 读取目录
        try:
            toc = marshal.load(f)
            print(f"[+] 成功加载 TOC")
            print(f"[*] 模块总数: {len(toc)}")
            
            # 查找 auth 相关模块
            print("\n[*] 搜索 auth 相关模块...")
            
            auth_modules = []
            for name in toc:
                if 'auth' in name.lower() or 'license' in name.lower() or 'check' in name.lower():
                    auth_modules.append(name)
                    print(f"  ✓ 找到: {name}")
            
            if not auth_modules:
                print("\n[!] 未找到 auth 模块")
                print("[*] 可能的原因:")
                print("  1. auth 逻辑在 main_refactored.pyc 中")
                print("  2. auth 逻辑被混淆或加密")
                print("  3. 使用了其他名称")
            else:
                # 提取 auth 模块
                for module_name in auth_modules:
                    print(f"\n[*] 提取模块: {module_name}")
                    
                    # 获取模块数据
                    is_pkg, pos, length = toc[module_name]
                    f.seek(pos)
                    data = f.read(length)
                    
                    # 保存为 .pyc
                    output_file = f"extracted_{module_name}.pyc"
                    with open(output_file, 'wb') as out:
                        # 写入 .pyc 头部 (Python 3.12)
                        out.write(b'\x6f\r\r\n')  # Magic number
                        out.write(b'\x00\x00\x00\x00')  # Timestamp
                        out.write(b'\x00\x00\x00\x00')  # Size
                        out.write(data)
                    
                    print(f"[+] 已保存: {output_file}")
                    
        except Exception as e:
            print(f"[!] 读取 TOC 失败: {e}")
            print("[*] 尝试直接搜索字符串...")
            
            # 回到文件开头
            f.seek(0)
            content = f.read()
            
            # 搜索 "卡密无效" 附近的代码
            search_bytes = "卡密无效".encode('utf-8')
            pos = content.find(search_bytes)
            
            if pos != -1:
                print(f"\n[+] 找到 '卡密无效' 位置: {pos}")
                
                # 提取附近的数据
                start = max(0, pos - 500)
                end = min(len(content), pos + 500)
                context = content[start:end]
                
                # 保存上下文
                with open("auth_context.bin", 'wb') as out:
                    out.write(context)
                
                print(f"[+] 已保存上下文: auth_context.bin")
                
                # 尝试查找可读字符串
                print("\n[*] 附近的字符串:")
                for i in range(max(0, pos - 200), min(len(content), pos + 200)):
                    try:
                        # 尝试解码
                        snippet = content[i:i+50]
                        decoded = snippet.decode('utf-8', errors='ignore')
                        if len(decoded) > 10 and decoded.isprintable():
                            print(f"  {decoded[:50]}")
                    except:
                        pass
            else:
                print("[!] 未找到 '卡密无效' 字符串")

except Exception as e:
    print(f"[!] 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("分析 main_refactored.pyc")
print("="*80)

# 分析主程序
main_file = "AI批量生图工具_2.0.14.exe_extracted/main_refactored.pyc"
if os.path.exists(main_file):
    with open(main_file, 'rb') as f:
        content = f.read()
        
        # 搜索关键字符串
        keywords = [b"auth", b"license", b"\xe5\x8d\xa1\xe5\xaf\x86", b"machine_code"]
        
        print("\n[*] 在 main_refactored.pyc 中搜索关键字:")
        for keyword in keywords:
            count = content.count(keyword)
            if count > 0:
                print(f"  ✓ '{keyword.decode('utf-8', errors='ignore')}' 出现 {count} 次")
                
                # 查找位置
                pos = 0
                positions = []
                while True:
                    pos = content.find(keyword, pos)
                    if pos == -1:
                        break
                    positions.append(pos)
                    pos += 1
                
                if positions:
                    print(f"    位置: {positions[:5]}")  # 只显示前5个

print("\n" + "="*80)
print("结论")
print("="*80)
print("\n授权验证逻辑最可能在:")
print("  1. main_refactored.pyc 主程序中")
print("  2. 或者通过 requests/urllib 调用外部 API")
print("\n下一步:")
print("  1. 反编译 main_refactored.pyc")
print("  2. 搜索 '卡密无效' 附近的代码")
print("  3. 找到验证函数")
