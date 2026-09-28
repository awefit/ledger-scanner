# Ledger Scanner

Screener gabungan **crypto** dan **saham BEI** (Yahoo Finance, ticker `.JK`), dijalankan lokal.

Data diambil di sisi server (Python), jadi bisa live dan otomatis tanpa batasan CORS browser.

## Struktur

```
ledger-scanner/
├── requirements.txt
├── app.py                 # Flask: API lokal + UI web
├── src/
│   ├── crypto_source.py   # public crypto market-data API
│   ├── idx_source.py      # BEI via yfinance (.JK)
│   └── screener.py        # gabung + filter + sort (CLI)
└── templates/index.html
```

## Menjalankan

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# CLI
python -m src.screener --type crypto --sort market_cap --top 20
python -m src.screener --type stock --sort change_24h_pct --top 20
python -m src.screener --type all --min-change 5

# Web app
python app.py                  # http://127.0.0.1:5000
```

## Catatan

- Crypto: default top 250 by market cap. Ubah `PAGES` di `crypto_source.py` untuk lebih banyak; ada jeda antar halaman untuk mengurangi risiko rate limit.
- Saham BEI: `DEFAULT_TICKERS` di `idx_source.py` berisi ~50 saham blue-chip likuid, **bukan** daftar resmi LQ45 terkini. Tambahkan kode saham lain sesuai kebutuhan (tanpa `.JK`).
- Mata uang: crypto dalam USD, saham dalam IDR. Market cap dan volume tidak dibandingkan lintas mata uang.
- Bukan nasihat investasi. Data pihak ketiga, bisa tertunda.
