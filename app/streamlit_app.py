import os
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Configuration & Session State Initialization
# ─────────────────────────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="AI Triage System", layout="wide", page_icon="🏥")

def init_state():
    defaults = {
        "role": None,
        "auth_done": False,
        "user_name": "",
        "user_email": "",
        "messages": [],
        "notes": [],
        "chat_active": False,
        "finished": False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
init_state()

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
# @st.cache_data
def fetch_assessments():
    try:
        resp = requests.get(f"{API_URL}/view-assessments")
        resp.raise_for_status()
        return resp.json().get("assessments", [])
    except:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar Role & Auth
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏥 AI Triage System")
    st.session_state.role = st.radio("I am a:", ["Patient", "Staff"], key="role_radio")
    if not st.session_state.auth_done:
        st.subheader("Sign In")
        name = st.text_input("Name", key="signin_name")
        email = st.text_input("Email", key="signin_email")
        if st.button("Sign In", key="signin_btn"):
            if name and email:
                st.session_state.user_name = name
                st.session_state.user_email = email
                st.session_state.auth_done = True
                # st.experimental_rerun()
            else:
                st.error("Name and email required.")
    else:
        st.markdown(f"**Signed in as:** {st.session_state.user_name} ({st.session_state.user_email})")

if not st.session_state.auth_done:
    st.write("Please sign in using the sidebar.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Patient Chat Interface (with smooth chat_input + rerun)
# ─────────────────────────────────────────────────────────────────────────────
def patient_interface():
    st.header(f"🩺 Patient Assessment ({st.session_state.user_name})")
    # Start new
    if not st.session_state.chat_active:
        if st.button("Start New Triage Assessment", key="start_assess"):
            st.session_state.chat_active = True
            st.session_state.messages = []
            try:
                r = requests.post(
                    f"{API_URL}/chat-to-triage",
                    json={
                        "message": "",
                        "history": [],
                        "patient_name": st.session_state.user_name,
                        "patient_email": st.session_state.user_email
                    }
                )
                r.raise_for_status()
                st.session_state.messages.append({"role":"assistant","content":r.json()["response"]})
                # st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.chat_active = False
    # Render conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    # Chat input
    if st.session_state.chat_active:
        if user_input := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role":"user","content":user_input})
            with st.chat_message("user"):
                st.write(user_input)
            try:
                with st.spinner("Processing..."):
                    r = requests.post(
                        f"{API_URL}/chat-to-triage",
                        json={
                            "message": user_input,
                            "history": st.session_state.messages,
                            "patient_name": st.session_state.user_name,
                            "patient_email": st.session_state.user_email
                        }
                    )
                    r.raise_for_status()
                    data = r.json()
                    st.session_state.messages.append({"role":"assistant","content":data["response"]})
                    with st.chat_message("assistant"):
                        st.write(data["response"])
                    if data.get("finished", False):
                        st.session_state.chat_active = False
                        st.success("✅ Assessment Complete")
                    # st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Staff Dashboard
# ─────────────────────────────────────────────────────────────────────────────
def staff_interface():
    st.header(f"👩‍⚕️ Staff Dashboard ({st.session_state.user_name})")
    df = pd.DataFrame(fetch_assessments())
    if df.empty:
        st.info("No assessments yet.")
        return
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"**Logged in as:** {st.session_state.user_name} ({st.session_state.user_email})")
    cols = ["assessment_id","esi_level","created_at"]
    if "patient_name" in df.columns and "patient_email" in df.columns:
        cols = ["assessment_id","patient_name","patient_email","esi_level","created_at"]
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Assessments", len(df))
    c2.metric("Avg. ESI Level", round(df['esi_level'].mean(),1))
    c3.metric("Last Assessment", df.iloc[0]['created_at'])
    st.dataframe(df[cols], use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Main Flow
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.role == "Patient":
    patient_interface()
else:
    staff_interface()