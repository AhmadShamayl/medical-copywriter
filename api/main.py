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


class ResetRequest(BaseModel):
    session_id: str


@app.get("/")
async def root():
    return {"message" : "Medical Copywriter API is running! Visit /docs for Swagger UI"}


@app.get("favicon.ico" , include_in_schema=False)
async def favicon():
    favicon_path = os.path.join("api" , "static" , "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return JSONResponse(status_code = 404, content = {"detail" : "Favicon not found"})


@app.post("/start_conversation")
async def api_start_conversation(req: StartRequest):
    session_id = start_conversation(req.user_id)
    return {"session_id" : session_id}


@app.post("/get_response")
async def api_get_response(req: ChatRequest):
    resp = get_response(req.session_id , req.query)
    return {"response" : resp}


@app.post("/ask")
async def ask(req: ChatRequest):
    resp = get_response(req.session_id , req.query)
    return {"response" : resp}



@app.post("/reset_conversation")
async def reset (req: ResetRequest):
    reset_conversation(req.session_id)
    return {"message" : f"Session {req.session_id} reset."}


@app.get("/list_sessions")
async def list_sessions():
    sessions = list_active_sessions()
    return {"active_sessions"  : sessions}