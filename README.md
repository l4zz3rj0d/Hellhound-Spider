<p align="center">
  <img src="Images/spider.jpg" alt="Hellhound Spider" width="600"/>
</p>

<h1 align="center">Hellhound Spider</h1>

<p align="center">
  Fast async web crawler for security testing — discovers endpoints, parameters, and security issues across traditional and SPA web applications.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square"/>
  <img src="https://img.shields.io/badge/version-11.2-red?style=flat-square"/>
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=flat-square"/>
</p>

---

## What It Does

Hellhound Spider maps every reachable endpoint, parameter, and security surface of a web application. It runs as a standalone CLI tool — no framework needed. Point it at a target, give it credentials if you have them, and it hands you a structured report ready for manual review or import into Burp Suite.

It covers both traditional server-rendered applications and modern JavaScript-heavy SPAs. For SPAs it spins up a headless Chromium browser and intercepts actual network calls as the page runs, so endpoints that never appear in HTML are still captured. For everything else it uses async HTTP with up to 12 concurrent workers.

The output is a confidence-sorted list of endpoints with discovered parameters, observed HTTP methods, auth requirements, and flagged security issues — exported as JSON, CSV, JSONL, or Burp XML.

---

## Features

- Dual-engine crawl — async HTTP + headless Chromium (Playwright) for SPA support
- `robots.txt` parsing — disallowed paths crawled as targets, not skipped
- Recursive sitemap.xml parsing including sitemap index files
- GraphQL introspection probe across common paths
- OpenAPI / Swagger spec discovery and full endpoint extraction
- CORS misconfiguration detection
- Source map exposure detection
- Secret detection in JavaScript and HTML — API keys, tokens, credentials
- HTTP method discovery per endpoint
- Parameter sensitivity detection via baseline comparison
- SPA request header capture for auth-aware downstream testing
- Scan diff engine — compare two reports to find what changed

---

## Installation

```bash
git clone https://github.com/l4zz3rj0d/hellhound-spider.git
cd hellhound-spider
pip install -r requirements.txt
```

**Optional — headless browser support for SPA targets:**

```bash
pip install -r requirements-playwright.txt
playwright install chromium
```

Without Playwright the spider falls back to pure HTTP crawling and still works on most targets. Use `--no-playwright` to force this mode explicitly.

**Requirements:** Python 3.10+

---

## Usage

```
python3 hellhound_spider.py <target> [options]
```

**Scan Options**

| Flag | Default | Description |
|---|---|---|
| `--depth`, `-d` | `4` | Maximum crawl depth |
| `--concurrency` | `12` | Concurrent async workers |
| `--timeout` | `15` | Per-request timeout in seconds |
| `--verbose`, `-v` | off | Show all discovery logs |

**Authentication**

| Flag | Description |
|---|---|
| `--cookie` | Cookie string, or path to a Netscape/JSON cookie file |
| `--auth` | Authorization header value e.g. `"Bearer eyJ..."` |

**Output**

| Flag | Default | Description |
|---|---|---|
| `--out` | auto | Output file path |
| `--format` | `json` | Format: `json` `jsonl` `csv` `burp` |

A JSON report is always auto-saved to the current directory even without `--out`.

**Feature Flags**

| Flag | Description |
|---|---|
| `--no-playwright` | HTTP crawl only, no headless browser |
| `--no-probing` | Skip intelligent probing phase |
| `--no-cors` | Skip CORS checks |
| `--no-graphql` | Skip GraphQL probe |
| `--no-openapi` | Skip OpenAPI discovery |

**Utilities**

| Flag | Description |
|---|---|
| `--diff OLD_REPORT` | Diff this scan against a previous JSON report |

---

## Examples

```bash
# Basic unauthenticated scan
python3 hellhound_spider.py https://target.com

# Authenticated with a session cookie
python3 hellhound_spider.py https://target.com --cookie "session=abc123; csrf=xyz"

# Authenticated with a JWT token cookie
python3 hellhound_spider.py https://target.com --cookie "token=eyJhbGci..."

# Authenticated with a Bearer token header
python3 hellhound_spider.py https://target.com --auth "Bearer eyJhbGci..."

# Load cookies from a browser-exported cookie file
python3 hellhound_spider.py https://target.com --cookie /path/to/cookies.txt

# Deeper crawl with verbose output
python3 hellhound_spider.py https://target.com -d 6 --verbose

# Export as Burp Suite XML
python3 hellhound_spider.py https://target.com --format burp --out burp.xml

# Export as CSV
python3 hellhound_spider.py https://target.com --format csv --out endpoints.csv

# Fast scan without headless browser
python3 hellhound_spider.py https://target.com --no-playwright

# Compare two scans
python3 hellhound_spider.py https://target.com --diff previous.json
```

---

## Output

The JSON report contains these top-level keys: `meta`, `summary`, `endpoints`, `secrets`, `cors_issues`, `graphql`, `openapi`, `sourcemaps`, `comments`, `robots_disallowed`, `tech_stack`.

Each endpoint includes its URL, discovered HTTP methods, parameters grouped by source bucket (`query`, `form`, `js`, `openapi`, `runtime`), observed status codes, auth requirement flag, and a confidence label.

**Confidence levels:**

| Label | Meaning |
|---|---|
| `CONFIRMED` | Observed as a live browser XHR/fetch, or from an OpenAPI spec |
| `HIGH` | Found via form action or multiple corroborating sources |
| `MEDIUM` | Found via HTML crawl, robots.txt, or sitemap |
| `LOW` | Found via JS analysis, CSP hints, or body text hints |

---

## Legal

This tool is intended for authorized security testing only. Only use it against systems you have explicit permission to test. The author is not responsible for misuse.

---

## Author

**Sree Danush S** (L4ZZ3RJ0D)

[GitHub](https://github.com/l4zz3rj0d) · [Medium](https://medium.com/@l4zz3rj0d) · [TryHackMe](https://tryhackme.com/p/L4ZZ3RJ0D)

> Also available as the recon module inside the [Hellhound](https://github.com/l4zz3rj0d/hellhound) pentest framework.