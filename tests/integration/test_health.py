from datetime import datetime, timezone


def test_health_returns_ok_and_a_current_utc_time(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    stamp = datetime.fromisoformat(body["timestamp"].replace("Z", "+00:00"))
    assert stamp.tzinfo is not None
    assert abs((datetime.now(timezone.utc) - stamp).total_seconds()) < 60
