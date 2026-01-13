#!/usr/bin/env bash
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
#   Coral USB Accelerator Environment Setup                                   #
#                                                                             #
#   Target OS : Debian 12 (Bookworm)                                          #
#   Hardware  : Raspberry Pi (expected)                                       #
#   TPU       : Coral USB Accelerator                                         #
#                                                                             #
###############################################################################

print_centered() {
  local cols="${COLUMNS:-80}"
  while IFS= read -r line; do
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

Coral USB Accelerator Environment Setup

EOF

# ---------------------- Configuration -----------------------
PYTHON_VERSION="${PYTHON_VERSION:-3.9.20}"          # Coral venv Python (via pyenv)
PROJECT_DIR="${PROJECT_DIR:-$HOME/dev/coral}"       # Where we install everything
DO_UPGRADE="${DO_UPGRADE:-1}"                       # 1 = full-upgrade, 0 = upgrade
PYENV_DIR="${PYENV_DIR:-$HOME/.pyenv}"              # pyenv install location

# Git repos
PYCORAL_REPO="${PYCORAL_REPO:-https://github.com/google-coral/pycoral.git}"
STARTER_REPO="${STARTER_REPO:-https://github.com/mpan1/elec392-coral-starter-kit.git}"
STARTER_DIRNAME="elec392-coral-starter-kit"

# Coral APT repo config
CORAL_KEYRING="/etc/apt/keyrings/coral.gpg"
CORAL_LIST="/etc/apt/sources.list.d/coral-edgetpu.list"

# ---------------------- Helpers ------------------------------
log()  { printf "\n\033[1;32m==>\033[0m %s\n" "$*"; }
warn() { printf "\n\033[1;33m[warn]\033[0m %s\n" "$*"; }
die()  { printf "\n\033[1;31m[error]\033[0m %s\n" "$*"; exit 1; }

append_if_missing() {
  local line="$1"
  local file="$2"
  grep -qxF "$line" "$file" 2>/dev/null || echo "$line" >> "$file"
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

# If pip hits Bookworm PEP 668 because we're accidentally using SYSTEM Python,
# retry with --break-system-packages. (We still aim to install Python packages
# into the *venv*, so this is mostly belt+suspenders.)
pip_install() {
  local args=("$@")
  local out
  out="$(python3 -m pip "${args[@]}" 2>&1 || true)"
  if echo "$out" | grep -qiE "externally[- ]managed|This environment is externally managed"; then
    warn "PEP 668 protection detected for system python pip; retrying with --break-system-packages..."
    sudo python3 -m pip --break-system-packages "${args[@]}"
    return $?
  fi
  # If first command succeeded, it would not be here; so print output and fail
  echo "$out"
  return 1
}

# ---------------------- Sanity checks ------------------------
if [[ "$EUID" -eq 0 ]]; then
  die "Run this script as a regular user, not with sudo."
fi

need_cmd sudo
need_cmd curl
need_cmd git
need_cmd gpg
need_cmd python3

# ---------------------- System update ------------------------
log "Updating system packages"
sudo apt-get update -y
if [[ "$DO_UPGRADE" -eq 1 ]]; then
  sudo apt-get full-upgrade -y
else
  sudo apt-get upgrade -y
fi

# ---------------------- Build deps (pyenv) --------------------
log "Installing Python build dependencies (for pyenv)"
sudo apt-get install -y --no-install-recommends \
  build-essential \
  libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev \
  libncursesw5-dev xz-utils tk-dev \
  libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev \
  ca-certificates \
  curl \
  git

# Optional but helpful per Bookworm guidance when dealing with pip/venv tooling
sudo apt-get install -y --no-install-recommends python3-full || true

# ---------------------- pyenv -------------------------------
if [[ ! -d "$PYENV_DIR" ]]; then
  log "Installing pyenv"
  curl -fsSL https://pyenv.run | bash
else
  log "pyenv already installed at $PYENV_DIR"
fi

log "Configuring ~/.bashrc for pyenv (idempotent)"
BASHRC="${HOME}/.bashrc"
append_if_missing 'export PYENV_ROOT="$HOME/.pyenv"' "$BASHRC"
append_if_missing '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' "$BASHRC"
append_if_missing 'eval "$(pyenv init -)"' "$BASHRC"

export PYENV_ROOT="$PYENV_DIR"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# ---------------------- Python 3.9 via pyenv -----------------
if ! pyenv versions --bare | grep -qx "$PYTHON_VERSION"; then
  log "Installing Python ${PYTHON_VERSION} via pyenv (this can take a while)"
  pyenv install -v "$PYTHON_VERSION"
else
  log "Python ${PYTHON_VERSION} already installed in pyenv"
fi

PY39="$(pyenv root)/versions/${PYTHON_VERSION}/bin/python"
[[ -x "$PY39" ]] || die "Expected pyenv Python not found at: $PY39"

log "Ensuring pyenv Python ${PYTHON_VERSION} has working pip tooling"
"$PY39" -m ensurepip --upgrade || true
"$PY39" -m pip install --upgrade pip setuptools wheel

# ---------------------- Coral runtime (APT) -------------------
log "Installing libedgetpu (standard USB runtime) via APT"

sudo install -d -m 0755 /etc/apt/keyrings

if [[ ! -f "$CORAL_KEYRING" ]]; then
  log "Adding Coral APT keyring"
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | sudo gpg --dearmor -o "$CORAL_KEYRING"
else
  log "Coral keyring already present: $CORAL_KEYRING"
fi

if [[ ! -f "$CORAL_LIST" ]]; then
  log "Adding Coral APT source list"
  echo "deb [signed-by=${CORAL_KEYRING}] https://packages.cloud.google.com/apt coral-edgetpu-stable main" \
    | sudo tee "$CORAL_LIST" >/dev/null
else
  log "Coral APT source list already present: $CORAL_LIST"
fi

sudo apt-get update -y

# libedgetpu + usb utils (lsusb) for debugging
sudo apt-get install -y --no-install-recommends \
  libedgetpu1-std \
  usbutils

# ---------------------- Project setup -------------------------
log "Creating ELEC 392 Coral directory at ${PROJECT_DIR}"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

log "Creating / updating Python 3.9 virtual environment at ${PROJECT_DIR}/.venv"
if [[ ! -d ".venv" ]]; then
  "$PY39" -m venv .venv
fi

# Activate venv (shellcheck is fine)
# shellcheck disable=SC1091
source ".venv/bin/activate"

log "Upgrading pip tooling inside venv"
python -m pip install --upgrade pip setuptools wheel

# ---------------------- Install Python deps (venv) ------------
log "Installing pycoral into venv (pinned numpy)"
python -m pip install numpy==1.26.4
python -m pip install --extra-index-url https://google-coral.github.io/py-repo/ "pycoral~=2.0"

log "Installing OpenCV into venv (opencv-python)"
python -m pip install "opencv-python==4.11.0.86"

log "Installing flatbuffers into venv (fixes TFLite metadata compatibility)"
python -m pip install "flatbuffers==23.5.26"

# ---------------------- TPU test script -----------------------
log "Writing TPU detection test script: ${PROJECT_DIR}/list_tpus.py"
cat > "${PROJECT_DIR}/list_tpus.py" <<'EOF'
from pycoral.utils.edgetpu import list_edge_tpus

def main():
    tpus = list_edge_tpus()
    if not tpus:
        print("NO_TPU_DETECTED")
        return 1
    print("TPU_DETECTED")
    for tpu in tpus:
        print(tpu)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
EOF

# ---------------------- Examples (pycoral) --------------------
log "Cloning / updating pycoral examples into ${PROJECT_DIR}/pycoral"
if [[ -d "${PROJECT_DIR}/pycoral/.git" ]]; then
  git -C "${PROJECT_DIR}/pycoral" pull --ff-only || true
else
  git clone --recurse-submodules "$PYCORAL_REPO" "${PROJECT_DIR}/pycoral"
fi

# Install example requirements *into the venv* (avoid accidental system installs)
# Prefer their script if it behaves; fallback to a minimal requirements install.
log "Installing pycoral example requirements into venv"
if [[ -x "${PROJECT_DIR}/pycoral/examples/install_requirements.sh" ]]; then
  # Some scripts call python3 explicitly; force them to use our venv python/pip via PATH
  export PATH="${PROJECT_DIR}/.venv/bin:${PATH}"
  (cd "${PROJECT_DIR}/pycoral" && bash examples/install_requirements.sh) || {
    warn "pycoral examples/install_requirements.sh failed; attempting minimal install instead"
    python -m pip install pillow
  }
else
  warn "No examples/install_requirements.sh found; attempting minimal install"
  python -m pip install pillow
fi

# ---------------------- ELEC 392 starter kit ------------------
log "Cloning / updating ELEC392 Coral Starter Kit"
if [[ -d "${PROJECT_DIR}/${STARTER_DIRNAME}/.git" ]]; then
  git -C "${PROJECT_DIR}/${STARTER_DIRNAME}" pull --ff-only || true
else
  git clone "$STARTER_REPO" "${PROJECT_DIR}/${STARTER_DIRNAME}"
fi

log "Installing starter kit into venv (editable)"
(cd "${PROJECT_DIR}/${STARTER_DIRNAME}" && python -m pip install -e .)

# ---------------------- Final TPU check -----------------------
log "Final check: TPU detected?"
set +e
TPU_OUT="$(python "${PROJECT_DIR}/list_tpus.py" 2>&1)"
TPU_RC=$?
set -e

echo
echo "------------------------------------------------------------"
echo "$TPU_OUT"
echo "------------------------------------------------------------"

if [[ "$TPU_RC" -eq 0 ]]; then
  log "TPU detected!"
else
  warn "TPU NOT detected!"
  warn "Common fixes:"
  warn "  - Plug the Coral USB Accelerator directly into the Pi (avoid flaky hubs)."
  warn "  - Try a different USB port/cable."
  warn "  - Check it appears in: lsusb"
  warn "  - Confirm runtime installed: dpkg -l | grep libedgetpu"
fi

# ---------------------- Done --------------------------------
echo
echo "============================================================"
echo " Setup complete!"
echo
echo " Next steps:"
echo "   1) Activate environment:"
echo "        source ${PROJECT_DIR}/.venv/bin/activate"
echo "   2) Verify TPU:"
echo "        python ${PROJECT_DIR}/list_tpus.py"
echo "   3) Run a pycoral example:"
echo "        cd ${PROJECT_DIR}/pycoral"
echo "        python3 examples/classify_image.py \\"
echo "          --model test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \\"
echo "          --labels test_data/inat_bird_labels.txt \\"
echo "          --input test_data/parrot.jpg"
echo
echo " ELEC 392 Coral environment ready. Script complete."
echo "============================================================"