from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import asyncio
import json
from .agents.coordinator import ResearchCoordinator
from .db.models import init_db, SessionLocal, ResearchSession
import os

app = FastAPI(title="Academic Research AI Agent")

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket Client Connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"WebSocket Client Disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        print(f"Broadcasting: {message.get('agent')} - {message.get('action')}")
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to a client: {e}")

manager = ConnectionManager()
coordinator = ResearchCoordinator(websocket_manager=manager)

# Init DB on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Models
class ResearchRequest(BaseModel):
    topic: str

@app.post("/research")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(coordinator.run_workflow, request.topic)
    return {"message": "Research started", "topic": request.topic}

@app.get("/sessions/{session_id}")
async def get_session(session_id: int):
    db = SessionLocal()
    session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
    db.close()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.get("/download/{session_id}/{format}")
async def download_paper(session_id: int, format: str):
    if format not in ["md", "latex"]:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'md' or 'latex'.")
    db = SessionLocal()
    session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
    db.close()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    filename = f"research_paper_{session_id}.{format}"
    filepath = f"data/{filename}"
    
    content = session.final_paper_md if format == "md" else session.final_paper_latex
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    return FileResponse(filepath, filename=filename)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    return FileResponse("static/index.html")
