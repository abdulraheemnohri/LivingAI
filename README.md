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
✅ **Agentic AI**: **Goal-driven autonomous agents** with planning, execution, and verification.

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

   AND

   Agentic Engine
   │
   ├── Agent Manager
   │     ├── Agent Creation
   │     ├── Agent Execution
   │     ├── Agent Monitoring
   │     └── Agent History
   │
   ├── Agent Planner
   │     ├── Goal Understanding
   │     ├── Task Decomposition
   │     ├── Dependency Resolution
   │     └── Risk Assessment
   │
   ├── Task Graph
   │     ├── Task Management
   │     ├── Dependency Tracking
   │     └── Execution Order
   │
   ├── Tool System
   │     ├── Tool Registry
   │     ├── Tool Selector
   │     ├── Tool Executor
   │     └── Permission Manager
   │
   ├── Verification Engine
   │     ├── Result Verification
   │     ├── Success Criteria
   │     └── Quality Assurance
   │
   └── State Machine
         ├── Lifecycle Management
         └── State Transitions
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
| `livingai agent` | **Manage autonomous agents** |

### **Agent Commands**

| Agent Command | Description |
|---------------|-------------|
| `livingai agent list` | List all agents |
| `livingai agent create <goal>` | Create a new agent |
| `livingai agent start <goal>` | Start an agent run |
| `livingai agent pause <run_id>` | Pause an agent run |
| `livingai agent resume <run_id>` | Resume a paused agent |
| `livingai agent stop <run_id>` | Stop an agent run |
| `livingai agent status` | Show status of active runs |
| `livingai agent inspect <run_id>` | Inspect an agent run in detail |
| `livingai agent logs <run_id>` | Show logs for an agent run |
| `livingai agent delete <agent_id>` | Delete an agent |

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
livingai > agent start "Organize my Downloads folder"
```
Exit with `/exit`.

---

## **🎯 Agentic AI System**

LivingAI now includes a **complete Agentic AI layer** that transforms it from a chatbot into a **goal-driven digital worker**.

### **Agent Capabilities**

- **UNDERSTAND** natural-language goals
- **CREATE** multi-step plans with task dependencies
- **SELECT** appropriate tools for each task
- **EXECUTE** tasks with validation and permissions
- **OBSERVE** results and detect failures
- **RETRY** recoverable failures automatically
- **VERIFY** results meet success criteria
- **LEARN** from each run to improve future performance
- **REPORT** completion with full transparency

### **Agent Modes**

| Mode | Description | Use Case |
|------|-------------|----------|
| **ASK** | Answer only | Simple questions |
| **ASSIST** | Create plans, request confirmation | Safe operations |
| **PLAN** | Create plan without executing | Review before action |
| **EXECUTE** | Execute approved plan | Pre-approved tasks |
| **AUTONOMOUS** | Execute allowed tasks | Trusted operations |
| **BACKGROUND** | Work during idle | Background processing |

### **Agent Example**

```bash
# Start an agent to organize Downloads
livingai agent start "Organize my Downloads folder"

# The agent will:
# 1. Understand the goal
# 2. Create a plan with tasks
# 3. Request confirmation for risky actions
# 4. Execute the plan
# 5. Verify results
# 6. Report completion
```

### **Agent Status Display**

```
╭──────────────────────────────────────────╮
│ AGENT STATUS                             │
├──────────────────────────────────────────┤
│ ID:       AGT-001                        │
│ Goal:     Organize Downloads             │
│ State:    EXECUTING                      │
│ Progress: 4/7 tasks                      │
│ Steps:    9/50                           │
│ Tools:    6                              │
│ Retries:  1/3                            │
│ Risk:     LOW                            │
│ Runtime:  03:21                          │
╰──────────────────────────────────────────╯
```

### **Agent Plan Display**

```
GOAL: Organize Downloads

PLAN:
✓ Inspect files
✓ Categorize
✓ Create folders
→ Move files
○ Verify
○ Final report
```

### **Agent Security**

- **One Model Only**: All agent intelligence comes from SmolLM3-3B
- **Permission Profiles**: READ_ONLY, SAFE, PRODUCTIVITY, FILE_MANAGER, DEVELOPER, AUTONOMOUS
- **Risk Assessment**: Every action is evaluated for risk
- **User Confirmation**: Required for medium/high/critical risk actions
- **Loop Protection**: Prevents infinite retries and circular dependencies
- **Resource Limits**: Budgets for steps, tool calls, runtime, and retries

### **Agent Verification**

Every action is verified:
- File operations: Check source/deletion and destination/creation
- Tool execution: Validate success and results
- Task completion: Verify all dependencies are satisfied
- Final result: Confirm all success criteria are met

### **Agent Learning**

After each run, agents:
1. Analyze the outcome
2. Extract lessons learned
3. Validate lessons with user feedback
4. Store lessons in memory
5. Use lessons to improve future plans

---

## **📂 Directory Structure**

```
~/.livingai/
├── app/               # Application files
├── config/           # Configuration files
│   └── config.yaml   # Main configuration
├── models/           # AI models (SmolLM3-3B)
├── data/             # SQLite database
│   ├── livingai.db   # Main database
│   └── agents.db     # Agent database
├── memory/           # Memory exports
├── skills/           # User-defined skills
├── workspace/        # Temporary workspace
├── logs/             # Log files
├── cache/            # Cached files
├── backups/          # Backup files
└── runtime/          # Python virtual environment
    └── venv/
```

**New Agent Files:**
```
livingai/agents/
├── __init__.py          # Package initialization
├── manager.py           # AgentManager - manages agent lifecycle
├── planner.py           # AgentPlanner - creates execution plans
├── task.py              # Task and TaskGraph - task management
├── state_machine.py     # AgentStateMachine - state transitions
├── tool_registry.py     # ToolRegistry - tool management
├── verification.py      # VerificationEngine - result verification
├── database.py          # AgentDatabase - SQLite storage
└── cli_handlers.py      # CLI command handlers
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

# Agent Configuration
agent:
  enabled: true
  default_mode: ASSIST
  max_steps: 50
  max_retries: 3
  max_runtime_minutes: 30
  max_tool_calls: 100
  require_confirmation: true
  verify_actions: true
  learn_from_runs: true
  background_agents: false
  parallel_agents: false
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

### **Agent Security**
- **One Model Rule**: Only SmolLM3-3B is used
- **Permission Gates**: Every action checked against profile
- **Risk Assessment**: All actions evaluated before execution
- **No Silent Execution**: User confirmation for risky actions
- **Audit Trail**: Complete logs of all agent actions

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

## **📚 Agentic AI Documentation**

For complete details on the Agentic AI system, see:
- **[LIVINGAI_AGENTIC_AI_EXTENSION.md](LIVINGAI_AGENTIC_AI_EXTENSION.md)** - Full agentic architecture specification

This document includes:
- Complete agent lifecycle
- Agent modes and configurations
- Task graph and dependency management
- Tool system architecture
- Verification engine
- Security policies
- Example agent runs
- Command reference

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

### **Agent Logs**
```bash
livingai agent logs <run_id>
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
