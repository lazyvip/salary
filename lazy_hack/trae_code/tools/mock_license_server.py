from datetime import datetime, timedelta
from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

store_path = Path(__file__).parent / "licenses.json"

def load_store():
    if store_path.exists():
        try:
            return json.loads(store_path.read_text(encoding="utf-8"))
        except Exception:
            return {"activations": {}}
    return {"activations": {}}

def save_store(data):
    store_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class ValidateReq(BaseModel):
    machine_id: str

class ActivateReq(BaseModel):
    machine_id: str
    license_key: str

@app.post("/validate")
def validate(req: ValidateReq):
    data = load_store()
    act = data.get("activations", {})
    info = act.get(req.machine_id)
    if not info:
        raise HTTPException(status_code=404, detail="未激活")
    exp = datetime.fromisoformat(info["expires_at"]) if isinstance(info, dict) else None
    if not exp or exp < datetime.utcnow():
        raise HTTPException(status_code=404, detail="已过期")
    return {"expires_at": info["expires_at"]}

@app.post("/activate")
def activate(req: ActivateReq):
    if not req.machine_id:
        raise HTTPException(status_code=400, detail="缺少机器码")
    if not req.license_key:
        raise HTTPException(status_code=400, detail="缺少授权码")
    expect = f"DEMO-{req.machine_id[:8]}"
    if req.license_key != expect:
        raise HTTPException(status_code=400, detail="授权码无效")
    data = load_store()
    act = data.setdefault("activations", {})
    exp = (datetime.utcnow() + timedelta(days=90)).isoformat()
    act[req.machine_id] = {"expires_at": exp}
    save_store(data)
    return {"message": "激活成功", "expires_at": exp}
