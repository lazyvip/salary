"""
将 data.json 中 aewz 的长链接（https://www.aewz.com/api/link?id=...）解析为真实网址，并回写到 data.json。

实现要点：
- 逐条检测 url 字段是否为 aewz 的 api/link 长链接；
- 通过跟随重定向获取最终网址（使用 urllib 内置，无需第三方依赖）；
- 失败时保留原链接并记录错误；
- 生成 id_url_map.json 作为缓存映射（id -> real_url）；

使用方法（在 video_nav 目录下执行）：
  python tools/resolve_urls.py
"""

from __future__ import annotations

import json
import ssl
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlunparse
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"
MAP_PATH = ROOT / "id_url_map.json"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.aewz.com/",
}


def is_aewz_api_link(url: str) -> bool:
    try:
        p = urlparse(url)
    except Exception:
        return False
    if not p.scheme.startswith("http"):
        return False
    host = (p.netloc or "").lower()
    if "aewz.com" not in host:
        return False
    if not p.path.startswith("/api/link"):
        return False
    qs = parse_qs(p.query)
    return "id" in qs and len(qs["id"]) > 0


def extract_id(url: str) -> Optional[str]:
    try:
        p = urlparse(url)
        qs = parse_qs(p.query)
        return qs.get("id", [None])[0]
    except Exception:
        return None


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # 阻止 urllib 自动跟随重定向
        return None

def canonicalize_url(u: str) -> str:
    """规范化 URL：在存在 query/fragment 且 path 为空时，补齐 '/'。"""
    try:
        p = urlparse(u)
        path = p.path or ('/' if (p.query or p.fragment or p.params) else '')
        return urlunparse((p.scheme, p.netloc, path, p.params, p.query, p.fragment))
    except Exception:
        return u

def resolve_real_url(aewz_url: str, timeout: float = 6.0) -> Tuple[Optional[str], Optional[str]]:
    """
    通过 HEAD + 禁止自动重定向的方式，仅获取 Location 头，避免拉取正文。
    若 HEAD 失败，则回退到 GET（跟随重定向）但尽量快速返回。
    返回 (final_url, error_msg)。成功时 error_msg 为 None。
    """
    ctx = ssl.create_default_context()

    # 1) 优先使用 HEAD + NoRedirect，直接拿 Location
    try:
        opener = build_opener(NoRedirectHandler())
        req = Request(aewz_url, headers=HEADERS, method="HEAD")
        # 不跟随重定向时，302/301 会抛出 HTTPError，可从 headers 读取 Location
        try:
            with opener.open(req, timeout=timeout) as resp:
                # 若没有重定向，返回原地址（罕见场景）
                return canonicalize_url(resp.geturl()), None
        except HTTPError as e:
            # 期望拿到 Location
            loc = e.headers.get("Location")
            if loc:
                return canonicalize_url(loc), None
            return None, f"HTTPError without Location: {e}"
    except Exception as e:
        head_err = str(e)
        # 回退到 GET
        try:
            req = Request(aewz_url, headers=HEADERS, method="GET")
            with urlopen(req, timeout=timeout, context=ctx) as resp:
                final_url = resp.geturl()
            return canonicalize_url(final_url), None
        except Exception as e2:
            return None, f"HEAD fail: {head_err}; GET fail: {e2}"


def main() -> int:
    if not DATA_PATH.exists():
        print(f"[ERROR] data.json 不存在: {DATA_PATH}")
        return 1

    data = json.loads(DATA_PATH.read_text("utf-8"))
    categories = data.get("categories", [])

    # 如果已有缓存映射，优先读取
    id_url_map: Dict[str, str] = {}
    if MAP_PATH.exists():
        try:
            id_url_map = json.loads(MAP_PATH.read_text("utf-8"))
        except Exception:
            id_url_map = {}
    total_items = 0
    api_items = 0
    resolved = 0
    unchanged = 0
    errors: Dict[str, str] = {}

    for cat in categories:
        items = cat.get("items", [])
        for item in items:
            total_items += 1
            url = item.get("url", "")
            if not isinstance(url, str) or not url:
                continue
            if not is_aewz_api_link(url):
                continue

            api_items += 1
            _id = extract_id(url) or ""
            # 若缓存已存在，直接使用缓存
            cached = id_url_map.get(_id)
            if cached:
                item["url"] = cached
                resolved += 1
                continue

            final_url, err = resolve_real_url(url)
            # 适当休眠，避免触发风控
            time.sleep(0.1)

            if final_url:
                item["url"] = final_url
                id_url_map[_id] = final_url
                resolved += 1
            else:
                # 保留原始链接，记录错误
                unchanged += 1
                errors[_id or url] = err or "unknown error"

    # 统一对所有 url 做一次规范化（补齐 '/' 等），避免格式不一致
    normalized = 0
    for cat in categories:
        for item in cat.get("items", []):
            u = item.get("url")
            if not isinstance(u, str):
                continue
            cn = canonicalize_url(u)
            if cn and cn != u:
                item["url"] = cn
                normalized += 1

    # 写出映射缓存
    try:
        MAP_PATH.write_text(json.dumps(id_url_map, ensure_ascii=False, indent=2), "utf-8")
    except Exception as e:
        print(f"[WARN] 写入映射 id_url_map.json 失败: {e}")

    # 备份原始数据
    backup_path = ROOT / "data.backup.api_link.json"
    try:
        backup_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    except Exception as e:
        print(f"[WARN] 写入备份失败: {e}")

    # 覆盖 data.json
    try:
        DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    except Exception as e:
        print(f"[ERROR] 写入 data.json 失败: {e}")
        return 2

    print(
        (
            f"处理完成：总项目 {total_items}，aewz 链接 {api_items}，成功解析 {resolved}，保留原始 {unchanged}，规范化 {normalized}\n"
            f"映射已保存：{MAP_PATH}"
        )
    )

    if errors:
        print("以下条目解析失败（保留原始链接）：")
        for k, v in list(errors.items())[:15]:
            print(f"  id/url={k} -> error: {v}")
        if len(errors) > 15:
            print(f"  ... 还有 {len(errors) - 15} 条失败未展示")

    # 展示部分映射样例
    sample = list(id_url_map.items())[:10]
    if sample:
        print("示例映射（前10条）：")
        for _id, real in sample:
            print(f"  {_id} -> {real}")

    # 成功返回 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
