import sys
from pathlib import Path

def strip_header(pyc_path: Path, out_path: Path, header_len: int = 16) -> None:
    data = pyc_path.read_bytes()
    if len(data) < header_len:
        raise ValueError("PYC file too small")
    out_path.write_bytes(data[header_len:])

def main():
    if len(sys.argv) < 3:
        print("Usage: python strip_pyc_header.py <input.pyc> <output.bin> [header_len]")
        sys.exit(1)
    inp = Path(sys.argv[1])
    out = Path(sys.argv[2])
    header = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    strip_header(inp, out, header)

if __name__ == "__main__":
    main()
