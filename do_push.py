import sys
from pathlib import Path
BASE_DIR = Path("/data/data/com.termux/files/home/phone_tool")
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from virgoyt.git_sync import safe_git_push

ok, msg = safe_git_push("Upgrade to VirgoYT v5.0.0 — Full-Spectrum OSINT & SpiderFoot Engine", repo_dir=BASE_DIR)
print(f"RESULT: {ok} | {msg}")
