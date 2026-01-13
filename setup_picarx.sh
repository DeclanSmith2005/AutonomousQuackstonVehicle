#!/usr/bin/env bash
#
# setup_picarx.sh
# - Clones SunFounder robot-hat + picar-x (+ vilib picamera2)
# - Installs into SYSTEM Python (intentionally, for ELEC 392)
# - Hardened for Debian 12 (Bookworm) PEP 668 pip restrictions
#
# Usage:
#   ./setup_picarx.sh
#
# Optional environment variables:
#   INSTALL_DIR    Where to put cloned repos (default: ~/dev/sunfounder)
#   ROBOT_HAT_REF  Branch/tag/commit (default: v2.0)
#   PICARX_REF     Branch/tag/commit (default: v2.0)
#   VILIB_REF      Branch/tag/commit (default: picamera2)
#   PYTHON_BIN     Python interpreter (default: python3)
#
set -euo pipefail

###############################################################################
#                                                                             #
#      ███████╗██╗     ███████╗ ██████╗        ██████╗  █████╗ ██████╗        #
#      ██╔════╝██║     ██╔════╝██╔════╝       ██╔════╝ ██╔══██╗██╔══██╗       #
#      █████╗  ██║     █████╗  ██║            ██║      ███████║██████╔╝       #
#      ██╔══╝  ██║     ██╔══╝  ██║            ██║      ██╔══██║██╔══██╗       #
#      ███████╗███████╗███████╗╚██████╗       ╚██████╗ ██║  ██║██║  ██║       #
#      ╚══════╝╚══════╝╚══════╝ ╚═════╝        ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝       #
#                                                                             #
#   ELEC 392 – Engineering Design & Development                               #
#   Picar-X Environment Setup                                   #
#                                                                             #
#   Target OS : Debian 12 (Bookworm)                                          #
#   Hardware  : Raspberry Pi 4B                                               #
#                                                                             #
###############################################################################

print_centered() {
  local cols="${COLUMNS:-80}"
  while IFS= read -r line; do
    # Strip trailing whitespace for accurate width
    local clean="${line%"${line##*[![:space:]]}"}"
    local len="${#clean}"
    if (( len < cols )); then
      printf "%*s%s\n" $(( (cols - len) / 2 )) "" "$clean"
    else
      printf "%s\n" "$clean"
    fi
  done
}

print_centered <<'EOF'

             ':looooooooooooooooooo;
          ':lxOOOOOOOOOOOOOOOOOOOkd;
       ':lxOOOOOOOOOOOOOOOOOOOkdc,
     ;lxOOOOOOOOOOOOOOOOOOOkdc,
    :kOOOOOOOOOOOOOOOOOOOdl;'
    ';;;;;;;:cdkOOOOOOOOkdooooooooo;
          ':oxOOOOOOOOOOOOOOOOOOOkd;
       ':lxOOOOOOOOOOOOOOOOOOOkdc,
    ';lxOOOOOOOOOOOOOOOOOOOkdc,
    :kOOOOOOOOOOOOOOOOOOOdl;
    ';;;;;;;cdkOOOOOOOOkxooooooooo;
          ':oxOOOOOOOOOOO0OOOOOOOko;
       ':oxOOOOOOOOOOOOOOOOOOOkdc,
    ':oxOOOOOOOOOOOOOOOOO0Okdc,
    :kOOOOOOOOOOOOOOOOOOkdc,
    ';;;;;;;;;;;;;;;;;;;,

ELEC 392 – Engineering Design & Development
Queen’s University | Smith Engineering

PiCar-X Environment Setup

EOF

# -------------------------
# Config (override via env)
# -------------------------
INSTALL_DIR="${INSTALL_DIR:-$HOME/dev/sunfounder}"
ROBOT_HAT_REF="${ROBOT_HAT_REF:-v2.0}"
PICARX_REF="${PICARX_REF:-v2.0}"
VILIB_REF="${VILIB_REF:-picamera2}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

ROBOT_HAT_REPO="https://github.com/sunfounder/robot-hat.git"
PICARX_REPO="https://github.com/sunfounder/picar-x.git"
VILIB_REPO="https://github.com/sunfounder/vilib.git"


# -------------------------
# Helpers
# -------------------------
log()  { echo -e "\n\033[1;34m[INFO]\033[0m $*"; }
warn() { echo -e "\n\033[1;33m[WARN]\033[0m $*"; }
err()  { echo -e "\n\033[1;31m[ERR ]\033[0m $*"; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { err "Missing required command: $1"; exit 1; }
}

is_pi() {
  grep -qi "raspberry pi" /proc/cpuinfo 2>/dev/null
}

# Clone or update a repo to a specific ref
sync_repo() {
  local url="$1"
  local dir="$2"
  local ref="$3"

  if [[ -d "$dir/.git" ]]; then
    log "Updating existing repo: $dir"
    git -C "$dir" fetch --all --tags --prune
  else
    log "Cloning repo: $url -> $dir"
    git clone "$url" "$dir"
  fi

  log "Checking out ref '$ref' in $dir"
  git -C "$dir" checkout "$ref" >/dev/null 2>&1 || {
    err "Failed to checkout '$ref' in $dir. Available refs:"
    git -C "$dir" branch -a || true
    git -C "$dir" tag -l || true
    exit 1
  }

  # If it's a branch, pull latest. If it's a tag/commit, no pull.
  if git -C "$dir" show-ref --verify --quiet "refs/heads/$ref"; then
    git -C "$dir" pull --ff-only
  fi

  log "Pinned $dir at: $(git -C "$dir" rev-parse --short HEAD)"
}

# Shallow clone/update for vilib (SunFounder requested pattern)
sync_vilib_shallow() {
  local url="$1"
  local dir="$2"
  local ref="$3"

  if [[ -d "$dir/.git" ]]; then
    log "Updating existing repo (vilib): $dir"
    git -C "$dir" fetch origin "$ref" --depth 1 || git -C "$dir" fetch origin "$ref" || true
    git -C "$dir" checkout "$ref" || true
  else
    log "Cloning vilib (branch=$ref, depth=1): $url -> $dir"
    git clone -b "$ref" --depth 1 "$url" "$dir"
  fi

  log "Pinned vilib at: $(git -C "$dir" rev-parse --short HEAD)"
}

# -------------------------
# Bookworm / PEP 668 pip hardening
# -------------------------
pip_install_editable() {
  local path="$1"
  log "pip install (editable): $path"

  # Capture output so we can detect PEP 668 and retry.
  local out
  out="$(sudo python3 -m pip install -e "$path" 2>&1 || true)"

  # Success?
  if echo "$out" | grep -qiE "Successfully installed|Installing collected packages|Obtaining file"; then
    echo "$out"
    return 0
  fi

  # PEP 668 externally-managed environment detection
  if echo "$out" | grep -qiE "externally[- ]managed|This environment is externally managed"; then
    warn "PEP 668 protection detected (Bookworm). Retrying with --break-system-packages..."
    sudo python3 -m pip install --break-system-packages -e "$path"
    return $?
  fi

  # Real failure
  err "pip install failed for: $path"
  echo "$out"
  return 1
}

# -------------------------
# Start
# -------------------------
if [[ $EUID -eq 0 ]]; then
  err "Do not run this script as root. Run it normally; it will sudo when needed."
  exit 1
fi

warn "This script installs Python packages into the SYSTEM Python environment."
warn "This is intentional for ELEC 392 (fewer venvs, fewer tears)."
warn "DO NOT run this on your personal laptop unless you enjoy consequences."
sleep 2

log "PiCar-X setup (SunFounder robot-hat + picar-x + vilib)"
log "Install dir: $INSTALL_DIR"
log "Refs:        robot-hat=$ROBOT_HAT_REF, picar-x=$PICARX_REF, vilib=$VILIB_REF"

need_cmd git
need_cmd "$PYTHON_BIN"

if ! is_pi; then
  warn "This does not look like a Raspberry Pi. Continuing anyway."
fi

# -------------------------
# System deps
# -------------------------
log "Installing system packages (requires sudo)"
sudo apt-get update

# python3-venv intentionally omitted (no venv usage here)
sudo apt-get install -y --no-install-recommends \
  python3-pip \
  python3-dev \
  python3-setuptools \
  python3-smbus \
  python3-smbus2 \
  python3-yaml \
  git \
  i2c-tools \
  libatlas-base-dev \
  build-essential \
  python3-libcamera \
  python3-picamera2 \
  rpicam-apps \
  python3-opencv \
  opencv-data \
  ffmpeg

# Optional: ensure pip tooling is modern enough (system-level)
log "Upgrading pip tooling (system Python)"
# This may also trip PEP 668; handle both cases.
if ! sudo python3 -m pip install --upgrade pip setuptools wheel 2>/dev/null; then
  warn "pip upgrade blocked by PEP 668; retrying with --break-system-packages..."
  sudo python3 -m pip install --break-system-packages --upgrade pip setuptools wheel
fi

# Optional: enable I2C tools visibility check
if [[ -e /dev/i2c-1 ]]; then
  log "I2C device present: /dev/i2c-1"
else
  warn "/dev/i2c-1 not found. I2C may be disabled."
  warn "Enable it with: sudo raspi-config  -> Interface Options -> I2C -> Enable -> Reboot"
fi

# -------------------------
# Clone repos (pinned)
# -------------------------
mkdir -p "$INSTALL_DIR"
ROBOT_HAT_DIR="$INSTALL_DIR/robot-hat"
PICARX_DIR="$INSTALL_DIR/picar-x"
VILIB_DIR="$INSTALL_DIR/vilib"

sync_repo "$ROBOT_HAT_REPO" "$ROBOT_HAT_DIR" "$ROBOT_HAT_REF"
sync_repo "$PICARX_REPO"     "$PICARX_DIR"     "$PICARX_REF"
sync_vilib_shallow "$VILIB_REPO" "$VILIB_DIR" "$VILIB_REF"

# -------------------------
# Install (editable) into SYSTEM Python
# -------------------------
pip_install_editable "$ROBOT_HAT_DIR"
pip_install_editable "$VILIB_DIR"
pip_install_editable "$PICARX_DIR"

# -------------------------
# Sanity checks
# -------------------------
log "Sanity check: Python imports"
python3 - <<'PY'
import sys
print("Python:", sys.version)

# robot-hat import check (module name varies)
ok_hat = False
last = None
for name in ("robot_hat", "robot_hat.core", "robot_hat.utils"):
    try:
        __import__(name)
        print(f"OK: import {name}")
        ok_hat = True
        break
    except Exception as e:
        last = e
if not ok_hat:
    print("WARN: Could not import robot_hat modules cleanly. (May still work on target)")
    if last:
        print("      Last error:", repr(last))

# vilib import check
try:
    import vilib
    print("OK: import vilib")
except Exception as e:
    print("WARN: import vilib failed (camera stack may not be ready yet)")
    print("      Error:", repr(e))

# picar-x import check
try:
    from picarx import Picarx
    print("OK: from picarx import Picarx")
except Exception as e:
    print("FAIL: from picarx import Picarx")
    raise
PY

log "Sanity check: I2C probe (won't fail the install)"
if command -v i2cdetect >/dev/null 2>&1; then
  sudo i2cdetect -y 1 || true
fi

# -------------------------
# Wrap up
# -------------------------
cat <<EOF

============================================================
DONE.

Python packages were installed into the SYSTEM Python environment.

Quick verify:
  python3 -c "from picarx import Picarx; import vilib; print('OK')"

Repos were installed from:
  $ROBOT_HAT_DIR  (ref: $ROBOT_HAT_REF)
  $VILIB_DIR      (ref: $VILIB_REF)
  $PICARX_DIR     (ref: $PICARX_REF)

If I2C was missing:
  sudo raspi-config -> Interface Options -> I2C -> Enable -> Reboot

Reminder:
- This Pi is now a course appliance.
- Re-imaging the SD card is the big red reset button.
============================================================

EOF