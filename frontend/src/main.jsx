import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity, ArrowDownRight, ArrowRight, Bell, BookOpen, Check, ChevronDown,
  CircleHelp, Clock3, GraduationCap, LayoutDashboard, Plus, Search, Settings2,
  ShieldCheck, Sparkles, Users, UserRoundCheck, UserRoundMinus, X
} from "lucide-react";
import "./styles.css";

const learnerPool = ["Ava", "Noah", "Mia", "Liam", "Zoe", "Ethan", "Ivy", "Leo", "Aria", "Kai"];
const initials = (name = "") => name.slice(0, 1).toUpperCase();
const colors = ["lilac", "mint", "peach", "sky", "rose"];

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || body.message || "Something went wrong.");
  return body;
}

function App() {
  const [data, setData] = useState(null);
  const [tab, setTab] = useState("overview");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState("");
  const [toast, setToast] = useState("");
  const [busy, setBusy] = useState(false);
  const [capacityDraft, setCapacityDraft] = useState(3);
  const [eligibilityOpen, setEligibilityOpen] = useState(false);
  const [eligibleDraft, setEligibleDraft] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showAddLearner, setShowAddLearner] = useState(false);
  const [newLearnerName, setNewLearnerName] = useState("");
  const [newLearnerEligible, setNewLearnerEligible] = useState(false);

  const reload = async () => {
    const state = await request("/api/state");
    setData(state);
    setCapacityDraft(state.capacity);
    setEligibleDraft(state.eligible_ids);
  };
  useEffect(() => { reload().catch((e) => setToast(e.message)); }, []);
  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 3200);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const enrolled = data?.enrolled || [];
  const waitlist = data?.waitlist || [];
  const eligible = data?.eligible_ids || [];
  const learnerPool = data?.learners || [];
  const capacity = data?.capacity ?? 0;
  const openSeats = Math.max(capacity - enrolled.length, 0);
  const remaining = learnerPool.filter((name) => !enrolled.includes(name) && !waitlist.includes(name));
  const filtered = remaining.filter((name) => name.toLowerCase().includes(search.toLowerCase()));
  const events = data?.events || [];
  const fillPercent = capacity ? Math.min(100, Math.round(enrolled.length / capacity * 100)) : 0;
  const status = openSeats > 0 ? "Enrollment open" : "Class at capacity";

  const act = async (path, payload, success) => {
    setBusy(true);
    try {
      const result = await request(path, { method: "POST", body: JSON.stringify(payload) });
      await reload();
      setToast(result.message || success);
      setSelected("");
    } catch (error) { setToast(error.message); }
    finally { setBusy(false); }
  };

  const applyEligibility = async () => {
    await act("/api/eligibility", { eligible_ids: eligibleDraft }, "Prerequisites updated");
    setEligibilityOpen(false);
  };

  if (!data) return <div className="boot"><div className="brand-mark"><GraduationCap /></div><h1>CourseFlow</h1><p>Connecting to your enrollment workspace…</p><button className="button button-dark" onClick={() => reload().catch(e => setToast(e.message))}>Retry connection</button>{toast && <div className="toast toast-error">{toast}</div>}</div>;

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><GraduationCap size={23} strokeWidth={2.3} /></div><div><strong>courseflow<span>.</span></strong><small>ENROLLMENT STUDIO</small></div></div>
      <div className="workspace-label">WORKSPACE <span>01</span></div>
      <nav className="nav-list">
        <button className={tab === "overview" ? "nav-item active" : "nav-item"} onClick={() => setTab("overview")}><LayoutDashboard size={18}/> Overview</button>
        <button className={tab === "roster" ? "nav-item active" : "nav-item"} onClick={() => setTab("roster")}><Users size={18}/> Class roster <span className="nav-count">{enrolled.length}</span></button>
        <button className={tab === "waitlist" ? "nav-item active" : "nav-item"} onClick={() => setTab("waitlist")}><Clock3 size={18}/> Waitlist <span className="nav-count">{waitlist.length}</span></button>
        <button className={tab === "activity" ? "nav-item active" : "nav-item"} onClick={() => setTab("activity")}><Activity size={18}/> Activity log</button>
      </nav>
      <div className="sidebar-course">
        <div className="course-art"><div className="orbit orbit-one"></div><div className="orbit orbit-two"></div><BookOpen size={34}/><span>01</span></div>
        <div className="eyebrow">CURRENT OFFERING</div>
        <h3>Product Design<br/>Foundations</h3>
        <p>Fall cohort · CS-204</p>
        <div className="side-progress"><div><span>Seat utilization</span><b>{fillPercent}%</b></div><div className="progress-track"><span style={{width: fillPercent + "%"}}/></div></div>
      </div>
      <div className="sidebar-bottom">
        <button className="nav-item" onClick={() => setShowSettings(!showSettings)}><Settings2 size={18}/> Offering settings <ArrowRight className="nav-trail" size={15}/></button>
        {showSettings && <div className="settings-box">
          <label>Seat capacity</label><div className="capacity-control"><button onClick={() => setCapacityDraft(v => Math.max(0, Number(v) - 1))}>−</button><input type="number" min="0" max="500" value={capacityDraft} onChange={e => setCapacityDraft(e.target.value)}/><button onClick={() => setCapacityDraft(v => Math.min(500, Number(v) + 1))}>＋</button></div>
          <button className="button button-dark button-full" onClick={() => act("/api/capacity", { capacity: Number(capacityDraft) }, "Capacity saved")}>Save capacity</button>
          <button className="text-button" onClick={() => setEligibilityOpen(true)}>Manage prerequisites</button>
        </div>}
        <div className="profile"><div className="profile-avatar">CF</div><div><b>Course Admin</b><small>Workspace owner</small></div><button className="icon-button" title="Help"><CircleHelp size={17}/></button></div>
      </div>
    </aside>

    <main className="main-content">
      <header className="topbar"><div className="breadcrumb">Courses <span>/</span> <b>Product Design Foundations</b></div><div className="top-actions"><div className="live-status"><span/> All changes saved</div><button className="icon-button notification" title="Notifications"><Bell size={18}/><i/></button><div className="top-avatar">CA</div></div></header>
      <div className="page-wrap">
        <section className="welcome-row"><div><div className="eyebrow welcome-eyebrow"><Sparkles size={13}/> COURSE MANAGEMENT</div><h1>Enrollment, at a glance<span>.</span></h1><p>Manage your cohort, keep the queue moving, and make every seat count.</p></div><div className="date-chip"><div className="date-dot"></div><div><b>FALL 2026</b><small>Registration window</small></div><ChevronDown size={16}/></div></section>

        <section className="stats-grid">
          <article className="stat-card stat-primary"><div className="stat-top"><span>SEAT CAPACITY</span><div className="stat-icon"><BookOpen size={17}/></div></div><div className="stat-number">{String(capacity).padStart(2,"0")}<small> seats</small></div><div className="stat-foot"><span className="stat-marker marker-lime"/> Total places available</div><div className="stat-watermark"><BookOpen size={76}/></div></article>
          <article className="stat-card"><div className="stat-top"><span>CONFIRMED</span><div className="stat-icon icon-mint"><UserRoundCheck size={17}/></div></div><div className="stat-number">{String(enrolled.length).padStart(2,"0")}<small> learners</small></div><div className="stat-foot"><span className="stat-marker marker-mint"/>{capacity ? Math.round(enrolled.length / capacity * 100) : 0}% of capacity filled</div><div className="mini-bars">{[0,1,2,3,4,5,6].map((n)=><i key={n} className={n < Math.ceil(fillPercent / 15) ? "bar-on" : ""}/>)}</div></article>
          <article className="stat-card"><div className="stat-top"><span>SEATS AVAILABLE</span><div className="stat-icon icon-peach"><ArrowDownRight size={17}/></div></div><div className="stat-number">{String(openSeats).padStart(2,"0")}<small> open</small></div><div className="stat-foot"><span className="stat-marker marker-peach"/>{openSeats ? "Ready for eligible learners" : "Waitlist is active"}</div><div className="ring-graphic"><span>{fillPercent}%</span></div></article>
          <article className="stat-card"><div className="stat-top"><span>WAITING IN LINE</span><div className="stat-icon icon-lilac"><Clock3 size={17}/></div></div><div className="stat-number">{String(waitlist.length).padStart(2,"0")}<small> learners</small></div><div className="stat-foot"><span className="stat-marker marker-lilac"/>{waitlist.length ? "FIFO order maintained" : "No one waiting yet"}</div><div className="queue-dots">{waitlist.slice(0,5).map((n,i)=><span key={n} className={colors[i%colors.length]}>{initials(n)}</span>)}</div></article>
        </section>

        <section className="content-grid">
          <div className="primary-column">
            <div className="section-head"><div><h2>{tab === "roster" ? "Confirmed learners" : tab === "waitlist" ? "The waitlist" : tab === "activity" ? "Recent activity" : "Manage enrollment"}</h2><p>{tab === "overview" ? "Your course roster, in real time." : tab === "roster" ? "Learners who have secured their place." : tab === "waitlist" ? "First in, first considered for the next seat." : "A record of changes in this offering."}</p></div><div className="section-actions"><button className="button button-dark" onClick={() => setShowAddLearner(true)}><Plus size={15}/> Add learner</button>{tab === "overview" && <button className="button button-outline" onClick={() => setTab("roster")}>View roster <ArrowRight size={15}/></button>}</div></div>

            {(tab === "overview" || tab === "roster") && <div className="panel roster-panel">
              <div className="panel-toolbar"><div className="panel-title"><span className="status-pip"/> Enrolled learners <span className="count-pill">{enrolled.length}</span></div><div className="searchbox"><Search size={15}/><input placeholder="Find a learner" value={search} onChange={e => setSearch(e.target.value)}/>{search && <button onClick={() => setSearch("")}><X size={13}/></button>}</div></div>
              {enrolled.filter(n => n.toLowerCase().includes(search.toLowerCase())).length ? <div className="learner-list">{enrolled.filter(n => n.toLowerCase().includes(search.toLowerCase())).map((name,index)=><div className="learner-row" key={name}><div className={"learner-avatar "+colors[index%colors.length]}>{initials(name)}</div><div className="learner-info"><b>{name}</b><small>Student ID · CF-{String(2041+learnerPool.indexOf(name)).slice(-4)}</small></div><span className="enrolled-badge"><Check size={12}/> Enrolled</span><button className="row-action" title={"Drop "+name} disabled={busy} onClick={() => act("/api/drop",{learner_id:name},name+" dropped")}><UserRoundMinus size={16}/></button></div>)}</div> : <div className="empty-state"><div className="empty-icon"><Users size={23}/></div><b>{search ? "No matching learners" : "Your roster is ready for its first learner"}</b><p>{search ? "Try another name." : "Enroll an eligible learner to start building your cohort."}</p></div>}
              <div className="panel-footer"><span>Showing <b>{enrolled.length}</b> of {capacity} available places</span><button onClick={() => setTab("waitlist")}>View waitlist <ArrowRight size={14}/></button></div>
            </div>}

            {(tab === "overview" || tab === "waitlist") && <div className="panel waitlist-panel">
              <div className="panel-toolbar"><div className="panel-title"><span className="queue-icon"><Clock3 size={15}/></span> FIFO waitlist <span className="count-pill count-lilac">{waitlist.length}</span></div><span className="fifo-label">FIRST IN, FIRST OUT</span></div>
              {waitlist.length ? <div className="queue-list">{waitlist.map((name,index)=><div className="queue-row" key={name}><div className="queue-position">{String(index+1).padStart(2,"0")}</div><div className={"learner-avatar small "+colors[index%colors.length]}>{initials(name)}</div><div className="learner-info"><b>{name}</b><small>{eligible.includes(name) ? "Prerequisites verified" : "Prerequisites not met"}</small></div><span className={eligible.includes(name) ? "queue-status ready" : "queue-status pending"}>{eligible.includes(name) ? "Ready for promotion" : "On hold"}</span></div>)}</div> : <div className="queue-empty"><div className="queue-empty-graphic"><div/><div/><div/></div><div><b>The line is clear.</b><p>When all seats are taken, eligible learners join the queue here.</p></div></div>}
              {waitlist.length > 0 && <div className="panel-footer"><span>Promotion follows <b>FIFO + eligibility</b></span><button onClick={() => act("/api/refresh",{}, "Waitlist refreshed")}>Refresh queue <ArrowRight size={14}/></button></div>}
            </div>}

            {tab === "activity" && <div className="panel activity-panel">{events.length ? events.map((event,index)=><div className="activity-row" key={index}><div className="activity-dot"><Activity size={15}/></div><div><b>{event[1]}</b><small>{event[0]} · {event[2]}</small></div><span>{index === 0 ? "LATEST" : ""}</span></div>) : <div className="empty-state"><b>No activity yet</b><p>Enrollment actions will appear here.</p></div>}</div>}
          </div>

          <aside className="enroll-column">
            <div className="enroll-card"><div className="enroll-card-head"><div><div className="eyebrow">QUICK ACTION</div><h2>Give a learner<br/>their next step.</h2></div><div className="enroll-illustration"><GraduationCap size={29}/><span>+</span></div></div><p className="enroll-description">Select a learner and we’ll check prerequisites and seat availability for you.</p>
              <label className="field-label" htmlFor="learner-search">LEARNER</label><div className="select-wrap"><select id="learner-search" value={selected} onChange={e=>setSelected(e.target.value)}><option value="">Choose a learner…</option>{filtered.map(n=><option key={n} value={n}>{n}</option>)}</select><ChevronDown size={16}/></div>
              {selected && <div className={eligible.includes(selected) ? "eligibility-note good" : "eligibility-note bad"}>{eligible.includes(selected) ? <ShieldCheck size={16}/> : <CircleHelp size={16}/>}<span><b>{eligible.includes(selected) ? "Prerequisites satisfied" : "Prerequisites not met"}</b><small>{eligible.includes(selected) ? "This learner can enroll or join the queue." : "Update eligibility before enrolling this learner."}</small></span></div>}
              <button className="button button-lime button-full enroll-button" disabled={!selected || busy} onClick={() => act("/api/enroll",{learner_id:selected},"Enrollment processed")}>{busy ? "Processing…" : "Process enrollment"} <ArrowRight size={17}/></button>
              <div className="enroll-card-bottom"><ShieldCheck size={14}/> Duplicate and capacity checks applied</div>
            </div>
            <div className="capacity-card"><div className="capacity-heading"><span>CAPACITY OVERVIEW</span><span className={openSeats ? "open-label" : "full-label"}>{status}</span></div><div className="capacity-big">{enrolled.length}<span> / {capacity} seats</span></div><div className="capacity-track"><span style={{width:fillPercent+"%"}}/></div><div className="capacity-legend"><span><i className="legend-enrolled"/> Enrolled <b>{enrolled.length}</b></span><span><i className="legend-open"/> Open <b>{openSeats}</b></span></div><div className="capacity-tip"><Sparkles size={15}/><span>{openSeats ? "You have room for more eligible learners." : "A dropped seat can be offered to the next eligible learner."}</span></div></div>
            <div className="rules-note"><div className="rules-icon"><ShieldCheck size={18}/></div><div><b>Fairness built in</b><p>Prerequisites are checked before enrollment. When a seat opens, the earliest eligible learner gets priority.</p><button onClick={() => setEligibilityOpen(true)}>Manage prerequisites <ArrowRight size={13}/></button></div></div>
          </aside>
        </section>
        <footer className="footer"><span>© 2026 CourseFlow Studio</span><span><span className="footer-live"/> Local database connected</span><span>Built for thoughtful enrollment <span className="footer-heart">✳</span></span></footer>
      </div>
    </main>
    {showAddLearner && <div className="modal-backdrop" onClick={() => setShowAddLearner(false)}><div className="modal add-learner-modal" onClick={e=>e.stopPropagation()}><button className="modal-close" onClick={() => setShowAddLearner(false)}><X size={18}/></button><div className="eyebrow">LEARNER MANAGEMENT</div><h2>Add a new learner</h2><p>Enter the learner's name and confirm prerequisite status. You can change eligibility later in Offering settings.</p><form onSubmit={async (e) => { e.preventDefault(); const name = newLearnerName.trim(); if (!name) { setToast("Enter a learner name."); return; } setBusy(true); try { const result = await request("/api/learners", { method: "POST", body: JSON.stringify({ learner_name: name, eligible: newLearnerEligible }) }); await reload(); setToast(result.message); setShowAddLearner(false); setNewLearnerName(""); setNewLearnerEligible(false); } catch (error) { setToast(error.message); } finally { setBusy(false); } }}><label className="field-label" htmlFor="new-learner-name">LEARNER NAME</label><input id="new-learner-name" className="add-learner-input" autoFocus maxLength={100} value={newLearnerName} onChange={e=>setNewLearnerName(e.target.value)} placeholder="e.g. Jordan Lee"/><label className="add-learner-eligible"><input type="checkbox" checked={newLearnerEligible} onChange={e=>setNewLearnerEligible(e.target.checked)}/><span><b>Prerequisites completed</b><small>Only check this if the learner has met the course requirements.</small></span></label><div className="modal-actions"><button type="button" className="button button-outline" onClick={() => setShowAddLearner(false)}>Cancel</button><button type="submit" className="button button-dark" disabled={busy}>{busy ? "Adding…" : "Add learner"} <ArrowRight size={15}/></button></div></form></div></div>}
    {eligibilityOpen && <div className="modal-backdrop" onClick={() => setEligibilityOpen(false)}><div className="modal" onClick={e=>e.stopPropagation()}><button className="modal-close" onClick={()=>setEligibilityOpen(false)}><X size={18}/></button><div className="eyebrow">OFFERING RULES</div><h2>Prerequisite eligibility</h2><p>Choose which learners have met the course prerequisites. Ineligible learners cannot enroll or be promoted from the queue.</p><div className="eligible-options">{learnerPool.map(name=><label key={name} className="eligible-option"><input type="checkbox" checked={eligibleDraft.includes(name)} onChange={e=>setEligibleDraft(old=>e.target.checked?[...old,name]:old.filter(n=>n!==name))}/><span className={"learner-avatar small "+colors[learnerPool.indexOf(name)%colors.length]}>{initials(name)}</span><b>{name}</b><span className="option-check"><Check size={13}/></span></label>)}</div><div className="modal-actions"><button className="button button-outline" onClick={()=>setEligibilityOpen(false)}>Cancel</button><button className="button button-dark" disabled={busy} onClick={applyEligibility}>Save eligibility <ArrowRight size={15}/></button></div></div></div>}
    {toast && <div className={toast.toLowerCase().includes("error") || toast.toLowerCase().includes("cannot") || toast.toLowerCase().includes("not") ? "toast toast-error" : "toast"}><span className="toast-check"><Check size={15}/></span>{toast}<button onClick={()=>setToast("")}><X size={14}/></button></div>}
  </div>;
}

createRoot(document.getElementById("root")).render(<React.StrictMode><App /></React.StrictMode>);