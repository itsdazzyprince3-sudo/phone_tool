"""
device_audit.py — Android Device Audit & Extraction Engine
VirgoYT OSINT Toolkit v5.0
Developer Credit: VIRGOYT707

Runs against a device you own or are explicitly authorized to assess.
Requires Android Platform Tools (`adb`) and an unlocked device with the
RSA debugging prompt accepted.
"""

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import C, EXPORT_DIR, prompt, sep

ADB_TIMEOUT = 30
SHELL_TIMEOUT = 60

SETTINGS_KEYS = [
    ("global", "adb_enabled"),
    ("global", "adb_wifi_enabled"),
    ("global", "development_settings_enabled"),
    ("global", "install_non_market_apps"),
    ("global", "package_verifier_enable"),
    ("global", "verifier_verify_adb_installs"),
    ("secure", "install_non_market_apps"),
    ("secure", "lockscreen.disabled"),
    ("secure", "enabled_accessibility_services"),
]

SHELL_PROBES = {
    "su_files": "ls /system/bin/su /system/xbin/su /sbin/su /su 2>/dev/null",
    "su_which": "which su 2>/dev/null",
    "debuggable": "dumpsys package packages | grep -B1 DEBUGGABLE | head -40",
    "providers": "dumpsys activity providers | grep -i 'exported=true' | head -30",
    "user_ca": "ls /data/misc/user/0/cacerts-added 2>/dev/null",
    "device_policy": "dumpsys device_policy | grep -iE 'admin=|Active admin' | head -20",
    "lock_state": "dumpsys trust | grep -m2 -i 'deviceLocked'",
    "backup": "bmgr enabled 2>/dev/null",
}

EXTRACTION_TARGETS = [
    ("props", "getprop", 30),
    ("settings_global", "settings list global", 30),
    ("settings_secure", "settings list secure", 30),
    ("settings_system", "settings list system", 30),
    ("packages_all", "pm list packages -f", 45),
    ("packages_third_party", "pm list packages -3", 30),
    ("accounts", "dumpsys account | head -200", 45),
    ("battery", "dumpsys battery", 30),
    ("connectivity", "dumpsys connectivity | head -300", 45),
    ("wifi", "dumpsys wifi | head -500", 60),
    ("telephony", "dumpsys telephony.registry | head -300", 45),
    ("location", "dumpsys location | head -300", 45),
    ("bluetooth", "dumpsys bluetooth_manager | head -200", 45),
    ("device_policy", "dumpsys device_policy | head -200", 45),
    ("storage", "df -h", 30),
    ("network_interfaces", "ip addr", 30),
    ("routes", "ip route", 30),
    ("processes", "ps -A", 45),
    ("sdcard_listing", "ls -la /sdcard", 30),
    ("sim_contacts", "content query --uri content://icc/adn", 45),
    ("contacts", "content query --uri content://com.android.contacts/data/phones --projection display_name:data1", 45),
    ("sms", "content query --uri content://sms --projection address:date:body", 45),
    ("call_log", "content query --uri content://call_log/calls --projection number:date:duration:type", 45),
]


def tool_ready() -> Tuple[bool, str]:
    """Confirm the adb binary is installed."""
    exe = shutil.which("adb")
    if not exe:
        return False, "adb not found — install with: pkg install android-tools"
    return True, exe


def run_adb(args: List[str], serial: Optional[str] = None, timeout: int = ADB_TIMEOUT) -> Tuple[int, str, str]:
    """Execute an adb subcommand and capture stdout/stderr without raising."""
    exe = shutil.which("adb")
    if not exe:
        return 127, "", "adb not found"
    cmd = [exe]
    if serial:
        cmd += ["-s", serial]
    cmd += args
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except OSError as exc:
        return 1, "", str(exc)


def shell(serial: str, command: str, timeout: int = SHELL_TIMEOUT) -> Tuple[int, str, str]:
    """Run a shell pipeline on the target device."""
    return run_adb(["shell", command], serial=serial, timeout=timeout)


def list_devices() -> List[Dict[str, str]]:
    """Parse `adb devices -l` into structured records."""
    rc, out, err = run_adb(["devices", "-l"])
    devices: List[Dict[str, str]] = []
    if rc != 0:
        return devices
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices") or line.startswith("*"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        record: Dict[str, str] = {"serial": parts[0], "state": parts[1]}
        for token in parts[2:]:
            if ":" in token:
                key, value = token.split(":", 1)
                record[key] = value
        devices.append(record)
    return devices


def select_device() -> Optional[str]:
    """Prompt for a connected device and return its serial."""
    devices = list_devices()
    if not devices:
        print(f"  {C.R}❌ No devices detected.{C.RST}")
        print(f"  {C.D}  1. Enable Developer Options → USB debugging (or Wireless debugging).{C.RST}")
        print(f"  {C.D}  2. Connect the cable and accept the RSA fingerprint prompt on the phone.{C.RST}")
        print(f"  {C.D}  3. Wireless: run option [6] and pair with the on-screen code.{C.RST}\n")
        return None

    print(f"\n  {C.CN}Connected devices:{C.RST}")
    for idx, dev in enumerate(devices, start=1):
        model = dev.get("model", "unknown").replace("_", " ")
        tag = f"{C.G}ready{C.RST}" if dev["state"] == "device" else f"{C.Y}{dev['state']}{C.RST}"
        print(f"  [{idx}] {dev['serial']}  {C.W}{model}{C.RST}  ({tag})")
    choice = prompt("SELECT DEVICE NUMBER [1]") or "1"
    if not choice.isdigit() or not (1 <= int(choice) <= len(devices)):
        print(f"  {C.R}❌ Invalid device selection.{C.RST}\n")
        return None

    serial = devices[int(choice) - 1]["serial"]
    state = devices[int(choice) - 1]["state"]
    if state != "device":
        print(f"  {C.Y}⚠ Device is '{state}'. Accept the RSA prompt on the phone, then retry.{C.RST}\n")
        return None
    return serial


def prop_map(serial: str) -> Dict[str, str]:
    """Read the full Android property table."""
    rc, out, _ = shell(serial, "getprop", timeout=30)
    props: Dict[str, str] = {}
    if rc != 0:
        return props
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("[") and "]:" in line:
            key, value = line.split("]: [", 1)
            props[key.lstrip("[")] = value.rstrip("]")
    return props


def read_setting(serial: str, scope: str, key: str) -> str:
    """Read one settings key, normalising null to empty."""
    rc, out, _ = shell(serial, f"settings get {scope} {key}", timeout=20)
    value = out.strip()
    return "" if rc != 0 or value in ("", "null") else value


def collect_evidence(serial: str) -> Dict[str, Any]:
    """Gather every value the config audit evaluates."""
    props = prop_map(serial)
    settings: Dict[str, str] = {}
    for scope, key in SETTINGS_KEYS:
        settings[f"{scope}.{key}"] = read_setting(serial, scope, key)

    probes: Dict[str, str] = {}
    for name, command in SHELL_PROBES.items():
        rc, out, _ = shell(serial, command, timeout=45)
        probes[name] = out.strip() if rc == 0 else ""

    return {"props": props, "settings": settings, "probes": probes}


def _finding(check: str, severity: str, exposed: bool, evidence: str,
             exposure: str, hardening: str) -> Dict[str, str]:
    return {
        "check": check,
        "severity": severity,
        "status": "EXPOSED" if exposed else "OK",
        "evidence": evidence.strip() or "no signal",
        "exposure": exposure,
        "hardening": hardening,
    }


def _unknown(check: str, severity: str, evidence: str, exposure: str) -> Dict[str, str]:
    return {
        "check": check,
        "severity": severity,
        "status": "UNKNOWN",
        "evidence": evidence.strip() or "no signal",
        "exposure": exposure,
        "hardening": "Inspect manually on the device.",
    }


def evaluate_evidence(evidence: Dict[str, Any]) -> List[Dict[str, str]]:
    """Turn raw evidence into a ranked list of non-CVE weakness findings."""
    props = evidence.get("props", {})
    settings = evidence.get("settings", {})
    probes = evidence.get("probes", {})

    def p(key: str) -> str:
        return props.get(key, "")

    def s(key: str) -> str:
        return settings.get(key, "")

    findings: List[Dict[str, str]] = []

    adb_on = s("global.adb_enabled") == "1"
    adb_secure = p("ro.adb.secure") == "1"
    findings.append(_finding(
        "USB debugging (ADB)",
        "HIGH" if adb_on and not adb_secure else "MEDIUM",
        adb_on,
        f"adb_enabled={s('global.adb_enabled') or 'unset'}, ro.adb.secure={p('ro.adb.secure') or 'unset'}",
        "An attached host can install packages, read app data on debuggable builds, dump settings and drive the UI.",
        "Disable USB debugging when not in use and keep ro.adb.secure=1 (RSA authorization enforced).",
    ))

    wl_port = p("service.adb.tcp.port") or p("persist.adb.tcp.port")
    wl_on = s("global.adb_wifi_enabled") == "1" or (wl_port not in ("", "-1", "0"))
    findings.append(_finding(
        "Wireless debugging",
        "HIGH",
        wl_on,
        f"adb_wifi_enabled={s('global.adb_wifi_enabled') or 'unset'}, tcp.port={wl_port or 'unset'}",
        "ADB is reachable over the local network; anyone who can route to the port inherits the debugging channel.",
        "Turn wireless debugging off after pairing and avoid debugging on untrusted networks.",
    ))

    build_type = p("ro.build.type")
    debug_build = build_type in ("userdebug", "eng") or p("ro.debuggable") == "1"
    findings.append(_finding(
        "Debug build / debuggable system",
        "HIGH",
        debug_build,
        f"ro.build.type={build_type or 'unset'}, ro.debuggable={p('ro.debuggable') or 'unset'}",
        "Debug builds expose root adbd, verbose logs and unrestricted app debugging.",
        "Run a production `user` build on any device holding real data.",
    ))

    boot_state = p("ro.boot.verifiedbootstate")
    verity = p("ro.boot.veritymode")
    boot_bad = boot_state in ("orange", "red", "yellow") or verity.lower() in ("disabled", "logging")
    findings.append(_finding(
        "Verified boot / dm-verity",
        "MEDIUM",
        boot_bad,
        f"verifiedbootstate={boot_state or 'unset'}, veritymode={verity or 'unset'}",
        "Boot chain or system partition integrity is not enforcing, so persistent tampering is harder to detect.",
        "Relock the bootloader and restore stock signed images.",
    ))

    su_files = probes.get("su_files", "")
    su_which = probes.get("su_which", "")
    test_keys = "test-keys" in p("ro.build.tags")
    rooted = bool(su_files) or bool(su_which) or test_keys
    findings.append(_finding(
        "Root / su binaries",
        "HIGH",
        rooted,
        f"su files={su_files or 'none'}, which su={su_which or 'none'}, tags={p('ro.build.tags') or 'unset'}",
        "A local su surface lets any process that reaches it cross app sandboxes and read protected stores.",
        "Remove root, restore stock boot image, keep the bootloader locked.",
    ))

    lock_disabled = s("secure.lockscreen.disabled") == "1"
    lock_probe = probes.get("lock_state", "")
    lock_weak = lock_disabled or "deviceLocked=true" in lock_probe
    findings.append(_finding(
        "Screen lock state",
        "MEDIUM",
        lock_weak,
        f"lockscreen.disabled={s('secure.lockscreen.disabled') or 'unset'}, trust={lock_probe or 'unset'}",
        "Without a lock the debugging channel and storage are usable by whoever holds the device.",
        "Enforce a PIN or biometric lock and a short lock timeout.",
    ))

    dev_options = s("global.development_settings_enabled") == "1"
    findings.append(_finding(
        "Developer options",
        "LOW",
        dev_options,
        f"development_settings_enabled={s('global.development_settings_enabled') or 'unset'}",
        "Developer options widen the attack surface: GPU debug, mock locations, layout inspection, ADB.",
        "Leave developer options off on daily drivers.",
    ))

    unknown_src = s("global.install_non_market_apps") == "1" or s("secure.install_non_market_apps") == "1"
    findings.append(_finding(
        "Sideloading (unknown sources)",
        "MEDIUM",
        unknown_src,
        f"global={s('global.install_non_market_apps') or 'unset'}, secure={s('secure.install_non_market_apps') or 'unset'}",
        "Sideloaded APKs bypass store review and are the usual delivery path for stalkerware and banking droppers.",
        "Disable unknown sources and install only through a vetted store profile.",
    ))

    verifier_off = s("global.package_verifier_enable") == "0"
    adb_unverified = s("global.verifier_verify_adb_installs") == "0"
    findings.append(_finding(
        "Package verifier disabled",
        "MEDIUM",
        verifier_off or adb_unverified,
        f"package_verifier_enable={s('global.package_verifier_enable') or 'unset'}, verify_adb_installs={s('global.verifier_verify_adb_installs') or 'unset'}",
        "Installs proceed without Play Protect style verification, so known-bad APKs land silently.",
        "Re-enable package and ADB install verification.",
    ))

    debuggable_out = probes.get("debuggable", "")
    findings.append(_finding(
        "Debuggable installed apps",
        "HIGH",
        bool(debuggable_out),
        debuggable_out.replace("\n", " | ")[:400] or "none found",
        "`run-as` against a debuggable app reads its private data directory without root.",
        "Ship release builds with android:debuggable=\"false\".",
    ))

    provider_out = probes.get("providers", "")
    findings.append(_finding(
        "Exported content providers",
        "MEDIUM",
        bool(provider_out),
        provider_out.replace("\n", " | ")[:400] or "none found",
        "World-exported providers can answer queries the UI would never ask.",
        "Set android:exported=\"false\" unless the component serves other apps.",
    ))

    accessibility = s("secure.enabled_accessibility_services")
    findings.append(_finding(
        "Accessibility services enabled",
        "HIGH",
        bool(accessibility),
        accessibility[:300] or "none",
        "Accessibility implies screen reading, keystroke observation and UI automation across apps.",
        "Keep only services you personally installed and audited.",
    ))

    policy_out = probes.get("device_policy", "")
    findings.append(_finding(
        "Active device administrators",
        "MEDIUM",
        bool(policy_out),
        policy_out.replace("\n", " | ")[:300] or "none found",
        "A device admin can wipe, lock and alter policy; a hostile admin is persistence.",
        "Audit active admins and revoke unknown ones.",
    ))

    crypto = p("ro.crypto.state").lower()
    findings.append(_finding(
        "Storage encryption",
        "HIGH",
        crypto not in ("", "encrypted"),
        f"ro.crypto.state={p('ro.crypto.state') or 'unset'}, ro.crypto.type={p('ro.crypto.type') or 'unset'}",
        "Unencrypted userdata is readable from recovery or an offline image.",
        "Enable file-based encryption and require credentials at boot.",
    ))

    user_ca = probes.get("user_ca", "")
    findings.append(_finding(
        "User-installed CA certificates",
        "MEDIUM",
        bool(user_ca),
        user_ca.replace("\n", " | ")[:300] or "none",
        "A trusted user CA lets whoever installed it intercept TLS for any app that accepts user roots.",
        "Remove unknown user certificates; pin certificates in sensitive apps.",
    ))

    backup_enabled = "enabled" in probes.get("backup", "").lower()
    findings.append(_finding(
        "ADB backup channel",
        "MEDIUM",
        backup_enabled,
        probes.get("backup") or "unset",
        "A live adb backup channel can pull app data and shared storage in one archive.",
        "Disable backup transport on managed devices.",
    ))

    return findings


def get_fingerprint(serial: str) -> Dict[str, str]:
    """Collect identifying device and build metadata."""
    props = prop_map(serial)
    rc, accounts, _ = shell(serial, "dumpsys account | grep -E 'Account \\{|type=' | head -40", timeout=30)
    rc, pkg_count, _ = shell(serial, "pm list packages | wc -l", timeout=30)
    rc, ip_addr, _ = shell(serial, "ip route get 1.1.1.1 2>/dev/null | head -1", timeout=20)

    return {
        "serial": serial,
        "manufacturer": props.get("ro.product.manufacturer", ""),
        "brand": props.get("ro.product.brand", ""),
        "model": props.get("ro.product.model", ""),
        "device": props.get("ro.product.device", ""),
        "android_version": props.get("ro.build.version.release", ""),
        "sdk": props.get("ro.build.version.sdk", ""),
        "security_patch": props.get("ro.build.version.security_patch", ""),
        "build_id": props.get("ro.build.id", ""),
        "build_type": props.get("ro.build.type", ""),
        "build_tags": props.get("ro.build.tags", ""),
        "fingerprint": props.get("ro.build.fingerprint", ""),
        "bootloader": props.get("ro.bootloader", ""),
        "baseband": props.get("gsm.version.baseband", ""),
        "sim_operator": props.get("gsm.sim.operator.alpha", ""),
        "network_operator": props.get("gsm.operator.alpha", ""),
        "sim_country": props.get("gsm.sim.operator.iso-country", ""),
        "android_id": props.get("ro.serialno", ""),
        "boot_verified": props.get("ro.boot.verifiedbootstate", ""),
        "selinux": "",
        "accounts": accounts.strip()[:4000],
        "installed_packages": pkg_count.strip(),
        "local_ip": ip_addr.strip(),
    }


def print_fingerprint(fp: Dict[str, str]) -> None:
    """Render the fingerprint card."""
    sep()
    print(f"  {C.CN}📱 DEVICE FINGERPRINT{C.RST}")
    sep()
    rows = [
        ("Serial", fp.get("serial")),
        ("Manufacturer", fp.get("manufacturer")),
        ("Brand / Model", f"{fp.get('brand')} / {fp.get('model')}"),
        ("Device", fp.get("device")),
        ("Android", f"{fp.get('android_version')} (SDK {fp.get('sdk')})"),
        ("Security Patch", fp.get("security_patch")),
        ("Build", f"{fp.get('build_id')} [{fp.get('build_type')}] {fp.get('build_tags')}"),
        ("Verified Boot", fp.get("boot_verified")),
        ("Bootloader", fp.get("bootloader")),
        ("Baseband", fp.get("baseband")),
        ("SIM Operator", fp.get("sim_operator")),
        ("Network Operator", fp.get("network_operator")),
        ("Packages", fp.get("installed_packages")),
        ("Local IP", fp.get("local_ip")),
        ("Fingerprint", fp.get("fingerprint")),
    ]
    for label, value in rows:
        print(f"  {C.DW}{label:<18}:{C.RST} {value or '—'}")
    if fp.get("accounts"):
        print(f"  {C.DW}{'Accounts':<18}:{C.RST}")
        for line in fp["accounts"].splitlines()[:12]:
            print(f"      {C.D}{line.strip()}{C.RST}")
    print()


def print_findings(findings: List[Dict[str, str]]) -> None:
    """Render the weakness table, exposed items first."""
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    ranked = sorted(findings, key=lambda f: (f["status"] != "EXPOSED", order.get(f["severity"], 9)))
    exposed = [f for f in findings if f["status"] == "EXPOSED"]

    sep()
    print(f"  {C.CN}🛡️  NON-CVE WEAKNESS AUDIT{C.RST}")
    sep()
    print(f"  {C.D}Checks are configuration weaknesses, not version-bound CVEs.{C.RST}\n")

    severity_color = {"CRITICAL": C.R, "HIGH": C.R, "MEDIUM": C.Y, "LOW": C.CN, "INFO": C.D}
    for item in ranked:
        if item["status"] == "OK":
            continue
        color = severity_color.get(item["severity"], C.W)
        print(f"  {color}[{item['severity']:<8}]{C.RST} {C.W}{item['check']}{C.RST}")
        print(f"      {C.D}evidence :{C.RST} {item['evidence']}")
        print(f"      {C.D}exposure :{C.RST} {item['exposure']}")
        print(f"      {C.D}hardening:{C.RST} {item['hardening']}")
        print()

    if not exposed:
        print(f"  {C.G}✅ No exposed configuration weaknesses matched on this device.{C.RST}\n")
    else:
        print(f"  {C.Y}⚠ {len(exposed)} exposed signal(s). Each is a configuration weakness, not a CVE.{C.RST}\n")


def extract_all(serial: str) -> Path:
    """Pull every readable artifact into a timestamped case folder."""
    stamp = time.strftime("%Y%m%d_%H%M%S")
    safe_serial = "".join(ch for ch in serial if ch.isalnum() or ch in "-_")[:24] or "device"
    out_dir = EXPORT_DIR / f"device_{safe_serial}_{stamp}"
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest: List[Dict[str, Any]] = []
    for name, command, timeout in EXTRACTION_TARGETS:
        started = time.time()
        rc, out, err = shell(serial, command, timeout=timeout)
        target = raw_dir / f"{name}.txt"
        body = out if out.strip() else (err or "[no output]")
        target.write_text(body, encoding="utf-8", errors="replace")
        manifest.append({
            "artifact": name,
            "command": command,
            "returncode": rc,
            "bytes": target.stat().st_size,
            "elapsed_ms": int((time.time() - started) * 1000),
            "restricted": "SecurityException" in body or "Permission Denial" in body,
        })
        state = f"{C.G}ok{C.RST}" if rc == 0 and target.stat().st_size > 0 else f"{C.Y}partial{C.RST}"
        print(f"  {state:<14} {C.DW}{name:<22}{C.RST} {C.D}{target.stat().st_size} bytes{C.RST}")

    fp = get_fingerprint(serial)
    (out_dir / "device_fingerprint.json").write_text(json.dumps(fp, indent=2), encoding="utf-8")

    findings = evaluate_evidence(collect_evidence(serial))
    (out_dir / "weakness_report.json").write_text(json.dumps(findings, indent=2), encoding="utf-8")

    lines = [f"VirgoYT device audit — {serial} — {stamp}", ""]
    for item in findings:
        lines.append(f"[{item['status']:<7}] {item['severity']:<8} {item['check']}")
        lines.append(f"    evidence : {item['evidence']}")
        lines.append(f"    exposure : {item['exposure']}")
        lines.append(f"    hardening: {item['hardening']}")
    (out_dir / "weakness_report.txt").write_text("\n".join(lines), encoding="utf-8")

    (out_dir / "manifest.json").write_text(json.dumps({
        "serial": serial,
        "captured_at": stamp,
        "artifacts": manifest,
    }, indent=2), encoding="utf-8")

    return out_dir


def adb_backup(serial: str, out_dir: Optional[Path] = None) -> Tuple[bool, str, Optional[Path]]:
    """Run a legacy adb backup; the phone must confirm the operation."""
    stamp = time.strftime("%Y%m%d_%H%M%S")
    target_dir = out_dir or (EXPORT_DIR / f"device_backup_{stamp}")
    target_dir.mkdir(parents=True, exist_ok=True)
    archive = target_dir / "backup.ab"

    print(f"  {C.Y}⚠ Unlock the phone and press 'Back up my data' when prompted.{C.RST}")
    rc, out, err = run_adb(
        ["backup", "-apk", "-shared", "-all", "-f", str(archive)],
        serial=serial,
        timeout=600,
    )
    if rc != 0 or not archive.exists() or archive.stat().st_size == 0:
        return False, (err or out or "backup produced no archive").strip(), None
    return True, f"{archive.stat().st_size} bytes", archive


def connect_wireless() -> Optional[str]:
    """Pair or connect to a wireless debugging endpoint."""
    endpoint = prompt("WIRELESS ADB TARGET (host:port)")
    if not endpoint:
        return None
    if ":" not in endpoint:
        endpoint = f"{endpoint}:5555"

    pair_code = prompt("PAIRING CODE (Enter to skip pairing)")
    if pair_code:
        pair_port = prompt("PAIRING PORT") or "0"
        rc, out, err = run_adb(["pair", f"{endpoint.split(':')[0]}:{pair_port}", pair_code], timeout=60)
        print(f"  {C.D}{out.strip() or err.strip()}{C.RST}")

    rc, out, err = run_adb(["connect", endpoint], timeout=30)
    print(f"  {C.D}{out.strip() or err.strip()}{C.RST}")
    return endpoint if "connected" in out.lower() else None


def run_device_audit() -> None:
    """Interactive device audit and extraction console."""
    print()
    sep()
    print(f"  {C.R}📱 VIRGOYT DEVICE AUDIT & EXTRACTION{C.RST}")
    print(f"  {C.D}Scope: devices you own or have written authorization to assess.{C.RST}")
    sep()

    ok, message = tool_ready()
    if not ok:
        print(f"  {C.R}❌ {message}{C.RST}\n")
        return

    serial = select_device()
    if not serial:
        return

    while True:
        print(f"  {C.DR}┌{'─'*54}┐{C.RST}")
        print(f"  {C.DR}│{C.RST} {C.W}Target: {serial:<44}{C.RST} {C.DR}│{C.RST}")
        print(f"  {C.DR}├{'─'*54}┤{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[1]{C.RST} Quick fingerprint                                  {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[2]{C.RST} Non-CVE weakness audit                             {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[3]{C.RST} Extract all readable data                          {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[4]{C.RST} ADB backup archive                                  {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[5]{C.RST} Full run (fingerprint + audit + extract)            {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[6]{C.RST} Connect wireless ADB                                {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[0]{C.RST} Back to main menu                                   {C.DR}│{C.RST}")
        print(f"  {C.DR}└{'─'*54}┘{C.RST}")

        action = prompt("SELECT DEVICE ACTION [0]") or "0"

        if action == "0":
            return
        if action == "1":
            print_fingerprint(get_fingerprint(serial))
        elif action == "2":
            findings = evaluate_evidence(collect_evidence(serial))
            print_findings(findings)
        elif action == "3":
            print()
            out_dir = extract_all(serial)
            print(f"\n  {C.G}✅ Artifacts written to {out_dir}{C.RST}\n")
        elif action == "4":
            ok_b, detail, archive = adb_backup(serial)
            if ok_b and archive:
                print(f"  {C.G}✅ Backup written: {archive} ({detail}){C.RST}\n")
            else:
                print(f"  {C.R}❌ Backup failed or was declined: {detail}{C.RST}\n")
        elif action == "5":
            print_fingerprint(get_fingerprint(serial))
            findings = evaluate_evidence(collect_evidence(serial))
            print_findings(findings)
            out_dir = extract_all(serial)
            print(f"\n  {C.G}✅ Full case folder: {out_dir}{C.RST}\n")
        elif action == "6":
            target = connect_wireless()
            if target:
                serial = target
                print(f"  {C.G}✅ Connected to {serial}{C.RST}\n")
        else:
            print(f"  {C.R}❌ Invalid selection.{C.RST}\n")
