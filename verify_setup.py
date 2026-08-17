import os
import sys
import json

def verify():
    print("Running Verification Script for Phase 1 & 2 Setup...")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of expected files relative to root_dir
    expected_files = [
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/api/__init__.py",
        "app/api/routes.py",
        "app/api/schemas.py",
        "app/core/__init__.py",
        "app/core/prompt.py",
        "app/core/agent.py",
        "app/services/__init__.py",
        "app/services/booking_service.py",
        "app/services/memory_service.py",
        "app/services/analytics_service.py",
        "app/templates/index.html",
        "tests/test_chat.py",
        "tests/test_booking.py",
        "tests/test_analytics.py",
        ".env.example",
        ".env",
        ".gitignore",
        "requirements.txt",
        "README.md",
        "run.py"
    ]
    
    # 1. Directory Structure Status
    structure_status = {}
    all_ok = True
    for f in expected_files:
        path = os.path.join(root_dir, f)
        exists = os.path.exists(path)
        structure_status[f] = "OK" if exists else "MISSING"
        if not exists:
            all_ok = False
            
    # 2. Config File Loading Check
    sys.path.insert(0, root_dir)
    config_ok = False
    config_error = None
    settings_data = {}
    try:
        from app.config import settings
        config_ok = True
        settings_data = {
            "PROJECT_NAME": settings.PROJECT_NAME,
            "LLM_MODEL": settings.LLM_MODEL,
            "HOST": settings.HOST,
            "PORT": settings.PORT
        }
    except Exception as e:
        config_error = str(e)
        all_ok = False
        
    # 3. System Prompt Voice Compatibility Rule Check
    prompt_ok = False
    prompt_issues = []
    try:
        from app.core.prompt import get_system_prompt
        prompt = get_system_prompt()
        
        # Check for forbidden characters
        if "*" in prompt:
            prompt_issues.append("Contains asterisk '*'")
        if "#" in prompt:
            prompt_issues.append("Contains hash header '#'")
            
        # Check for line-based markdown patterns
        for idx, line in enumerate(prompt.splitlines()):
            trimmed = line.strip()
            if trimmed.startswith("- "):
                prompt_issues.append(f"Line {idx+1} starts with dash bullet point: '{trimmed}'")
            if trimmed.startswith("* "):
                prompt_issues.append(f"Line {idx+1} starts with asterisk bullet point: '{trimmed}'")
            if trimmed.startswith("1. ") or trimmed.startswith("2. ") or trimmed.startswith("3. "):
                prompt_issues.append(f"Line {idx+1} starts with numbered list item: '{trimmed}'")
                
        if not prompt_issues:
            prompt_ok = True
        else:
            all_ok = False
    except Exception as e:
        prompt_issues.append(f"Failed to load prompt: {str(e)}")
        all_ok = False

    # 4. Readiness for Phase 3
    readiness = "READY" if all_ok else "NOT READY"
    
    # Format and write MD report
    report_md = f"""# PHASE 1 & 2 AUDIT REPORT

## Directory Structure Status
{"".join([f"- `{f}`: {status}\n" for f, status in structure_status.items()])}

## Config File Loading Check
- Status: {"OK" if config_ok else "FAILED"}
- Loaded Project Name: {settings_data.get("PROJECT_NAME", "N/A")}
- Loaded LLM Model: {settings_data.get("LLM_MODEL", "N/A")}
- Host & Port: {settings_data.get("HOST", "N/A")}:{settings_data.get("PORT", "N/A")}
{f"- Error: {config_error}" if config_error else ""}

## System Prompt Voice Compatibility Rule Check
- Status: {"OK" if prompt_ok else "FAIL"}
- Markdown Symbols Found: {len(prompt_issues)}
{"".join([f"  - {issue}\n" for issue in prompt_issues]) if prompt_issues else "- Confirming zero markdown symbols in prompt text: Verified"}

## Readiness for Phase 3 (Agent Core & Booking Tools)
- Status: **{readiness}**
"""
    
    print("\n================================================================================")
    print("PHASE 1 & 2 AUDIT REPORT")
    print("================================================================================")
    print(report_md)
    print("================================================================================")
    
    # Also write report to a local markdown file for records
    with open(os.path.join(root_dir, "phase_1_2_audit_report.md"), "w") as rf:
        rf.write(report_md)
        
    if not all_ok:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    verify()
