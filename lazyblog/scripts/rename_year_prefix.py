import re
from pathlib import Path

def target_name(name: str) -> str | None:
    m = re.match(r"^(23)(\d{4})(.*)$", name)
    if m:
        return f"2023{m.group(2)}{m.group(3)}"
    m = re.match(r"^(24)(\d{4})(.*)$", name)
    if m:
        return f"2024{m.group(2)}{m.group(3)}"
    return None

def main():
    files_dir = Path(r"d:\github\salary\lazyblog\files")
    changed = []
    skipped = []
    for p in files_dir.glob("*.md"):
        new_name = target_name(p.name)
        if not new_name:
            continue
        dest = p.with_name(new_name)
        if dest.exists():
            skipped.append((p.name, new_name))
            continue
        p.rename(dest)
        changed.append((p.name, new_name))
    print("Renamed:")
    for old, new in changed:
        print(f"  {old} -> {new}")
    if skipped:
        print("Skipped (target exists):")
        for old, new in skipped:
            print(f"  {old} -> {new}")

if __name__ == "__main__":
    main()