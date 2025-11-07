#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
为 video_nav/data.json 的每个条目添加语言标注（lang: EN/CH）。

规则（更贴近原站数据）：
- 若条目已显式提供 lang（EN/CH/CN），优先使用；其中 CN 将统一为 CH。
- 读取覆盖表 tools/lang_override.json（若存在），按域名精确指定 EN 或 CH；覆盖表优先级最高。
- 启发式判断（按顺序）：
  * URL 的域名以 .cn 结尾（含 .com.cn 等）→ CH
  * URL 路径包含 /zh 或 /zh-cn → CH
  * URL 查询参数 lang/locale/hl 为 zh、zh-cn 等 → CH
  * 标题或描述包含中文字符 → CH
  * 其他情况 → EN

脚本会将原始 data.json 备份为 data.json.bak，然后覆盖写入更新后的 data.json。
"""

import json
import os
import re
import argparse
from urllib.parse import urlparse, parse_qs

# 内置少量常见域名映射，进一步贴近原站数据；可通过 tools/lang_override.json 扩展或覆盖
DEFAULT_DOMAIN_LANG = {
    # 英文站
    'mixkit.co': 'EN',
    'vidsplay.com': 'EN',
    'bensound.com': 'EN',
    'videezy.com': 'EN',
    'wedistill.io': 'EN',
    'videvo.net': 'EN',
    # 中文站
    'bilibili.com': 'CH',
    'douyin.com': 'CH',
    'xinpianchang.com': 'CH',
    'ibaotu.com': 'CH',
    '699pic.com': 'CH',
    'aigei.com': 'CH',
    'shipin520.com': 'CH',
    'kol.cn': 'CH',
    'soundems.com': 'CH',
    'ffkuaidu.com': 'CH',
    '1txm.com': 'CH',
    '91sotu.com': 'CH',
    'vlogxz.com': 'CH',
    'lizhi.io': 'CH',
    'aoao365.com': 'CH',
    'douban.com': 'CH',
    'miaopai.com': 'CH',
    'ulikecam.com': 'CH',
    'toutiao.com': 'CH',
}


def load_overrides() -> dict:
    path = os.path.join('video_nav', 'tools', 'lang_override.json')
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 预期格式：{"domains": {"example.com": "CH"}} 或直接 {"example.com": "CH"}
        if isinstance(data, dict) and 'domains' in data and isinstance(data['domains'], dict):
            return {k.lower(): str(v).upper() for k, v in data['domains'].items()}
        return {k.lower(): str(v).upper() for k, v in data.items()}
    except Exception:
        return {}


def normalize_url(url: str, name: str = "") -> str:
    if not url:
        return ""
    url = str(url)
    if url.startswith('/'):
        return 'https://www.aewz.com' + url
    return url


def guess_lang(item: dict, keep_existing: bool = False, overrides: dict | None = None) -> str:
    # 若选择保留现有标注，则优先使用
    if keep_existing:
        v = str(item.get('lang', '')).strip().upper()
        if v in ('EN', 'CH', 'CN'):
            return 'CH' if v == 'CN' else v

    url = normalize_url(item.get('url', ''), item.get('name', ''))
    try:
        u = urlparse(url)
        host = u.hostname or ''
        path = u.path or ''
        qs = parse_qs(u.query or '')

        # 覆盖表优先（支持子域名：host 以覆盖域名结尾）
        if overrides:
            h = (host or '').lower()
            for dom, lang in overrides.items():
                dom = dom.lower()
                if h == dom or h.endswith('.' + dom):
                    return 'CH' if lang == 'CN' else (lang if lang in ('EN', 'CH') else 'EN')

        # 内置域名映射其次
        h = (host or '').lower()
        for dom, lang in DEFAULT_DOMAIN_LANG.items():
            if h == dom or h.endswith('.' + dom):
                return 'CH' if lang.upper() == 'CN' else (lang.upper() if lang.upper() in ('EN', 'CH') else 'EN')

        if host.endswith('.cn'):
            return 'CH'

        if re.search(r'/zh(?:-cn)?/', path, re.IGNORECASE):
            return 'CH'

        for k in ('lang', 'locale', 'hl'):
            val = (qs.get(k, [''])[0] or '').lower()
            if val.startswith('zh'):
                return 'CH'
    except Exception:
        pass

    # 标题或描述含中文字符也认为是中文站
    text = f"{item.get('name', '')} {item.get('description', '')}"
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'CH'

    return 'EN'


def process(data: dict, keep_existing: bool = False, overrides: dict | None = None) -> dict:
    for cat in data.get('categories', []):
        for item in cat.get('items', []):
            item['lang'] = guess_lang(item, keep_existing=keep_existing, overrides=overrides)
    return data


def main():
    parser = argparse.ArgumentParser(description='为 data.json 添加或更新语言标注 (EN/CH)。')
    parser.add_argument('--keep-existing', action='store_true', help='保留已有的 lang 值，不覆盖。默认不保留（会重新计算并覆盖）。')
    args = parser.parse_args()

    path = os.path.join('video_nav', 'data.json')
    bak = os.path.join('video_nav', 'data.json.bak')

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 备份原文件
    with open(bak, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 读取覆盖表
    overrides = load_overrides()

    # 更新并写回
    data = process(data, keep_existing=args.keep_existing, overrides=overrides)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('语言标注已更新并写回:', path)
    print('已创建备份文件:', bak)
    if overrides:
        print('已应用域名覆盖表项数量:', len(overrides))


if __name__ == '__main__':
    main()
