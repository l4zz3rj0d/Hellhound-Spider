#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
#  Hellhound Spider — Uninstaller
# ─────────────────────────────────────────────────────────────────────

set -e

RED='\033[91m'
GRN='\033[92m'
CYN='\033[96m'
RST='\033[0m'
BLD='\033[1m'

info()    { echo -e "${CYN}[*]${RST} $1"; }
success() { echo -e "${GRN}${BLD}[✓]${RST} $1"; }
error()   { echo -e "${RED}[✗]${RST} $1"; exit 1; }

LOCATIONS=(
    "/usr/local/bin/spider"
    "/usr/bin/spider"
    "$HOME/.local/bin/spider"
)

FOUND=false
for LOC in "${LOCATIONS[@]}"; do
    if [ -f "$LOC" ]; then
        info "Removing $LOC..."
        if [ -w "$(dirname "$LOC")" ]; then
            rm -f "$LOC"
        else
            sudo rm -f "$LOC"
        fi
        success "Removed $LOC"
        FOUND=true
    fi
done

if [ "$FOUND" = false ]; then
    error "spider command not found in any standard location"
fi

echo ""
echo -e "  ${GRN}${BLD}Uninstall complete.${RST}"
echo ""