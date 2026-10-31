# 🎭 VirgoYT — OSINT Toolkit (v5.0 Full-Spectrum Upgrade)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Android%20%2F%20Termux%20%2F%20Linux-orange.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Developer](https://img.shields.io/badge/Developer-VIRGOYT707-red.svg)](#)
[![Status](https://img.shields.io/badge/Status-FULL--SPECTRUM%20OSINT-red.svg)](#)

A high-precision, privacy-focused telecommunication metadata analysis and evidence management application architected specifically for Android Termux and Linux environments.

```text
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

 ██╗   ██╗██╗██████╗  ██████╗  ██████╗ ██╗   ██╗████████╗
 ██║   ██║██║██╔══██╗██╔════╝ ██╔═══██╗╚██╗ ██╔╝╚══██╔══╝
 ██║   ██║██║██████╔╝██║  ███╗██║   ██║ ╚████╔╝    ██║   
 ╚██╗ ██╔╝██║██╔══██╗██║   ██║██║   ██║  ╚██╔╝     ██║   
  ╚████╔╝ ██║██║  ██║╚██████╔╝╚██████╔╝   ██║      ██║   
   ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝      ╚═╝   
```

---

## 📌 Project Overview

**VirgoYT OSINT Toolkit v4.0** is an open-source, investigative intelligence application designed to analyze phone number numbering plans, extract telecommunications registry metadata, evaluate risk profiles with transparent and verifiable signals, and manage investigative cases locally.

Designed from the ground up by **VIRGOYT707**, v4.0 introduces modular architecture, transparent risk explanations, crash-consistent SQLite backups, leak-proof GitHub synchronization, and a built-in automated test suite.

---

## ⚡ Core Features

- **ITU-T E.164 Number Validation:** Parses international and national phone numbers worldwide; differentiates technical numbering-plan validation from possibility checks.
- **Telecom Registry Correlation:** Identifies country jurisdiction, national destination codes, original carrier block allocations, and regulatory timezones.
- **Transparent Threat Scoring:** Replaces arbitrary risk formulas with verifiable, documented signals (VoIP disposable capability, numbering-plan mismatches, tariff anomalies). Shows `UNKNOWN` when evidence is insufficient.
- **Privacy-Focused OSINT Engine:** Generates search dorks and formatted query variations (E.164, RFC3966, dotted, spaced) for manual open-web discovery. No illegal scraping, credential harvesting, or intrusive bypasses.
- **Encrypted Evidence Vault (SQLite):** Stores case dossiers with unique IDs (`VY-YYYYMMDD-XXXX`), creation/update timestamps, categories, and searchable analyst tags.
- **Case Note Editing:** Update investigation findings, tags, and categories at any point during active investigations.
- **CSV Reporting Engine:** Export complete or filtered subsets of evidence records for formal case reporting.
- **Database Backup & Restore:** Built-in live SQLite backups (`PRAGMA integrity_check` verified) with one-click restore.
- **Leak-Proof GitHub Synchronization:** Pre-flight audit engine inspects pending changes and prevents sensitive evidence databases, CSV files, and API credentials from ever being committed or pushed.
- **Self-Test Verification Suite:** 14-point automated test suite validating parsing, scoring, database operations, git safety, device-weakness evaluation, spyware scoring, and PCAP anomaly detection using synthetic data.
- **Device Audit & ADB Extraction:** Fingerprints connected Android devices, ranks 16 non-CVE configuration weaknesses, and captures dumpsys/settings/package/network artifacts into a timestamped case folder.
- **Monitoring Detection:** Scores installed packages for stalkerware permission patterns, inventories accessibility/notification/admin/overlay access, scans SMS heuristics, and parses PCAP/pcapng for beaconing and DNS-tunnel signals.

---

## 📋 System Requirements

- **Environment:** Android with Termux, or any standard Linux distribution.
- **Python:** Python 3.8+ (standard library: `sqlite3`, `csv`, `pathlib`, `hashlib`, `secrets`, `subprocess`).
- **Package Dependency:** `phonenumbers>=8.12.0`
- **Permissions:** Standard non-root user execution. No thermal or partition modifications required.

---

## 🚀 Installation — Termux / Linux PC

The same source tree runs on both. `setup.py` detects the platform and finishes the right setup.

### Universal (auto-detect)

```bash
git clone https://github.com/itsdazzyprince3-sudo/phone_tool.git
cd phone_tool
python3 setup.py            # Termux: pip-installs + creates ~/phone_tool vault
                            # Linux:  pip-installs + creates ~/.local/share/virgoyt vault
numbertrackervy
```

### Termux / Android

```bash
pkg update -y && pkg install python git -y
pkg install android-tools -y   # required only for option [13] device audit
pip install .
numbertrackervy
```

### Linux PC (Debian / Ubuntu / Kali)

```bash
sudo apt update
sudo apt install python3 python3-phonenumbers git
pipx install .              # or: sudo python3 setup.py install
numbertrackervy
```

### npm (launcher package)

Node is only a launcher here — the engine stays Python. The postinstall step checks for `phonenumbers` and attempts a pip install when it is missing (`VIRGOYT_SKIP_PIP=1` skips that).

```bash
npm install -g . --allow-scripts numbertrackervy
numbertrackervy
```

Local project install also works:

```bash
npm install . --allow-scripts numbertrackervy
npx numbertrackervy
```

npm 12 blocks lifecycle scripts by default, so the `--allow-scripts` flag lets the postinstall dependency check run. If scripts stay blocked, install the one Python dependency yourself: `python3 -m pip install "phonenumbers>=8.12.0"`.

Set `PYTHON=/path/to/python3` if your interpreter is not named `python3`.

### Debian package (.deb) — install with apt

```bash
python3 setup.py deb
sudo apt install ./dist/numbertrackervy_4.0.0_all.deb
numbertrackervy
```

The `.deb` declares `python3-phonenumbers`, so apt pulls the dependency. Package name is lowercase: `numbertrackervy`.

To run the standalone automated test suite at any time:
```bash
python3 test_toolkit.py     # or: python3 setup.py test
```

---

## 🎮 Command Center Menu

```text
  ╔════════════════════════════════════════════════════════╗
  ║ 🎭 VirgoYT OSINT — COMMAND CENTER (v4.0.0)             ║
  ╠════════════════════════════════════════════════════════╣
  ║  [1]  🔍 Analyze Phone Number                          ║
  ║  [2]  💾 Analyze + Save Case                           ║
  ║  [3]  📊 View Evidence Vault                           ║
  ║  [4]  🔎 Search Cases (ID, Notes, Tags, Phone)        ║
  ║  [5]  👁️  View Case Details                            ║
  ║  [6]  📝 Edit Case Notes & Tags                        ║
  ║  [7]  📤 Export to CSV                                 ║
  ║  [8]  📈 Vault Statistics & Analytics                  ║
  ║  [9]  🛡️  Backup Database (Live SQLite Backup)         ║
  ║  [10] ♻️  Restore Database from Backup                 ║
  ║  [11] 🧪 Run System Self-Test Suite                    ║
  ║  [12] 🔄 GitHub Sync & Leak-Prevention Audit          ║
  ║  [13] 📱 Device Audit & ADB Extraction                ║
  ║  [14] 🕵️  Monitoring & Traffic Detection              ║
  ║  [0]  ⚡ Exit Toolkit                                   ║
  ╚════════════════════════════════════════════════════════╝
```

---

## 📱 Device Audit & ADB Extraction

Menu option `[13]` works against an Android device you own or are explicitly authorized to assess. The phone must be unlocked, USB debugging (or wireless debugging) enabled, and the RSA fingerprint prompt accepted.

| Action | Output |
|---|---|
| `[1]` Quick fingerprint | Manufacturer, model, Android/SDK, security patch, build tags, verified-boot state, bootloader, baseband, SIM/network operator, account list, package count, local IP |
| `[2]` Non-CVE weakness audit | 16 configuration checks ranked `CRITICAL → LOW`, each with evidence, exposure, and hardening step |
| `[3]` Extract all readable data | `dumpsys` snapshots, settings scopes, package inventory, accounts, connectivity, Wi-Fi, telephony, location, Bluetooth, storage, routes, process list, and SIM/contact/SMS/call-log queries |
| `[4]` ADB backup | Legacy `adb backup -apk -shared -all` archive; the phone must confirm |
| `[5]` Full run | Fingerprint + audit + extraction into one timestamped case folder |
| `[6]` Wireless ADB | `adb pair` against a pairing port, then `adb connect` to `host:port` |

### Weakness checks (configuration-based, not CVE-bound)

- USB debugging and RSA authorization (`ro.adb.secure`)
- Wireless debugging port and Wi-Fi ADB toggle
- Debug build type and `ro.debuggable`
- Verified boot and dm-verity mode
- Root / `su` binaries and test-keys builds
- Screen-lock state (`lockscreen.disabled`, trust state)
- Developer options
- Sideloading / unknown sources
- Package verifier and ADB install verification
- Debuggable installed packages
- Exported content providers
- Enabled accessibility services
- Active device administrators
- Storage encryption state
- User-installed CA certificates (TLS interception surface)
- ADB backup channel

### Artifacts

Every extraction writes `exports/device_<serial>_<timestamp>/`:

```text
device_<serial>_<timestamp>/
├── manifest.json               # command, return code, bytes, elapsed ms, restricted flag
├── device_fingerprint.json
├── weakness_report.json
├── weakness_report.txt
└── raw/
    ├── props.txt
    ├── settings_global.txt
    ├── settings_secure.txt
    ├── packages_all.txt
    ├── accounts.txt
    ├── wifi.txt
    ├── telephony.txt
    ├── location.txt
    ├── contacts.txt
    └── ...
```

Queries denied by Android 11+ scoped storage / permission policy are recorded with `"restricted": true` in the manifest instead of failing silently. Wireless ADB should be switched off after use, and the audit is read-only — it changes no device state.

### Install adb

```bash
# Termux
pkg install android-tools -y

# Debian / Ubuntu
sudo apt install adb
```

---

## 🕵️ Monitoring & Traffic Detection

Menu option `[14]` is the defensive counterpart to the device audit. It looks for signs that a device is being watched, and for network behaviour that looks automated.

| Action | What it does |
|---|---|
| `[1]` Package scan | Parses `dumpsys package`, scores third-party apps on surveillance permission clusters, declared accessibility/admin/notification components, installers, and name patterns |
| `[2]` Sensitive access inventory | Lists enabled accessibility services, notification listeners, device admins, overlay permission holders, usage-access holders, and the always-on VPN app |
| `[3]` SMS anomaly scan | Reads the SMS store for unusual protocol values, very short payloads, and repeat senders; records permission denial honestly |
| `[4]` PCAP analysis | Parses classic pcap and pcapng, then reports beacon candidates, high-entropy/long DNS labels, cleartext HTTP hosts, TLS SNI, and top destinations |
| `[5]` Full run | Package scan + access inventory + SMS scan, written to `exports/detection_<serial>_<timestamp>.json` |

### Scoring model

Each package gets a heuristic score from explicit weights:

- `READ_SMS` + `READ_CONTACTS` plus `CAMERA` or `RECORD_AUDIO` → **surveillance cluster** (+6)
- `READ_CALL_LOG`, `RECORD_AUDIO`, `SEND_SMS`, `WRITE_CALL_LOG`, `ANSWER_PHONE_CALLS` (+2 each)
- Declared `BIND_ACCESSIBILITY_SERVICE`, `BIND_DEVICE_ADMIN` (+5), `BIND_NOTIFICATION_LISTENER_SERVICE` (+4)
- `SYSTEM_ALERT_WINDOW`, `REQUEST_INSTALL_PACKAGES` (+3), background location, storage (+2)
- No installer record on a non-system app (possible sideload, +2), debuggable package (+3)
- Monitoring-family package name patterns (+3 to +10)

`HIGH ≥ 12`, `MEDIUM ≥ 7`, `LOW ≥ 4`. System packages are hidden unless they exceed the HIGH threshold. Messaging and parental-control apps can legitimately score — the tool reports signals, never verdicts.

### PCAP support

- Link types: Ethernet, Linux SLL (113), SLL2 (276), raw IPv4/IPv6 (101/12/228/229)
- IPv4 and IPv6 (basic extension-header walk)
- UDP/DNS question extraction, TCP SYN timing, TLS ClientHello SNI, cleartext HTTP `Host:`
- `pcapng` Section Header / Interface Description / Enhanced Packet / Simple Packet blocks, including `if_tsresol`

Beaconing uses the coefficient of variation of connection intervals: `cv ≤ 0.35` over at least 8 connections is flagged as machine-regular. That is a heuristic — CDNs, push channels, and update checks can look periodic.

### Honest limitations

- Android does not deliver type-0 (silent) SMS to apps, so an empty SMS scan is not proof of absence.
- Beacons over TLS without SNI and DNS over HTTPS are not attributable from the capture alone.
- Package scoring sees declared permissions, not runtime behaviour. A clean package list does not rule out a compromised system app.
- Full detection runs are read-only and change no device state.

---

## 📑 Example Intelligence Report (Synthetic Data)

```text
  ╔══════════════════════════════════════════════════════════════════╗
  ║ 🎭 VirgoYT OSINT — TELECOM INTELLIGENCE REPORT                  ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║  Case ID   : VY-20261031-7F8A       Timestamp : 2026-10-31 UTC   ║
  ║                                                                  ║
  ║  ┌── TARGET SPECIFICATION ────────────────────────────────       ║
  ║  │ 📱 Input Text    : +1 415 555 2671                            ║
  ║  │ 📞 International : +1 415-555-2671                            ║
  ║  │ 🔢 E.164 Standard: +14155552671                               ║
  ║  │ 🏷️  National Dial : (415) 555-2671                            ║
  ║  │ 🔑 Technical Plan: ✔ VALID (Numbering Plan Conforming)        ║
  ║  │ ℹ️  Structure Note: Possible according to numbering plan length║
  ║  │                                                               ║
  ║  ┌── TELECOM ALLOCATION & REGISTRY METADATA ──────────────       ║
  ║  │ 🌐 Jurisdiction  : United States  [US]  (CC: +1)              ║
  ║  │ 📡 Assigned Telco: Pacific Bell Telephone Company             ║
  ║  │ 🏠 Line Category : Fixed Line                                 ║
  ║  │ 🕐 Regulatory TZ : America/Los_Angeles                        ║
  ║  │                                                               ║
  ║  ┌── THREAT & ANOMALY ASSESSMENT ─────────────────────────       ║
  ║  │ 🎯 Composite Risk: ██░░░░░░░░░░░░░░░░░░ 10/100 [LOW]          ║
  ║  │ 🛡️  Confidence    : HIGH  (Evidence Density)                   ║
  ║  │ Verifiable Signals:                                           ║
  ║  │   -5 PHYSICAL_WIRELINE_ALLOCATION (Telecom Registry)          ║
  ║  │      ▸ Allocated to a physical wireline exchange premises.    ║
  ║  │                                                               ║
  ║  ┌── SOURCE ATTRIBUTION & LEGAL LIMITATIONS ──────────────       ║
  ║  │ 📚 Source      : ITU-T E.164 / Google libphonenumber database  ║
  ║  │ ⚠  Valid format does NOT guarantee the number is actively in service.
  ║  │ ⚠  Carrier metadata indicates original allocation, NOT ported MNP network.
  ║  │ ⚠  Timezone indicates geographic numbering area, NOT current GPS location.
  ║  │ ⚠  Real-time interception or live subscriber tracking is impossible.
  ║                                                                  ║
  ║  VirgoYT v4.0.0  |  Developer: VIRGOYT707  |  PRIVACY-FOCUSED    ║
  ╚══════════════════════════════════════════════════════════════════╝
```

---

## ⚖️ Privacy, Ethics & Legal Disclaimers

1. **No Real-Time Tracking:** Phone number metadata cannot be used to pinpoint the live location, GPS coordinates, or physical movement of a phone. Timezone data reflects regulatory telephone exchanges only.
2. **No Portability Guarantee:** Carrier information reflects historical/initial block allocations from telecommunications regulatory authorities. Numbers may have transitioned across operators via Mobile Number Portability (MNP).
3. **No Active Status Proof:** An algorithmically valid phone number does not confirm that an active contract, SIM, or subscription currently exists.
4. **Legitimate OSINT Only:** VirgoYT v4.0 strictly rejects credential harvesting, unauthorized carrier lookup APIs, spoofed login portals, and private subscriber identification. All external lookups are user-initiated through public web destinations.

---

## 🔧 Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `sqlite3.OperationalError: unable to open database file` | Directory permissions restricted | VirgoYT v4.0 creates `~/phone_tool` on Termux or `~/.local/share/virgoyt` on Linux (override with `VIRGOYT_DATA_DIR`). Ensure storage permission is granted in Termux (`termux-setup-storage`). |
| `Missing or invalid default region` | Ambiguous national number format | Enter national numbers with international calling code (e.g. `+919876543210`), or supply `IN` or `91` at the region prompt. |
| `git push failed / authentication error` | GitHub credentials unauthenticated in Termux | Run `gh auth login` or configure SSH keys in Termux. VirgoYT will safely block sync until credentials are authenticated. |
| `Sync blocked: Sensitive files detected` | Evidence database or export unstaged | VirgoYT auto-protects `.db` and `.csv` files. Run `virgoyt` option `[12]` to audit the `.gitignore` configuration. |

---

## 👤 Developer Credit

- **Project:** VirgoYT OSINT Toolkit v4.0
- **Lead Developer:** **VIRGOYT707**
- **Repository:** [https://github.com/itsdazzyprince3-sudo/phone_tool.git](https://github.com/itsdazzyprince3-sudo/phone_tool.git)
