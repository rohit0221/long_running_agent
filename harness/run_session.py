import os
import sys
import argparse
import subprocess
import logging
from harness.utils import (
    init_artifacts, log_progress, append_history, 
    backup_file, restore_file, delete_backup,
    COVERAGE_PLAN_FILE
)
from harness.coverage_manager import (
    update_coverage_plan, select_target_module, 
    mark_module_status, get_overall_coverage
)
from harness.llm_client import LLMClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SessionRunner")

def run_tests_script():
    """Run the test script. Returns True if success, False otherwise."""
    # Detect OS and choose script
    if os.name == 'nt':
        script = ["harness\\run_tests.bat"]
    else:
        script = ["bash", "harness/run_tests.sh"]
    
    logger.info(f"Running tests with command: {script}")
    result = subprocess.run(script, capture_output=True, text=True)
    
    # Exit code 0 means tests passed.
    # Exit code 5 means "no tests collected", which is fine for a fresh start.
    if result.returncode != 0 and result.returncode != 5:
        logger.error("Tests failed!")
        logger.error(result.stdout)
        logger.error(result.stderr)
        return False
    
    logger.info("Tests passed.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Run a coverage improvement session.")
    parser.add_argument("--session-id", type=int, default=1, help="Session ID")
    args = parser.parse_args()
    
    session_id = args.session_id
    logger.info(f"Starting Session {session_id}")
    
    # 1. Init artifacts
    init_artifacts()
    
    # 2. Health Check
    if not run_tests_script():
        log_progress(session_id, "Initial health check failed.", "NO_OP", "Tests failed before starting.")
        # Even if NO_OP, we might want to record it in history if we can get coverage, 
        # but if tests fail, coverage might be invalid. Let's just exit.
        # For history consistency, we could append a 0.0 or last known, but let's skip for now or append 0.
        append_history(session_id, get_overall_coverage("coverage.xml"), "NO_OP")
        sys.exit(1)
        
    # 3. Update Plan
    update_coverage_plan("coverage.xml")
    
    # 4. Select Module
    target = select_target_module()
    if not target:
        log_progress(session_id, "No pending modules found in plan.", "NO_OP", "All modules meet target coverage.")
        append_history(session_id, get_overall_coverage("coverage.xml"), "NO_OP")
        logger.info("All modules meet target coverage!")
        sys.exit(0)
        
    module_path = target["module"]
    current_cov = target["current_coverage"]
    logger.info(f"Selected target: {module_path} (Coverage: {current_cov}%)")
    
    # Mark as in_progress
    mark_module_status(module_path, "in_progress")
    
    # 5. Gather Context
    source_file = module_path
    filename = os.path.basename(source_file)
    test_filename = f"test_{filename}"
    test_file = os.path.join("target_repo", "tests", test_filename)
    
    if not os.path.exists(source_file):
        logger.error(f"Source file {source_file} not found.")
        log_progress(session_id, f"Source file {source_file} missing.", "NO_OP", "Source file not found.")
        append_history(session_id, get_overall_coverage("coverage.xml"), "NO_OP")
        sys.exit(1)
        
    if not os.path.exists(test_file):
        logger.info(f"Test file {test_file} does not exist. Will create.")
        existing_test_code = ""
    else:
        with open(test_file, "r") as f:
            existing_test_code = f.read()
            
    with open(source_file, "r") as f:
        module_code = f.read()
        
    # 6. Call LLM
    llm = LLMClient()
    try:
        new_test_code = llm.generate_tests(
            module_code=module_code,
            module_path=module_path,
            existing_test_code=existing_test_code,
            coverage_info=f"Current coverage: {current_cov}%"
        )
    except Exception as e:
        log_progress(session_id, f"LLM call failed: {e}", "NO_OP", "LLM API Error")
        append_history(session_id, get_overall_coverage("coverage.xml"), "NO_OP")
        sys.exit(1)
        
    # 7. Apply Changes (with Backup)
    backup_path = None
    if os.path.exists(test_file):
        backup_path = backup_file(test_file)
    
    with open(test_file, "w") as f:
        f.write(new_test_code)
        
    # 8. Re-run Health Check
    if run_tests_script():
        # Success
        logger.info("Changes verified. Tests passed.")
        
        # Update artifacts
        update_coverage_plan("coverage.xml")
        overall_cov = get_overall_coverage("coverage.xml")
        append_history(session_id, overall_cov, "SUCCESS")
        
        # Get new coverage for the module to log
        from harness.coverage_manager import parse_coverage_xml
        new_cov_data = parse_coverage_xml("coverage.xml")
        new_cov = new_cov_data.get(module_path, 0.0)
        
        log_progress(
            session_id, 
            f"Improved coverage for {module_path} from {current_cov:.1f}% to {new_cov:.1f}%", 
            "SUCCESS"
        )
        
        if backup_path:
            delete_backup(test_file)
            
    else:
        # Failure
        logger.warning("Tests failed after changes. Reverting...")
        if backup_path:
            restore_file(test_file)
        else:
            # If we created a new file and it failed, delete it
            if os.path.exists(test_file):
                os.remove(test_file)
        
        # We still record history, but coverage hasn't changed (or we use the old one)
        # Since we reverted, coverage should be same as start.
        overall_cov = get_overall_coverage("coverage.xml")
        append_history(session_id, overall_cov, "REVERTED")
                
        log_progress(session_id, f"Tests failed for {module_path}. Reverted changes.", "REVERTED", "Tests failed after applying LLM changes.")

if __name__ == "__main__":
    main()
