"""Gabung data crypto + saham BEI, lalu filter dan sort. Bisa dipakai sebagai CLI."""
import argparse
import pandas as pd

from .crypto_source import fetch_crypto
from .idx_source import fetch_idx


def load(kind="all"):
    rows = []
    if kind in ("all", "crypto"):
        rows += fetch_crypto()
    if kind in ("all", "stock"):
        rows += fetch_idx()
    return rows


def screen(rows, min_change=None, max_change=None, min_cap=None, query=None):
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if min_change is not None:
        df = df[df["change_24h_pct"] >= min_change]
    if max_change is not None:
        df = df[df["change_24h_pct"] <= max_change]
    if min_cap is not None:
        df = df[df["market_cap"] >= min_cap]
    if query:
        q = query.lower()
        df = df[df["symbol"].str.lower().str.contains(q) | df["name"].str.lower().str.contains(q, na=False)]
    return df


def main():
    p = argparse.ArgumentParser(description="Ledger Scanner - crypto + saham BEI")
    p.add_argument("--type", choices=["all", "crypto", "stock"], default="all")
    p.add_argument("--sort", default="market_cap",
                   choices=["market_cap", "price", "volume_24h", "change_24h_pct", "change_7d_pct"])
    p.add_argument("--asc", action="store_true", help="urut naik (default turun)")
    p.add_argument("--top", type=int, default=25)
    p.add_argument("--min-change", type=float, help="minimal %% perubahan 24j")
    p.add_argument("--max-change", type=float, help="maksimal %% perubahan 24j")
    p.add_argument("--min-cap", type=float, help="minimal market cap (satuan mata uang aset)")
    p.add_argument("--search", help="cari nama/simbol")
    a = p.parse_args()

    df = screen(load(a.type), a.min_change, a.max_change, a.min_cap, a.search)
    if df.empty:
        print("Tidak ada hasil.")
        return
    df = df.sort_values(a.sort, ascending=a.asc, na_position="last").head(a.top)
    cols = ["type", "symbol", "name", "currency", "price", "change_24h_pct", "change_7d_pct", "market_cap", "volume_24h"]
    pd.set_option("display.width", 200)
    pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
    print(df[cols].to_string(index=False))


if __name__ == "__main__":
    main()
