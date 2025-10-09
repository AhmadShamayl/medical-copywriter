import os 
import uuid
from typing import Dict
from memory.conversation_memory import HybridConversationMemory
from langgraph.store.memory import InMemoryStore
from rag_pipeline import generate_answer


store = InMemoryStore ()
SESSION_NAMESPACE = "memory/sessions"

os.makedirs(SESSION_NAMESPACE, exist_ok =True)

_sessions: Dict[str , HybridConversationMemory] = {}
_sessions_user_map = {}

def start_conversation(user_id: str) -> str:
    session_id = str(uuid.uuid4())
    mem = HybridConversationMemory()
    _sessions[session_id] = mem
    _sessions_user_map[session_id]  =user_id

    session_record = {
        "user_id" : user_id,
        "summary" : mem.summary,
        "buffer" : list(mem.buffer),
        "turn_count" : mem.turn_count
    }

    store.put(
        namespace = SESSION_NAMESPACE, 
        key = session_id,
        value = session_record
        )
    
    print (f"[CONVO] Started new session {session_id} for user {user_id}")
    return session_id

def get_response (session_id: str , query: str) -> str:
    mem = _sessions.get(session_id)
    if not mem:
        raise ValueError(f"no actove session found for {session_id}")
    mem = _sessions[session_id]
    memory_context = mem.load_context()
    result = generate_answer(query, memory= mem , memory_context = memory_context)
    mem.save_context(query, result["answer"])

    user_id = _sessions_user_map.get(session_id, "unknown_user")
    store.put (
        namespace= SESSION_NAMESPACE,
        key = session_id,
        value= { 
            "user_id" : user_id,
            "summary" : mem.summary,
            "buffer" : list(mem.buffer),
            "turn_count" : mem.turn_count
        }
    )

    return result

def reset_conversation (session_id:str):
    mem = _sessions.get(session_id)
    if mem: 
        mem.reset_memory()
        user_id = _sessions_user_map.get(session_id , "unknown_user")
        print(f"[CONVO] Session {session_id} has been reset")

        store.put(
            namespace= SESSION_NAMESPACE,
            key = session_id,
            value = {
                "user_id" : user_id,
                "summary" : "",
                "buffer": [],
                "turn_count" : 0
            }
        )
        print (f"[CONVO] Session {session_id} has been reset")



def get_user_sessions(user_id : str):
    all_sessions = store.search(SESSION_NAMESPACE)
    user_sessions = []
    for s in all_sessions:
        data = store.get(namespace=SESSION_NAMESPACE, key = s.key)
        if data and data.get("user_id" ) == user_id:
            user_sessions.append(s.key) 
    return user_sessions


def list_active_sessions():
    """
    Return all sessions stored in the InMemoryStore
    as [{'session_id': ..., 'user_id': ...}]
    """
    result = []

    try:
        all_sessions = store.search(SESSION_NAMESPACE)
        print(f"[DEBUG] store.search() returned: {all_sessions}")
    except Exception as e:
        print(f"[ERROR] Could not fetch sessions: {e}")
        return []

    if not all_sessions:
        print("[INFO] No active sessions found.")
        return []

    for idx, s in enumerate(all_sessions):
        data = {}  # Always define it at the top of the loop to avoid NameError
        try:
            if hasattr(s, "key"):  # When store returns an object
                session_id = getattr(s, "key", None)
                data = getattr(s, "value", {}) or {}
            else:  # When store returns string keys
                session_id = str(s)
                data = store.get(namespace=SESSION_NAMESPACE, key=session_id) or {}

            result.append({
                "session_id": session_id,
                "user_id": data.get("user_id", "unknown_user"),
                "turn_count": data.get("turn_count", 0)
            })
        except Exception as inner_e:
            print(f"[WARN] Failed to process session {idx}: {inner_e}")
            continue

    print(f"[DEBUG] Active sessions result: {result}")
    return result

    