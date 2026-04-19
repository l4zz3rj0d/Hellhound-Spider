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

# Check for local changes and stash them to avoid pull conflicts
LOCAL_CHANGES=$(git status --porcelain)
if [ -n "$LOCAL_CHANGES" ]; then
    warn "Local changes detected — stashing to ensure a clean update..."
    git stash
fi

# Determine current branch and pull
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
if git pull origin "$CURRENT_BRANCH"; then
    success "Source code updated [branch: $CURRENT_BRANCH]"
else
    warn "Standard pull failed — attempting emergency fetch/reset..."
    git fetch --all
    git pull || warn "Could not pull latest changes. You may have uncommitted conflicts."
fi

# Restore local changes if they were stashed
if [ -n "$LOCAL_CHANGES" ]; then
    info "Restoring your local changes..."
    git stash pop &>/dev/null || warn "Could not auto-apply local changes. Use 'git stash pop' manually."
fi

# ── Run installer in non-interactive mode ─────────────────────────────────────
info "Refreshing installation..."
chmod +x install.sh
./install.sh --yes
success "Installation refreshed successfully"

echo ""
echo -e "  ${GRN}${BLD}Update complete.${RST} You are now on the latest version.\n"
echo ""
