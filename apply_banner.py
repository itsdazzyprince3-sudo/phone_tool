#!/usr/bin/env python3
import os

target = os.path.expanduser("~/phone_tool/phone_tool.py")

NEW_BANNER = '''BANNER = f"""{C.Y}{C.B}
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
{C.R}
 ██╗   ██╗██╗██████╗  ██████╗  ██████╗ ██╗   ██╗████████╗
 ██║   ██║██║██╔══██╗██╔════╝ ██╔═══██╗╚██╗ ██╔╝╚══██╔══╝
 ██║   ██║██║██████╔╝██║  ███╗██║   ██║ ╚████╔╝    ██║   
 ╚██╗ ██╔╝██║██╔══██╗██║   ██║██║   ██║  ╚██╔╝     ██║   
  ╚████╔╝ ██║██║  ██║╚██████╔╝╚██████╔╝   ██║      ██║   
   ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝      ╚═╝{C.RST}
{C.DC}
  ╔══════════════════════════════════════════════════════════╗
  ║  {C.R}{C.B}🎭  VirgoYT — ANONYMOUS INTELLIGENCE ENGINE  🎭{C.RST}{C.DC}         ║
  ║  {C.DR}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.DC}  ║
  ║  {C.W}AGENT    :{C.RST} {C.R}{C.B}VirgoYT{C.RST}{C.DC}                                       ║
  ║  {C.W}PROTOCOL :{C.RST} {C.Y}OSINT / CARRIER TRACE / THREAT RECON{C.RST}{C.DC}       ║
  ║  {C.W}DATABASE :{C.RST} {C.CN}ENCRYPTED EVIDENCE VAULT{C.RST}{C.DC}                      ║
  ║  {C.W}SYSTEM   :{C.RST} {C.G}● ONLINE // UNTRACEABLE{C.RST}{C.DC}                     ║
  ╚══════════════════════════════════════════════════════════╝{C.RST}
"""'''

with open(target, "r") as f:
    code = f.read()

# Replace the BANNER block
if 'BANNER = f"""' in code:
    start = code.find('BANNER = f"""')
    end = code.find('"""', start + 14) + 3
    updated = code[:start] + NEW_BANNER + code[end:]
    with open(target, "w") as f:
        f.write(updated)
    print("✔ Yellow Hacker Mask Banner applied successfully.")
else:
    print("✘ Could not locate BANNER block.")
