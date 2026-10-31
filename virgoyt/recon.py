"""
recon.py — Exhaustive OSINT Reconnaissance & Footprint Engine
VirgoYT OSINT Toolkit v5.0
Developer Credit: VIRGOYT707
"""

from typing import Dict, Any, List
import urllib.parse
from .config import REGION_NAMES

def generate_all_formats(
    parsed: Any,
    e164: str,
    international: str,
    national: str,
    raw_intl: str,
    raw_national: str
) -> Dict[str, str]:
    """Generate every standard and permutation layout for search footprinting."""
    formats: Dict[str, str] = {
        "e164": e164 or "",
        "international": international or "",
        "national": national or "",
        "raw_intl": raw_intl or "",
        "raw_national": raw_national or "",
        "url_encoded": urllib.parse.quote_plus(e164) if e164 else "",
    }

    clean_digits = "".join(ch for ch in (raw_national or "") if ch.isdigit())
    if len(clean_digits) == 10:
        formats["dotted"] = f"{clean_digits[:3]}.{clean_digits[3:6]}.{clean_digits[6:]}"
        formats["dashed"] = f"{clean_digits[:3]}-{clean_digits[3:6]}-{clean_digits[6:]}"
        formats["spaced"] = f"{clean_digits[:3]} {clean_digits[3:6]} {clean_digits[6:]}"
        formats["parentheses"] = f"({clean_digits[:3]}) {clean_digits[3:6]}-{clean_digits[6:]}"
        formats["trunk_prefix"] = f"0{clean_digits}"
    elif len(clean_digits) > 6:
        p = len(clean_digits) // 3
        formats["dotted"] = f"{clean_digits[:p]}.{clean_digits[p:2*p]}.{clean_digits[2*p:]}"
        formats["dashed"] = f"{clean_digits[:p]}-{clean_digits[p:2*p]}-{clean_digits[2*p:]}"
        formats["spaced"] = f"{clean_digits[:p]} {clean_digits[p:2*p]} {clean_digits[2*p:]}"
        formats["trunk_prefix"] = f"0{clean_digits}"

    intl_digits = "".join(ch for ch in (raw_intl or "") if ch.isdigit())
    if intl_digits:
        formats["intl_spaced"] = " ".join(intl_digits[i:i+3] for i in range(0, len(intl_digits), 3))

    return formats

def generate_mega_dorks(formats: Dict[str, str], region: str = "IN") -> List[str]:
    """Generate exhaustive Google dork queries across 100+ public platforms."""
    e164 = formats.get("e164", "")
    raw_intl = formats.get("raw_intl", "")
    nat_raw = formats.get("raw_national", "")
    target = f'"{e164}"' if e164 else (f'"{raw_intl}"' if raw_intl else "")

    if not target:
        return []

    dorks: List[str] = [
        target,
        f'"{nat_raw}"' if nat_raw and nat_raw != e164 else "",
    ]
    dorks = [d for d in dorks if d]

    social_platforms = [
        "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
        "tiktok.com", "snapchat.com", "pinterest.com", "reddit.com", "tumblr.com",
        "quora.com", "medium.com", "vk.com", "ok.ru", "weibo.com", "telegram.org",
        "discord.com", "twitch.tv", "youtube.com", "github.com", "gitlab.com",
        "bitbucket.org", "stackoverflow.com", "behance.net", "dribbble.com",
        "deviantart.com", "flickr.com", "500px.com", "soundcloud.com", "spotify.com",
        "meetup.com", "badoo.com", "tagged.com", "hi5.com", "minds.com",
        "mastodon.social", "gab.com", "parler.com", "rumble.com", "odysee.com",
        "bitchute.com", "dailymotion.com", "vimeo.com", "signal.org", "viber.com",
        "line.me", "kakaotalk.com", "wechat.com"
    ]
    for s in social_platforms:
        dorks.append(f'site:{s} {target}')

    jobs = [
        "naukri.com", "linkedin.com", "indeed.com", "glassdoor.com", "shine.com",
        "foundit.in", "timesjobs.com", "internshala.com", "freshersworld.com",
        "upwork.com", "freelancer.com", "fiverr.com", "toptal.com", "guru.com",
        "simplyhired.com", "ziprecruiter.com", "careerbuilder.com", "dice.com"
    ]
    for j in jobs:
        dorks.append(f'site:{j} {target}')

    ecommerce = [
        "amazon.in", "flipkart.com", "ebay.com", "olx.in", "quikr.com",
        "justdial.com", "sulekha.com", "indiamart.com", "tradeindia.com",
        "alibaba.com", "aliexpress.com", "etsy.com", "shopify.com", "craigslist.org"
    ]
    for ec in ecommerce:
        dorks.append(f'site:{ec} {target}')

    filetypes = ["pdf", "xlsx", "xls", "docx", "doc", "csv", "txt", "sql", "log", "json"]
    for ft in filetypes:
        dorks.append(f'{target} filetype:{ft}')

    pastes = [
        "pastebin.com", "ghostbin.com", "dpaste.org", "hastebin.com", "rentry.co",
        "privatebin.net", "paste.ee", "justpaste.it", "controlc.com", "paste2.org"
    ]
    for p in pastes:
        dorks.append(f'site:{p} {target}')

    dorks.extend([
        f'{target} "leak"',
        f'{target} "breach"',
        f'{target} "dump"',
        f'{target} "database"',
        f'{target} "password"',
        f'{target} "contact list"',
    ])

    return dorks

def generate_mega_platform_links(formats: Dict[str, str], region: str = "IN") -> Dict[str, str]:
    """Generate direct verifiable web and OSINT portal lookup links."""
    e164 = formats.get("e164", "")
    raw_intl = formats.get("raw_intl", "")
    nat_raw = formats.get("raw_national", "")

    links: Dict[str, str] = {}
    if raw_intl:
        links["WhatsApp Direct"] = f"https://wa.me/{raw_intl}"
        links["Telegram Direct"] = f"https://t.me/+{raw_intl}"
        links["Sync.me Lookup"] = f"https://sync.me/search/?number=%2B{raw_intl}"
        links["Viber Direct"] = f"viber://chat?number=%2B{raw_intl}"

    if e164:
        enc = urllib.parse.quote_plus(e164)
        links["Google Search"] = f"https://www.google.com/search?q=%22{enc}%22"
        links["Bing Search"] = f"https://www.bing.com/search?q=%22{enc}%22"
        links["DuckDuckGo"] = f"https://duckduckgo.com/?q=%22{enc}%22"
        links["Yandex Search"] = f"https://yandex.com/search/?text=%22{enc}%22"
        links["NumLookup"] = f"https://www.numlookup.com/lookup?number={enc}"
        links["Whoscall Search"] = f"https://whoscall.com/search?phone={enc}"
        links["Spokeo Lookup"] = f"https://www.spokeo.com/search?q={enc}"
        links["IntelX Directory"] = f"https://intelx.io/?s={enc}"

    if nat_raw:
        links["Truecaller Web"] = f"https://www.truecaller.com/search/in/{nat_raw}"
        links["SpyDialer"] = f"https://www.spydialer.com/results.aspx?Number={nat_raw}"
        links["FastPeopleSearch"] = f"https://www.fastpeoplesearch.com/{nat_raw}"
        links["ThatsThem Lookup"] = f"https://thatsthem.com/phone/{nat_raw}"

    if raw_intl.startswith("91") or region == "IN":
        links["TRAI DND Registry (India)"] = "https://www.nccptrai.gov.in/nccpregistry/search.misc"

    return links

def generate_email_discovery_dorks(formats: Dict[str, str]) -> List[str]:
    """Generate search footprint queries targeting linked email addresses."""
    e164 = formats.get("e164", "")
    raw_intl = formats.get("raw_intl", "")
    nat_raw = formats.get("raw_national", "")

    terms = [t for t in [e164, raw_intl, nat_raw] if t]
    if not terms:
        return []

    dorks: List[str] = []
    domains = ["@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com", "@proton.me", "@icloud.com"]
    for t in terms[:2]:
        for dom in domains:
            dorks.append(f'"{t}" "{dom}"')
        dorks.append(f'"{t}" "email"')
        dorks.append(f'"{t}" "contact email"')
        dorks.append(f'site:gravatar.com "{t}"')
        dorks.append(f'site:keybase.io "{t}"')

    return dorks

def generate_gov_recon_dorks(formats: Dict[str, str], region: str = "IN") -> List[str]:
    """Generate public domain regulatory, public record, and institutional queries."""
    e164 = formats.get("e164", "")
    nat_raw = formats.get("raw_national", "")
    target = f'"{e164}"' if e164 else (f'"{nat_raw}"' if nat_raw else "")
    if not target:
        return []

    dorks: List[str] = []
    if region == "IN" or (e164 and e164.startswith("+91")):
        gov_domains = [
            "gov.in", "nic.in", "uidai.gov.in", "epfindia.gov.in",
            "incometax.gov.in", "nvsp.in", "digilocker.gov.in", "umang.gov.in",
            "parivahan.gov.in", "ecourts.gov.in", "courtnic.nic.in",
            "indiankanoon.org", "mca.gov.in"
        ]
        for gd in gov_domains:
            dorks.append(f'site:{gd} {target}')
            if nat_raw and nat_raw != e164:
                dorks.append(f'site:{gd} "{nat_raw}"')
    else:
        dorks.extend([
            f'site:gov {target}',
            f'site:org {target}',
            f'site:court {target}',
            f'site:registry {target}',
        ])

    return dorks

def generate_breach_recon(formats: Dict[str, str]) -> List[str]:
    """Generate footprint search signatures for breach dumps and leak archives."""
    e164 = formats.get("e164", "")
    raw_intl = formats.get("raw_intl", "")
    nat_raw = formats.get("raw_national", "")
    target = f'"{e164}"' if e164 else (f'"{raw_intl}"' if raw_intl else "")
    if not target:
        return []

    recon: List[str] = [
        f'{target} "dehashed"',
        f'{target} "leak-lookup"',
        f'{target} "breachdirectory"',
        f'{target} "combo list"',
        f'{target} "data dump" 2024 OR 2025 OR 2026',
        f'{target} "sql dump"',
        f'site:anonfiles.* {target}',
        f'site:mega.nz {target}',
    ]
    if nat_raw:
        recon.append(f'"{nat_raw}" "data breach"')

    return recon

def generate_deep_web_dorks(formats: Dict[str, str]) -> List[str]:
    """Generate clearnet directory queries pointing towards indexed onion/tor mirrors."""
    e164 = formats.get("e164", "")
    raw_intl = formats.get("raw_intl", "")
    target = f'"{e164}"' if e164 else (f'"{raw_intl}"' if raw_intl else "")
    if not target:
        return []

    return [
        f'site:ahmia.fi {target}',
        f'site:tor2web.* {target}',
        f'site:onion.ws {target}',
        f'site:onion.ly {target}',
        f'{target} inurl:onion',
    ]

def run_full_recon(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Execute complete multi-engine reconnaissance generator."""
    parsed = analysis.get("parsed")
    e164 = analysis.get("e164", "")
    intl = analysis.get("international", "")
    nat = analysis.get("national", "")
    raw_intl = analysis.get("formats", {}).get("raw_intl", "")
    raw_nat = analysis.get("formats", {}).get("raw_national", "")
    region = analysis.get("region_code", "IN")

    all_formats = generate_all_formats(parsed, e164, intl, nat, raw_intl, raw_nat)
    mega_dorks = generate_mega_dorks(all_formats, region)
    platform_links = generate_mega_platform_links(all_formats, region)
    email_dorks = generate_email_discovery_dorks(all_formats)
    gov_dorks = generate_gov_recon_dorks(all_formats, region)
    breach_recon = generate_breach_recon(all_formats)
    deep_web = generate_deep_web_dorks(all_formats)

    total_dorks = (
        len(mega_dorks) + len(email_dorks) +
        len(gov_dorks) + len(breach_recon) + len(deep_web)
    )

    return {
        "all_formats": all_formats,
        "mega_dorks": mega_dorks,
        "platform_links": platform_links,
        "email_dorks": email_dorks,
        "gov_dorks": gov_dorks,
        "breach_recon": breach_recon,
        "deep_web_dorks": deep_web,
        "total_dorks_count": total_dorks,
        "total_platforms_count": len(platform_links),
    }
