import sys
import marshal
import dis
from pathlib import Path

def disasm(pyc_path: Path, out_path: Path, offset: int):
    data = pyc_path.read_bytes()
    co = marshal.loads(data[offset:])
    with out_path.open('w', encoding='utf-8') as f:
        f.write(f"file: {pyc_path}\n")
        f.write(f"offset: {offset}\n")
        f.write(f"co_name: {co.co_name}\n")
        f.write(f"co_argcount: {co.co_argcount}\n")
        f.write(f"co_posonlyargcount: {getattr(co,'co_posonlyargcount',0)}\n")
        f.write(f"co_kwonlyargcount: {co.co_kwonlyargcount}\n")
        f.write(f"co_nlocals: {co.co_nlocals}\n")
        f.write(f"co_consts: {co.co_consts}\n")
        f.write(f"co_names: {co.co_names}\n")
        f.write(f"co_varnames: {co.co_varnames}\n")
        f.write("\nDisassembly:\n")
        f.write(dis.Bytecode(co).dis())

def main():
    if len(sys.argv) < 4:
        print("Usage: python disasm_pyc.py <input.pyc> <offset> <out.txt>")
        sys.exit(1)
    pyc = Path(sys.argv[1])
    offset = int(sys.argv[2])
    out = Path(sys.argv[3])
    disasm(pyc, out, offset)

if __name__ == "__main__":
    main()
