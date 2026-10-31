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
- **Self-Test Verification Suite:** 10-point automated test suite validating parsing, scoring, database operations, and git safety using synthetic numbers.

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
  ║  [0]  ⚡ Exit Toolkit                                   ║
  ╚════════════════════════════════════════════════════════╝
```

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
