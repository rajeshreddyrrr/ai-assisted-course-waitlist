"""FastAPI endpoints for the React CourseFlow dashboard with SQLite persistence."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from threading import RLock
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from course_waitlist import CourseOffering, EnrollmentService, ResultCode

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "course_waitlist.db"
DEFAULT_LEARNERS = ["Ava", "Noah", "Mia", "Liam", "Zoe", "Ethan", "Ivy", "Leo", "Aria", "Kai"]
LOCK = RLock()
app = FastAPI(title="CourseFlow API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EnrollRequest(BaseModel):
    learner_id: str = Field(min_length=1, max_length=100)


class AddLearnerRequest(BaseModel):
    learner_name: str = Field(min_length=1, max_length=100)
    eligible: bool = False


class CapacityRequest(BaseModel):
    capacity: int = Field(ge=0, le=500)


class EligibilityRequest(BaseModel):
    eligible_ids: list[str]


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS app_state "
        "(id INTEGER PRIMARY KEY CHECK (id = 1), payload TEXT NOT NULL)"
    )
    return connection


def load_state() -> dict[str, Any]:
    with connect() as connection:
        row = connection.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
        if row:
            saved = json.loads(row[0])
            learners = list(dict.fromkeys(saved.get("learners", DEFAULT_LEARNERS)))
            eligible_ids = sorted(set(saved.get("eligible_ids", DEFAULT_LEARNERS)) & set(learners))
            return {
                "capacity": int(saved.get("capacity", 3)),
                "learners": learners,
                "eligible_ids": eligible_ids,
                "enrolled": list(saved.get("enrolled", [])),
                "waitlist": list(saved.get("waitlist", [])),
                "events": [list(event) for event in saved.get("events", [])],
            }
        initial = {
            "capacity": 3,
            "learners": DEFAULT_LEARNERS,
            "eligible_ids": DEFAULT_LEARNERS,
            "enrolled": [],
            "waitlist": [],
            "events": [["SYSTEM", "CourseFlow workspace initialized", "Ready"]],
        }
        save_state(initial)
        return initial


def save_state(state: dict[str, Any]) -> None:
    payload = json.dumps(state)
    with connect() as connection:
        connection.execute(
            "INSERT INTO app_state (id, payload) VALUES (1, ?) "
            "ON CONFLICT(id) DO UPDATE SET payload = excluded.payload",
            (payload,),
        )
        connection.commit()


def record(state: dict[str, Any], actor: str, detail: str, status: str) -> None:
    state["events"].insert(0, [actor, detail, status])
    state["events"] = state["events"][:50]


def build_service(state: dict[str, Any]) -> EnrollmentService:
    offering = CourseOffering(
        capacity=state["capacity"],
        enrolled=list(state["enrolled"]),
        waitlist=list(state["waitlist"]),
    )
    eligible_ids = set(state["eligible_ids"])
    return EnrollmentService(offering, eligible=lambda learner: learner in eligible_ids)


def service_state(state: dict[str, Any], service: EnrollmentService) -> None:
    offering = service.offering
    state["enrolled"] = offering.enrolled
    state["waitlist"] = offering.waitlist


def promote_until_full(service: EnrollmentService) -> list[str]:
    """Promote eligible waitlisted learners until capacity is full or no match remains."""
    promoted: list[str] = []
    while len(service.offering.enrolled) < service.offering.capacity:
        learner_id = service.refresh_waitlist()
        if learner_id is None:
            break
        promoted.append(learner_id)
    return promoted


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": DB_PATH.name}


@app.get("/api/state")
def get_state() -> dict[str, Any]:
    with LOCK:
        state = load_state()
        # Validate persisted invariants before sending state to the UI.
        build_service(state)
        return state


@app.post("/api/learners")
def add_learner(body: AddLearnerRequest) -> dict[str, Any]:
    learner_name = body.learner_name.strip()
    if not learner_name:
        raise HTTPException(status_code=422, detail="Enter a learner name.")

    with LOCK:
        state = load_state()
        if any(name.casefold() == learner_name.casefold() for name in state["learners"]):
            raise HTTPException(status_code=409, detail="That learner already exists.")

        state["learners"].append(learner_name)
        if body.eligible:
            state["eligible_ids"] = list(dict.fromkeys([*state["eligible_ids"], learner_name]))
        record(
            state,
            "ADMIN",
            f"Added learner {learner_name}",
            "Created — eligible" if body.eligible else "Created — prerequisite verification needed",
        )
        save_state(state)
        return {
            "message": f"{learner_name} added successfully"
            + (" and marked eligible." if body.eligible else ". Mark prerequisite status before enrollment."),
            "state": state,
        }


@app.post("/api/enroll")
def enroll(body: EnrollRequest) -> dict[str, Any]:
    with LOCK:
        state = load_state()
        service = build_service(state)
        result = service.enroll(body.learner_id)
        service_state(state, service)
        record(state, body.learner_id.strip(), result.message, result.code.value.replace("_", " ").title())
        save_state(state)
        return {"code": result.code.value, "message": result.message, "state": state}


@app.post("/api/drop")
def drop(body: EnrollRequest) -> dict[str, Any]:
    with LOCK:
        state = load_state()
        service = build_service(state)
        result = service.drop(body.learner_id)
        service_state(state, service)
        record(state, body.learner_id.strip(), result.message, result.code.value.replace("_", " ").title())
        save_state(state)
        return {"code": result.code.value, "message": result.message, "state": state}


@app.post("/api/capacity")
def set_capacity(body: CapacityRequest) -> dict[str, Any]:
    with LOCK:
        state = load_state()
        if body.capacity < len(state["enrolled"]):
            raise HTTPException(status_code=409, detail="Capacity cannot be lower than current enrollment.")
        state["capacity"] = body.capacity
        # Fill every newly available seat, preserving FIFO among eligible learners.
        service = build_service(state)
        promoted_learners = promote_until_full(service)
        service_state(state, service)
        message = f"Capacity set to {body.capacity}."
        if promoted_learners:
            message += f" Promoted {', '.join(promoted_learners)} from the waitlist."
        record(state, "ADMIN", message, "Updated")
        save_state(state)
        return {"message": message, "state": state}


@app.post("/api/eligibility")
def set_eligibility(body: EligibilityRequest) -> dict[str, Any]:
    with LOCK:
        state = load_state()
        eligible_ids = list(dict.fromkeys(name.strip() for name in body.eligible_ids if name.strip()))
        state["eligible_ids"] = eligible_ids
        record(state, "ADMIN", "Prerequisite eligibility updated", "Updated")
        save_state(state)
        return {"message": "Prerequisite eligibility saved.", "state": state}


@app.post("/api/refresh")
def refresh_waitlist() -> dict[str, Any]:
    with LOCK:
        state = load_state()
        service = build_service(state)
        promoted = promote_until_full(service)
        service_state(state, service)
        message = f"Promoted {', '.join(promoted)} from the waitlist." if promoted else "Waitlist refreshed; no eligible learner could be promoted."
        record(state, "SYSTEM", message, "Updated")
        save_state(state)
        return {"message": message, "state": state}
