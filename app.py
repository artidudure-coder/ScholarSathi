"""Streamlit UI:  streamlit run app.py"""
import streamlit as st
import eligibility, llm
from agent import ScholarAgent

st.set_page_config(page_title="ScholarSathi", page_icon="🎓", layout="wide")
st.title("🎓 ScholarSathi")
st.caption("Agentic RAG assistant that finds scholarships you qualify for, explains why, and tracks deadlines.")

with st.sidebar:
    st.header("Student profile")
    profile = {
        "category": st.selectbox("Category", ["Open", "EWS", "OBC", "SC", "ST", "VJNT", "SBC"]),
        "income": st.number_input("Annual family income (Rs)", 0, 5_000_000, 400_000, 10_000),
        "level": st.selectbox("Course level", ["Diploma", "UG", "PG"], index=1),
        "percentage": st.number_input("Previous exam percentage", 0.0, 100.0, 68.0, 0.5),
        "gender": st.selectbox("Gender", ["Female", "Male", "Other"]),
        "domicile": st.text_input("Domicile state", "Maharashtra"),
    }
    st.info("LLM mode: **ON**" if llm.available() else "LLM mode: OFF (offline rule engine). Set ANTHROPIC_API_KEY to enable the agent.")

agent = ScholarAgent(profile)
tab1, tab2 = st.tabs(["Your matches", "Ask the agent"])
with tab1:
    for r in eligibility.rank(profile, agent.criteria):
        icon = {"ELIGIBLE": "✅", "NOT ELIGIBLE": "❌", "CLOSED": "⏰"}[r["status"]]
        with st.expander(f"{icon} {r['scheme']} - {r['status']}", expanded=r["status"] == "ELIGIBLE"):
            if r["days_left"] is not None and r["status"] != "CLOSED":
                (st.warning if r["days_left"] <= 21 else st.write)(f"Deadline {r['deadline']} - {r['days_left']} days left")
            st.write(r["benefit"])
            for p in r["passed"]: st.write(f"✔ {p}")
            for f in r["failed"]: st.write(f"✘ {f}")
            if r["status"] == "ELIGIBLE": st.write("**Documents:** " + ", ".join(r["documents"]))
with tab2:
    q = st.text_input("Ask anything (e.g. 'How do I apply for the girls fellowship?')")
    if q:
        st.text(agent.ask(q))
