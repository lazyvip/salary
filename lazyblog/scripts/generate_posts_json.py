import os
import re
import json
from datetime import datetime
from pathlib import Path

def parse_date_from_name(name: str) -> datetime:
    m = re.match(r"^(\d{8}|\d{6})", name)
    if not m:
        return datetime.fromtimestamp(0)
    s = m.group(1)
    if len(s) == 6:
        y = 2000 + int(s[0:2])
        mo = int(s[2:4])
        d = int(s[4:6])
    else:
        y = int(s[0:4])
        mo = int(s[4:6])
        d = int(s[6:8])
    try:
        return datetime(y, mo, d)
    except ValueError:
        return datetime.fromtimestamp(0)

def main():
    files_dir = Path(r"d:\github\salary\lazyblog\files")
    out_dir = Path(r"d:\github\salary\lazyblog\data")
    out_dir.mkdir(parents=True, exist_ok=True)
    posts = []
    for p in files_dir.glob("*.md"):
        dt = parse_date_from_name(p.name)
        posts.append({
            "title": p.name,
            "date": dt.strftime("%Y-%m-%d"),
            "filename": p.name
        })
    posts.sort(key=lambda x: x["date"], reverse=True)
    out_path = out_dir / "posts.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()