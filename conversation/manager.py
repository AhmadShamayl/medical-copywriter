import os 
import uuid
from typing import Dict
from memory.conversation_memory import HybridConversationMemory
from rag_pipeline import generate_answer

SESSION_DIR = "memory/sessions"

os.makedirs(SESSION_DIR, exist_ok =True)

_sessions: Dict[str , HybridConversationMemory] = {}

def start_conversation(user_id: str) -> str:
    session_id = str =(uuid.uuid4())
    memory_path = os.path.join(SESSION_DIR, f"{session_id}.json")
    mem = HybridConversationMemory(save_path = memory_path)
    _sessions[session_id] = mem
    print (f"[CONVO] Started new session {session_id} for user {user_id}")
    return session_id

def get_response (session_id: str , query: str) -> str:

    if session_id not in _sessions:
        memory_path = os.path.join(SESSION_DIR, f"{session_id}.json")
        if os.path.exists(memory_path):
            mem = HybridConversationMemory()
            mem._load_memory()
            _sessions[session_id] = mem
        else:
            raise ValueError(f"Session {session_id} does not exist.")
        

    mem = _sessions[session_id]
    memory_context = mem.load_context()
    answer = generate_answer(query)
    mem.save_context(query, answer)

    return answer

def reset_conversation (session_id:str):
    if session_id not in _sessions:
        raise ValueError(f"Session {session_id} not found.")
    
    mem = _sessions[session_id]
    mem.reset_memory()
    del _sessions[session_id]

    memory_path = os.path.join(SESSION_DIR, f'{session_id}.json')
    if os.path.exists(memory_path):
        os.remove(memory_path)

    print(f"[CONVO] Session {session_id} has been reset.")

def list_sessions() -> Dict[str, str]:
    return list (_sessions.keys())

