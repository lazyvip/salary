import os
import base64
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from platformdirs import user_data_dir

BACKEND_URL = "http://101.35.94.153:5555"
APP_IDENTIFIER = "大臣"
UUID_SALT = "dachen101"
UUID_CACHE_FILE = ".cache.tmp"

def get_user_data_path() -> Path:
    return Path(user_data_dir(APP_IDENTIFIER))

def get_data_path() -> Path:
    p = get_user_data_path()
    p.mkdir(parents=True, exist_ok=True)
    return p

def _run(cmd: str) -> str:
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        return out.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def _clean(s: str) -> str:
    s = s.strip().replace("\r", "").replace("\n", "")
    for r in ("Default string", "To be filled by O.E.M.", "Unknown", "None"):
        s = s.replace(r, "")
    return s

def get_motherboard_serial():
    return _clean(_run("wmic baseboard get serialnumber"))

def get_cpu_id():
    return _clean(_run("wmic cpu get ProcessorId"))

def get_primary_disk_serial():
    return _clean(_run("wmic diskdrive get SerialNumber"))

def get_primary_mac_address():
    return _clean(_run("getmac /fo csv /nh"))

def get_system_uuid():
    return _clean(_run("wmic csproduct get UUID"))

def get_bios_info():
    return _clean(_run("wmic bios get serialnumber"))

def get_gpu_info():
    return _clean(_run("wmic path win32_VideoController get name"))

def generate_machine_id_v2() -> str:
    parts = [
        get_motherboard_serial(),
        get_cpu_id(),
        get_primary_disk_serial(),
        get_system_uuid(),
        get_primary_mac_address(),
        get_bios_info(),
        get_gpu_info(),
    ]
    joined = "|".join([p for p in parts if p])
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()

def derive_uuid_encryption_key() -> bytes:
    salt = UUID_SALT.encode("utf-8")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = kdf.derive(UUID_SALT.encode("utf-8"))
    return base64.urlsafe_b64encode(key)

def encrypt_uuid(uuid_text: str) -> str:
    f = Fernet(derive_uuid_encryption_key())
    token = f.encrypt(uuid_text.encode("utf-8"))
    return base64.b64encode(token).decode("utf-8")

def decrypt_uuid(encrypted_text: str) -> str:
    f = Fernet(derive_uuid_encryption_key())
    raw = base64.b64decode(encrypted_text.encode("utf-8"))
    return f.decrypt(raw).decode("utf-8")

def read_cached_uuid() -> str | None:
    p = get_data_path() / UUID_CACHE_FILE
    if not p.exists():
        return None
    try:
        s = p.read_text(encoding="utf-8").strip()
        if not s:
            return None
        return decrypt_uuid(s)
    except Exception:
        return None

def write_cached_uuid(uuid_text: str) -> None:
    p = get_data_path() / UUID_CACHE_FILE
    p.write_text(encrypt_uuid(uuid_text), encoding="utf-8")

class LicenseManager:
    def __init__(self):
        self.machine_id = generate_machine_id_v2()
        self._backend_url = os.environ.get("AI_TOOL_BACKEND_URL", BACKEND_URL)

    def activate(self, license_key: str):
        try:
            r = requests.post(f"{self._backend_url}/activate", json={"machine_id": self.machine_id, "license_key": license_key}, timeout=60)
            if r.status_code == 200:
                msg = r.json().get("message", "激活成功！")
                return True, msg
            else:
                return False, {"message": r.text}
        except requests.exceptions.RequestException as e:
            return False, {"message": str(e)}

    def validate_with_machine_id(self, machine_id: str):
        if os.environ.get("AI_TOOL_DEV") == "1":
            expires_at = (datetime.utcnow() + timedelta(days=3)).isoformat()
            return "valid", {"expires_at": expires_at}
        try:
            r = requests.post(f"{self._backend_url}/validate", json={"machine_id": machine_id}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    if "expires_at" in data:
                        return "valid", data
                    msg = data.get("message") or data.get("detail") or "授权验证失败"
                    return "not_activated", {"message": msg}
                return "client_error", {"message": "响应格式错误"}
            if r.status_code == 404:
                try:
                    data = r.json()
                    msg = data.get("message") if isinstance(data, dict) else "未激活"
                except Exception:
                    msg = "未激活"
                return "not_activated", {"message": msg}
            if 400 <= r.status_code < 500:
                return "client_error", {"message": f"客户端错误({r.status_code})"}
            if 500 <= r.status_code:
                return "server_error", {"message": f"服务器错误({r.status_code})"}
            return "network_error", {"message": "网络连接失败"}
        except requests.exceptions.Timeout:
            return "network_error", {"message": "网络请求超时"}
        except requests.exceptions.RequestException as e:
            return "network_error", {"message": str(e)}

    def validate(self):
        return self.validate_with_machine_id(self.machine_id)
