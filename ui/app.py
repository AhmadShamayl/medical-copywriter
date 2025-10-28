import streamlit as st
import requests
import json
import os
from datetime import datetime


# Point this to your FastAPI server
FASTAPI_URL = "http://localhost:9000"
DATA_FILE = "data/conversations.json"

st.set_page_config(
    page_title="Medical Copywriter Assistant",
    page_icon="🩺",
    layout="wide"
)

st.title("Medical Copywriter Assistant")

def load_conversations():
    if not os.path.exists (DATA_FILE):
        return {}
    
    try: 
        with open(DATA_FILE, "r", encoding = "utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, OSError) as e:
        print (f"Failed to load conversations: {e}")
        return {}
    
def save_conversations(convos):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f ,indent=2)
    
conversations = load_conversations()
user_id = "user_123"


# Initialize session
if "session_id" not in st.session_state:
    with st.spinner("Starting new conversation..."):
        resp = requests.post(f"{FASTAPI_URL}/start_conversation", json={"user_id": "user_123"})
        if resp.status_code == 200:
            st.session_state.session_id = resp.json()["session_id"]
            st.session_state.messages = []
            conversations.setdefault(user_id, {})[st.session_state.session_id] = []
            save_conversations(conversations)

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
    st.title("🩺 MediCopy AI")
    st.markdown("Your medical copywriter companion")
    st.subheader("Past Conversations")

    user_convos = conversations.get(user_id, {})

    for session_id, msgs in user_convos.items():
        print(session_id, msgs)
        if st.button(f"{session_id[:8]}...", key = f"load_{session_id}"):
            st.session_state.session_id = session_id
            st.session_state.messages = user_convos[session_id]
            st.experimental_rerun()

    st.markdown("---")

    if st.button("Start New Chat", key = "start_new_chat_sidebar"):
        resp = requests.post(f"{FASTAPI_URL}/start_conversation", json={"user_id": user_id})
        if resp.status_code == 200:
            new_session = resp.json()["session_id"]
            st.session_state.session_id = new_session
            st.session_state.messages = []
            conversations[user_id][new_session] = []
            save_conversations(conversations)
            st.experimental_rerun()
        else:
            st.error("Failed to start new conversation.")