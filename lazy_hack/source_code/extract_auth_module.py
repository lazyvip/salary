"""
从 PYZ.pyz 提取 auth.license_check 模块
"""
import struct
import marshal
import zlib
import os

pyz_file = "AI批量生图工具_2.0.14.exe_extracted/PYZ.pyz"

print("="*80)
print("提取 auth.license_check 模块")
print("="*80)

with open(pyz_file, 'rb') as f:
    # 读取头部
    magic = f.read(4)
    print(f"\n[*] Magic: {magic}")
    
    if magic != b'PYZ\x00':
        print("[!] 不是有效的 PYZ 文件")
        exit(1)
    
    # 读取 PKG 索引的位置
    pkg_start = f.tell()
    
    # 尝试读取TOC
    # PYZ 格式: 'PYZ\0' + TOC位置(int) + TOC
    toc_pos_data = f.read(4)
    
    if len(toc_pos_data) == 4:
        toc_pos = struct.unpack('!i', toc_pos_data)[0]
        print(f"[*] TOC位置: {toc_pos}")
        
        # 读取TOC
        f.seek(toc_pos)
        toc_data = f.read()
        
        try:
            toc = marshal.loads(toc_data)
            print(f"[+] 成功加载TOC")
            print(f"[*] 模块数量: {len(toc)}")
            
            # 列出所有模块
            print("\n[*] 所有模块:")
            for name in sorted(toc.keys())[:30]:  # 只显示前30个
                print(f"  - {name}")
            
            # 查找 auth 相关模块
            print("\n[*] auth 相关模块:")
            auth_modules = [name for name in toc.keys() if 'auth' in name.lower() or 'license' in name.lower()]
            
            for name in auth_modules:
                print(f"  ✓ {name}")
            
            # 提取模块
            for module_name in auth_modules:
                print(f"\n[*] 提取模块: {module_name}")
                
                is_pkg, pos, length = toc[module_name]
                
                print(f"    是否包: {is_pkg}")
                print(f"    位置: {pos}")
                print(f"    长度: {length}")
                
                # 读取数据
                f.seek(pos)
                data = f.read(length)
                
                # 尝试解压
                try:
                    decompressed = zlib.decompress(data)
                    print(f"    解压后大小: {len(decompressed)}")
                    
                    # 保存为 .pyc
                    output_file = f"extracted_{module_name.replace('.', '_')}.pyc"
                    with open(output_file, 'wb') as out:
                        # Python 3.12 magic number
                        out.write(b'\xcb\x0d\x0d\x0a')  # Magic
                        out.write(b'\x00\x00\x00\x00')  # Flags
                        out.write(b'\x00\x00\x00\x00')  # Timestamp
                        out.write(b'\x00\x00\x00\x00')  # Size
                        out.write(decompressed)
                    
                    print(f"    [+] 已保存: {output_file}")
                    
                except Exception as e:
                    print(f"    [!] 解压失败: {e}")
                    # 直接保存原始数据
                    output_file = f"extracted_{module_name.replace('.', '_')}.bin"
                    with open(output_file, 'wb') as out:
                        out.write(data)
                    print(f"    [+] 已保存原始数据: {output_file}")
        
        except Exception as e:
            print(f"[!] 解析TOC失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("[!] 无法读取TOC位置")
        
        # 尝试直接搜索
        print("\n[*] 尝试直接搜索模块名...")
        f.seek(0)
        content = f.read()
        
        # 搜索模块名
        search_names = [b'auth.license_check', b'auth.license_manager', b'license_check']
        
        for name in search_names:
            pos = content.find(name)
            if pos != -1:
                print(f"  ✓ 找到 '{name.decode()}' 在位置: {pos}")

print("\n" + "="*80)
print("提取完成")
print("="*80)
