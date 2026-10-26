"""Run a small deterministic demonstration of the service."""

from .service import CourseOffering, EnrollmentService


def main() -> None:
    service = EnrollmentService(CourseOffering(capacity=2), eligible=lambda learner: learner != "learner-3")
    for learner in ("learner-1", "learner-2", "learner-4", "learner-3"):
        result = service.enroll(learner)
        print(f"{learner}: {result.code.value} — {result.message}")
    dropped = service.drop("learner-1")
    print(f"drop learner-1: {dropped.message}")
    print(f"enrolled={service.offering.enrolled}")
    print(f"waitlist={service.offering.waitlist}")


if __name__ == "__main__":
    main()
