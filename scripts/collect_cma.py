# CMA 금리 수집 - KOFIA 금융투자협회 전자공시 (http://dis.kofia.or.kr)
import json
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_PATH = os.path.join(DATA_DIR, "cma.json")
SOURCE_URL = "http://dis.kofia.or.kr"
TARGET_URL = "https://dis.kofia.or.kr/websquare/popup.do?w2xPath=/wq/cmpny/DISCMACmpnyInq.xml"

TARGET_FIRMS = {
    "한국투자증권", "미래에셋증권", "NH투자증권", "KB증권",
    "삼성증권", "신한투자증권", "키움증권", "대신증권",
}

FALLBACK_ITEMS = [
    {"rank": 1, "firm": "한국투자증권", "product_type": "발행어음형", "rate": 4.35, "change": 0.10, "as_of": "2026-04-18"},
    {"rank": 2, "firm": "미래에셋증권", "product_type": "RP형",      "rate": 4.20, "change": 0.00, "as_of": "2026-04-18"},
    {"rank": 3, "firm": "NH투자증권",   "product_type": "발행어음형", "rate": 4.18, "change": -0.05, "as_of": "2026-04-18"},
    {"rank": 4, "firm": "KB증권",       "product_type": "RP형",      "rate": 4.15, "change": 0.00, "as_of": "2026-04-18"},
    {"rank": 5, "firm": "삼성증권",     "product_type": "RP형",      "rate": 4.10, "change": 0.05, "as_of": "2026-04-18"},
    {"rank": 6, "firm": "신한투자증권", "product_type": "RP형",      "rate": 4.08, "change": 0.00, "as_of": "2026-04-18"},
    {"rank": 7, "firm": "키움증권",     "product_type": "RP형",      "rate": 4.05, "change": 0.00, "as_of": "2026-04-18"},
    {"rank": 8, "firm": "대신증권",     "product_type": "RP형",      "rate": 4.00, "change": -0.05, "as_of": "2026-04-18"},
]


def _save(items, stale=False):
    os.makedirs(DATA_DIR, exist_ok=True)
    payload = {
        "updated_at": str(date.today()),
        "source": "KOFIA 전자공시",
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


def _parse_rate(val):
    try:
        return round(float(str(val).replace("%", "").replace(",", "").strip()), 4)
    except (ValueError, TypeError):
        return None


def _fetch_with_pandas():
    import pandas as pd
    # KOFIA 공시 메인 페이지 — CMA 금리 테이블
    tables = pd.read_html(TARGET_URL, encoding="utf-8", flavor="bs4")
    items = []
    today = str(date.today())
    rank = 1
    for tbl in tables:
        tbl.columns = [str(c) for c in tbl.columns]
        for _, row in tbl.iterrows():
            row_str = " ".join(str(v) for v in row.values)
            matched_firm = next((f for f in TARGET_FIRMS if f in row_str), None)
            if not matched_firm:
                continue
            product_type = "발행어음형" if "발행어음" in row_str else "RP형"
            # try to extract a numeric rate from any column
            rate = None
            for v in row.values:
                r = _parse_rate(v)
                if r and 0.1 < r < 20:
                    rate = r
                    break
            if rate is None:
                continue
            items.append({
                "rank": rank,
                "firm": matched_firm,
                "product_type": product_type,
                "rate": rate,
                "change": 0.0,
                "as_of": today,
            })
            rank += 1
    return items if items else None


def _fetch_with_bs4():
    import requests
    from bs4 import BeautifulSoup

    headers = {"User-Agent": "Mozilla/5.0 (compatible; deposit-collector/1.0)"}
    resp = requests.get(TARGET_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    today = str(date.today())
    items = []
    rank = 1
    for row in soup.find_all("tr"):
        text = row.get_text(" ", strip=True)
        matched_firm = next((f for f in TARGET_FIRMS if f in text), None)
        if not matched_firm:
            continue
        product_type = "발행어음형" if "발행어음" in text else "RP형"
        rate = None
        for td in row.find_all("td"):
            r = _parse_rate(td.get_text(strip=True))
            if r and 0.1 < r < 20:
                rate = r
                break
        if rate is None:
            continue
        items.append({
            "rank": rank,
            "firm": matched_firm,
            "product_type": product_type,
            "rate": rate,
            "change": 0.0,
            "as_of": today,
        })
        rank += 1
    return items if items else None


def main():
    items = None

    try:
        items = _fetch_with_pandas()
    except Exception as e:
        print(f"[WARN] pandas.read_html failed: {e}")

    if not items:
        try:
            items = _fetch_with_bs4()
        except Exception as e:
            print(f"[WARN] BeautifulSoup fetch failed: {e}")

    if items:
        _save(items)
        print(f"[OK] Saved {len(items)} CMA items → {OUT_PATH}")
        return

    # stale fallback
    existing = _load_existing()
    if existing:
        print("[WARN] Using existing cached data (stale).")
        _save(existing, stale=True)
    else:
        print("[WARN] No live data and no cache - using hardcoded fallback.")
        _save(FALLBACK_ITEMS, stale=True)


if __name__ == "__main__":
    main()
