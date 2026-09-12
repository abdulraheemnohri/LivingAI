# LIVINGAI AGENTIC AI EXTENSION

## Overview

Extend LivingAI CLI into a local agentic AI operating system.

The system retains the existing architecture:
- Termux
- Python
- SQLite
- local-first operation
- one AI model
- SmolLM3-3B
- local memory
- skills
- goals
- controlled terminal actions

## Agentic AI Objective

LivingAI must be capable of:

**UNDERSTAND** → **PLAN** → **ACT** → **OBSERVE** → **EVALUATE** → **ADAPT** → **VERIFY** → **COMPLETE**

Instead of:
```
User → AI → Answer
```

Implement:
```
User
 ↓
Goal
 ↓
Agent
 ↓
Plan
 ↓
Tools
 ↓
Actions
 ↓
Observations
 ↓
Evaluation
 ↓
Correction
 ↓
Verification
 ↓
Final Result
```

The agent must be **goal-oriented** rather than merely **conversation-oriented**.

## ONE MODEL ONLY

The agentic architecture continues using:

**HuggingFaceTB/SmolLM3-3B**

The agent framework itself must NOT introduce another AI model.

Agent components such as:
- planner
- evaluator
- task manager
- memory retriever
- tool selector
- safety checker

must be implemented as **software logic** and calls to the same SmolLM3-3B model.

**DO NOT create:**
```
Planner LLM
+
Executor LLM
+
Critic LLM
```

**Instead:**
```
                 SmolLM3-3B
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
     Planning      Evaluation     Reasoning
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                 Agent Engine
```

## AGENT MANAGER

### Responsibilities

- create agents
- start agent runs
- pause agents
- resume agents
- stop agents
- inspect agents
- track agent state
- manage agent goals
- manage agent plans
- manage agent tasks
- manage tool permissions
- manage budgets
- manage retries
- manage deadlines
- manage verification
- store agent history

### Commands

```bash
livingai agent
livingai agent list
livingai agent create
livingai agent start
livingai agent pause
livingai agent resume
livingai agent stop
livingai agent status
livingai agent inspect
livingai agent logs
livingai agent delete
livingai agent schedule
livingai agent schedules
livingai agent cancel
```

## AGENT MODES

- **ASK**: Answer only
- **ASSIST**: Create plans and request confirmation
- **PLAN**: Create a plan without executing it
- **EXECUTE**: Execute approved plan
- **AUTONOMOUS**: Execute allowed tasks according to policies
- **BACKGROUND**: Work on approved background goals during idle periods

## AGENT LIFECYCLE

```
CREATED
 ↓
INITIALIZING
 ↓
UNDERSTANDING
 ↓
PLANNING
 ↓
READY
 ↓
EXECUTING
 ↓
OBSERVING
 ↓
EVALUATING
 ↓
VERIFYING
 ↓
COMPLETED
```

### Failure Path

```
EXECUTING
 ↓
FAILED
 ↓
DIAGNOSING
 ↓
RETRYING
 ↓
EXECUTING
```

If recovery fails:
```
BLOCKED
 ↓
USER INPUT REQUIRED
```

## GOAL-BASED AGENTS

### Example

```bash
livingai agent start "Organize my Downloads folder"
```

The agent transforms the request into:

**GOAL**: Organize Downloads

**TASKS**:
1. Inspect files
2. Identify categories
3. Propose organization
4. Request confirmation
5. Move files
6. Verify results
7. Report completion

## AGENT PLANNER

### Responsibilities

- understand objective
- identify constraints
- identify required tools
- decompose task
- determine dependencies
- estimate complexity
- identify risks
- create execution order
- identify verification requirements

### Plan Format

```json
{
  "goal": "Organize Downloads",
  "tasks": [
    {
      "id": "TASK-0001",
      "title": "Inspect files",
      "description": "List and inspect files in Downloads",
      "dependencies": [],
      "tool": "filesystem.list",
      "risk": "LOW"
    },
    {
      "id": "TASK-0002",
      "title": "Identify categories",
      "description": "Identify file types and categories",
      "dependencies": ["TASK-0001"],
      "tool": null,
      "risk": "LOW"
    }
  ],
  "dependencies": {
    "TASK-0002": ["TASK-0001"]
  },
  "constraints": [],
  "risk": "LOW",
  "verification_required": true
}
```

## TASK GRAPH

Supports dependency graphs:

```
       Task A
       /    \
      ↓      ↓
   Task B  Task C
      \      /
       ↓    ↓
       Task D
```

Each task has:
- id
- title
- description
- status
- priority
- dependencies
- tool
- risk
- timeout
- retry_limit
- verification
- result

## TASK STATES

- PENDING
- READY
- RUNNING
- WAITING
- COMPLETED
- FAILED
- RETRYING
- BLOCKED
- CANCELLED
- SKIPPED

## TOOL SYSTEM

### Components

- **ToolRegistry**: Registry of all available tools
- **ToolSelector**: Selects appropriate tools for tasks
- **ToolExecutor**: Executes tools with validation
- **ToolPermissionManager**: Manages tool permissions

### Available Tools

- filesystem (list, read, write, copy, move, delete, mkdir, stat)
- terminal (execute)
- sqlite (query)
- memory (search, add)
- skills (run)
- calculator (evaluate)
- datetime (now)

### Tool Call Format

```json
{
  "type": "tool_call",
  "tool": "filesystem.list",
  "arguments": {
    "path": "~/storage/downloads"
  }
}
```

### Tool Validation Pipeline

```
Model
 ↓
Tool Request
 ↓
Schema Validation
 ↓
Permission Check
 ↓
Risk Check
 ↓
Argument Sanitization
 ↓
User Confirmation (if required)
 ↓
Execute
 ↓
Return Structured Result
```

## AGENT LOOP

```python
while goal_not_complete:
    observe_context()
    retrieve_memory()
    evaluate_current_state()
    choose_next_task()
    select_tool()
    validate_action()
    execute_action()
    observe_result()
    evaluate_result()
    
    if success:
        verify()
    elif recoverable_failure:
        diagnose()
        retry()
    elif blocked:
        ask_user()
    
    update_memory()
    update_plan()
```

Every loop has limits:
- Maximum steps
- Maximum retries
- Maximum runtime
- Maximum tool calls
- Maximum filesystem operations

## AGENT BUDGET

Each agent receives resource limits:

```yaml
agent:
  max_steps: 50
  max_retries: 3
  max_runtime_minutes: 30
  max_tool_calls: 100
  max_filesystem_ops: 50
  max_generated_output: 10000
  max_background_runtime: 60
```

## LOOP PROTECTION

Prevents infinite loops:
- Retry limit
- Repeated-error detection
- Repeated-tool-call detection
- Cyclic-plan detection
- Timeout
- Maximum steps

If exceeded:
```
Agent stopped: Loop protection triggered.
```

## VERIFICATION ENGINE

Never assume an action succeeded.

**Example**: Move file operation

1. Agent: "Move report.txt"
2. After moving:
   - Check source: NOT FOUND ✓
   - Check destination: FOUND ✓
   - Verify file: PASS ✓
3. Only then mark task complete

## SUCCESS CRITERIA

Every agent goal must define success criteria.

**Example**: Create backup

```yaml
Success:
  - backup exists
  - archive opens
  - database exists
  - checksum valid
```

The agent must not report success until all criteria are satisfied.

## HUMAN-IN-THE-LOOP

The agent knows when to stop and ask the user.

**Ask user when:**
- Permissions are missing
- Action is high-risk
- Task requirements are ambiguous
- Destructive action is required
- Credentials are needed
- External communication requires approval
- Budget is exceeded
- Verification fails repeatedly

**Example**:
```
AGENT PAUSED

I need your confirmation.

Action: Delete 14 duplicate files.
Risk: HIGH

[Allow] [Deny] [Inspect]
```

## AGENT PERMISSION PROFILES

- **READ_ONLY**: No modifications
- **SAFE**: Safe local operations
- **PRODUCTIVITY**: Approved file/task operations
- **FILE_MANAGER**: File organization
- **DEVELOPER**: Development tools
- **AUTONOMOUS**: All explicitly permitted operations
- **CUSTOM**: Custom permissions

## AGENT SECURITY

The agent must never:
- Bypass Android security
- Bypass Termux restrictions
- Steal credentials
- Extract secrets
- Disable security software
- Modify authentication without permission
- Silently send external communications
- Install arbitrary software
- Execute untrusted downloaded scripts

**Security policy always overrides agent instructions.**

## AGENT MEMORY

Each agent run creates structured memory:

```json
{
  "agent_id": "AGT-001",
  "run_id": "RUN-001",
  "goal": "Organize Downloads",
  "plan": {...},
  "tasks": [...],
  "observations": [...],
  "actions": [...],
  "results": [...],
  "failures": [...],
  "lessons": [...],
  "final_result": {...}
}
```

## EXPERIENCE LEARNING

After completion:

```
Agent Run
 ↓
Outcome
 ↓
Reflection
 ↓
Lesson
 ↓
Validation
 ↓
Memory
```

**Example Lesson:**
```
"When organizing Downloads, inspect file extensions before creating categories."
```

## AGENT SKILLS

Agents can use existing skills:

```
Goal
 ↓
Find relevant skills
 ↓
Select skill
 ↓
Validate skill
 ↓
Execute skill
 ↓
Observe
 ↓
Verify
```

## SKILL COMPOSITION

Allow multiple safe skills to be combined:

```
Skill A
   ↓
Skill B
   ↓
Skill C
```

**Example**: Read Report → Analyze Report → Generate Summary → Save Summary

## AGENT ARCHITECTURE

```
                         USER
                           │
                           ▼
                       GOAL ENGINE
                           │
                           ▼
                      AGENT MANAGER
                           │
                           ▼
                     CONTEXT BUILDER
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
         MEMORY          STATE          SKILLS
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                     SMOLLM3-3B
                      ONE MODEL
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
         PLANNER        TOOL SELECTOR   EVALUATOR
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                       TASK GRAPH
                           │
                           ▼
                    PERMISSION GATE
                           │
                           ▼
                       TOOL CALL
                           │
                           ▼
                       EXECUTION
                           │
                           ▼
                      OBSERVATION
                           │
                           ▼
                       EVALUATION
                           │
                 ┌─────────┼─────────┐
                 ▼         ▼         ▼
              SUCCESS    RETRY     BLOCKED
                 │         │         │
                 ▼         ▼         ▼
             VERIFY    RECOVER    USER
                 │         │      INPUT
                 └────┬────┘
                      ▼
                   RESULT
                      │
                      ▼
                  REFLECTION
                      │
                      ▼
                   LEARNING
                      │
                      ▼
                    MEMORY
```

## AGENT COMMAND EXAMPLES

### Simple
```bash
livingai agent start "Create a summary of report.txt"
```

### Complex
```bash
livingai agent start "Organize my project files and create a report"
```

### Planning only
```bash
livingai agent plan "Clean my Downloads folder"
```

### Status
```bash
livingai agent status
```

### Stop
```bash
livingai agent stop AGT-001
```

## AGENT STATUS DISPLAY

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

## AGENT PLAN DISPLAY

```bash
livingai agent inspect AGT-001
```

**Output:**
```
GOAL
Organize Downloads

PLAN

✓ Inspect files
✓ Categorize
✓ Create folders
→ Move files
○ Verify
○ Final report
```

## AGENT LOG

```bash
livingai agent logs AGT-001
```

**Output:**
```
[20:10:01] Agent started
[20:10:02] Goal parsed
[20:10:03] Plan created
[20:10:04] Tool: filesystem.list
[20:10:04] Result: 27 files
[20:10:06] Task completed
[20:10:07] Next task selected
```

## AGENT DASHBOARD

**Interactive dashboard:**
```
ACTIVE AGENTS
─────────────

AGT-001  Organize files     57%
AGT-002  Prepare report     31%

QUEUED

AGT-003  Weekly summary

COMPLETED TODAY

AGT-004  Backup verification
```

## AGENT CONFIGURATION

```yaml
agent:
  enabled: true
  default_mode: assisted
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

## AUTONOMY SETTINGS

**Agent autonomy levels:**
- OFF: No autonomous actions
- ASSISTED: Create plans, request confirmation
- LIMITED: Execute safe actions automatically
- AUTONOMOUS: Execute allowed tasks according to policies

**Controls:**
- Automatic planning
- Automatic tool selection
- Automatic safe actions
- Automatic retry
- Automatic learning
- Background agents
- Scheduled agents
- Event-triggered agents
- Parallel agents

## AGENT RESULT FORMAT

Every completed agent provides:

```yaml
OBJECTIVE: Organize Downloads
PLAN: Multi-step organization plan
ACTIONS: 7 tasks executed
RESULT: SUCCESS
VERIFICATION: PASS
PROBLEMS: 0
CHANGES: 21 files moved
LESSONS: None
FILES CREATED: 3
FILES MODIFIED: 21
```

## AGENTIC CHAT

**Inside `livingai chat`:**

```
User:
> organize my project folder

LivingAI:
I can do that.

Proposed plan:
1. Inspect project
2. Identify duplicate files
3. Identify temporary files
4. Propose changes
5. Apply approved changes
6. Verify structure

Risk: MEDIUM

Proceed?
[Y] Yes
[N] No
[P] Preview
```

## AGENTIC NATURAL LANGUAGE COMMANDS

Supported commands:
- "Plan this."
- "Do this."
- "Do this and verify it."
- "Do this but ask me before changing anything."
- "Do this automatically."
- "Stop."
- "Pause."
- "Continue."
- "Undo the last safe action."

## AGENT PREVIEW

Before risky execution:

```
PROPOSED CHANGES

Create: 3 folders
Move: 17 files
Rename: 2 files
Delete: 0 files

Risk: LOW

[Execute] [Edit Plan] [Cancel]
```

## AGENT LEARNING

If user changes the plan:

**Original:** Move PDF files to Documents
**User:** Keep invoices separate.
**System:** Record preference/lesson

Future plans use validated preferences.

## AGENT SELF-EVALUATION

After each run:
- Was goal achieved?
- Were actions correct?
- Were permissions respected?
- Was verification completed?
- Was user intervention needed?
- Was there an avoidable failure?

Save structured evaluation.

## AGENT OBSERVABILITY

Metrics available via:
```bash
livingai agent metrics
```

**Metrics:**
- Tasks completed
- Tasks failed
- Success rate
- Average steps
- Average retries
- Tool calls
- Verification rate
- User interventions
- Runtime
- RAM usage
- Model tokens used

## AGENT SECURITY PRIORITY

Priority order:
1. **USER SAFETY**
2. **SYSTEM SECURITY**
3. **PERMISSION POLICY**
4. **USER GOAL**
5. **AGENT PLAN**
6. **OPTIMIZATION**

**The agent cannot override a higher-level rule to accomplish a lower-level goal.**

## DEFINITION OF DONE

The agentic extension is complete when LivingAI can:

✓ Understand natural-language goals
✓ Create multi-step plans
✓ Decompose goals into tasks
✓ Build task dependencies
✓ Select available tools
✓ Generate structured tool calls
✓ Validate tool calls
✓ Request permissions
✓ Execute safe operations
✓ Observe results
✓ Detect failures
✓ Retry recoverable failures
✓ Change strategy after failure
✓ Verify results
✓ Stop when successful
✓ Ask the user when blocked
✓ Pause
✓ Resume
✓ Stop
✓ Recover after crashes
✓ Maintain checkpoints
✓ Maintain agent memory
✓ Learn validated lessons
✓ Reuse skills
✓ Schedule agents
✓ Run approved background tasks
✓ Apply resource limits
✓ Prevent infinite loops
✓ Maintain audit logs
✓ Provide transparent status
✓ Never silently execute dangerous operations
✓ Never bypass security
✓ Never use a second AI model
✓ Work locally after model installation
✓ Continue functioning without cloud AI

## FINAL PRINCIPLE

LivingAI should behave like a **goal-driven digital worker**, not a chatbot.

- **Model** provides intelligence
- **Agent Engine** provides agency
- **Memory Engine** provides continuity
- **Skill Engine** provides reusable abilities
- **Tool Engine** provides capabilities
- **Permission Engine** provides boundaries
- **Verification Engine** provides reliability
- **Scheduler** provides persistence
- **Reflection Engine** provides improvement

**Together:**

INTELLIGENCE + MEMORY + AGENCY + TOOLS + GOALS + PLANNING + EXECUTION + OBSERVATION + VERIFICATION + LEARNING = **LIVINGAI AGENT**

The entire system remains powered by **one local SmolLM3-3B model**.
