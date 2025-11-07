import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT, 'data.json')
FEE_MAP_PATH = os.path.join(ROOT, 'id_fee_map.json')

def parse_id_from_url(url: str):
    if not isinstance(url, str):
        return None
    m = re.search(r'[?&]id=([a-z0-9]+)', url)
    return m.group(1) if m else None

def main():
    if not os.path.exists(DATA_PATH):
        print(f'ERROR: data.json not found at {DATA_PATH}', file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(FEE_MAP_PATH):
        print(f'ERROR: id_fee_map.json not found at {FEE_MAP_PATH}', file=sys.stderr)
        sys.exit(1)

    with open(FEE_MAP_PATH, 'r', encoding='utf-8') as f:
        id_fee = json.load(f)
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = 0
    updated = 0
    for cat in data.get('categories', []):
        for item in cat.get('items', []):
            total += 1
            id_ = parse_id_from_url(item.get('url'))
            if id_ and id_ in id_fee:
                item['fee'] = id_fee[id_]
                updated += 1

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'Done. Items: {total}, updated with fee: {updated}. Saved to {DATA_PATH}')

if __name__ == '__main__':
    main()

