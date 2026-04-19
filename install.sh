#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
#  Hellhound Spider — Installer (v12.0)
#  Installs the `spider` command with an isolated virtual environment.
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

# Parse flags
NON_INTERACTIVE=false
for arg in "$@"; do
    if [[ "$arg" == "--yes" || "$arg" == "-y" || "$arg" == "--non-interactive" ]]; then
        NON_INTERACTIVE=true
    fi
done

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
echo -e "  ${CYN}Hellhound Spider v12.0${RST}  —  Installer\n"

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

# ── Virtual Environment Setup ────────────────────────────────────────────────
info "Setting up virtual environment..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR" || error "Failed to create virtual environment. Ensure 'python3-venv' is installed."
fi
VENV_PYTHON="$VENV_DIR/bin/python3"
success "Virtual environment ready: $VENV_DIR"

# ── Install pip dependencies ───────────────────────────────────────────────────
info "Installing dependencies from requirements.txt into venv..."
"$VENV_PYTHON" -m pip install --quiet --upgrade pip
"$VENV_PYTHON" -m pip install --quiet -r requirements.txt
success "Core dependencies installed"

# ── Optional: Playwright ───────────────────────────────────────────────────────
INSTALL_PLAYWRIGHT="n"
if [ "$NON_INTERACTIVE" = true ]; then
    # In non-interactive mode, only install Playwright if already present
    if "$VENV_PYTHON" -c "import playwright" &>/dev/null; then
        INSTALL_PLAYWRIGHT="y"
        info "Playwright detected in venv — updating..."
    else
        warn "Non-interactive mode: skipping Playwright installation"
    fi
else
    echo ""
    echo -e "  ${CYN}Playwright${RST} enables headless browser scanning for SPA targets"
    echo -e "  (React, Angular, Vue, Next.js). Requires ~150MB for Chromium.\n"
    read -r -p "  Install Playwright for SPA support? [y/N] " INSTALL_PLAYWRIGHT
    echo ""
fi

if [[ "$INSTALL_PLAYWRIGHT" =~ ^[Yy]$ ]]; then
    info "Installing Playwright package..."
    "$VENV_PYTHON" -m pip install --quiet --upgrade playwright
    
    info "Installing Chromium browser binaries..."
    "$VENV_PYTHON" -m playwright install chromium
    
    info "Installing system dependencies (may require sudo)..."
    if command -v sudo &>/dev/null && [ "$EUID" -ne 0 ]; then
        sudo "$VENV_PYTHON" -m playwright install-deps chromium || warn "System dependency installation failed. You might need to install them manually."
    else
        "$VENV_PYTHON" -m playwright install-deps chromium || warn "System dependency installation failed. You might need to install them manually."
    fi
    
    success "Playwright + Chromium + Dependencies installed"
fi

# ── Install the spider command ─────────────────────────────────────────────────
info "Installing spider command binary..."

SPIDER_SRC="$SCRIPT_DIR/spider.py"
if [ ! -f "$SPIDER_SRC" ]; then
    error "spider.py not found in $SCRIPT_DIR"
fi

# Create a temporary wrapper script
WRAPPER_TMP=$(mktemp)
cat << EOW > "$WRAPPER_TMP"
#!/usr/bin/env bash
# Hellhound Spider — Wrapper Script
# Generated on $(date)
"$VENV_PYTHON" "$SPIDER_SRC" "\$@"
EOW

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
    sudo cp "$WRAPPER_TMP" "$INSTALL_PATH"
    sudo chmod +x "$INSTALL_PATH"
else
    cp "$WRAPPER_TMP" "$INSTALL_PATH"
    chmod +x "$INSTALL_PATH"
fi
rm -f "$WRAPPER_TMP"

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
