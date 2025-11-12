import os
import subprocess
import hashlib
import base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

BACKEND_URL = "http://101.35.94.153:5555"
UUID_SALT = "dachen101"

def _run_wmic(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        return out.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def get_motherboard_serial():
    return _run_wmic("wmic baseboard get serialnumber")

def get_cpu_id():
    return _run_wmic("wmic cpu get ProcessorId")

def get_primary_disk_serial():
    return _run_wmic("wmic diskdrive get SerialNumber")

def get_primary_mac_address():
    return _run_wmic("getmac /fo csv /nh")

def get_system_uuid():
    return _run_wmic("wmic csproduct get UUID")

def get_bios_info():
    return _run_wmic("wmic bios get serialnumber")

def get_gpu_info():
    return _run_wmic("wmic path win32_VideoController get name")

def _clean(s: str) -> str:
    s = s.strip()
    s = s.replace("\r", "").replace("\n", "")
    repl = ["Default string", "To be filled by O.E.M.", "Unknown", "None"]
    for r in repl:
        s = s.replace(r, "")
    return s

def generate_machine_id_v2() -> str:
    factors = [
        _clean(get_motherboard_serial()),
        _clean(get_cpu_id()),
        _clean(get_primary_disk_serial()),
        _clean(get_system_uuid()),
        _clean(get_primary_mac_address()),
        _clean(get_bios_info()),
        _clean(get_gpu_info()),
    ]
    valid = [f for f in factors if f]
    combined = "|".join(valid[:7])
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

def derive_uuid_encryption_key() -> bytes:
    salt = UUID_SALT.encode("utf-8")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = kdf.derive(UUID_SALT.encode("utf-8"))
    return base64.urlsafe_b64encode(key)

def encrypt_uuid(uuid_text: str) -> str:
    f = Fernet(derive_uuid_encryption_key())
    token = f.encrypt(base64.b64encode(uuid_text.encode("utf-8")))
    return token.decode("utf-8")

def decrypt_uuid(encrypted_uuid: str) -> str:
    f = Fernet(derive_uuid_encryption_key())
    raw = f.decrypt(encrypted_uuid.encode("utf-8"))
    return base64.b64decode(raw).decode("utf-8")

def write_cache(uuid_text: str, cache_dir: Path) -> Path:
    cache_file = cache_dir / ".cache.tmp"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(encrypt_uuid(uuid_text), encoding="utf-8")
    return cache_file

def read_cache(cache_dir: Path) -> str | None:
    p = cache_dir / ".cache.tmp"
    if not p.exists():
        return None
    try:
        enc = p.read_text(encoding="utf-8")
        return decrypt_uuid(enc)
    except Exception:
        return None

def main():
    machine_id = generate_machine_id_v2()
    enc = encrypt_uuid(machine_id)
    print(machine_id)
    print(enc)

if __name__ == "__main__":
    main()
