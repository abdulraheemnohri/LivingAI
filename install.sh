#!/bin/bash

# LivingAI Termux Installer
# ========================
# This script automates the installation of LivingAI CLI in Termux on Android.
# It detects the environment, installs dependencies, and sets up the application.

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Functions ---

# Print a colored message
print_message() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Print an error and exit
print_error_and_exit() {
    print_message "$RED" "❌ $1"
    exit 1
}

# Print a success message
print_success() {
    print_message "$GREEN" "✅ $1"
}

# Print an info message
print_info() {
    print_message "$BLUE" "ℹ️ $1"
}

# Print a warning message
print_warning() {
    print_message "$YELLOW" "⚠️ $1"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Termux Detection ---
print_info "Detecting Termux environment..."
if ! command_exists "termux-info" && ! [[ -d "$PREFIX" ]]; then
    print_error_and_exit "This script must be run in Termux on Android."
fi
print_success "Termux detected."

# --- Android Detection ---
print_info "Detecting Android version..."
ANDROID_VERSION=$(getprop ro.build.version.release 2>/dev/null || echo "Unknown")
ANDROID_SDK=$(getprop ro.build.version.sdk 2>/dev/null || echo "Unknown")
print_success "Android Version: $ANDROID_VERSION (SDK: $ANDROID_SDK)"

# --- Architecture Detection ---
print_info "Detecting CPU architecture..."
CPU_ABI=$(getprop ro.product.cpu.abi 2>/dev/null || uname -m)
print_success "CPU ABI: $CPU_ABI"

# --- RAM Detection ---
print_info "Detecting RAM..."
TOTAL_RAM=$(free -b | awk '/^Mem:/{print $2}')
TOTAL_RAM_GB=$((TOTAL_RAM / 1073741824))
AVAILABLE_RAM=$(free -b | awk '/^Mem:/{print $4}')
AVAILABLE_RAM_GB=$((AVAILABLE_RAM / 1073741824))
print_success "Total RAM: ${TOTAL_RAM_GB}GB, Available: ${AVAILABLE_RAM_GB}GB"

# --- Storage Detection ---
print_info "Detecting storage..."
STORAGE_PATH=$(df -h /data | awk 'NR==2 {print $4}')
print_success "Available Storage: $STORAGE_PATH"

# --- Python Detection ---
print_info "Detecting Python..."
if command_exists "python3"; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    print_success "Python: $PYTHON_VERSION"
elif command_exists "python"; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    print_success "Python: $PYTHON_VERSION"
else
    print_warning "Python not found. Installing Python..."
    pkg install -y python || print_error_and_exit "Failed to install Python."
    PYTHON_CMD="python"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    print_success "Python installed: $PYTHON_VERSION"
fi

# --- Git Detection ---
print_info "Detecting Git..."
if ! command_exists "git"; then
    print_warning "Git not found. Installing Git..."
    pkg install -y git || print_error_and_exit "Failed to install Git."
    print_success "Git installed."
else
    print_success "Git detected."
fi

# --- Curl Detection ---
print_info "Detecting Curl..."
if ! command_exists "curl"; then
    print_warning "Curl not found. Installing Curl..."
    pkg install -y curl || print_error_and_exit "Failed to install Curl."
    print_success "Curl installed."
else
    print_success "Curl detected."
fi

# --- Required Termux Packages ---
print_info "Installing required Termux packages..."
REQUIRED_PACKAGES=(
    "python"
    "git"
    "curl"
    "wget"
    "clang"
    "make"
    "cmake"
    "pkg-config"
    "openssl"
    "libffi"
    "sqlite"
    "ffmpeg"
    "ripgrep"
    "jq"
    "unzip"
    "zip"
)

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! pkg list-installed | grep -q "^$pkg$"; then
        print_warning "Installing $pkg..."
        pkg install -y "$pkg" || print_warning "Failed to install $pkg. Continuing..."
    else
        print_success "$pkg is already installed."
    fi
done

# --- Create LivingAI Directory ---
print_info "Creating LivingAI directory structure..."
LIVINGAI_HOME="$HOME/.livingai"
mkdir -p "$LIVINGAI_HOME/app"
mkdir -p "$LIVINGAI_HOME/config"
mkdir -p "$LIVINGAI_HOME/models"
mkdir -p "$LIVINGAI_HOME/data"
mkdir -p "$LIVINGAI_HOME/memory"
mkdir -p "$LIVINGAI_HOME/skills"
mkdir -p "$LIVINGAI_HOME/workspace"
mkdir -p "$LIVINGAI_HOME/logs"
mkdir -p "$LIVINGAI_HOME/cache"
mkdir -p "$LIVINGAI_HOME/backups"
mkdir -p "$LIVINGAI_HOME/runtime/venv"
print_success "Directory structure created at $LIVINGAI_HOME."

# --- Clone LivingAI Repository ---
print_info "Cloning LivingAI repository..."
REPO_DIR="$HOME/LivingAI"
if [ -d "$REPO_DIR" ]; then
    print_warning "LivingAI repository already exists. Pulling latest changes..."
    cd "$REPO_DIR" && git pull || print_warning "Failed to pull latest changes."
else
    git clone https://github.com/abdulraheemnohri/LivingAI "$REPO_DIR" || print_error_and_exit "Failed to clone LivingAI repository."
fi
print_success "LivingAI repository cloned to $REPO_DIR."

# --- Create Python Virtual Environment ---
print_info "Creating Python virtual environment..."
cd "$REPO_DIR"
$PYTHON_CMD -m venv "$LIVINGAI_HOME/runtime/venv" || print_error_and_exit "Failed to create virtual environment."
source "$LIVINGAI_HOME/runtime/venv/bin/activate"
print_success "Python virtual environment created."

# --- Install Python Dependencies ---
print_info "Installing Python dependencies..."
pip install --upgrade pip || print_warning "Failed to upgrade pip."
pip install -e . || print_error_and_exit "Failed to install LivingAI package."
print_success "Python dependencies installed."

# --- Initialize Configuration ---
print_info "Initializing configuration..."
CONFIG_FILE="$LIVINGAI_HOME/config/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
model:
  repository: HuggingFaceTB/SmolLM3-3B
  revision: main
  runtime: auto
  quantization: auto
  context: auto
  threads: auto
  batch_size: auto

generation:
  temperature: 0.7
  top_p: 0.9
  max_tokens: 512
  streaming: true

memory:
  enabled: true
  consolidation_interval: 3600

learning:
  enabled: true
  auto_consolidate: true

skills:
  enabled: true
  sandbox: true

actions:
  auto_allow_low_risk: true
  confirm_medium_risk: true
  block_high_risk: true

voice:
  enabled: false
  stt_engine: termux
  tts_engine: android

privacy:
  cloud_ai: false
  telemetry: false
  analytics: false

battery:
  min_percentage: 20
  charging_required: false

logging:
  level: INFO
  file: ~/.livingai/logs/livingai.log
EOF
    print_success "Configuration initialized at $CONFIG_FILE."
else
    print_warning "Configuration file already exists. Skipping."
fi

# --- Initialize Database ---
print_info "Initializing database..."
DATABASE_FILE="$LIVINGAI_HOME/data/livingai.db"
if [ ! -f "$DATABASE_FILE" ]; then
    $PYTHON_CMD -c "
import sqlite3
import os

db_path = os.path.expanduser('$DATABASE_FILE')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    importance REAL DEFAULT 0.5,
    relevance REAL DEFAULT 0.5,
    recency REAL DEFAULT 0.5,
    confidence REAL DEFAULT 0.5,
    frequency INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'PLANNED',
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    source TEXT,
    importance REAL DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event TEXT NOT NULL,
    action TEXT,
    risk TEXT,
    permission TEXT,
    result TEXT,
    error TEXT
)
''')

conn.commit()
conn.close()
print('✅ Database initialized.')
" || print_error_and_exit "Failed to initialize database."
else
    print_warning "Database file already exists. Skipping."
fi

# --- Download SmolLM3-3B Model ---
print_info "Checking for SmolLM3-3B model..."
MODEL_DIR="$LIVINGAI_HOME/models"
MODEL_PATH="$MODEL_DIR/SmolLM3-3B"
if [ ! -d "$MODEL_PATH" ]; then
    print_warning "SmolLM3-3B not found. Downloading..."
    cd "$MODEL_DIR"
    git lfs install || print_warning "Git LFS not installed. Continuing without it."
    git clone https://huggingface.co/HuggingFaceTB/SmolLM3-3B "$MODEL_PATH" || print_error_and_exit "Failed to download SmolLM3-3B."
    print_success "SmolLM3-3B downloaded to $MODEL_PATH."
else
    print_success "SmolLM3-3B already exists at $MODEL_PATH."
fi

# --- Add LivingAI to PATH ---
print_info "Adding LivingAI to PATH..."
if ! grep -q "export PATH=\"\(.*\)$HOME/LivingAI/bin:\1" "$HOME/.bashrc"; then
    echo 'export PATH="$HOME/LivingAI/bin:$PATH"' >> "$HOME/.bashrc"
    print_success "Added LivingAI to PATH in ~/.bashrc."
else
    print_warning "LivingAI already in PATH. Skipping."
fi

# --- Create livingai CLI Symlink ---
print_info "Creating livingai CLI symlink..."
BIN_DIR="$HOME/LivingAI/bin"
mkdir -p "$BIN_DIR"
LIVINGAI_SCRIPT="$BIN_DIR/livingai"
cat > "$LIVINGAI_SCRIPT" << 'EOF'
#!/bin/bash
source "$HOME/.livingai/runtime/venv/bin/activate"
exec python -m livingai.cli "$@"
EOF
chmod +x "$LIVINGAI_SCRIPT"
print_success "Created livingai CLI symlink at $LIVINGAI_SCRIPT."

# --- Final Checks ---
print_info "Running final checks..."

# Check if livingai command works
if command_exists "livingai"; then
    print_success "livingai command is available."
else
    print_warning "livingai command not found. Try restarting Termux or running:"
    print_warning "source ~/.bashrc"
fi

# Check model files
if [ -d "$MODEL_PATH" ]; then
    print_success "SmolLM3-3B model is ready."
else
    print_warning "SmolLM3-3B model not found. Run 'livingai model download' to install."
fi

# --- Summary ---
print_success ""
print_message "$CYAN" "╭──────────────────────────────────────────────╮"
print_message "$CYAN" "│              ✦ LIVINGAI INSTALLATION COMPLETE ✦       │"
print_message "$CYAN" "╰──────────────────────────────────────────────╯"
print_message "$CYAN" ""
print_message "$CYAN" "Next Steps:"
print_message "$CYAN" "1. Restart Termux or run: source ~/.bashrc"
print_message "$CYAN" "2. Run: livingai doctor (to verify installation)"
print_message "$CYAN" "3. Run: livingai (to start the CLI)"
print_message "$CYAN" ""
print_message "$CYAN" "Installation Log: $LIVINGAI_HOME/logs/install.log"
print_message "$CYAN" ""
