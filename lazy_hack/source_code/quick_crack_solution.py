"""
快速破解方案 - 基于错误信息分析
"""
import hashlib
import json

machine_code = "8ee8d931c26f457bac19512cde21c8e3"

print("="*80)
print("基于错误信息的快速破解分析")
print("="*80)

print(f"\n机器码: {machine_code}")
print(f"\n错误信息: {{'message':'卡密无效','status':'error'}}")

print("\n" + "="*80)
print("分析:")
print("="*80)

print("""
1. 错误信息是中文 '卡密无效'
2. 返回格式是 JSON
3. 没有网络请求（hosts已阻止）
4. 说明是本地验证逻辑

可能的验证方式:
A. 授权码 = F(机器码)  - 某个函数计算
B. 授权码在硬编码的列表中
C. 授权码有特定格式要求
""")

print("\n" + "="*80)
print("🔥 新策略: 暴力尝试常见算法")
print("="*80)

# 生成更多候选
candidates = []

# 策略 1: 简单变换
candidates.append(("空字符串", ""))
candidates.append(("机器码本身", machine_code))
candidates.append(("大写机器码", machine_code.upper()))
candidates.append(("机器码反转", machine_code[::-1]))

# 策略 2: 固定授权码
common_keys = [
    "ADMIN",
    "admin",
    "123456",
    "888888",
    "666666",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "00000000000000000000000000000000",
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
]

for key in common_keys:
    candidates.append((f"固定值:{key}", key))

# 策略 3: 机器码的哈希
candidates.append(("MD5(机器码)", hashlib.md5(machine_code.encode()).hexdigest()))
candidates.append(("SHA1(机器码)", hashlib.sha1(machine_code.encode()).hexdigest()))
candidates.append(("SHA256(机器码)", hashlib.sha256(machine_code.encode()).hexdigest()))

# 策略 4: 特殊盐值
salts = ["CRACK", "VIP", "PREMIUM", "LICENSE", "ACTIVATED", "2024"]
for salt in salts:
    key = hashlib.md5(f"{machine_code}{salt}".encode()).hexdigest()
    candidates.append((f"MD5(机器码+{salt})", key))

# 策略 5: 机器码变体
# 去掉数字
no_digits = ''.join(c for c in machine_code if not c.isdigit())
if no_digits:
    candidates.append(("机器码去数字", no_digits))
    candidates.append(("MD5(去数字)", hashlib.md5(no_digits.encode()).hexdigest()))

# 只保留数字
only_digits = ''.join(c for c in machine_code if c.isdigit())
if only_digits:
    candidates.append(("只保留数字", only_digits))

# 策略 6: 特殊格式
# UUID格式
uuid_format = f"{machine_code[:8]}-{machine_code[8:12]}-{machine_code[12:16]}-{machine_code[16:20]}-{machine_code[20:]}"
candidates.append(("UUID格式", uuid_format))

# 策略 7: XOR
def xor_encode(s, key=0x5A):
    return ''.join(chr(ord(c) ^ key) for c in s)

candidates.append(("XOR(0x5A)", xor_encode(machine_code)))
candidates.append(("XOR(0xFF)", xor_encode(machine_code, 0xFF)))

# 策略 8: Base转换
try:
    # 尝试将hex转int再转回
    int_val = int(machine_code, 16)
    candidates.append(("十进制", str(int_val)))
    candidates.append(("MD5(十进制)", hashlib.md5(str(int_val).encode()).hexdigest()))
except:
    pass

print(f"\n生成了 {len(candidates)} 个候选授权码\n")

# 保存到文件
with open("最终授权码候选.txt", 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("最终授权码候选列表\n")
    f.write("="*80 + "\n\n")
    f.write(f"机器码: {machine_code}\n\n")
    f.write("="*80 + "\n")
    f.write("使用说明:\n")
    f.write("1. 从上到下依次尝试\n")
    f.write("2. 如果错误信息变化，立即停止并反馈\n")
    f.write("3. 特别关注是否出现 'success' 或其他新错误\n")
    f.write("="*80 + "\n\n")
    
    for i, (name, key) in enumerate(candidates, 1):
        f.write(f"{i}. {name}\n")
        f.write(f"   {key}\n\n")

print("✅ 已保存到: 最终授权码候选.txt")

print("\n" + "="*80)
print("🎯 优先尝试这 10 个:")
print("="*80)

priority_list = candidates[:10]
for i, (name, key) in enumerate(priority_list, 1):
    print(f"\n{i}. {name}")
    print(f"   {key}")

print("\n" + "="*80)
print("⚡ 终极方案: 修补验证逻辑")
print("="*80)

print("""
如果所有授权码都失败，我们需要：

方案 A: 内存补丁
1. 使用 Cheat Engine 或类似工具
2. 搜索字符串 "卡密无效"
3. 找到验证函数
4. 修改返回值为 "success"

方案 B: 二进制补丁
1. 在 exe 中搜索 "卡密无效" 字符串
2. 定位验证函数
3. 使用 NOP 或 JMP 跳过验证

方案 C: DLL注入
1. 创建 DLL Hook 验证函数
2. 强制返回成功

你想尝试哪个方案?
""")

print("="*80)
