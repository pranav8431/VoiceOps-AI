import jwt


def test_create_token_default_identity(client):
    res = client.post("/api/token", json={"room": "test-room"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert "url" in data
    assert data["url"] == "ws://localhost:7880"

    claims = jwt.decode(data["token"], options={"verify_signature": False})
    assert claims["sub"].startswith("user-")
    video = claims.get("video", {})
    assert video.get("room") == "test-room"
    assert video.get("roomJoin") is True


def test_create_token_custom_identity(client):
    res = client.post(
        "/api/token", json={"identity": "pranav", "room": "voicd-room"}
    )
    assert res.status_code == 200
    data = res.json()

    claims = jwt.decode(data["token"], options={"verify_signature": False})
    assert claims["sub"] == "pranav"


def test_create_token_default_room(client):
    res = client.post("/api/token", json={})
    assert res.status_code == 200
    data = res.json()

    claims = jwt.decode(data["token"], options={"verify_signature": False})
    video = claims.get("video", {})
    assert video.get("room") == "voicd-room"


def test_create_token_invalid_body(client):
    res = client.post("/api/token", content=b"not json", headers={"Content-Type": "application/json"})
    assert res.status_code == 422


def test_token_contains_required_jwt_fields(client):
    res = client.post("/api/token", json={})
    data = res.json()
    claims = jwt.decode(data["token"], options={"verify_signature": False})
    assert "iss" in claims
    assert "sub" in claims
    assert "exp" in claims
    assert "video" in claims


def test_token_grants_are_minimal(client):
    res = client.post("/api/token", json={})
    data = res.json()
    claims = jwt.decode(data["token"], options={"verify_signature": False})
    video = claims["video"]
    assert video.get("roomJoin") is True
    assert video.get("roomAdmin", False) is False
