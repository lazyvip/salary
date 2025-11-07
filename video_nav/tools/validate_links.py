#!/usr/bin/env python3
"""
Validate external links referenced in video_nav/data.json and report invalid ones.

Usage:
  python tools/validate_links.py [--timeout 6] [--outfile broken_links.json]

What it does:
  - Loads video_nav/data.json (schema: {"categories": [{"name": str, "items": [{"name": str, "url": str, ...}]}]})
  - Normalizes URLs the same way as the frontend (prefixes relative paths with https://www.aewz.com)
  - Checks reachability (HTTP 2xx/3xx considered OK)
  - Writes a machine-readable report (JSON) to video_nav/broken_links.json by default
  - Also writes a human-friendly text summary to video_nav/broken_links.txt

Notes:
  - HEAD requests are often blocked; we use GET with a small Range to minimize bandwidth
  - Redirects (3xx) are treated as success
  - Network errors, timeouts, SSL errors will be marked with error details
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    # urllib is part of standard library; no third-party deps
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError
except Exception as e:
    print("Failed to import urllib: ", e, file=sys.stderr)
    sys.exit(1)


ROOT = Path(__file__).resolve().parents[1]  # .../video_nav
DATA_JSON = ROOT / 'data.json'
DEFAULT_OUT_JSON = ROOT / 'broken_links.json'
DEFAULT_OUT_TXT = ROOT / 'broken_links.txt'


@dataclass
class BrokenLink:
    category_index: int
    item_index: int
    category_name: str
    item_name: str
    url: str
    status_code: Optional[int]
    error: Optional[str]


def normalize_url(url: Optional[str], name: Optional[str] = None) -> Optional[str]:
    """Mirror the frontend's normalizeUrl logic.
    - If empty or '#' -> return None (treated as missing_url)
    - If startswith('/') -> prefix with https://www.aewz.com
    - Else return as-is
    """
    if not url or url == '#':
        return None
    url = str(url)
    if url.startswith('/'):
        return 'https://www.aewz.com' + url
    return url


def check_url(url: str, timeout: float, ctx: ssl.SSLContext) -> (Optional[int], Optional[str]):
    """Return (status_code, error_message).
    Consider 2xx/3xx as success. On errors/4xx/5xx, return details.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        # Try to minimize content size when servers support Range
        'Range': 'bytes=0-64',
    }
    req = Request(url, headers=headers, method='GET')
    try:
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            code = getattr(resp, 'status', None)
            # Some Python versions use resp.getcode()
            if code is None:
                code = resp.getcode()
            if code is None:
                # No code? Treat as unknown but OK
                return None, None
            if 200 <= code <= 399:
                return code, None
            else:
                return code, f'HTTP {code}'
    except HTTPError as e:
        return e.code, f'HTTPError: {e.reason}'
    except URLError as e:
        return None, f'URLError: {getattr(e, "reason", str(e))}'
    except ssl.SSLError as e:
        return None, f'SSLError: {e}'
    except Exception as e:
        return None, f'Error: {e}'


def load_data() -> Dict[str, Any]:
    if not DATA_JSON.exists():
        print(f'Not found: {DATA_JSON}', file=sys.stderr)
        sys.exit(1)
    with DATA_JSON.open('r', encoding='utf-8') as f:
        return json.load(f)


def validate_links(timeout: float = 6.0, sleep: float = 0.0, max_items: Optional[int] = None) -> Dict[str, Any]:
    data = load_data()
    categories = data.get('categories', [])
    broken: List[BrokenLink] = []
    ok_count = 0
    total = 0

    # SSL context
    ctx = ssl.create_default_context()

    for ci, cat in enumerate(categories):
        items = cat.get('items', [])
        cname = str(cat.get('name', f'分类{ci}'))
        for ii, it in enumerate(items):
            total += 1
            if max_items is not None and total > max_items:
                break
            url_raw = it.get('url')
            name = it.get('name', f'项目{ii}')
            url = normalize_url(url_raw, name)

            if url is None:
                broken.append(BrokenLink(ci, ii, cname, name, str(url_raw), None, 'missing_url'))
                continue

            status, err = check_url(url, timeout=timeout, ctx=ctx)
            if err is None:
                ok_count += 1
            else:
                broken.append(BrokenLink(ci, ii, cname, name, url, status, err))

            if sleep > 0:
                time.sleep(sleep)

    return {
        'total': total,
        'ok': ok_count,
        'broken_count': len(broken),
        'broken': [asdict(b) for b in broken],
    }


def write_reports(result: Dict[str, Any], out_json: Path, out_txt: Path) -> None:
    # JSON report
    with out_json.open('w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Human-friendly text summary
    lines: List[str] = []
    lines.append(f"总计: {result['total']} | 可访问: {result['ok']} | 失效: {result['broken_count']}")
    lines.append('')
    for i, b in enumerate(result['broken'], start=1):
        lines.append(f"[{i}] 分类({b['category_index']}) {b['category_name']} -> 项目({b['item_index']}) {b['item_name']}")
        lines.append(f"    URL: {b['url']}")
        lines.append(f"    状态: {b['status_code']} | 错误: {b['error']}")
        lines.append('')
    with out_txt.open('w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description='Validate links in video_nav/data.json and report broken ones.')
    p.add_argument('--timeout', type=float, default=6.0, help='Per-request timeout seconds (default: 6)')
    p.add_argument('--sleep', type=float, default=0.0, help='Sleep between requests seconds (default: 0)')
    p.add_argument('--max', dest='max_items', type=int, default=None, help='Max items to check (default: all)')
    p.add_argument('--outfile', type=str, default=str(DEFAULT_OUT_JSON), help='Output JSON path')
    p.add_argument('--outtxt', type=str, default=str(DEFAULT_OUT_TXT), help='Output text summary path')
    args = p.parse_args(argv)

    result = validate_links(timeout=args.timeout, sleep=args.sleep, max_items=args.max_items)
    out_json = Path(args.outfile)
    out_txt = Path(args.outtxt)
    write_reports(result, out_json, out_txt)

    print(f"已完成检测：总计 {result['total']}，可访问 {result['ok']}，失效 {result['broken_count']}")
    print(f"JSON 报告: {out_json}")
    print(f"文本报告: {out_txt}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

