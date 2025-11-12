import sys
import marshal
from pathlib import Path

def try_offsets(pyc_path: Path, start: int = 0, end: int = 2048, step: int = 1):
    data = pyc_path.read_bytes()
    for off in range(start, end, step):
        try:
            obj = marshal.loads(data[off:])
        except Exception:
            continue
        t = type(obj).__name__
        print(f"offset {off}: success -> type {t}")
        return off, obj
    return None, None

def main():
    if len(sys.argv) < 2:
        print("Usage: python probe_pyc_offsets.py <input.pyc>")
        sys.exit(1)
    off, co = try_offsets(Path(sys.argv[1]))
    if off is None:
        print("No valid marshal offset found in first 64 bytes.")
        sys.exit(2)
    print(f"Found offset {off}")

if __name__ == "__main__":
    main()
