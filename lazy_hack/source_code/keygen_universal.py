"""
AI批量生图工具 v2.0.14 - 通用注册机
基于逆向分析结果编写

使用方法:
1. 运行程序，选择机器码生成方式
2. 选择授权码生成算法
3. 测试生成的授权码是否有效
"""

import hashlib
import uuid
import base64
import platform
import subprocess
from datetime import datetime

class UniversalKeygen:
    """通用注册机"""
    
    def __init__(self):
        self.machine_code = None
        self.license_key = None
        self.salt_candidates = [
            "",  # 无盐值
            "AI_IMAGE_TOOL",
            "ai_batch_image",
            "license_key_salt",
            "machine_code_salt",
            "2024",
            "v2.0.14",
            "refactored",
        ]
    
    # ========== 机器码生成方法 ==========
    
    def get_mac_address(self):
        """方法1: 获取 MAC 地址"""
        mac = uuid.getnode()
        machine_code = str(mac)
        print(f"[+] MAC 地址: {mac}")
        print(f"[+] 机器码 (十进制): {machine_code}")
        return machine_code
    
    def get_mac_hex(self):
        """方法2: 获取 MAC 地址 (16进制)"""
        mac = uuid.getnode()
        machine_code = hex(mac)[2:].upper()
        print(f"[+] MAC 地址: {mac}")
        print(f"[+] 机器码 (16进制): {machine_code}")
        return machine_code
    
    def get_mac_formatted(self):
        """方法3: 获取格式化的 MAC 地址"""
        mac = uuid.getnode()
        mac_hex = hex(mac)[2:].zfill(12)
        machine_code = ':'.join(mac_hex[i:i+2] for i in range(0, 12, 2))
        print(f"[+] 机器码 (格式化): {machine_code}")
        return machine_code
    
    def get_uuid(self):
        """方法4: 生成 UUID"""
        machine_code = str(uuid.uuid4())
        print(f"[+] 机器码 (UUID): {machine_code}")
        return machine_code
    
    def get_windows_hwid(self):
        """方法5: Windows 硬件 ID (仅 Windows)"""
        if platform.system() != 'Windows':
            print("[!] 此方法仅支持 Windows")
            return None
        
        try:
            # CPU ID
            cpu = subprocess.check_output('wmic cpu get ProcessorId', shell=True).decode()
            cpu_id = cpu.split('\n')[1].strip()
            
            # 主板序列号
            board = subprocess.check_output('wmic baseboard get SerialNumber', shell=True).decode()
            board_id = board.split('\n')[1].strip()
            
            # 组合
            combined = f"{cpu_id}_{board_id}"
            machine_code = hashlib.md5(combined.encode()).hexdigest()
            
            print(f"[+] CPU ID: {cpu_id}")
            print(f"[+] Board Serial: {board_id}")
            print(f"[+] 机器码 (组合哈希): {machine_code}")
            return machine_code
        except Exception as e:
            print(f"[!] 获取失败: {e}")
            return None
    
    def get_mac_md5(self):
        """方法6: MAC 地址 MD5"""
        mac = uuid.getnode()
        machine_code = hashlib.md5(str(mac).encode()).hexdigest()
        print(f"[+] MAC: {mac}")
        print(f"[+] 机器码 (MD5): {machine_code}")
        return machine_code
    
    # ========== 授权码生成算法 ==========
    
    def gen_md5(self, machine_code, salt=""):
        """算法1: MD5(机器码 + 盐)"""
        data = f"{machine_code}{salt}"
        license_key = hashlib.md5(data.encode()).hexdigest()
        return license_key
    
    def gen_sha256(self, machine_code, salt=""):
        """算法2: SHA256(机器码 + 盐)"""
        data = f"{machine_code}{salt}"
        license_key = hashlib.sha256(data.encode()).hexdigest()
        return license_key
    
    def gen_sha1(self, machine_code, salt=""):
        """算法3: SHA1(机器码 + 盐)"""
        data = f"{machine_code}{salt}"
        license_key = hashlib.sha1(data.encode()).hexdigest()
        return license_key
    
    def gen_base64(self, machine_code):
        """算法4: Base64 编码"""
        license_key = base64.b64encode(machine_code.encode()).decode()
        return license_key
    
    def gen_reverse_md5(self, machine_code):
        """算法5: 反转 + MD5"""
        reversed_code = machine_code[::-1]
        license_key = hashlib.md5(reversed_code.encode()).hexdigest()
        return license_key
    
    def gen_double_md5(self, machine_code):
        """算法6: 双重 MD5"""
        first = hashlib.md5(machine_code.encode()).hexdigest()
        license_key = hashlib.md5(first.encode()).hexdigest()
        return license_key
    
    def gen_xor_md5(self, machine_code, key=0x5A):
        """算法7: XOR + MD5"""
        xored = ''.join(chr(ord(c) ^ key) for c in machine_code)
        license_key = hashlib.md5(xored.encode()).hexdigest()
        return license_key
    
    def gen_timestamp_md5(self, machine_code):
        """算法8: 机器码 + 时间戳的 MD5"""
        # 使用固定时间戳 (可能的发布日期)
        timestamp = "20241112"  # 或者其他日期
        data = f"{machine_code}{timestamp}"
        license_key = hashlib.md5(data.encode()).hexdigest()
        return license_key
    
    def gen_upper_md5(self, machine_code):
        """算法9: 大写 + MD5"""
        license_key = hashlib.md5(machine_code.upper().encode()).hexdigest()
        return license_key
    
    def gen_lower_md5(self, machine_code):
        """算法10: 小写 + MD5"""
        license_key = hashlib.md5(machine_code.lower().encode()).hexdigest()
        return license_key
    
    # ========== 批量生成 ==========
    
    def generate_all_combinations(self, machine_code):
        """生成所有可能的组合"""
        print("\n" + "="*80)
        print("批量生成所有可能的授权码")
        print("="*80)
        
        results = []
        
        # 算法列表
        algorithms = [
            ("MD5", self.gen_md5),
            ("SHA256", self.gen_sha256),
            ("SHA1", self.gen_sha1),
            ("Base64", self.gen_base64),
            ("Reverse+MD5", self.gen_reverse_md5),
            ("Double MD5", self.gen_double_md5),
            ("XOR+MD5", self.gen_xor_md5),
            ("Timestamp+MD5", self.gen_timestamp_md5),
            ("Upper+MD5", self.gen_upper_md5),
            ("Lower+MD5", self.gen_lower_md5),
        ]
        
        print(f"\n机器码: {machine_code}\n")
        
        for algo_name, algo_func in algorithms:
            # 无盐值
            try:
                if algo_name in ["Base64", "Reverse+MD5", "Double MD5", "XOR+MD5", "Timestamp+MD5", "Upper+MD5", "Lower+MD5"]:
                    license_key = algo_func(machine_code)
                    results.append((algo_name, "", license_key))
                    print(f"[{algo_name:20s}] {license_key}")
                else:
                    # 尝试所有盐值
                    for salt in self.salt_candidates:
                        license_key = algo_func(machine_code, salt)
                        salt_display = f"(salt:{salt})" if salt else "(no salt)"
                        results.append((algo_name, salt, license_key))
                        print(f"[{algo_name:20s}] {salt_display:25s} {license_key}")
            except Exception as e:
                print(f"[!] {algo_name} 失败: {e}")
        
        return results
    
    def save_to_file(self, machine_code, results, filename="license_keys.txt"):
        """保存到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("AI批量生图工具 v2.0.14 - 授权码生成结果\n")
            f.write("="*80 + "\n\n")
            f.write(f"机器码: {machine_code}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            for algo_name, salt, license_key in results:
                salt_display = f"(salt:{salt})" if salt else "(no salt)"
                f.write(f"[{algo_name:20s}] {salt_display:25s}\n")
                f.write(f"  {license_key}\n\n")
        
        print(f"\n[+] 结果已保存到: {filename}")
    
    # ========== 交互式界面 ==========
    
    def interactive(self):
        """交互式界面"""
        print("\n" + "="*80)
        print("AI批量生图工具 v2.0.14 - 通用注册机")
        print("="*80)
        
        # 1. 选择机器码生成方式
        print("\n[1] 选择机器码生成方式:")
        print("  1. MAC 地址 (十进制)")
        print("  2. MAC 地址 (十六进制)")
        print("  3. MAC 地址 (格式化 XX:XX:XX:XX:XX:XX)")
        print("  4. UUID")
        print("  5. Windows 硬件 ID (CPU+主板)")
        print("  6. MAC 地址 MD5")
        print("  7. 手动输入")
        
        choice = input("\n请选择 (1-7): ").strip()
        
        machine_code_methods = {
            '1': self.get_mac_address,
            '2': self.get_mac_hex,
            '3': self.get_mac_formatted,
            '4': self.get_uuid,
            '5': self.get_windows_hwid,
            '6': self.get_mac_md5,
        }
        
        if choice == '7':
            machine_code = input("\n请输入机器码: ").strip()
        elif choice in machine_code_methods:
            print(f"\n[*] 生成机器码...")
            machine_code = machine_code_methods[choice]()
        else:
            print("[!] 无效选择，使用默认方法 (MAC 十进制)")
            machine_code = self.get_mac_address()
        
        if not machine_code:
            print("[!] 机器码生成失败")
            return
        
        # 2. 选择生成模式
        print("\n[2] 选择生成模式:")
        print("  1. 单个算法")
        print("  2. 批量生成所有可能的组合")
        
        mode = input("\n请选择 (1-2): ").strip()
        
        if mode == '1':
            # 单个算法
            print("\n[3] 选择授权码生成算法:")
            print("  1. MD5")
            print("  2. SHA256")
            print("  3. SHA1")
            print("  4. Base64")
            print("  5. Reverse + MD5")
            print("  6. Double MD5")
            print("  7. XOR + MD5")
            print("  8. Timestamp + MD5")
            print("  9. Upper + MD5")
            print("  10. Lower + MD5")
            
            algo_choice = input("\n请选择 (1-10): ").strip()
            
            algorithms = {
                '1': ('MD5', self.gen_md5),
                '2': ('SHA256', self.gen_sha256),
                '3': ('SHA1', self.gen_sha1),
                '4': ('Base64', self.gen_base64),
                '5': ('Reverse+MD5', self.gen_reverse_md5),
                '6': ('Double MD5', self.gen_double_md5),
                '7': ('XOR+MD5', self.gen_xor_md5),
                '8': ('Timestamp+MD5', self.gen_timestamp_md5),
                '9': ('Upper+MD5', self.gen_upper_md5),
                '10': ('Lower+MD5', self.gen_lower_md5),
            }
            
            if algo_choice in algorithms:
                algo_name, algo_func = algorithms[algo_choice]
                
                # 是否使用盐值
                if algo_name in ['MD5', 'SHA256', 'SHA1']:
                    use_salt = input("\n是否使用盐值? (y/n): ").strip().lower()
                    if use_salt == 'y':
                        salt = input("请输入盐值 (直接回车表示无盐): ").strip()
                        license_key = algo_func(machine_code, salt)
                    else:
                        license_key = algo_func(machine_code)
                else:
                    license_key = algo_func(machine_code)
                
                print("\n" + "="*80)
                print("生成结果")
                print("="*80)
                print(f"\n机器码: {machine_code}")
                print(f"算法:   {algo_name}")
                print(f"授权码: {license_key}")
                print("\n" + "="*80)
                
                # 复制到剪贴板 (可选)
                try:
                    import pyperclip
                    pyperclip.copy(license_key)
                    print("[+] 授权码已复制到剪贴板")
                except:
                    pass
            else:
                print("[!] 无效选择")
        
        elif mode == '2':
            # 批量生成
            results = self.generate_all_combinations(machine_code)
            
            # 保存到文件
            save = input("\n是否保存到文件? (y/n): ").strip().lower()
            if save == 'y':
                filename = input("文件名 (默认: license_keys.txt): ").strip()
                if not filename:
                    filename = "license_keys.txt"
                self.save_to_file(machine_code, results, filename)
        else:
            print("[!] 无效选择")

def main():
    """主函数"""
    keygen = UniversalKeygen()
    
    try:
        keygen.interactive()
    except KeyboardInterrupt:
        print("\n\n[*] 用户中断")
    except Exception as e:
        print(f"\n[!] 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n\n按 Enter 键退出...")

if __name__ == "__main__":
    main()
