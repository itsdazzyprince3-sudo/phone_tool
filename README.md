# 🎭 VirgoYT — Phone OSINT & Evidence Toolkit (v3.0)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-VirgoYT-red.svg)](#)

A high-performance command-line OSINT and telecom reconnaissance tool built for cyber analysts, investigators, and security researchers.

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

## ⚡ Features

- **Telecom Intelligence:** Country, circle/region, telco carrier, line type (Mobile, Landline, VoIP).
- **Burner & Fraud Detection:** Identifies virtual/VoIP disposable numbers (TextNow, Google Voice, burner apps).
- **Threat & Risk Engine:** Dynamic risk calculation (0-100) based on telecom flags.
- **Search Dorks & Platform Hooks:** One-click OSINT search queries and direct lookups for WhatsApp, Telegram, Truecaller, Sync.me, and search engines.
- **Encrypted Evidence Vault:** Embedded SQLite tracking with MD5 case hashing, tags, and notes.
- **Auto-Sync & Git Updater:** Option `[9]` checks your remote GitHub repo, pulls updates, and hot-restarts in real time.
- **Data Export:** Clean CSV reporting for case management.

---

## 🚀 Installation & Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/VirgoYT-Phone-OSINT.git
cd VirgoYT-Phone-OSINT

# Install dependencies
pip install -r requirements.txt

# Run toolkit
python3 phone_tool.py
```

---

## 👤 Author
- **VirgoYT**
