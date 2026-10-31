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



def test_api_add_learner_persists_and_sets_optional_eligibility(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DB_PATH", tmp_path / "test-courseflow.db")
    client = TestClient(api.app)

    response = client.post(
        "/api/learners",
        json={"learner_name": "Jordan Lee", "eligible": True},
    )
    assert response.status_code == 200
    state = response.json()["state"]
    assert "Jordan Lee" in state["learners"]
    assert "Jordan Lee" in state["eligible_ids"]
    assert "Jordan Lee added successfully" in response.json()["message"]

    persisted = client.get("/api/state").json()
    assert "Jordan Lee" in persisted["learners"]
    assert "Jordan Lee" in persisted["eligible_ids"]



def test_api_add_learner_rejects_duplicate_name_case_insensitively(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DB_PATH", tmp_path / "test-courseflow.db")
    client = TestClient(api.app)

    assert client.post(
        "/api/learners",
        json={"learner_name": "Test Learner Duplicate"},
    ).status_code == 200

    duplicate = client.post(
        "/api/learners",
        json={"learner_name": "  tEsT lEaRnEr DuPlIcAtE  "},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "That learner already exists."


def test_api_allows_ineligible_waitlist_and_drop_promotes_next_eligible(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "DB_PATH", tmp_path / "test-courseflow.db")
    client = TestClient(api.app)

    client.post("/api/capacity", json={"capacity": 1})
    # Noah is ineligible from the beginning; Ava and Mia are eligible.
    client.post("/api/eligibility", json={"eligible_ids": ["Ava", "Mia"]})

    assert client.post("/api/enroll", json={"learner_id": "Ava"}).json()["code"] == "enrolled"
    ineligible = client.post("/api/enroll", json={"learner_id": "Noah"}).json()
    assert ineligible["code"] == "waitlisted"
    assert ineligible["state"]["waitlist"] == ["Noah"]

    eligible = client.post("/api/enroll", json={"learner_id": "Mia"}).json()
    assert eligible["code"] == "waitlisted"
    assert eligible["state"]["waitlist"] == ["Noah", "Mia"]

    # When Ava drops, Noah is skipped and retained; Mia takes the vacant seat.
    dropped = client.post("/api/drop", json={"learner_id": "Ava"}).json()
    assert dropped["code"] == "dropped"
    assert dropped["state"]["enrolled"] == ["Mia"]
    assert dropped["state"]["waitlist"] == ["Noah"]

    saved = client.get("/api/state").json()
    assert saved["enrolled"] == ["Mia"]
    assert saved["waitlist"] == ["Noah"]
