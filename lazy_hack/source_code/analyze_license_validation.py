"""
分析本地授权验证逻辑
从提取的字符串中查找验证相关的代码
"""
import os
import re

def analyze_validation_logic():
    """分析验证逻辑"""
    
    print("="*80)
    print("分析本地授权验证逻辑")
    print("="*80)
    
    # 读取字符串文件
    strings_file = "AI批量生图工具_2.0.14.exe_extracted/main_refactored_strings.txt"
    
    if not os.path.exists(strings_file):
        print(f"[!] 文件不存在: {strings_file}")
        return
    
    with open(strings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找关键信息
    print("\n[*] 搜索授权相关字符串...")
    
    keywords = [
        '卡密', '无效', 'error', 'status', 'message',
        '验证', '授权码', '机器码', 'license', 'key'
    ]
    
    for keyword in keywords:
        if keyword in content:
            print(f"  ✓ 找到关键词: {keyword}")
    
    # 从错误信息推断
    print("\n" + "="*80)
    print("根据错误信息推断:")
    print("="*80)
    
    print("\n错误信息: {\"message\":\"卡密无效\",\"status\":\"error\"}")
    print("\n这说明:")
    print("  1. 软件有本地验证逻辑")
    print("  2. 验证失败返回 JSON 格式")
    print("  3. '卡密' 可能是授权码的别称")
    
    # 生成新的授权码候选
    print("\n" + "="*80)
    print("重新分析机器码和授权码关系")
    print("="*80)
    
    machine_code = "8ee8d931c26f457bac19512cde21c8e3"
    
    print(f"\n机器码: {machine_code}")
    print("\n注意到机器码本身就是 MD5 格式 (32位16进制)")
    print("这可能意味着:")
    print("  1. 机器码 = MD5(真实硬件ID)")
    print("  2. 授权码可能需要基于这个 MD5 机器码再次计算")
    
    import hashlib
    
    # 尝试不同的组合
    print("\n[*] 生成新的授权码候选...")
    
    candidates = []
    
    # 1. 直接使用机器码（可能授权码 = 机器码）
    candidates.append(("机器码本身", machine_code))
    
    # 2. 机器码转大写
    candidates.append(("机器码大写", machine_code.upper()))
    
    # 3. 某个固定值
    candidates.append(("固定值1", "admin"))
    candidates.append(("固定值2", "123456"))
    candidates.append(("固定值3", "888888"))
    
    # 4. 机器码的某种变换
    # 取前16位
    candidates.append(("机器码前16位", machine_code[:16]))
    
    # 取后16位  
    candidates.append(("机器码后16位", machine_code[16:]))
    
    # 5. 基于机器码的特殊计算
    # SHA256(机器码) 的前32位
    sha256_mc = hashlib.sha256(machine_code.encode()).hexdigest()[:32]
    candidates.append(("SHA256(机器码)前32", sha256_mc))
    
    # 6. 反转机器码
    candidates.append(("机器码反转", machine_code[::-1]))
    
    # 7. 机器码 XOR 某个值
    def xor_string(s, key=0x5A):
        result = ""
        for c in s:
            result += format(ord(c) ^ key, '02x')
        return result
    
    candidates.append(("机器码XOR", xor_string(machine_code)))
    
    # 8. 时间戳相关
    candidates.append(("机器码+2024", hashlib.md5(f"{machine_code}2024".encode()).hexdigest()))
    candidates.append(("机器码+20241112", hashlib.md5(f"{machine_code}20241112".encode()).hexdigest()))
    
    # 9. 特殊格式
    # 带破折号
    formatted = f"{machine_code[:8]}-{machine_code[8:16]}-{machine_code[16:24]}-{machine_code[24:]}"
    candidates.append(("格式化(破折号)", formatted))
    
    # 10. Base64
    import base64
    b64 = base64.b64encode(machine_code.encode()).decode()
    candidates.append(("Base64编码", b64))
    
    print("\n" + "="*80)
    print("新的授权码候选列表:")
    print("="*80)
    
    for i, (name, value) in enumerate(candidates, 1):
        print(f"\n{i}. {name}")
        print(f"   {value}")
    
    # 保存到文件
    with open("新授权码候选.txt", 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("基于错误信息生成的新授权码候选\n")
        f.write("="*80 + "\n\n")
        f.write(f"机器码: {machine_code}\n\n")
        f.write("="*80 + "\n")
        f.write("授权码候选列表 (请依次尝试)\n")
        f.write("="*80 + "\n\n")
        
        for i, (name, value) in enumerate(candidates, 1):
            f.write(f"{i}. {name}\n")
            f.write(f"   {value}\n\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("使用说明:\n")
        f.write("1. 从上到下依次复制授权码\n")
        f.write("2. 粘贴到软件中\n")
        f.write("3. 观察是否还是 '卡密无效'\n")
        f.write("4. 如果错误信息变化，立即反馈\n")
        f.write("="*80 + "\n")
    
    print("\n✅ 新候选已保存到: 新授权码候选.txt")
    
    # 重点推荐
    print("\n" + "="*80)
    print("🔥 重点尝试这些:")
    print("="*80)
    
    priority = [
        ("机器码本身", machine_code),
        ("机器码大写", machine_code.upper()),
        ("格式化(破折号)", formatted),
    ]
    
    for name, value in priority:
        print(f"\n{name}:")
        print(f"  {value}")

if __name__ == "__main__":
    analyze_validation_logic()
