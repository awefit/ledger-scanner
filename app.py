"""Flask app: API lokal + UI web untuk Ledger Scanner."""
import threading
import time

from flask import Flask, jsonify, render_template, request

from src.crypto_source import fetch_crypto
from src.idx_source import fetch_idx

app = Flask(__name__)

TTL_CRYPTO = 60
TTL_STOCK = 120
_cache = {
    "crypto": {"t": 0, "data": [], "error": None},
    "stock": {"t": 0, "data": [], "error": None},
}
_lock = threading.Lock()
_refreshing = set()


def _fetch(kind):
    return fetch_crypto() if kind == "crypto" else fetch_idx()


def _get(kind):
    """Read cache and refresh stale data without holding the lock during I/O."""
    if kind not in _cache:
        raise ValueError(f"unknown cache kind: {kind}")

    ttl = TTL_CRYPTO if kind == "crypto" else TTL_STOCK
    now = time.time()

    with _lock:
        entry = _cache[kind]
        if now - entry["t"] <= ttl:
            return entry["data"], entry["error"], entry["t"]

        if kind in _refreshing:
            return entry["data"], entry["error"], entry["t"]

        _refreshing.add(kind)
        old_data, old_t = entry["data"], entry["t"]

    try:
        data = _fetch(kind)
    except Exception:
        with _lock:
            entry = _cache[kind]
            entry["error"] = "Sumber data sementara tidak tersedia."
            _refreshing.discard(kind)
            return old_data, entry["error"], old_t

    with _lock:
        entry = _cache[kind]
        entry["data"] = data
        entry["t"] = time.time()
        entry["error"] = None
        _refreshing.discard(kind)
        return entry["data"], None, entry["t"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    kind = request.args.get("type", "all")
    if kind not in {"all", "crypto", "stock"}:
        return jsonify({"error": "type harus all, crypto, atau stock"}), 400

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
