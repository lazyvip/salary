"""
本地授权服务器 - 模拟真实授权服务器
用于破解 AI批量生图工具
"""
from fastapi import FastAPI
from datetime import datetime, timedelta
import uvicorn

app = FastAPI()

# 存储激活的机器码和过期时间
activated_machines = {}

@app.post("/activate")
async def activate(data: dict):
    """
    激活接口
    接受格式: {"machine_id": "xxx", "license_key": "DEMO-xxx"}
    """
    machine_id = data.get("machine_id", "")
    license_key = data.get("license_key", "")
    
    print(f"\n[激活请求]")
    print(f"  机器码: {machine_id}")
    print(f"  授权码: {license_key}")
    
    # 验证授权码格式: DEMO-<机器码前8位>
    expected_key = f"DEMO-{machine_id[:8]}"
    
    if license_key == expected_key or license_key == "ADMIN" or license_key == "CRACK":
        # 激活成功，设置90天有效期
        expires_at = (datetime.utcnow() + timedelta(days=90)).isoformat()
        activated_machines[machine_id] = expires_at
        
        print(f"  ✓ 激活成功！有效期至: {expires_at}")
        
        return {
            "status": "success",
            "message": "激活成功！",
            "expires_at": expires_at
        }
    else:
        print(f"  ✗ 授权码错误")
        print(f"  正确的授权码应该是: {expected_key}")
        
        return {
            "status": "error",
            "message": f"卡密无效"
        }, 400

@app.post("/validate")
async def validate(data: dict):
    """
    验证接口
    接受格式: {"machine_id": "xxx"}
    """
    machine_id = data.get("machine_id", "")
    
    print(f"\n[验证请求]")
    print(f"  机器码: {machine_id}")
    
    if machine_id in activated_machines:
        expires_at = activated_machines[machine_id]
        print(f"  ✓ 已激活，有效期至: {expires_at}")
        
        return {
            "status": "valid",
            "expires_at": expires_at
        }
    else:
        print(f"  ✗ 未激活")
        
        # 自动激活（破解模式）
        expires_at = (datetime.utcnow() + timedelta(days=90)).isoformat()
        activated_machines[machine_id] = expires_at
        
        print(f"  🔥 自动激活（破解模式），有效期至: {expires_at}")
        
        return {
            "status": "valid",
            "expires_at": expires_at
        }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI批量生图工具 - 本地授权服务器",
        "activated_count": len(activated_machines),
        "activated_machines": list(activated_machines.keys())
    }

if __name__ == "__main__":
    print("="*80)
    print("🔥 AI批量生图工具 - 本地授权服务器")
    print("="*80)
    print("\n[*] 启动授权服务器...")
    print("[*] 地址: http://127.0.0.1:5555")
    print("\n[*] 破解模式: 所有验证请求自动通过")
    print("[*] 授权码格式: DEMO-<机器码前8位>")
    print("\n" + "="*80)
    
    uvicorn.run(app, host="127.0.0.1", port=5555)
