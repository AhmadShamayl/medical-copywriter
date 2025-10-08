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
            st.session_state.messages = []
        else:
            st.error("Failed to start conversation. Please check FastAPI server.")
            st.stop()


for msg in st.session_state.get("messages", []):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("Ask your medical copywriting question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
       with st.spinner("thinking..."):
           try:
               resp = requests.post(
                   f"{FASTAPI_URL}/get_response",
                   json = {"session_id": st.session_state.session_id, "query": prompt},
                   timeout=60
               )
               if resp.status_code == 200:
                   data = resp.json()

                   answer =(
                       data.get("response", {}).get("answer")
                       or data.get("answer")
                       or "No response recieved from backend"
                   )

                   st.markdown(answer)

                   if "sources" in data and isinstance(data["sources"], list):
                       st.markdown("**Sources:**")
                       for src in data["sources"]:
                            title = src.get("title" , "Untitled")
                            url = src.get("url" , "#")
                            st.markdown(f"- [{title}]({url})")

                   st.session_state.messages.append({"role": "assistant", "content": answer})
               else:
                   st.error(f"Backend error: {resp.status_code}")
                   st.session_state.messages.append({"role": "assistant", "content": "Failed to fetch response from backend"})
                
           except Exception as e:
               st.error(f"Request failed: {e}")
               st.session_state.messages.append({"role": "assistant", 
                                                 "content": f"An error occured: {e}"})

with st.sidebar:
    st.subheader("Active Sessions")
    if st.button("Refresh Active Sessions"):
        resp = requests.get(f"{FASTAPI_URL}/list_sessions")
        if resp.status_code == 200:
            sessions = resp.json()
            for s in sessions:
                st.sidebar.write(f"- {s['session_id']} ({s['user_id']})")
        else:
            st.sidebar.error("Failed to fetch sessions.")