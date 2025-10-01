import streamlit as st
import requests

# Point this to your FastAPI server
FASTAPI_URL = "http://localhost:9000"

st.set_page_config(
    page_title="Medical Copywriter Assistant",
    page_icon="🩺",
    layout="wide"
)

st.title("Medical Copywriter Assistant")

# Initialize session
if "session_id" not in st.session_state:
    with st.spinner("Starting new conversation..."):
        resp = requests.post(f"{FASTAPI_URL}/start_conversation", json={"user_id": "user_123"})
        if resp.status_code == 200:
            st.session_state.session_id = resp.json()["session_id"]
        else:
            st.error("Failed to start conversation. Please check FastAPI server.")
            st.stop()

# Chat input
query = st.text_input("Ask your medical question:")

if st.button("Send") and query:
    with st.spinner("Fetching response..."):
        resp = requests.post(f"{FASTAPI_URL}/get_response", json={
            "session_id": st.session_state.session_id,
            "query": query
        })

        if resp.status_code == 200:
            data = resp.json()
            st.markdown(f"**Assistant:** {data['response']['answer']}")
            
            if "sources" in data:
                st.markdown("**Sources:**")
                for src in data["sources"]:
                    st.markdown(f"- [{src['title']}]({src['']})")
        else:
            st.error("Error communicating with backend.")

# Show active sessions (optional)
if st.sidebar.button("Refresh Active Sessions"):
    resp = requests.get(f"{FASTAPI_URL}/list_sessions")
    if resp.status_code == 200:
        sessions = resp.json()
        st.sidebar.write("Active Sessions")
        for s in sessions:
            st.sidebar.write(f"- {s['session_id']} ({s['user_id']})")
    else:
        st.sidebar.error("Failed to fetch sessions.")
