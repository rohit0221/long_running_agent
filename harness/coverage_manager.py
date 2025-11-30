import xml.etree.ElementTree as ET
import json
import os
from typing import List, Dict, Optional
from harness.utils import COVERAGE_PLAN_FILE

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
            # Normalize path to be relative to src root if possible, or just use filename
            # Assuming filename in xml is relative to execution root or absolute
            # We want to map it to our source files. 
            # For this POC, we'll assume the filename in XML matches our project structure relative to root.
            
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

def update_coverage_plan(xml_path: str, target_coverage: float = 90.0):
    """Update coverage_plan.json based on latest XML."""
    current_data = parse_coverage_xml(xml_path)
    
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
