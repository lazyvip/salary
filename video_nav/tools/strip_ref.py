"""
移除 data.json 中所有网址的 ref=aewz.com 查询参数，保留其它查询参数不变，并做 URL 规范化。

使用方法（在 video_nav 目录下执行）：
  python tools/strip_ref.py
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"


def canonicalize_url(u: str) -> str:
    """规范化 URL：在存在 query/fragment/params 且 path 为空时，补齐 '/'。"""
    try:
        p = urlparse(u)
        path = p.path or ('/' if (p.query or p.fragment or p.params) else '')
        return urlunparse((p.scheme, p.netloc, path, p.params, p.query, p.fragment))
    except Exception:
        return u


def strip_ref_param(u: str) -> str:
    """移除 ref=aewz.com 参数（大小写不敏感，容忍结尾斜杠），保持其它参数不变。"""
    try:
        p = urlparse(u)
        qs = parse_qsl(p.query, keep_blank_values=True)
        new_qs = []
        for k, v in qs:
            if k.lower() == 'ref':
                vv = (v or '').strip().lower().rstrip('/')
                if vv == 'aewz.com':
                    # 丢弃该参数
                    continue
            new_qs.append((k, v))
        new_query = urlencode(new_qs, doseq=True)
        new_u = urlunparse((p.scheme, p.netloc, p.path, p.params, new_query, p.fragment))
        return canonicalize_url(new_u)
    except Exception:
        return u


def main() -> int:
    if not DATA_PATH.exists():
        print(f"[ERROR] data.json 不存在: {DATA_PATH}")
        return 1

    data = json.loads(DATA_PATH.read_text('utf-8'))
    categories = data.get('categories', [])

    total = 0
    changed = 0
    normalized = 0

    for cat in categories:
        for item in cat.get('items', []):
            u = item.get('url')
            if not isinstance(u, str) or not u:
                continue
            total += 1
            new_u = strip_ref_param(u)
            if new_u != u:
                item['url'] = new_u
                changed += 1
            # 再做一次规范化，尽量统一风格
            cu = canonicalize_url(item['url'])
            if cu != item['url']:
                item['url'] = cu
                normalized += 1

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf-8')
    print(f"处理完成：总链接 {total}，移除 ref 参数 {changed}，额外规范化 {normalized}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

