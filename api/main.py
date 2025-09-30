from fastapi import FastAPI
from fastapi.responses import FileResponse , JSONResponse
from pydantic import BaseModel
from conversation.manager import start_conversation , get_response, reset_conversation , list_active_sessions
import os

app = FastAPI(title = "Medical Copywriter API", version = "1.0.0")


class ChatRequest(BaseModel):
    session_id : str
    query : str

class StartRequest(BaseModel):
    user_id : str

@app.get("/")
async def root():
    return {"message" : "Medical Copywriter API is running! Visit /docs for Swagger UI"}

@app.get("favicon.ico" , include_in_schema=False)
async def favicon():
    favicon_path = os.path.join("api" , "static" , "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return JSONResponse(status_code = 404, content = {"detail" : "Favicon not found"})

@app.post("/start/{user_id}")
async def start(user_id: str):
    session_id = start_conversation(user_id)
    return {"session_id" : session_id, "message" : "Conversation Starterd"}

@app.post("/ask/{session_id}")
async def ask(session_id: str, query:str):
    response = get_response(session_id , query)
    return query


@app.post("/reset/{session_id}")
def reset (session_id : str):
    reset_conversation(session_id)
    return {"message" : f"Session {session_id} reset."}

@app.get("/sessions")
def list_sessions():
    sessions = list_active_sessions()
    return {"active_sessions"  : sessions}