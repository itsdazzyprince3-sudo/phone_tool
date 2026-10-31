"""
config.py — Configuration, Branding, ANSI Colors & Path Management
VirgoYT OSINT Toolkit v4.0
Developer Credit: VIRGOYT707
"""

import os
import sys
import time
import random
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PROJECT METADATA & BRANDING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERSION = "4.0.0"
AUTHOR = "VIRGOYT707"
PROJECT_NAME = "VirgoYT OSINT Toolkit"
MASK = "🎭"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PATHS (TERMUX COMPATIBLE VIA PATHLIB)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BASE_DIR = Path(__file__).resolve().parent.parent

def get_writable_base_dir() -> Path:
    """Find a guaranteed writable directory for evidence DB and exports."""
    candidates = [
        BASE_DIR,
        Path.home() / "phone_tool",
        Path.home(),
        Path(os.environ.get("HOME", "/data/data/com.termux/files/home")),
        Path("/data/data/com.termux/files/home"),
        Path("/tmp"),
    ]
    for c in candidates:
        try:
            if c.exists() and os.access(str(c), os.W_OK):
                return c
        except Exception:
            continue
    return BASE_DIR

APP_DIR = get_writable_base_dir()
DB_FILE = APP_DIR / "virgoyt_evidence.db"
BACKUP_DIR = APP_DIR / "backups"
EXPORT_DIR = APP_DIR / "exports"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ANSI COLOR SYSTEM (Termux 16/256-color friendly)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class C:
    RST = "\033[0m"
    B   = "\033[1m"
    D   = "\033[2m"
    BLK = "\033[5m"

    R   = "\033[91m"
    G   = "\033[92m"
    Y   = "\033[93m"
    BL  = "\033[94m"
    M   = "\033[95m"
    CN  = "\033[96m"
    W   = "\033[97m"

    DR  = "\033[31m"
    DG  = "\033[32m"
    DY  = "\033[33m"
    DC  = "\033[36m"
    DW  = "\033[37m"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ASCII ART & BRANDING BANNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BANNER = f"""{C.Y}{C.B}
              ⣀⣀⣀⣀⣠⣤⣤⣄⣀⣀⣀⣀
       ⢀⣠⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣄⡀
       ⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷
       ⣿⣿⣿⡿⠛⠉⠉⠙⠿⣿⣿⣿⣿⠿⠋⠉⠉⠛⢿⣿⣿⣿
       ⣿⣿⣿⣶⣿⣿⣿⣦⠀⢘⣿⣿⡃⠀⣴⣿⣿⣿⣶⣿⣿⣿
       ⣿⣿⣿⣏⠉⠀⠈⣙⣿⣿⣿⣿⣿⣿⣋⠁⠀⠉⣹⣿⣿⣿
       ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
       ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
       ⢸⣿⣿⣎⠻⣿⣿⣿⣿⡿⠋⠙⢿⣿⣿⣿⣿⠟⣱⣿⣿⡇
       ⠀⢿⣿⣿⣧⠀⠉⠉⠉⠀⢀⡀⠀⠉⠉⠉⠀⣼⣿⣿⡿⠀
       ⠀⠈⢻⣿⣿⣷⣶⣶⣶⣶⣿⣿⣶⣶⣶⣶⣾⣿⣿⡟⠁
       ⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⠉⠉⣿⣿⣿⣿⣿⣿⠏
       ⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⠀⠀⣿⣿⣿⣿⠟⠁
       ⠀⠀⠀⠀⠀⠀⠀⠙⠻⢿⣦⣴⡿⠟⠋
{C.R}
 ██╗   ██╗██╗██████╗  ██████╗  ██████╗ ██╗   ██╗████████╗
 ██║   ██║██║██╔══██╗██╔════╝ ██╔═══██╗╚██╗ ██╔╝╚══██╔══╝
 ██║   ██║██║██████╔╝██║  ███╗██║   ██║ ╚████╔╝    ██║   
 ╚██╗ ██╔╝██║██╔══██╗██║   ██║██║   ██║  ╚██╔╝     ██║   
  ╚████╔╝ ██║██║  ██║╚██████╔╝╚██████╔╝   ██║      ██║   
   ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝      ╚═╝{C.RST}
{C.DC}
  ╔══════════════════════════════════════════════════════════╗
  ║  {C.R}{C.B}🎭  VirgoYT — PRIVACY-FOCUSED OSINT ENGINE  🎭{C.RST}{C.DC}         ║
  ║  {C.DR}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.DC}  ║
  ║  {C.W}DEVELOPER:{C.RST} {C.R}{C.B}{AUTHOR}{C.RST}{C.DC}                                      ║
  ║  {C.W}VERSION  :{C.RST} {C.Y}v{VERSION} [ARCHITECT BUILD]{C.RST}{C.DC}                   ║
  ║  {C.W}STORAGE  :{C.RST} {C.CN}LOCAL EVIDENCE VAULT (SQLITE){C.RST}{C.DC}                 ║
  ║  {C.W}STATUS   :{C.RST} {C.G}● ONLINE // PRIVACY-FOCUSED{C.RST}{C.DC}                     ║
  ╚══════════════════════════════════════════════════════════╝{C.RST}
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DIAL CODES & REGION LOOKUPS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIAL_TO_REGION = {
    "1": "US", "7": "RU", "20": "EG", "27": "ZA", "30": "GR",
    "31": "NL", "32": "BE", "33": "FR", "34": "ES", "36": "HU",
    "39": "IT", "40": "RO", "41": "CH", "43": "AT", "44": "GB",
    "45": "DK", "46": "SE", "47": "NO", "48": "PL", "49": "DE",
    "51": "PE", "52": "MX", "53": "CU", "54": "AR", "55": "BR",
    "56": "CL", "57": "CO", "58": "VE", "60": "MY", "61": "AU",
    "62": "ID", "63": "PH", "64": "NZ", "65": "SG", "66": "TH",
    "81": "JP", "82": "KR", "84": "VN", "86": "CN", "90": "TR",
    "91": "IN", "92": "PK", "93": "AF", "94": "LK", "95": "MM",
    "98": "IR", "212": "MA", "213": "DZ", "216": "TN", "218": "LY",
    "220": "GM", "221": "SN", "234": "NG", "249": "SD", "251": "ET",
    "254": "KE", "255": "TZ", "256": "UG", "260": "ZM", "263": "ZW",
    "880": "BD", "886": "TW", "960": "MV", "961": "LB", "962": "JO",
    "963": "SY", "964": "IQ", "965": "KW", "966": "SA", "967": "YE",
    "968": "OM", "971": "AE", "972": "IL", "973": "BH", "974": "QA",
    "975": "BT", "976": "MN", "977": "NP", "992": "TJ", "993": "TM",
    "994": "AZ", "995": "GE", "996": "KG", "998": "UZ",
}

REGION_NAMES = {
    "IN": "India", "US": "United States", "GB": "United Kingdom",
    "PK": "Pakistan", "BD": "Bangladesh", "AE": "UAE", "SA": "Saudi Arabia",
    "AU": "Australia", "CA": "Canada", "DE": "Germany", "FR": "France",
    "JP": "Japan", "CN": "China", "BR": "Brazil", "RU": "Russia",
    "NG": "Nigeria", "KE": "Kenya", "ZA": "South Africa", "MX": "Mexico",
    "PH": "Philippines", "ID": "Indonesia", "MY": "Malaysia", "SG": "Singapore",
    "TR": "Turkey", "EG": "Egypt", "TH": "Thailand", "VN": "Vietnam",
    "KR": "South Korea", "IT": "Italy", "ES": "Spain", "NL": "Netherlands",
    "NP": "Nepal", "LK": "Sri Lanka", "AF": "Afghanistan", "IR": "Iran",
    "IQ": "Iraq", "QA": "Qatar", "KW": "Kuwait", "OM": "Oman",
    "BH": "Bahrain", "JO": "Jordan",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TERMINAL INTERFACE HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ttype(text: str, speed: float = 0.012) -> None:
    """Print text with typewriter pacing for cyber-analyst UX."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def loadbar(label: str = "PROCESSING", length: int = 26, dur: float = 0.4) -> None:
    """Render an animated progress bar."""
    print()
    step = max(0.005, dur / max(1, length))
    for i in range(length + 1):
        pct = int((i / length) * 100)
        bar = "█" * i + "░" * (length - i)
        sys.stdout.write(f"\r  {C.R}🎭{C.RST} {C.DC}{label:<20}{C.RST} {C.DG}[{bar}]{C.RST} {C.W}{pct:>3}%{C.RST}")
        sys.stdout.flush()
        time.sleep(step)
    print()

def sep(length: int = 58) -> None:
    """Print a clean glitch-accented separator line."""
    chars = "─━┄┅╌╍"
    line = "".join(random.choice(chars) for _ in range(length))
    print(f"  {C.DR}{C.D}{line}{C.RST}")

def glitch_line() -> None:
    sep()

def prompt(label: str) -> str:
    """Formatted input prompt with VirgoYT signature."""
    try:
        return input(f"  {C.R}🎭{C.RST} {C.B}{C.W}{label}{C.RST} {C.DR}»{C.RST} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""
