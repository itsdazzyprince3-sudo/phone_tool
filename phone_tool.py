#!/usr/bin/env python3
"""
VirgoYT OSINT Toolkit — Version 4.0
Telecom Intelligence & Evidence Management Application for Android / Termux

Developer Credit : VIRGOYT707
Environment      : Android / Termux
Core Dependencies: phonenumbers, sqlite3
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path for modular imports
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from virgoyt.config import (
    C,
    VERSION,
    AUTHOR,
    MASK,
    BANNER,
    DB_FILE,
    BACKUP_DIR,
    EXPORT_DIR,
    ttype,
    loadbar,
    sep,
    prompt,
    REGION_NAMES,
)
from virgoyt.analyzer import analyze_number, resolve_region
from virgoyt.risk import RiskEngine
from virgoyt.report import (
    print_analysis_report,
    print_evidence_table,
    print_case_detail,
    print_stats_card,
)
from virgoyt.vault import (
    init_db,
    save_case,
    update_case_notes,
    get_case,
    list_all_cases,
    search_cases,
    delete_case,
    export_to_csv,
    backup_database,
    restore_database,
    get_vault_stats,
    check_integrity,
)
from virgoyt.git_sync import (
    audit_sync_safety,
    safe_git_pull,
    safe_git_push,
    get_remote_info,
)
from virgoyt.test_suite import run_all_tests


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STARTUP & SHUTDOWN ANIMATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def boot_sequence():
    """Display startup diagnostics and mount evidence vault."""
    os.system("clear 2>/dev/null || cls 2>/dev/null || true")
    print(BANNER)
    time.sleep(0.08)

    # Database mount and schema check
    db_ok = init_db()
    int_ok, _ = check_integrity(DB_FILE)

    msgs = [
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}Kernel core loaded // Python {sys.version.split()[0]}{C.RST}",
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}libphonenumber telecom metadata registry active{C.RST}",
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}Transparent risk evaluation engine armed{C.RST}",
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}Evidence vault mounted @ {DB_FILE.name} [Integrity: {C.G}OK{C.D}]{C.RST}",
        f"  {C.DR}[{C.G}✔{C.DR}]{C.RST} {C.D}Developer: {AUTHOR} | Status: PRIVACY-FOCUSED{C.RST}",
    ]
    for m in msgs:
        ttype(m, speed=0.003)
        time.sleep(0.02)

    print()
    ttype(f"  {C.R}{C.B}🎭 VirgoYT OSINT TOOLKIT v{VERSION} — READY ⚡{C.RST}", speed=0.008)
    sep()

def shutdown():
    """Graceful exit sequence."""
    print()
    sep()
    ttype(f"  {C.R}⚡ TERMINATING OSINT SESSION...{C.RST}", speed=0.015)
    print(f"""
  {C.DR}╔{'═'*48}╗
  ║   {C.R}{C.B}🎭 VirgoYT — SESSION SECURED & CLOSED 🎭{C.RST}{C.DR}     ║
  ║   {C.D}{C.DC}Developer: {AUTHOR}  //  Privacy Maintained.{C.RST}{C.DR}   ║
  ╚{'═'*48}╝{C.RST}
""")
    sys.exit(0)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MENU INTERFACE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def show_main_menu():
    """Render the primary navigation menu matching user specifications."""
    print()
    print(f"  {C.DR}╔{'═'*56}╗{C.RST}")
    print(f"  {C.DR}║{C.RST} {C.B}{C.W}🎭 VirgoYT OSINT — COMMAND CENTER (v{VERSION}){C.RST}          {C.DR}║{C.RST}")
    print(f"  {C.DR}╠{'═'*56}╣{C.RST}")
    print(f"  {C.DR}║{C.RST}                                                        {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}1{C.R}]{C.RST}  🔍 {C.W}Analyze Phone Number{C.RST}                           {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}2{C.R}]{C.RST}  💾 {C.W}Analyze + Save Case{C.RST}                            {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}3{C.R}]{C.RST}  📊 {C.W}View Evidence Vault{C.RST}                            {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}4{C.R}]{C.RST}  🔎 {C.W}Search Cases (ID, Notes, Tags, Phone){C.RST}       {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}5{C.R}]{C.RST}  👁️  {C.W}View Case Details{C.RST}                               {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}6{C.R}]{C.RST}  📝 {C.W}Edit Case Notes & Tags{C.RST}                         {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}7{C.R}]{C.RST}  📤 {C.W}Export to CSV{C.RST}                                  {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}8{C.R}]{C.RST}  📈 {C.W}Vault Statistics & Analytics{C.RST}                  {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}9{C.R}]{C.RST}  🛡️  {C.W}Backup Database (Live SQLite Backup){C.RST}          {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}10{C.R}]{C.RST} ♻️  {C.W}Restore Database from Backup{C.RST}                 {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}11{C.R}]{C.RST} 🧪 {C.W}Run System Self-Test Suite{C.RST}                   {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}12{C.R}]{C.RST} 🔄 {C.W}GitHub Sync & Leak-Prevention Audit{C.RST}          {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}  {C.R}[{C.W}0{C.R}]{C.RST}  ⚡ {C.R}Exit Toolkit{C.RST}                                    {C.DR}║{C.RST}")
    print(f"  {C.DR}║{C.RST}                                                        {C.DR}║{C.RST}")
    print(f"  {C.DR}╚{'═'*56}╝{C.RST}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ACTION HANDLERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def handle_analyze(save_mode: bool = False):
    """Analyze a single phone number, evaluate risk, and optionally save."""
    raw = prompt("TARGET PHONE NUMBER")
    if not raw:
        print(f"  {C.R}❌ No input provided.{C.RST}")
        return

    region_in = prompt("REGION (IN/US/GB/91/44 or country name) [IN]") or "IN"
    resolved = resolve_region(region_in)
    r_name = REGION_NAMES.get(resolved, resolved)
    print(f"  {C.D}  ► Resolved Region: {resolved} ({r_name}){C.RST}")

    loadbar("EVALUATING NUMBER", 25, 0.4)
    analysis = analyze_number(raw, resolved)

    platform_context = ""
    if save_mode:
        platform_context = prompt("CONTACT PLATFORM (WhatsApp/SMS/Telegram/Call/Web)")

    risk = RiskEngine.evaluate(analysis, platform=platform_context)
    print_analysis_report(analysis, risk)

    if save_mode:
        category = prompt("CATEGORY (Phishing / Scam / Harassment / General) [General]") or "General"
        tags = prompt("TAGS (comma-separated, e.g. spoofed,urgent,voip)")
        notes = prompt("ANALYST NOTES / CASE OBSERVATION")

        loadbar("LOGGING TO VAULT", 20, 0.3)
        row_id, case_id = save_case(
            analysis, risk,
            platform=platform_context,
            notes=notes,
            category=category,
            tags=tags,
        )
        print(f"  {C.G}✅ Case #{row_id} logged successfully.{C.RST}")
        print(f"  {C.D}  Case ID : {C.W}{case_id}{C.RST}  |  Developer: {AUTHOR}\n")

def handle_list_vault():
    """List all evidence vault records."""
    loadbar("RETRIEVING VAULT", 20, 0.3)
    rows = list_all_cases()
    print_evidence_table(rows)

def handle_search_cases():
    """Search vault across multiple attributes."""
    q = prompt("SEARCH QUERY (Phone / Case ID / Notes / Tags / Carrier)")
    if not q:
        print(f"  {C.R}❌ Search query cannot be empty.{C.RST}")
        return

    loadbar("INDEX SCANNING", 20, 0.3)
    rows = search_cases(q)
    print_evidence_table(rows)

def handle_view_case():
    """View full detailed dossier of a single case record."""
    ref = prompt("RECORD ID or CASE ID")
    if not ref:
        print(f"  {C.R}❌ No identifier entered.{C.RST}")
        return

    row = get_case(ref)
    if row:
        print_case_detail(row)
    else:
        print(f"  {C.R}❌ Case '{ref}' not found in evidence vault.{C.RST}")

def handle_edit_case():
    """Edit notes, tags, or category on an existing case record."""
    ref = prompt("RECORD ID or CASE ID to edit")
    if not ref:
        return

    row = get_case(ref)
    if not row:
        print(f"  {C.R}❌ Record '{ref}' not found.{C.RST}")
        return

    print(f"\n  {C.CN}Current Notes   :{C.RST} {row['notes'] or 'None'}")
    print(f"  {C.CN}Current Tags    :{C.RST} {row['tags'] or 'None'}")
    print(f"  {C.CN}Current Category:{C.RST} {row['category'] or 'General'}\n")

    new_notes = prompt("NEW NOTES (Enter to keep existing)") or row["notes"] or ""
    new_tags = prompt("NEW TAGS (Enter to keep existing)") or row["tags"] or ""
    new_cat = prompt("NEW CATEGORY (Enter to keep existing)") or row["category"] or "General"

    if update_case_notes(row["id"], new_notes, new_tags, new_cat):
        print(f"  {C.G}✅ Record #{row['id']} ({row['case_id']}) updated successfully.{C.RST}\n")
    else:
        print(f"  {C.R}❌ Update failed.{C.RST}\n")

def handle_export_csv():
    """Export evidence records to CSV."""
    scope = prompt("EXPORT SCOPE: [A]ll cases or [S]elected IDs? [A]").upper() or "A"
    selected_ids = None

    if scope == "S":
        ids_input = prompt("ENTER COMMA-SEPARATED IDs (e.g. 1, 2, VY-20261030-A1B2)")
        if ids_input:
            selected_ids = [i.strip() for i in ids_input.split(",") if i.strip()]

    loadbar("GENERATING CSV", 24, 0.4)
    count, out_path = export_to_csv(case_ids=selected_ids)
    print(f"  {C.G}✅ Successfully exported {count} record(s).{C.RST}")
    print(f"  {C.D}  File: {C.W}{out_path.name}{C.RST}")
    print(f"  {C.D}  Path: {C.DC}{out_path}{C.RST}\n")

def handle_vault_stats():
    """Display vault statistics and metrics card."""
    loadbar("COMPILING ANALYTICS", 20, 0.3)
    stats = get_vault_stats()
    print_stats_card(stats)

def handle_backup():
    """Create a live SQLite database backup."""
    loadbar("CREATING LIVE BACKUP", 25, 0.4)
    bak = backup_database()
    is_ok, msg = check_integrity(bak)
    if is_ok:
        print(f"  {C.G}✅ Evidence vault backup created successfully.{C.RST}")
        print(f"  {C.D}  Location : {C.W}{bak}{C.RST}")
        print(f"  {C.D}  Integrity: {C.G}{msg}{C.RST}\n")
    else:
        print(f"  {C.R}❌ Backup created but integrity check reported: {msg}{C.RST}\n")

def handle_restore():
    """Restore evidence vault from an existing backup."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backups = sorted(BACKUP_DIR.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not backups:
        print(f"\n  {C.R}❌ No backup files found in {BACKUP_DIR}.{C.RST}\n")
        return

    print(f"\n  {C.CN}Available Backups in Vault Archive:{C.RST}")
    for idx, b in enumerate(backups[:8], start=1):
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(b.stat().st_mtime))
        print(f"  [{idx}] {b.name} ({mtime})")

    choice = prompt("SELECT BACKUP NUMBER or enter custom path")
    selected_path = None
    if choice.isdigit() and 1 <= int(choice) <= len(backups):
        selected_path = backups[int(choice) - 1]
    elif choice:
        p = Path(choice)
        if p.exists():
            selected_path = p

    if not selected_path:
        print(f"  {C.R}❌ Invalid selection.{C.RST}")
        return

    confirm = prompt(f"⚠️  RESTORE FROM '{selected_path.name}'? Existing database will be safeguarded (y/n)")
    if confirm.lower() != "y":
        print(f"  {C.Y}Restore cancelled.{C.RST}\n")
        return

    loadbar("RESTORING VAULT", 25, 0.5)
    ok, msg = restore_database(selected_path)
    if ok:
        print(f"  {C.G}✅ {msg}{C.RST}\n")
    else:
        print(f"  {C.R}❌ Restore failed: {msg}{C.RST}\n")

def handle_github_sync():
    """Audit local changes and perform secure GitHub sync."""
    print()
    sep()
    print(f"  {C.CN}🛡️  VIRGOYT GITHUB SYNCHRONIZATION & DATA LEAK AUDIT{C.RST}")
    sep()

    audit = audit_sync_safety()
    r_info = audit.get("remote_info", {})
    print(f"  {C.W}Remote Origin :{C.RST} {C.CN}{r_info.get('remote_url')}{C.RST}")
    print(f"  {C.W}Active Branch :{C.RST} {C.Y}{r_info.get('branch')}{C.RST}")
    print(f"  {C.W}Safety Status :{C.RST} {C.G}CLEAN & SECURE{C.RST}" if audit["is_safe"] else f"{C.R}BLOCKED (SENSITIVE DATA DETECTED){C.RST}")

    if not audit["is_safe"]:
        print(f"\n  {C.R}🚨 CRITICAL DATA PROTECTION ALERT:{C.RST}")
        print(f"  {C.R}The following files are blocked from Git sync to protect evidence/credentials:{C.RST}")
        for viol in audit["sensitive_violations"]:
            print(f"    {C.R}▸ {viol}{C.RST}")
        print(f"  {C.D}Ensure these files are listed in .gitignore before attempting sync.{C.RST}\n")
        return

    staged_cnt = len(audit["staged"])
    unstaged_cnt = len(audit["unstaged"])
    untracked_cnt = len(audit["untracked"])
    print(f"  {C.D}Files changed: {staged_cnt} staged, {unstaged_cnt} unstaged, {untracked_cnt} untracked.{C.RST}\n")

    print(f"  {C.R}[{C.W}P{C.R}]{C.RST} Pull latest updates from GitHub")
    print(f"  {C.R}[{C.W}U{C.R}]{C.RST} Commit & Push toolkit updates to GitHub")
    print(f"  {C.R}[{C.W}C{C.R}]{C.RST} Cancel")

    action = prompt("ACTION (P/U/C)").upper()
    if action == "P":
        ok, msg = safe_git_pull()
        if ok:
            print(f"  {C.G}✅ {msg}{C.RST}\n")
            restart = prompt("Hot-restart VirgoYT engine now? (y/n)")
            if restart.lower() == "y":
                print(f"  {C.CN}⚡ Restarting...{C.RST}\n")
                time.sleep(1)
                os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print(f"  {C.R}❌ {msg}{C.RST}\n")

    elif action == "U":
        commit_msg = prompt("COMMIT MESSAGE") or f"VirgoYT OSINT Toolkit v{VERSION} update"
        confirm = prompt(f"Push to '{r_info.get('remote_url')}'? (y/n)")
        if confirm.lower() == "y":
            ok, msg = safe_git_push(commit_msg)
            if ok:
                print(f"  {C.G}✅ {msg}{C.RST}\n")
            else:
                print(f"  {C.R}❌ {msg}{C.RST}\n")
        else:
            print(f"  {C.Y}Push cancelled.{C.RST}\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN ENTRY POINT & EVENT LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Primary application entry point."""
    boot_sequence()

    while True:
        try:
            show_main_menu()
            choice = prompt("SELECT ACTION")

            if choice == "1":
                handle_analyze(save_mode=False)
            elif choice == "2":
                handle_analyze(save_mode=True)
            elif choice == "3":
                handle_list_vault()
            elif choice == "4":
                handle_search_cases()
            elif choice == "5":
                handle_view_case()
            elif choice == "6":
                handle_edit_case()
            elif choice == "7":
                handle_export_csv()
            elif choice == "8":
                handle_vault_stats()
            elif choice == "9":
                handle_backup()
            elif choice == "10":
                handle_restore()
            elif choice == "11":
                run_all_tests()
            elif choice == "12":
                handle_github_sync()
            elif choice == "0":
                shutdown()
            else:
                print(f"  {C.R}❌ Invalid selection. Please enter 0-12.{C.RST}")

        except KeyboardInterrupt:
            print("\n")
            shutdown()
        except Exception as e:
            print(f"\n  {C.R}❌ Application Error: {e}{C.RST}\n")

if __name__ == "__main__":
    main()
