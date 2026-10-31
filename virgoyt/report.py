"""
report.py — Intelligence Report Formatter & Presentation Engine
VirgoYT OSINT Toolkit v5.0
Developer Credit: VIRGOYT707
"""

from typing import Dict, Any, List, Optional
import sqlite3
from datetime import datetime

from .config import C, MASK, VERSION, AUTHOR
from .risk import RiskEngine
from .spiderfoot import SpiderFootEngine

def print_analysis_report(
    analysis: Dict[str, Any],
    risk: Dict[str, Any],
    case_id: str = "",
    recon: Optional[Dict[str, Any]] = None
) -> None:
    """Render a comprehensive intelligence report in terminal with deep OSINT dorks & links."""
    is_valid = analysis.get("is_valid", False)
    is_possible = analysis.get("is_possible", False)

    if is_valid:
        valid_badge = f"{C.G}✔ VALID (Numbering Plan Conforming){C.RST}"
    elif is_possible:
        valid_badge = f"{C.Y}⚠ POSSIBLE LENGTH (Unallocated / Unverified Scheme){C.RST}"
    else:
        valid_badge = f"{C.R}✘ INVALID FORMAT (Violates E.164){C.RST}"

    score = risk.get("score")
    risk_level = risk.get("risk_level", "UNKNOWN")
    confidence = risk.get("confidence", "MEDIUM")
    risk_bar_str = RiskEngine.format_risk_bar(score, risk_level)

    cid_str = case_id or f"SCAN-{datetime.now().strftime('%H%M%S')}"

    print()
    print(f"  {C.R}╔{'═'*64}╗{C.RST}")
    print(f"  {C.R}║{C.RST} {C.B}{C.W}🎭 VirgoYT OSINT — DEEP RECON INTELLIGENCE REPORT (v{VERSION}){C.RST} {C.R}║{C.RST}")
    print(f"  {C.R}╠{'═'*64}╣{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.D}Case ID   : {C.W}{cid_str:<22}{C.RST} {C.D}Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}{C.RST}  {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}                                                                {C.R}║{C.RST}")

    # ── TARGET SECTION ──
    print(f"  {C.R}║{C.RST}  {C.DC}┌── TARGET SPECIFICATION ────────────────────────────────{C.RST}   {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 📱 {C.W}Input Text    :{C.RST} {C.Y}{analysis.get('phone_input')}{C.RST}")
    if analysis.get("phone_processed") != analysis.get("phone_input"):
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🔄 {C.W}Normalized    :{C.RST} {C.G}{analysis.get('phone_processed')}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 📞 {C.W}International :{C.RST} {C.G}{C.B}{analysis.get('international')}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🔢 {C.W}E.164 Standard:{C.RST} {C.CN}{analysis.get('e164')}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🏷️  {C.W}National Dial :{C.RST} {C.CN}{analysis.get('national')}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🔑 {C.W}Technical Plan:{C.RST} {valid_badge}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} ℹ️  {C.W}Structure Note:{C.RST} {C.D}{analysis.get('possibility_reason')}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── TELECOM ALLOCATION SECTION ──
    print(f"  {C.R}║{C.RST}  {C.DC}┌── TELECOM ALLOCATION & REGISTRY METADATA ──────────────{C.RST}   {C.R}║{C.RST}")
    cc = analysis.get("country_code", "?")
    rc = analysis.get("region_code", "??")
    cname = analysis.get("country_name", "UNKNOWN")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🌐 {C.W}Jurisdiction  :{C.RST} {C.CN}{cname}{C.RST}  [{C.W}{rc}{C.RST}]  (CC: +{cc})")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 📡 {C.W}Assigned Telco:{C.RST} {C.M}{analysis.get('carrier')}{C.RST}")
    icon = analysis.get("line_icon", "❓")
    ltype = analysis.get("line_type", "Unknown Line Type")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} {icon} {C.W}Line Category :{C.RST} {C.Y}{ltype}{C.RST}")
    tzs = ", ".join(analysis.get("timezones", []))
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🕐 {C.W}Regulatory TZ :{C.RST} {C.D}{tzs}{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── THREAT ASSESSMENT SECTION ──
    print(f"  {C.R}║{C.RST}  {C.DC}┌── THREAT & ANOMALY ASSESSMENT ─────────────────────────{C.RST}   {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🎯 {C.W}Composite Risk:{C.RST} {risk_bar_str}")
    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🛡️  {C.W}Confidence    :{C.RST} {C.W}{confidence}{C.RST}  {C.D}(Evidence Density){C.RST}")

    factors = risk.get("factors", [])
    if factors:
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} {C.B}{C.W}Verifiable Signals:{C.RST}")
        for f in factors:
            sign = f"{C.R}+{f['delta']}{C.RST}" if f['delta'] > 0 else f"{C.G}{f['delta']}{C.RST}"
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {sign} {C.W}{f['code']}{C.RST} {C.D}({f['category']}){C.RST}")
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}      {C.D}▸ {f['reason']}{C.RST}")

    if analysis.get("is_voip"):
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} {C.Y}⚠ PRIVACY / DISPOSABLE LINE NOTICE:{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.D}Virtual/VoIP telephony detected. Likely burner app or SIP proxy.{C.RST}")

    print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── DEEP RECON / ALL FORMATS ──
    formats = (recon.get("all_formats") if recon else None) or analysis.get("formats", {})
    if formats:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── NUMBER PERMUTATIONS & BRUTE FORMAT VARIATIONS ───────{C.RST}   {C.R}║{C.RST}")
        for k, v in formats.items():
            if v:
                label = k.replace("_", " ").upper()
                print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.D}{label:<15}:{C.RST} {C.CN}{v}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── VERIFIABLE PUBLIC LOOKUP LINKS ──
    links = (recon.get("platform_links") if recon else None) or analysis.get("platform_links", {})
    if links:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── DIRECT PLATFORM & RECON DIRECTORY SHORTCUTS ─────────{C.RST}   {C.R}║{C.RST}")
        for pname, purl in links.items():
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   🔗 {C.W}{pname:<24}:{C.RST} {C.D}{C.BL}{purl}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── EMAIL DISCOVERY SIGNALS ──
    email_dorks = recon.get("email_dorks", []) if recon else []
    if email_dorks:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── EMAIL FOOTPRINT DISCOVERY (Linked Accounts / Dumps) ─{C.RST}   {C.R}║{C.RST}")
        for ed in email_dorks[:8]:
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.Y}📧{C.RST} {C.D}{ed}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── GOV / PUBLIC RECORDS RECON ──
    gov_dorks = recon.get("gov_dorks", []) if recon else []
    if gov_dorks:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── PUBLIC & INSTITUTIONAL RECORD FOOTPRINT QUERIES ─────{C.RST}   {C.R}║{C.RST}")
        for gd in gov_dorks[:8]:
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.CN}🏛️{C.RST} {C.D}{gd}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── BREACH / LEAK CORRELATION ──
    breach_recon = recon.get("breach_recon", []) if recon else []
    if breach_recon:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── BREACH DUMPS & LEAK ARCHIVE CORRELATION ─────────────{C.RST}   {C.R}║{C.RST}")
        for br in breach_recon[:6]:
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.R}💥{C.RST} {C.D}{br}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── ONION / DEEP RECON ──
    deep_web = recon.get("deep_web_dorks", []) if recon else []
    if deep_web:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── DARKNET / ONION INDEX FOOTPRINTS (Clearnet Proxies) ──{C.RST}   {C.R}║{C.RST}")
        for dw in deep_web[:5]:
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.M}🧅{C.RST} {C.D}{dw}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── SPIDERFOOT OSINT ENGINE INTEGRATION ──
    sf_targets = SpiderFootEngine.generate_targets(analysis)
    for sf_line in SpiderFootEngine.format_spiderfoot_summary(sf_targets):
        print(sf_line)

    # ── COMPREHENSIVE SEARCH DORKS ──
    dorks = (recon.get("mega_dorks") if recon else None) or analysis.get("dorks", [])
    if dorks:
        print(f"  {C.R}║{C.RST}  {C.DC}┌── ADVANCED RECON QUERIES (Social, Job, Web Footprint) ─{C.RST}   {C.R}║{C.RST}")
        for d in dorks[:15]:
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.DG}▸{C.RST} {C.D}{d}{C.RST}")
        if len(dorks) > 15:
            print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.Y}... and {len(dorks) - 15} more queries generated.{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── RECON SUMMARY STATS ──
    if recon:
        total_q = recon.get("total_dorks_count", 0)
        total_p = recon.get("total_platforms_count", 0)
        print(f"  {C.R}║{C.RST}  {C.DC}┌── RECON METRICS & DENSITY SUMMARY ─────────────────────{C.RST}   {C.R}║{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 📊 {C.W}Total Footprint Queries:{C.RST} {C.G}{total_q}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🌐 {C.W}Connected Platforms    :{C.RST} {C.G}{total_p}{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🎯 {C.W}Search Strategy        :{C.RST} {C.CN}Brute-Permutation Dork Matrix{C.RST}")
        print(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")

    # ── STATUS FOOTER ──
    print(f"  {C.R}║{C.RST}                                                                {C.R}║{C.RST}")
    print(f"  {C.R}║{C.RST}  {C.D}VirgoYT v{VERSION}  |  Developer: {AUTHOR}  |  STATUS: FULL-SPECTRUM OSINT{C.RST}  {C.R}║{C.RST}")
    print(f"  {C.R}╚{'═'*64}╝{C.RST}\n")

def print_evidence_table(rows: List[sqlite3.Row]) -> None:
    """Print an aligned ASCII evidence vault summary table."""
    if not rows:
        print(f"\n  {C.R}❌ Vault empty. No records matching criteria.{C.RST}\n")
        return

    print()
    print(f"  {C.R}{C.B}🎭 EVIDENCE VAULT — {len(rows)} RECORD(S) RETRIEVED{C.RST}")
    print(f"  {C.DR}┌{'─'*4}┬{'─'*17}┬{'─'*18}┬{'─'*12}┬{'─'*12}┬{'─'*10}┬{'─'*10}┬{'─'*6}┬{'─'*19}┐{C.RST}")
    print(f"  {C.DR}│{C.W}{C.B} ID {C.DR}│{C.W} CASE ID         {C.DR}│{C.W} PHONE            {C.DR}│{C.W} COUNTRY    {C.DR}│{C.W} CARRIER    {C.DR}│{C.W} TYPE     {C.DR}│{C.W} CATEGORY {C.DR}│{C.W} RISK {C.DR}│{C.W} UPDATED (UTC)     {C.DR}│{C.RST}")
    print(f"  {C.DR}├{'─'*4}┼{'─'*17}┼{'─'*18}┼{'─'*12}┼{'─'*12}┼{'─'*10}┼{'─'*10}┼{'─'*6}┼{'─'*19}┤{C.RST}")

    for r in rows:
        cid = (r["case_id"] or r["case_hash"] or str(r["id"]))[:15]
        phone = (r["phone"] or "")[:16]
        country = (r["country"] or "Unknown")[:10]
        carrier = (r["carrier"] or "Unknown")[:10]
        ltype = (r["line_type"] or "Unknown")[:8]
        cat = (r["category"] or "General")[:8]
        rs = r["risk_score"] if r["risk_score"] is not None and r["risk_score"] >= 0 else 0
        r_col = C.R if rs >= 70 else (C.Y if rs >= 45 else (C.CN if rs >= 20 else C.G))
        score_str = f"{rs}%" if r["risk_score"] is not None and r["risk_score"] >= 0 else "N/A"
        u_date = (r["updated_at"] or r["date_added"] or "")[:17]

        print(f"  {C.DR}│{C.W}{r['id']:>3} "
              f"{C.DR}│ {C.W}{cid:<15}{C.RST} "
              f"{C.DR}│ {C.CN}{phone:<16}{C.RST} "
              f"{C.DR}│ {C.W}{country:<10}{C.RST} "
              f"{C.DR}│ {C.M}{carrier:<10}{C.RST} "
              f"{C.DR}│ {C.Y}{ltype:<8}{C.RST} "
              f"{C.DR}│ {C.D}{cat:<8}{C.RST} "
              f"{C.DR}│ {r_col}{score_str:>4} {C.RST}"
              f"{C.DR}│ {C.D}{u_date:<17}{C.RST} {C.DR}│{C.RST}")

    print(f"  {C.DR}└{'─'*4}┴{'─'*17}┴{'─'*18}┴{'─'*12}┴{'─'*12}┴{'─'*10}┴{'─'*10}┴{'─'*6}┴{'─'*19}┘{C.RST}\n")

def print_case_detail(row: sqlite3.Row) -> None:
    """Print full investigative dossier for a single case record."""
    is_valid = bool(row["is_valid"])
    v_sym = f"{C.G}✔ Validated numbering plan{C.RST}" if is_valid else f"{C.R}✘ Non-standard numbering{C.RST}"
    rs = row["risk_score"]
    r_level = row["risk_level"] or "UNKNOWN"
    r_bar = RiskEngine.format_risk_bar(rs if rs >= 0 else None, r_level)

    print()
    print(f"  {C.R}┌{'─'*60}┐{C.RST}")
    print(f"  {C.R}│{C.RST} {C.B}{C.W}🎭 EVIDENCE DOSSIER — CASE: {row['case_id'] or row['id']}{C.RST}")
    print(f"  {C.R}├{'─'*60}┤{C.RST}")
    print(f"  {C.R}│{C.RST} 🆔 {C.W}Primary ID  :{C.RST} #{row['id']}  {C.D}(Legacy Ref: {row['case_hash'] or 'N/A'}){C.RST}")
    print(f"  {C.R}│{C.RST} 📱 {C.W}Target Phone:{C.RST} {C.G}{C.B}{row['phone']}{C.RST}")
    print(f"  {C.R}│{C.RST} 🔢 {C.W}E.164 / Nat :{C.RST} {C.CN}{row['e164_fmt'] or '—'}  /  {row['national_fmt'] or '—'}{C.RST}")
    print(f"  {C.R}│{C.RST} 🌐 {C.W}Jurisdiction:{C.RST} {C.CN}{row['country']}{C.RST} [{C.W}{row['region']}{C.RST}]")
    print(f"  {C.R}│{C.RST} 📡 {C.W}Telco Carrier:{C.RST} {C.M}{row['carrier']}{C.RST}")
    print(f"  {C.R}│{C.RST} 📞 {C.W}Line Type   :{C.RST} {C.Y}{row['line_type']}{C.RST}")
    print(f"  {C.R}│{C.RST} 🕐 {C.W}Timezones   :{C.RST} {C.D}{row['timezones'] or 'N/A'}{C.RST}")
    print(f"  {C.R}│{C.RST} 🔑 {C.W}Validation  :{C.RST} {v_sym}")
    print(f"  {C.R}│{C.RST} 🎯 {C.W}Risk Score  :{C.RST} {r_bar}")
    print(f"  {C.R}│{C.RST} 🛡️  {C.W}Confidence  :{C.RST} {C.W}{row['confidence'] or 'MEDIUM'}{C.RST}")
    if row["risk_factors"]:
        print(f"  {C.R}│{C.RST} 🔍 {C.W}Signals     :{C.RST} {C.D}{row['risk_factors']}{C.RST}")
    print(f"  {C.R}│{C.RST} 📁 {C.W}Category    :{C.RST} {C.W}{row['category'] or 'General'}{C.RST}")
    print(f"  {C.R}│{C.RST} 🏷️  {C.W}Tags        :{C.RST} {C.CN}{row['tags'] or '—'}{C.RST}")
    print(f"  {C.R}│{C.RST} 🔗 {C.W}Platform    :{C.RST} {C.W}{row['platform'] or '—'}{C.RST}")
    print(f"  {C.R}│{C.RST} 📝 {C.W}Analyst Note:{C.RST} {C.Y}{row['notes'] or '—'}{C.RST}")
    print(f"  {C.R}│{C.RST} 📅 {C.W}Created     :{C.RST} {C.D}{row['date_added']}{C.RST}")
    print(f"  {C.R}│{C.RST} 🔄 {C.W}Last Updated:{C.RST} {C.D}{row['updated_at']}{C.RST}")
    print(f"  {C.R}└{'─'*60}┘{C.RST}\n")

def print_stats_card(stats: Dict[str, Any]) -> None:
    """Print an aggregated statistics summary card."""
    print()
    print(f"  {C.R}┌{'─'*50}┐{C.RST}")
    print(f"  {C.R}│{C.RST} {C.B}{C.W}🎭 EVIDENCE VAULT ANALYTICS & METRICS{C.RST}")
    print(f"  {C.R}├{'─'*50}┤{C.RST}")
    print(f"  {C.R}│{C.RST} 📊 {C.W}Total Cases Recorded :{C.RST}  {C.CN}{C.B}{stats['total']}{C.RST}")
    print(f"  {C.R}│{C.RST} 👻 {C.W}VoIP / Virtual Lines :{C.RST}  {C.R}{stats['burners']}{C.RST}")
    print(f"  {C.R}│{C.RST} 🚨 {C.W}High Suspicion Cases :{C.RST}  {C.Y}{stats['high_risk']}{C.RST}")
    print(f"  {C.R}│{C.RST} 🎯 {C.W}Mean Telecom Risk    :{C.RST}  {RiskEngine.format_risk_bar(stats['avg_risk'], 'MEAN')}")

    cats = stats.get("categories", [])
    if cats:
        print(f"  {C.R}│{C.RST}")
        print(f"  {C.R}│{C.RST} {C.B}{C.W}Categories Breakdown:{C.RST}")
        for c, count in cats[:5]:
            print(f"  {C.R}│{C.RST}   {C.D}▸ {c:<18}: {count}{C.RST}")

    plats = stats.get("top_platforms", [])
    if plats:
        print(f"  {C.R}│{C.RST}")
        print(f"  {C.R}│{C.RST} {C.B}{C.W}Top Contact Platforms:{C.RST}")
        for p, count in plats:
            p_label = p if p else "Unspecified"
            print(f"  {C.R}│{C.RST}   {C.D}▸ {p_label:<18}: {count}{C.RST}")

    print(f"  {C.R}└{'─'*50}┘{C.RST}\n")
