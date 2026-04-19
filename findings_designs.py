#!/usr/bin/env python3
import sys

# ══════════════════════════════════════════════════════════════════════
# COLOR DEFINITIONS
# ══════════════════════════════════════════════════════════════════════
class C:
    R   = "\033[91m"    # bright red
    RD  = "\033[31m"    # dark red
    G   = "\033[92m"    # bright green
    Y   = "\033[93m"    # yellow
    CY  = "\033[96m"    # bright cyan
    CYD = "\033[36m"    # dim cyan
    MG  = "\033[95m"    # magenta
    W   = "\033[97m"    # white
    GR  = "\033[90m"    # grey
    GL  = "\033[37m"    # light grey
    B   = "\033[1m"     # bold
    DIM = "\033[2m"
    RST = "\033[0m"     # reset

def section(title):
    print(f"\n  {C.R}{C.B}{title}{C.RST}")
    print(f"  {C.RD}{'─' * 60}{C.RST}")

# ══════════════════════════════════════════════════════════════════════
# STYLE A: Minimalist High-Signal
# ══════════════════════════════════════════════════════════════════════
def style_a():
    section("STYLE A: MINIMALIST DOT-LEADERS")
    findings = [
        ("CORS",     "MEDIUM",   "http://localhost:3000/api/config"),
        ("SOURCEMAP","MEDIUM",   "http://localhost:3000/main.js.map"),
        ("SQLI",     "HIGH",     "http://localhost:3000/search?q=")
    ]
    for tag, sev, url in findings:
        sc = C.R if sev == "HIGH" else C.Y
        print(f"  {sc}[{sev:<7}]{C.RST} {C.W}┄{C.RST} {C.MG}{tag:^12}{C.RST} {C.W}┄{C.RST} {C.CY}{url}{C.RST}")

# ══════════════════════════════════════════════════════════════════════
# STYLE B: Cyber-List (Angled Brackets)
# ══════════════════════════════════════════════════════════════════════
def style_b():
    section("STYLE B: CYBER-LIST")
    findings = [
        ("CORS",     "MEDIUM",   "http://localhost:3000/api/config"),
        ("SOURCEMAP","MEDIUM",   "http://localhost:3000/main.js.map"),
        ("SQLI",     "HIGH",     "http://localhost:3000/search?q=")
    ]
    for tag, sev, url in findings:
        sc = C.R if sev == "HIGH" else C.Y
        print(f"  {C.RD}│{C.RST} {C.W}»{C.RST} {sc}{sev:<7}{C.RST} {C.B}{C.MG}[{tag}]{C.RST} {C.GL}{url}{C.RST}")

# ══════════════════════════════════════════════════════════════════════
# STYLE C: Iconic Grid (Modern HUD)
# ══════════════════════════════════════════════════════════════════════
def style_c():
    section("STYLE C: MODERN HUD GRID")
    findings = [
        ("CORS",     "MEDIUM",   "http://localhost:3000/api/config"),
        ("SOURCEMAP","MEDIUM",   "http://localhost:3000/main.js.map"),
        ("SQLI",     "HIGH",     "http://localhost:3000/search?q=")
    ]
    # Header
    print(f"  {C.GR}{'SEVERITY':<10}  {'CATEGORY':<14}  {'TARGET ENDPOINT'}{C.RST}")
    for tag, sev, url in findings:
        sc = C.R if sev == "HIGH" else C.Y
        print(f"  {C.B}{sc}{sev:<10}{C.RST}  {C.MG}{tag:<14}{C.RST}  {C.W}{url}{C.RST}")

if __name__ == "__main__":
    print(f"\n{C.B}{C.R}--- HELLHOUND FINDINGS DESIGN SAMPLES ---{C.RST}")
    style_a()
    style_b()
    style_c()
    print("\n")
