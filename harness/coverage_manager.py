import xml.etree.ElementTree as ET
import json
import os
from typing import List, Dict, Optional
from harness.utils import COVERAGE_PLAN_FILE

def normalize_path(path: str) -> str:
    """Normalize path to use forward slashes."""
    return path.replace("\\", "/")

def parse_coverage_xml(xml_path: str) -> Dict[str, float]:
    """Parse coverage.xml and return a dict of {module_path: coverage_percent}."""
    if not os.path.exists(xml_path):
        return {}
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    coverage_data = {}
    
    # Iterate over packages and classes
    for package in root.findall(".//package"):
        for cls in package.findall(".//class"):
            filename = cls.get("filename")
            # Normalize path
            filename = normalize_path(filename)
            
            line_rate = float(cls.get("line-rate", 0.0))
            coverage_percent = line_rate * 100.0
            coverage_data[filename] = coverage_percent
            
    return coverage_data

def get_overall_coverage(xml_path: str) -> float:
    """Get overall coverage from coverage.xml."""
    if not os.path.exists(xml_path):
        return 0.0
    tree = ET.parse(xml_path)
    root = tree.getroot()
    return float(root.get("line-rate", 0.0)) * 100.0

def scan_source_files(root_dir: str = "target_repo/src") -> List[str]:
    """Recursively find all .py files in root_dir."""
    source_files = []
    if not os.path.exists(root_dir):
        return []
        
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Create relative path from project root
                full_path = os.path.join(root, file)
                source_files.append(normalize_path(full_path))
    return source_files

def update_coverage_plan(xml_path: str, target_coverage: float = 90.0):
    """Update coverage_plan.json based on latest XML."""
    current_data = parse_coverage_xml(xml_path)
    
    # Fallback: Scan source files to ensure everything is tracked
    # This handles the case where coverage.xml is missing or empty (no tests)
    found_files = scan_source_files()
    for f in found_files:
        # Check if file is already in current_data (handling separator differences)
        if f in current_data:
            continue
        
        # Try alternative separators
        alt_f1 = f.replace("\\", "/")
        alt_f2 = f.replace("/", "\\")
        
        if alt_f1 in current_data:
            continue
        if alt_f2 in current_data:
            continue
            
        # Not found, add with 0.0 coverage
        current_data[f] = 0.0
    
    try:
        with open(COVERAGE_PLAN_FILE, "r") as f:
            plan = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        plan = []
        
    # Convert plan to dict for easy update
    plan_dict = {item["module"]: item for item in plan}
    
    # Update existing and add new
    for module, coverage in current_data.items():
        # Filter for only source files we care about (e.g., in target_repo/src)
        if "target_repo/src" not in module and "target_repo\\src" not in module:
            continue
            
        status = "pending"
        if coverage >= target_coverage:
            status = "done"
        elif module in plan_dict and plan_dict[module]["status"] == "in_progress":
            # Keep in_progress unless done
            status = "in_progress"
            
        if module in plan_dict:
            plan_dict[module]["current_coverage"] = coverage
            if plan_dict[module]["status"] != "done": # Don't regress status from done
                plan_dict[module]["status"] = status
        else:
            plan_dict[module] = {
                "module": module,
                "current_coverage": coverage,
                "target_coverage": target_coverage,
                "status": status
            }
            
    # Write back
    new_plan = list(plan_dict.values())
    with open(COVERAGE_PLAN_FILE, "w") as f:
        json.dump(new_plan, f, indent=2)

def select_target_module() -> Optional[Dict]:
    """Select a module to work on."""
    try:
        with open(COVERAGE_PLAN_FILE, "r") as f:
            plan = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
        
    # Filter for pending or in_progress
    candidates = [m for m in plan if m["status"] in ["pending", "in_progress"]]
    
    if not candidates:
        return None
        
    # Sort by coverage ascending
    candidates.sort(key=lambda x: x["current_coverage"])
    
    return candidates[0]

def mark_module_status(module_name: str, status: str):
    """Update status of a module."""
    try:
        with open(COVERAGE_PLAN_FILE, "r") as f:
            plan = json.load(f)
    except:
        return

    for item in plan:
        if item["module"] == module_name:
            item["status"] = status
            break
            
    with open(COVERAGE_PLAN_FILE, "w") as f:
        json.dump(plan, f, indent=2)
