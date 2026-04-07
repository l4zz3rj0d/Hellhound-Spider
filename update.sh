#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
#  Hellhound Spider — Updater
#  Pulls the latest changes from Git and refreshes the installation.
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
echo -e "  ${CYN}Hellhound Spider v12.0${RST}  —  Updater\n"

# ── Check if Git repository ───────────────────────────────────────────────────
if [ ! -d ".git" ]; then
    error "Not a git repository. Download the source via 'git clone' to use the updater."
fi

# ── Pull latest changes ───────────────────────────────────────────────────────
info "Fetching latest changes from repository..."
git pull origin main || warn "Could not pull from 'main' branch. Trying default..." && git pull
success "Source code updated"

# ── Run installer in non-interactive mode ─────────────────────────────────────
info "Refreshing installation..."
chmod +x install.sh
./install.sh --yes
success "Installation refreshed successfully"

echo ""
echo -e "  ${GRN}${BLD}Update complete.${RST} You are now on the latest version.\n"
echo ""
