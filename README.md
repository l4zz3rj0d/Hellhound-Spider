<p align="center">
  <img src="Images/spider.jpg" alt="Hellhound Spider" width="600"/>
</p>

<h1 align="center">Hellhound Spider</h1>

<p align="center">
  Fast async web crawler for security testing — maps endpoints, parameters, and security issues across traditional and SPA web applications.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/version-11.2-red?style=flat-square"/>
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

The installer handles dependencies, optionally installs Playwright for SPA support, and puts the `spider` command in your PATH. After that you call it like any system tool:

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

## What It Does

Hellhound Spider crawls a web application and produces a complete map of every endpoint, parameter, and security surface it can reach. The output is a structured JSON report — sorted by confidence, with parameters grouped by source, ready to feed directly into attack agents or import into Burp Suite.

It uses two crawl engines in parallel: async HTTP workers for speed and coverage, and headless Chromium for JavaScript-heavy SPAs that load content dynamically. For SPAs it intercepts live XHR and fetch calls as the browser actually makes them — so endpoints that never appear in HTML are still captured, including their POST body parameters and response IDs.

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
| `--verbose`, `-v` | off | Show all discovery logs |

**Authentication**

| Flag | Description |
|---|---|
| `--cookie` | Cookie string `"name=value; name2=value2"` or path to a cookie file |
| `--auth` | Authorization header value e.g. `"Bearer eyJ..."` |

Accepts Netscape cookie files, JSON browser exports, and inline strings. JWT tokens work regardless of length.

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
| `--no-probing` | Skip intelligent probing phase |
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

**Endpoints** — HTML crawl, live SPA XHR interception, robots.txt disallowed paths, sitemap XML, `.well-known` files, JSON response path chaining, SPA hash routes, lazy-load attributes, JSON-LD.

**Parameters** — Form fields (all types including hidden), JS fetch/axios body keys, URL query strings, OpenAPI spec fields, POST body params from live browser requests, JSON response key extraction, validation error message scanning.

**Security issues** — GraphQL introspection, OpenAPI/Swagger spec exposure, CORS misconfiguration, source map exposure, secrets in JS/HTML (API keys, tokens, credentials, crypto addresses), auth-walled endpoints, param-sensitive endpoints.

---

## Output

Results are printed to the terminal as a colour-coded report and saved as JSON. Each endpoint in the report includes its URL, discovered HTTP methods, parameters by source bucket, observed HTTP status codes, auth requirement flag, confidence label, and any custom request headers captured during SPA scanning.

**Confidence levels:**

| Label | Meaning |
|---|---|
| `CONFIRMED` | Observed as a live browser XHR/fetch, or from an OpenAPI spec |
| `HIGH` | Found via form action or multiple corroborating sources |
| `MEDIUM` | Found via HTML crawl, robots.txt, or sitemap |
| `LOW` | Found via JS analysis, CSP hints, or body text hints |

Output formats: `json`, `jsonl`, `csv`, `burp` (Burp Suite XML).

---

## Requirements

- Python 3.10+
- `aiohttp`, `beautifulsoup4`, `lxml`
- Playwright + Chromium *(optional, for SPA targets)*

---

## Legal

For authorized security testing only. Only use against systems you have explicit permission to test. The author is not responsible for misuse.

---

## Author

**Sree Danush S** (L4ZZ3RJ0D)

[GitHub](https://github.com/l4zz3rj0d) · [Medium](https://medium.com/@l4zz3rj0d) · [TryHackMe](https://tryhackme.com/p/L4ZZ3RJ0D)

> Also available as the recon module inside the [Hellhound](https://github.com/l4zz3rj0d/Hellhound-Pentest) pentest framework.