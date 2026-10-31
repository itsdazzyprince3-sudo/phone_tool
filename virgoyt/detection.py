"""
detection.py — Monitoring, Spyware & Traffic Anomaly Detection Engine
VirgoYT OSINT Toolkit v5.0
Developer Credit: VIRGOYT707

Runs against a device you own or are explicitly authorized to assess.
Detection is heuristic: a high score is a signal to investigate, not proof.
"""

import json
import math
import re
import socket
import struct
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import C, EXPORT_DIR, prompt, sep
from .device_audit import read_setting, select_device, shell

SURVEILLANCE_PERMS = {
    "android.permission.READ_SMS": 3,
    "android.permission.RECEIVE_SMS": 2,
    "android.permission.READ_CALL_LOG": 2,
    "android.permission.READ_CONTACTS": 1,
    "android.permission.RECORD_AUDIO": 2,
    "android.permission.CAMERA": 1,
    "android.permission.ACCESS_FINE_LOCATION": 1,
    "android.permission.ACCESS_BACKGROUND_LOCATION": 2,
}

EXTRA_PERMS = {
    "android.permission.SYSTEM_ALERT_WINDOW": (3, "overlay windows over other apps"),
    "android.permission.REQUEST_INSTALL_PACKAGES": (3, "can install other APKs"),
    "android.permission.PACKAGE_USAGE_STATS": (2, "reads app usage history"),
    "android.permission.BIND_ACCESSIBILITY_SERVICE": (5, "declares an accessibility service"),
    "android.permission.BIND_DEVICE_ADMIN": (5, "declares a device admin"),
    "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE": (4, "reads every notification"),
    "android.permission.MANAGE_EXTERNAL_STORAGE": (2, "broad shared-storage access"),
    "android.permission.READ_PHONE_STATE": (1, "reads telephony state"),
    "android.permission.READ_PHONE_NUMBERS": (1, "reads the subscriber number"),
    "android.permission.PROCESS_OUTGOING_CALLS": (1, "observes outgoing calls"),
    "android.permission.ANSWER_PHONE_CALLS": (2, "answers calls silently"),
    "android.permission.CALL_PHONE": (1, "places calls"),
    "android.permission.QUERY_ALL_PACKAGES": (1, "enumerates every installed app"),
    "android.permission.RECEIVE_BOOT_COMPLETED": (1, "starts at boot"),
    "android.permission.SEND_SMS": (2, "sends SMS"),
    "android.permission.WRITE_CALL_LOG": (2, "modifies the call log"),
}

MONITORING_KEYWORDS = {
    "mspy": 10, "flexispy": 10, "hoverwatch": 10, "spyera": 10, "cocospy": 10,
    "spyzie": 10, "thetruthspy": 10, "mobistealth": 10, "xnspy": 10, "kidsguard": 9,
    "qustodio": 8, "umobix": 9, "eyezy": 9, "spyic": 9, "minspy": 9, "neospy": 9,
    "phonesheriff": 9, "highster": 9, "spyphone": 9, "spybubble": 9, "trackmyfone": 9,
    "pumpic": 9, "spy24": 9, "stealthgenie": 9, "mspy": 10, "cerberus": 5,
    "keylog": 7, "stalker": 7, "spyware": 8, "stealth": 5, "hiddenapp": 6,
    "monitor": 3, "tracker": 3, "spy": 6, "secret": 3, "watcher": 5,
}

DANGEROUS_NOTES = {
    "ACCESSIBILITY": "An enabled accessibility service can read screens and simulate taps across every app.",
    "NOTIFICATION": "A notification listener reads every notification, including OTP and message previews.",
    "DEVICE_ADMIN": "A device admin can lock, wipe and change policy without the app being visible.",
    "VPN": "A local VPN service sees all device traffic unless the app is trusted.",
    "OVERLAY": "Draw-over-other-apps is the classic credential-overlay primitive.",
}

PCAP_MAGICS = {
    b"\xd4\xc3\xb2\xa1": ("<", 1e6),
    b"\xa1\xb2\xc3\xd4": (">", 1e6),
    b"\x4d\x3c\xb2\xa1": ("<", 1e9),
    b"\xa1\xb2\x3c\x4d": (">", 1e9),
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PACKAGE + PERMISSION ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_package_dump(text: str) -> Dict[str, Dict[str, Any]]:
    """Parse `dumpsys package` into per-package records."""
    packages: Dict[str, Dict[str, Any]] = {}
    current: Optional[Dict[str, Any]] = None
    in_requested = False

    for raw in text.splitlines():
        header = re.match(r"^\s*Package \[([^\]]+)\]", raw)
        if header:
            name = header.group(1)
            current = {"name": name, "permissions": [], "flags": "", "installer": "",
                       "version": "", "target_sdk": "", "debuggable": False}
            packages[name] = current
            in_requested = False
            continue

        if current is None:
            continue

        stripped = raw.strip()
        if stripped == "requested permissions:":
            in_requested = True
            continue
        if in_requested:
            if re.match(r"^[A-Za-z].*permissions:$", stripped) or stripped.startswith("User "):
                in_requested = False
            elif re.match(r"^[a-zA-Z][\w.]*$", stripped):
                current["permissions"].append(stripped)
                continue

        for key, field in (("versionName=", "version"), ("installerPackageName=", "installer"),
                           ("targetSdk=", "target_sdk")):
            if key in stripped and not current[field]:
                tail = stripped.split(key, 1)[1].split()
                current[field] = tail[0] if tail else ""

        if stripped.startswith("flags=["):
            current["flags"] = stripped
            if "DEBUGGABLE" in stripped:
                current["debuggable"] = True

    return packages


def score_package(package: Dict[str, Any]) -> Dict[str, Any]:
    """Score one package's declared surface for monitoring behaviour."""
    name = package.get("name", "")
    perms = set(package.get("permissions", []))
    score = 0
    signals: List[str] = []

    for permission, weight in SURVEILLANCE_PERMS.items():
        if permission in perms:
            score += weight
            signals.append(f"{permission.rsplit('.', 1)[-1]} (+{weight})")

    combo_core = {"android.permission.READ_SMS", "android.permission.READ_CONTACTS"}
    combo_media = {"android.permission.RECORD_AUDIO", "android.permission.CAMERA"}
    if combo_core <= perms and (combo_media & perms):
        score += 6
        signals.append("surveillance permission cluster (+6)")

    for permission, (weight, note) in EXTRA_PERMS.items():
        if permission in perms:
            score += weight
            signals.append(f"{note} (+{weight})")

    lowered = name.lower()
    for keyword, weight in MONITORING_KEYWORDS.items():
        if keyword in lowered:
            score += weight
            signals.append(f"package name matches '{keyword}' (+{weight})")
            break

    if package.get("installer") == "" and "SYSTEM" not in package.get("flags", ""):
        score += 2
        signals.append("no installer record — possible sideload (+2)")

    if package.get("debuggable"):
        score += 3
        signals.append("debuggable package (+3)")

    if score >= 12:
        level = "HIGH"
    elif score >= 7:
        level = "MEDIUM"
    elif score >= 4:
        level = "LOW"
    else:
        level = "INFO"

    return {
        "name": name,
        "score": score,
        "level": level,
        "signals": signals,
        "installer": package.get("installer", ""),
        "version": package.get("version", ""),
        "system": "SYSTEM" in package.get("flags", ""),
    }


def scan_packages(serial: str, timeout: int = 120) -> List[Dict[str, Any]]:
    """Pull the package table and rank monitoring signals."""
    rc, out, err = shell(serial, "dumpsys package", timeout=timeout)
    if rc != 0 or not out.strip():
        return []
    parsed = parse_package_dump(out)
    ranked = [score_package(pkg) for pkg in parsed.values()]
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return [item for item in ranked if item["score"] >= 4]


def scan_installed(serial: str) -> List[Dict[str, str]]:
    """Inventory third-party packages with their installer."""
    rc, out, _ = shell(serial, "pm list packages -3 -i", timeout=45)
    rows: List[Dict[str, str]] = []
    if rc != 0:
        return rows
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("package:"):
            continue
        body = line[len("package:"):]
        parts = body.split()
        package = parts[0]
        installer = parts[1].split("=", 1)[1] if len(parts) > 1 and "=" in parts[1] else ""
        rows.append({"package": package, "installer": installer})
    return rows


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SENSITIVE ACCESS AUDIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _components(setting: str) -> List[str]:
    return [c for c in setting.split(":") if c]


def audit_sensitive_access(serial: str) -> Dict[str, Any]:
    """Inventory accessibility, notification, admin, VPN and overlay access."""
    accessibility = _components(read_setting(serial, "secure", "enabled_accessibility_services"))
    listeners = _components(read_setting(serial, "secure", "enabled_notification_listeners"))
    vpn_app = read_setting(serial, "secure", "always_on_vpn_app")

    rc, policy_out, _ = shell(serial, "dumpsys device_policy | grep -i 'admin=ComponentInfo' | head -20", timeout=45)
    admins = re.findall(r"admin=ComponentInfo\{([^}]+)\}", policy_out if rc == 0 else "")

    overlays: List[str] = []
    for command in ("cmd appops query-op SYSTEM_ALERT_WINDOW allow",
                    "appops query-op SYSTEM_ALERT_WINDOW allow"):
        rc, out, _ = shell(serial, command, timeout=30)
        if rc == 0 and out.strip():
            overlays = [line.strip() for line in out.splitlines() if line.strip()]
            break

    usage: List[str] = []
    for command in ("cmd appops query-op GET_USAGE_STATS allow",
                    "appops query-op GET_USAGE_STATS allow"):
        rc, out, _ = shell(serial, command, timeout=30)
        if rc == 0 and out.strip():
            usage = [line.strip() for line in out.splitlines() if line.strip()]
            break

    return {
        "accessibility": accessibility,
        "notification_listeners": listeners,
        "device_admins": admins,
        "vpn_app": vpn_app,
        "overlays": overlays,
        "usage_access": usage,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SMS ANOMALY SCAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _parse_content_rows(text: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("Row:"):
            continue
        body = line.split(" ", 2)
        if len(body) < 3:
            continue
        chunks = re.split(r", (?=[A-Za-z_]+=)", body[2])
        record: Dict[str, str] = {}
        for chunk in chunks:
            if "=" in chunk:
                key, value = chunk.split("=", 1)
                record[key.strip()] = value.strip()
        if record:
            rows.append(record)
    return rows


def scan_sms_anomalies(serial: str) -> Dict[str, Any]:
    """Heuristic scan of the SMS store for silent/type-0 and odd senders."""
    projection = "_id:address:date:protocol:type:body"
    rc, out, err = shell(
        serial,
        f"content query --uri content://sms --projection {projection}",
        timeout=60,
    )
    if rc != 0 or not out.strip():
        detail = (err or out).strip()
        return {"restricted": True, "detail": detail[:300], "rows": 0, "findings": []}

    rows = _parse_content_rows(out)
    findings: List[Dict[str, str]] = []
    sender_counts: Counter = Counter()

    for row in rows:
        address = row.get("address", "")
        body = row.get("body", "")
        protocol = row.get("protocol", "")
        sms_type = row.get("type", "")
        sender_counts[address] += 1

        if protocol not in ("", "0"):
            findings.append({
                "kind": "unusual_protocol",
                "address": address,
                "type": sms_type,
                "protocol": protocol,
                "detail": f"protocol field {protocol} outside the common set",
            })
        if body and len(body) <= 4 and address and not address.startswith("+1"):
            findings.append({
                "kind": "short_body",
                "address": address,
                "type": sms_type,
                "protocol": protocol,
                "detail": f"very short payload ({len(body)} chars)",
            })

    repeated = [{"address": addr, "count": count} for addr, count in sender_counts.most_common(5) if count >= 5]

    return {
        "restricted": False,
        "detail": "",
        "rows": len(rows),
        "findings": findings[:50],
        "top_senders": repeated,
        "note": "Android does not deliver type-0 (silent) SMS to apps; absent rows are not proof of absence.",
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PCAP PARSER + TRAFFIC ANOMALIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PcapError(Exception):
    pass


def _read_name(payload: bytes, offset: int, depth: int = 0) -> Tuple[str, int]:
    labels: List[str] = []
    while offset < len(payload) and depth < 8:
        length = payload[offset]
        if length == 0:
            offset += 1
            break
        if length & 0xC0 == 0xC0:
            pointer = ((length & 0x3F) << 8) | payload[offset + 1]
            inner, _ = _read_name(payload, pointer, depth + 1)
            if inner:
                labels.append(inner)
            return ".".join(labels), offset + 2
        labels.append(payload[offset + 1:offset + 1 + length].decode("ascii", "replace"))
        offset += 1 + length
    return ".".join(labels), offset


def _dns_queries(payload: bytes) -> List[str]:
    if len(payload) < 12:
        return []
    qdcount = struct.unpack_from("!H", payload, 4)[0]
    offset = 12
    queries: List[str] = []
    for _ in range(min(qdcount, 8)):
        name, offset = _read_name(payload, offset)
        if offset + 4 > len(payload):
            break
        offset += 4
        if name:
            queries.append(name.rstrip("."))
    return queries


def _tls_sni(payload: bytes) -> str:
    if len(payload) < 6 or payload[0] != 0x16 or payload[1] != 0x03:
        return ""
    try:
        record_len = struct.unpack_from("!H", payload, 3)[0]
        handshake = payload[5:5 + record_len]
        if len(handshake) < 42 or handshake[0] != 0x01:
            return ""
        length = struct.unpack_from("!I", handshake, 1)[0] >> 8
        if length + 4 > len(handshake):
            return ""
        p = 4 + 2 + 32
        session_len = handshake[p]
        p += 1 + session_len
        cipher_len = struct.unpack_from("!H", handshake, p)[0]
        p += 2 + cipher_len
        compression_len = handshake[p]
        p += 1 + compression_len
        if p + 2 > len(handshake):
            return ""
        ext_total = struct.unpack_from("!H", handshake, p)[0]
        p += 2
        end = min(p + ext_total, len(handshake))
        while p + 4 <= end:
            ext_type, ext_len = struct.unpack_from("!HH", handshake, p)
            p += 4
            if ext_type == 0 and p + ext_len <= len(handshake):
                data = handshake[p:p + ext_len]
                if len(data) > 5:
                    name_len = struct.unpack_from("!H", data, 3)[0]
                    return data[5:5 + name_len].decode("ascii", "replace")
            p += ext_len
    except (struct.error, IndexError):
        return ""
    return ""


def _decode_packet(linktype: int, raw: bytes) -> Optional[Dict[str, Any]]:
    offset = 0
    proto = 0
    if linktype == 1:
        if len(raw) < 14:
            return None
        ethertype = struct.unpack_from("!H", raw, 12)[0]
        offset = 14
        while ethertype in (0x8100, 0x88A8) and len(raw) >= offset + 4:
            ethertype = struct.unpack_from("!H", raw, offset + 2)[0]
            offset += 4
        proto = 4 if ethertype == 0x0800 else 6 if ethertype == 0x86DD else 0
    elif linktype == 113:
        if len(raw) < 16:
            return None
        proto = struct.unpack_from("!H", raw, 14)[0]
        offset = 16
        proto = 4 if proto == 0x0800 else 6 if proto == 0x86DD else 0
    elif linktype == 276:
        if len(raw) < 20:
            return None
        proto_raw = struct.unpack_from("!H", raw, 0)[0]
        offset = 20
        proto = 4 if proto_raw == 0x0800 else 6 if proto_raw == 0x86DD else 0
    elif linktype in (101, 12, 14, 228, 229):
        if not raw:
            return None
        version = raw[0] >> 4
        proto = 4 if version == 4 else 6 if version == 6 else 0
        offset = 0
    else:
        return None

    src_ip = dst_ip = ""
    if proto == 4:
        if len(raw) < offset + 20:
            return None
        ihl = (raw[offset] & 0x0F) * 4
        if ihl < 20 or len(raw) < offset + ihl:
            return None
        ip_proto = raw[offset + 9]
        src_ip = socket.inet_ntoa(raw[offset + 12:offset + 16])
        dst_ip = socket.inet_ntoa(raw[offset + 16:offset + 20])
        payload_off = offset + ihl
    elif proto == 6:
        if len(raw) < offset + 40:
            return None
        ip_proto = raw[offset + 6]
        src_ip = socket.inet_ntop(socket.AF_INET6, raw[offset + 8:offset + 24])
        dst_ip = socket.inet_ntop(socket.AF_INET6, raw[offset + 24:offset + 40])
        payload_off = offset + 40
        while ip_proto in (0, 43, 60) and len(raw) >= payload_off + 2:
            length = (raw[payload_off + 1] + 1) * 8
            ip_proto = raw[payload_off]
            payload_off += length
        if ip_proto == 44:
            ip_proto = raw[payload_off] if payload_off < len(raw) else 0
            payload_off += 8
    else:
        return None

    event: Dict[str, Any] = {"src": src_ip, "dst": dst_ip, "proto": "", "sport": 0,
                             "dport": 0, "syn": False, "dns": [], "sni": "", "http_host": ""}

    if ip_proto == 17 and len(raw) >= payload_off + 8:
        event["proto"] = "UDP"
        event["sport"], event["dport"] = struct.unpack_from("!HH", raw, payload_off)
        payload = raw[payload_off + 8:]
        if 53 in (event["sport"], event["dport"]):
            event["dns"] = _dns_queries(payload)
    elif ip_proto == 6 and len(raw) >= payload_off + 20:
        event["proto"] = "TCP"
        event["sport"], event["dport"] = struct.unpack_from("!HH", raw, payload_off)
        flags = raw[payload_off + 13]
        event["syn"] = bool(flags & 0x02) and not bool(flags & 0x10)
        data_off = (raw[payload_off + 12] >> 4) * 4
        payload = raw[payload_off + data_off:]
        if payload:
            head = payload[:2048]
            if event["dport"] == 443 or head[:2] == b"\x16\x03":
                event["sni"] = _tls_sni(payload)
            if head[:4] in (b"GET ", b"POST", b"HEAD", b"PUT "):
                match = re.search(rb"\r\nHost:\s*([^\r\n]+)", head, re.IGNORECASE)
                if match:
                    event["http_host"] = match.group(1).decode("ascii", "replace").strip()
    else:
        return None

    return event


def read_pcap(path: Path) -> List[Dict[str, Any]]:
    """Parse classic pcap or pcapng into link-layer events."""
    data = path.read_bytes()
    if len(data) < 24:
        raise PcapError("file too short for a capture header")

    if data[:4] == b"\x0a\x0d\x0d\x0a":
        return _read_pcapng(data)

    magic = data[:4]
    if magic not in PCAP_MAGICS:
        raise PcapError("unrecognised capture magic")
    endian, divisor = PCAP_MAGICS[magic]
    linktype = struct.unpack_from(endian + "I", data, 20)[0]

    events: List[Dict[str, Any]] = []
    offset = 24
    while offset + 16 <= len(data):
        ts_sec, ts_frac, incl_len, _orig = struct.unpack_from(endian + "IIII", data, offset)
        offset += 16
        if incl_len > len(data) - offset:
            break
        raw = data[offset:offset + incl_len]
        offset += incl_len
        event = _decode_packet(linktype, raw)
        if event is not None:
            event["ts"] = ts_sec + ts_frac / divisor
            events.append(event)
    return events


def _read_pcapng(data: bytes) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    endian = "<"
    linktype = 1
    resolution = 1e6
    offset = 0

    while offset + 12 <= len(data):
        if data[offset:offset + 4] == b"\x0a\x0d\x0d\x0a":
            try:
                bom = data[offset + 8:offset + 12]
                endian = "<" if bom == b"\x4d\x3c\x2b\x1a" else ">"
                block_len = struct.unpack_from(endian + "I", data, offset + 4)[0]
            except struct.error:
                break
        else:
            try:
                block_len = struct.unpack_from(endian + "I", data, offset + 4)[0]
            except struct.error:
                break

        if block_len < 12 or offset + block_len > len(data):
            break
        block_type = struct.unpack_from(endian + "I", data, offset)[0]

        if block_type == 1 and block_len >= 20:
            linktype = struct.unpack_from(endian + "H", data, offset + 8)[0]
            resolution = 1e6
            opt = offset + 16
            end_opts = offset + block_len - 4
            while opt + 4 <= end_opts:
                code, length = struct.unpack_from(endian + "HH", data, opt)
                if code == 0:
                    break
                value = data[opt + 4:opt + 4 + length]
                if code == 9 and value:
                    resolution = 2 ** value[0]
                opt += 4 + ((length + 3) & ~3)
        elif block_type == 6 and block_len >= 28:
            ts_high, ts_low = struct.unpack_from(endian + "II", data, offset + 12)
            cap_len = struct.unpack_from(endian + "I", data, offset + 20)[0]
            ts = ((ts_high << 32) | ts_low) / resolution
            if 28 + cap_len <= block_len:
                event = _decode_packet(linktype, data[offset + 28:offset + 28 + cap_len])
                if event is not None:
                    event["ts"] = ts
                    events.append(event)
        elif block_type == 3 and block_len >= 16:
            cap_len = struct.unpack_from(endian + "I", data, offset + 8)[0]
            avail = block_len - 16
            if cap_len > avail:
                cap_len = avail
            event = _decode_packet(linktype, data[offset + 12:offset + 12 + cap_len])
            if event is not None:
                event["ts"] = 0.0
                events.append(event)

        offset += block_len

    return events


def label_entropy(label: str) -> float:
    """Shannon entropy per character of a DNS label."""
    if not label:
        return 0.0
    counts = Counter(label)
    total = len(label)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def detect_periodic(events: List[float], min_events: int = 8, max_cv: float = 0.35) -> Optional[Dict[str, Any]]:
    """Coefficient-of-variation test for machine-regular beaconing."""
    if len(events) < min_events:
        return None
    ordered = sorted(events)
    gaps = [b - a for a, b in zip(ordered, ordered[1:]) if b >= a]
    gaps = [gap for gap in gaps if gap > 0]
    if len(gaps) < min_events - 1:
        return None
    mean = sum(gaps) / len(gaps)
    if mean <= 0:
        return None
    variance = sum((gap - mean) ** 2 for gap in gaps) / len(gaps)
    cv = math.sqrt(variance) / mean
    if cv <= max_cv:
        return {"count": len(ordered), "mean_interval": mean, "cv": cv}
    return None


def analyze_traffic(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarise DNS, TLS, HTTP and beaconing anomalies in a capture."""
    dns_counter: Counter = Counter()
    long_labels: List[str] = []
    sni: Counter = Counter()
    http_hosts: Counter = Counter()
    destinations: Counter = Counter()
    connection_times: Dict[Tuple[str, int], List[float]] = defaultdict(list)

    for event in events:
        for name in event.get("dns", []):
            dns_counter[name] += 1
            for label in name.split("."):
                if len(label) >= 32 and label_entropy(label) >= 3.6:
                    long_labels.append(name)
                    break

        if event.get("sni"):
            sni[event["sni"]] += 1
        if event.get("http_host"):
            http_hosts[event["http_host"]] += 1
        if event.get("syn") and event.get("ts"):
            key = (event.get("dst", ""), event.get("dport", 0))
            connection_times[key].append(event["ts"])
            destinations[event.get("dst", "")] += 1

    beacons = []
    for (dest, port), times in connection_times.items():
        periodic = detect_periodic(times)
        if periodic:
            beacons.append({
                "destination": f"{dest}:{port}",
                "connections": periodic["count"],
                "mean_interval_s": round(periodic["mean_interval"], 2),
                "cv": round(periodic["cv"], 3),
            })
    beacons.sort(key=lambda item: item["cv"])

    return {
        "packets": len(events),
        "dns_queries": dns_counter.most_common(25),
        "dns_unique": len(dns_counter),
        "suspect_dns_labels": long_labels[:25],
        "tls_sni": sni.most_common(25),
        "http_hosts": http_hosts.most_common(25),
        "beacons": beacons,
        "top_destinations": destinations.most_common(15),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONSOLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_package_scan(ranked: List[Dict[str, Any]]) -> None:
    sep()
    print(f"  {C.CN}🕵️  MONITORING / STALKERWARE SIGNAL SCAN{C.RST}")
    sep()
    print(f"  {C.D}Score is heuristic. Messaging and parental-control apps can score without malice.{C.RST}\n")

    level_color = {"HIGH": C.R, "MEDIUM": C.Y, "LOW": C.CN, "INFO": C.D}
    shown = 0
    for item in ranked:
        if item["system"] and item["score"] < 12:
            continue
        color = level_color.get(item["level"], C.W)
        print(f"  {color}[{item['level']:<6} {item['score']:>2}]{C.RST} {C.W}{item['name']}{C.RST}")
        if item.get("version"):
            print(f"      {C.D}version  :{C.RST} {item['version']}")
        if item.get("installer"):
            print(f"      {C.D}installer:{C.RST} {item['installer']}")
        for signal in item["signals"][:6]:
            print(f"      {C.D}· {signal}{C.RST}")
        print()
        shown += 1
        if shown >= 15:
            break

    if shown == 0:
        print(f"  {C.G}✅ No packages crossed the risk threshold.{C.RST}\n")
    else:
        print(f"  {C.Y}⚠ Review the ranked packages above before drawing conclusions.{C.RST}\n")


def print_access_audit(audit: Dict[str, Any]) -> None:
    sep()
    print(f"  {C.CN}🔐 SENSITIVE ACCESS INVENTORY{C.RST}")
    sep()

    sections = [
        ("Accessibility services", audit.get("accessibility", []), "ACCESSIBILITY"),
        ("Notification listeners", audit.get("notification_listeners", []), "NOTIFICATION"),
        ("Device administrators", audit.get("device_admins", []), "DEVICE_ADMIN"),
        ("Overlay permission", audit.get("overlays", []), "OVERLAY"),
        ("Usage access", audit.get("usage_access", []), ""),
    ]
    for title, items, note_key in sections:
        if items:
            print(f"  {C.Y}{title}{C.RST}")
            for item in items[:20]:
                print(f"      {C.W}•{C.RST} {item}")
            if note_key:
                print(f"      {C.D}{DANGEROUS_NOTES[note_key]}{C.RST}")
            print()
        else:
            print(f"  {C.G}✓{C.RST} {title}: none")

    vpn = audit.get("vpn_app", "")
    if vpn:
        print(f"  {C.Y}Always-on VPN{C.RST}: {vpn}")
        print(f"      {C.D}{DANGEROUS_NOTES['VPN']}{C.RST}")
    else:
        print(f"  {C.G}✓{C.RST} Always-on VPN: none")
    print()


def print_traffic(report: Dict[str, Any]) -> None:
    sep()
    print(f"  {C.CN}📡 TRAFFIC ANOMALY REPORT{C.RST}")
    sep()
    print(f"  {C.DW}Packets parsed{C.RST} : {report['packets']}")
    print(f"  {C.DW}DNS queries  {C.RST} : {report['dns_unique']} unique")

    if report["beacons"]:
        print(f"\n  {C.Y}Periodic connections (beacon candidates):{C.RST}")
        for beacon in report["beacons"][:10]:
            print(f"      {C.W}{beacon['destination']}{C.RST}  "
                  f"{beacon['connections']} conns, ~{beacon['mean_interval_s']}s, cv={beacon['cv']}")
    else:
        print(f"\n  {C.G}✓ No machine-regular beaconing detected.{C.RST}")

    if report["suspect_dns_labels"]:
        print(f"\n  {C.Y}Long / high-entropy DNS names (tunnel candidates):{C.RST}")
        for name in report["suspect_dns_labels"][:10]:
            print(f"      {C.D}{name}{C.RST}")

    if report["http_hosts"]:
        print(f"\n  {C.Y}Cleartext HTTP hosts:{C.RST}")
        for host, count in report["http_hosts"][:10]:
            print(f"      {C.W}{host}{C.RST} ({count})")

    if report["tls_sni"]:
        print(f"\n  {C.D}Top TLS SNI:{C.RST}")
        for host, count in report["tls_sni"][:10]:
            print(f"      {C.D}{host} ({count}){C.RST}")

    if report["top_destinations"]:
        print(f"\n  {C.D}Top destinations:{C.RST}")
        for host, count in report["top_destinations"][:8]:
            print(f"      {C.D}{host} ({count}){C.RST}")
    print()


def save_detection_report(payload: Dict[str, Any]) -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    serial = payload.get("serial", "device")
    safe = "".join(ch for ch in serial if ch.isalnum() or ch in "-_")[:24] or "device"
    path = EXPORT_DIR / f"detection_{safe}_{stamp}.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def run_detection_console() -> None:
    """Interactive monitoring and traffic detection console."""
    print()
    sep()
    print(f"  {C.R}🕵️  VIRGOYT MONITORING & TRAFFIC DETECTION{C.RST}")
    print(f"  {C.D}Scope: devices you own or have written authorization to assess.{C.RST}")
    sep()

    serial = select_device()
    if not serial:
        return

    while True:
        print(f"  {C.DR}┌{'─'*54}┐{C.RST}")
        print(f"  {C.DR}│{C.RST} {C.W}Target: {serial:<44}{C.RST} {C.DR}│{C.RST}")
        print(f"  {C.DR}├{'─'*54}┤{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[1]{C.RST} Scan packages for monitoring signals                {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[2]{C.RST} Sensitive access inventory                          {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[3]{C.RST} SMS anomaly scan                                    {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[4]{C.RST} Analyze PCAP capture                                {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[5]{C.RST} Full detection run + JSON report                    {C.DR}│{C.RST}")
        print(f"  {C.DR}│{C.RST}  {C.R}[0]{C.RST} Back to main menu                                   {C.DR}│{C.RST}")
        print(f"  {C.DR}└{'─'*54}┘{C.RST}")

        action = prompt("SELECT DETECTION ACTION [0]") or "0"
        payload: Dict[str, Any] = {"serial": serial, "mode": action}

        if action == "0":
            return
        if action == "1":
            ranked = scan_packages(serial)
            print_package_scan(ranked)
        elif action == "2":
            print_access_audit(audit_sensitive_access(serial))
        elif action == "3":
            report = scan_sms_anomalies(serial)
            sep()
            print(f"  {C.CN}✉️  SMS ANOMALY SCAN{C.RST}")
            sep()
            if report.get("restricted"):
                print(f"  {C.Y}⚠ SMS store not readable: {report['detail']}{C.RST}\n")
            else:
                print(f"  {C.DW}Rows read{C.RST}: {report['rows']}")
                for finding in report["findings"][:15]:
                    print(f"      {C.Y}{finding['kind']}{C.RST} {finding.get('address')} — {finding['detail']}")
                if not report["findings"]:
                    print(f"  {C.G}✓ No heuristic SMS anomalies.{C.RST}")
                print(f"  {C.D}{report['note']}{C.RST}\n")
        elif action == "4":
            raw_path = prompt("PCAP FILE PATH")
            if raw_path:
                path = Path(raw_path).expanduser()
                try:
                    events = read_pcap(path)
                    print_traffic(analyze_traffic(events))
                except (OSError, PcapError) as exc:
                    print(f"  {C.R}❌ Capture parse failed: {exc}{C.RST}\n")
        elif action == "5":
            ranked = scan_packages(serial)
            access = audit_sensitive_access(serial)
            sms = scan_sms_anomalies(serial)
            print_package_scan(ranked)
            print_access_audit(access)
            sep()
            print(f"  {C.CN}✉️  SMS ANOMALY SCAN{C.RST}")
            sep()
            if sms.get("restricted"):
                print(f"  {C.Y}⚠ SMS store not readable: {sms['detail']}{C.RST}\n")
            else:
                print(f"  {C.DW}Rows read{C.RST}: {sms['rows']}  anomalies: {len(sms['findings'])}\n")

            payload.update({"packages": ranked[:40], "access": access, "sms": sms})
            path = save_detection_report(payload)
            print(f"  {C.G}✅ Detection report: {path}{C.RST}\n")
        else:
            print(f"  {C.R}❌ Invalid selection.{C.RST}\n")
