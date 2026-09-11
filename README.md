# LivingAI: One-Model Local AI Operating System for Android Terminal

**LivingAI CLI** is a **persistent, local-first, human-inspired AI operating environment** designed to run **entirely in Termux on Android**. It uses **only one AI model (HuggingFaceTB/SmolLM3-3B)** for all cognitive tasks, ensuring **offline, private, and autonomous** operation.

---

## **🚀 Features**

✅ **Terminal-First**: Runs entirely in **Termux** on Android.
✅ **One-Model Rule**: Uses **only SmolLM3-3B** (no cloud AI, no secondary models).
✅ **Automatic Model Download**: Downloads, verifies, and loads **SmolLM3-3B** automatically.
✅ **Persistent Memory**: **SQLite-based memory** (memories, goals, skills, lessons).
✅ **Cognitive Engine**: **PERCEIVE → REMEMBER → UNDERSTAND → THINK → PLAN → DECIDE → ACT → OBSERVE → REFLECT → LEARN → CONSOLIDATE → IDLE → REPEAT**.
✅ **Skills System**: **Learn, validate, and execute skills** in a sandboxed environment.
✅ **Goals & Planning**: **Create, track, and execute goals** with task breakdowns.
✅ **Action System**: **Safe terminal actions** with risk levels (LOW/MEDIUM/HIGH/CRITICAL).
✅ **Voice & TTS**: **Optional voice input/output** (Termux:API or Android TTS).
✅ **Backup & Restore**: **Backup and restore** memories, skills, goals, and configs.
✅ **Daemon Mode**: **Background processing** (memory consolidation, goal review).
✅ **Security**: **Audit logging, prompt injection protection, sandboxed skills**.
✅ **Battery & Thermal Protection**: **Stops inference if low battery/overheating**.

---

## **📋 Architecture**

```
ANDROID
   │
   ▼
TERMUX
   │
   ▼
LivingAI CLI (Python)
   │
   ├── Cognitive Engine
   │     ├── Context Builder
   │     ├── Memory Retriever
   │     ├── Goal Resolver
   │     ├── Prompt Builder
   │     ├── SmolLM3-3B (ONLY MODEL)
   │     ├── Output Parser
   │     ├── Decision Engine
   │     └── Action Planner
   │
   ├── Memory (SQLite)
   │     ├── Memories
   │     ├── Goals
   │     ├── Skills
   │     ├── Lessons
   │     └── State
   │
   ├── Model Manager
   │     ├── Downloader
   │     ├── Verifier
   │     └── Runtime
   │
   ├── Terminal UI
   │     ├── ANSI Colors
   │     ├── Progress Bars
   │     ├── Interactive Menus
   │     └── Autocomplete
   │
   └── Platform (Termux/Android)
         ├── Termux API
         ├── Battery Check
         ├── Thermal Check
         └── Storage Check
```

---

## **🛠 Installation**

### **1. Install via cURL (Recommended)**
```bash
curl -fsSL https://raw.githubusercontent.com/abdulraheemnohri/LivingAI/main/install.sh | bash
```

### **2. Manual Installation**
```bash
git clone https://github.com/abdulraheemnohri/LivingAI
cd LivingAI
bash install.sh
```

### **3. Post-Installation**
- The installer will:
  - Detect **Termux, Android version, RAM, storage, and CPU ABI**.
  - Install **required Termux packages** (`python`, `git`, `curl`, `sqlite`, etc.).
  - Set up **`~/.livingai/`** directory structure.
  - Create a **Python virtual environment** (`~/.livingai/runtime/venv/`).
  - Install **Python dependencies**.
  - Download **SmolLM3-3B** (if not already present).
  - Initialize **SQLite database**.
  - Configure **default settings**.

---

## **🚀 Usage**

### **Start LivingAI**
```bash
livingai
```

### **Commands**

| Command | Description |
|---------|-------------|
| `livingai chat` | Start an interactive chat session |
| `livingai ask "question"` | Ask a direct question (output only) |
| `livingai voice` | Voice input/output (if supported) |
| `livingai status` | Show system status (model, memory, goals) |
| `livingai model` | Manage the AI model (download, verify, status) |
| `livingai memory` | Manage memories (list, search, add, forget) |
| `livingai skill` | Manage skills (list, create, test, run) |
| `livingai goal` | Manage goals (list, add, start, complete) |
| `livingai learn` | Review and consolidate learning |
| `livingai activity` | Show recent activity |
| `livingai action` | Manage actions (allowlist, confirmations) |
| `livingai config` | Configure settings |
| `livingai doctor` | Run system diagnostics |
| `livingai benchmark` | Benchmark model performance |
| `livingai backup` | Backup memories, skills, goals |
| `livingai restore` | Restore from backup |
| `livingai daemon` | Start background daemon |
| `livingai idle` | Run idle-mode tasks |
| `livingai shell` | Controlled shell interface |
| `livingai version` | Show version |
| `livingai --help` | Show help |

### **Interactive Mode**
```bash
livingai
```
Then type commands like:
```
livingai > hello
livingai > what are my active goals?
livingai > remember this
livingai > create a skill
livingai > status
```
Exit with `/exit`.

---

## **📂 Directory Structure**

```
~/.livingai/
├── app/               # Application files
├── config/           # Configuration files
│   └── config.yaml   # Main configuration
├── models/           # AI models (SmolLM3-3B)
├── data/             # SQLite database
│   └── livingai.db   # Main database
├── memory/           # Memory exports
├── skills/           # User-defined skills
├── workspace/        # Temporary workspace
├── logs/             # Log files
├── cache/            # Cached files
├── backups/          # Backup files
└── runtime/          # Python virtual environment
    └── venv/
```

---

## **🔧 Configuration**

### **Main Config File**
`~/.livingai/config/config.yaml`

Example:
```yaml
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
```

### **Environment Variables**
```bash
export LIVINGAI_HOME=$HOME/.livingai
export LIVINGAI_MODEL_DIR=$HOME/.livingai/models
export LIVINGAI_CONFIG=$HOME/.livingai/config/config.yaml
export LIVINGAI_LOG_LEVEL=INFO
```

---

## **🤖 Model Management**

### **Download SmolLM3-3B**
```bash
livingai model download
```

### **Verify Model**
```bash
livingai model verify
```

### **Check Model Status**
```bash
livingai model status
```

### **Benchmark Model**
```bash
livingai benchmark
```

---

## **🧠 Cognitive Engine**

The **Cognitive Engine** follows this loop:

```
PERCEIVE
   ↓
REMEMBER
   ↓
UNDERSTAND
   ↓
THINK
   ↓
PLAN
   ↓
DECIDE
   ↓
ACT
   ↓
OBSERVE
   ↓
REFLECT
   ↓
LEARN
   ↓
CONSOLIDATE
   ↓
IDLE
   ↓
REPEAT
```

### **Memory Types**
- **Working Memory**: Short-term, temporary.
- **Short-Term Memory**: Recent interactions.
- **Long-Term Memory**: Persistent knowledge.
- **Episodic Memory**: Events and experiences.
- **Semantic Memory**: Facts and concepts.
- **Procedural Memory**: Skills and procedures.
- **Preference Memory**: User preferences.
- **Goal Memory**: Active and completed goals.
- **Lesson Memory**: Learned lessons.

---

## **🛡 Security**

### **Action Risk Levels**
| Risk Level | Description | Default Behavior |
|------------|-------------|------------------|
| **LOW** | Read-only commands (`ls`, `cat`, `grep`) | Auto-allow |
| **MEDIUM** | File modifications (`mv`, `cp`, `rm`) | Confirmation required |
| **HIGH** | System configuration (`chmod`, `apt`) | Confirmation required |
| **CRITICAL** | Security-sensitive (`su`, `dd`, `rm -rf`) | Blocked by default |

### **Prompt Injection Protection**
- **All inputs are treated as data, not code**.
- **Skills are sandboxed** (no unrestricted shell access).
- **Audit logging** for all actions.

---

## **🔋 Battery & Thermal Protection**

- **Low Battery**: Stops background processing if battery < 20%.
- **Thermal Throttling**: Reduces processing if device is overheating.

---

## **📦 Backup & Restore**

### **Create Backup**
```bash
livingai backup create
```

### **List Backups**
```bash
livingai backup list
```

### **Restore Backup**
```bash
livingai backup restore
```

---

## **🐛 Troubleshooting**

### **Doctor Command**
```bash
livingai doctor
```
Checks:
- Termux environment
- Android version
- Python installation
- Model status
- Storage & RAM
- Permissions

### **Logs**
```bash
cat ~/.livingai/logs/livingai.log
```

---

## **🗑 Uninstall**

```bash
livingai uninstall
```
Options:
1. Remove application only
2. Remove application + cache
3. Remove everything (including memories, skills, logs)

---

## **📜 License**

MIT License. See [LICENSE](LICENSE).

---

## **🤝 Contributing**

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "feat: add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

---

## **📬 Contact**

- **GitHub**: [abdulraheemnohri](https://github.com/abdulraheemnohri)
- **Email**: abdulraheemnohri@gmail.com
