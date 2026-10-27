from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from course_waitlist import CourseOffering, EnrollmentService, ResultCode


def test_enrolls_when_capacity_available():
    service = EnrollmentService(CourseOffering(capacity=2))
    result = service.enroll(" learner-1 ")
    assert result.code == ResultCode.ENROLLED
    assert service.offering.enrolled == ["learner-1"]
    assert service.offering.waitlist == []


def test_full_capacity_adds_eligible_learner_to_waitlist_once():
    service = EnrollmentService(CourseOffering(capacity=1))
    assert service.enroll("a").code == ResultCode.ENROLLED
    assert service.enroll("b").code == ResultCode.WAITLISTED
    assert service.enroll("b").code == ResultCode.ALREADY_WAITLISTED
    assert service.offering.waitlist == ["b"]


def test_duplicate_enrollment_request_does_not_duplicate_enrolled_record():
    service = EnrollmentService(CourseOffering(capacity=2))
    assert service.enroll("a").code == ResultCode.ENROLLED
    assert service.enroll("a").code == ResultCode.ALREADY_ENROLLED
    assert service.offering.enrolled == ["a"]


def test_drop_promotes_earliest_eligible_waitlisted_learner_fifo():
    service = EnrollmentService(CourseOffering(capacity=1))
    service.enroll("a")
    service.enroll("b")
    service.enroll("c")
    result = service.drop("a")
    assert result.code == ResultCode.DROPPED
    assert result.promoted_learner_id == "b"
    assert service.offering.enrolled == ["b"]
    assert service.offering.waitlist == ["c"]


def test_ineligible_learner_is_skipped_and_retained_when_promotion_scans():
    eligible = {"a": True, "b": True, "c": True}
    service = EnrollmentService(CourseOffering(capacity=1), eligible=lambda learner: eligible.get(learner, False))
    assert service.enroll("a").code == ResultCode.ENROLLED
    # b is eligible at request time, so may join the waitlist.
    assert service.enroll("b").code == ResultCode.WAITLISTED
    assert service.enroll("c").code == ResultCode.WAITLISTED
    eligible["b"] = False
    result = service.drop("a")
    assert result.promoted_learner_id == "c"
    assert service.offering.enrolled == ["c"]
    assert service.offering.waitlist == ["b"]


def test_prerequisite_failure_does_not_mutate_state():
    service = EnrollmentService(CourseOffering(capacity=1), eligible=lambda learner: learner == "eligible")
    result = service.enroll("ineligible")
    assert result.code == ResultCode.PREREQUISITE_NOT_MET
    assert service.offering.enrolled == []
    assert service.offering.waitlist == []


def test_invalid_and_repeated_drops_do_not_change_state():
    service = EnrollmentService(CourseOffering(capacity=1))
    service.enroll("a")
    before = service.offering
    assert service.drop("").code == ResultCode.INVALID_LEARNER
    assert service.drop("missing").code == ResultCode.NOT_ENROLLED
    assert service.drop("a").code == ResultCode.DROPPED
    after_first_drop = service.offering
    assert service.drop("a").code == ResultCode.NOT_ENROLLED
    after_second_drop = service.offering
    assert before.enrolled == ["a"]
    assert after_first_drop.enrolled == []
    assert after_second_drop.enrolled == []
    assert after_second_drop.waitlist == []


def test_invalid_capacity_is_rejected():
    for value in (-1, 1.5, True):
        with pytest.raises(ValueError):
            CourseOffering(capacity=value)


def test_capacity_zero_never_enrolls_and_can_retain_waitlist():
    service = EnrollmentService(CourseOffering(capacity=0))
    assert service.enroll("a").code == ResultCode.WAITLISTED
    assert service.offering.enrolled == []
    assert service.offering.waitlist == ["a"]


def test_concurrent_duplicate_requests_preserve_uniqueness_and_capacity():
    service = EnrollmentService(CourseOffering(capacity=1))
    barrier = Barrier(12)

    def request():
        barrier.wait()
        return service.enroll("same-learner")

    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(lambda _: request(), range(12)))
    state = service.offering
    assert len(state.enrolled) <= state.capacity
    assert state.enrolled == ["same-learner"]
    assert state.waitlist == []
    assert sum(result.code == ResultCode.ENROLLED for result in results) == 1
    assert sum(result.code == ResultCode.ALREADY_ENROLLED for result in results) == 11


def test_waitlist_eligibility_lookup_error_fails_closed():
    def broken(_learner):
        raise RuntimeError("eligibility provider unavailable")

    service = EnrollmentService(CourseOffering(capacity=1), eligible=broken)
    assert service.enroll("a").code == ResultCode.PREREQUISITE_NOT_MET
    assert service.offering.enrolled == []
    assert service.offering.waitlist == []

def test_invalid_learner_ids_are_rejected_without_mutation():
    service = EnrollmentService(CourseOffering(capacity=1))
    for learner_id in ("", "   ", None, 123):
        result = service.enroll(learner_id)
        assert result.code == ResultCode.INVALID_LEARNER
        assert service.offering.enrolled == []
        assert service.offering.waitlist == []


def test_refresh_waitlist_does_not_over_enroll_when_capacity_is_full():
    eligible = {"a": True, "b": True, "c": True}
    service = EnrollmentService(
        CourseOffering(capacity=1),
        eligible=lambda learner: eligible.get(learner, False),
    )
    assert service.enroll("a").code == ResultCode.ENROLLED
    assert service.enroll("b").code == ResultCode.WAITLISTED
    assert service.enroll("c").code == ResultCode.WAITLISTED

    eligible["b"] = False
    assert service.drop("a").promoted_learner_id == "c"
    assert service.offering.enrolled == ["c"]
    assert service.offering.waitlist == ["b"]

    # If eligibility is restored while no seat is open, refresh must not over-enroll.
    eligible["b"] = True
    assert service.refresh_waitlist() is None
    assert service.offering.enrolled == ["c"]
    assert service.offering.waitlist == ["b"]

