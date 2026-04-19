# 파킹통장 금리 수집 - 금융감독원 금융상품통합비교공시 API (https://finlife.fss.or.kr)
import json
import os
from datetime import date

import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_PATH = os.path.join(DATA_DIR, "parking.json")
BASE_URL = "https://finlife.fss.or.kr/finLifeApi/api/depositProductsSearch.json"
SOURCE_URL = "https://finlife.fss.or.kr"

PARKING_KEYWORDS = {"파킹", "세이프박스", "플러스박스", "수시", "자유입출"}

INTERNET_BANKS = {"한국카카오은행", "케이뱅크", "토스뱅크"}

FALLBACK_ITEMS = [
    {"rank": 1, "firm": "한국카카오은행",  "product_name": "카카오뱅크 세이프박스",  "bank_type": "인터넷은행", "rate": 3.80, "base_rate": 3.80, "protection": True, "join_channel": "앱",        "as_of": "2026-04-18"},
    {"rank": 2, "firm": "케이뱅크",        "product_name": "케이뱅크 파킹통장",      "bank_type": "인터넷은행", "rate": 3.70, "base_rate": 3.70, "protection": True, "join_channel": "앱",        "as_of": "2026-04-18"},
    {"rank": 3, "firm": "토스뱅크",        "product_name": "토스뱅크 통장",          "bank_type": "인터넷은행", "rate": 3.50, "base_rate": 3.50, "protection": True, "join_channel": "앱",        "as_of": "2026-04-18"},
    {"rank": 4, "firm": "우리은행",        "product_name": "WON통장",               "bank_type": "시중은행",   "rate": 3.20, "base_rate": 3.20, "protection": True, "join_channel": "인터넷/앱", "as_of": "2026-04-18"},
    {"rank": 5, "firm": "신한은행",        "product_name": "SOL파킹통장",           "bank_type": "시중은행",   "rate": 3.15, "base_rate": 3.15, "protection": True, "join_channel": "인터넷/앱", "as_of": "2026-04-18"},
    {"rank": 6, "firm": "하나은행",        "product_name": "달달하나",               "bank_type": "시중은행",   "rate": 3.10, "base_rate": 3.10, "protection": True, "join_channel": "인터넷/앱", "as_of": "2026-04-18"},
    {"rank": 7, "firm": "KB국민은행",      "product_name": "KB스타클럽 통장",        "bank_type": "시중은행",   "rate": 3.00, "base_rate": 3.00, "protection": True, "join_channel": "인터넷/앱", "as_of": "2026-04-18"},
    {"rank": 8, "firm": "NH농협은행",      "product_name": "NH올원통장",             "bank_type": "시중은행",   "rate": 2.90, "base_rate": 2.90, "protection": True, "join_channel": "인터넷/앱", "as_of": "2026-04-18"},
]


def _save(items, stale=False):
    os.makedirs(DATA_DIR, exist_ok=True)
    payload = {
        "updated_at": str(date.today()),
        "source": "금융감독원 금융상품비교공시",
        "source_url": SOURCE_URL,
        "items": items,
    }
    if stale:
        payload["stale"] = True
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _load_existing():
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("items", [])
    return None


def _parse_float(val):
    try:
        return round(float(val), 4)
    except (TypeError, ValueError):
        return None


def _join_way_label(codes):
    mapping = {"1": "인터넷", "2": "앱", "3": "인터넷/앱", "4": "영업점", "5": "전화(ARS)"}
    if any(c.strip() in ("2", "3") for c in codes):
        return "인터넷/앱"
    if "1" in [c.strip() for c in codes]:
        return "인터넷"
    return mapping.get(codes[0].strip(), "영업점") if codes else "영업점"


def _is_parking(prod_name, save_trm):
    name = str(prod_name)
    if any(kw in name for kw in PARKING_KEYWORDS):
        return True
    try:
        if int(save_trm) == 0:
            return True
    except (TypeError, ValueError):
        pass
    return False


def fetch():
    api_key = os.environ.get("FSS_API_KEY", "")
    params = {"auth": api_key, "topFinGrpNo": "020000", "pageNo": 1}
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    result = data.get("result", {})
    base_list = result.get("baseList", [])
    option_list = result.get("optionList", [])

    rate_map = {}
    base_rate_map = {}
    period_map = {}
    for opt in option_list:
        cd = opt.get("fin_prdt_cd")
        max_r = _parse_float(opt.get("intr_rate2"))
        base_r = _parse_float(opt.get("intr_rate"))
        period = opt.get("save_trm")
        if cd is None:
            continue
        if max_r is not None and (cd not in rate_map or max_r > rate_map[cd]):
            rate_map[cd] = max_r
            base_rate_map[cd] = base_r or 0.0
            try:
                period_map[cd] = int(period)
            except (TypeError, ValueError):
                period_map[cd] = 0

    today = str(date.today())
    products = []
    for prod in base_list:
        cd = prod.get("fin_prdt_cd")
        prod_name = prod.get("fin_prdt_nm", "")
        save_trm = period_map.get(cd, 12)
        if not _is_parking(prod_name, save_trm):
            continue
        max_r = rate_map.get(cd)
        if max_r is None:
            continue
        join_codes = str(prod.get("join_way", "")).split(",")
        firm = prod.get("kor_co_nm", "")
        products.append({
            "firm": firm,
            "product_name": prod_name,
            "bank_type": "인터넷은행" if firm in INTERNET_BANKS else "시중은행",
            "rate": max_r,
            "base_rate": base_rate_map.get(cd, 0.0),
            "protection": True,
            "join_channel": _join_way_label(join_codes),
            "as_of": today,
        })

    products.sort(key=lambda x: x["rate"], reverse=True)
    top10 = products[:10]
    for i, p in enumerate(top10, 1):
        p["rank"] = i
    return top10


def main():
    items = None
    try:
        items = fetch()
        if not items:
            raise ValueError("Empty result from API")
    except Exception as e:
        print(f"[WARN] FSS API fetch failed: {e}")

    if items:
        _save(items)
        print(f"[OK] Saved {len(items)} parking items → {OUT_PATH}")
        return

    existing = _load_existing()
    if existing:
        print("[WARN] Using existing cached data (stale).")
        _save(existing, stale=True)
    else:
        print("[WARN] No live data and no cache - using hardcoded fallback.")
        _save(FALLBACK_ITEMS, stale=True)


if __name__ == "__main__":
    main()
