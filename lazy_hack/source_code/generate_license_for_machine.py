"""
为特定机器码生成授权码
机器码: 8ee8d931c26f457bac19512cde21c8e3
"""
import hashlib
import base64

def generate_all_licenses(machine_code):
    """为指定机器码生成所有可能的授权码"""
    
    print("="*80)
    print(f"机器码: {machine_code}")
    print("="*80)
    print("\n正在生成所有可能的授权码...\n")
    
    results = []
    
    # 盐值候选
    salts = [
        "",
        "AI_IMAGE_TOOL",
        "ai_batch_image",
        "license_key_salt",
        "machine_code_salt",
        "2024",
        "v2.0.14",
        "refactored",
    ]
    
    # 1. MD5 系列
    print("[MD5 系列]")
    for salt in salts:
        data = f"{machine_code}{salt}"
        key = hashlib.md5(data.encode()).hexdigest()
        salt_info = f" (salt: {salt})" if salt else " (无盐)"
        print(f"  {key}{salt_info}")
        results.append(("MD5" + salt_info, key))
    
    # 2. SHA256 系列
    print("\n[SHA256 系列]")
    for salt in salts:
        data = f"{machine_code}{salt}"
        key = hashlib.sha256(data.encode()).hexdigest()
        salt_info = f" (salt: {salt})" if salt else " (无盐)"
        print(f"  {key}{salt_info}")
        results.append(("SHA256" + salt_info, key))
    
    # 3. SHA1 系列
    print("\n[SHA1 系列]")
    for salt in salts:
        data = f"{machine_code}{salt}"
        key = hashlib.sha1(data.encode()).hexdigest()
        salt_info = f" (salt: {salt})" if salt else " (无盐)"
        print(f"  {key}{salt_info}")
        results.append(("SHA1" + salt_info, key))
    
    # 4. Base64
    print("\n[Base64]")
    key = base64.b64encode(machine_code.encode()).decode()
    print(f"  {key}")
    results.append(("Base64", key))
    
    # 5. Reverse + MD5
    print("\n[Reverse + MD5]")
    reversed_code = machine_code[::-1]
    key = hashlib.md5(reversed_code.encode()).hexdigest()
    print(f"  {key}")
    results.append(("Reverse+MD5", key))
    
    # 6. Double MD5
    print("\n[Double MD5]")
    first = hashlib.md5(machine_code.encode()).hexdigest()
    key = hashlib.md5(first.encode()).hexdigest()
    print(f"  {key}")
    results.append(("Double MD5", key))
    
    # 7. Upper + MD5
    print("\n[Upper + MD5]")
    key = hashlib.md5(machine_code.upper().encode()).hexdigest()
    print(f"  {key}")
    results.append(("Upper+MD5", key))
    
    # 8. Lower + MD5
    print("\n[Lower + MD5]")
    key = hashlib.md5(machine_code.lower().encode()).hexdigest()
    print(f"  {key}")
    results.append(("Lower+MD5", key))
    
    # 9. 特殊变换
    print("\n[特殊算法]")
    
    # 去掉所有数字
    no_digits = ''.join(c for c in machine_code if not c.isdigit())
    key = hashlib.md5(no_digits.encode()).hexdigest()
    print(f"  去数字+MD5: {key}")
    results.append(("去数字+MD5", key))
    
    # 只保留字母
    only_letters = ''.join(c for c in machine_code if c.isalpha())
    key = hashlib.md5(only_letters.encode()).hexdigest()
    print(f"  只字母+MD5: {key}")
    results.append(("只字母+MD5", key))
    
    # 只保留数字
    only_digits = ''.join(c for c in machine_code if c.isdigit())
    if only_digits:
        key = hashlib.md5(only_digits.encode()).hexdigest()
        print(f"  只数字+MD5: {key}")
        results.append(("只数字+MD5", key))
    
    print("\n" + "="*80)
    print(f"总计生成了 {len(results)} 个授权码")
    print("="*80)
    
    return results

def save_to_file(machine_code, results, filename="授权码列表.txt"):
    """保存到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("AI批量生图工具 v2.0.14 - 授权码生成结果\n")
        f.write("="*80 + "\n\n")
        f.write(f"您的机器码: {machine_code}\n\n")
        f.write("="*80 + "\n")
        f.write("授权码列表 (请依次尝试)\n")
        f.write("="*80 + "\n\n")
        
        for i, (algo, key) in enumerate(results, 1):
            f.write(f"{i}. {algo}\n")
            f.write(f"   {key}\n\n")
        
        f.write("="*80 + "\n")
        f.write("使用说明:\n")
        f.write("1. 复制上面的授权码\n")
        f.write("2. 在软件中粘贴并提交\n")
        f.write("3. 如果不对，尝试下一个\n")
        f.write("4. 建议优先尝试 MD5 和 SHA256 系列\n")
        f.write("="*80 + "\n")
    
    print(f"\n✅ 授权码已保存到: {filename}")

if __name__ == "__main__":
    # 你的机器码
    machine_code = "8ee8d931c26f457bac19512cde21c8e3"
    
    # 生成所有可能的授权码
    results = generate_all_licenses(machine_code)
    
    # 保存到文件
    save_to_file(machine_code, results)
    
    print("\n" + "="*80)
    print("🎯 重点推荐尝试以下授权码:")
    print("="*80)
    
    # 显示最可能的几个
    priority_algos = ["MD5 (无盐)", "SHA256 (无盐)", "MD5 (salt: AI_IMAGE_TOOL)", 
                     "MD5 (salt: ai_batch_image)", "Double MD5"]
    
    for algo in priority_algos:
        for name, key in results:
            if name == algo:
                print(f"\n{algo}:")
                print(f"  {key}")
                break
