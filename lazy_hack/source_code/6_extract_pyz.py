"""
提取 PYZ.pyz 压缩包中的所有 Python 模块
"""
import os
import sys
import marshal
import zlib
import struct

def extract_pyz(pyz_path, output_dir):
    """
    提取 PYZ.pyz 文件
    
    Args:
        pyz_path: PYZ 文件路径
        output_dir: 输出目录
    """
    print(f"[*] 开始提取 PYZ: {pyz_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(pyz_path, 'rb') as f:
            # 读取 PYZ 头部
            magic = f.read(4)
            print(f"[*] Magic: {magic}")
            
            # 读取 Python 对象
            try:
                pyz_data = marshal.load(f)
            except:
                f.seek(0)
                # 跳过一些字节
                f.read(8)
                try:
                    pyz_data = marshal.load(f)
                except Exception as e:
                    print(f"[!] 无法读取 marshal 数据: {e}")
                    return False
            
            if isinstance(pyz_data, dict):
                print(f"[+] 找到 {len(pyz_data)} 个模块")
                
                for module_name, (ispkg, pos, length) in pyz_data.items():
                    try:
                        # 保存位置
                        current_pos = f.tell()
                        
                        # 读取模块数据
                        f.seek(pos)
                        module_data = f.read(length)
                        
                        # 解压缩
                        try:
                            module_data = zlib.decompress(module_data)
                        except:
                            pass  # 可能没有压缩
                        
                        # 保存到文件
                        if '/' in module_name or '\\' in module_name:
                            module_path = module_name.replace('/', os.sep).replace('\\', os.sep)
                        else:
                            module_path = module_name.replace('.', os.sep)
                        
                        output_file = os.path.join(output_dir, module_path + '.pyc')
                        os.makedirs(os.path.dirname(output_file), exist_ok=True)
                        
                        with open(output_file, 'wb') as out:
                            # 写入 pyc 头部 (Python 3.7+)
                            out.write(b'\x55\x0d\x0d\x0a')  # magic number
                            out.write(b'\x00' * 12)  # flags + timestamp
                            out.write(module_data)
                        
                        print(f"[+] 提取: {module_name} -> {output_file}")
                        
                        # 恢复位置
                        f.seek(current_pos)
                    except Exception as e:
                        print(f"[!] 提取失败 {module_name}: {e}")
                        continue
                
                print(f"\n[+] 提取完成！输出目录: {output_dir}")
                return True
            else:
                print(f"[!] PYZ 数据格式不正确: {type(pyz_data)}")
                return False
    except Exception as e:
        print(f"[!] 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_pyz_alternative(pyz_path, output_dir):
    """
    备用方法：手动解析 PYZ
    """
    print(f"\n[*] 尝试备用方法...")
    
    try:
        # 使用 PyInstaller 的工具
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        
        # 直接读取整个文件
        with open(pyz_path, 'rb') as f:
            data = f.read()
        
        # 查找所有可能的 marshal 对象
        print(f"[*] 文件大小: {len(data)} 字节")
        print(f"[*] 尝试查找嵌入的 Python 模块...")
        
        # 保存原始文件以便分析
        output_file = os.path.join(output_dir, "../PYZ_raw_dump.bin")
        with open(output_file, 'wb') as out:
            out.write(data)
        
        print(f"[*] 原始数据已保存: {output_file}")
        print(f"[*] 请使用专门的 PYZ 提取工具")
        
        return False
    except Exception as e:
        print(f"[!] 备用方法失败: {e}")
        return False

if __name__ == "__main__":
    pyz_path = r"d:\github\salary\lazy_hack\source_code\AI批量生图工具_2.0.14.exe_extracted\PYZ.pyz"
    output_dir = r"d:\github\salary\lazy_hack\source_code\AI批量生图工具_2.0.14.exe_extracted\PYZ_extracted"
    
    success = extract_pyz(pyz_path, output_dir)
    
    if not success:
        extract_pyz_alternative(pyz_path, output_dir)
