"""
analyzer.py — Phone Number Analysis Engine using libphonenumber
VirgoYT OSINT Toolkit v4.0
Developer Credit: VIRGOYT707
"""

from typing import Dict, Any, Tuple, List
import phonenumbers
from phonenumbers import (
    geocoder,
    carrier as pn_carrier,
    timezone as pn_timezone,
    number_type,
    PhoneNumberType,
    PhoneNumberFormat,
    ValidationResult,
)

from .config import DIAL_TO_REGION, REGION_NAMES

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NUMBER TYPE MAPPINGS & DESCRIPTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LINE_TYPE_MAP = {
    PhoneNumberType.FIXED_LINE:           "Fixed Line",
    PhoneNumberType.MOBILE:               "Mobile",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line / Mobile",
    PhoneNumberType.TOLL_FREE:            "Toll-Free",
    PhoneNumberType.PREMIUM_RATE:         "Premium Rate",
    PhoneNumberType.SHARED_COST:          "Shared Cost",
    PhoneNumberType.VOIP:                 "VoIP / Virtual",
    PhoneNumberType.PERSONAL_NUMBER:      "Personal Number",
    PhoneNumberType.PAGER:                "Pager",
    PhoneNumberType.UAN:                  "Universal Access (UAN)",
    PhoneNumberType.VOICEMAIL:            "Voicemail Access",
    PhoneNumberType.UNKNOWN:              "Unknown Line Type",
}

LINE_ICONS = {
    "Fixed Line": "🏠",
    "Mobile": "📱",
    "Fixed Line / Mobile": "📞",
    "Toll-Free": "🆓",
    "Premium Rate": "💰",
    "Shared Cost": "🤝",
    "VoIP / Virtual": "👻",
    "Personal Number": "👤",
    "Pager": "📟",
    "Universal Access (UAN)": "📡",
    "Voicemail Access": "📬",
    "Unknown Line Type": "❓",
}

POSSIBILITY_REASONS = {
    ValidationResult.IS_POSSIBLE: "Possible according to numbering plan length and leading digits.",
    ValidationResult.IS_POSSIBLE_LOCAL_ONLY: "Possible for local dialling only (missing prefix for trunk/international).",
    ValidationResult.INVALID_COUNTRY_CODE: "Country calling code is unassigned or invalid.",
    ValidationResult.TOO_SHORT: "Number has fewer digits than minimum for this numbering plan.",
    ValidationResult.TOO_LONG: "Number has more digits than maximum allowed by ITU-T E.164.",
    ValidationResult.INVALID_LENGTH: "Number length does not match any valid pattern for this region.",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  INPUT NORMALIZATION & REGION RESOLUTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def resolve_region(user_input: str) -> str:
    """
    Resolve user input (2-letter ISO, dial code, or country name) to a 2-letter ISO code.
    Defaults to 'IN' (India).
    """
    val = (user_input or "").strip()
    if not val:
        return "IN"

    upper = val.upper()
    if len(upper) == 2 and upper.isalpha():
        return upper

    # Numeric dial code (e.g., '91', '1', '44')
    digits = "".join(ch for ch in val if ch.isdigit())
    if digits in DIAL_TO_REGION:
        return DIAL_TO_REGION[digits]

    # Search by country name substring
    lower = val.lower()
    for code, name in REGION_NAMES.items():
        if lower in name.lower():
            return code

    return "IN"

def smart_number(raw: str, region: str) -> Tuple[str, str]:
    """
    Normalize raw user input without corrupting national formats.
    Auto-detects dial code prefixes and formats clean E.164 candidate strings.
    """
    cleaned = raw.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")
    if cleaned.startswith("+"):
        return cleaned, region

    # Find dial code corresponding to region
    dial_code = None
    for dc, rc in DIAL_TO_REGION.items():
        if rc == region:
            dial_code = dc
            break
    if not dial_code:
        dial_code = "91" if region == "IN" else "1"

    # Strip single leading trunk zero (e.g. 09153705685 -> 9153705685)
    if cleaned.startswith("0") and len(cleaned) > 8:
        cleaned = cleaned[1:]

    # Handle standard 10-digit national numbers
    if len(cleaned) == 10:
        cleaned = f"+{dial_code}{cleaned}"
    elif cleaned.startswith(dial_code) and len(cleaned) == (len(dial_code) + 10):
        cleaned = f"+{cleaned}"
    elif not cleaned.startswith("+"):
        cleaned = f"+{dial_code}{cleaned}" if len(cleaned) <= 10 else f"+{cleaned}"

    return cleaned, region

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FORMAT GENERATION FOR OSINT CORRELATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_osint_formats(parsed: phonenumbers.PhoneNumber) -> Dict[str, str]:
    """
    Produce standard numbering representations for database searches,
    breach lookups, and OSINT index querying.
    """
    formats: Dict[str, str] = {}
    try:
        formats["e164"] = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
    except Exception:
        formats["e164"] = ""

    try:
        formats["international"] = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
    except Exception:
        formats["international"] = ""

    try:
        formats["national"] = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
    except Exception:
        formats["national"] = ""

    try:
        formats["rfc3966"] = phonenumbers.format_number(parsed, PhoneNumberFormat.RFC3966)
    except Exception:
        formats["rfc3966"] = ""

    # Raw digits (no symbols)
    raw_intl = formats["e164"].replace("+", "")
    formats["raw_intl"] = raw_intl

    nat_raw = "".join(ch for ch in formats["national"] if ch.isdigit())
    formats["raw_national"] = nat_raw

    # Punctuation variants (useful in forum dumps and pasted lists)
    if len(nat_raw) == 10:
        formats["dotted"] = f"{nat_raw[:3]}.{nat_raw[3:6]}.{nat_raw[6:]}"
        formats["spaced"] = f"{nat_raw[:3]} {nat_raw[3:6]} {nat_raw[6:]}"
    elif len(nat_raw) > 6:
        part = len(nat_raw) // 3
        formats["dotted"] = f"{nat_raw[:part]}.{nat_raw[part:2*part]}.{nat_raw[2*part:]}"
        formats["spaced"] = f"{nat_raw[:part]} {nat_raw[part:2*part]} {nat_raw[2*part:]}"
    else:
        formats["dotted"] = nat_raw
        formats["spaced"] = nat_raw

    return formats

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SEARCH ENGINE DORKS & PLATFORM SHORTCUTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_search_dorks(formats: Dict[str, str]) -> List[str]:
    """
    Generate legitimate, public search engine queries to discover public footprints.
    No scraping; formatted for standard search engine input.
    """
    e164 = formats.get("e164", "")
    intl = formats.get("international", "")
    raw_intl = formats.get("raw_intl", "")
    nat_raw = formats.get("raw_national", "")

    dorks: List[str] = []
    if e164:
        dorks.append(f'"{e164}"')
    if intl and intl != e164:
        dorks.append(f'"{intl}"')
    if nat_raw and nat_raw != e164:
        dorks.append(f'"{nat_raw}"')

    # Public social and business directories (Google indexing checks)
    for site in ["linkedin.com", "facebook.com", "instagram.com", "twitter.com"]:
        if e164:
            dorks.append(f'site:{site} "{e164}"')

    # Public document indexing (inadvertently exposed contact sheets / lists)
    if e164:
        dorks.append(f'"{e164}" filetype:pdf')
        dorks.append(f'"{e164}" filetype:xlsx')

    # Text paste indexes
    if raw_intl:
        dorks.append(f'site:pastebin.com "{raw_intl}"')

    return dorks

def generate_platform_links(formats: Dict[str, str]) -> Dict[str, str]:
    """
    Generate verifiable direct public lookup shortcuts.
    All lookups are user-initiated in an external browser.
    """
    e164 = formats.get("e164", "")
    raw_intl = formats.get("raw_intl", "")
    nat_raw = formats.get("raw_national", "")
    links: Dict[str, str] = {}

    if raw_intl:
        links["WhatsApp Direct"] = f"https://wa.me/{raw_intl}"
        links["Telegram Direct"] = f"https://t.me/+{raw_intl}"
        links["Sync.me Lookup"] = f"https://sync.me/search/?number=%2B{raw_intl}"

    if e164:
        links["Google Search"] = f"https://www.google.com/search?q=%22{e164}%22"
        links["NumLookup (Public)"] = f"https://www.numlookup.com/lookup?number={e164}"
        links["Whoscall Search"] = f"https://whoscall.com/search?phone={e164}"

    if nat_raw:
        links["Truecaller Web"] = f"https://www.truecaller.com/search/in/{nat_raw}"
        links["SpyDialer (US)"] = f"https://www.spydialer.com/results.aspx?Number={nat_raw}"

    if raw_intl.startswith("91"):
        links["TRAI DND Registry (India)"] = "https://www.nccptrai.gov.in/nccpregistry/search.misc"

    return links

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CORE ANALYSIS FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_number(raw_number: str, default_region: str = "IN") -> Dict[str, Any]:
    """
    Comprehensive phone number analysis using Google's libphonenumber.
    Extracts numbering-plan compliance, metadata, timezones, and OSINT variations.
    Enforces strict truthfulness constraints regarding live status and tracking.
    """
    resolved_region = resolve_region(default_region)
    processed, resolved_region = smart_number(raw_number, resolved_region)

    result: Dict[str, Any] = {
        "phone_input": raw_number,
        "phone_processed": processed,
        "default_region": resolved_region,
        "is_valid": False,
        "is_possible": False,
        "possibility_reason": "Not evaluated",
        "country_code": None,
        "region_code": "??",
        "country_name": "UNKNOWN",
        "carrier": "UNKNOWN",
        "line_type": "Unknown Line Type",
        "line_icon": "❓",
        "is_voip": False,
        "timezones": [],
        "formats": {},
        "dorks": [],
        "platform_links": {},
        "e164": processed,
        "international": processed,
        "national": processed,
        "error": None,
        "data_source": "ITU-T E.164 / Google libphonenumber metadata database",
        "disclaimers": [
            "Valid format does NOT guarantee the number is actively assigned or in service.",
            "Carrier metadata indicates original block allocation, NOT live ported MNP network operator.",
            "Timezone indicates geographic numbering area, NOT current device or GPS location.",
            "Real-time interception or live subscriber tracking is technically impossible via phone metadata.",
        ],
    }

    try:
        parsed = phonenumbers.parse(processed, resolved_region)
    except phonenumbers.NumberParseException as e:
        result["error"] = str(e)
        result["possibility_reason"] = f"Parse failure: {e}"
        return result
    except Exception as e:
        result["error"] = f"Unexpected parse error: {e}"
        return result

    # Validation & Possibility
    result["is_valid"] = phonenumbers.is_valid_number(parsed)
    result["is_possible"] = phonenumbers.is_possible_number(parsed)

    reason_enum = phonenumbers.is_possible_number_with_reason(parsed)
    result["possibility_reason"] = POSSIBILITY_REASONS.get(
        reason_enum, f"Validation code: {reason_enum}"
    )

    result["country_code"] = parsed.country_code
    rc = phonenumbers.region_code_for_number(parsed)
    result["region_code"] = rc if rc else "??"

    # Geographic and Telecom Metadata
    c_name = geocoder.description_for_number(parsed, "en")
    result["country_name"] = c_name if c_name else (REGION_NAMES.get(result["region_code"], "UNKNOWN"))

    c_carrier = pn_carrier.name_for_number(parsed, "en")
    result["carrier"] = c_carrier if c_carrier else "UNAVAILABLE (No carrier metadata in registry)"

    # Timezones
    tz_list = list(pn_timezone.time_zones_for_number(parsed))
    result["timezones"] = tz_list if tz_list else ["UNAVAILABLE"]

    # Number Type Classification
    nt = number_type(parsed)
    result["line_type"] = LINE_TYPE_MAP.get(nt, "Unknown Line Type")
    result["line_icon"] = LINE_ICONS.get(result["line_type"], "❓")
    result["is_voip"] = (nt == PhoneNumberType.VOIP)

    # Formats, Dorks, Platform Links
    result["formats"] = generate_osint_formats(parsed)
    result["e164"] = result["formats"].get("e164", processed)
    result["international"] = result["formats"].get("international", processed)
    result["national"] = result["formats"].get("national", processed)

    result["dorks"] = generate_search_dorks(result["formats"])
    result["platform_links"] = generate_platform_links(result["formats"])

    return result
