"""
git_sync.py — Safe GitHub Synchronization & Security Audit Engine
VirgoYT OSINT Toolkit v4.0
Developer Credit: VIRGOYT707
"""

import subprocess
import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

from .config import BASE_DIR, C, loadbar, sep

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SENSITIVE DATA GUARD LISTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SENSITIVE_PATTERNS = [
    r"\.db$", r"\.sqlite$", r"\.sqlite3$",
    r"\.csv$", r"\.tsv$",
    r"\.env$", r"token", r"key", r"credential",
    r"id_rsa", r"id_ed25519", r"\.bak$",
    r"^backups/", r"^exports/",
]

REQUIRED_GITIGNORE_RULES = [
    "*.db",
    "*.sqlite3",
    "*.sqlite",
    "*.csv",
    "*.bak",
    ".env",
    "backups/",
    "exports/",
    "__pycache__/",
    "*.py[cod]",
    ".venv/",
]

def ensure_gitignore_safety(repo_dir: Path = BASE_DIR) -> List[str]:
    """
    Audit .gitignore and append any missing protection patterns
    to guarantee databases and exports are never committed.
    """
    gi_path = repo_dir / ".gitignore"
    existing_content = ""
    if gi_path.exists():
        existing_content = gi_path.read_text(encoding="utf-8", errors="ignore")

    existing_lines = {line.strip() for line in existing_content.splitlines() if line.strip()}
    added_rules: List[str] = []

    for rule in REQUIRED_GITIGNORE_RULES:
        if rule not in existing_lines:
            added_rules.append(rule)

    if added_rules:
        with open(gi_path, "a", encoding="utf-8") as f:
            if not existing_content.endswith("\n") and existing_content:
                f.write("\n")
            f.write("# VirgoYT v4.0 Automated Data Protection Rules\n")
            for r in added_rules:
                f.write(f"{r}\n")

    return added_rules

def get_remote_info(repo_dir: Path = BASE_DIR) -> Dict[str, str]:
    """Retrieve current Git remote origin URL and active branch."""
    info = {"remote_url": "NOT CONFIGURED", "branch": "unknown"}
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_dir), "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, timeout=3
        )
        if r.returncode == 0 and r.stdout.strip():
            info["remote_url"] = r.stdout.strip()

        b = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=3
        )
        if b.returncode == 0 and b.stdout.strip():
            info["branch"] = b.stdout.strip()
    except Exception:
        pass
    return info

def audit_sync_safety(repo_dir: Path = BASE_DIR) -> Dict[str, Any]:
    """
    Inspect pending changes and verify no sensitive files (databases,
    tokens, exports) are staged or eligible for synchronization.
    """
    ensure_gitignore_safety(repo_dir)

    report: Dict[str, Any] = {
        "is_git_repo": False,
        "is_safe": True,
        "staged": [],
        "unstaged": [],
        "untracked": [],
        "sensitive_violations": [],
        "remote_info": get_remote_info(repo_dir),
    }

    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        return report
    report["is_git_repo"] = True

    try:
        res = subprocess.run(
            ["git", "-C", str(repo_dir), "status", "--porcelain"],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode != 0:
            return report

        for line in res.stdout.splitlines():
            if len(line) < 4:
                continue
            index_status = line[0]
            work_status = line[1]
            filepath = line[3:].strip()

            # Check against sensitive regex patterns
            is_sensitive = False
            for pat in SENSITIVE_PATTERNS:
                if re.search(pat, filepath, re.IGNORECASE):
                    is_sensitive = True
                    break

            if is_sensitive:
                report["sensitive_violations"].append(filepath)
                report["is_safe"] = False

            if index_status in ("M", "A", "R", "C"):
                report["staged"].append(filepath)
            elif work_status in ("M", "D"):
                report["unstaged"].append(filepath)
            elif index_status == "?" and work_status == "?":
                report["untracked"].append(filepath)

    except Exception as e:
        report["is_safe"] = False
        report["error"] = str(e)

    return report

def safe_git_pull(repo_dir: Path = BASE_DIR) -> Tuple[bool, str]:
    """
    Safely pull updates from the remote repository.
    Verifies working tree safety before fast-forward pulling.
    """
    audit = audit_sync_safety(repo_dir)
    if not audit["is_git_repo"]:
        return False, "Not a valid Git repository."

    if not audit["is_safe"]:
        return False, f"Sync blocked: Sensitive files detected ({', '.join(audit['sensitive_violations'])})"

    try:
        loadbar("VERIFYING REMOTE", 20, 0.3)
        fetch_res = subprocess.run(
            ["git", "-C", str(repo_dir), "fetch", "origin"],
            capture_output=True, text=True, timeout=12
        )
        if fetch_res.returncode != 0:
            return False, f"Remote fetch failed: {fetch_res.stderr.strip()}"

        status_res = subprocess.run(
            ["git", "-C", str(repo_dir), "status", "-uno"],
            capture_output=True, text=True, timeout=5
        )
        status_txt = status_res.stdout

        if "Your branch is behind" in status_txt:
            print(f"\n  {C.Y}► Remote repository contains newer commits.{C.RST}")
            loadbar("APPLYING UPDATES", 20, 0.4)
            pull_res = subprocess.run(
                ["git", "-C", str(repo_dir), "pull", "--ff-only"],
                capture_output=True, text=True, timeout=15
            )
            if pull_res.returncode == 0:
                return True, "Toolkit updated successfully."
            else:
                return False, f"Pull failed (fast-forward conflict): {pull_res.stderr.strip()}"
        elif "Your branch is up to date" in status_txt:
            return True, "Toolkit is already running the latest remote version."
        else:
            return True, "Local branch is synchronized with remote."

    except subprocess.TimeoutExpired:
        return False, "Git operation timed out. Verify network connection."
    except Exception as e:
        return False, f"Git error: {e}"

def safe_git_push(commit_msg: str, repo_dir: Path = BASE_DIR) -> Tuple[bool, str]:
    """
    Safely stage non-sensitive files, commit, and push to remote.
    Strictly verifies .gitignore and blocks any evidence/database leak.
    """
    audit = audit_sync_safety(repo_dir)
    if not audit["is_git_repo"]:
        return False, "Directory is not a Git repository."

    if not audit["is_safe"]:
        return False, f"ABORTED: Sensitive files ({', '.join(audit['sensitive_violations'])}) must not be pushed."

    try:
        # Stage only tracked files and safe new source files
        subprocess.run(["git", "-C", str(repo_dir), "add", "-A"], check=True, timeout=5)

        # Re-check after staging to ensure no sensitive files were added
        post_audit = audit_sync_safety(repo_dir)
        if not post_audit["is_safe"]:
            subprocess.run(["git", "-C", str(repo_dir), "reset"], check=True, timeout=5)
            return False, f"SAFETY ABORT: Sensitive files staged ({', '.join(post_audit['sensitive_violations'])})"

        # Commit
        c_res = subprocess.run(
            ["git", "-C", str(repo_dir), "commit", "-m", commit_msg],
            capture_output=True, text=True, timeout=8
        )
        if c_res.returncode != 0 and "nothing to commit" not in c_res.stdout:
            return False, f"Commit failed: {c_res.stderr.strip()}"

        # Push
        loadbar("PUSHING TO REMOTE", 24, 0.5)
        p_res = subprocess.run(
            ["git", "-C", str(repo_dir), "push", "origin", "HEAD"],
            capture_output=True, text=True, timeout=20
        )
        if p_res.returncode == 0:
            return True, "Successfully synchronized with GitHub remote."
        else:
            # Sanitize stderr to prevent accidental token exposure
            clean_err = re.sub(r"://[^@]+@", "://***@", p_res.stderr.strip())
            return False, f"Push failed: {clean_err}"

    except Exception as e:
        return False, f"Sync exception: {e}"
