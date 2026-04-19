# ETF 시세 수집 - FinanceDataReader / pykrx (단기채권 파킹형 ETF)
import json
import os
from datetime import date, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_PATH = os.path.join(DATA_DIR, "etf.json")
SOURCE_URL = "https://finance.naver.com"

ETF_LIST = [
    {"ticker": "449170", "name": "KODEX KOFR금리액티브(합성)"},
    {"ticker": "453850", "name": "TIGER CD금리투자KIS(합성)"},
    {"ticker": "461980", "name": "KODEX CD금리액티브(합성)"},
    {"ticker": "494030", "name": "KBSTAR 머니마켓액티브"},
]

FALLBACK_ITEMS = [
    {"rank": 1, "ticker": "449170", "name": "KODEX KOFR금리액티브(합성)", "close": 103250, "prev_close": 103240, "change": 10,  "change_pct": 0.0097, "as_of": "2026-04-18"},
    {"rank": 2, "ticker": "453850", "name": "TIGER CD금리투자KIS(합성)", "close": 104380, "prev_close": 104370, "change": 10,  "change_pct": 0.0096, "as_of": "2026-04-18"},
    {"rank": 3, "ticker": "461980", "name": "KODEX CD금리액티브(합성)",  "close": 102150, "prev_close": 102140, "change": 10,  "change_pct": 0.0098, "as_of": "2026-04-18"},
    {"rank": 4, "ticker": "494030", "name": "KBSTAR 머니마켓액티브",     "close": 101200, "prev_close": 101190, "change": 10,  "change_pct": 0.0099, "as_of": "2026-04-18"},
]


def _save(items, stale=False):
    os.makedirs(DATA_DIR, exist_ok=True)
    payload = {
        "updated_at": str(date.today()),
        "source": "FinanceDataReader / KRX",
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


def _fetch_with_fdr():
    import FinanceDataReader as fdr
    end = date.today()
    start = end - timedelta(days=35)
    items = []
    for i, etf in enumerate(ETF_LIST, 1):
        df = fdr.DataReader(etf["ticker"], start=str(start), end=str(end))
        if df is None or df.empty:
            continue
        df = df.sort_index()
        last = df.iloc[-1]
        close = int(last.get("Close", last.iloc[0]))
        prev_close = int(df.iloc[-2]["Close"]) if len(df) >= 2 else close
        change = close - prev_close
        change_pct = round(change / prev_close * 100, 4) if prev_close else 0.0
        items.append({
            "rank": i,
            "ticker": etf["ticker"],
            "name": etf["name"],
            "close": close,
            "prev_close": prev_close,
            "change": change,
            "change_pct": change_pct,
            "as_of": str(df.index[-1].date()),
        })
    return items if items else None


def _fetch_with_pykrx():
    from pykrx import stock
    end = date.today()
    start = end - timedelta(days=35)
    items = []
    for i, etf in enumerate(ETF_LIST, 1):
        df = stock.get_market_ohlcv_by_date(
            start.strftime("%Y%m%d"), end.strftime("%Y%m%d"), etf["ticker"]
        )
        if df is None or df.empty:
            continue
        df = df.sort_index()
        close = int(df.iloc[-1]["종가"])
        prev_close = int(df.iloc[-2]["종가"]) if len(df) >= 2 else close
        change = close - prev_close
        change_pct = round(change / prev_close * 100, 4) if prev_close else 0.0
        items.append({
            "rank": i,
            "ticker": etf["ticker"],
            "name": etf["name"],
            "close": close,
            "prev_close": prev_close,
            "change": change,
            "change_pct": change_pct,
            "as_of": str(df.index[-1].date()),
        })
    return items if items else None


def main():
    items = None

    try:
        items = _fetch_with_fdr()
    except Exception as e:
        print(f"[WARN] FinanceDataReader fetch failed: {e}")

    if not items:
        try:
            items = _fetch_with_pykrx()
        except Exception as e:
            print(f"[WARN] pykrx fetch failed: {e}")

    if items:
        _save(items)
        print(f"[OK] Saved {len(items)} ETF items → {OUT_PATH}")
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
