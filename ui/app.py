import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation.manager import start_conversation, get_response, reset_conversation


st.set_page_config(page_title = "Medical Copyrwriter Assistant" , page_icon = "🩺", layout = "wide")

st.sidebar.title("Controls")

user_id = st.sidebar.text_input( "User ID" , value = "demo_user")
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if st.sidebar.button("Start New Conversation"):
    session_id = start_conversation(user_id)
    st.session_state.session_id = session_id   
    st.sidebar.success(f"New session started: {session_id}")

if st.sidebar.button("reset Memory") and st.session_state.session_id:
    reset_conversation(st.session_state.session_id)
    st.sidebar.warning("Memory has been reset")

st.title("Medical Copywriter Assistant")
if not st.session_state.session_id:
    st.info("Start a conversation in the sidebar to begin")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

        for msg in st.session_state.messages: 
            with st.chat_message(msg['role']):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask me anything about medical research, treatments, or copywriting..."):
            st.session_state.message.append({"role" : "user" , "content" : prompt})
            with st.chat_message("user"):
                st.matkdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    resp = get_response(st.session_state.session_id , prompt)

                    answer = resp.get("answer" , "No response generated.")
                    sources = resp.get("sorurces" , [])

                    st.mardown(answer)
                    if sources:
                        st.markdown ("**Sources:**")
                        for src in sources:
                            st.mardown(f" - [{src['title']}]({src['url']}) ({src['source']})")
                    
                    st.session_state.messages.append({"role" : "assistant" , "content" : answer})