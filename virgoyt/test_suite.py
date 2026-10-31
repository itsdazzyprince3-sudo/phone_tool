"""
test_suite.py — Built-in Verification & Unit Test Suite
VirgoYT OSINT Toolkit v4.0
Developer Credit: VIRGOYT707
"""

import socket
import struct
import sys
import tempfile
import sqlite3
import csv
from pathlib import Path
from typing import Dict, Any, List, Tuple

from .config import C, VERSION, AUTHOR
from .analyzer import analyze_number, resolve_region, generate_osint_formats
from .recon import run_full_recon
from .risk import RiskEngine
from .spiderfoot import SpiderFootEngine
from .device_audit import evaluate_evidence
from .detection import (
    parse_package_dump,
    score_package,
    detect_periodic,
    read_pcap,
    analyze_traffic,
)
from .vault import (
    init_db,
    save_case,
    get_case,
    search_cases,
    update_case_notes,
    delete_case,
    export_to_csv,
    backup_database,
    restore_database,
    check_integrity,
)
from .git_sync import audit_sync_safety, ensure_gitignore_safety

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SYNTHETIC TEST FIXTURES (ITU-T & SYNTHETIC DATA)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Reserved fictitious numbers per ITU-T and national regulatory standards
SYNTHETIC_NUMBERS = {
    "us_valid_sample": "+1 415 555 2671",        # Fictitious US exchange
    "in_synthetic_mobile": "+91 91537 05685",     # Synthetic Indian mobile format
    "uk_valid_sample": "+44 20 7946 0991",        # Ofcom fictitious drama number
    "invalid_country_code": "+999 555 123456",   # Non-existent ITU country code
    "invalid_length_short": "+1 415",            # Too short for NANPA
    "voip_synthetic": "+1 201 555 0199",         # Synthetic US VoIP/virtual block
}

def run_all_tests() -> Dict[str, Any]:
    """
    Execute end-to-end self-tests across all 10 required audit areas.
    Uses temporary environments to ensure zero mutation of production databases.
    """
    results: List[Dict[str, Any]] = []

    def record_test(name: str, passed: bool, detail: str) -> None:
        results.append({"name": name, "passed": passed, "detail": detail})

    print(f"\n  {C.R}🎭 VirgoYT v{VERSION} — SELF-TEST VERIFICATION SUITE{C.RST}")
    print(f"  {C.D}Developer: {AUTHOR} | Target: Android/Termux + Linux Python Environment{C.RST}\n")

    # ── TEST 1: Valid and Invalid Phone Numbers ──
    try:
        res_valid = analyze_number(SYNTHETIC_NUMBERS["us_valid_sample"], "US")
        res_invalid = analyze_number(SYNTHETIC_NUMBERS["invalid_country_code"], "US")
        t1_ok = (res_valid["is_valid"] is True) and (res_invalid["is_valid"] is False)
        record_test("Valid & Invalid Phone Parsing", t1_ok, "Properly discriminates ITU numbering plan compliance.")
    except Exception as e:
        record_test("Valid & Invalid Phone Parsing", False, str(e))

    # ── TEST 2: International Formatting ──
    try:
        res_fmt = analyze_number(SYNTHETIC_NUMBERS["in_synthetic_mobile"], "IN")
        fmts = res_fmt.get("formats", {})
        has_e164 = fmts.get("e164", "").startswith("+91")
        has_nat = bool(fmts.get("national"))
        has_rfc = fmts.get("rfc3966", "").startswith("tel:")
        t2_ok = has_e164 and has_nat and has_rfc
        record_test("International Formatting (E.164/Nat/RFC)", t2_ok, f"Generated E.164 ({fmts.get('e164')}) and RFC3966.")
    except Exception as e:
        record_test("International Formatting", False, str(e))

    # ── TEST 3: Missing Carrier Metadata Handling ──
    try:
        # A wireline or unassigned number where carrier metadata is sparse
        res_sparse = analyze_number(SYNTHETIC_NUMBERS["uk_valid_sample"], "GB")
        carrier = res_sparse.get("carrier")
        t3_ok = bool(carrier) and isinstance(carrier, str)
        record_test("Missing / Unavailable Carrier Handling", t3_ok, f"Graceful fallback string: '{carrier[:25]}'")
    except Exception as e:
        record_test("Missing Carrier Handling", False, str(e))

    # ── TEST 4: Unknown Regions & Auto-Resolution ──
    try:
        r1 = resolve_region("91")      # Dial code to ISO
        r2 = resolve_region("United States")  # Substring to ISO
        r3 = resolve_region("UNKNOWN_XYZ")    # Fallback to default
        t4_ok = (r1 == "IN") and (r2 == "US") and (r3 == "IN")
        record_test("Unknown Regions & Dial Code Resolution", t4_ok, f"Resolved '91'->'{r1}', 'United States'->'{r2}'.")
    except Exception as e:
        record_test("Unknown Regions Resolution", False, str(e))

    # ── TEST 5: Risk Scoring Engine & Confidence ──
    try:
        norm_eval = analyze_number(SYNTHETIC_NUMBERS["us_valid_sample"], "US")
        risk_profile = RiskEngine.evaluate(norm_eval)
        has_score = (risk_profile["score"] is not None) and (0 <= risk_profile["score"] <= 100)
        has_factors = len(risk_profile.get("factors", [])) >= 0
        has_confidence = risk_profile.get("confidence") in ("HIGH", "MEDIUM", "LOW", "INSUFFICIENT")

        # Unknown handling
        inval_eval = analyze_number(SYNTHETIC_NUMBERS["invalid_country_code"])
        inval_risk = RiskEngine.evaluate(inval_eval)
        inval_ok = (inval_risk["risk_level"] == "UNKNOWN") or (inval_risk["confidence"] == "INSUFFICIENT")

        t5_ok = has_score and has_factors and has_confidence and inval_ok
        record_test("Transparent Risk Scoring & Confidence", t5_ok, f"Score: {risk_profile['score_display']}, Confidence: {risk_profile['confidence']}")
    except Exception as e:
        record_test("Transparent Risk Scoring", False, str(e))

    # Setup isolated test database for DB tests
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_db = Path(tmp_dir) / "test_evidence.db"
        test_backup = Path(tmp_dir) / "test_backup.db"
        test_csv = Path(tmp_dir) / "test_export.csv"

        # ── TEST 6: Evidence Creation with Unique Case ID ──
        try:
            init_db(test_db)
            analysis = analyze_number(SYNTHETIC_NUMBERS["us_valid_sample"], "US")
            risk = RiskEngine.evaluate(analysis)
            row_id, case_id = save_case(
                analysis, risk,
                platform="WhatsApp",
                notes="Synthetic test investigation note",
                category="Phishing Recon",
                tags="test,recon,sample",
                db_path=test_db,
            )
            t6_ok = (row_id > 0) and case_id.startswith("VY-")
            record_test("Evidence Creation & Unique Case ID", t6_ok, f"Saved Row #{row_id} with Case ID '{case_id}'.")
        except Exception as e:
            record_test("Evidence Creation", False, str(e))
            row_id, case_id = 1, "VY-TEST"

        # ── TEST 7: Evidence Retrieval, Search & Edit Notes ──
        try:
            fetched = get_case(row_id, db_path=test_db)
            search_res = search_cases("Synthetic test", db_path=test_db)
            edit_ok = update_case_notes(row_id, "Updated analyst conclusion.", new_tags="verified,closed", db_path=test_db)
            refetched = get_case(row_id, db_path=test_db)

            t7_ok = (fetched is not None) and (len(search_res) >= 1) and edit_ok and (refetched["notes"] == "Updated analyst conclusion.")
            record_test("Evidence Retrieval, Search & Note Editing", t7_ok, "Search by query and in-place note updates succeeded.")
        except Exception as e:
            record_test("Evidence Retrieval & Search", False, str(e))

        # ── TEST 8: CSV Export ──
        try:
            count, out_p = export_to_csv(destination=test_csv, db_path=test_db)
            with open(out_p, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                rows_csv = list(reader)
            t8_ok = (count == 1) and ("Case_ID" in header) and (len(rows_csv) == 1)
            record_test("CSV Export & Field Integrity", t8_ok, f"Exported {count} record(s) with {len(header)} standard columns.")
        except Exception as e:
            record_test("CSV Export", False, str(e))

        # ── TEST 9: Database Backup, Integrity & Restore ──
        try:
            bak_path = backup_database(dest_path=test_backup, src_path=test_db)
            int_ok, int_msg = check_integrity(bak_path)
            restore_ok, restore_msg = restore_database(bak_path, target_path=test_db)
            t9_ok = bak_path.exists() and int_ok and restore_ok
            record_test("Database Backup, Integrity & Restore", t9_ok, f"Integrity: {int_msg}, Live SQLite backup & restore verified.")
        except Exception as e:
            record_test("Database Backup & Restore", False, str(e))

        # ── TEST 10: GitHub Sync Safety & .gitignore Audit ──
        try:
            added_rules = ensure_gitignore_safety(Path(tmp_dir))
            audit = audit_sync_safety(Path(tmp_dir))
            # Verify sensitive extensions are classified as unsafe if present
            gi_content = (Path(tmp_dir) / ".gitignore").read_text()
            has_db_rule = "*.db" in gi_content and "*.csv" in gi_content
            t10_ok = has_db_rule and audit["is_safe"] is True
            record_test("GitHub Sync Safety & Leak Prevention", t10_ok, "Verified .gitignore rules for *.db, *.csv, and credentials.")
        except Exception as e:
            record_test("GitHub Sync Safety", False, str(e))

        # ── TEST 11: Deep OSINT Recon Engine & Footprint Matrix ──
        try:
            analysis_sample = analyze_number(SYNTHETIC_NUMBERS["in_synthetic_mobile"], "IN")
            recon_res = run_full_recon(analysis_sample)
            t11_ok = (
                recon_res.get("total_dorks_count", 0) > 30
                and recon_res.get("total_platforms_count", 0) > 5
                and len(recon_res.get("gov_dorks", [])) > 0
                and len(recon_res.get("email_dorks", [])) > 0
            )
            record_test(
                "Deep OSINT Recon Engine (Dorks, Gov, Email)",
                t11_ok,
                f"Generated {recon_res.get('total_dorks_count')} queries & {recon_res.get('total_platforms_count')} platforms."
            )
        except Exception as e:
            record_test("Deep OSINT Recon Engine", False, str(e))

        # ── TEST 12: SpiderFoot Correlation & Target Generation ──
        try:
            sf_targets = SpiderFootEngine.generate_targets(analysis_sample)
            t12_ok = (
                len(sf_targets.get("SIMULATED_MODULES", [])) >= 6
                and len(sf_targets.get("CORRELATED_QUERIES", [])) > 0
            )
            record_test(
                "SpiderFoot OSINT Module Matrix",
                t12_ok,
                f"Generated {len(sf_targets.get('SIMULATED_MODULES', []))} modules and target correlations."
            )
        except Exception as e:
            record_test("SpiderFoot OSINT Module Matrix", False, str(e))

        # ── TEST 13: Non-CVE Device Weakness Evaluation ──
        try:
            synthetic_evidence = {
                "props": {
                    "ro.adb.secure": "0",
                    "ro.build.type": "userdebug",
                    "ro.debuggable": "1",
                    "ro.boot.verifiedbootstate": "orange",
                    "ro.boot.veritymode": "disabled",
                    "ro.build.tags": "test-keys",
                    "ro.crypto.state": "unencrypted",
                    "ro.crypto.type": "",
                },
                "settings": {
                    "global.adb_enabled": "1",
                    "global.adb_wifi_enabled": "0",
                    "global.development_settings_enabled": "1",
                    "global.install_non_market_apps": "1",
                    "global.package_verifier_enable": "0",
                    "global.verifier_verify_adb_installs": "0",
                    "secure.install_non_market_apps": "",
                    "secure.lockscreen.disabled": "1",
                    "secure.enabled_accessibility_services": "",
                },
                "probes": {
                    "su_files": "/system/xbin/su",
                    "su_which": "/system/xbin/su",
                    "debuggable": "Package [com.demo] flags=DEBUGGABLE",
                    "providers": "",
                    "user_ca": "",
                    "device_policy": "",
                    "lock_state": "",
                    "backup": "Backup Manager is enabled",
                },
            }
            device_findings = evaluate_evidence(synthetic_evidence)
            exposed_names = {f["check"] for f in device_findings if f["status"] == "EXPOSED"}
            required = {
                "USB debugging (ADB)",
                "Debug build / debuggable system",
                "Root / su binaries",
                "Sideloading (unknown sources)",
                "Storage encryption",
            }
            t13_ok = required.issubset(exposed_names) and len(device_findings) >= 14
            record_test(
                "Non-CVE Device Weakness Engine",
                t13_ok,
                f"Evaluated {len(device_findings)} checks, detected {len(exposed_names)} exposed signals."
            )
        except Exception as e:
            record_test("Non-CVE Device Weakness Engine", False, str(e))

        # ── TEST 14: Spyware Scoring & Traffic Anomaly Engine ──
        try:
            dump = """
  Package [com.spy.example] (abc):
    versionName=3.1
    installerPackageName=
    flags=[ HAS_CODE ]
    requested permissions:
      android.permission.READ_SMS
      android.permission.RECEIVE_SMS
      android.permission.READ_CONTACTS
      android.permission.CAMERA
      android.permission.ACCESS_FINE_LOCATION
    install permissions:
      android.permission.INTERNET
  Package [com.chat.app] (def):
    versionName=2.0
    installerPackageName=com.android.vending
    flags=[ HAS_CODE ]
    requested permissions:
      android.permission.READ_CONTACTS
      android.permission.RECORD_AUDIO
      android.permission.CAMERA
"""
            parsed = parse_package_dump(dump)
            spy_score = score_package(parsed["com.spy.example"])
            chat_score = score_package(parsed["com.chat.app"])

            regular = detect_periodic([i * 30 for i in range(10)])
            irregular = detect_periodic([1, 4, 19, 55, 120, 300, 301, 900, 2000])

            def eth_udp_dns(qname: str, ts: float) -> bytes:
                dns = struct.pack("!HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
                for label in qname.split("."):
                    dns += bytes([len(label)]) + label.encode()
                dns += b"\x00" + struct.pack("!HH", 1, 1)
                udp = struct.pack("!HHHH", 5353, 53, 8 + len(dns), 0) + dns
                ip = struct.pack(
                    "!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), 0, 0, 64, 17, 0,
                    socket.inet_aton("192.168.1.10"), socket.inet_aton("9.9.9.9")
                ) + udp
                frame = b"\x00" * 12 + struct.pack("!H", 0x0800) + ip
                return struct.pack("<IIII", int(ts), int((ts % 1) * 1e6), len(frame), len(frame)) + frame

            def eth_tcp_syn(dst: str, port: int, ts: float) -> bytes:
                tcp = struct.pack("!HHIIBBHHH", 40000, port, 0, 0, 0x50, 0x02, 8192, 0, 0)
                ip = struct.pack(
                    "!BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp), 0, 0, 64, 6, 0,
                    socket.inet_aton("192.168.1.10"), socket.inet_aton(dst)
                ) + tcp
                frame = b"\x00" * 12 + struct.pack("!H", 0x0800) + ip
                return struct.pack("<IIII", int(ts), int((ts % 1) * 1e6), len(frame), len(frame)) + frame

            capture = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
            capture += eth_udp_dns("aGVsbG8xMjM0NTY3ODkwYWJjZGVmLmV2aWwuY29t", 1000.0)
            for i in range(10):
                capture += eth_tcp_syn("203.0.113.9", 8443, 2000 + i * 30)
            capture_path = Path(tmp_dir) / "synthetic.pcap"
            capture_path.write_bytes(capture)

            traffic = analyze_traffic(read_pcap(capture_path))
            t14_ok = (
                spy_score["level"] == "HIGH"
                and spy_score["score"] >= 12
                and chat_score["level"] != "HIGH"
                and regular is not None
                and irregular is None
                and len(traffic["beacons"]) >= 1
                and len(traffic["suspect_dns_labels"]) >= 1
            )
            record_test(
                "Spyware Scoring & Traffic Anomaly Engine",
                t14_ok,
                f"Spy package {spy_score['score']} ({spy_score['level']}), "
                f"{len(traffic['beacons'])} beacon(s), {traffic['packets']} packets parsed."
            )
        except Exception as e:
            record_test("Spyware Scoring & Traffic Anomaly Engine", False, str(e))

    # Print Report Summary Table
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = total - passed_count

    print(f"  {C.DR}┌{'─'*4}┬{'─'*42}┬{'─'*10}┐{C.RST}")
    print(f"  {C.DR}│{C.W}{C.B} #  {C.DR}│{C.W} TEST MODULE                             {C.DR}│{C.W} RESULT   {C.DR}│{C.RST}")
    print(f"  {C.DR}├{'─'*4}┼{'─'*42}┼{'─'*10}┤{C.RST}")

    for idx, r in enumerate(results, start=1):
        status_sym = f"{C.G}✔ PASS{C.RST}" if r["passed"] else f"{C.R}✘ FAIL{C.RST}"
        name_str = r["name"][:40]
        print(f"  {C.DR}│{C.W}{idx:>2}  "
              f"{C.DR}│ {C.W}{name_str:<40}{C.RST} "
              f"{C.DR}│ {status_sym:<8} {C.DR}│{C.RST}")
        if not r["passed"]:
            print(f"  {C.DR}│    │   {C.R}Error: {r['detail'][:36]}{C.RST}   {C.DR}│          │{C.RST}")

    print(f"  {C.DR}└{'─'*4}┴{'─'*42}┴{'─'*10}┘{C.RST}\n")

    if failed_count == 0:
        print(f"  {C.G}✅ ALL {total} SYSTEM TESTS PASSED PERFECTLY.{C.RST}")
        print(f"  {C.CN}⚡ VirgoYT OSINT Toolkit v{VERSION} is operating at 100% integrity.{C.RST}\n")
    else:
        print(f"  {C.R}❌ {failed_count} TEST(S) FAILED. Review details above.{C.RST}\n")

    return {
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "details": results,
    }

if __name__ == "__main__":
    run_all_tests()
