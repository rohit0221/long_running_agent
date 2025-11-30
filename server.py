import os
import subprocess
import threading
import json
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
REPO_ROOT = Path(__file__).parent
STATIC_DIR = REPO_ROOT / "static"
PLAN_FILE = REPO_ROOT / "coverage_plan.json"
HISTORY_FILE = REPO_ROOT / "coverage_history.json"
LOG_FILE = REPO_ROOT / "agent_progress.log"
TESTS_DIR = REPO_ROOT / "target_repo" / "tests"

# Ensure static dir exists
os.makedirs(STATIC_DIR, exist_ok=True)

# Global state for the running process
agent_process = None

@app.get("/")
async def read_index():
    return FileResponse(STATIC_DIR / "index.html")

@app.post("/start")
async def start_agent(background_tasks: BackgroundTasks):
    global agent_process
    if agent_process and agent_process.poll() is None:
        print("[server] Agent already running")
        return {"status": "running", "message": "Agent is already running"}
    
    # Run the agent in a separate process using the same Python interpreter
    import sys
    cmd = [sys.executable, "run_all_sessions.py"]
    print(f"[server] Starting agent with command: {cmd}")
    try:
        agent_process = subprocess.Popen(
            cmd, 
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            text=True,
            bufsize=1  # Line buffered
        )
        print(f"[server] Agent started with PID: {agent_process.pid}")
        return {"status": "started", "message": "Agent started", "pid": agent_process.pid}
    except Exception as e:
        print(f"[server] Failed to start agent: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/stop")
async def stop_agent():
    global agent_process
    if agent_process and agent_process.poll() is None:
        agent_process.terminate()
        try:
            agent_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            agent_process.kill()
            agent_process.wait()
        return {"status": "stopped", "message": "Agent stopped"}
    return {"status": "not_running", "message": "Agent is not running"}

@app.get("/status")
async def get_status():
    # Read Plan
    plan = []
    if PLAN_FILE.exists():
        try:
            plan = json.loads(PLAN_FILE.read_text())
        except:
            pass
            
    # Read History
    history = []
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text())
        except:
            pass
            
    # List Test Files
    test_files = []
    if TESTS_DIR.exists():
        test_files = [f.name for f in TESTS_DIR.glob("test_*.py")]
        
    # Check if agent is running
    is_running = agent_process is not None and agent_process.poll() is None
    
    return {
        "running": is_running,
        "plan": plan,
        "history": history,
        "test_files": sorted(test_files)
    }

@app.get("/logs")
async def get_logs():
    if LOG_FILE.exists():
        return {"logs": LOG_FILE.read_text()}
    return {"logs": ""}

# Mount static files (if we had more assets, but we just have index.html for now)
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
