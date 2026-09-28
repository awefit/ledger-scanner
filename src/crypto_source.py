"""Ambil data crypto dari public market-data API."""
import time
import requests

URL = "https://api.coingecko.com/api/v3/coins/markets"
PER_PAGE = 250
PAGES = 1          # 1 halaman = top 250. Naikkan untuk lebih banyak.
PAGE_DELAY = 6.0   # detik, hindari rate limit tier gratis


def fetch_crypto(vs_currency="usd", pages=PAGES):
    rows = []
    for page in range(1, pages + 1):
        resp = requests.get(
            URL,
            params={
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": PER_PAGE,
                "page": page,
                "sparkline": "false",
                "price_change_percentage": "1h,24h,7d",
            },
            timeout=20,
        )
        resp.raise_for_status()
        for c in resp.json():
            rows.append({
                "type": "crypto",
                "symbol": (c.get("symbol") or "").upper(),
                "name": c.get("name"),
                "currency": vs_currency.upper(),
                "price": c.get("current_price"),
                "change_1h_pct": c.get("price_change_percentage_1h_in_currency"),
                "change_24h_pct": c.get("price_change_percentage_24h_in_currency"),
                "change_7d_pct": c.get("price_change_percentage_7d_in_currency"),
                "market_cap": c.get("market_cap"),
                "volume_24h": c.get("total_volume"),
                "rank": c.get("market_cap_rank"),
            })
        if page < pages:
            time.sleep(PAGE_DELAY)
    return rows
