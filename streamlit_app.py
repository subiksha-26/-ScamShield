import streamlit as st
from app import scan_offer, check_resume, GAME, LEVELS, FLAGS, FEED, LOCK

st.set_page_config(page_title="ScamShield AI", page_icon="🛡️", layout="wide")
st.title("🛡️ ScamShield AI")
st.caption("Fake Job & Internship Scam Detection · Detect. Explain. Report. Protect, before you pay.")
t1, t2, t3, t4, t5 = st.tabs(["Student", "Recruiter", "Dashboard", "Scam or Real?", "About"])

with t1:
    st.subheader("Check a job message")
    text = st.text_area("Paste the job offer or message", height=160, max_chars=12000,
                        placeholder="Congratulations! Pay a registration fee to confirm your job...")
    st.caption("Do not paste passwords, ID numbers or bank details.")
    if st.button("Analyse message", type="primary") and text.strip():
        st.session_state.res = scan_offer(text)
    r = st.session_state.get("res")
    if r:
        c1, c2, c3 = st.columns(3)
        c1.metric("Risk level", r["level"]); c2.metric("Score", f"{r['score']} / 100"); c3.metric("Scam type", r["type"])
        st.progress(r["score"] / 100)
        st.markdown("**Your message, risky words highlighted**")
        st.markdown(f"<div style='white-space:pre-wrap'>{r['highlighted']}</div>", unsafe_allow_html=True)
        st.markdown("**Why it was flagged**")
        for x in r["reasons"]: st.write("•", x)
        st.info("**Safer next step:** " + r["advice"])
        if r["level"] != "Low":
            st.markdown("**Safe reply helper**: ask the recruiter for their official company email, interview date/time, the official job listing link, and why any payment is needed.")
            st.markdown("**Complaint draft** (fill the [brackets], then submit on [cybercrime.gov.in](https://cybercrime.gov.in/). Call **1930** for financial fraud)")
            st.code(r["complaint"], language=None)
        st.warning("Basic keyword-rule check, not a trained ML model. A low score never proves an offer is safe.")

with t2:
    st.subheader("Recruiter Mode: verify a resume")
    rt = st.text_area("Paste resume text", height=200, max_chars=20000)
    if st.button("Verify resume", type="primary") and rt.strip():
        st.session_state.rr = check_resume(rt)
    rr = st.session_state.get("rr")
    if rr:
        st.metric("Verification", rr["level"], f"{rr['score']} / 100 risk", delta_color="off")
        st.markdown("**Flags**")
        for f in rr["flags"]: st.write("•", f)
        st.markdown("**Suggested interview questions**")
        for q in rr["questions"]: st.write("•", q)

with t3:
    st.subheader("Live dashboard")
    st.caption("Updates every 3 seconds. Starts with demo baseline data; every scan is added live.")
    @st.fragment(run_every=3)
    def live():
        with LOCK:
            lv, fl, fd = dict(LEVELS), FLAGS.most_common(6), list(FEED)
        a, b = st.columns(2)
        a.metric("Total scans", sum(lv.values())); b.metric("High risk", lv.get("High", 0))
        x, y = st.columns(2)
        x.markdown("**Risk levels**"); x.bar_chart(lv)
        y.markdown("**Top red-flag words**"); y.bar_chart(dict(fl))
        st.markdown("**Live scan feed**")
        st.dataframe(fd or [{"info": "No live scans yet"}], use_container_width=True, hide_index=True)
    live()

with t4:
    st.subheader("Scam or Real?")
    s = st.session_state
    s.setdefault("i", 0); s.setdefault("score", 0); s.setdefault("ans", None)
    if s.i >= len(GAME):
        st.success(f"You scored {s.score} / {len(GAME)}")
        if st.button("Play again"): s.i, s.score, s.ans = 0, 0, None; st.rerun()
    else:
        q = GAME[s.i]
        st.caption(f"Question {s.i + 1} of {len(GAME)} · Score {s.score}")
        st.markdown(f"> {q['m']}")
        if s.ans is None:
            a, b = st.columns(2)
            if a.button("Scam", use_container_width=True): s.ans = True; s.score += q["scam"]; st.rerun()
            if b.button("Real", use_container_width=True): s.ans = False; s.score += (not q["scam"]); st.rerun()
        else:
            (st.success if s.ans == q["scam"] else st.error)(("Correct! " if s.ans == q["scam"] else "Not quite. ") + q["why"])
            if st.button("Next"): s.i += 1; s.ans = None; st.rerun()

with t5:
    st.subheader("About")
    st.write("Team: Sivadharshini S, Sruthiks G, Subiksha D, Yogalakshme M")
    st.write("Uses keyword and rule checks. No trained ML model, OCR/PDF scanning or database yet. Never treat a result as a final verdict.")
