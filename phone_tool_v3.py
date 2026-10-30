#!/usr/bin/env python3
"""
VirgoYT OSINT Phone Recon Tool v3.0
Built for paneer by spinach.
"""

import sqlite3
import sys
import os
import time
import random
import hashlib
import subprocess
from datetime import datetime

import phonenumbers
from phonenumbers import (
    geocoder,
    carrier as pn_carrier,
    timezone as pn_timezone,
    number_type,
    PhoneNumberType,
    PhoneNumberFormat,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ANSI COLORS
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BRANDING & BANNER (YELLOW BRAILLE MASK + RED VirgoYT)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERSION = "3.0"
AUTHOR  = "VirgoYT"
MASK    = "🎭"

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
  ║  {C.R}{C.B}🎭  VirgoYT — ANONYMOUS INTELLIGENCE ENGINE  🎭{C.RST}{C.DC}         ║
  ║  {C.DR}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.DC}  ║
  ║  {C.W}AGENT    :{C.RST} {C.R}{C.B}VirgoYT{C.RST}{C.DC}                                       ║
  ║  {C.W}PROTOCOL :{C.RST} {C.Y}OSINT / CARRIER TRACE / THREAT RECON{C.RST}{C.DC}       ║
  ║  {C.W}DATABASE :{C.RST} {C.CN}ENCRYPTED EVIDENCE VAULT{C.RST}{C.DC}                      ║
  ║  {C.W}SYSTEM   :{C.RST} {C.G}● ONLINE // UNTRACEABLE{C.RST}{C.DC}                     ║
  ╚══════════════════════════════════════════════════════════╝{C.RST}
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TERMINAL HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ttype(text, speed=0.012):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def loadbar(label="PROCESSING", length=30, dur=0.6):
    print()
    for i in range(length + 1):
        pct = int((i / length) * 100)
        bar = "█" * i + "░" * (length - i)
        sys.stdout.write(f"\r  {C.R}🎭{C.RST} {C.DC}{label}{C.RST} {C.DG}[{bar}]{C.RST} {C.W}{pct}%{C.RST}")
        sys.stdout.flush()
        time.sleep(dur / length)
    print()

def sep():
    chars = "░▒▓█╌╍┄┅≋≈"
    print(f"  {C.DR}{C.D}{''.join(random.choice(chars) for _ in range(56))}{C.RST}")

def glitch_line():
    sep()

def prompt(label):
    return input(f"  {C.R}🎭{C.RST} {C.B}{C.W}{label}{C.RST} {C.DR}»{C.RST} ").strip()

def case_hash(phone):
    raw = f"{phone}-{time.time()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12].upper()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DATABASE PATH (TERMUX COMPATIBLE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _find_db_path():
    candidates = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.expanduser("~"),
        os.environ.get("HOME", ""),
        "/data/data/com.termux/files/home",
        os.getcwd(),
        "/tmp",
    ]
    for d in candidates:
        if d and os.path.isdir(d) and os.access(d, os.W_OK):
            return os.path.join(d, "virgoyt_evidence.db")
    return "virgoyt_evidence.db"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = _find_db_path()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            case_hash   TEXT,
            phone       TEXT NOT NULL,
            country     TEXT,
            region      TEXT,
            carrier     TEXT,
            line_type   TEXT,
            timezones   TEXT,
            is_valid    INTEGER,
            burner_flag INTEGER DEFAULT 0,
            risk_score  INTEGER DEFAULT 0,
            platform    TEXT,
            notes       TEXT,
            intl_fmt    TEXT,
            e164_fmt    TEXT,
            national_fmt TEXT,
            date_added  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LOOKUP TABLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LINE_TYPE_MAP = {
    PhoneNumberType.FIXED_LINE:           "Fixed Line",
    PhoneNumberType.MOBILE:               "Mobile",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed/Mobile",
    PhoneNumberType.TOLL_FREE:            "Toll-Free",
    PhoneNumberType.PREMIUM_RATE:         "Premium Rate",
    PhoneNumberType.SHARED_COST:          "Shared Cost",
    PhoneNumberType.VOIP:                 "VoIP",
    PhoneNumberType.PERSONAL_NUMBER:      "Personal",
    PhoneNumberType.PAGER:                "Pager",
    PhoneNumberType.UAN:                  "UAN",
    PhoneNumberType.UNKNOWN:              "Unknown",
}

LINE_ICONS = {
    "Fixed Line": "🏠", "Mobile": "📱", "Fixed/Mobile": "📞",
    "Toll-Free": "🆓", "Premium Rate": "💰", "Shared Cost": "🤝",
    "VoIP": "👻", "Personal": "👤", "Pager": "📟", "UAN": "📡",
    "Unknown": "❓",
}

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
    "975": "BT", "976": "NP", "977": "NP", "992": "TJ", "993": "TM",
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


def resolve_region(user_input):
    val = user_input.strip()
    if not val:
        return "IN"
    upper = val.upper()
    if len(upper) == 2 and upper.isalpha():
        return upper
    if val.isdigit() and val in DIAL_TO_REGION:
        return DIAL_TO_REGION[val]
    lower = val.lower()
    for code, name in REGION_NAMES.items():
        if lower in name.lower():
            return code
    return "IN"


def smart_number(raw, region):
    cleaned = raw.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if cleaned.startswith("+"):
        return cleaned, region

    dial_code = None
    for dc, rc in DIAL_TO_REGION.items():
        if rc == region:
            dial_code = dc
            break
    if not dial_code:
        dial_code = "91"

    if cleaned.startswith("0") and len(cleaned) > 9:
        cleaned = cleaned[1:]

    # 10 digits in India e.g. 9153705685 is a mobile number, not +91 with 8 digits
    if len(cleaned) == 10:
        cleaned = f"+{dial_code}{cleaned}"
    elif cleaned.startswith(dial_code) and len(cleaned) == (len(dial_code) + 10):
        cleaned = f"+{cleaned}"
    elif not cleaned.startswith("+"):
        if len(cleaned) <= 10:
            cleaned = f"+{dial_code}{cleaned}"
        else:
            cleaned = f"+{cleaned}"

    return cleaned, region


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  OSINT ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def compute_risk_score(result):
    score = 0
    if result["line_type"] == "VoIP":
        score += 40
    if result["line_type"] == "Unknown":
        score += 25
    if not result["is_valid"]:
        score += 30
    if result["line_type"] in ("Toll-Free", "Premium Rate"):
        score += 15
    if result["carrier"] in ("Unknown", "", None):
        score += 15
    if result["country"] in ("Unknown", "", None):
        score += 10
    return min(score, 100)


def generate_osint_formats(parsed):
    formats = {}
    formats["e164"] = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
    formats["international"] = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
    formats["national"] = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
    formats["rfc3966"] = phonenumbers.format_number(parsed, PhoneNumberFormat.RFC3966)
    raw = formats["e164"].replace("+", "")
    formats["raw_intl"] = raw

    nat_raw = formats["national"]
    for ch in "()- +":
        nat_raw = nat_raw.replace(ch, "")
    formats["raw_national"] = nat_raw

    if len(nat_raw) == 10:
        formats["dotted"] = f"{nat_raw[:3]}.{nat_raw[3:6]}.{nat_raw[6:]}"
        formats["spaced"] = f"{nat_raw[:3]} {nat_raw[3:6]} {nat_raw[6:]}"

    return formats


def generate_search_dorks(formats):
    e164 = formats.get("e164", "")
    intl = formats.get("international", "")
    raw  = formats.get("raw_intl", "")
    nat  = formats.get("raw_national", "")

    dorks = [f'"{e164}"', f'"{intl}"']
    if nat:
        dorks.append(f'"{nat}"')

    sites = [
        ("facebook.com", "Facebook"),
        ("instagram.com", "Instagram"),
        ("twitter.com", "Twitter/X"),
        ("linkedin.com", "LinkedIn"),
        ("truecaller.com", "Truecaller"),
        ("whocalledme.com", "WhoCalledMe"),
    ]
    for site, _ in sites:
        dorks.append(f'site:{site} "{e164}"')

    for ps in ["pastebin.com", "ghostbin.com", "dpaste.org"]:
        dorks.append(f'site:{ps} "{raw}"')

    dorks.append(f'"{e164}" filetype:pdf')
    dorks.append(f'"{e164}" filetype:xlsx')
    dorks.append(f'"{e164}" filetype:csv')

    return dorks


def generate_platform_links(formats):
    e164 = formats.get("e164", "")
    raw  = formats.get("raw_intl", "")
    nat  = formats.get("raw_national", "")
    links = {}

    links["WhatsApp Check"] = f"https://wa.me/{raw}"
    links["Telegram Check"] = f"https://t.me/+{raw}"
    if nat:
        links["Truecaller"] = f"https://www.truecaller.com/search/in/{nat}"
    links["Sync.me"] = f"https://sync.me/search/?number=%2B{raw}"
    links["Google Search"] = f"https://www.google.com/search?q=%22{e164}%22"
    links["NumLookup"] = f"https://www.numlookup.com/lookup?number={e164}"
    if nat:
        links["SpyDialer"] = f"https://www.spydialer.com/results.aspx?Number={nat}"
    links["Eyecon"] = "https://www.eyecon.com/"
    links["Facebook Search"] = f"https://www.facebook.com/search/top/?q={raw}"
    if raw.startswith("91"):
        links["TRAI DND Registry"] = "https://www.nccptrai.gov.in/nccpregistry/search.misc"

    return {k: v for k, v in links.items() if v}


def analyze_number(raw_number, default_region="IN"):
    processed, default_region = smart_number(raw_number, default_region)
    result = {
        "phone": raw_number,
        "phone_processed": processed,
        "is_valid": False,
        "country": "Unknown",
        "region": "Unknown",
        "carrier": "Unknown",
        "line_type": "Unknown",
        "timezones": [],
        "burner_flag": False,
        "risk_score": 0,
        "formats": {},
        "dorks": [],
        "platform_links": {},
        "e164": raw_number,
        "international": raw_number,
        "national": raw_number,
    }

    try:
        parsed = phonenumbers.parse(processed, default_region)
    except phonenumbers.NumberParseException as e:
        result["error"] = str(e)
        result["risk_score"] = 50
        return result

    result["is_valid"] = phonenumbers.is_valid_number(parsed)
    result["country_code"] = parsed.country_code
    rc = phonenumbers.region_code_for_number(parsed)
    result["region_code"] = rc if rc else "??"

    result["country"] = geocoder.description_for_number(parsed, "en") or "Unknown"
    result["region"]  = geocoder.description_for_number(parsed, "en") or "Unknown"
    result["carrier"] = pn_carrier.name_for_number(parsed, "en") or "Unknown"

    tz = pn_timezone.time_zones_for_number(parsed)
    result["timezones"] = list(tz) if tz else ["Unknown"]

    nt = number_type(parsed)
    result["line_type"] = LINE_TYPE_MAP.get(nt, "Unknown")
    if nt == PhoneNumberType.VOIP:
        result["burner_flag"] = True

    result["formats"] = generate_osint_formats(parsed)
    result["e164"]          = result["formats"].get("e164", raw_number)
    result["international"] = result["formats"].get("international", raw_number)
    result["national"]      = result["formats"].get("national", raw_number)

    result["dorks"] = generate_search_dorks(result["formats"])
    result["platform_links"] = generate_platform_links(result["formats"])
    result["risk_score"] = compute_risk_score(result)

    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DATABASE OPS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def save_evidence(analysis, platform, notes):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    ch = case_hash(analysis["e164"])
    cur.execute("""
        INSERT INTO evidence (case_hash, phone, country, region, carrier,
                              line_type, timezones, is_valid, burner_flag,
                              risk_score, platform, notes, intl_fmt, e164_fmt,
                              national_fmt, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ch,
        analysis["international"],
        analysis["country"],
        analysis.get("region_code", "??"),
        analysis["carrier"],
        analysis["line_type"],
        ", ".join(analysis["timezones"]),
        1 if analysis["is_valid"] else 0,
        1 if analysis["burner_flag"] else 0,
        analysis["risk_score"],
        platform,
        notes,
        analysis["international"],
        analysis["e164"],
        analysis["national"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    row_id = cur.lastrowid
    conn.commit()
    conn.close()
    return row_id, ch


def list_all_evidence():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM evidence ORDER BY date_added DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def search_evidence(query):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    t = f"%{query}%"
    cur.execute("""
        SELECT * FROM evidence
        WHERE phone LIKE ? OR country LIKE ? OR carrier LIKE ?
           OR platform LIKE ? OR notes LIKE ? OR case_hash LIKE ?
           OR e164_fmt LIKE ? OR national_fmt LIKE ?
        ORDER BY date_added DESC
    """, (t, t, t, t, t, t, t, t))
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_evidence(row_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM evidence WHERE id = ?", (row_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted > 0


def get_stats():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM evidence")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM evidence WHERE burner_flag = 1")
    burners = cur.fetchone()[0]
    cur.execute("SELECT AVG(risk_score) FROM evidence")
    avg_risk = cur.fetchone()[0] or 0
    cur.execute("SELECT platform, COUNT(*) as c FROM evidence GROUP BY platform ORDER BY c DESC LIMIT 5")
    top_platforms = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM evidence WHERE risk_score >= 50")
    high_risk = cur.fetchone()[0]
    conn.close()
    return {
        "total": total,
        "burners": burners,
        "avg_risk": round(avg_risk),
        "high_risk": high_risk,
        "top_platforms": top_platforms,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  AUTO UPDATE & SYNC (GITHUB HOOK)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def auto_sync_git():
    """Sync with GitHub remote and hot-restart."""
    print()
    sep()
    print(f"  {C.CN}⚡ CHECKING FOR UPDATES (GITHUB SYNC)...{C.RST}")
    sep()
    try:
        loadbar("CONNECTING TO REMOTE", 20, 0.4)
        subprocess.run(["git", "fetch", "origin"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        status = subprocess.check_output(["git", "status", "-uno"]).decode("utf-8")
        if "Your branch is behind" in status:
            print(f"\n  {C.Y}► New commits detected on GitHub remote!{C.RST}")
            loadbar("PULLING LATEST CODE", 25, 0.5)
            res = subprocess.run(["git", "pull", "--ff-only"], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"  {C.G}✅ Successfully updated to latest version!{C.RST}")
                print(f"  {C.CN}⚡ Hot-restarting VirgoYT engine...{C.RST}\n")
                time.sleep(1)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print(f"  {C.R}❌ Pull conflict detected: {res.stderr.strip()}{C.RST}\n")
        elif "Your branch is up to date" in status:
            print(f"  {C.G}✅ Toolkit is already on the latest build.{C.RST}\n")
        else:
            subprocess.run(["git", "pull"], check=True)
            print(f"  {C.G}✅ Synced successfully.{C.RST}\n")
    except FileNotFoundError:
        print(f"  {C.R}❌ Git is not installed in Termux. Run 'pkg install git'.{C.RST}\n")
    except subprocess.CalledProcessError:
        print(f"  {C.R}❌ Sync failed: Ensure remote repository is linked with 'git remote add origin ...'{C.RST}\n")
    except Exception as e:
        print(f"  {C.R}❌ Error during update: {e}{C.RST}\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DISPLAY REPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def risk_bar(score):
    filled = score // 5
    empty  = 20 - filled
    if score >= 60:
        color = C.R
        label = "HIGH"
    elif score >= 30:
        color = C.Y
        label = "MEDIUM"
    else:
        color = C.G
        label = "LOW"
    return f"{color}{'█' * filled}{'░' * empty} {score}/100 [{label}]{C.RST}"


def print_analysis(result):
    loadbar("RECON IN PROGRESS", 35, 0.7)
    valid_sym = f"{C.G}✔ VALID{C.RST}" if result["is_valid"] else f"{C.R}✘ INVALID{C.RST}"
    t_icon = LINE_ICONS.get(result["line_type"], "❓")
    rs = result["risk_score"]

    print()
    print(f"  {C.R}╔{'═'*60}╗{C.RST}")
    print(f"  {C.R}║{C.RST} {C.B}{C.W}🎭 VirgoYT OSINT — INTELLIGENCE REPORT{C.RST}                      {C.R}║{C.RST}")
    print(f"  {C.R}╠{'═'*60}╣{C.RST}")
    print(f"  {C.R}║{C.RST}                                                            {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}┌── TARGET ──────────────────────────────────────{C.RST}       {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 📱 {C.W}Input    :{C.RST} {C.Y}{result['phone']}{C.RST}")
    if result.get("phone_processed") and result["phone_processed"] != result["phone"]:
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🔄 {C.W}Auto-fix :{C.RST} {C.G}{result['phone_processed']}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 📞 {C.W}Intl     :{C.RST} {C.G}{C.B}{result['international']}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🔢 {C.W}E.164    :{C.RST} {C.CN}{result['e164']}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🏷️  {C.W}National :{C.RST} {C.CN}{result['national']}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🔑 {C.W}Status   :{C.RST} {valid_sym}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    print(f"  {C.R}║{C.RST}  {C.DC}┌── INTELLIGENCE ────────────────────────────────{C.RST}       {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🌐 {C.W}Region   :{C.RST} {C.CN}{result['country']}{C.RST}  [{C.W}{result.get('region_code','??')}{C.RST}]  +{result.get('country_code','?')}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 📡 {C.W}Carrier  :{C.RST} {C.M}{result['carrier']}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} {t_icon} {C.W}Type     :{C.RST} {C.Y}{result['line_type']}{C.RST}")
    tz_str = " | ".join(result["timezones"][:3])
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🕐 {C.W}Timezone :{C.RST} {C.D}{tz_str}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    print(f"  {C.R}║{C.RST}  {C.DC}┌── RISK ASSESSMENT ─────────────────────────────{C.RST}       {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🎯 {C.W}Score    :{C.RST} {risk_bar(rs)}")
    if result["burner_flag"]:
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} {C.R}{C.B}{C.BLK}🚨 ▓▓ BURNER DETECTED ▓▓{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} {C.R}  👻 VoIP / Virtual Number — Disposable{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} {C.R}  🔥 Likely: TextNow / GVoice / Burner App{C.RST}")
    if "error" in result:
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} {C.R}🐛 Parse Error: {result['error']}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    fmts = result.get("formats", {})
    if fmts:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── OSINT FORMATS (for searching) ───────────────{C.RST}       {C.R}║{C.RST}")
        for fname, fval in fmts.items():
            label = fname.replace("_", " ").upper()
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.D}{label:16}{C.RST} {C.CN}{fval}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    links = result.get("platform_links", {})
    if links:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── PLATFORM LOOKUP LINKS ───────────────────────{C.RST}       {C.R}║{C.RST}")
        for pname, purl in links.items():
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   🔗 {C.W}{pname:16}{C.RST} {C.D}{C.BL}{purl}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    dorks = result.get("dorks", [])
    if dorks:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── SEARCH DORKS (paste into Google) ────────────{C.RST}       {C.R}║{C.RST}")
        for d in dorks[:8]:
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.DG}▸{C.RST} {C.D}{d}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    print(f"  {C.R}║{C.RST}  {C.D}case: {case_hash(result['e164'])}  |  {MASK} VirgoYT v{VERSION}{C.RST}")
    print(f"  {C.R}╚{'═'*60}╝{C.RST}\n")


def print_evidence_table(rows):
    if not rows:
        print(f"\n  {C.R}❌ Vault empty. No records found.{C.RST}\n")
        return
    sep()
    print(f"  {C.R}{C.B}🎭 EVIDENCE VAULT — {len(rows)} RECORD(S){C.RST}")
    sep()
    print(f"  {C.DR}┌{'─'*4}┬{'─'*12}┬{'─'*20}┬{'─'*16}┬{'─'*14}┬{'─'*10}┬{'─'*10}┬{'─'*6}┬{'─'*5}┬{'─'*19}┐{C.RST}")
    print(f"  {C.DR}│{C.W}{C.B} ID {C.DR}│{C.W} CASE       {C.DR}│{C.W} PHONE              {C.DR}│{C.W} REGION         {C.DR}│{C.W} CARRIER      {C.DR}│{C.W} TYPE     {C.DR}│{C.W} PLATFORM {C.DR}│{C.W} RISK {C.DR}│{C.W}  🚨 {C.DR}│{C.W} DATE              {C.DR}│{C.RST}")
    print(f"  {C.DR}├{'─'*4}┼{'─'*12}┼{'─'*20}┼{'─'*16}┼{'─'*14}┼{'─'*10}┼{'─'*10}┼{'─'*6}┼{'─'*5}┼{'─'*19}┤{C.RST}")

    for row in rows:
        burner = f"{C.R}☠{C.RST}" if row["burner_flag"] else f"{C.D}—{C.RST}"
        rs = row["risk_score"] or 0
        rc = C.R if rs >= 60 else (C.Y if rs >= 30 else C.G)
        ch = (row["case_hash"] or "")[:10]
        plat = (row["platform"] or "—")[:8]
        print(f"  {C.DR}│{C.W}{row['id']:>3} "
              f"{C.DR}│ {C.D}{ch:<10}{C.RST} "
              f"{C.DR}│ {C.CN}{row['phone'][:18]:<18}{C.RST} "
              f"{C.DR}│ {C.W}{row['country'][:14]:<14}{C.RST} "
              f"{C.DR}│ {C.M}{row['carrier'][:12]:<12}{C.RST} "
              f"{C.DR}│ {C.Y}{row['line_type'][:8]:<8}{C.RST} "
              f"{C.DR}│ {C.W}{plat:<8}{C.RST} "
              f"{C.DR}│ {rc}{rs:>3}% {C.RST}"
              f"{C.DR}│ {burner}   "
              f"{C.DR}│ {C.D}{row['date_added'][:17]}{C.RST} {C.DR}│{C.RST}")
    print(f"  {C.DR}└{'─'*4}┴{'─'*12}┴{'─'*20}┴{'─'*16}┴{'─'*14}┴{'─'*10}┴{'─'*10}┴{'─'*6}┴{'─'*5}┴{'─'*19}┘{C.RST}\n")


def print_evidence_detail(row):
    valid_sym = f"{C.G}✔ Yes{C.RST}" if row["is_valid"] else f"{C.R}✘ No{C.RST}"
    burner_sym = f"{C.R}{C.B}🚨 YES{C.RST}" if row["burner_flag"] else f"{C.G}🛡️  No{C.RST}"
    t_icon = LINE_ICONS.get(row["line_type"], "❓")
    rs = row["risk_score"] or 0

    print()
    print(f"  {C.R}┌{'─'*55}┐{C.RST}")
    print(f"  {C.R}│{C.RST} {C.B}{C.W}🎭 EVIDENCE FILE — #{row['id']}{C.RST}")
    print(f"  {C.R}├{'─'*55}┤{C.RST}")
    print(f"  {C.R}│{C.RST} {C.D}Case Hash :{C.RST}  {C.W}{row['case_hash'] or '—'}{C.RST}")
    print(f"  {C.R}│{C.RST} 📱 {C.W}Phone    :{C.RST}  {C.G}{C.B}{row['phone']}{C.RST}")
    print(f"  {C.R}│{C.RST} 🌐 {C.W}Region   :{C.RST}  {C.CN}{row['country']}{C.RST}  [{C.W}{row['region']}{C.RST}]")
    print(f"  {C.R}│{C.RST} 📡 {C.W}Carrier  :{C.RST}  {C.M}{row['carrier']}{C.RST}")
    print(f"  {C.R}│{C.RST} {t_icon} {C.W}Type     :{C.RST}  {C.Y}{row['line_type']}{C.RST}")
    print(f"  {C.R}│{C.RST} 🔑 {C.W}Valid    :{C.RST}  {valid_sym}")
    print(f"  {C.R}│{C.RST} ☠  {C.W}Burner   :{C.RST}  {burner_sym}")
    print(f"  {C.R}│{C.RST} 🎯 {C.W}Risk     :{C.RST}  {risk_bar(rs)}")
    print(f"  {C.R}│{C.RST} 🔗 {C.W}Platform :{C.RST}  {C.W}{row['platform'] or '—'}{C.RST}")
    print(f"  {C.R}│{C.RST} 📝 {C.W}Notes    :{C.RST}  {C.D}{row['notes'] or '—'}{C.RST}")
    print(f"  {C.R}│{C.RST} 🕐 {C.W}Logged   :{C.RST}  {C.D}{row['date_added']}{C.RST}")
    print(f"  {C.R}└{'─'*55}┘{C.RST}\n")


def print_stats():
    stats = get_stats()
    print()
    print(f"  {C.R}┌{'─'*45}┐{C.RST}")
    print(f"  {C.R}│{C.RST} {C.B}{C.W}🎭 VAULT STATISTICS{C.RST}")
    print(f"  {C.R}├{'─'*45}┤{C.RST}")
    print(f"  {C.R}│{C.RST} 📊 {C.W}Total Records  :{C.RST}  {C.CN}{C.B}{stats['total']}{C.RST}")
    print(f"  {C.R}│{C.RST} 👻 {C.W}Burner Numbers :{C.RST}  {C.R}{stats['burners']}{C.RST}")
    print(f"  {C.R}│{C.RST} 🚨 {C.W}High Risk (50+):{C.RST}  {C.Y}{stats['high_risk']}{C.RST}")
    print(f"  {C.R}│{C.RST} 🎯 {C.W}Avg Risk Score :{C.RST}  {risk_bar(stats['avg_risk'])}")
    print(f"  {C.R}└{'─'*45}┘{C.RST}\n")


def export_to_csv():
    import csv
    rows = list_all_evidence()
    if not rows:
        print(f"\n  {C.R}❌ No entries to export.{C.RST}\n")
        return

    filename = f"virgoyt_evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(SCRIPT_DIR, filename)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Case Hash", "Phone", "E164", "National",
                         "Country", "Region", "Carrier", "Line Type", "Timezones",
                         "Valid", "Burner", "Risk Score", "Platform", "Notes", "Date"])
        for row in rows:
            writer.writerow([
                row["id"], row["case_hash"], row["phone"],
                row.get("e164_fmt", ""), row.get("national_fmt", ""),
                row["country"], row["region"], row["carrier"],
                row["line_type"], row.get("timezones", ""),
                row["is_valid"], row["burner_flag"], row["risk_score"],
                row["platform"], row["notes"], row["date_added"]
            ])

    loadbar("EXPORTING", 20, 0.4)
    print(f"  {C.G}✅ Exported {len(rows)} records → {C.B}{filename}{C.RST}")
    print(f"  {C.D}{C.DC}  📁 {filepath}{C.RST}\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MENU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def show_menu():
    print()
    print(f"  {C.DR}╔{'═'*54}╗{C.RST}")
    print(f"  {C.DR}║{C.RST} {C.B}{C.W}🎭 VirgoYT — COMMAND CENTER{C.RST}                            {C.DR}║{C.RST}")
    print(f"  {C.DR}╠{'═'*54}╣{C.RST}")
    print(f"  {C.DR}║{C.RST}                                                      {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}1{C.R}]{C.RST} 🔍 {C.W}Analyze Number (Full OSINT Recon){C.RST}           {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}2{C.R}]{C.RST} 💾 {C.W}Analyze + Save to Evidence Vault{C.RST}            {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}3{C.R}]{C.RST} 📊 {C.W}List All Evidence{C.RST}                          {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}4{C.R}]{C.RST} 🔍 {C.W}Search Evidence{C.RST}                            {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}5{C.R}]{C.RST} 👁️  {C.W}View Entry Detail{C.RST}                          {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}6{C.R}]{C.RST} 🗑️  {C.W}Delete Entry{C.RST}                               {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}7{C.R}]{C.RST} 📤 {C.W}Export to CSV{C.RST}                              {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}8{C.R}]{C.RST} 📊 {C.W}Vault Statistics{C.RST}                           {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}9{C.R}]{C.RST} 🔄 {C.W}Sync & Update from GitHub (Hot-Restart){C.RST}     {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}0{C.R}]{C.RST} ⚡ {C.R}Exit{C.RST}                                       {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}                                                      {C.DR}║{C.RST}")
    print(f"  {C.DR}╚{'═'*54}╝{C.RST}")


def boot():
    os.system("clear 2>/dev/null || cls 2>/dev/null || true")
    print(BANNER)
    time.sleep(0.1)
    msgs = [
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}Engine loaded{C.RST}",
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}Carrier attribution database mounted{C.RST}",
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}OSINT dork engine armed{C.RST}",
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}VoIP / burner detector active{C.RST}",
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}Evidence vault connected @ {DB_FILE}{C.RST}",
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}Auto-sync GitHub engine online{C.RST}",
    ]
    for m in msgs:
        ttype(m, speed=0.005)
        time.sleep(0.04)

    print()
    ttype(f"  {C.R}{C.B}🎭 VirgoYT OSINT TOOLKIT — READY ⚡{C.RST}", speed=0.01)
    sep()


def shutdown():
    print()
    sep()
    ttype(f"  {C.R}⚡ SHUTTING DOWN...{C.RST}", speed=0.02)
    print(f"""
  {C.DR}╔{'═'*44}╗
  ║   {C.R}{C.B}🎭 VirgoYT — CONNECTION TERMINATED 🎭{C.RST}{C.DR}     ║
  ║   {C.D}{C.DC}stay dangerous.{C.RST}{C.DR}                              ║
  ╚{'═'*44}╝{C.RST}
""")
    sys.exit(0)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    init_db()
    boot()

    while True:
        show_menu()
        choice = prompt("SELECT")

        if choice == "1":
            raw = prompt("📱 TARGET NUMBER")
            if not raw:
                print(f"  {C.R}❌ No number.{C.RST}"); continue
            region_in = prompt("🌐 REGION (IN/US/91/44 or country name) [IN]") or "IN"
            region = resolve_region(region_in)
            rname = REGION_NAMES.get(region, region)
            print(f"  {C.D}  ► Region resolved: {region} ({rname}){C.RST}")
            result = analyze_number(raw, region)
            print_analysis(result)

        elif choice == "2":
            raw = prompt("📱 TARGET NUMBER")
            if not raw:
                print(f"  {C.R}❌ No number.{C.RST}"); continue
            region_in = prompt("🌐 REGION (IN/US/91/44 or country name) [IN]") or "IN"
            region = resolve_region(region_in)
            rname = REGION_NAMES.get(region, region)
            print(f"  {C.D}  ► Region resolved: {region} ({rname}){C.RST}")
            result = analyze_number(raw, region)
            print_analysis(result)
            platform = prompt("🔗 PLATFORM (WhatsApp/SMS/Telegram/Call)")
            notes    = prompt("📝 NOTES")
            loadbar("LOGGING EVIDENCE", 25, 0.4)
            row_id, ch = save_evidence(result, platform, notes)
            print(f"  {C.G}✅ {C.B}Evidence #{row_id} logged{C.RST}")
            print(f"  {C.D}  Case: {ch}  |  {MASK} VirgoYT{C.RST}\n")

        elif choice == "3":
            loadbar("DECRYPTING VAULT", 20, 0.3)
            rows = list_all_evidence()
            print_evidence_table(rows)

        elif choice == "4":
            q = prompt("🔍 SEARCH")
            if not q:
                print(f"  {C.R}❌ No query.{C.RST}"); continue
            loadbar("SCANNING", 20, 0.3)
            rows = search_evidence(q)
            print_evidence_table(rows)

        elif choice == "5":
            id_str = prompt("👁️  RECORD ID")
            if not id_str.isdigit():
                print(f"  {C.R}❌ Invalid ID.{C.RST}"); continue
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM evidence WHERE id = ?", (int(id_str),))
            row = cur.fetchone()
            conn.close()
            if row:
                print_evidence_detail(row)
            else:
                print(f"  {C.R}❌ Not found.{C.RST}")

        elif choice == "6":
            id_str = prompt("🗑️  DELETE RECORD ID")
            if not id_str.isdigit():
                print(f"  {C.R}❌ Invalid.{C.RST}"); continue
            confirm = prompt(f"⚠️  DESTROY #{id_str}? (y/n)")
            if confirm.lower() == "y":
                loadbar("SHREDDING", 15, 0.3)
                if delete_evidence(int(id_str)):
                    print(f"  {C.G}✅ Record #{id_str} destroyed.{C.RST}\n")
                else:
                    print(f"  {C.R}❌ Not found.{C.RST}\n")

        elif choice == "7":
            export_to_csv()

        elif choice == "8":
            print_stats()

        elif choice == "9":
            auto_sync_git()

        elif choice == "0":
            shutdown()

        else:
            print(f"  {C.R}❌ Invalid. Enter 0-9.{C.RST}")


if __name__ == "__main__":
    main()
