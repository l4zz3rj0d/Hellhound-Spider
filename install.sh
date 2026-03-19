#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
#  Hellhound Spider — Installer
#  Installs the `spider` command system-wide so you can run it from
#  anywhere without typing python3 or a file path.
# ─────────────────────────────────────────────────────────────────────

set -e

RED='\033[91m'
GRN='\033[92m'
CYN='\033[96m'
YLW='\033[93m'
RST='\033[0m'
BLD='\033[1m'

info()    { echo -e "${CYN}[*]${RST} $1"; }
success() { echo -e "${GRN}${BLD}[✓]${RST} $1"; }
warn()    { echo -e "${YLW}[!]${RST} $1"; }
error()   { echo -e "${RED}[✗]${RST} $1"; exit 1; }

echo -e "${RED}${BLD}"
cat << 'BANNER'
              ██╗  ██╗███████╗██╗     ██╗     ██╗  ██╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗
              ██║  ██║██╔════╝██║     ██║     ██║  ██║██╔═══██╗██║   ██║████╗  ██║██╔══██╗
              ███████║█████╗  ██║     ██║     ███████║██║   ██║██║   ██║██╔██╗ ██║██║  ██║
              ██╔══██║██╔══╝  ██║     ██║     ██╔══██║██║   ██║██║   ██║██║╚██╗██║██║  ██║
              ██║  ██║███████╗███████╗███████╗██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝
              ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝
BANNER
echo -e "${RST}"
echo -e "  ${CYN}Hellhound Spider v11.2${RST}  —  Installer\n"

# ── Check Python version ───────────────────────────────────────────────────────
info "Checking Python version..."
if ! command -v python3 &>/dev/null; then
    error "Python 3 not found. Install Python 3.10+ and try again."
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    error "Python 3.10+ required. Found: $PY_VERSION"
fi
success "Python $PY_VERSION found"

# ── Install pip dependencies ───────────────────────────────────────────────────
info "Installing dependencies..."
pip3 install --quiet aiohttp beautifulsoup4 lxml
success "Core dependencies installed"

# ── Optional: Playwright ───────────────────────────────────────────────────────
echo ""
echo -e "  ${CYN}Playwright${RST} enables headless browser scanning for SPA targets"
echo -e "  (React, Angular, Vue, Next.js). Requires ~150MB for Chromium.\n"
read -r -p "  Install Playwright for SPA support? [y/N] " INSTALL_PLAYWRIGHT
echo ""

if [[ "$INSTALL_PLAYWRIGHT" =~ ^[Yy]$ ]]; then
    info "Installing Playwright..."
    pip3 install --quiet playwright
    playwright install chromium
    success "Playwright + Chromium installed"
else
    warn "Skipping Playwright — SPA scanning will be disabled (use --no-playwright)"
fi

# ── Install the spider command ─────────────────────────────────────────────────
info "Installing spider command..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPIDER_SRC="$SCRIPT_DIR/spider.py"

if [ ! -f "$SPIDER_SRC" ]; then
    error "spider.py not found in $SCRIPT_DIR"
fi

# Determine install location — prefer /usr/local/bin, fall back to ~/.local/bin
if [ -w "/usr/local/bin" ]; then
    INSTALL_DIR="/usr/local/bin"
elif sudo -n true 2>/dev/null; then
    INSTALL_DIR="/usr/local/bin"
    USE_SUDO=true
else
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
fi

INSTALL_PATH="$INSTALL_DIR/spider"

# Copy and make executable
if [ "${USE_SUDO:-false}" = true ]; then
    sudo cp "$SPIDER_SRC" "$INSTALL_PATH"
    sudo chmod +x "$INSTALL_PATH"
else
    cp "$SPIDER_SRC" "$INSTALL_PATH"
    chmod +x "$INSTALL_PATH"
fi

success "Installed to $INSTALL_PATH"

# ── PATH check for ~/.local/bin ────────────────────────────────────────────────
if [ "$INSTALL_DIR" = "$HOME/.local/bin" ]; then
    if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
        warn "$HOME/.local/bin is not in your PATH"
        echo ""
        echo "  Add this line to your ~/.bashrc or ~/.zshrc:"
        echo ""
        echo -e "    ${GRN}export PATH=\"\$HOME/.local/bin:\$PATH\"${RST}"
        echo ""
        echo "  Then run:  source ~/.bashrc"
        echo ""
    fi
fi

# ── Done ───────────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${GRN}${BLD}Installation complete.${RST}\n"
echo -e "  Usage:"
echo -e "    ${CYN}spider${RST} https://target.com"
echo -e "    ${CYN}spider${RST} https://target.com --cookie \"session=abc\""
echo -e "    ${CYN}spider${RST} https://target.com --auth \"Bearer eyJ...\""
echo -e "    ${CYN}spider${RST} --help"
echo ""