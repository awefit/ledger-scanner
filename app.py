"""Flask app: API lokal + UI web untuk Ledger Scanner."""
import threading
import time

from flask import Flask, jsonify, render_template, request

from src.crypto_source import fetch_crypto
from src.idx_source import fetch_idx

app = Flask(__name__)

TTL_CRYPTO = 60    # detik
TTL_STOCK = 120
_cache = {"crypto": {"t": 0, "data": []}, "stock": {"t": 0, "data": []}}
_lock = threading.Lock()


def _get(kind):
    ttl = TTL_CRYPTO if kind == "crypto" else TTL_STOCK
    with _lock:
        entry = _cache[kind]
        if time.time() - entry["t"] > ttl:
            try:
                entry["data"] = fetch_crypto() if kind == "crypto" else fetch_idx()
                entry["t"] = time.time()
                entry["error"] = None
            except Exception as e:  # tetap tampilkan data lama kalau ada
                entry["error"] = str(e)
        return entry["data"], entry.get("error"), entry["t"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    kind = request.args.get("type", "all")
    rows, errors, updated = [], {}, {}
    for k in ("crypto", "stock"):
        if kind in ("all", k):
            data, err, t = _get(k)
            rows += data
            updated[k] = t
            if err:
                errors[k] = err
    return jsonify({"rows": rows, "errors": errors, "updated": updated})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
