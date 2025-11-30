# run_all_sessions.py
# -------------------------------------------------
# Automated driver for the long‑running coverage‑hardener.
# It repeatedly calls `python -m harness.run_session --session-id N`
# and stops when the harness reports a NO_OP (i.e. nothing left to improve).
# -------------------------------------------------
import subprocess
import json
import pathlib
import sys
import time

# Repository root (where this script lives)
REPO_ROOT = pathlib.Path(__file__).parent
PLAN_FILE = REPO_ROOT / "coverage_plan.json"

def load_plan() -> list[dict]:
    try:
        return json.loads(PLAN_FILE.read_text())
    except Exception:
        return []

def any_pending(plan: list[dict]) -> bool:
    return any(item.get("status") != "done" for item in plan)

def run_session(session_id: int) -> int:
    cmd = [sys.executable, "-m", "harness.run_session", "--session-id", str(session_id)]
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("--- STDERR ---", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
    return result.returncode

def main():
    session_id = 1
    while True:
        rc = run_session(session_id)
        if rc != 0:
            print(f"[run_all_sessions] Session {session_id} failed with exit code {rc}. Retrying next session...", file=sys.stderr)
            # Don't exit, just continue to next session
        
        plan = load_plan()
        if not any_pending(plan):
            print("[run_all_sessions] 🎉 All modules have reached target coverage. Finished.")
            break
        time.sleep(2)  # optional pause to avoid rate‑limit issues
        session_id += 1

if __name__ == "__main__":
    main()
