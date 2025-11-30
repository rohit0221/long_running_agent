import os
import json
import shutil
import logging
from datetime import datetime
from typing import List, Dict, Any

# Constants
ARTIFACTS_DIR = "."
COVERAGE_PLAN_FILE = os.path.join(ARTIFACTS_DIR, "coverage_plan.json")
AGENT_PROGRESS_FILE = os.path.join(ARTIFACTS_DIR, "agent_progress.log")
COVERAGE_HISTORY_FILE = os.path.join(ARTIFACTS_DIR, "coverage_history.json")
BACKUP_EXT = ".bak"

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Harness")

def init_artifacts():
    """Initialize artifacts if they don't exist."""
    if not os.path.exists(COVERAGE_PLAN_FILE):
        with open(COVERAGE_PLAN_FILE, "w") as f:
            json.dump([], f, indent=2)
    
    if not os.path.exists(AGENT_PROGRESS_FILE):
        with open(AGENT_PROGRESS_FILE, "w") as f:
            f.write(f"[{datetime.now().isoformat()}] Log initialized.\n")

    if not os.path.exists(COVERAGE_HISTORY_FILE):
        with open(COVERAGE_HISTORY_FILE, "w") as f:
            json.dump([], f, indent=2)

def log_progress(session_id: int, message: str, result: str = "INFO", reason: str = None):
    """Append to agent_progress.log."""
    timestamp = datetime.now().isoformat()
    entry = f"[{timestamp}] Session {session_id}\n  {message}"
    if reason:
        entry += f"\n  Reason: {reason}"
    entry += f"\n  Result: {result}\n"
    
    with open(AGENT_PROGRESS_FILE, "a") as f:
        f.write(entry + "\n")
    logger.info(f"Session {session_id}: {message} ({result})")

def append_history(session_id: int, overall_coverage: float, result: str):
    """Append to coverage_history.json."""
    try:
        with open(COVERAGE_HISTORY_FILE, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    
    history.append({
        "session_id": session_id,
        "overall_coverage": overall_coverage,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })
    
    with open(COVERAGE_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def backup_file(file_path: str) -> str:
    """Create a backup of the file."""
    backup_path = file_path + BACKUP_EXT
    shutil.copy2(file_path, backup_path)
    return backup_path

def restore_file(file_path: str):
    """Restore file from backup."""
    backup_path = file_path + BACKUP_EXT
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        os.remove(backup_path)

def delete_backup(file_path: str):
    """Delete the backup file."""
    backup_path = file_path + BACKUP_EXT
    if os.path.exists(backup_path):
        os.remove(backup_path)
