"""
步骤4: 注册机/破解工具模板
根据逆向分析的结果，这里提供一个通用的模板
需要根据实际的授权算法进行修改
"""
import hashlib
import uuid
import platform
import subprocess
import base64

class LicenseCracker:
    """授权破解工具"""
    
    def __init__(self):
        self.machine_code = None
        self.license_key = None
    
    def get_machine_code_method1(self):
        """
        方法1: 使用 MAC 地址作为机器码
        这是最常见的方法
        """
        mac = uuid.getnode()
        machine_code = str(mac)
        print(f"[*] 机器码 (MAC): {machine_code}")
        return machine_code
    
    def get_machine_code_method2(self):
        """
        方法2: 使用多种硬件信息组合
        """
        try:
            # CPU ID (Windows)
            if platform.system() == 'Windows':
                result = subprocess.check_output('wmic cpu get ProcessorId', shell=True)
                cpu_id = result.decode().split('\n')[1].strip()
            else:
                cpu_id = "unknown"
            
            # MAC 地址
            mac = uuid.getnode()
            
            # 组合信息
            combined = f"{cpu_id}-{mac}"
            machine_code = hashlib.md5(combined.encode()).hexdigest()
            
            print(f"[*] 机器码 (组合): {machine_code}")
            return machine_code
        except Exception as e:
            print(f"[!] 获取机器码失败: {e}")
            return None
    
    def get_machine_code_method3(self):
        """
        方法3: UUID
        """
        machine_code = str(uuid.uuid4())
        print(f"[*] 机器码 (UUID): {machine_code}")
        return machine_code
    
    def generate_license_algorithm1(self, machine_code):
        """
        算法1: 简单 MD5 哈希
        授权码 = MD5(机器码)
        """
        license_key = hashlib.md5(machine_code.encode()).hexdigest()
        return license_key
    
    def generate_license_algorithm2(self, machine_code):
        """
        算法2: MD5 + Salt
        授权码 = MD5(机器码 + 固定盐值)
        """
        salt = "YOUR_SALT_HERE"  # 需要从源码中找到
        license_key = hashlib.md5(f"{machine_code}{salt}".encode()).hexdigest()
        return license_key
    
    def generate_license_algorithm3(self, machine_code):
        """
        算法3: SHA256
        """
        license_key = hashlib.sha256(machine_code.encode()).hexdigest()
        return license_key
    
    def generate_license_algorithm4(self, machine_code):
        """
        算法4: Base64 编码
        """
        license_key = base64.b64encode(machine_code.encode()).decode()
        return license_key
    
    def generate_license_algorithm5(self, machine_code):
        """
        算法5: 自定义算法示例
        反转字符串 + MD5
        """
        reversed_code = machine_code[::-1]
        license_key = hashlib.md5(reversed_code.encode()).hexdigest()
        return license_key
    
    def verify_license(self, machine_code, license_key, algorithm_func):
        """
        验证授权码是否正确
        
        Args:
            machine_code: 机器码
            license_key: 要验证的授权码
            algorithm_func: 生成算法函数
        """
        generated_key = algorithm_func(machine_code)
        is_valid = (generated_key == license_key)
        
        print(f"\n[*] 验证结果:")
        print(f"    机器码: {machine_code}")
        print(f"    生成的授权码: {generated_key}")
        print(f"    提供的授权码: {license_key}")
        print(f"    验证状态: {'✓ 有效' if is_valid else '✗ 无效'}")
        
        return is_valid
    
    def crack_interactive(self):
        """
        交互式破解工具
        """
        print("="*80)
        print("AI批量生图工具 - 注册机")
        print("="*80)
        
        # 获取机器码
        print("\n[1] 选择机器码获取方法:")
        print("    1. MAC 地址")
        print("    2. CPU+MAC 组合")
        print("    3. UUID")
        print("    4. 手动输入")
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == '1':
            machine_code = self.get_machine_code_method1()
        elif choice == '2':
            machine_code = self.get_machine_code_method2()
        elif choice == '3':
            machine_code = self.get_machine_code_method3()
        elif choice == '4':
            machine_code = input("请输入机器码: ").strip()
        else:
            print("[!] 无效选择")
            return
        
        # 选择算法
        print("\n[2] 选择授权码生成算法:")
        print("    1. MD5(机器码)")
        print("    2. MD5(机器码 + Salt)")
        print("    3. SHA256(机器码)")
        print("    4. Base64(机器码)")
        print("    5. 反转 + MD5")
        print("    6. 尝试所有算法")
        
        algo_choice = input("\n请选择 (1-6): ").strip()
        
        algorithms = {
            '1': self.generate_license_algorithm1,
            '2': self.generate_license_algorithm2,
            '3': self.generate_license_algorithm3,
            '4': self.generate_license_algorithm4,
            '5': self.generate_license_algorithm5,
        }
        
        print("\n" + "="*80)
        print("生成的授权码:")
        print("="*80)
        
        if algo_choice == '6':
            # 尝试所有算法
            for name, func in algorithms.items():
                license_key = func(machine_code)
                print(f"\n算法 {name}: {license_key}")
        elif algo_choice in algorithms:
            license_key = algorithms[algo_choice](machine_code)
            print(f"\n授权码: {license_key}")
        else:
            print("[!] 无效选择")
    
    def batch_generate(self, machine_codes, output_file="licenses.txt"):
        """
        批量生成授权码
        
        Args:
            machine_codes: 机器码列表
            output_file: 输出文件
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("机器码 -> 授权码映射表\n")
            f.write("="*80 + "\n\n")
            
            for mc in machine_codes:
                # 使用所有算法生成
                f.write(f"机器码: {mc}\n")
                f.write(f"  算法1 (MD5): {self.generate_license_algorithm1(mc)}\n")
                f.write(f"  算法2 (MD5+Salt): {self.generate_license_algorithm2(mc)}\n")
                f.write(f"  算法3 (SHA256): {self.generate_license_algorithm3(mc)}\n")
                f.write(f"  算法4 (Base64): {self.generate_license_algorithm4(mc)}\n")
                f.write(f"  算法5 (反转+MD5): {self.generate_license_algorithm5(mc)}\n")
                f.write("\n")
        
        print(f"[+] 批量生成完成，已保存到: {output_file}")

def main():
    """主函数"""
    cracker = LicenseCracker()
    
    print("""
    使用说明:
    1. 这是一个通用的注册机模板
    2. 需要根据实际逆向分析的结果修改算法
    3. 重点关注源码中的:
       - 机器码获取方式
       - 授权码生成算法
       - 验证逻辑
    """)
    
    cracker.crack_interactive()

if __name__ == "__main__":
    main()
