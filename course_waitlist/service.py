"""Enrollment, drop, and FIFO waitlist promotion for one course offering."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Callable


class ResultCode(str, Enum):
    ENROLLED = "enrolled"
    WAITLISTED = "waitlisted"
    ALREADY_ENROLLED = "already_enrolled"
    ALREADY_WAITLISTED = "already_waitlisted"
    PREREQUISITE_NOT_MET = "prerequisite_not_met"
    INVALID_LEARNER = "invalid_learner"
    DROPPED = "dropped"
    NOT_ENROLLED = "not_enrolled"


@dataclass(frozen=True)
class Result:
    code: ResultCode
    message: str
    learner_id: str | None = None
    promoted_learner_id: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.code in {ResultCode.ENROLLED, ResultCode.WAITLISTED, ResultCode.DROPPED}


@dataclass
class CourseOffering:
    """State for a single offering. IDs are kept in insertion/FIFO order."""

    capacity: int
    enrolled: list[str] = field(default_factory=list)
    waitlist: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not isinstance(self.capacity, int) or self.capacity < 0:
            raise ValueError("capacity must be a non-negative integer")
        if len(self.enrolled) > self.capacity:
            raise ValueError("enrolled learners cannot exceed capacity")
        if len(self.enrolled) != len(set(self.enrolled)):
            raise ValueError("enrolled learner IDs must be unique")
        if len(self.waitlist) != len(set(self.waitlist)):
            raise ValueError("waitlist learner IDs must be unique")
        if set(self.enrolled) & set(self.waitlist):
            raise ValueError("a learner cannot be both enrolled and waitlisted")


class EnrollmentService:
    """Thread-safe, process-local service for one course offering."""

    def __init__(self, offering: CourseOffering, eligible: Callable[[str], bool] | None = None) -> None:
        self._offering = offering
        self._eligible = eligible or (lambda _learner_id: True)
        self._lock = RLock()

    @property
    def offering(self) -> CourseOffering:
        """Return a defensive snapshot of offering state."""
        with self._lock:
            return CourseOffering(
                capacity=self._offering.capacity,
                enrolled=list(self._offering.enrolled),
                waitlist=list(self._offering.waitlist),
            )

    def enroll(self, learner_id: str) -> Result:
        learner_id = self._normalize_learner_id(learner_id)
        if learner_id is None:
            return Result(ResultCode.INVALID_LEARNER, "Learner ID must be a non-empty string.")

        with self._lock:
            state = self._offering
            if learner_id in state.enrolled:
                return Result(ResultCode.ALREADY_ENROLLED, "Learner is already enrolled.", learner_id)
            if learner_id in state.waitlist:
                return Result(ResultCode.ALREADY_WAITLISTED, "Learner is already on the waitlist.", learner_id)
            if not self._is_eligible(learner_id):
                return Result(ResultCode.PREREQUISITE_NOT_MET, "Learner does not meet prerequisites.", learner_id)
            if len(state.enrolled) < state.capacity:
                state.enrolled.append(learner_id)
                return Result(ResultCode.ENROLLED, "Enrollment successful.", learner_id)
            state.waitlist.append(learner_id)
            return Result(ResultCode.WAITLISTED, "Course is full; learner added to waitlist.", learner_id)

    def drop(self, learner_id: str) -> Result:
        learner_id = self._normalize_learner_id(learner_id)
        if learner_id is None:
            return Result(ResultCode.INVALID_LEARNER, "Learner ID must be a non-empty string.")
        with self._lock:
            state = self._offering
            if learner_id not in state.enrolled:
                return Result(ResultCode.NOT_ENROLLED, "Learner is not enrolled; no state changed.", learner_id)
            state.enrolled.remove(learner_id)
            promoted = self._promote_earliest_eligible()
            message = "Enrollment dropped." if promoted is None else f"Enrollment dropped; promoted {promoted}."
            return Result(ResultCode.DROPPED, message, learner_id, promoted)

    def refresh_waitlist(self) -> str | None:
        """Promote one eligible learner if a seat is open; otherwise do nothing."""
        with self._lock:
            if len(self._offering.enrolled) >= self._offering.capacity:
                return None
            return self._promote_earliest_eligible()

    def _promote_earliest_eligible(self) -> str | None:
        state = self._offering
        if len(state.enrolled) >= state.capacity:
            return None
        for learner_id in state.waitlist:
            if self._is_eligible(learner_id):
                state.waitlist.remove(learner_id)
                state.enrolled.append(learner_id)
                return learner_id
        return None

    def _is_eligible(self, learner_id: str) -> bool:
        try:
            return bool(self._eligible(learner_id))
        except Exception:
            # Fail closed: eligibility lookup errors must not enroll/promote.
            return False

    @staticmethod
    def _normalize_learner_id(learner_id: object) -> str | None:
        if not isinstance(learner_id, str) or not learner_id.strip():
            return None
        return learner_id.strip()
