import time

import app


def test_api_rejects_unknown_type():
    response = app.app.test_client().get("/api/data?type=invalid")
    assert response.status_code == 400


def test_get_uses_cache(monkeypatch):
    calls = []

    def fake_fetch():
        calls.append(1)
        return [{"symbol": "TEST"}]

    app._cache["crypto"] = {"t": 0, "data": [], "error": None}
    app._refreshing.clear()
    monkeypatch.setattr(app, "fetch_crypto", fake_fetch)

    first, error, updated = app._get("crypto")
    second, error2, updated2 = app._get("crypto")

    assert first == second == [{"symbol": "TEST"}]
    assert error is None and error2 is None
    assert updated == updated2
    assert len(calls) == 1


def test_get_returns_stale_data_on_fetch_error(monkeypatch):
    app._cache["crypto"] = {
        "t": time.time() - app.TTL_CRYPTO - 1,
        "data": [{"symbol": "STALE"}],
        "error": None,
    }
    app._refreshing.clear()

    def fail_fetch():
        raise RuntimeError("upstream failure")

    monkeypatch.setattr(app, "fetch_crypto", fail_fetch)

    data, error, updated = app._get("crypto")

    assert data == [{"symbol": "STALE"}]
    assert error == "Sumber data sementara tidak tersedia."
    assert updated < time.time()
