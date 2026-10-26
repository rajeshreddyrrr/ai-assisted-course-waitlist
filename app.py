from __future__ import annotations

import streamlit as st

from course_waitlist import CourseOffering, EnrollmentService, ResultCode

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
.hero { padding: 1.4rem 1.6rem; border-radius: 20px; color: white;
        background: linear-gradient(120deg, #13294b 0%, #174b78 58%, #237d91 100%);
        margin-bottom: 1.3rem; }
.hero h1 { color: white; margin: 0; font-size: 2.15rem; }
.hero p { color: #d9e8f6; margin: .45rem 0 0 0; }
.metric { background: white; border: 1px solid #e4eaf2; border-radius: 16px;
          padding: 1rem 1.15rem; min-height: 105px; }
.metric-label { color: #65748b; font-size: .85rem; font-weight: 600; }
.metric-value { color: #13294b; font-family: 'Space Grotesk', sans-serif;
                font-size: 2rem; font-weight: 700; margin-top: .15rem; }
.metric-note { color: #7d8aa0; font-size: .78rem; }
.panel { background: white; border: 1px solid #e4eaf2; border-radius: 16px;
         padding: 1.15rem 1.25rem; margin-bottom: 1rem; }
.small-muted { color: #65748b; font-size: .9rem; }
div.stButton > button { border-radius: 10px; font-weight: 600; min-height: 2.7rem; }
[data-testid="stSidebar"] { background: #edf2f8; }
</style>
""", unsafe_allow_html=True)


def init_state() -> None:
    if "capacity" not in st.session_state:
        st.session_state.capacity = 3
    if "eligible_ids" not in st.session_state:
        st.session_state.eligible_ids = {"Ava", "Noah", "Mia", "Liam", "Zoe", "Ethan"}
    if "enrolled" not in st.session_state:
        st.session_state.enrolled = []
    if "waitlist" not in st.session_state:
        st.session_state.waitlist = []
    if "events" not in st.session_state:
        st.session_state.events = [("SYSTEM", "CourseFlow workspace initialized", "Ready")]
    if "service" not in st.session_state:
        rebuild_service()


def rebuild_service() -> None:
    offering = CourseOffering(
        capacity=st.session_state.get("capacity", 3),
        enrolled=list(st.session_state.get("enrolled", [])),
        waitlist=list(st.session_state.get("waitlist", [])),
    )
    eligible_ids = set(st.session_state.get("eligible_ids", set()))
    st.session_state.service = EnrollmentService(offering, eligible=lambda learner: learner in eligible_ids)


def sync_state() -> None:
    state = st.session_state.service.offering
    st.session_state.enrolled = state.enrolled
    st.session_state.waitlist = state.waitlist


def log_event(actor: str, detail: str, status: str) -> None:
    st.session_state.events.insert(0, (actor, detail, status))
    st.session_state.events = st.session_state.events[:30]


init_state()

with st.sidebar:
    st.markdown("## 🎓 CourseFlow")
    st.caption("ENROLLMENT MANAGEMENT")
    st.divider()
    st.markdown("### Offering settings")
    new_capacity = st.number_input("Seat capacity", min_value=0, max_value=500, value=int(st.session_state.capacity), step=1)
    if st.button("Apply capacity", use_container_width=True):
        if new_capacity < len(st.session_state.enrolled):
            st.error("Capacity cannot be lower than current enrollment.")
        else:
            st.session_state.capacity = int(new_capacity)
            rebuild_service()
            log_event("ADMIN", f"Capacity set to {new_capacity}", "Updated")
            st.success("Capacity updated.")
    st.markdown("### Prerequisites")
    all_learners = ["Ava", "Noah", "Mia", "Liam", "Zoe", "Ethan", "Ivy", "Leo", "Aria", "Kai"]
    eligible = st.multiselect(
        "Learners who meet prerequisites",
        all_learners,
        default=[x for x in all_learners if x in st.session_state.eligible_ids],
        help="Enrollment and waitlist promotion are restricted to eligible learners.",
    )
    if set(eligible) != st.session_state.eligible_ids:
        st.session_state.eligible_ids = set(eligible)
        rebuild_service()
    if st.button("Refresh waitlist", use_container_width=True):
        promoted = st.session_state.service.refresh_waitlist()
        sync_state()
        log_event("SYSTEM", f"Waitlist refreshed; promoted {promoted or 'nobody'}", "Updated")
        st.rerun()
    st.divider()
    st.caption("AI-assisted engineering demo · In-memory state")

st.markdown("""
<div class="hero">
  <h1>Course Enrollment Console</h1>
  <p>A clear view of seat availability, learner enrollment, prerequisites, and fair FIFO waitlist promotion.</p>
</div>
""", unsafe_allow_html=True)

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
        st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

st.write("")
enroll_tab, roster_tab, activity_tab = st.tabs(["＋  Manage enrollment", "▤  Class roster", "◷  Activity log"])

with enroll_tab:
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown("### Enroll a learner")
        st.markdown('<p class="small-muted">Choose a learner and let CourseFlow apply the enrollment rules.</p>', unsafe_allow_html=True)
        available_learners = [x for x in all_learners if x not in state.enrolled and x not in state.waitlist]
        selected = st.selectbox("Learner", available_learners, index=None, placeholder="Select a learner…")
        selected_eligible = selected in st.session_state.eligible_ids if selected else False
        if selected:
            if selected_eligible:
                st.success("Prerequisites satisfied")
            else:
                st.warning("Prerequisites not satisfied")
        if st.button("Process enrollment", type="primary", use_container_width=True, disabled=not selected):
            result = service.enroll(selected)
            sync_state()
            log_event(selected, result.message, result.code.value.replace("_", " ").title())
            if result.code == ResultCode.ENROLLED:
                st.success(result.message)
            elif result.code == ResultCode.WAITLISTED:
                st.info(result.message)
            else:
                st.error(result.message)
            st.rerun()

        st.markdown("### Drop an enrollment")
        drop_candidate = st.selectbox("Currently enrolled learner", state.enrolled, index=None, placeholder="Select an enrolled learner…")
        if st.button("Drop learner", use_container_width=True, disabled=not drop_candidate):
            result = service.drop(drop_candidate)
            sync_state()
            log_event(drop_candidate, result.message, result.code.value.replace("_", " ").title())
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
                st.markdown(f'<div class="panel"><b>{index:02d}</b> &nbsp; {learner} <span style="float:right;color:#18866b">● Enrolled</span></div>', unsafe_allow_html=True)
        else:
            st.info("No learners enrolled yet.")
    with roster_right:
        st.markdown("### FIFO waitlist")
        if state.waitlist:
            for index, learner in enumerate(state.waitlist, start=1):
                eligible_now = learner in st.session_state.eligible_ids
                label = "Eligible" if eligible_now else "Prerequisite pending"
                st.markdown(f'<div class="panel"><b>{index:02d}</b> &nbsp; {learner} <span style="float:right;color:{"#18866b" if eligible_now else "#b7791f"}">● {label}</span></div>', unsafe_allow_html=True)
        else:
            st.info("The waitlist is empty.")

with activity_tab:
    st.markdown("### Recent activity")
    if st.session_state.events:
        st.dataframe(
            [{"Actor": actor, "Event": detail, "Result": status} for actor, detail, status in st.session_state.events],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No activity recorded.")

st.divider()
st.caption("CourseFlow is an assessment demo. Data is held in memory for the current Streamlit session and is not persisted.")
