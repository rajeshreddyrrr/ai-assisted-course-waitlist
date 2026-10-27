from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import streamlit as st

from course_waitlist import CourseOffering, EnrollmentService, ResultCode

DB_PATH = Path(__file__).with_name("course_waitlist.db")
DEFAULT_LEARNERS = ["Ava", "Noah", "Mia", "Liam", "Zoe", "Ethan", "Ivy", "Leo", "Aria", "Kai"]


def init_database() -> None:
    """Create the small SQLite state table if it does not already exist."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK (id = 1), payload TEXT NOT NULL)"
        )
        connection.commit()


def load_persisted_state() -> dict | None:
    with sqlite3.connect(DB_PATH) as connection:
        row = connection.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
    return json.loads(row[0]) if row else None


def save_persisted_state() -> None:
    payload = {
        "capacity": int(st.session_state.capacity),
        "learners": list(st.session_state.learners),
        "eligible_ids": sorted(st.session_state.eligible_ids),
        "enrolled": list(st.session_state.enrolled),
        "waitlist": list(st.session_state.waitlist),
        "events": list(st.session_state.events),
    }
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT INTO app_state (id, payload) VALUES (1, ?) "
            "ON CONFLICT(id) DO UPDATE SET payload = excluded.payload",
            (json.dumps(payload),),
        )
        connection.commit()


def rebuild_service() -> None:
    offering = CourseOffering(
        capacity=int(st.session_state.get("capacity", 3)),
        enrolled=list(st.session_state.get("enrolled", [])),
        waitlist=list(st.session_state.get("waitlist", [])),
    )
    eligible_ids = set(st.session_state.get("eligible_ids", set()))
    st.session_state.service = EnrollmentService(
        offering, eligible=lambda learner: learner in eligible_ids
    )


def sync_state() -> None:
    state = st.session_state.service.offering
    st.session_state.enrolled = state.enrolled
    st.session_state.waitlist = state.waitlist


def log_event(actor: str, detail: str, status: str) -> None:
    st.session_state.events.insert(0, (actor, detail, status))
    st.session_state.events = st.session_state.events[:50]


def init_state() -> None:
    if st.session_state.get("initialized"):
        return
    init_database()
    saved = load_persisted_state()
    if saved:
        st.session_state.capacity = int(saved.get("capacity", 3))
        st.session_state.learners = list(dict.fromkeys(saved.get("learners", DEFAULT_LEARNERS)))
        st.session_state.eligible_ids = set(saved.get("eligible_ids", DEFAULT_LEARNERS[:6]))
        st.session_state.enrolled = list(saved.get("enrolled", []))
        st.session_state.waitlist = list(saved.get("waitlist", []))
        st.session_state.events = [tuple(item) for item in saved.get("events", [])]
    else:
        st.session_state.capacity = 3
        st.session_state.learners = list(DEFAULT_LEARNERS)
        st.session_state.eligible_ids = set(DEFAULT_LEARNERS[:6])
        st.session_state.enrolled = []
        st.session_state.waitlist = []
        st.session_state.events = [("SYSTEM", "CourseFlow workspace initialized", "Ready")]
        save_persisted_state()
    rebuild_service()
    st.session_state.initialized = True


st.set_page_config(
    page_title="CourseFlow | Enrollment Console",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f5f7fb; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: #12213b; }
.hero { padding: 1.4rem 1.6rem; border-radius: 20px; color: white; background: linear-gradient(120deg, #13294b 0%, #174b78 58%, #237d91 100%); margin-bottom: 1.3rem; }
.hero h1 { color: white; margin: 0; font-size: 2.15rem; }
.hero p { color: #d9e8f6; margin: .45rem 0 0 0; }
.metric { background: white; border: 1px solid #e4eaf2; border-radius: 16px; padding: 1rem 1.15rem; min-height: 105px; }
.metric-label { color: #65748b; font-size: .85rem; font-weight: 600; }
.metric-value { color: #13294b; font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; margin-top: .15rem; }
.metric-note { color: #7d8aa0; font-size: .78rem; }
.panel { background: white; border: 1px solid #e4eaf2; border-radius: 16px; padding: 1.15rem 1.25rem; margin-bottom: 1rem; }
.small-muted { color: #65748b; font-size: .9rem; }
div.stButton > button { border-radius: 10px; font-weight: 600; min-height: 2.7rem; }
[data-testid="stSidebar"] { background: #edf2f8; }
</style>
""", unsafe_allow_html=True)

init_state()

with st.sidebar:
    st.markdown("## 🎓 CourseFlow")
    st.caption("ENROLLMENT MANAGEMENT")
    st.info("Use the **Course setup** section on the main page to change capacity, add learners, and verify prerequisites.")
    st.divider()
    st.caption(f"SQLite database: {DB_PATH.name}")

st.markdown("""
<div class="hero">
  <h1>Course Enrollment Console</h1>
  <p>A clear view of seat availability, learner enrollment, prerequisites, and fair FIFO waitlist promotion.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## Course setup")
st.caption("These controls are intentionally shown on the main page so capacity, learner creation, and prerequisite status are easy to find.")

setup_capacity, setup_add, setup_prereq = st.columns([0.85, 1.0, 1.4], gap="large")
with setup_capacity:
    st.markdown("### 1. Seat capacity")
    new_capacity = st.number_input(
        "Maximum enrolled learners", min_value=0, max_value=500,
        value=int(st.session_state.capacity), step=1, key="capacity_main_input"
    )
    st.caption(f"Currently enrolled: {len(st.session_state.enrolled)} / {st.session_state.capacity}")
    if st.button("Save capacity", use_container_width=True):
        if new_capacity < len(st.session_state.enrolled):
            st.error("Capacity cannot be lower than current enrollment.")
        else:
            st.session_state.capacity = int(new_capacity)
            rebuild_service()
            log_event("ADMIN", f"Capacity set to {new_capacity}", "Updated")
            save_persisted_state()
            st.success("Capacity updated.")
            st.rerun()

with setup_add:
    st.markdown("### 2. Add a learner")
    with st.form("add_learner_form_main", clear_on_submit=True):
        new_learner = st.text_input("Learner name", placeholder="Enter a new learner name")
        add_learner_clicked = st.form_submit_button("＋ Add learner", use_container_width=True)
    if add_learner_clicked:
        learner_name = new_learner.strip()
        existing_names = {name.casefold() for name in st.session_state.learners}
        if not learner_name:
            st.error("Enter a learner name.")
        elif learner_name.casefold() in existing_names:
            st.error("That learner already exists.")
        else:
            st.session_state.learners.append(learner_name)
            log_event("ADMIN", f"Added learner {learner_name}", "Created")
            save_persisted_state()
            st.success(f"{learner_name} added. Its prerequisite status is not verified yet.")
            st.rerun()
    st.caption(f"{len(st.session_state.learners)} learners available")

with setup_prereq:
    st.markdown("### 3. Prerequisite status")
    st.write("Select only learners whose required prerequisites have been completed.")
    eligible = st.multiselect(
        "Eligible learners",
        options=st.session_state.learners,
        default=[x for x in st.session_state.learners if x in st.session_state.eligible_ids],
        help="Only selected learners can enroll or join the waitlist. A full course waitlists eligible learners automatically.",
        key="eligible_main_input",
    )
    if set(eligible) != st.session_state.eligible_ids:
        st.session_state.eligible_ids = set(eligible)
        rebuild_service()
        log_event("ADMIN", "Prerequisite eligibility updated", "Updated")
        save_persisted_state()
    st.caption(f"{len(st.session_state.eligible_ids)} of {len(st.session_state.learners)} learners marked eligible")
    if st.button("Refresh waitlist", use_container_width=True):
        promoted = st.session_state.service.refresh_waitlist()
        sync_state()
        log_event("SYSTEM", f"Waitlist refreshed; promoted {promoted or 'nobody'}", "Updated")
        save_persisted_state()
        st.rerun()

st.divider()

service = st.session_state.service
state = service.offering
enrolled_count = len(state.enrolled)
waitlist_count = len(state.waitlist)
open_seats = max(state.capacity - enrolled_count, 0)

m1, m2, m3, m4 = st.columns(4)
for col, label, value, note in [
    (m1, "TOTAL CAPACITY", state.capacity, "Seats configured"),
    (m2, "ENROLLED", enrolled_count, "Confirmed learners"),
    (m3, "AVAILABLE SEATS", open_seats, "Open for enrollment"),
    (m4, "WAITLIST", waitlist_count, "Learners waiting"),
]:
    with col:
        st.markdown(
            f'<div class="metric"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
            unsafe_allow_html=True,
        )

enroll_tab, roster_tab, activity_tab = st.tabs(
    ["＋  Manage enrollment", "▤  Class roster", "◷  Activity log"]
)

with enroll_tab:
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown("### Enroll a learner")
        st.markdown('<p class="small-muted">Choose a learner and let CourseFlow apply the enrollment rules.</p>', unsafe_allow_html=True)
        available_learners = [
            x for x in st.session_state.learners if x not in state.enrolled and x not in state.waitlist
        ]
        selected = st.selectbox(
            "Learner", available_learners, index=None,
            placeholder="Select a learner…", key="enroll_learner",
        )
        if selected:
            if selected in st.session_state.eligible_ids:
                st.success("Prerequisites satisfied")
            else:
                st.warning("Prerequisites not satisfied")
        if st.button("Process enrollment", type="primary", use_container_width=True, disabled=not selected):
            result = service.enroll(selected)
            sync_state()
            log_event(selected, result.message, result.code.value.replace("_", " ").title())
            save_persisted_state()
            if result.code == ResultCode.ENROLLED:
                st.success(result.message)
            elif result.code == ResultCode.WAITLISTED:
                st.info(result.message)
            else:
                st.error(result.message)
            st.rerun()

        st.markdown("### Drop an enrollment")
        drop_candidate = st.selectbox(
            "Currently enrolled learner", state.enrolled, index=None,
            placeholder="Select an enrolled learner…", key="drop_learner",
        )
        if st.button("Drop learner", use_container_width=True, disabled=not drop_candidate):
            result = service.drop(drop_candidate)
            sync_state()
            log_event(drop_candidate, result.message, result.code.value.replace("_", " ").title())
            save_persisted_state()
            st.success(result.message) if result.code == ResultCode.DROPPED else st.error(result.message)
            st.rerun()

    with right:
        st.markdown("### Enrollment rules")
        st.markdown("""
        <div class="panel">
          <b>01 · Capacity protection</b><br><span class="small-muted">Confirmed enrollment never exceeds the configured seat count.</span><br><br>
          <b>02 · Prerequisite validation</b><br><span class="small-muted">Only eligible learners may enroll or join the waitlist.</span><br><br>
          <b>03 · FIFO promotion</b><br><span class="small-muted">When a seat opens, the earliest eligible learner is promoted.</span><br><br>
          <b>04 · Duplicate protection</b><br><span class="small-muted">A learner cannot have duplicate active enrollment or waitlist entries.</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### Queue health")
        if state.capacity == 0:
            st.warning("This offering has zero seats configured.")
        elif open_seats == 0:
            st.warning("Offering is full. Eligible new requests join the waitlist.")
        else:
            st.success(f"{open_seats} seat(s) available for eligible learners.")

with roster_tab:
    roster_left, roster_right = st.columns(2, gap="large")
    with roster_left:
        st.markdown("### Confirmed learners")
        if state.enrolled:
            for index, learner in enumerate(state.enrolled, start=1):
                st.markdown(
                    f'<div class="panel"><b>{index:02d}</b> &nbsp; {learner}'
                    '<span style="float:right;color:#18866b">● Enrolled</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No learners enrolled yet.")
    with roster_right:
        st.markdown("### FIFO waitlist")
        if state.waitlist:
            for index, learner in enumerate(state.waitlist, start=1):
                eligible_now = learner in st.session_state.eligible_ids
                label = "Eligible" if eligible_now else "Prerequisite pending"
                color = "#18866b" if eligible_now else "#b7791f"
                st.markdown(
                    f'<div class="panel"><b>{index:02d}</b> &nbsp; {learner}'
                    f'<span style="float:right;color:{color}">● {label}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("The waitlist is empty.")

with activity_tab:
    st.markdown("### Recent activity")
    if st.session_state.events:
        for actor, detail, status in st.session_state.events:
            st.markdown(
                f'<div class="panel"><b>{actor}</b> &nbsp; {detail}'
                f'<span style="float:right;color:#65748b">{status}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No activity recorded.")

st.divider()
st.caption("CourseFlow uses a local SQLite database (course_waitlist.db) so enrollment and waitlist state survive app restarts.")
