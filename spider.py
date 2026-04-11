#!/usr/bin/env python3
"""
  HELLHOUND SPIDER  v12.0  —  Standalone Recon Engine

  Full SPA + Non-SPA Crawler | robots.txt | sitemap.xml | JS Analysis

Dependencies:
  pip install aiohttp beautifulsoup4 lxml
  pip install playwright && playwright install chromium     # optional SPA
"""

import argparse
import asyncio
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import random
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, urlunparse

import aiohttp
from bs4 import BeautifulSoup, Comment

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════
# METADATA
# ══════════════════════════════════════════════════════════════════════

VERSION      = "12.0"
__author__   = "Sree Danush S (L4ZZ3RJ0D)"
__license__  = "MIT"
__credits__  = ["L4ZZ3RJ0D"]
__maintainer__ = "L4ZZ3RJ0D"

# ══════════════════════════════════════════════════════════════════════
# TERMINAL COLOURS
# ══════════════════════════════════════════════════════════════════════

class C:
    R   = "\033[91m"    # bright red
    RD  = "\033[31m"    # dark red
    G   = "\033[92m"    # bright green
    GD  = "\033[32m"    # dark green
    Y   = "\033[93m"    # yellow
    O   = "\033[38;5;208m"  # orange
    CY  = "\033[96m"    # bright cyan
    CYD = "\033[36m"    # dim cyan
    BL  = "\033[94m"    # blue
    MG  = "\033[95m"    # magenta
    W   = "\033[97m"    # white
    GR  = "\033[90m"    # grey
    GL  = "\033[37m"    # light grey
    B   = "\033[1m"     # bold
    DIM = "\033[2m"
    RST = "\033[0m"     # reset

def _no_color() -> bool:
    return not sys.stdout.isatty() or bool(os.environ.get("NO_COLOR"))

def _strip(s: str) -> str:
    return re.sub(r'\033\[[^m]*m', '', s)

# ══════════════════════════════════════════════════════════════════════
# BANNER  — pure red ASCII art
# ══════════════════════════════════════════════════════════════════════

_BANNER_ART = r"""
                                         .=.        .-.
                                      .:   :#.        .*:   :.
                                     .#:  .#*.        .+#.  :#.
                                    .%#  .+@:          :@*. .#%.
                                  .:@@. .-@#.          .#@-. .@@:
                                 .-@@=..:@@-            :@@:. =@@-.
                                .-@@*. :@@+.            .+@@:..*@@-.
                               .*@@@..+@@@.             ..@@@+..@@@*.
                              .%@@@:.%@@@-.    ..  ...   .:@@@#.:@@@%.
                             ..*@@#..#@@%.   .-@....@-.   .%@@#..#@@#..
                              .@@@:.+@@@:.   .@@%@@%@@.  ..-@@@+..@@@.
                              .@@@+...=@@@*:..*@@@@@@*..:+%@@=...+@@@.
                              .%@@@@@@@%+:+@@@@@@@@@@@@@@+:+%@@@@@@@%.
                              .::....-+*%@@@@@@@@@@@@@@@@@@%*+-....::.
                               ..        ..:*@@@@@@@@@@#:..        ...
                              .@=....-*@@@@@%#@@@@@@@@#%@@@@@*-....=@.
                             .*@@@@@@@@#+-.:@@*@@@@@@#@@:.-+#@@@@@@@@#.
                             .@@@=.....  .*@@+@@@@@@@@+@@#.   ....=@@@.
                             :@@@:  :...*@@#=@@@@@@@@@@=#@@*...:. :@@@:.
                          ...-@@@-. %@@@@#.=@@@@@@@@@@@@=.#@@@@%. -@@@-..
                           .*@@@@+. %@@@....@@@@@@@@@@@@. ..%@@%. +@@@@+.
                            .*@@@%:*#@@#   .=@@@@@@@@@@+.  .#@@%#.%@@@*.
                             .*@@@.+@@@#    -@@@@@@@@@@-   .#@@@=.@@@+.
                              .#@@+.#@@@    .@@@@@@@@@@.   .%@@#.+@@%.
                               .@@@..@@@..  .:@#@@@@#@:     @@@..@@@:
                               .:@@=.+@@=.   ...:@@-...   .=@@+.=@@:.
                                ..@@:.@@@..      ..       .@@@..@@:.
                                  .%*.=@@:.              .:@@=.*@..
                                   .+-.#@%.              .%@#.-*.
                                    ....@@-.            .-@@...
                                        .%@..           .@@.
                                         .%+.          .+%.
                                          .+:          .+.
                                           ..         ...

                        ___________________.___________  _____________________ 
                        /   _____/\______   \   \______ \ \_   _____/\______   \
                         \_____  \  |     ___/   ||    |  \ |    __)_  |       _/
                        /        \ |    |   |   ||    `   \|        \ |    |   \
                        /_______  /|____|   |___/_______  /_______  / |____|_  /
                                \/                      \/        \/         \/"""

_BANNER_CREDIT = "                            [ Created by L4ZZ3RJ0D — @l4zz3rj0d ]"

_BANNER_SUB = "                   v{ver}  │  SPA + Non-SPA Engine  │  Full Intelligence Recon"

def print_banner():
    if _no_color():
        print(f"  HELLHOUND SPIDER v{VERSION}  —  Recon Engine")
        print(f"  {_BANNER_CREDIT.strip()}\n")
        return
    print(f"{C.R}{C.B}{_BANNER_ART}{C.RST}")
    print()
    print(f"{C.W}{_BANNER_CREDIT}{C.RST}")
    print()
    print(f"{C.RD}{_BANNER_SUB.format(ver=VERSION)}{C.RST}\n")

# ══════════════════════════════════════════════════════════════════════
# EMIT
# ══════════════════════════════════════════════════════════════════════

class Emit:
    """
    Tiers:
      .info / .success  — verbose only  (noisy discovery detail)
      .warn             — always        (critical findings / errors)
      .always_info      — always        (lifecycle events)
      .always_success   — always        (phase completions)
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._nc     = _no_color()

    # ── raw write ─────────────────────────────────────────────────────

    def _w(self, line: str):
        print(_strip(line) if self._nc else line, flush=True)

    # ── log helpers ───────────────────────────────────────────────────

    def info(self, msg: str):
        if self.verbose:
            self._w(f"{C.CYD}[~]{C.RST} {C.GR}{msg}{C.RST}")

    def success(self, msg: str):
        if self.verbose:
            self._w(f"{C.G}[+]{C.RST} {C.GD}{msg}{C.RST}")

    def warn(self, msg: str):
        self._w(f"{C.R}[!]{C.RST} {C.Y}{msg}{C.RST}")

    def always_info(self, msg: str):
        self._w(f"{C.CY}[*]{C.RST} {msg}")

    def always_success(self, msg: str):
        self._w(f"{C.G}{C.B}[✓]{C.RST} {C.B}{msg}{C.RST}")

    # ── structured output helpers (used by print_results) ────────────

    def section(self, title: str):
        """Bold red section divider."""
        bar = "═" * 72
        if self._nc:
            print(f"\n  {bar}\n    {title}\n  {bar}")
            return
        print(f"\n  {C.RD}{bar}{C.RST}")
        print(f"  {C.R}{C.B}  {title}{C.RST}")
        print(f"  {C.RD}{bar}{C.RST}")

    def row(self, label: str, value: str, label_colour=None, value_colour=None):
        lc = label_colour or C.CYD
        vc = value_colour or C.W
        if self._nc:
            print(f"    {label:<30}  {_strip(value)}")
        else:
            print(f"  {C.RD}│{C.RST}  {lc}{label:<30}{C.RST}  {vc}{value}{C.RST}")

    def finding(self, tag: str, severity: str, msg: str):
        sev_c = {
            "CRITICAL": C.R + C.B,
            "HIGH":     C.R,
            "MEDIUM":   C.Y,
            "LOW":      C.CYD,
            "INFO":     C.GL,
        }.get(severity.upper(), C.W)
        if self._nc:
            print(f"    [{severity:<8}] [{tag}] {msg}")
        else:
            print(
                f"  {C.RD}│{C.RST}"
                f"  {sev_c}[{severity:<8}]{C.RST}"
                f"  {C.MG}[{tag}]{C.RST}"
                f"  {msg}"
            )

    def endpoint_row(self, ep: dict):
        method = ep.get("methods", ["GET"])[0]
        conf   = ep.get("confidence_label", "LOW")
        url    = ep.get("url", "")
        auth   = "🔒" if ep.get("auth_required") else "  "
        sens   = "⚡" if ep.get("parameter_sensitive") else "  "

        mc = {
            "GET":    C.GD,  "POST":  C.Y,
            "PUT":    C.O,   "PATCH": C.O,
            "DELETE": C.R,   "WS":    C.MG,
        }.get(method, C.GL)

        cc = {
            "CONFIRMED": C.G,
            "HIGH":      C.Y,
            "MEDIUM":    C.CYD,
            "LOW":       C.GR,
        }.get(conf, C.GR)

        disp = url if len(url) <= 72 else url[:69] + "..."

        if self._nc:
            print(f"    {method:<7}  {conf:<10}  {_strip(auth)}{_strip(sens)}  {disp}")
        else:
            print(
                f"  {C.RD}│{C.RST}"
                f"  {mc}{C.B}{method:<7}{C.RST}"
                f"  {cc}{conf:<10}{C.RST}"
                f"  {auth}{sens}"
                f"  {C.W}{disp}{C.RST}"
            )

    def print_always(self, msg: str):
        self._w(msg)

# ══════════════════════════════════════════════════════════════════════
# RESULTS PRINTER  — replaces raw JSON dump
# ══════════════════════════════════════════════════════════════════════

def print_results(intel: dict, target: str, elapsed: float,
                  emit: Emit, saved_path: str = ""):

    s   = intel.get("summary", {})
    eps = intel.get("endpoints", [])
    nc  = emit._nc

    def _bad(v):
        """Red if > 0 (something found), grey if 0 (clean)."""
        if isinstance(v, int):
            if v == 0:
                return f"{C.GR}0{C.RST}" if not nc else "0"
            return f"{C.R}{C.B}{v}{C.RST}" if not nc else str(v)
        return str(v)

    def _good(v):
        """Green if > 0, grey if 0."""
        if isinstance(v, int):
            if v == 0:
                return f"{C.GR}0{C.RST}" if not nc else "0"
            return f"{C.G}{C.B}{v}{C.RST}" if not nc else str(v)
        return str(v)

    # ── top header ────────────────────────────────────────────────────
    print()
    if nc:
        print(f"  ══ SCAN COMPLETE ══  {target}")
    else:
        bar = "═" * 72
        tgt = target[:60] + "…" if len(target) > 60 else target
        print(f"  {C.R}{C.B}{bar}{C.RST}")
        print(f"  {C.R}{C.B}  SCAN COMPLETE{C.RST}  {C.GR}·{C.RST}  {C.W}{tgt}{C.RST}")
        print(f"  {C.R}{C.B}{bar}{C.RST}")

    # -- summary
    _NOISE_SRCS = frozenset({"Backup_Probe", "Backup_Suffix", "WellKnown", "Leaked_File"})
    _real_eps   = [e for e in eps if not all(src in _NOISE_SRCS for src in e.get("source", ["Crawl"]))]
    _backup_eps = [e for e in eps if all(src in _NOISE_SRCS for src in e.get("source", ["Crawl"]))]
    emit.section("SUMMARY")
    emit.row("Target",             target)
    emit.row("Scan Time",          f"{elapsed:.1f}s")
    emit.row("Crawled Endpoints",  _good(len(_real_eps)))
    emit.row("Confirmed",          _good(sum(1 for e in _real_eps if e.get("confidence_label") == "CONFIRMED")))
    emit.row("High Confidence",    _good(sum(1 for e in _real_eps if e.get("confidence_label") == "HIGH")))
    emit.row("Auth-Walled",        _good(s.get("auth_required", 0)),    value_colour=C.CY)
    emit.row("Param-Sensitive",    _good(s.get("parameter_sensitive", 0)), value_colour=C.Y)
    emit.row("Backup Files Found", _bad(len(_backup_eps)))
    emit.row("Secrets Found",      _bad(s.get("secrets", 0)))
    emit.row("CORS Issues",        _bad(s.get("cors_issues", 0)))
    emit.row("GraphQL Exposed",    _bad(s.get("graphql_exposed", 0)))
    emit.row("OpenAPI Exposed",    _bad(s.get("openapi_exposed", 0)))
    emit.row("SourceMaps Exposed", _bad(s.get("sourcemaps_exposed", 0)))
    tech = ", ".join(s.get("tech_stack", [])) or "unknown"
    tech_col = f"{C.MG}{tech}{C.RST}" if not nc else tech
    emit.row("Tech Stack", tech_col)

    # ── security findings ─────────────────────────────────────────────
    secrets    = intel.get("secrets", [])
    cors       = intel.get("cors_issues", [])
    gql        = intel.get("graphql", [])
    oas        = intel.get("openapi", [])
    sourcemaps = intel.get("sourcemaps", [])

    if any([secrets, cors, gql, oas, sourcemaps]):
        emit.section("SECURITY FINDINGS")

    for item in gql:
        emit.finding("GraphQL", "HIGH",
                     f"Introspection OPEN — {item.get('url','')}  "
                     f"({item.get('types_count','?')} types)")

    for item in oas:
        emit.finding("OpenAPI", "MEDIUM",
                     f"Spec exposed — {item.get('url','')}")

    for item in cors:
        sev = "HIGH" if item.get("allow_credentials") else "MEDIUM"
        emit.finding("CORS", sev,
                     f"{item.get('url','')}  "
                     f"origin={item.get('reflected','')}  "
                     f"creds={item.get('allow_credentials', False)}")

    for item in sourcemaps:
        emit.finding("SourceMap", "MEDIUM",
                     f"Exposed — {item.get('url','')}")

    for item in secrets:
        emit.finding(item.get("type", "Secret"), "HIGH",
                     f"{str(item.get('content',''))[:70]}  ← {item.get('source','')}")

    # ── endpoints table ───────────────────────────────────────────────
    if eps:
        emit.section(f"ENDPOINTS  ({len(eps)} discovered)")

        # column header
        if nc:
            print(f"    {'METHOD':<7}  {'CONFIDENCE':<10}  FLAGS  URL")
            print(f"    {'─'*66}")
        else:
            print(
                f"  {C.RD}│{C.RST}  "
                f"{C.GL}{'METHOD':<7}  {'CONFIDENCE':<10}  FLAGS  URL{C.RST}"
            )
            print(f"  {C.RD}│{C.RST}  {C.GR}{'─'*66}{C.RST}")

        order = {"CONFIRMED": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        _NOISE_SOURCES = frozenset({"Backup_Probe", "Backup_Suffix", "WellKnown", "Leaked_File"})
        # Separate real crawled EPs from backup-probe EPs for display
        real_eps = [
            e for e in eps
            if not all(s in _NOISE_SOURCES for s in e.get("source", ["Crawl"]))
        ]
        backup_eps = [
            e for e in eps
            if all(s in _NOISE_SOURCES for s in e.get("source", ["Crawl"]))
        ]
        sorted_eps = sorted(real_eps, key=lambda e: (
            order.get(e.get("confidence_label", "LOW"), 4), e.get("url", "")
        )) + sorted(backup_eps, key=lambda e: e.get("url", ""))
        shown    = sorted_eps[:200]
        overflow = len(sorted_eps) - len(shown)

        for ep in shown:
            emit.endpoint_row(ep)

        if overflow > 0:
            if nc:
                print(f"    … {overflow} more — see JSON report")
            else:
                print(f"  {C.RD}│{C.RST}  {C.GR}  … {overflow} more — see JSON report{C.RST}")

        # ── param map for interesting endpoints ──────────────────────
        # Only consider real crawled endpoints (not backup probe noise)
        interesting = [
            e for e in real_eps
            if (any(e.get("params",{}).get(b) for b in ("form","js","openapi","query","runtime"))
                or e.get("parameter_sensitive"))
        ][:40]

        if interesting:
            emit.section(f"PARAMETER MAP  ({len(interesting)} endpoints)")
            for ep in interesting:
                url = ep.get("url","")
                all_p: List[str] = []
                for b in ("form","js","openapi","query","runtime"):
                    all_p += ep.get("params",{}).get(b,[])
                all_p = list(dict.fromkeys(all_p))
                if not all_p:
                    continue

                method  = ep.get("methods",["GET"])[0]
                methods = "|".join(ep.get("methods",[]))
                disp    = url if len(url) <= 64 else url[:61] + "…"
                mc = {
                    "GET":    C.GD, "POST":  C.Y,
                    "PUT":    C.O,  "PATCH": C.O,
                    "DELETE": C.R,
                }.get(method, C.GL)

                if nc:
                    print(f"    {methods:<10}  {disp}")
                    print(f"    {'':10}  params: {', '.join(all_p)}")
                else:
                    print(
                        f"  {C.RD}│{C.RST}  "
                        f"{mc}{C.B}{methods:<10}{C.RST}  "
                        f"{C.W}{disp}{C.RST}"
                    )
                    print(
                        f"  {C.RD}│{C.RST}  "
                        f"{'':10}  "
                        f"{C.CYD}params:{C.RST}  "
                        f"{C.Y}{', '.join(all_p)}{C.RST}"
                    )

    # ── auth-walled ───────────────────────────────────────────────────
    auth_eps = [e for e in eps if e.get("auth_required")]
    if auth_eps:
        emit.section(f"AUTH-WALLED  ({len(auth_eps)} endpoints)")
        for ep in auth_eps[:40]:
            method = ep.get("methods",["GET"])[0]
            url    = ep.get("url","")
            if nc:
                print(f"    LOCK  {method:<7}  {url}")
            else:
                print(
                    f"  {C.RD}│{C.RST}  "
                    f"{C.R}🔒 {method:<7}{C.RST}  "
                    f"{C.GL}{url}{C.RST}"
                )

    # ── robots disallowed ─────────────────────────────────────────────
    robots = intel.get("robots_disallowed", [])
    if robots:
        emit.section(f"ROBOTS DISALLOWED  ({len(robots)} paths)")
        for path in robots[:50]:
            if nc:
                print(f"    Disallow: {path}")
            else:
                print(
                    f"  {C.RD}│{C.RST}  "
                    f"{C.O}Disallow:{C.RST}  "
                    f"{C.W}{path}{C.RST}"
                )

    # ── tech stack ────────────────────────────────────────────────────
    tech_list = intel.get("tech_stack", [])
    if tech_list:
        emit.section("TECH STACK")
        if nc:
            print(f"    {' · '.join(tech_list)}")
        else:
            sep = f"  {C.GR}·{C.RST}  "
            row = sep.join(f"{C.MG}{t}{C.RST}" for t in tech_list)
            print(f"  {C.RD}│{C.RST}  {row}")

    # ── footer ────────────────────────────────────────────────────────
    print()
    if saved_path:
        if nc:
            print(f"  [✓] Report saved  →  {saved_path}")
        else:
            print(
                f"  {C.G}{C.B}[✓]{C.RST}  "
                f"{C.B}Report saved{C.RST}  "
                f"{C.CYD}→{C.RST}  "
                f"{C.W}{saved_path}{C.RST}"
            )
    if nc:
        print(f"  HELLHOUND SPIDER v{VERSION}  ·  done.\n")
    else:
        bar = "═" * 72
        ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {C.RD}{bar}{C.RST}")
        print(
            f"  {C.R}{C.B}HELLHOUND SPIDER v{VERSION}{C.RST}"
            f"  {C.GR}·  complete  ·  {ts}{C.RST}"
        )
        print(f"  {C.RD}{bar}{C.RST}\n")


# ══════════════════════════════════════════════════════════════════════
# CONFIDENCE
# ══════════════════════════════════════════════════════════════════════

class Conf:
    LOW       = 1
    MEDIUM    = 3
    HIGH      = 6
    CONFIRMED = 10

    @staticmethod
    def label(score: int) -> str:
        if score >= Conf.CONFIRMED: return "CONFIRMED"
        if score >= Conf.HIGH:      return "HIGH"
        if score >= Conf.MEDIUM:    return "MEDIUM"
        return "LOW"

# ══════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════

class Config:
    def __init__(self, **kw):
        self.max_depth          = kw.get("max_depth",          4)
        self.concurrency        = kw.get("concurrency",        12)
        self.timeout            = kw.get("timeout",            15)
        self.max_retries        = kw.get("max_retries",        3)
        self.retry_base_delay   = kw.get("retry_base_delay",   0.5)
        self.max_urls_per_depth = kw.get("max_urls_per_depth", 500)
        self.jitter_min         = kw.get("jitter_min",         0.05)
        self.jitter_max         = kw.get("jitter_max",         0.35)
        self.verbose            = kw.get("verbose",            False)
        self.use_playwright     = kw.get("use_playwright",     True)
        self.enable_spa_interact = kw.get("enable_spa_interact", False)
        self.enable_probing     = kw.get("enable_probing",     True)
        self.enable_method_disc = kw.get("enable_method_disc", True)
        self.enable_graphql     = kw.get("enable_graphql",     True)
        self.enable_openapi     = kw.get("enable_openapi",     True)
        self.enable_cors        = kw.get("enable_cors",        True)
        self.output_format      = kw.get("output_format",      "json")
        self.output_file: Optional[str] = kw.get("output_file", None)
        self.user_agent = kw.get(
            "user_agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        self.extensions_to_ignore: List[str] = kw.get("extensions_to_ignore", [
            ".png",".jpg",".jpeg",".gif",".ico",".svg",".webp",
            ".woff",".woff2",".ttf",".eot",".css",
            ".mp4",".mp3",".avi",".mov",".webm",
            ".zip",".gz",".tar",".rar",".pdf",".exe",".dmg",".apk",
        ])

    def validate(self):
        if not (0 <= self.max_depth <= 20):
            raise ValueError("max_depth must be 0–20")
        if not (1 <= self.concurrency <= 100):
            raise ValueError("concurrency must be 1–100")

# ══════════════════════════════════════════════════════════════════════
# SESSION / COOKIE MANAGER
# ══════════════════════════════════════════════════════════════════════

class SessionManager:
    @staticmethod
    def parse_cookies(raw) -> Dict[str, str]:
        if not raw:
            return {}
        if isinstance(raw, dict):
            if any(k.lower() in ("authorization","x-api-key","x-auth-token") for k in raw):
                return {}
            return raw
        if isinstance(raw, str):
            raw = raw.strip()
            # Only attempt a filesystem lookup when the string is a plausible
            # path — short enough for the OS and looks like a file reference.
            # Long strings like JWTs must never reach Path.exists(); Linux
            # raises OSError "File name too long" for strings over ~255 bytes.
            _looks_like_path = (
                len(raw) <= 255
                and " " not in raw
                and ("/" in raw or raw.endswith((".txt", ".json")))
            )
            if _looks_like_path:
                try:
                    p = Path(raw)
                    if p.exists() and p.is_file():
                        return SessionManager._load_file(p)
                except OSError:
                    pass  # filesystem error — fall through to string parsing
            # Parse as inline cookie string: "name=value; name2=value2"
            # partition("=") keeps the full value even if it contains "="
            # (base64 padding, JWT segments, etc.)
            out: Dict[str, str] = {}
            for part in raw.split(";"):
                part = part.strip()
                if "=" in part:
                    k, _, v = part.partition("=")
                    k = k.strip(); v = v.strip()
                    if k:
                        out[k] = v
            return out
        return {}

    @staticmethod
    def _load_file(path: Path) -> Dict[str, str]:
        try:
            data = json.loads(path.read_text())
            if isinstance(data, list):
                return {c["name"]: c["value"] for c in data if "name" in c and "value" in c}
        except Exception:
            pass
        try:
            jar = MozillaCookieJar(str(path))
            jar.load(ignore_discard=True, ignore_expires=True)
            return {c.name: c.value for c in jar}
        except Exception:
            pass
        return {}

    @staticmethod
    def parse_auth_header(raw) -> Dict[str, str]:
        if not raw:
            return {}
        if isinstance(raw, dict):
            return {k: v for k, v in raw.items()
                    if k.lower() in ("authorization","x-api-key","x-auth-token",
                                     "x-csrf-token","x-access-token")}
        if isinstance(raw, str):
            raw = raw.strip()
            if re.match(r'^(Bearer|Basic|Token)\s+\S+', raw, re.I):
                return {"Authorization": raw}
        return {}

# ══════════════════════════════════════════════════════════════════════
# RATE LIMITER
# ══════════════════════════════════════════════════════════════════════

class DomainRateLimiter:
    def __init__(self, base_delay: float = 0.05):
        self._delays: Dict[str, float] = defaultdict(lambda: base_delay)
        self._locks:  Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def wait(self, domain: str):
        async with self._locks[domain]:
            await asyncio.sleep(self._delays[domain])

    def backoff(self, domain: str):
        self._delays[domain] = min(self._delays[domain] * 2.0, 10.0)

    def recover(self, domain: str):
        self._delays[domain] = max(self._delays[domain] * 0.9, 0.03)

# ══════════════════════════════════════════════════════════════════════
# FETCH HELPER
# ══════════════════════════════════════════════════════════════════════

async def fetch(session, method, url, rl, max_retries=3, base_delay=0.5, **kw):
    domain = urlparse(url).netloc
    await rl.wait(domain)
    for attempt in range(max_retries + 1):
        try:
            async with session.request(method, url, ssl=False, **kw) as resp:
                if resp.status == 429:
                    rl.backoff(domain)
                    await asyncio.sleep(float(resp.headers.get("Retry-After", base_delay * (2**attempt))))
                    continue
                body = await resp.text(errors="replace")
                rl.recover(domain)
                return resp.status, dict(resp.headers), body
        except Exception:
            if attempt < max_retries:
                await asyncio.sleep(base_delay * (2**attempt))
    return None, None, None

# ══════════════════════════════════════════════════════════════════════
# URL UTILITIES
# ══════════════════════════════════════════════════════════════════════

_ID_RE = re.compile(
    r'^(?:\d{1,20}'
    r'|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    r'|[0-9a-fA-F]{24}'
    r'|[0-9a-zA-Z]{20,}'
    r')$',
    re.I
)

def normalize(url: str) -> str:
    try:
        p  = urlparse(url)
        qs = urlencode(sorted(parse_qs(p.query, keep_blank_values=True).items()), doseq=True)
        return urlunparse((p.scheme.lower(), p.netloc.lower(),
                           p.path.rstrip("/") or "/", p.params, qs, ""))
    except Exception:
        return url

def cluster(url: str) -> str:
    try:
        p    = urlparse(url)
        segs = ["{id}" if _ID_RE.match(s) else s for s in p.path.split("/")]
        return urlunparse((p.scheme, p.netloc, "/".join(segs), "", "", ""))
    except Exception:
        return url

# ══════════════════════════════════════════════════════════════════════
# DATA STORE
# ══════════════════════════════════════════════════════════════════════

class Store:
    def __init__(self):
        self.endpoints:    Dict[str, dict] = {}
        self.comments:     List[dict]       = []
        self.secrets:      List[dict]       = []
        self.tech_stack:   Set[str]         = set()
        self.robots_paths: List[str]        = []
        self.cors_issues:  List[dict]       = []
        self.graphql:      List[dict]       = []
        self.openapi:      List[dict]       = []
        self.sourcemaps:   List[dict]       = []

    def _key(self, url, method):
        return f"{method.upper()}:{cluster(normalize(url))}"

    def _new_ep(self, url, method):
        return {
            "url": url, "cluster": cluster(normalize(url)),
            "methods": [method.upper()],
            "params": {"query":[],"form":[],"js":[],"openapi":[],"runtime":[]},
            "observed_values": {},
            "headers": {},
            "source": [], "confidence": 0, "confidence_label": "LOW",
            "auth_required": False, "parameter_sensitive": False,
            "observed_status": [], "baseline": None,
            # v12.0 additions
            "admin_panel":          False,
            "auth_classification":  [],
            "file_upload_candidate": False,
            "idor_candidate":       False,
            "idor_signals":         {},
            "sqli_candidate":       False,
            "sqli_params":          [],
            "cmdi_candidate":       False,
            "cmdi_params":          [],
        }

    def add_endpoint(self, url, method="GET", source="Static",
                     params=None, score=Conf.LOW, auth_required=False):
        key = self._key(url, method)
        if key not in self.endpoints:
            self.endpoints[key] = self._new_ep(url, method)
        ep = self.endpoints[key]
        if source not in ep["source"]:
            ep["source"].append(source)
        ep["confidence"]       = min(ep["confidence"] + score, Conf.CONFIRMED)
        ep["confidence_label"] = Conf.label(ep["confidence"])
        if auth_required:
            ep["auth_required"] = True
        if params:
            if source == "OpenAPI":
                bucket = "openapi"
            elif source == "Form":
                bucket = "form"
            elif source.startswith("JS_") or source in ("SPA_XHR", "SPA_DOM"):
                bucket = "js"
            else:
                bucket = "runtime"
            for p in params:
                if p and p not in ep["params"][bucket]:
                    ep["params"][bucket].append(p)
        return ep

    # Noise headers present on every browser request — no IDOR signal.
    _HEADER_SKIP = frozenset({
        "accept", "accept-encoding", "accept-language", "cache-control",
        "connection", "host", "origin", "pragma", "referer",
        "sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform",
        "sec-fetch-dest", "sec-fetch-mode", "sec-fetch-site",
        "upgrade-insecure-requests", "user-agent",
    })

    def merge_headers(self, url: str, method: str, headers: dict) -> bool:
        """
        Filter noise headers out, then merge remaining custom/auth headers into
        the endpoint's headers dict.  Keeps the first observed value per name.
        Returns True if any new header names were written.
        """
        if not headers:
            return False
        key = self._key(url, method)
        if key not in self.endpoints:
            return False
        ep    = self.endpoints[key]
        added = False
        for k, v in headers.items():
            lo = k.lower()
            if lo in self._HEADER_SKIP:
                continue
            if lo not in ep["headers"]:
                ep["headers"][lo] = v
                added = True
        return added

    def add_js_params(self, url, params):
        key = self._key(url, "GET")
        if key not in self.endpoints:
            self.endpoints[key] = self._new_ep(url, "GET")
        ep  = self.endpoints[key]
        new = [p for p in params if p not in ep["params"]["js"]]
        ep["params"]["js"].extend(new)
        if new:
            ep["confidence"] = min(ep["confidence"] + 1, Conf.CONFIRMED)
            ep["confidence_label"] = Conf.label(ep["confidence"])
        return bool(new)

    # High-risk param names — any endpoint bearing these warrants extra scrutiny
    _RISK_PARAMS = frozenset({
        "cmd","command","exec","run","shell","host","hostname","ip","addr","address",
        "url","uri","target","dest","src","source","file","path","dir","query","q",
        "search","input","arg","id","key","token","user","pass","passwd","password",
    })
    # Sanitization suffixes — strip these to get the base param name
    _PARAM_SUFFIXES = ("_raw","_sanitized","_input","_clean","_safe","_encoded","_value","_param")

    def add_runtime_params(self, url: str, method: str, names: List[str]) -> bool:
        """
        Strip sanitization suffixes FIRST, then store only the base name.
        Detects sanitization fingerprint: if a raw key like host_raw is seen,
        the base name host is stored AND the endpoint is auto-marked sensitive
        (because it proves the app is sanitizing an input whose unsanitized form
        was visible in the response).
        Returns True if any new base names were added.
        """
        key = self._key(url, method)
        if key not in self.endpoints:
            return False
        ep = self.endpoints[key]

        sanitization_seen = False
        added = []
        for raw_name in names:
            if not raw_name:
                continue
            base = raw_name
            is_suffixed = False
            for suf in self._PARAM_SUFFIXES:
                if raw_name.endswith(suf):
                    base = raw_name[: -len(suf)]
                    is_suffixed = True
                    break
            # If we saw a suffixed name → sanitization fingerprint
            if is_suffixed:
                sanitization_seen = True
            # Store only the base name
            if base and base not in ep["params"]["runtime"]:
                ep["params"]["runtime"].append(base)
                added.append(base)

        if added:
            ep["confidence"] = min(ep["confidence"] + 1, Conf.CONFIRMED)
            ep["confidence_label"] = Conf.label(ep["confidence"])

        if sanitization_seen:
            ep["parameter_sensitive"] = True
            ep["confidence"] = min(ep["confidence"] + 2, Conf.CONFIRMED)
            ep["confidence_label"] = Conf.label(ep["confidence"])

        return bool(added)

    def add_query_params(self, url):
        parsed = urlparse(url)
        if not parsed.query:
            return
        key = self._key(url, "GET")
        if key not in self.endpoints:
            self.endpoints[key] = self._new_ep(url, "GET")
        ep = self.endpoints[key]
        for param, values in parse_qs(parsed.query).items():
            if param not in ep["params"]["query"]:
                ep["params"]["query"].append(param)
            if values:
                existing = ep["observed_values"].setdefault(param, [])
                for v in values:
                    if v and v not in existing:
                        existing.append(v)

    def update_methods(self, url, methods):
        key = self._key(url, methods[0] if methods else "GET")
        if key not in self.endpoints:
            return
        ep = self.endpoints[key]
        for m in methods:
            if m not in ep["methods"]:
                ep["methods"].append(m)
        ep["confidence"] = min(ep["confidence"] + 1, Conf.CONFIRMED)
        ep["confidence_label"] = Conf.label(ep["confidence"])

    def record_status(self, url, method, status):
        key = self._key(url, method)
        if key in self.endpoints:
            ep = self.endpoints[key]
            if status not in ep["observed_status"]:
                ep["observed_status"].append(status)
            if status in (401, 403):
                ep["auth_required"] = True

    def mark_sensitive(self, url, method):
        key = self._key(url, method)
        if key in self.endpoints:
            ep = self.endpoints[key]
            ep["parameter_sensitive"] = True
            ep["confidence"] = min(ep["confidence"] + 2, Conf.CONFIRMED)
            ep["confidence_label"] = Conf.label(ep["confidence"])

    def add_comment(self, content, source_url):
        content = content.strip()
        if len(content) < 4 or any(c["content"] == content for c in self.comments):
            return False
        self.comments.append({"content": content, "source": source_url})
        return True

    def add_secret(self, val, stype, source_url):
        if any(s["content"] == val for s in self.secrets):
            return False
        self.secrets.append({"content": val, "type": stype, "source": source_url})
        return True

    def add_cors(self, url, origin_sent, reflected, creds):
        self.cors_issues.append({
            "url": url, "origin_sent": origin_sent, "reflected": reflected,
            "allow_credentials": creds, "severity": "HIGH" if creds else "MEDIUM"
        })

    def add_sourcemap(self, map_url, parent):
        if not any(s["url"] == map_url for s in self.sourcemaps):
            self.sourcemaps.append({"url": map_url, "parent": parent})

    def all_endpoints(self):
        return [e for e in self.endpoints.values() if e["confidence"] >= Conf.LOW]

    def export(self, target, fmt="json"):
        eps  = self.all_endpoints()
        meta = {"tool": f"Hellhound Spider v{VERSION}", "target": target}
        summary = {
            "total_endpoints":     len(eps),
            "confirmed":           sum(1 for e in eps if e["confidence_label"] == "CONFIRMED"),
            "high":                sum(1 for e in eps if e["confidence_label"] == "HIGH"),
            "auth_required":       sum(1 for e in eps if e["auth_required"]),
            "parameter_sensitive": sum(1 for e in eps if e["parameter_sensitive"]),
            "secrets":             len(self.secrets),
            "cors_issues":         len(self.cors_issues),
            "graphql_exposed":     len(self.graphql),
            "openapi_exposed":     len(self.openapi),
            "sourcemaps_exposed":  len(self.sourcemaps),
            "tech_stack":          sorted(self.tech_stack),
            # v12.0 additions
            "admin_panels":       sum(1 for e in eps if e.get("admin_panel")),
            "auth_endpoints":     sum(1 for e in eps if e.get("auth_classification")),
            "upload_endpoints":   sum(1 for e in eps if e.get("file_upload_candidate")),
            "idor_candidates":    sum(1 for e in eps if e.get("idor_candidate")),
            "sqli_candidates":    sum(1 for e in eps if e.get("sqli_candidate")),
            "cmdi_candidates":    sum(1 for e in eps if e.get("cmdi_candidate")),
        }
        data = {
            "meta": meta, "summary": summary, "endpoints": eps,
            "secrets": self.secrets, "cors_issues": self.cors_issues,
            "graphql": self.graphql, "openapi": self.openapi,
            "sourcemaps": self.sourcemaps, "comments": self.comments,
            "robots_disallowed": self.robots_paths,
            "tech_stack": sorted(self.tech_stack),
        }

        if fmt == "json":
            return json.dumps(data, indent=2)

        if fmt == "jsonl":
            lines = [json.dumps({"type":"meta","data":meta}),
                     json.dumps({"type":"summary","data":summary})]
            for ep in eps:
                lines.append(json.dumps({"type":"endpoint","data":ep}))
            return "\n".join(lines)

        if fmt == "csv":
            buf = io.StringIO()
            w   = csv.writer(buf)
            w.writerow(["url","cluster","methods","confidence","auth_required",
                         "param_sensitive","sources","query_params","form_params",
                         "js_params","openapi_params","status_codes","headers"])
            for ep in eps:
                w.writerow([ep["url"], ep["cluster"], "|".join(ep["methods"]),
                             ep["confidence_label"], ep["auth_required"],
                             ep["parameter_sensitive"], "|".join(ep["source"]),
                             "|".join(ep["params"].get("query",[])),
                             "|".join(ep["params"].get("form",[])),
                             "|".join(ep["params"].get("js",[])),
                             "|".join(ep["params"].get("openapi",[])),
                             "|".join(str(s) for s in ep.get("observed_status",[])),
                             json.dumps(ep.get("headers", {}))])
            return buf.getvalue()

        if fmt == "burp":
            root = ET.Element("items", burpVersion="2.0",
                              exportTime=datetime.now(timezone.utc).isoformat())
            for ep in eps:
                item = ET.SubElement(root, "item")
                ET.SubElement(item, "url").text          = ep["url"]
                ET.SubElement(item, "method").text       = ep["methods"][0]
                ET.SubElement(item, "confidence").text   = ep["confidence_label"]
                ET.SubElement(item, "authRequired").text = str(ep["auth_required"])
                ET.SubElement(item, "params").text       = json.dumps(ep["params"])
                ET.SubElement(item, "headers").text      = json.dumps(ep.get("headers", {}))
            return ET.tostring(root, encoding="unicode", xml_declaration=True)

        return json.dumps(data, indent=2)

# ══════════════════════════════════════════════════════════════════════
# EXTRACTORS
# ══════════════════════════════════════════════════════════════════════

class Extractor:
    _JS_NOISE = {
        "console","window","document","return","function","const","let","var",
        "this","class","import","export","default","null","undefined","true",
        "false","new","async","await","try","catch","if","else","for","while",
        "switch","case","break","continue","typeof","instanceof","void","delete",
    }
    _PARAM_RE = [
        r'body\s*:\s*JSON\.stringify\s*\(\s*\{([^}]{1,400})\}',
        r'axios\.(?:post|put|patch)\s*\([^,]{1,120},\s*\{([^}]{1,400})\}',
        r'(?:data|payload|body)\s*:\s*\{([^}]{1,400})\}',
        r'params\s*:\s*\{([^}]{1,400})\}',
        r'new\s+URLSearchParams\s*\(\s*\{([^}]{1,400})\}',
        r'FormData\s*\(\s*\)\s*;(?:[^}]{0,200}\.append\s*\(\s*["\']([^"\']+)["\'])',
    ]
    _SECRET_RE = [
        (r'\b([13][a-km-zA-HJ-NP-Z1-9]{25,34})\b',                       "Bitcoin_Address"),
        (r'\b(0x[a-fA-F0-9]{40})\b',                                      "Ethereum_Address"),
        (r'(AIza[0-9A-Za-z\-_]{35})',                                     "Google_API_Key"),
        (r'(AKIA[0-9A-Z]{16})',                                            "AWS_Access_Key"),
        (r'Bearer\s+([a-zA-Z0-9\-._~+/]{20,}=*)',                         "Bearer_Token"),
        (r'["\']sk-[a-zA-Z0-9]{20,}["\']',                                "Stripe_Key"),
        (r'gh[pousr]_[A-Za-z0-9_]{36,}',                                  "GitHub_PAT"),
        (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',                      "Private_Key_PEM"),
        (r'["\'](?:password|passwd|secret|api_?key|token)\s*["\']?\s*[:=]\s*["\']([^"\']{6,})["\']',
                                                                           "Hardcoded_Credential"),
        (r'["\']([0-9a-fA-F]{32})["\']',                                  "Possible_MD5"),
    ]
    # Pattern 1: quoted path containing API-style keywords
    # Pattern 2+3: fetch/axios/.method calls — capture FULL URL including ?qs (note: no ? in exclusion set)
    # Pattern 4: template literal base path
    # Pattern 5: broad same-origin path — catches /c7r3xq?pid=&text= style literals
    _API_RE = [
        r'["\']([/][a-zA-Z0-9_\-\.\/]*(?:api|v\d+|graphql|admin|auth|login|logout|rest|search|data|internal|upload|download)[a-zA-Z0-9_\-\.\/]*(?:\?[^"\'#\s]*)?)["\']',
        r'(?:fetch|axios)\s*\(\s*["\']([^"\'#\s]{5,})["\']',
        r'\.\s*(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\'#\s]{5,})["\']',
        r'`\$\{[^}]+\}(/[a-zA-Z0-9_\-\/]+(?:\?[^`#\s]*)?)`',
        r'(?:fetch|axios|\.\s*(?:get|post|put|delete|patch))\s*\(\s*["\']([/][^"\'#\s]{3,})["\']',
    ]

    @classmethod
    def _obj_keys(cls, block):
        keys = re.findall(r'["\']?([a-zA-Z_$][a-zA-Z0-9_$]*)["\']?\s*:', block)
        return [k for k in keys if k not in cls._JS_NOISE and len(k) > 1]

    @classmethod
    def _build_var_url_map(cls, text):
        """Pre-scan JS block for variable assignments like: const url = \"/path\"
        Returns dict of {varname: path} for URL association in js_params."""
        var_map = {}
        for m in re.finditer(
            r"""(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*["']([/][a-zA-Z0-9_\-\./?&=]+)["']""",
            text
        ):
            var_map[m.group(1)] = m.group(2)
        for m in re.finditer(
            r"""(?:url|endpoint|action|path|href)\s*:\s*["']([/][a-zA-Z0-9_\-\./]+)["']""",
            text
        ):
            var_map["__prop_%d" % m.start()] = m.group(1)
        return var_map

    @classmethod
    def _find_url_for_params(cls, text, match_start, match_end, base_url, var_map):
        """Find the URL most likely associated with a JS param block.
        Priority: (1) closest literal URL in 600 chars before the block,
        (2) first literal URL in 500 chars after, (3) known variable name
        within ±800 chars, (4) fallback to base_url (current page)."""
        url_lit = r"""["']([/][a-zA-Z0-9_\-\./]+(?:\?[^"'#\s]*)?)["']"""
        pre_window = text[max(0, match_start - 600): match_start]
        pre_matches = list(re.finditer(url_lit, pre_window))
        if pre_matches:
            return urljoin(base_url, pre_matches[-1].group(1).split("?")[0])
        post_window = text[match_end: match_end + 500]
        post_m = re.search(url_lit, post_window)
        if post_m:
            return urljoin(base_url, post_m.group(1).split("?")[0])
        for varname, vpath in var_map.items():
            if varname.startswith("__prop_"):
                if abs(int(varname[7:]) - match_start) <= 800:
                    return urljoin(base_url, vpath.split("?")[0])
            else:
                window = text[max(0, match_start - 800): match_end + 800]
                if re.search(r"\b" + re.escape(varname) + r"\b", window):
                    return urljoin(base_url, vpath.split("?")[0])
        return base_url

    @classmethod
    def js_params(cls, text, base_url, store, emit):
        var_map = cls._build_var_url_map(text)
        for pat in cls._PARAM_RE:
            for m in re.finditer(pat, text, re.S):
                keys = cls._obj_keys(m.group(1) if m.lastindex else m.group(0))
                if not keys:
                    continue
                turl = cls._find_url_for_params(text, m.start(), m.end(), base_url, var_map)
                if store.add_js_params(turl, keys):
                    emit.info("[JS-Params] %s -> %s" % (keys, turl))

    @classmethod
    def secrets(cls, text, url, store, emit):
        for pat, stype in cls._SECRET_RE:
            for m in re.finditer(pat, text):
                val = m.group(1) if m.lastindex else m.group(0)
                if stype not in ("Bitcoin_Address","Ethereum_Address","Private_Key_PEM",
                                  "Hardcoded_Credential","GitHub_PAT") and len(val) < 20:
                    continue
                if store.add_secret(val, stype, url):
                    emit.warn(f"[SECRET:{stype}] {val[:80]}")

    @classmethod
    def exposed_files(cls, text, base_url, store, emit):
        # Passive discovery of common backend/backup/config extensions
        _EXPOSED_RE = r'(?:https?://|//|/)[a-zA-Z0-9_\-\.\/]*\.(?:log|bak|sql|old|txt|zip|tar\.gz|env|json|xml|yml|yaml|ini|conf)\b'
        _seen = set()
        for m in re.finditer(_EXPOSED_RE, text, re.I):
            raw = m.group(0)
            if raw in _seen: continue
            _seen.add(raw)
            if raw.startswith("//"): full = "http:" + raw
            elif raw.startswith("/"): full = urljoin(base_url, raw)
            else: full = raw
            store.add_endpoint(full, source="Leaked_File", score=Conf.MEDIUM)
            emit.info(f"[Leaked-File] {full}")

    @classmethod
    def js_endpoints(cls, text, base_url, store, emit):
        # Dedup by (clean_path, frozenset(qs_params)) across all 5 patterns
        _seen_paths: set = set()
        for pat in cls._API_RE:
            for m in re.finditer(pat, text):
                raw = m.group(1)
                if not raw or not raw.startswith("/") or len(raw) < 3:
                    continue
                # Fix D + Fix 3: parse QS from the full literal BEFORE stripping
                _parsed    = urlparse(raw)
                _qs_params = list(parse_qs(_parsed.query).keys())
                clean_path = _parsed.path
                if not clean_path or clean_path == "/":
                    continue
                full = urljoin(base_url, clean_path)
                # Dedup: same endpoint from multiple patterns → merge params, skip re-emit
                _dedup_key = (full, frozenset(_qs_params))
                if _dedup_key in _seen_paths:
                    continue
                _seen_paths.add(_dedup_key)
                store.add_endpoint(full, source="JS_Analysis", score=Conf.MEDIUM)
                if _qs_params:
                    store.add_js_params(full, _qs_params)
                    emit.info(f"[JS-QS-Params] {_qs_params} ← {full}")
                emit.info(f"[JS-API] {full}")

    @classmethod
    def html_comments(cls, soup, url, store, emit):
        kw = {"todo","fixme","bug","admin","hidden","secret","debug","config",
              "key","password","cred","token","hack","temp","test","internal",
              "private","disabled","api","endpoint"}
        for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
            txt = c.strip()
            if len(txt) < 4:
                continue
            if (any(k in txt.lower() for k in kw)
                    or bool(re.match(r'^[/\.][a-z0-9_\-\.#]{3,}', txt))):
                if store.add_comment(txt, url):
                    emit.info(f"[Comment] {txt[:100]}")

    @classmethod
    def csp_hints(cls, headers, base_url, store, emit):
        csp = headers.get("Content-Security-Policy","") or headers.get("content-security-policy","")
        if not csp:
            return
        domain = urlparse(base_url).netloc
        for tok in csp.split():
            tok = tok.rstrip(";")
            if tok.startswith("/") and len(tok) > 2:
                store.add_endpoint(urljoin(base_url, tok), source="CSP", score=Conf.LOW)
            elif tok.startswith(("https://","http://")) and urlparse(tok).netloc != domain:
                emit.info(f"[CSP-3rd-party] {tok}")

# ══════════════════════════════════════════════════════════════════════
# GRAPHQL PROBER
# ══════════════════════════════════════════════════════════════════════

_GQL_PATHS = ["/graphql","/api/graphql","/gql","/query","/v1/graphql","/graphiql","/playground"]
_GQL_QUERY = '{"query":"{ __schema { queryType { name } types { name fields { name args { name } } } } }"}'

async def probe_graphql(session, base, store, emit, rl):
    for path in _GQL_PATHS:
        url = urljoin(base, path)
        s, _, text = await fetch(session, "POST", url, rl, data=_GQL_QUERY,
                                  headers={"Content-Type": "application/json"})
        if s and s < 400 and text and '"__schema"' in text:
            emit.warn(f"[GraphQL] Introspection OPEN → {url}")
            store.add_endpoint(url, method="POST", source="GraphQL", score=Conf.CONFIRMED)
            try:
                schema = json.loads(text)
                types  = schema.get("data",{}).get("__schema",{}).get("types",[])
                store.graphql.append({"url": url, "types_count": len(types), "schema": schema})
                emit.warn(f"[GraphQL] {len(types)} types exposed — disable introspection!")
            except Exception:
                pass
            return

# ══════════════════════════════════════════════════════════════════════
# OPENAPI PROBER
# ══════════════════════════════════════════════════════════════════════

_OAS_PATHS = [
    "/swagger.json","/swagger/v1/swagger.json","/swagger/v2/swagger.json",
    "/api-docs","/api-docs.json","/api-docs/swagger.json",
    "/openapi.json","/openapi.yaml","/openapi/v3/api-docs",
    "/v1/swagger.json","/v2/swagger.json","/v3/api-docs",
    "/.well-known/openapi","/api/swagger.json",
]

async def probe_openapi(session, base, store, emit, rl):
    for path in _OAS_PATHS:
        url = urljoin(base, path)
        s, _, text = await fetch(session, "GET", url, rl)
        if s != 200 or not text:
            continue
        try:
            spec = json.loads(text)
        except Exception:
            continue
        if not any(k in spec for k in ("paths","swagger","openapi")):
            continue
        emit.warn(f"[OpenAPI] Spec exposed → {url}")
        store.openapi.append({"url": url})
        server_prefix = ""
        for srv in spec.get("servers", []):
            u = srv.get("url","")
            if not u.startswith("http"):
                server_prefix = u
            break
        count = 0
        for ep_path, methods_obj in spec.get("paths", {}).items():
            for method, detail in methods_obj.items():
                if method.lower() not in ("get","post","put","patch","delete","head","options"):
                    continue
                clean  = (server_prefix + ep_path).replace("{","").replace("}","")
                full   = urljoin(base, clean)
                params = [p.get("name","") for p in detail.get("parameters",[]) if p.get("name")]
                bp: List[str] = []
                for ct_data in detail.get("requestBody",{}).get("content",{}).values():
                    bp += list(ct_data.get("schema",{}).get("properties",{}).keys())
                store.add_endpoint(full, method=method.upper(), source="OpenAPI",
                                   params=params+bp, score=Conf.CONFIRMED)
                emit.info(f"[OpenAPI] {method.upper()} {full} ({len(params+bp)} params)")
                count += 1
        emit.always_success(f"[OpenAPI] Mapped {count} endpoints from spec")
        return

# ══════════════════════════════════════════════════════════════════════
# INTELLIGENT PROBER
# ══════════════════════════════════════════════════════════════════════

class IntelligentProber:
    _METHODS = ["PUT", "PATCH", "DELETE", "HEAD", "TRACE"]

    # Param names to exclude from method oracle results (form/browser noise)
    _ORACLE_NOISE = frozenset({
        "viewport", "description", "author", "keywords", "charset",
        "submit", "button", "action", "method", "enctype",
    })

    def __init__(self, session, store, emit, rl, cfg):
        self.session = session; self.store = store
        self.emit = emit; self.rl = rl; self.cfg = cfg

    async def run(self):
        self.emit.always_info("Phase: Intelligent Probing…")

        _slug_re = re.compile(r'^[a-z][a-z0-9]{3,9}$')

        def _is_slug_path(url: str) -> bool:
            segs = urlparse(url).path.strip("/").split("/")
            return any(
                _slug_re.match(seg) and not seg.isalpha() and not seg.isdigit()
                for seg in segs
            )

        def _has_params(ep: dict) -> bool:
            return any(ep.get("params",{}).get(b) for b in ("form","js","openapi","query","runtime"))

        all_eps = self.store.all_endpoints()
        targets = [
            e for e in all_eps
            if (
                e.get("confidence", 0) >= Conf.MEDIUM
                or _has_params(e)
                or _is_slug_path(e.get("url",""))
            )
        ]
        # Sort by confidence descending, cap at 100
        targets = sorted(targets, key=lambda e: e.get("confidence", 0), reverse=True)[:100]

        self.emit.always_info(f"[Prober] {len(targets)} endpoints selected for probing")
        n_sens = n_meth = 0
        for ep in targets:
            url = ep["url"]; method = ep["methods"][0]
            s, hdrs, body = await fetch(self.session, method, url, self.rl)
            if s is None: continue
            self.store.record_status(url, method, s)
            bh = hashlib.md5(body.encode(errors="ignore")).hexdigest()
            ep["baseline"] = {"status": s, "hash": bh, "length": len(body)}
            probe = url + ("&" if "?" in url else "?") + f"_hh={int(time.time())}"
            s2, _, b2 = await fetch(self.session, method, probe, self.rl)
            if s2 and b2:
                h2 = hashlib.md5(b2.encode(errors="ignore")).hexdigest()
                if h2 != bh or abs(len(b2) - len(body)) > 50:
                    self.store.mark_sensitive(url, method)
                    self.emit.warn(f"[Sensitive] Param-reactive: {url}")
                    n_sens += 1
            if self.cfg.enable_method_disc:
                found = await self._methods(url, hdrs or {})
                if found:
                    self.store.update_methods(url, found)
                    self.emit.info(f"[Methods] {url} → {', '.join(found)}")
                    n_meth += 1

                # BUG-4 Upgrade: Method Oracle – parse error bodies for parameter names
                oracle_params = await self._method_oracle_params(url)
                if oracle_params:
                    changed = self.store.add_runtime_params(url, method, oracle_params)
                    if changed:
                        self.emit.info(f"[MethodOracle] Params discovered: {oracle_params} ← {url}")
            if self.cfg.enable_cors:
                await self._cors(url)
        self.emit.always_success(f"Probing done — sensitive: {n_sens}, new methods: {n_meth}")

    async def _methods(self, url, base_hdrs):
        found = []
        _, hdrs, _ = await fetch(self.session, "OPTIONS", url, self.rl)
        if hdrs:
            allow = hdrs.get("Allow","") or hdrs.get("allow","")
            if allow:
                return [m for m in self._METHODS if m in allow]
        for m in self._METHODS:
            s, _, _ = await fetch(self.session, m, url, self.rl,
                                   data="{}", headers={"Content-Type":"application/json"})
            if s is not None and s not in (405, 501, 400, 404):
                found.append(m)
        return found

    async def _cors(self, url):
        evil = "https://evil.hellhound.test"
        _, hdrs, _ = await fetch(self.session, "GET", url, self.rl, headers={"Origin": evil})
        if not hdrs: return
        acao = hdrs.get("Access-Control-Allow-Origin","") or hdrs.get("access-control-allow-origin","")
        acac = (hdrs.get("Access-Control-Allow-Credentials","") or
                hdrs.get("access-control-allow-credentials","")).lower() == "true"
        if acao and (acao == "*" or acao == evil):
            sev = "HIGH" if acac else "MEDIUM"
            self.store.add_cors(url, evil, acao, acac)
            self.emit.warn(f"[CORS:{sev}] {url} — origin reflected, creds={acac}")

    async def _method_oracle_params(self, url: str) -> List[str]:
        """
        Switch method from GET→POST and parse the error body for parameter names.
        Returns a list of discovered parameter names (may be empty).
        """
        discovered = []

        # Try POST with empty JSON body first (REST APIs)
        s, _, body = await fetch(
            self.session, "POST", url, self.rl,
            data="{}",
            headers={"Content-Type": "application/json"},
        )
        if body:
            discovered += self._parse_oracle_body(body)

        # If nothing found, try POST with empty form body (traditional apps)
        if not discovered:
            s2, _, body2 = await fetch(
                self.session, "POST", url, self.rl,
                data="",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if body2:
                discovered += self._parse_oracle_body(body2)

        # Deduplicate and filter noise
        seen = set()
        result = []
        for n in discovered:
            nl = n.lower()
            if nl in self._ORACLE_NOISE or nl in seen:
                continue
            seen.add(nl)
            result.append(n)
        return result

    def _parse_oracle_body(self, body: str) -> List[str]:
        """
        Extract parameter names from error/validation response bodies.
        Handles JSON structured errors AND plain text error messages.
        """
        found = []

        # --- JSON structured errors ---
        try:
            obj = json.loads(body)
            def _mine(o, depth=0):
                if depth > 4:
                    return
                if isinstance(o, dict):
                    for k, v in o.items():
                        # FastAPI/Pydantic loc arrays
                        if k == "loc" and isinstance(v, list):
                            for item in v:
                                if isinstance(item, str) and item not in ("body","query","path","__root__"):
                                    found.append(item)
                        # Missing/required arrays
                        elif k in ("missing","required","fields","params","parameters","expected") and isinstance(v, list):
                            for item in v:
                                if isinstance(item, str) and len(item) <= 60:
                                    found.append(item)
                        # Nested error objects: {"errors": {"fieldname": "msg"}}
                        elif k in ("errors","error","validation","detail") and isinstance(v, dict):
                            found.extend(vk for vk in v.keys() if isinstance(vk, str))
                        elif isinstance(v, (dict, list)):
                            _mine(v, depth + 1)
                elif isinstance(o, list):
                    for item in o:
                        _mine(item, depth + 1)
            _mine(obj)
        except Exception:
            pass

        # --- Plain text / HTML error messages ---
        text_patterns = [
            r"""(?:missing|required|invalid|unknown|bad)\s+(?:field|param|parameter|key|argument)[:\s]+["']?([a-zA-Z_][a-zA-Z0-9_]{2,40})["']?""",
            r"""["']([a-zA-Z_][a-zA-Z0-9_]{2,40})["']\s+(?:is required|is missing|not found|is invalid|cannot be blank)""",
            r"""(?:field|param|parameter|argument)[:\s]+["']?([a-zA-Z_][a-zA-Z0-9_]{2,40})["']?""",
            r"""(?:provide|supply|include|send)\s+(?:a\s+)?["']?([a-zA-Z_][a-zA-Z0-9_]{2,40})["']?""",
        ]
        for pat in text_patterns:
            for m in re.finditer(pat, body, re.I):
                n = m.group(1).strip()
                if n and len(n) <= 60:
                    found.append(n)

        return found

# ══════════════════════════════════════════════════════════════════════
# ROBOTS + SITEMAP PARSER
# Disallowed paths are crawled as high-value targets, not skipped.
# ══════════════════════════════════════════════════════════════════════

class RobotsParser:
    def __init__(self, session, base_url, store, queue, emit, rl, is_valid_fn):
        self.session = session; self.base_url = base_url
        self.store = store; self.queue = queue
        self.emit = emit; self.rl = rl; self.is_valid = is_valid_fn
        self.crawl_delay = 0.0
        self._sitemap_seen: Set[str] = set()

    async def run(self) -> float:
        url = urljoin(self.base_url, "/robots.txt")
        s, _, text = await fetch(self.session, "GET", url, self.rl)
        if s != 200 or not text:
            return 0.0
        self.emit.always_info(f"[Robots] Parsing {url}")
        dis_count = sit_count = 0
        for line in text.splitlines():
            line = line.strip(); lower = line.lower()
            if lower.startswith("crawl-delay:"):
                try:
                    self.crawl_delay = float(line.split(":",1)[1].strip())
                    self.emit.always_info(f"[Robots] Crawl-delay: {self.crawl_delay}s — honouring")
                except ValueError:
                    pass
            elif lower.startswith("disallow:"):
                path = line.split(":",1)[1].strip()
                if not path or path == "/": continue
                full = urljoin(self.base_url, path)
                if self.is_valid(full):
                    self.store.robots_paths.append(path)
                    self.store.add_endpoint(full, source="Robots_Disallow", score=Conf.MEDIUM)
                    self.queue.put_nowait((full, 1, "Robots_Disallow"))
                    dis_count += 1
                    self.emit.info(f"[Robots] Disallow queued: {path}")
            elif lower.startswith("allow:"):
                path = line.split(":",1)[1].strip()
                if path and path != "/":
                    full = urljoin(self.base_url, path)
                    if self.is_valid(full):
                        self.store.add_endpoint(full, source="Robots_Allow", score=Conf.LOW)
                        self.queue.put_nowait((full, 1, "Robots_Allow"))
                        self.emit.info(f"[Robots] Allow queued: {path}")
            elif lower.startswith("sitemap:"):
                sitemap_url = line.split(":",1)[1].strip()
                if not sitemap_url.startswith("http"):
                    sitemap_url = line.partition(":")[2].strip()
                await self.parse_sitemap(sitemap_url)
                sit_count += 1
        self.emit.always_info(
            f"[Robots] Done — {dis_count} disallow, {sit_count} sitemaps, "
            f"crawl-delay={self.crawl_delay}s")
        return self.crawl_delay

    async def parse_sitemap(self, sitemap_url: str):
        if sitemap_url in self._sitemap_seen: return
        self._sitemap_seen.add(sitemap_url)
        s, _, text = await fetch(self.session, "GET", sitemap_url, self.rl)
        if s != 200 or not text: return
        try:
            root = ET.fromstring(text)
        except ET.ParseError:
            return
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for loc in (root.findall("sm:sitemap/sm:loc", ns) or root.findall("sitemap/loc")):
            if loc.text: await self.parse_sitemap(loc.text.strip())
        count = 0
        for loc in (root.findall("sm:url/sm:loc", ns) or root.findall("url/loc")):
            u = (loc.text or "").strip()
            if u and self.is_valid(u):
                self.store.add_endpoint(u, source="Sitemap", score=Conf.LOW)
                self.queue.put_nowait((u, 1, "Sitemap"))
                count += 1
        if count:
            self.emit.always_info(f"[Sitemap] {sitemap_url} → {count} URLs queued")

# ══════════════════════════════════════════════════════════════════════
# SPA SCANNER
# ══════════════════════════════════════════════════════════════════════

class SPAScanner:
    def __init__(self, target_url, store, emit, cookies, extra_headers, queue, is_valid_fn, enable_spa_interact=False):
        self.target_url = target_url; self.store = store; self.emit = emit
        self.cookies = cookies; self.extra_headers = extra_headers
        self.queue = queue; self.is_valid = is_valid_fn
        self._enable_spa_interact = enable_spa_interact

    async def run(self):
        if not PLAYWRIGHT_AVAILABLE:
            self.emit.info("[SPA] Playwright not installed — skipping")
            return
        self.emit.always_info("[SPA] Launching headless Chromium…")
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True, args=[
                    "--no-sandbox","--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"])
                ctx_args: dict = {"ignore_https_errors": True}
                if self.cookies:
                    parsed = urlparse(self.target_url)
                    ctx_args["storage_state"] = {"cookies": [
                        {"name":k,"value":v,"domain":parsed.netloc,"path":"/"}
                        for k, v in self.cookies.items()]}
                if self.extra_headers:
                    ctx_args["extra_http_headers"] = self.extra_headers
                context = await browser.new_context(**ctx_args)
                await context.route(
                    re.compile(r'\.(png|jpg|jpeg|gif|svg|ico|woff2?|ttf|css|mp4|mp3)(\?.*)?$'),
                    lambda route, _: asyncio.create_task(route.abort()))
                page = await context.new_page()

                async def on_request(req):
                    url = req.url; rtype = req.resource_type; method = req.method or "GET"
                    if rtype in ("fetch","xhr"):
                        hdrs = dict(req.headers or {})
                        auth = any(h.lower() in ("authorization","cookie","x-auth-token")
                                   for h in hdrs)
                        self.store.add_endpoint(url, method=method, source="SPA_XHR",
                                                score=Conf.CONFIRMED, auth_required=auth)
                        if self.store.merge_headers(url, method, hdrs):
                            self.emit.info(f"[SPA-Headers] captured for {url}")
                        # S2: capture POST body params
                        if method == "POST":
                            try:
                                post_data = req.post_data
                                if post_data:
                                    try:
                                        body_obj = json.loads(post_data)
                                        if isinstance(body_obj, dict):
                                            self.store.add_endpoint(
                                                url, method="POST",
                                                source="SPA_XHR_POST",
                                                params=list(body_obj.keys()),
                                                score=Conf.CONFIRMED,
                                                auth_required=auth,
                                            )
                                    except Exception:
                                        parsed_body = parse_qs(post_data)
                                        if parsed_body:
                                            self.store.add_endpoint(
                                                url, method="POST",
                                                source="SPA_XHR_POST",
                                                params=list(parsed_body.keys()),
                                                score=Conf.CONFIRMED,
                                                auth_required=auth,
                                            )
                            except Exception:
                                pass
                        self.emit.success(f"[SPA-XHR] {method} {url}")
                    elif rtype == "websocket":
                        self.store.add_endpoint(url, method="WS", source="SPA_WebSocket",
                                                score=Conf.CONFIRMED)
                        self.emit.warn(f"[SPA-WS] WebSocket: {url}")
                    elif rtype == "script" and self.is_valid(url):
                        self.queue.put_nowait((url, 1, "SPA_Script"))

                page.on("request", on_request)

                # S1: capture XHR response bodies to harvest real object IDs
                async def on_response(resp):
                    try:
                        r_url    = resp.url
                        r_method = resp.request.method or "GET"
                        r_status = resp.status
                        r_rtype  = resp.request.resource_type
                        if r_rtype not in ("fetch", "xhr"):
                            return
                        if r_status not in range(200, 210):
                            return
                        ct = (resp.headers.get("content-type") or "").lower()
                        if "json" not in ct:
                            return
                        body = await resp.text()
                        if not body or len(body) > 512_000:
                            return
                        try:
                            obj = json.loads(body)
                        except Exception:
                            return
                        def _mine_resp(o, depth=0):
                            if depth > 3 or not isinstance(o, dict):
                                return
                            for k, v in o.items():
                                if re.match(
                                    r'^(?:id|uid|user_?id|order_?id|basket_?id|'
                                    r'item_?id|product_?id|address_?id|card_?id)$',
                                    str(k), re.I
                                ):
                                    vstr = str(v) if v is not None else ""
                                    if re.match(r'^\d{1,12}$', vstr):
                                        r_key = self.store._key(r_url, r_method)
                                        if r_key in self.store.endpoints:
                                            ep  = self.store.endpoints[r_key]
                                            obs = ep["observed_values"].setdefault(k, [])
                                            if vstr not in obs:
                                                obs.append(vstr)
                                                self.emit.info(
                                                    f"[SPA-ResponseID] {k}={vstr} ← {r_url}")
                                if isinstance(v, (dict, list)):
                                    _mine_resp(v, depth + 1)
                        if isinstance(obj, list):
                            for item in obj[:10]:
                                _mine_resp(item)
                        else:
                            _mine_resp(obj)
                    except Exception:
                        pass

                page.on("response", on_response)

                try:
                    await page.goto(self.target_url, wait_until="networkidle", timeout=20000)
                except Exception as e:
                    self.emit.info(f"[SPA] Goto warning: {e}")
                try:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(1.5)
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(0.5)
                except Exception:
                    pass
                # S4: wait for SPA to fully settle before interacting
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)
                    await asyncio.sleep(1.0)
                except Exception:
                    pass
                if self._enable_spa_interact:
                    await self._interact(page)
                await self._harvest_dom(page)
                await self._harvest_hash(page)
                await browser.close()
                self.emit.always_info("[SPA] Dynamic analysis complete")
        except Exception as e:
            self.emit.warn(f"[SPA] Error: {e}")

    async def _interact(self, page):
        """
        3-phase SPA interaction to trigger XHR calls universally.
        Phase 1: navigation clicks to load route-based content.
        Phase 2: fill and submit visible forms to trigger POST XHR calls.
        Phase 3: click remaining action buttons.
        """
        # Phase 1: navigation
        for sel in ["[role='menuitem']", "[role='tab']", ".nav-item",
                    "[data-toggle]", "a[href]:not([href^='http'])"]:
            try:
                for el in (await page.query_selector_all(sel))[:8]:
                    try:
                        if await el.is_visible():
                            await el.click(timeout=1500)
                            await asyncio.sleep(0.4)
                    except Exception:
                        pass
            except Exception:
                pass

        # Phase 2: fill and submit visible forms
        try:
            forms = await page.query_selector_all("form")
            for form in forms[:5]:
                try:
                    if not await form.is_visible():
                        continue
                    inputs = await form.query_selector_all(
                        "input[type='text'], input[type='email'], "
                        "input[type='number'], input:not([type])"
                    )
                    for inp in inputs[:6]:
                        try:
                            itype = await inp.get_attribute("type") or "text"
                            name  = (await inp.get_attribute("name") or "").lower()
                            if "email" in name or itype == "email":
                                await inp.fill("test@example.com", timeout=800)
                            elif "quantity" in name or "qty" in name or itype == "number":
                                await inp.fill("1", timeout=800)
                            else:
                                await inp.fill("test", timeout=800)
                        except Exception:
                            pass
                    submit = await form.query_selector(
                        "button[type='submit'], input[type='submit'], button:not([type])"
                    )
                    if submit and await submit.is_visible():
                        await submit.click(timeout=1500)
                        await asyncio.sleep(0.5)
                except Exception:
                    pass
        except Exception:
            pass

        # Phase 3: remaining action buttons
        try:
            for el in (await page.query_selector_all(
                "button:not([disabled]):not([type='submit'])"
            ))[:10]:
                try:
                    if await el.is_visible():
                        await el.click(timeout=1500)
                        await asyncio.sleep(0.3)
                except Exception:
                    pass
        except Exception:
            pass

    async def _harvest_dom(self, page):
        try:
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll('[href],[src],[action]'))
                    .map(e => e.href || e.src || e.action)
                    .filter(u => u && u.startsWith('/'))
            """)
            for path in (links or []):
                full = urljoin(self.target_url, path) if path.startswith("/") else path
                if self.is_valid(full):
                    self.store.add_endpoint(full, source="SPA_DOM", score=Conf.MEDIUM)
                    self.queue.put_nowait((full, 1, "SPA_DOM"))
        except Exception:
            pass

    async def _harvest_hash(self, page):
        try:
            src = await page.content()
            for r in re.findall(r'["\']#/([a-zA-Z0-9_\-/]+)["\']', src):
                url = self.target_url.rstrip("/") + "/#/" + r
                self.store.add_endpoint(url, source="SPA_HashRoute", score=Conf.MEDIUM)
                self.emit.info(f"[SPA-Hash] {url}")
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════════════
# CORE SPIDER
# ══════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════
# RECON UTILITIES (v12.0)
# ══════════════════════════════════════════════════════════════════════

_BACKUP_SUFFIXES = [".bak", ".old", ".orig", ".backup", ".tmp",
                    ".swp", ".save", "~", ".copy", ".1", ".2"]
_BACKUP_PATHS    = [
    "/backup.sql", "/dump.sql", "/database.sql", "/db.sql",
    "/backup.zip", "/site.zip", "/www.tar.gz",
    "/.git/HEAD", "/.git/config", "/.svn/entries",
    "/.env", "/.env.bak", "/.env.local", "/.env.production",
    "/config.php.bak", "/wp-config.php.bak",
    "/web.config.bak", "/application.yml.bak",
    "/id_rsa", "/id_rsa.pub", "/.ssh/id_rsa",
]

_ADMIN_PATTERNS = re.compile(
    r'/(?:admin|administrator|administration|manage|management|manager|'
    r'dashboard|control|panel|backend|backoffice|back-office|'
    r'staff|internal|superuser|root|god|devops|ops|'
    r'phpmyadmin|pma|adminer|pgadmin|dbadmin|'
    r'wp-admin|wp-login|cpanel|whm|plesk|'
    r'kibana|grafana|jenkins|sonarqube|portainer|traefik|'
    r'swagger|api-docs|graphiql|playground)(?:/|$)',
    re.I
)

_AUTH_PATTERNS = {
    "login":          re.compile(r'/(?:login|signin|sign-in|auth/login|oauth/login)', re.I),
    "logout":         re.compile(r'/(?:logout|signout|sign-out|auth/logout)', re.I),
    "register":       re.compile(r'/(?:register|signup|sign-up|create.?account|new.?user)', re.I),
    "token":          re.compile(r'/(?:token|oauth/token|auth/token|refresh.?token|access.?token)', re.I),
    "password_reset": re.compile(r'/(?:password.?reset|forgot.?password|reset.?password|recover)', re.I),
    "mfa":            re.compile(r'/(?:mfa|2fa|otp|totp|verify|confirm)', re.I),
}

_NUMERIC_ID_RE = re.compile(r'(?:^|[_\-/])(?:id|uid|user_id|order_id|item_id|record_id|object_id)$', re.I)
_PATH_ID_RE    = re.compile(r'/\d{1,12}(?:/|$)')
_UUID_PATH_RE  = re.compile(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)

_SQLI_PARAM_RE  = re.compile(r'^(?:id|uid|search|q|query|filter|order|sort|page|limit|'
                               r'category|type|name|user|username|email|product|item|'
                               r'start|end|from|to|where|group|having)$', re.I)
_CMDI_PARAM_RE  = re.compile(r'^(?:cmd|command|exec|run|shell|ping|host|ip|addr|address|'
                               r'url|uri|target|dest|src|source|file|path|dir|input|arg)$', re.I)

_WELL_KNOWN_PATHS = [
    "/.well-known/security.txt",
    "/.well-known/change-password",
    "/.well-known/openid-configuration",   # OAuth/OIDC discovery
    "/.well-known/oauth-authorization-server",
    "/.well-known/webfinger",
    "/.well-known/jwks.json",              # JWT public keys — feeds JWT config checker
    "/.well-known/assetlinks.json",        # Android app links
    "/.well-known/apple-app-site-association",
    "/.well-known/mta-sts.txt",
    "/.well-known/dnt-policy.txt",
]

class BackupProber:
    def __init__(self, session, target, store: Store, emit: Emit, rl):
        self.session = session
        self.target  = target
        self.store   = store
        self.emit    = emit
        self.rl      = rl

    async def run(self):
        self.emit.always_info("[Backup] Probing for exposed backup/config files…")
        found = 0
        for path in _BACKUP_PATHS:
            url = urljoin(self.target, path)
            s, hdrs, body = await fetch(self.session, "GET", url, self.rl)
            if s == 200 and body and len(body) > 10:
                ct = (hdrs or {}).get("content-type", "").lower()
                # Avoid false positives from HTML error pages returned as 200
                if "text/html" in ct and "<html" in body.lower():
                    continue
                self.store.add_endpoint(url, source="Backup_Probe", score=Conf.CONFIRMED)
                self.emit.warn(f"[BACKUP] Exposed: {url}  ({len(body)} bytes)")
                Extractor.secrets(body, url, self.store, self.emit)
                found += 1
        # Suffix sweep: only apply to REAL crawled endpoints (not backup/well-known sources)
        # and only to paths that look like plain API/file paths (no existing ext like .bak/.env)
        _SKIP_SOURCES = frozenset({"Backup_Probe", "Backup_Suffix", "WellKnown", "Leaked_File"})
        _EXT_RE = re.compile(r'\.(bak|old|backup|env|sql|zip|tar|gz|swp|tmp|copy|orig|log|conf|ini|yml|yaml)$', re.I)
        for ep in list(self.store.all_endpoints()):
            if ep.get("confidence_label") not in ("CONFIRMED", "HIGH"):
                continue
            # Skip endpoints added by backup/surface probers themselves
            if any(s in _SKIP_SOURCES for s in ep.get("source", [])):
                continue
            base_url = ep["url"].split("?")[0].rstrip("/")
            # Skip if the path already ends with a backup-like extension
            if _EXT_RE.search(base_url):
                continue
            # Skip bare-root or very short paths
            path_part = urlparse(base_url).path
            if not path_part or path_part in ("/", ""):
                continue
            for suf in _BACKUP_SUFFIXES:
                bak_url = base_url + suf
                if bak_url in [e["url"] for e in self.store.endpoints.values()]:
                    continue
                s, hdrs, body = await fetch(self.session, "GET", bak_url, self.rl)
                if s == 200 and body and len(body) > 10:
                    ct = (hdrs or {}).get("content-type", "").lower()
                    # Critical: skip HTML 200s — SPA apps return 200 for everything
                    if "text/html" in ct and "<html" in body.lower():
                        continue
                    self.store.add_endpoint(bak_url, source="Backup_Suffix",
                                            score=Conf.CONFIRMED)
                    self.emit.warn(f"[BACKUP-SUFFIX] Exposed: {bak_url}")
                    Extractor.secrets(body, bak_url, self.store, self.emit)
                    found += 1
        if found:
            self.emit.always_success(f"[Backup] {found} exposed files found")
        else:
            self.emit.always_info("[Backup] No exposed backup files found")

def classify_admin_endpoints(store: Store):
    for ep in store.endpoints.values():
        if _ADMIN_PATTERNS.search(ep["url"]):
            ep["admin_panel"] = True

def classify_auth_endpoints(store: Store):
    for ep in store.endpoints.values():
        for label, pat in _AUTH_PATTERNS.items():
            if pat.search(ep["url"]):
                ep.setdefault("auth_classification", [])
                if label not in ep["auth_classification"]:
                    ep["auth_classification"].append(label)

def classify_idor_candidates(store: Store):
    for ep in store.endpoints.values():
        url = ep["url"]
        all_params = []
        for b in ("query", "form", "js", "openapi", "runtime"):
            all_params += ep.get("params", {}).get(b, [])
        has_id_param = any(_NUMERIC_ID_RE.search(p) for p in all_params)
        has_id_path  = bool(_PATH_ID_RE.search(url) or _UUID_PATH_RE.search(url))
        if has_id_param or has_id_path:
            ep["idor_candidate"] = True
            ep["idor_signals"] = {
                "id_params":   [p for p in all_params if _NUMERIC_ID_RE.search(p)],
                "has_id_path": has_id_path,
            }

def score_injection_candidates(store: Store):
    for ep in store.endpoints.values():
        all_params = []
        for b in ("query", "form", "js", "openapi", "runtime"):
            all_params += ep.get("params", {}).get(b, [])
        sqli_params = [p for p in all_params if _SQLI_PARAM_RE.match(p)]
        cmdi_params = [p for p in all_params if _CMDI_PARAM_RE.match(p)]
        if sqli_params:
            ep["sqli_candidate"]  = True
            ep["sqli_params"]     = sqli_params
        if cmdi_params:
            ep["cmdi_candidate"]  = True
            ep["cmdi_params"]     = cmdi_params

def _flag_upload_endpoints(store: Store):
    upload_re = re.compile(
        r'/(?:upload|uploads|file|files|media|attachment|attachments|'
        r'import|ingest|document|documents|image|images|avatar|photo|'
        r'asset|assets|storage|blob|chunk|multipart)',
        re.I
    )
    for ep in store.endpoints.values():
        if upload_re.search(ep["url"]):
            ep["file_upload_candidate"] = True
        if any("file" in p.lower() or "upload" in p.lower()
               for p in ep.get("params", {}).get("form", [])):
            ep["file_upload_candidate"] = True

class Spider:
    def __init__(self, target, cfg, emit, cookies, extra_headers):
        self.target = target; self.cfg = cfg; self.emit = emit
        self.cookies = cookies; self.extra_headers = extra_headers
        self.base_domain = urlparse(target).netloc
        self.store = Store()
        self.visited: Set[str] = set()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.sem = asyncio.Semaphore(cfg.concurrency)
        self.rl = DomainRateLimiter()
        self._depth_cnt: Dict[int,int] = defaultdict(int)
        self.queue.put_nowait((target, 0, "Seed"))

    def is_valid(self, url):
        try:
            p = urlparse(url)
        except Exception:
            return False
        if p.netloc != self.base_domain: return False
        low = url.lower()
        if any(low.endswith(ext) or f"{ext}?" in low for ext in self.cfg.extensions_to_ignore):
            return False
        return bool(p.scheme in ("http","https"))

    def _over_budget(self, depth):
        return self._depth_cnt[depth] >= self.cfg.max_urls_per_depth

    def _detect_tech(self, headers, body, url):
        tech: Set[str] = set()
        srv = (headers.get("Server","") or headers.get("server","")).lower()
        xpb = (headers.get("X-Powered-By","") or headers.get("x-powered-by","")).lower()
        ct  = (headers.get("Content-Type","") or headers.get("content-type","")).lower()
        body_lo = body.lower()

        # ── Leakage: Expose highly verbose Server headers ───────────────
        raw_srv = headers.get("Server") or headers.get("server", "")
        raw_xpb = headers.get("X-Powered-By") or headers.get("x-powered-by", "")
        raw_asp = headers.get("X-AspNet-Version") or headers.get("x-aspnet-version", "")
        if raw_srv: tech.add(f"Server: {raw_srv}")
        if raw_xpb: tech.add(f"X-Powered-By: {raw_xpb}")
        if raw_asp: tech.add(f"X-AspNet-Version: {raw_asp}")

        # ── Server / infrastructure ──────────────────────────────────────
        if "nginx"        in srv:                               tech.add("Nginx")
        if "apache"       in srv:                               tech.add("Apache")
        if "cloudflare"   in srv:                               tech.add("Cloudflare")
        if "iis"          in srv:                               tech.add("IIS")
        if "gunicorn"     in srv:                               tech.add("Python/Gunicorn")
        if "werkzeug"     in srv:                               tech.add("Python/Werkzeug")
        if "jetty"        in srv:                               tech.add("Java/Jetty")
        if "tomcat"       in srv:                               tech.add("Java/Tomcat")
        if "lighttpd"     in srv:                               tech.add("Lighttpd")
        if "caddy"        in srv:                               tech.add("Caddy")

        # ── X-Powered-By ─────────────────────────────────────────────────
        if "php"          in xpb:                               tech.add("PHP")
        if "express"      in xpb:                               tech.add("Node.js/Express")
        if "asp.net"      in xpb:                               tech.add("ASP.NET")
        if "next.js"      in xpb:                               tech.add("Next.js")
        if "servlet"      in xpb or "jsp"       in xpb:        tech.add("Java")

        # ── Response headers (framework fingerprints) ────────────────────
        if headers.get("X-Shopify-Stage"):                      tech.add("Shopify")
        if headers.get("x-drupal-cache") or headers.get("X-Drupal-Cache"):
            tech.add("Drupal")
        if headers.get("x-pingback") or "xmlrpc.php" in body:  tech.add("WordPress")
        if headers.get("x-generator","").lower().startswith("drupal"):
            tech.add("Drupal")
        if "laravel_session" in (headers.get("set-cookie","") or "").lower():
            tech.add("Laravel")
        if "django" in (headers.get("set-cookie","") or "").lower():
            tech.add("Django")

        # ── Body — JavaScript frameworks (strict signals only) ───────────
        # Next.js — very specific marker
        if "_next/" in body or "__NEXT_DATA__" in body:         tech.add("Next.js")

        # Nuxt.js — specific marker
        if "__nuxt" in body or "_nuxt/" in body:                tech.add("Nuxt.js")

        # Angular (modern v2+) — use app-root + angular bundle markers
        # ng-version appears in dev; angular.json and zone.js appear in prod
        _is_angular = (
            "<app-root" in body or
            "ng-version=" in body or
            ("zone.js" in body_lo and "angular" in body_lo) or
            "platformBrowserDynamic" in body or
            "BrowserModule" in body
        )
        if _is_angular:
            tech.add("Angular")

        # AngularJS (v1.x) — must be an actual HTML attribute, not minified string
        if re.search(r'<[^>]+\bng-app\b', body) or re.search(r'<[^>]+\bng-controller\b', body):
            tech.add("AngularJS")

        # React — require specific React DOM markers, NOT just "react"
        # ReactDOM.render or createRoot are definitive
        # Exclude if Angular already detected (Angular bundles mention react in comments)
        _is_react = (
            "ReactDOM" in body or
            "react-dom" in body_lo or
            "__reactFiber" in body or
            "__reactProps" in body or
            ("data-reactroot" in body)
        )
        if _is_react and "Angular" not in tech:
            tech.add("React")

        # Vue.js — specific markers
        if "__vue_app__" in body or "v-bind:" in body or "data-v-" in body:
            tech.add("Vue.js")
        elif "vue" in body_lo and "v-app" in body:
            tech.add("Vue.js")

        # Svelte
        if "__svelte" in body or "svelte-" in body_lo:         tech.add("Svelte")

        # ── Body — Backend frameworks ────────────────────────────────────
        if "wp-content" in body or "wp-json" in body or "wp-login" in body:
            tech.add("WordPress")
        if "Drupal.settings" in body or "drupal.js" in body_lo:
            tech.add("Drupal")
        if "csrfmiddlewaretoken" in body_lo or "django" in body_lo and "__admin" in body_lo:
            tech.add("Django")
        if "laravel" in body_lo and ("csrf_token" in body_lo or "blade" in body_lo):
            tech.add("Laravel")
        if "rails-ujs" in body_lo or "data-remote=\"true\"" in body_lo:
            tech.add("Ruby on Rails")
        if "jsf" in body_lo and "javax.faces" in body_lo:
            tech.add("Java/JSF")

        # ── Body — Infrastructure/runtime ───────────────────────────────
        if "socket.io" in body_lo:                              tech.add("Socket.IO")
        if "graphql" in body_lo and ("__schema" in body or "introspection" in body_lo):
            tech.add("GraphQL")

        # ── Body — UI libraries ──────────────────────────────────────────
        # Bootstrap — require the actual CSS class patterns used in markup
        if re.search(r'class=["\'][^"\']*\b(?:navbar-brand|btn-primary|btn-secondary|col-md-|container-fluid)\b', body):
            tech.add("Bootstrap")
        if "jquery" in body_lo and ("$.ajax" in body or "$(document)" in body):
            tech.add("jQuery")
        if "material-icons" in body_lo or "mat-" in body_lo:   tech.add("Angular Material")

        new_tech = tech - self.store.tech_stack
        for t in tech:
            self.store.tech_stack.add(t)
        if new_tech:
            self.emit.always_info(f"[Tech] {', '.join(sorted(new_tech))}")

    async def _check_sourcemap(self, session, js_url):
        s, _, _ = await fetch(session, "GET", js_url + ".map", self.rl)
        if s == 200:
            self.emit.warn(f"[SourceMap] Exposed: {js_url}.map")
            self.store.add_sourcemap(js_url + ".map", js_url)

    def _queue_url(self, url, depth, source):
        if not self.is_valid(url): return
        norm = normalize(url)
        if norm in self.visited: return
        self.store.add_query_params(url)
        self.queue.put_nowait((url, depth, source))

    @staticmethod
    def _collect_json_keys(obj) -> List[str]:
        """
        Return ONLY the top-level string keys of a JSON object.
        No recursion — keys inside nested objects belong to their own
        endpoints, not the endpoint whose response body we are examining.
        If the root is a list, examine the first dict element only.
        """
        if isinstance(obj, dict):
            return [k for k in obj.keys() if isinstance(k, str)]
        if isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    return [k for k in item.keys() if isinstance(k, str)]
        return []

    @staticmethod
    def _strip_param_suffix(name: str) -> str:
        for suf in Store._PARAM_SUFFIXES:
            if name.endswith(suf):
                return name[: -len(suf)]
        return name

    def _extract_body_param_hints(self, url, body):
        """Scan any text response body for embedded field-name hints:
        validation error messages, JSON required-field arrays, name= echoes.
        Writes discovered names to the runtime bucket of the current endpoint."""
        found = []
        err_pats = [
            r"""(?:missing|required|invalid|unknown|bad)\s+(?:field|param|parameter|key|argument)[:\s]+["']?([a-zA-Z_][a-zA-Z0-9_]{2,40})["']?""",
            r"""["']([a-zA-Z_][a-zA-Z0-9_]{2,40})["']\s+(?:is required|is missing|not found|is invalid)""",
            r"""(?:field|param|parameter)[:\s]+["']([a-zA-Z_][a-zA-Z0-9_]{2,40})["']""",
        ]
        for pat in err_pats:
            for m in re.finditer(pat, body, re.I):
                n = m.group(1).strip()
                if n and n not in found:
                    found.append(n)
        for m in re.finditer(
            r"""["'](?:required|fields|params|parameters|missing|expected)["']\s*:\s*\[([^\]]{1,400})\]""",
            body, re.I
        ):
            for nm in re.finditer(r"""["']([a-zA-Z_][a-zA-Z0-9_]{2,40})["']""", m.group(1)):
                n = nm.group(1)
                if n not in found:
                    found.append(n)
        # Filter known meta-noise and og:/twitter: prefixed names
        _META_NOISE = frozenset({
            "viewport", "description", "author", "keywords", "robots", "theme-color",
            "generator", "referrer", "rating", "revisit-after", "copyright",
            "application-name", "msapplication-tilecolor", "msapplication-config",
            "format-detection", "apple-mobile-web-app-capable",
            "apple-mobile-web-app-status-bar-style", "apple-mobile-web-app-title",
            "og", "twitter",
        })
        for m in re.finditer(r"""name=["']([a-zA-Z_][a-zA-Z0-9_]{2,40})["']""", body):
            n = m.group(1)
            nl = n.lower()
            if nl in _META_NOISE or nl.startswith(("og:", "twitter:")):
                continue
            if n not in found:
                found.append(n)
        if found:
            self.store.add_endpoint(url, source="Body_Hints", score=Conf.LOW)
            changed = self.store.add_runtime_params(url, "GET", found)
            if changed:
                self.emit.info("[Body-Hints] %s <- %s" % (found, url))

    def _process_html(self, url, text, depth, source):
        soup = BeautifulSoup(text, "lxml")
        Extractor.html_comments(soup, url, self.store, self.emit)
        for tag in soup.find_all(["a","link","area"], href=True):
            href = tag.get("href","").strip()
            if href and not href.startswith(("javascript:","mailto:","tel:","#")):
                self._queue_url(urljoin(url, href), depth+1, "HTML_Link")
        for tag in soup.find_all("script", src=True):
            src = tag.get("src","").strip()
            if src:
                full = urljoin(url, src)
                if self.is_valid(full):
                    self._queue_url(full, depth+1, "HTML_Script")
        for tag in soup.find_all("script"):
            if not tag.get("src") and tag.string:
                Extractor.js_endpoints(tag.string, url, self.store, self.emit)
                Extractor.js_params(tag.string, url, self.store, self.emit)
                Extractor.secrets(tag.string, url, self.store, self.emit)
                Extractor.exposed_files(tag.string, url, self.store, self.emit)
        for form in soup.find_all("form"):
            action = form.get("action") or url
            full   = urljoin(url, action)
            method = (form.get("method") or "POST").upper()
            # Exhaustive field extraction: all named elements + data-* param hints
            inputs = []
            for el in form.find_all(["input","select","textarea","button","datalist"]):
                nm = el.get("name","").strip()
                if nm and nm not in inputs:
                    inputs.append(nm)
                for da in ("data-param","data-field","data-name","data-key","data-input"):
                    dv = el.get(da,"").strip()
                    if dv and dv not in inputs:
                        inputs.append(dv)
            # data-* on the form element itself (e.g. data-params="field1,field2")
            for da in ("data-params","data-fields","data-inputs"):
                dv = form.get(da,"").strip()
                if dv:
                    for part in re.split(r"[,;|\s]+", dv):
                        p = part.strip()
                        if p and p not in inputs:
                            inputs.append(p)
            if inputs: self.emit.info("[Form] %s %s <- [%s]" % (method, full, ", ".join(inputs)))
            # Fix C: register exact URL, write params directly to form bucket
            self.store.add_endpoint(full, method=method, source="Form", score=Conf.HIGH)
            self.store.add_query_params(full)
            _fkey = self.store._key(full, method)
            if _fkey in self.store.endpoints:
                _ep = self.store.endpoints[_fkey]
                for _p in inputs:
                    if _p and _p not in _ep["params"]["form"]:
                        _ep["params"]["form"].append(_p)
            self._queue_url(full, depth+1, "Form_Action")
        for attr in ("data-src","data-href","data-url"):
            for tag in soup.find_all(attrs={attr: True}):
                self._queue_url(urljoin(url, tag[attr]), depth+1, "DataAttr")
        for tag in soup.find_all("script", type="application/ld+json"):
            if tag.string:
                for m in re.finditer(r'"(?:url|@id|contentUrl|embedUrl)"\s*:\s*"([^"]+)"', tag.string):
                    self._queue_url(m.group(1), depth+1, "JSONLD")

    async def _process_js(self, url, text, session):
        Extractor.secrets(text, url, self.store, self.emit)
        Extractor.js_endpoints(text, url, self.store, self.emit)
        Extractor.js_params(text, url, self.store, self.emit)
        Extractor.exposed_files(text, url, self.store, self.emit)
        await self._check_sourcemap(session, url)
        for m in re.finditer(r'import\s*\(\s*["\']([^"\']+)["\']', text):
            full = urljoin(url, m.group(1))
            if self.is_valid(full): self._queue_url(full, 1, "JS_DynImport")
        for m in re.finditer(r'["\']\/(?:static|_next|assets)\/[a-zA-Z0-9._\-\/]+\.js["\']', text):
            path = m.group(0).strip('"\'')
            self._queue_url(urljoin(url, path), 1, "JS_Chunk")

    async def _worker(self, session, worker_id, crawl_delay):
        while True:
            acquired = False
            try:
                async with self.sem:
                    try:
                        url, depth, source = await asyncio.wait_for(self.queue.get(), timeout=4.0)
                        acquired = True
                    except asyncio.TimeoutError:
                        break
                    norm = normalize(url)
                    if norm in self.visited or depth > self.cfg.max_depth or self._over_budget(depth):
                        pass
                    else:
                        self.visited.add(norm)
                        self._depth_cnt[depth] += 1
                        s, hdrs, body = await fetch(session, "GET", url, self.rl,
                                                    max_retries=self.cfg.max_retries,
                                                    base_delay=self.cfg.retry_base_delay)
                        if s is not None and body is not None:
                            self.store.record_status(url, "GET", s)
                            if s in (401, 403):
                                self.store.add_endpoint(url, source=source,
                                                        score=Conf.MEDIUM, auth_required=True)
                                self.emit.warn(f"[Auth-wall:{s}] {url}")
                            elif s in (500, 501, 502, 503) and body:
                                # Error Leak: verbose stack traces or DB errors
                                _ERR_RE = re.compile(
                                    r'(?:Traceback|Exception in thread|SyntaxError|ParseError|'
                                    r'SQLSTATE|You have an error in your SQL|ORA-\d{5}|'
                                    r'Fatal error:|Warning:|Uncaught \w+Error|'
                                    r'at [a-zA-Z\.]+\([a-zA-Z]+\.java:\d+\))',
                                    re.I
                                )
                                if _ERR_RE.search(body):
                                    self.store.add_endpoint(url, source="Error_Leak", score=Conf.HIGH)
                                    self.store.add_secret(body[:200], "Error_Stack_Trace", url)
                                    self.emit.warn(f"[Error-Leak] Verbose error at {url}")
                            elif s == 200:
                                if depth <= 1:
                                    self._detect_tech(hdrs, body, url)
                                    Extractor.csp_hints(hdrs, url, self.store, self.emit)
                                ct = (hdrs.get("Content-Type","") or hdrs.get("content-type","")).lower()
                                if "text/html" in ct:
                                    self.store.add_endpoint(url, source=f"HTML({source})", score=Conf.MEDIUM)
                                    self._process_html(url, body, depth, source)
                                    self._extract_body_param_hints(url, body)
                                elif "javascript" in ct or url.split("?")[0].endswith(".js"):
                                    self.store.add_endpoint(url, source="JS_File", score=Conf.LOW)
                                    await self._process_js(url, body, session)
                                elif "json" in ct:
                                    self.store.add_endpoint(url, source="JSON_Response", score=Conf.MEDIUM)
                                    # -- Geo-location leak check
                                    _GEO_RE = re.compile(
                                        r'(?:"latitude"|"lat"|"lng"|"longitude"|"geo"|"coordinates")'
                                        r'\s*:\s*(-?\d{1,3}\.\d+)',
                                        re.I
                                    )
                                    for _gm in _GEO_RE.finditer(body):
                                        self.store.add_secret(
                                            f"GeoCoord: {_gm.group(0)[:60]}",
                                            "GeoLocation_Leak", url)
                                        self.emit.warn(f"[Geo-Leak] Coordinates exposed in response: {url}")
                                        break  # One warning per endpoint is enough
                                    # ── path strings in JSON values ────────────────
                                    for m in re.finditer(r'"([/][a-zA-Z0-9_\-\/]+)"', body):
                                        path = m.group(1)
                                        if len(path) > 3:
                                            full = urljoin(url, path)
                                            if self.is_valid(full):
                                                self.store.add_endpoint(full, source="JSON_Path", score=Conf.LOW)
                                                # Fix 6: queue for recursive crawl
                                                if not self._over_budget(depth + 1):
                                                    self._queue_url(full, depth + 1, "JSON_Path")
                                    # Body hints (error messages / required-fields in JSON body)
                                    self._extract_body_param_hints(url, body)
                                    # ── Fix A+B: top-level JSON keys → runtime params ──
                                    try:
                                        _jdata = json.loads(body)
                                        # top-level keys only (Fix B) — no recursion
                                        _top_keys = self._collect_json_keys(_jdata)
                                        # filter to high-risk base names (Fix A: strip before match)
                                        _risk = [
                                            k for k in _top_keys
                                            if self._strip_param_suffix(k) in Store._RISK_PARAMS
                                        ]
                                        if _risk:
                                            # add_runtime_params strips suffixes again before writing
                                            # (idempotent — handles both raw and already-base names)
                                            changed = self.store.add_runtime_params(url, "GET", _risk)
                                            if changed:
                                                _bases = self.store.endpoints[
                                                    self.store._key(url, "GET")
                                                ]["params"]["runtime"]
                                                self.emit.info(f"[JSON-Params] {_bases} ← {url}")
                                    except Exception:
                                        pass
                                elif "xml" in ct:
                                    try:
                                        root = ET.fromstring(body)
                                        ns = {"sm":"http://www.sitemaps.org/schemas/sitemap/0.9"}
                                        for loc in root.findall("sm:url/sm:loc", ns):
                                            if loc.text: self._queue_url(loc.text, depth+1, "XML_Sitemap")
                                    except Exception:
                                        pass
            except Exception:
                pass
            finally:
                if acquired:
                    self.queue.task_done()
                if acquired:
                    delay = crawl_delay if crawl_delay > 0 else random.uniform(
                        self.cfg.jitter_min, self.cfg.jitter_max)
                    await asyncio.sleep(delay)

    async def _probe_oidc(self, session, base):
        url = urljoin(base, "/.well-known/openid-configuration")
        s, _, text = await fetch(session, "GET", url, self.rl)
        if s != 200 or not text:
            return
        try:
            cfg = json.loads(text)
        except Exception:
            return
        oidc_keys = [
            "authorization_endpoint", "token_endpoint", "userinfo_endpoint",
            "end_session_endpoint", "introspection_endpoint", "revocation_endpoint",
            "jwks_uri", "registration_endpoint",
        ]
        for key in oidc_keys:
            ep_url = cfg.get(key)
            if ep_url and isinstance(ep_url, str):
                self.store.add_endpoint(ep_url, source="OIDC_Discovery", score=Conf.CONFIRMED,
                                        auth_required=True)
                self.emit.always_success(f"[OIDC] {key}: {ep_url}")

    async def run(self):
        req_headers = {
            "User-Agent": self.cfg.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "application/json;q=0.8,*/*;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
        }
        req_headers.update(self.extra_headers)
        connector = aiohttp.TCPConnector(limit=self.cfg.concurrency, ttl_dns_cache=300, ssl=False)
        timeout   = aiohttp.ClientTimeout(total=self.cfg.timeout)
        async with aiohttp.ClientSession(headers=req_headers, cookies=self.cookies,
                                          timeout=timeout, connector=connector) as session:
            if self.cfg.enable_graphql:
                await probe_graphql(session, self.target, self.store, self.emit, self.rl)
            if self.cfg.enable_openapi:
                await probe_openapi(session, self.target, self.store, self.emit, self.rl)
            robots = RobotsParser(session, self.target, self.store, self.queue,
                                  self.emit, self.rl, self.is_valid)
            crawl_delay = await robots.run()

            # Fix 5: unconditionally probe canonical sitemap paths
            # (robots.run may have already parsed some — RobotsParser deduplicates by URL)
            for _smap in ("/sitemap.xml", "/sitemap_index.xml", "/.well-known/sitemap.xml"):
                _smap_url = urljoin(self.target, _smap)
                if _smap_url not in robots._sitemap_seen:
                    _s, _, _t = await fetch(session, "GET", _smap_url, self.rl)
                    if _s == 200 and _t:
                        await robots.parse_sitemap(_smap_url)

            # Fix 5: Expanded well-known paths (v12.0)
            for _wk in _WELL_KNOWN_PATHS:
                _wk_url = urljoin(self.target, _wk)
                _s, _, _t = await fetch(session, "GET", _wk_url, self.rl)
                if _s == 200 and _t:
                    self.store.add_endpoint(_wk_url, source="WellKnown", score=Conf.LOW)
                    self.emit.always_success(f"[.well-known] Found: {_wk_url}")
                    
                    if _wk.endswith("openid-configuration"):
                        await self._probe_oidc(session, self.target)

                    # Extract any URL-like paths from the body
                    for _m in re.finditer(r'(?:^|\s)((?:https?://[^\s]+|/[a-zA-Z0-9_\-/]+))', _t, re.M):
                        _path = _m.group(1).strip()
                        if _path.startswith("/"):
                            _full = urljoin(self.target, _path)
                            if self.is_valid(_full):
                                self.store.add_endpoint(_full, source="WellKnown", score=Conf.LOW)
                                self._queue_url(_full, 1, "WellKnown")
            if self.cfg.use_playwright:
                spa = SPAScanner(self.target, self.store, self.emit, self.cookies,
                                 self.extra_headers, self.queue, self.is_valid,
                                 enable_spa_interact=self.cfg.enable_spa_interact)
                await spa.run()
            self.emit.always_info(
                f"[Spider] Crawl started — depth={self.cfg.max_depth}, "
                f"concurrency={self.cfg.concurrency}, "
                f"auth={'yes' if self.cookies or self.extra_headers else 'no'}, "
                f"seed={self.queue.qsize()} URLs")
            workers = [asyncio.create_task(self._worker(session, i, crawl_delay))
                       for i in range(self.cfg.concurrency)]
            await self.queue.join()
            for w in workers: w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            if self.cfg.enable_probing:
                prober = IntelligentProber(session, self.store, self.emit, self.rl, self.cfg)
                await prober.run()

                # v12.0 Upgrades: Active Probes & Classification
                backup_probe = BackupProber(session, self.target, self.store, self.emit, self.rl)
                await backup_probe.run()

                # Run classification passes
                # No network I/O — pure store operations
                classify_admin_endpoints(self.store)
                classify_auth_endpoints(self.store)
                classify_idor_candidates(self.store)
                score_injection_candidates(self.store)
                _flag_upload_endpoints(self.store)

# ══════════════════════════════════════════════════════════════════════
# DIFF ENGINE
# ══════════════════════════════════════════════════════════════════════

def diff_crawls(old_json: str, new_json: str) -> dict:
    old = json.loads(old_json); new = json.loads(new_json)
    om  = {e["cluster"]: e for e in old.get("endpoints",[])}
    nm  = {e["cluster"]: e for e in new.get("endpoints",[])}
    ok, nk = set(om), set(nm)
    added   = [nm[k] for k in (nk - ok)]
    removed = [om[k] for k in (ok - nk)]
    changed = []
    for k in ok & nk:
        o, n = om[k], nm[k]; diff: dict = {}
        if set(o["methods"]) != set(n["methods"]):
            diff["methods"] = {"old": o["methods"], "new": n["methods"]}
        if o["confidence_label"] != n["confidence_label"]:
            diff["confidence"] = {"old": o["confidence_label"], "new": n["confidence_label"]}
        if o["auth_required"] != n["auth_required"]:
            diff["auth_required"] = {"old": o["auth_required"], "new": n["auth_required"]}
        if diff: changed.append({"cluster": k, "url": n["url"], "changes": diff})
    return {"old_target": old.get("meta",{}).get("target"),
            "new_target": new.get("meta",{}).get("target"),
            "added": added, "removed": removed, "changed": changed,
            "summary": {"added": len(added), "removed": len(removed), "changed": len(changed)}}

# ══════════════════════════════════════════════════════════════════════
# AUTO-SAVE  — always writes JSON; optional extra format file
# ══════════════════════════════════════════════════════════════════════

def _auto_save(store: Store, target: str, out_path: Optional[str],
               fmt: str, emit: Emit) -> str:
    """Always saves a .json report. Returns the path saved."""
    domain    = re.sub(r'[^a-zA-Z0-9_\-]', '_', urlparse(target).netloc)
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_path if (out_path and out_path.endswith(".json")) \
                else f"hellhound_{domain}_{ts}.json"

    try:
        Path(json_path).write_text(store.export(target, fmt="json"))
        emit.always_info(f"[Report] JSON saved → {json_path}")
    except Exception as e:
        emit.warn(f"[Report] JSON save failed: {e}")
        json_path = ""

    # If extra format requested with an explicit path, save it too
    if out_path and fmt != "json":
        try:
            Path(out_path).write_text(store.export(target, fmt=fmt))
            emit.always_info(f"[Report] {fmt.upper()} saved → {out_path}")
        except Exception as e:
            emit.warn(f"[Report] {fmt.upper()} save failed: {e}")

    return json_path

# ══════════════════════════════════════════════════════════════════════
# MODULE ENTRY (Hellhound framework)
# ══════════════════════════════════════════════════════════════════════

def run(target: str, emit_obj, options: dict = None, stop_check=None, pause_check=None):
    opts    = options or {}
    cookies = SessionManager.parse_cookies(opts.get("cookie") or opts.get("auth"))
    xhdrs   = SessionManager.parse_auth_header(opts.get("headers", {}))
    cfg     = Config(**{k: v for k, v in opts.items() if k not in ("cookie","auth","headers")})
    cfg.validate()

    class _W:
        def __init__(self, b, v): self._b = b; self._v = v
        def info(self, m):
            if self._v: self._b.info(m)
        def success(self, m):
            if self._v: self._b.success(m)
        def warn(self, m):            self._b.warn(m)
        def always_info(self, m):     self._b.info(m)
        def always_success(self, m):  self._b.success(m)
        def section(self, t):         self._b.info(f"── {t} ──")
        def row(self, k, v, **kw):    self._b.info(f"{k}: {_strip(str(v))}")
        def finding(self, *a):        self._b.warn(str(a))
        def endpoint_row(self, ep):   self._b.info(ep.get("url",""))
        def print_always(self, m):    print(m)
        @property
        def _nc(self): return True

    emit = _W(emit_obj, cfg.verbose)
    return _do_run(target, cfg, emit, cookies, xhdrs)

# ══════════════════════════════════════════════════════════════════════
# SHARED RUN LOGIC
# ══════════════════════════════════════════════════════════════════════

def _do_run(target: str, cfg: Config, emit,
            cookies: Dict[str, str], extra_headers: Dict[str, str]) -> dict:
    if not target.startswith("http"):
        target = "https://" + target

    emit.always_info(f"Hellhound Spider v{VERSION} — {target}")
    start = time.time()

    spider: Optional[Spider] = None
    try:
        spider = Spider(target, cfg, emit, cookies, extra_headers)
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(spider.run())
    except KeyboardInterrupt:
        emit.warn("Scan interrupted — partial results follow")
    except ValueError as e:
        emit.warn(f"Config error: {e}")
        return {"raw": str(e), "intel": {}}
    except Exception as e:
        emit.warn(f"Spider error: {e}")

    if spider is None:
        return {"raw": "Spider failed to initialize.", "intel": {}}

    elapsed = time.time() - start

    # Always auto-save JSON
    json_path = _auto_save(spider.store, target, cfg.output_file,
                           cfg.output_format, emit)

    intel  = json.loads(spider.store.export(target, fmt="json"))
    result = {"raw": "", "intel": intel}

    # Print rich CLI results
    print_results(intel, target, elapsed, emit, saved_path=json_path)

    return result

# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hellhound_spider",
        description=(
            f"{C.R}{C.B}Hellhound Spider v{VERSION}{C.RST}  —  "
            "SPA + Non-SPA Web Crawler & Endpoint Discoverer"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"\n{C.GR}  ── Examples ────────────────────────────────────────────────────\n\n"
            f"  python3 spider.py https://target.com\n"
            f"  python3 spider.py https://target.com --verbose\n"
            f"  python3 spider.py https://target.com --cookie \"s=abc; csrf=xy\"\n"
            f"  python3 spider.py https://target.com --cookie /path/cookies.txt\n"
            f"  python3 spider.py https://target.com --auth \"Bearer eyJhbGci...\"\n"
            f"  python3 spider.py https://target.com --depth 5 --out report.json\n"
            f"  python3 spider.py https://target.com --format csv --out e.csv\n"
            f"  python3 spider.py https://target.com --no-playwright\n"
            f"  python3 spider.py https://target.com --spa-interact\n"
            f"  python3 spider.py https://target.com --diff old.json\n"
            f"\n  JSON report is always auto-saved even without --out.{C.RST}\n"
        ),
    )

    p.add_argument("target", help="Target URL  (e.g. https://example.com)")

    scan = p.add_argument_group(f"{C.CY}Scan Options{C.RST}")
    scan.add_argument("--depth",   "-d",  type=int, default=4,  metavar="N",
                      help="Max crawl depth  (default: 4)")
    scan.add_argument("--concurrency",     type=int, default=12, metavar="N",
                      help="Concurrent workers  (default: 12)")
    scan.add_argument("--timeout",         type=int, default=15, metavar="S",
                      help="Per-request timeout in seconds  (default: 15)")
    scan.add_argument("--verbose", "-v",  action="store_true",
                      help="Show all discovery logs")

    auth = p.add_argument_group(f"{C.CY}Authentication{C.RST}")
    auth.add_argument("--cookie",  type=str, default=None, metavar="COOKIE",
                      help="Cookie string, dict, or path to cookie file")
    auth.add_argument("--auth",    type=str, default=None, metavar="HEADER",
                      help='Authorization header  e.g. "Bearer eyJ..."')

    out = p.add_argument_group(f"{C.CY}Output{C.RST}")
    out.add_argument("--out",      type=str, default=None, metavar="FILE",
                     help="Extra output file  (JSON always auto-saved)")
    out.add_argument("--format",   type=str, default="json",
                     choices=["json","jsonl","csv","burp"],
                     help="Extra output format  (default: json)")

    flags = p.add_argument_group(f"{C.CY}Feature Flags{C.RST}")
    flags.add_argument("--no-playwright", action="store_true",
                       help="Disable headless browser SPA scanning")
    flags.add_argument("--no-probing",    action="store_true",
                       help="Disable intelligent probing phase")
    flags.add_argument("--spa-interact", action="store_true",
                       help="Enable SPA form filling and button clicking (use only on authorized targets)")
    flags.add_argument("--no-cors",       action="store_true",
                       help="Disable CORS misconfiguration checks")
    flags.add_argument("--no-graphql",    action="store_true",
                       help="Disable GraphQL introspection probe")
    flags.add_argument("--no-openapi",    action="store_true",
                       help="Disable OpenAPI / Swagger discovery")

    util = p.add_argument_group(f"{C.CY}Utilities{C.RST}")
    util.add_argument("--diff",    type=str, default=None, metavar="OLD_REPORT",
                      help="Diff this scan against an old JSON report")

    return p


def main():
    parser = _build_parser()
    args   = parser.parse_args()

    emit = Emit(verbose=args.verbose)
    print_banner()

    # Pre-flight info block
    nc = emit._nc
    def _pf(label, value, vc=None):
        vc = vc or C.W
        if nc:
            print(f"  {label:<18}  {_strip(value)}")
        else:
            print(f"  {C.CYD}{label:<18}{C.RST}  {vc}{value}{C.RST}")

    _pf("Target",      args.target)
    _pf("Depth",       str(args.depth))
    _pf("Concurrency", str(args.concurrency))
    _pf("Timeout",     f"{args.timeout}s")
    _pf("Playwright",
        "enabled" if (not args.no_playwright and PLAYWRIGHT_AVAILABLE) else "disabled",
        C.G if (not args.no_playwright and PLAYWRIGHT_AVAILABLE) else C.GR)
    _pf("Verbose",
        "on" if args.verbose else "off",
        C.G if args.verbose else C.GR)
    print()

    cookies = SessionManager.parse_cookies(args.cookie)
    xhdrs   = SessionManager.parse_auth_header(args.auth or "")

    if cookies:
        emit.always_info(f"[Auth] Cookies loaded  →  {list(cookies.keys())}")
    elif xhdrs:
        emit.always_info(f"[Auth] Header auth     →  {list(xhdrs.keys())}")
    else:
        emit.always_info("[Auth] No credentials — unauthenticated scan")

    cfg = Config(
        max_depth       = args.depth,
        concurrency     = args.concurrency,
        timeout         = args.timeout,
        verbose         = args.verbose,
        use_playwright  = not args.no_playwright,
        enable_spa_interact = args.spa_interact,
        enable_probing  = not args.no_probing,
        enable_cors     = not args.no_cors,
        enable_graphql  = not args.no_graphql,
        enable_openapi  = not args.no_openapi,
        output_format   = args.format,
        output_file     = args.out,
    )

    try:
        cfg.validate()
    except ValueError as e:
        emit.warn(str(e))
        sys.exit(1)

    print()
    result = _do_run(args.target, cfg, emit, cookies, xhdrs)

    # ── diff mode ─────────────────────────────────────────────────────
    if args.diff:
        try:
            old  = Path(args.diff).read_text()
            new  = json.dumps(result["intel"], indent=2)
            diff = diff_crawls(old, new)
            emit.section(f"DIFF  vs  {args.diff}")
            emit.row("Added",   str(diff["summary"]["added"]),   value_colour=C.R)
            emit.row("Removed", str(diff["summary"]["removed"]), value_colour=C.GR)
            emit.row("Changed", str(diff["summary"]["changed"]), value_colour=C.Y)
            if diff["added"]:
                print()
                emit.always_info(f"New endpoints ({len(diff['added'])}):")
                for ep in diff["added"]:
                    emit.finding("NEW", "HIGH", ep["url"])
            if diff["removed"]:
                print()
                emit.always_info(f"Gone endpoints ({len(diff['removed'])}):")
                for ep in diff["removed"]:
                    emit.finding("GONE", "INFO", ep["url"])
        except Exception as e:
            emit.warn(f"[Diff] Error: {e}")


if __name__ == "__main__":
    main()