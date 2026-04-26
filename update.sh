#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
#  SPIDER — Updater v2.0 (Cinematic)
#  Pulls the latest changes from Git and refreshes the installation.
# ─────────────────────────────────────────────────────────────────────

set -e

RED="\033[91m"
GRN="\033[92m"
CYN="\033[96m"
YLW="\033[93m"
RST="\033[0m"
BLD="\033[1m"

info()    { echo -e "${CYN}[*]${RST} $1"; }
success() { echo -e "${GRN}${BLD}[✓]${RST} $1"; }
warn()    { echo -e "${YLW}[!]${RST} $1"; }
error()   { echo -e "${RED}[✗]${RST} $1"; stop_animation; exit 1; }

# ── Animator Logic (Cinematic) ────────────────────────────────────────────────
ANIM_PID=0

start_animation() {
    local label="$1"
    stop_animation
    
    # Python-based Cinematic Animator (v2.0 - Flush-Hardened)
    python3 -c "
import math, time, sys
label = \"$label\"
def wave(label, t):
    res = ''
    for i, c in enumerate(label):
        if not c.isalpha(): res += c; continue
        v = math.sin(t * 10 + i * 0.4)
        if v > 0: res += f'\033[91m\033[1m{c.upper()}\033[0m'
        else: res += f'\033[31m{c.lower()}\033[0m'
    return res
def braille(t):
    chars = '⡀⡄⡆⡇⣇⣧⣷⣿'
    bar = ''
    for i in range(40):
        idx = int((math.sin(t * 5 + i * 0.2) + 1) / 2 * (len(chars) - 1))
        bar += f'\033[91m{chars[idx]}\033[0m'
    return bar
start = time.time()
try:
    while True:
        t = time.time() - start
        sys.stdout.write(f'\r  {wave(label, t):<30} {braille(t)} ')
        sys.stdout.flush()
        time.sleep(0.05)
except:
    pass
" &
    ANIM_PID=$!
    disown $ANIM_PID 2>/dev/null || true
}

stop_animation() {
    if [ "$ANIM_PID" -ne 0 ]; then
        kill -9 "$ANIM_PID" &>/dev/null || true
        wait "$ANIM_PID" 2>/dev/null || true
        printf "\r\b\b\033[K"
        ANIM_PID=0
    fi
}

trap "stop_animation" EXIT INT TERM

# ── Check if Git repository ───────────────────────────────────────────────────
start_animation "VERIFYING SOURCE"
if [ ! -d ".git" ]; then
    stop_animation
    error "Not a git repository. Download the source via \"git clone\" to use the updater."
fi

# ── Remote Sync (Ensure Org URL) ──────────────────────────────────────────────
# Automatically update remote to point to the official organization
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$REMOTE_URL" == *"l4zz3rj0d"* ]]; then
    NEW_URL=$(echo "$REMOTE_URL" | sed "s/l4zz3rj0d/project-hellhound-org/g")
    git remote set-url origin "$NEW_URL" &>/dev/null || true
fi

# ── Pull latest changes ───────────────────────────────────────────────────────
stop_animation
start_animation "FETCHING UPDATES"

LOCAL_CHANGES=$(git status --porcelain)
if [ -n "$LOCAL_CHANGES" ]; then
    stop_animation
    warn "Local changes detected — stashing to ensure a clean update..."
    git stash
    start_animation "FETCHING UPDATES"
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
stop_animation
info "Fetching updates from branch: $CURRENT_BRANCH..."
if git pull origin "$CURRENT_BRANCH"; then
    success "Source code updated"
else
    warn "Standard pull failed — attempting emergency fetch/reset..."
    git fetch --all
    git pull || warn "Could not pull latest changes. You may have uncommitted conflicts."
fi

if [ -n "$LOCAL_CHANGES" ]; then
    info "Restoring your local changes..."
    git stash pop &>/dev/null || warn "Could not auto-apply local changes. Use \"git stash pop\" manually."
fi

# ── Run installer ─────────────────────────────────────────────────────────────
# IMPORTANT: Stop animation before calling installer to prevent duplicate text
stop_animation 
info "Synchronizing system configuration..."
chmod +x install.sh
if [ -f "install.sh" ]; then
    ./install.sh --yes || ./install.sh
fi

echo ""
echo -e "  ${GRN}${BLD}Update complete.${RST} SPIDER is now on the latest version.\n"
echo ""
