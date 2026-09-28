"""Ambil data saham BEI via Yahoo Finance (ticker berakhiran .JK)."""
import yfinance as yf

# Seed watchlist: saham blue-chip likuid. Bukan daftar resmi LQ45 terkini.
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


def fetch_idx(tickers=None, with_market_cap=True):
    tickers = tickers or DEFAULT_TICKERS
    symbols = [f"{t}.JK" for t in tickers]
    data = yf.download(
        tickers=symbols, period="10d", interval="1d",
        group_by="ticker", threads=True, progress=False, auto_adjust=False,
    )
    rows = []
    for t, sym in zip(tickers, symbols):
        try:
            hist = (data[sym] if len(symbols) > 1 else data).dropna(subset=["Close"])
            if hist.empty:
                continue
            last = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else None
            change_24h = None
            if prev is not None and prev["Close"]:
                change_24h = (last["Close"] - prev["Close"]) / prev["Close"] * 100
            change_7d = None
            if len(hist) >= 6 and hist.iloc[-6]["Close"]:
                change_7d = (last["Close"] - hist.iloc[-6]["Close"]) / hist.iloc[-6]["Close"] * 100
            market_cap = None
            if with_market_cap:
                try:
                    market_cap = yf.Ticker(sym).fast_info.get("market_cap")
                except Exception:
                    market_cap = None
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
                "market_cap": market_cap,
                "volume_24h": price * volume_shares,  # perkiraan nilai transaksi (IDR)
                "rank": None,
            })
        except Exception:
            continue
    return rows
