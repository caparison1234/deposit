# 정기예금 금리 수집 - 금융감독원 금융상품통합비교공시 API (https://finlife.fss.or.kr)
import json
import os
from datetime import date

import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_PATH = os.path.join(DATA_DIR, "deposit.json")
BASE_URL = "https://finlife.fss.or.kr/finLifeApi/api/depositProductsSearch.json"
SOURCE_URL = "https://finlife.fss.or.kr"

FALLBACK_ITEMS = [
    {"rank": 1,  "firm": "한국카카오은행",  "product_name": "카카오뱅크 정기예금",         "base_rate": 3.50, "max_rate": 4.20, "period_months": 12, "protection": True,  "join_channel": "앱"},
    {"rank": 2,  "firm": "케이뱅크",        "product_name": "코드K 정기예금",              "base_rate": 3.45, "max_rate": 4.15, "period_months": 12, "protection": True,  "join_channel": "앱"},
    {"rank": 3,  "firm": "토스뱅크",        "product_name": "토스뱅크 정기예금",           "base_rate": 3.40, "max_rate": 4.10, "period_months": 12, "protection": True,  "join_channel": "앱"},
    {"rank": 4,  "firm": "KB국민은행",      "product_name": "KB Star 정기예금",            "base_rate": 3.70, "max_rate": 4.05, "period_months": 12, "protection": True,  "join_channel": "인터넷/앱"},
    {"rank": 5,  "firm": "신한은행",        "product_name": "쏠편한 정기예금",             "base_rate": 3.65, "max_rate": 4.00, "period_months": 12, "protection": True,  "join_channel": "인터넷/앱"},
    {"rank": 6,  "firm": "하나은행",        "product_name": "하나의 정기예금",             "base_rate": 3.60, "max_rate": 3.95, "period_months": 12, "protection": True,  "join_channel": "인터넷/앱"},
    {"rank": 7,  "firm": "우리은행",        "product_name": "WON 정기예금",                "base_rate": 3.55, "max_rate": 3.90, "period_months": 12, "protection": True,  "join_channel": "인터넷/앱"},
    {"rank": 8,  "firm": "NH농협은행",      "product_name": "NH왈츠회전예금 II",          "base_rate": 3.50, "max_rate": 3.85, "period_months": 12, "protection": True,  "join_channel": "인터넷/앱"},
    {"rank": 9,  "firm": "IBK기업은행",     "product_name": "IBK D-Day 통장",              "base_rate": 3.45, "max_rate": 3.80, "period_months": 12, "protection": True,  "join_channel": "인터넷/앱"},
    {"rank": 10, "firm": "SC제일은행",      "product_name": "e-그린세이브 예금",           "base_rate": 3.30, "max_rate": 3.75, "period_months": 12, "protection": True,  "join_channel": "인터넷"},
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


def _join_way_label(code):
    mapping = {"1": "인터넷", "2": "앱", "3": "인터넷/앱", "4": "영업점", "5": "전화(ARS)"}
    return mapping.get(str(code), str(code))


def fetch():
    api_key = os.environ.get("FSS_API_KEY", "")
    params = {
        "auth": api_key,
        "topFinGrpNo": "020000",
        "pageNo": 1,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    # response envelope: result > baseList (상품) + optionList (금리옵션)
    result = data.get("result", {})
    base_list = result.get("baseList", [])
    option_list = result.get("optionList", [])

    # build a map of fin_prdt_cd → max maxRate across all options
    rate_map = {}
    base_rate_map = {}
    period_map = {}
    for opt in option_list:
        cd = opt.get("fin_prdt_cd")
        max_r = _parse_float(opt.get("intr_rate2"))  # 우대금리
        base_r = _parse_float(opt.get("intr_rate"))   # 기본금리
        period = opt.get("save_trm")                   # 저축기간(개월)
        if cd is None:
            continue
        # prefer the option with the highest max_rate
        if max_r is not None and (cd not in rate_map or max_r > rate_map[cd]):
            rate_map[cd] = max_r
            base_rate_map[cd] = base_r or 0.0
            try:
                period_map[cd] = int(period)
            except (TypeError, ValueError):
                period_map[cd] = 12

    # attach rates to products and sort
    products = []
    for prod in base_list:
        cd = prod.get("fin_prdt_cd")
        max_r = rate_map.get(cd)
        if max_r is None:
            continue
        join_codes = str(prod.get("join_way", "")).split(",")
        # pick the most convenient channel label
        if any(c.strip() in ("2", "3") for c in join_codes):
            channel = "인터넷/앱"
        elif "1" in [c.strip() for c in join_codes]:
            channel = "인터넷"
        else:
            channel = _join_way_label(join_codes[0].strip()) if join_codes else "영업점"

        products.append({
            "firm": prod.get("kor_co_nm", ""),
            "product_name": prod.get("fin_prdt_nm", ""),
            "base_rate": base_rate_map.get(cd, 0.0),
            "max_rate": max_r,
            "period_months": period_map.get(cd, 12),
            "protection": True,  # 020000 = 은행권, 모두 예금자보호 적용
            "join_channel": channel,
        })

    products.sort(key=lambda x: x["max_rate"], reverse=True)
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
        print(f"[OK] Saved {len(items)} deposit items → {OUT_PATH}")
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
