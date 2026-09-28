"""Ambil data saham BEI via Yahoo Finance (ticker berakhiran .JK)."""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import yfinance as yf

logger = logging.getLogger(__name__)

DEFAULT_TICKERS = [
    "BBCA", "BBRI", "BBNI", "BMRI", "BBTN", "BRIS", "ARTO",
    "ASII", "TLKM", "EXCL", "ISAT", "TOWR", "TBIG",
    "UNVR", "ICBP", "INDF", "GGRM", "HMSP", "KLBF", "SIDO", "CPIN", "JPFA",
    "AMRT", "MAPI", "ACES", "ERAA",
    "ANTM", "INCO", "MDKA", "AMMN", "MBMA",
    "ADRO", "PTBA", "ITMG", "MEDC", "PGAS", "AKRA",
    "SMGR", "INTP", "TPIA", "BRPT",
    "CTRA", "BSDE", "PWON", "SMRA", "JSMR",
    "GOTO", "BUKA", "EMTK", "MNCN", "SCMA",
]


def _market_cap(symbol):
    try:
        return yf.Ticker(symbol).fast_info.get("market_cap")
    except Exception:
        logger.warning("market cap unavailable for %s", symbol, exc_info=True)
        return None


def fetch_idx(tickers=None, with_market_cap=True):
    tickers = tickers or DEFAULT_TICKERS
    symbols = [f"{t}.JK" for t in tickers]
    data = yf.download(
        tickers=symbols,
        period="10d",
        interval="1d",
        group_by="ticker",
        threads=True,
        progress=False,
        auto_adjust=False,
    )

    market_caps = {}
    if with_market_cap:
        # Bounded concurrency avoids a long serial chain of network requests.
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(_market_cap, sym): sym for sym in symbols}
            for future in as_completed(futures):
                market_caps[futures[future]] = future.result()

    rows = []
    for t, sym in zip(tickers, symbols):
        try:
            hist = (data[sym] if len(symbols) > 1 else data).dropna(subset=["Close"])
            if hist.empty:
                logger.warning("no price data for %s", sym)
                continue

            last = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else None
            change_24h = None
            if prev is not None and prev["Close"]:
                change_24h = (last["Close"] - prev["Close"]) / prev["Close"] * 100

            change_7d = None
            if len(hist) >= 6 and hist.iloc[-6]["Close"]:
                change_7d = (last["Close"] - hist.iloc[-6]["Close"]) / hist.iloc[-6]["Close"] * 100

            price = float(last["Close"])
            volume_shares = float(last["Volume"])
            rows.append({
                "type": "stock",
                "symbol": t,
                "name": t,
                "currency": "IDR",
                "price": price,
                "change_1h_pct": None,
                "change_24h_pct": change_24h,
                "change_7d_pct": change_7d,
                "market_cap": market_caps.get(sym),
                "volume_24h": price * volume_shares,
                "rank": None,
            })
        except Exception:
            logger.warning("failed to build row for %s", sym, exc_info=True)
            continue
    return rows
