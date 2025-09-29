from fastapi import FastAPI
from pydantic import BaseModel
from conversation.manager import start_conversation , get_response, reset_conversation , list_active_sessions

app = FastAPI(title = "Medical Copywriter API")


class ChatRequest(BaseModel):
    session_id : str
    query : str

class StartRequest(BaseModel):
    user_id : str

@app.get("/")
async def root():
    return {"message" : "Medical Copywriter API is running"}

@app.post("/start")
def start_chat(req: StartRequest):
    session_id = start_conversation(req.user_id)
    return {"session_id" : session_id, "message" : "Conversation Starterd"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        result = get_response(req.session_id, req.query)
        return {
            "answer" : result["answer"],
            "sources" : result["sources"]
        }
    except Exception as e:
        return {"error" : str(e)}


@app.post("/reset/{session_id}")
def reset (session_id : str):
    reset_conversation(session_id)
    return {"message" : f"Session {session_id} reset."}

@app.get("/sessions")
def list_sessions():
    sessions = list_active_sessions()
    return {"active_sessions"  : sessions}