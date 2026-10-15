def test_health_returns_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_health_method_not_allowed(client):
    res = client.post("/health")
    assert res.status_code == 405
