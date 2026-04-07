<p align="center">
  <img src="Images/spider.jpg" alt="Hellhound Spider" width="600"/>
</p>

<h1 align="center">Hellhound Spider</h1>

<p align="center">
  Fast async web crawler for security testing — maps endpoints, parameters, and security issues across traditional and SPA web applications.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/version-12.0-red?style=flat-square"/>
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=flat-square"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square"/>
</p>

---

## Installation

### Linux / macOS

```bash
git clone https://github.com/l4zz3rj0d/hellhound-spider.git
cd hellhound-spider
chmod +x install.sh
./install.sh
```

The installer automatically creates an **isolated virtual environment (`.venv`)** in the project directory. All dependencies (including Playwright) are installed within this environment to prevent conflicts with your system Python. 

A binary wrapper is generated at `/usr/local/bin/spider` (or `~/.local/bin/spider`) which automatically launches the tool using the internal environment. You can run it from anywhere like any other system tool:

```bash
spider https://target.com
```

### Windows

The bash installer doesn't run on Windows. Use pip instead:

```bash
git clone https://github.com/l4zz3rj0d/hellhound-spider.git
cd hellhound-spider
pip install -e .                    # core install
pip install -e ".[spa]"             # with Playwright SPA support
playwright install chromium         # download browser
```

This registers the `spider` command via pip's entry points so it works from any terminal:

```bash
spider https://target.com
```

> **Note:** Colours render correctly in Windows Terminal and PowerShell 7+. On old `cmd.exe` the output falls back to plain text automatically.

### Manual install (pip) — any platform

```bash
pip install -e .                    # core install
pip install -e ".[spa]"             # with Playwright SPA support
playwright install chromium         # download browser
```

### Uninstall

**Linux / macOS:**
```bash
./uninstall.sh
```

**Windows:**
```bash
pip uninstall hellhound-spider
```

---

## v12.0 — High-Fidelity Recon

The v12.0 release transitions Hellhound Spider into a professional-grade reconnaissance engine with three new core systems:

1.  **Method Oracle**: Automatically discovers mandatory parameter names for REST APIs by switching methods (GET→POST) and parsing validation error bodies (400/405/422).
2.  **Backup Prober**: Scans for exposed configuration and backup files (`.bak`, `.old`, `.env`, `.sql`) and automatically harvests secrets from them.
3.  **Intelligence Classification**: Every discovered endpoint is automatically classified with metadata tags to feed downstream security agents.

---

## What It Does

Hellhound Spider crawls a web application and produces a complete map of every endpoint, parameter, and security surface it can reach. The output is a structured JSON report — sorted by confidence, with parameters grouped by source, ready to feed directly into attack agents or import into Burp Suite.

It uses two crawl engines in parallel: async HTTP workers for speed, and headless Chromium for JavaScript-heavy SPAs. For SPAs it intercepts live XHR and fetch calls as the browser actually makes them — including POST body parameters and response IDs.

---

## Usage

```
spider <target> [options]
```

**Scan**

| Flag | Default | Description |
|---|---|---|
| `--depth`, `-d` | `4` | Maximum crawl depth |
| `--concurrency` | `12` | Concurrent async workers |
| `--timeout` | `15` | Per-request timeout in seconds |
| `--verbose`, `-v` | off | Show all discovery logs (including Method Oracle & Backup finds) |

**Authentication**

Accepts Netscape cookie files, JSON browser exports, and inline strings.

| Flag | Description |
|---|---|
| `--cookie` | Cookie string `"name=value"` or path to a cookie file |
| `--auth` | Authorization header value e.g. `"Bearer eyJ..."` |

**Output**

| Flag | Default | Description |
|---|---|---|
| `--out` | auto-named | Output file path |
| `--format` | `json` | `json` `jsonl` `csv` `burp` |

A JSON report is always auto-saved to the current directory even without `--out`.

**Feature Flags**

| Flag | Description |
|---|---|
| `--no-playwright` | HTTP crawl only, no headless browser |
| `--no-probing` | Skip Method Oracle and CORS probes |
| `--no-cors` | Skip CORS checks |
| `--no-graphql` | Skip GraphQL introspection probe |
| `--no-openapi` | Skip OpenAPI / Swagger discovery |

**Utilities**

| Flag | Description |
|---|---|
| `--diff OLD_REPORT` | Diff this scan against a previous JSON report |

---

## Examples

```bash
# Basic scan
spider https://target.com

# Authenticated with a session cookie
spider https://target.com --cookie "session=abc123; csrf=xyz"

# Authenticated with a JWT
spider https://target.com --cookie "token=eyJhbGci..."

# Authenticated with Bearer token
spider https://target.com --auth "Bearer eyJhbGci..."

# Load cookies from a browser-exported file
spider https://target.com --cookie /path/to/cookies.txt

# Deeper crawl, all logs visible
spider https://target.com -d 6 --verbose

# Export for Burp Suite
spider https://target.com --format burp --out burp.xml

# Export as CSV
spider https://target.com --format csv --out endpoints.csv

# No headless browser
spider https://target.com --no-playwright

# Diff two scans
spider https://target.com --diff previous.json
```

---

## What Gets Found

**Discovery Vectors** — HTML crawl, live SPA XHR interception, robots.txt, sitemap XML, `.well-known` (including OIDC/JWKS), JSON path chaining, SPA hash routes, lazy-load attributes.

**Parameter Mining** — Form fields, JS fetch/axios body keys, URL query strings, OpenAPI spec fields, POST body params from live browser requests, **Method Oracle** (error-body parsing).

**Security Issues** — GraphQL introspection, OpenAPI/Swagger exposure, CORS misconfiguration, Source map exposure, **Exposed Backups/Configs**, **Secrets Harvesting** (API keys, credentials, JWTs).

---

## Intelligence Classification (v12.0)

Endpoints are automatically tagged in the JSON report with intelligence metadata:

| Tag | Meaning |
|---|---|
| `admin_panel` | Management/Administration interface detected |
| `auth_classification` | login, logout, register, token, mfa, password_reset |
| `idor_candidate` | Endpoints with ID-like parameters or UUIDs in the path |
| `sqli_candidate` | Parameters prone to SQL injection (id, query, filter, sort) |
| `cmdi_candidate` | Parameters prone to Command injection (cmd, exec, file, path) |
| `file_upload` | Endpoints for file/media ingestion |

---

## Output Formats

- **JSON**: Full-fidelity report with classification metadata.
- **Burp**: XML format for direct import into Burp Suite.
- **CSV**: Spreadsheet-ready list of endpoints and parameters.

---

## Requirements

- Python 3.10+
- `aiohttp`, `beautifulsoup4`, `lxml`
- Playwright + Chromium *(optional, for SPA targets)*

---

## Legal

For authorized security testing only. The author is not responsible for misuse.

---

## Author

**Sree Danush S** (L4ZZ3RJ0D)

[GitHub](https://github.com/l4zz3rj0d) · [Medium](https://medium.com/@l4zz3rj0d) · [TryHackMe](https://tryhackme.com/p/L4ZZ3RJ0D)

> Integrated into the [Hellhound Pentest Framework](https://github.com/l4zz3rj0d/Hellhound-Pentest).