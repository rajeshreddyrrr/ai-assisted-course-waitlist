from fastapi.testclient import TestClient

import api


def test_api_enroll_waitlist_drop_promotes_and_persists(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DB_PATH", tmp_path / "test-courseflow.db")
    client = TestClient(api.app)

    assert client.get("/api/health").json()["status"] == "ok"
    assert client.post("/api/capacity", json={"capacity": 1}).status_code == 200

    first = client.post("/api/enroll", json={"learner_id": "Ava"}).json()
    second = client.post("/api/enroll", json={"learner_id": "Noah"}).json()
    assert first["code"] == "enrolled"
    assert second["code"] == "waitlisted"
    assert second["state"]["waitlist"] == ["Noah"]

    dropped = client.post("/api/drop", json={"learner_id": "Ava"}).json()
    assert dropped["code"] == "dropped"
    assert dropped["state"]["enrolled"] == ["Noah"]
    assert dropped["state"]["waitlist"] == []

    # A fresh state read loads the same values from SQLite.
    saved = client.get("/api/state").json()
    assert saved["enrolled"] == ["Noah"]
    assert saved["waitlist"] == []


def test_api_capacity_increase_fills_multiple_seats_in_fifo_order(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DB_PATH", tmp_path / "test-courseflow.db")
    client = TestClient(api.app)
    client.post("/api/capacity", json={"capacity": 1})
    client.post("/api/enroll", json={"learner_id": "Ava"})
    client.post("/api/enroll", json={"learner_id": "Noah"})
    client.post("/api/enroll", json={"learner_id": "Mia"})

    result = client.post("/api/capacity", json={"capacity": 3})
    assert result.status_code == 200
    assert result.json()["state"]["enrolled"] == ["Ava", "Noah", "Mia"]
    assert result.json()["state"]["waitlist"] == []


def test_api_prerequisite_validation_and_waitlist_refresh(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DB_PATH", tmp_path / "test-courseflow.db")
    client = TestClient(api.app)
    client.post("/api/eligibility", json={"eligible_ids": ["Ava"]})
    response = client.post("/api/enroll", json={"learner_id": "Noah"})
    assert response.json()["code"] == "prerequisite_not_met"
    assert response.json()["state"]["enrolled"] == []
    assert response.json()["state"]["waitlist"] == []

    client.post("/api/eligibility", json={"eligible_ids": ["Ava", "Noah"]})
    client.post("/api/capacity", json={"capacity": 0})
    client.post("/api/enroll", json={"learner_id": "Ava"})
    client.post("/api/enroll", json={"learner_id": "Noah"})
    refreshed = client.post("/api/capacity", json={"capacity": 2}).json()["state"]
    assert refreshed["enrolled"] == ["Ava", "Noah"]
    assert refreshed["waitlist"] == []


def test_api_rejects_capacity_below_current_enrollment(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DB_PATH", tmp_path / "test-courseflow.db")
    client = TestClient(api.app)
    client.post("/api/capacity", json={"capacity": 2})
    client.post("/api/enroll", json={"learner_id": "Ava"})
    response = client.post("/api/capacity", json={"capacity": 0})
    assert response.status_code == 409
