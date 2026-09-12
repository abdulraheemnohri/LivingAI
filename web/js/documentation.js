/**
 * LivingAI - Documentation JavaScript
 * ===================================
 * Documentation viewer with search, navigation, and markdown rendering
 */

// ============================================
// DOCUMENTATION INITIALIZATION
// ============================================

let documentation = {};
let currentSection = 'overview';
let searchIndex = [];

function initDocumentation() {
    console.log('Initializing Documentation Module...');
    
    // Load documentation
    loadDocumentation();
    
    // Initialize navigation
    initNavigation();
    
    // Initialize search
    initSearch();
    
    console.log('Documentation Module Initialized');
}

// ============================================
// DATA LOADING
// ============================================

async function loadDocumentation() {
    console.log('Loading documentation...');
    
    try {
        // Show loading state
        const docContainer = document.getElementById('documentation-container');
        if (docContainer) {
            docContainer.innerHTML = '<div class="loading-spinner"></div>';
        }
        
        // Fetch documentation from API (or use mock data)
        documentation = await fetchDocumentation();
        
        // Build search index
        buildSearchIndex();
        
        // Render documentation
        renderDocumentation();
        renderNavigation();
        
        console.log('Documentation loaded');
    } catch (error) {
        console.error('Error loading documentation:', error);
        showError('Failed to load documentation');
        
        // Show empty state
        const docContainer = document.getElementById('documentation-container');
        if (docContainer) {
            docContainer.innerHTML = '<div class="empty-state"><i class="fa fa-book"></i><p>No documentation available</p></div>';
        }
    }
}

async function fetchDocumentation() {
    // Simulate API call
    // Replace with: const response = await fetch('/api/documentation');
    // return await response.json();
    
    return {
        title: 'LivingAI Documentation',
        description: 'Complete documentation for LivingAI - Local AI Operating System',
        version: '1.0.0',
        lastUpdated: '2024-01-20',
        sections: {
            overview: {
                title: 'Overview',
                icon: 'fa-home',
                content: `# LivingAI Overview

## What is LivingAI?

LivingAI is a **Local AI Operating System** designed to run entirely on your Android device. It provides a complete AI-powered environment for tasks, agents, tools, and memory management without requiring cloud connectivity.

## Key Features

- **🤖 AI Agents**: Create and manage specialized AI agents for different tasks
- **🔧 Tools Integration**: Access a growing library of AI tools and utilities
- **📋 Task Management**: Organize, prioritize, and track AI-powered tasks
- **💾 Memory System**: Store and retrieve knowledge, conversations, and data
- **🖥️ Terminal Interface**: Command-line interface for power users
- **📊 Analytics**: Monitor system performance and usage statistics
- **⚙️ Customizable**: Tailor the system to your specific needs

## Architecture

LivingAI follows a modular architecture with the following components:

1. **Core Engine**: The heart of LivingAI that manages agents, tools, and tasks
2. **Memory System**: Persistent storage for knowledge and data
3. **API Layer**: RESTful API for programmatic access
4. **User Interface**: Web-based dashboard and mobile app
5. **Integration Layer**: Connectors for external services

## Use Cases

- **Research**: Automate web research and data gathering
- **Development**: Generate code, debug, and test applications
- **Analysis**: Process and analyze complex datasets
- **Creativity**: Generate content, brainstorm ideas, and solve problems
- **Automation**: Streamline repetitive tasks with AI agents

## Getting Started

1. Install LivingAI on your Android device
2. Launch the application and complete the setup
3. Create your first AI agent
4. Explore available tools and start using them
5. Customize settings to match your preferences`
            },
            installation: {
                title: 'Installation',
                icon: 'fa-download',
                content: `# Installation Guide

## System Requirements

- Android 8.0 (Oreo) or higher
- Minimum 2 GB RAM
- 100 MB free storage space
- Internet connection (for initial setup and updates)

## Installation Methods

### Method 1: Google Play Store (Coming Soon)

1. Open Google Play Store on your Android device
2. Search for "LivingAI"
3. Tap "Install"
4. Wait for the installation to complete
5. Open the app and follow the setup instructions

### Method 2: APK Download

1. Download the latest APK from our [releases page](https://github.com/abdulraheemnohri/LivingAI/releases)
2. Enable "Unknown Sources" in your device settings
3. Open the downloaded APK file
4. Tap "Install" and confirm
5. Open LivingAI from your app drawer

### Method 3: Build from Source

See the [Development Guide](#development) section for build instructions.

## Post-Installation Setup

After installation, follow these steps:

1. **Language Selection**: Choose your preferred language (English, Urdu, etc.)
2. **Theme Selection**: Select dark or light theme
3. **Permissions**: Grant necessary permissions for full functionality
4. **Initial Configuration**: Set up your first AI agent
5. **Tutorial**: Complete the interactive tutorial (recommended)

## Updating LivingAI

LivingAI supports automatic updates. You can also manually check for updates:

1. Open LivingAI
2. Go to Settings
3. Select "Check for Updates"
4. If an update is available, follow the prompts to install

## Uninstalling

To uninstall LivingAI:

1. Go to your device Settings
2. Open Apps or Application Manager
3. Find LivingAI in the list
4. Tap "Uninstall"
5. Confirm the uninstallation

> **Note**: Uninstalling will remove all local data. Make sure to export your data first if you want to keep it.`
            },
            agents: {
                title: 'Agents',
                icon: 'fa-users',
                content: `# AI Agents

## What are Agents?

Agents are specialized AI entities that can perform specific tasks. Each agent has its own personality, capabilities, and knowledge base.

## Agent Types

LivingAI comes with several pre-configured agent types:

### Research Agent
- **Purpose**: Web research, data gathering, and information retrieval
- **Capabilities**: Web search, content summarization, data extraction
- **Use Cases**: Market research, competitive analysis, fact-checking

### Development Agent
- **Purpose**: Software development assistance
- **Capabilities**: Code generation, debugging, testing, documentation
- **Use Cases**: Building applications, fixing bugs, writing tests

### Analysis Agent
- **Purpose**: Data analysis and pattern recognition
- **Capabilities**: Statistical analysis, data visualization, predictive modeling
- **Use Cases**: Business intelligence, trend analysis, decision support

### Creative Agent
- **Purpose**: Creative tasks and content generation
- **Capabilities**: Text generation, brainstorming, storytelling, design
- **Use Cases**: Content creation, idea generation, creative writing

### General Purpose Agent
- **Purpose**: Versatile AI assistant
- **Capabilities**: General knowledge, conversation, problem-solving
- **Use Cases**: Q&A, advice, general assistance

## Creating Agents

To create a new agent:

1. Navigate to the **Agents** section
2. Click "Create New Agent"
3. Enter a name for your agent
4. Select an agent type
5. Configure agent-specific settings
6. Click "Create Agent"

## Agent Configuration

Each agent can be customized with the following settings:

- **Name**: Unique identifier for the agent
- **Type**: Determines the agent's capabilities
- **Description**: Brief description of the agent's purpose
- **Personality**: Define the agent's tone and style
- **Knowledge Base**: Upload or connect to specific knowledge sources
- **Tools**: Select which tools the agent can use
- **Permissions**: Set access controls for the agent

## Managing Agents

### Starting/Stopping Agents
- Agents can be started or stopped as needed
- Active agents consume system resources
- Inactive agents are paused but retain their state

### Editing Agents
- Modify agent configuration at any time
- Changes take effect immediately for active agents

### Deleting Agents
- Delete agents that are no longer needed
- Deleting an agent removes all its data and history

## Agent Workflow

1. **Creation**: Define the agent's purpose and capabilities
2. **Configuration**: Customize the agent's behavior and tools
3. **Activation**: Start the agent to make it available
4. **Task Assignment**: Assign tasks to the agent
5. **Execution**: Agent processes tasks autonomously
6. **Review**: Monitor results and provide feedback

## Best Practices

- Give agents descriptive names
- Use appropriate agent types for different tasks
- Limit the number of active agents based on your device capabilities
- Regularly review and update agent configurations
- Monitor agent performance and adjust as needed`
            },
            tools: {
                title: 'Tools',
                icon: 'fa-wrench',
                content: `# Tools

## Overview

Tools are the building blocks that enable LivingAI to perform various tasks. Each tool is a specialized function that can be used by agents or directly by users.

## Tool Categories

### Search Tools
- **Web Search**: Search the internet for information
- **Site Search**: Search within specific websites
- **Image Search**: Find images based on descriptions

### Development Tools
- **Code Generation**: Generate code in various programming languages
- **Code Review**: Analyze and review code for quality
- **Debugging**: Identify and fix code issues
- **Testing**: Create and run tests

### Analysis Tools
- **Data Analysis**: Process and analyze structured data
- **Statistical Analysis**: Perform statistical calculations
- **Data Visualization**: Create charts and graphs
- **Predictive Modeling**: Build predictive models

### Text Processing Tools
- **Summarization**: Condense long texts into summaries
- **Translation**: Translate text between languages
- **Text Generation**: Generate human-like text
- **Sentiment Analysis**: Determine the sentiment of text

### Creative Tools
- **Image Generation**: Create images from text prompts
- **Content Generation**: Generate various types of content
- **Brainstorming**: Generate ideas and solutions
- **Story Telling**: Create stories and narratives

### System Tools
- **File Management**: Manage files and directories
- **Database Query**: Execute SQL queries
- **API Integration**: Connect to external APIs
- **System Monitoring**: Monitor system health

## Using Tools

### Direct Usage
1. Navigate to the **Tools** section
2. Browse or search for the tool you need
3. Click on the tool
4. Enter the required input
5. Execute the tool
6. View the results

### Agent Usage
1. Assign tools to an agent during creation or editing
2. When the agent performs tasks, it will use its assigned tools
3. Monitor tool usage in the agent's activity log

## Tool Configuration

Each tool can be configured with:

- **Name**: Tool identifier
- **Description**: What the tool does
- **Parameters**: Input parameters the tool accepts
- **API Keys**: Required credentials (if applicable)
- **Rate Limits**: Usage limits to prevent abuse
- **Timeout**: Maximum execution time

## Creating Custom Tools

You can create custom tools to extend LivingAI's capabilities:

1. Navigate to **Tools** > **Create Custom Tool**
2. Define the tool's purpose and parameters
3. Write the implementation code (JavaScript/Python)
4. Test the tool
5. Deploy the tool

### Custom Tool Example

```javascript
// Example: Custom greeting tool
function greet(name) {
    return `Hello, ${name}! Welcome to LivingAI.`;
}

// Tool configuration
{
    name: "Custom Greeting",
    description: "Generates a personalized greeting",
    parameters: [
        {
            name: "name",
            type: "string",
            required: true,
            description: "The name to greet"
        }
    ],
    implementation: greet
}
```

## Tool Management

### Enabling/Disabling Tools
- Enable tools that you want to use
- Disable tools that you don't need
- Disabled tools are not available to agents

### Updating Tools
- Update tool configurations as needed
- Updates may require restarting active agents

### Deleting Tools
- Remove tools that are no longer needed
- Deleting a tool removes it from all agents that use it

## Tool Performance

Monitor tool performance in the Analytics section:

- **Usage Count**: How often each tool is used
- **Success Rate**: Percentage of successful executions
- **Execution Time**: Average time to complete
- **Error Rate**: Frequency of failures

## Best Practices

- Only enable tools that you need
- Regularly update tools to their latest versions
- Monitor tool usage and performance
- Review and clean up unused tools periodically
- Secure API keys and sensitive credentials`
            },
            tasks: {
                title: 'Tasks',
                icon: 'fa-tasks',
                content: `# Task Management

## What are Tasks?

Tasks are specific jobs or operations that you want LivingAI to perform. Tasks can be simple one-time operations or complex multi-step workflows.

## Task Types

### Simple Tasks
- Single operation that runs once
- Example: "Summarize this document"
- Example: "Translate this text to Urdu"

### Complex Tasks
- Multiple steps or operations
- Example: "Research AI trends, analyze data, and create a report"
- Can involve multiple agents and tools

### Recurring Tasks
- Tasks that run on a schedule
- Example: "Daily news summary at 9 AM"
- Example: "Weekly system health check"

## Creating Tasks

To create a new task:

1. Navigate to the **Tasks** section
2. Click "Create New Task"
3. Enter a title and description
4. Select an agent to perform the task
5. Choose the tools to use
6. Set priority and due date
7. Configure task-specific settings
8. Click "Create Task"

## Task Configuration

### Basic Settings
- **Title**: Brief description of the task
- **Description**: Detailed explanation of what the task should do
- **Agent**: Which agent will perform the task
- **Tools**: Which tools are available to the agent

### Advanced Settings
- **Priority**: Low, Medium, High, or Critical
- **Due Date**: When the task should be completed
- **Retry Count**: How many times to retry if the task fails
- **Timeout**: Maximum time allowed for the task
- **Notifications**: When to notify you about task status

## Task Status

Tasks can have the following statuses:

- **Pending**: Task has been created but not started
- **In Progress**: Task is currently running
- **Completed**: Task has finished successfully
- **Failed**: Task failed to complete
- **Cancelled**: Task was cancelled by the user

## Managing Tasks

### Starting Tasks
- Tasks can be started manually or automatically
- Auto-start can be configured in settings

### Monitoring Tasks
- View task progress in the Tasks section
- Detailed logs are available for each task
- Real-time updates for in-progress tasks

### Pausing/Resuming Tasks
- Pause tasks that need to be temporarily stopped
- Resume paused tasks to continue execution

### Cancelling Tasks
- Cancel tasks that are no longer needed
- Cancelled tasks cannot be resumed

### Deleting Tasks
- Remove tasks from the system
- Deleting a task removes all its history and data

## Task Workflow

1. **Creation**: Define what the task should do
2. **Queueing**: Task is added to the queue
3. **Execution**: Agent starts working on the task
4. **Progress**: Task makes progress (can be monitored)
5. **Completion**: Task finishes successfully or fails
6. **Review**: Review results and provide feedback

## Task Prioritization

Tasks are executed based on priority:

1. **Critical**: Highest priority, runs immediately
2. **High**: Runs after critical tasks
3. **Medium**: Runs after high priority tasks
4. **Low**: Runs when system resources are available

## Best Practices

- Use descriptive titles for tasks
- Set appropriate priorities based on urgency
- Set realistic due dates
- Monitor long-running tasks
- Review completed tasks for quality
- Clean up old or unnecessary tasks regularly`
            },
            memory: {
                title: 'Memory System',
                icon: 'fa-database',
                content: `# Memory System

## Overview

The Memory System is LivingAI's persistent storage for knowledge, conversations, and data. It allows the system to remember and learn from interactions, making it smarter over time.

## Memory Types

### Knowledge Base
- **Purpose**: Store facts, information, and knowledge
- **Content**: Documents, notes, research findings
- **Use Cases**: Reference material, knowledge sharing, learning

### Conversations
- **Purpose**: Store chat history and interactions
- **Content**: User prompts, AI responses, context
- **Use Cases**: Continuing conversations, reference past discussions

### Settings
- **Purpose**: Store user preferences and configurations
- **Content**: User settings, agent configurations, tool preferences
- **Use Cases**: Personalization, quick setup, consistency

### Cache
- **Purpose**: Temporary storage for performance optimization
- **Content**: Frequently accessed data, intermediate results
- **Use Cases**: Faster access, reduced computation, efficiency

## Memory Structure

Memory is organized into entries with the following structure:

```json
{
    "id": "unique-identifier",
    "title": "Entry title",
    "content": "Main content",
    "category": "knowledge|conversations|settings|cache",
    "type": "document|conversation|configuration|cache",
    "tags": ["tag1", "tag2"],
    "metadata": {
        "createdAt": "timestamp",
        "updatedAt": "timestamp",
        "accessCount": 0,
        "lastAccessed": "timestamp"
    }
}
```

## Memory Operations

### Adding to Memory
- Memory is automatically updated during interactions
- You can manually add entries through the Memory section
- Agents can add to memory based on their learning

### Accessing Memory
- Memory is automatically searched when relevant to queries
- You can manually search memory for specific information
- Agents use memory to provide better responses

### Updating Memory
- Memory entries can be updated at any time
- Updates preserve the original creation timestamp
- Version history is maintained for important entries

### Deleting from Memory
- Remove entries that are no longer needed
- Deleting from memory removes all references
- Some system entries cannot be deleted

## Memory Search

Search memory using:

- **Keywords**: Search for specific terms
- **Tags**: Filter by assigned tags
- **Categories**: Filter by memory type
- **Date Range**: Filter by creation or update date

### Advanced Search

Use the following syntax for advanced searches:

- `tag:knowledge` - Find entries with the "knowledge" tag
- `category:conversations` - Find conversation entries
- `before:2024-01-01` - Find entries before a date
- `after:2024-01-01` - Find entries after a date
- `size:>1000` - Find entries larger than 1000 bytes

## Memory Management

### Memory Limits
- Total memory usage is limited by your device storage
- Individual entry size is limited to 10 MB
- Configure memory limits in Settings

### Memory Cleanup
- Regularly review and clean up old entries
- Use the cleanup tool to remove unused entries
- Archive important entries before deletion

### Memory Backup
- Export memory entries for backup
- Import from backups to restore data
- Backup format is JSON for compatibility

## Memory Analytics

View memory usage statistics:

- **Total Entries**: Number of memory entries
- **Total Size**: Combined size of all entries
- **Most Accessed**: Most frequently used entries
- **Recently Updated**: Most recently modified entries

## Best Practices

- Organize memory with descriptive titles and tags
- Regularly review and update memory entries
- Use categories appropriately for different types of data
- Archive or delete old entries to free up space
- Backup important memory entries regularly`
            },
            terminal: {
                title: 'Terminal',
                icon: 'fa-terminal',
                content: `# Terminal Interface

## Overview

The Terminal provides a command-line interface for advanced users to interact with LivingAI. It offers direct access to all system functions with a familiar command-line experience.

## Getting Started

To open the terminal:

1. Navigate to the **Terminal** section
2. Or use the quick action button in the dashboard

## Terminal Features

### Command Execution
- Type commands and press Enter to execute
- View command output in real-time
- Command history is preserved between sessions

### Command History
- Use ↑ and ↓ arrow keys to navigate history
- All executed commands are saved
- History is searchable and filterable

### Auto-Completion
- Press Tab to auto-complete commands
- Shows suggestions for partial commands
- Works for command names and arguments

### Syntax Highlighting
- Commands are color-coded by type
- Errors are highlighted in red
- Output is formatted for readability

## Available Commands

### General Commands

| Command | Description |
|---------|-------------|
| `help` | Show help information |
| `clear`, `cls` | Clear the terminal screen |
| `exit`, `quit` | Exit the terminal |

### Navigation Commands

| Command | Description |
|---------|-------------|
| `ls [path]` | List files and directories |
| `cd [path]` | Change directory |
| `pwd` | Print working directory |
| `cat [file]` | Display file content |

### Text Commands

| Command | Description |
|---------|-------------|
| `echo [text]` | Display text |

### System Commands

| Command | Description |
|---------|-------------|
| `date` | Show current date |
| `time` | Show current time |
| `version`, `-v` | Show LivingAI version |

### LivingAI Commands

| Command | Description |
|---------|-------------|
| `agents` | List all AI agents |
| `tools` | List all available tools |
| `tasks` | List all tasks |
| `memory` | Show memory information |

## Command Reference

### help

Show help information.

**Usage:**
```bash
help [command]
```

**Examples:**
```bash
help
help agents
help tools
```

### clear, cls

Clear the terminal screen.

**Usage:**
```bash
clear
cls
```

### ls

List files and directories.

**Usage:**
```bash
ls [path]
```

**Examples:**
```bash
ls
ls /agents
ls /tools
```

### cd

Change directory.

**Usage:**
```bash
cd [path]
```

**Examples:**
```bash
cd /agents
cd ..
cd /
```

### pwd

Print the current working directory.

**Usage:**
```bash
pwd
```

### cat

Display file content.

**Usage:**
```bash
cat [file]
```

**Examples:**
```bash
cat README.md
cat config.json
```

### echo

Display text.

**Usage:**
```bash
echo [text]
```

**Examples:**
```bash
echo "Hello, World!"
echo This is a test
```

### agents

List all AI agents.

**Usage:**
```bash
agents
```

### tools

List all available tools.

**Usage:**
```bash
tools
```

### tasks

List all tasks.

**Usage:**
```bash
tasks
```

### memory

Show memory information.

**Usage:**
```bash
memory
```

## Terminal Shortcuts

| Shortcut | Description |
|----------|-------------|
| ↑ | Previous command in history |
| ↓ | Next command in history |
| Tab | Auto-complete command |
| Ctrl+C | Cancel current command |
| Ctrl+D | Exit terminal |

## Terminal Settings

Configure terminal behavior in Settings:

- **Font Size**: Adjust text size
- **Color Scheme**: Choose color theme
- **History Size**: Maximum number of commands to remember
- **Auto-Complete**: Enable or disable auto-completion

## Tips and Tricks

1. **Use Tab for Completion**: Saves time and reduces errors
2. **Command History**: Navigate with arrow keys to reuse commands
3. **Help Command**: Use `help` to discover available commands
4. **Command Chaining**: Some commands can be chained with pipes
5. **Clear Screen**: Use `clear` or `cls` to clean up the display

## Troubleshooting

### Command Not Found
- Check spelling with `help`
- Ensure the command is available in your version
- Some commands require specific permissions

### Terminal Not Responding
- Try refreshing the page
- Check for JavaScript errors in the console
- Clear browser cache and try again

### Commands Not Working
- Verify you have the required tools installed
- Check that agents are running
- Review command syntax with `help`

## Advanced Usage

### Scripting

Create scripts by saving commands to files:

```bash
# Create a script file
cat > myscript.sh
# Add commands
agents
tools
tasks
# Save and exit (Ctrl+D)

# Run the script
cat myscript.sh
```

### Piping

Some commands support piping output to other commands:

```bash
# Example: Count agents
agents | wc -l

# Example: Filter tools
tools | grep search
```

### Environment Variables

View and set environment variables:

```bash
# View all variables
env

# Set a variable (temporary)
export MY_VAR=value

# Use a variable
echo $MY_VAR
````
            },
            api: {
                title: 'API Reference',
                icon: 'fa-code',
                content: `# API Reference

## Overview

LivingAI provides a RESTful API for programmatic access to all system functions. The API allows you to integrate LivingAI with other applications, automate workflows, and build custom interfaces.

## Base URL

```
https://api.livingai.local/v1
```

Or for local development:

```
http://localhost:3000/api/v1
```

## Authentication

All API requests must include an authentication token in the `Authorization` header:

```
Authorization: Bearer YOUR_API_TOKEN
```

Get your API token from Settings > API Access.

## API Endpoints

### Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/agents` | List all agents |
| GET | `/agents/{id}` | Get specific agent |
| POST | `/agents` | Create new agent |
| PUT | `/agents/{id}` | Update agent |
| DELETE | `/agents/{id}` | Delete agent |
| POST | `/agents/{id}/start` | Start agent |
| POST | `/agents/{id}/stop` | Stop agent |

### Tools

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tools` | List all tools |
| GET | `/tools/{id}` | Get specific tool |
| POST | `/tools` | Create new tool |
| PUT | `/tools/{id}` | Update tool |
| DELETE | `/tools/{id}` | Delete tool |
| POST | `/tools/{id}/execute` | Execute tool |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List all tasks |
| GET | `/tasks/{id}` | Get specific task |
| POST | `/tasks` | Create new task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| POST | `/tasks/{id}/start` | Start task |
| POST | `/tasks/{id}/cancel` | Cancel task |

### Memory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/memory` | List all memory entries |
| GET | `/memory/{id}` | Get specific entry |
| POST | `/memory` | Create new entry |
| PUT | `/memory/{id}` | Update entry |
| DELETE | `/memory/{id}` | Delete entry |
| GET | `/memory/search` | Search memory |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/system/status` | Get system status |
| GET | `/system/stats` | Get system statistics |
| GET | `/system/health` | Get system health |
| POST | `/system/shutdown` | Shutdown system |
| POST | `/system/restart` | Restart system |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics` | Get analytics overview |
| GET | `/analytics/tools` | Get tool usage analytics |
| GET | `/analytics/tasks` | Get task analytics |
| GET | `/analytics/agents` | Get agent analytics |

## Request Examples

### GET /agents

Get a list of all agents.

**Request:**
```bash
curl -X GET \
  https://api.livingai.local/v1/agents \
  -H 'Authorization: Bearer YOUR_API_TOKEN'
```

**Response:**
```json
{
  "agents": [
    {
      "id": "agent-001",
      "name": "Research Agent",
      "type": "research",
      "status": "active",
      "createdAt": "2024-01-15T10:30:00Z",
      "lastUsed": "2024-01-20T14:25:00Z"
    },
    {
      "id": "agent-002",
      "name": "Development Agent",
      "type": "development",
      "status": "inactive",
      "createdAt": "2024-01-16T11:45:00Z",
      "lastUsed": "2024-01-19T09:15:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "perPage": 50
}
```

### POST /agents

Create a new agent.

**Request:**
```bash
curl -X POST \
  https://api.livingai.local/v1/agents \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Custom Agent",
    "type": "general",
    "description": "My custom agent"
  }'
```

**Response:**
```json
{
  "id": "agent-003",
  "name": "Custom Agent",
  "type": "general",
  "status": "inactive",
  "createdAt": "2024-01-20T16:30:00Z",
  "lastUsed": null
}
```

### POST /tools/{id}/execute

Execute a tool.

**Request:**
```bash
curl -X POST \
  https://api.livingai.local/v1/tools/tool-001/execute \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "input": "Search for AI trends",
    "parameters": {
      "limit": 10
    }
  }'
```

**Response:**
```json
{
  "id": "execution-001",
  "toolId": "tool-001",
  "status": "completed",
  "result": {
    "data": [
      {
        "title": "AI Trends 2024",
        "url": "https://example.com/ai-trends",
        "snippet": "Latest AI developments..."
      }
    ]
  },
  "executionTime": 2.5,
  "createdAt": "2024-01-20T16:35:00Z"
}
```

### POST /tasks

Create a new task.

**Request:**
```bash
curl -X POST \
  https://api.livingai.local/v1/tasks \
  -H 'Authorization: Bearer YOUR_API_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Research AI Trends",
    "description": "Analyze current AI trends",
    "agentId": "agent-001",
    "priority": "high",
    "dueDate": "2024-01-21T18:00:00Z"
  }'
```

**Response:**
```json
{
  "id": "task-003",
  "title": "Research AI Trends",
  "description": "Analyze current AI trends",
  "agentId": "agent-001",
  "priority": "high",
  "status": "pending",
  "createdAt": "2024-01-20T16:40:00Z",
  "dueDate": "2024-01-21T18:00:00Z"
}
```

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Success message",
  "timestamp": "2024-01-20T16:45:00Z"
}
```

For errors:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": { ... }
  },
  "timestamp": "2024-01-20T16:45:00Z"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_ERROR` | Invalid or missing authentication token |
| `VALIDATION_ERROR` | Invalid request data |
| `NOT_FOUND` | Resource not found |
| `UNAUTHORIZED` | Insufficient permissions |
| `RATE_LIMITED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Standard**: 100 requests per minute
- **Premium**: 1000 requests per minute
- **Enterprise**: 10000 requests per minute

Rate limit headers:

- `X-RateLimit-Limit`: Total requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: When the limit resets (timestamp)

## Pagination

List endpoints support pagination:

- `page`: Page number (default: 1)
- `perPage`: Items per page (default: 50, max: 100)

**Example:**
```bash
GET /agents?page=2&perPage=25
```

## Filtering

List endpoints support filtering:

- `filter[field]`: Filter by field value
- `sort[field]`: Sort by field (asc/desc)

**Example:**
```bash
GET /agents?filter[status]=active&sort[name]=asc
```

## WebSocket API

For real-time updates, use WebSocket:

```
wss://api.livingai.local/v1/ws
```

### WebSocket Events

- `agent:status`: Agent status changed
- `task:status`: Task status changed
- `tool:execution`: Tool execution started/completed
- `system:health`: System health update

**Example:**
```javascript
const socket = new WebSocket('wss://api.livingai.local/v1/ws');

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.type, data.payload);
};

socket.send(JSON.stringify({
  type: 'subscribe',
  channels: ['agent:status', 'task:status']
}));
```

## SDKs

Official SDKs are available for popular languages:

- **JavaScript/Node.js**: [@livingai/sdk](https://www.npmjs.com/package/@livingai/sdk)
- **Python**: [livingai-python](https://pypi.org/project/livingai/)
- **Java**: [livingai-java](https://github.com/abdulraheemnohri/livingai-java)
- **Android**: [livingai-android](https://github.com/abdulraheemnohri/livingai-android)

## Best Practices

1. **Use Authentication**: Always include your API token
2. **Handle Errors**: Check for errors in all responses
3. **Rate Limiting**: Respect rate limits and implement retries
4. **Pagination**: Use pagination for large datasets
5. **Caching**: Cache responses when appropriate
6. **Security**: Never expose your API token in client-side code
7. **Logging**: Log API requests and responses for debugging
8. **Updates**: Keep your SDKs and libraries updated`
            },
            development: {
                title: 'Development',
                icon: 'fa-code',
                content: `# Development Guide

## Overview

This guide covers how to contribute to LivingAI development, build from source, and extend the system with custom functionality.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 16+ (for web interface)
- **Python** 3.8+ (for backend)
- **Git** (for version control)
- **Android Studio** (for Android app)
- **Java** 11+ (for Android development)

## Setting Up Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/abdulraheemnohri/LivingAI.git
cd LivingAI
```

### 2. Install Dependencies

#### Backend (Python)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Web Interface

```bash
cd web
npm install
```

#### Android App

```bash
cd android
# Open in Android Studio and let it install dependencies
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```
# Backend Configuration
PORT=3000
DEBUG=true
DATABASE_URL=sqlite:///livingai.db

# API Configuration
API_TOKEN=your-secure-token
RATE_LIMIT=100

# AI Configuration
AI_MODEL=mistral
AI_API_KEY=your-ai-api-key

# Web Configuration
WEB_PORT=8080
WEB_HOST=localhost
```

## Running LivingAI

### Development Mode

Run all components in development mode:

```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Web Interface
cd web
npm run dev

# Terminal 3: Android (in Android Studio)
# Open android/ directory in Android Studio and run
```

### Production Mode

Build and run in production mode:

```bash
# Build web interface
cd web
npm run build

# Run backend in production
python app.py --production
```

## Project Structure

```
LivingAI/
├── android/              # Android application
│   ├── app/             # Android app source
│   ├── gradle/          # Gradle configuration
│   └── ...
├── web/                 # Web interface
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   ├── assets/          # Static assets
│   └── index.html       # Main HTML file
├── backend/             # Python backend
│   ├── agents/          # Agent implementations
│   ├── tools/           # Tool implementations
│   ├── models/          # Data models
│   ├── routes/          # API routes
│   └── app.py           # Main application
├── config/              # Configuration files
├── docs/                # Documentation
├── tests/               # Test files
└── README.md            # Project documentation
```

## Backend Development

### Architecture

The backend follows a modular architecture:

- **API Layer**: FastAPI for RESTful endpoints
- **Service Layer**: Business logic and processing
- **Data Layer**: Database models and queries
- **Integration Layer**: External service connectors

### Key Files

- `app.py`: Main application entry point
- `config.py`: Configuration management
- `database.py`: Database connection and models
- `routes/*.py`: API route handlers
- `services/*.py`: Business logic services
- `models/*.py`: Data models

### Adding a New API Endpoint

1. Create a new route file in `routes/`
2. Define your endpoint with FastAPI decorators
3. Register the route in `app.py`

**Example:**

```python
# routes/new_route.py
from fastapi import APIRouter, HTTPException
from models.new_model import NewModel

router = APIRouter(prefix="/new", tags=["new"])

@router.get("/items")
async def get_items():
    items = await NewModel.all()
    return {"items": items}

@router.post("/items")
async def create_item(item: NewModel):
    new_item = await NewModel.create(**item.dict())
    return {"item": new_item}
```

4. Register in `app.py`:

```python
from routes.new_route import router as new_router

app.include_router(new_router)
```

### Adding a New Agent

1. Create a new agent file in `agents/`
2. Implement the agent class inheriting from `BaseAgent`
3. Register the agent in `agents/__init__.py`

**Example:**

```python
# agents/new_agent.py
from agents.base import BaseAgent
from tools.registry import ToolRegistry

class NewAgent(BaseAgent):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.type = "new"
        self.description = "A new type of agent"
        
    async def execute(self, task):
        # Implement agent execution logic
        result = await self.process(task)
        return result
```

4. Register in `agents/__init__.py`:

```python
from agents.new_agent import NewAgent

AGENT_TYPES = {
    # ... existing agents
    "new": NewAgent,
}
```

### Adding a New Tool

1. Create a new tool file in `tools/`
2. Implement the tool class inheriting from `BaseTool`
3. Register the tool in `tools/__init__.py`

**Example:**

```python
# tools/new_tool.py
from tools.base import BaseTool

class NewTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="new_tool",
            description="A new tool",
            parameters={
                "param1": {"type": "string", "required": True},
                "param2": {"type": "integer", "default": 10}
            }
        )
        
    async def execute(self, param1, param2=10):
        # Implement tool logic
        result = f"Processed {param1} with {param2}"
        return result
```

4. Register in `tools/__init__.py`:

```python
from tools.new_tool import NewTool

TOOL_REGISTRY = {
    # ... existing tools
    "new_tool": NewTool,
}
```

## Web Interface Development

### Architecture

The web interface uses:

- **Vanilla JavaScript**: No framework dependencies
- **CSS Variables**: For theming and styling
- **Modular Structure**: Separate files for each component

### Key Files

- `index.html`: Main HTML structure
- `css/style.css`: Main stylesheet
- `css/dashboard.css`: Dashboard-specific styles
- `css/terminal.css`: Terminal-specific styles
- `js/app.js`: Main application logic
- `js/dashboard.js`: Dashboard functionality
- `js/agents.js`: Agents management
- `js/tools.js`: Tools management
- `js/terminal.js`: Terminal emulator

### Adding a New Page

1. Add a new section in `index.html`
2. Create a new JavaScript file for the page logic
3. Add navigation to the sidebar
4. Initialize the page in `app.js`

**Example:**

```html
<!-- In index.html -->
<div id="new-page" class="page">
    <div class="page-header">
        <h1><i class="fa fa-new"></i> New Page</h1>
    </div>
    <div class="page-content">
        <!-- Page content here -->
    </div>
</div>
```

```javascript
// In js/new_page.js
function initNewPage() {
    console.log('Initializing New Page...');
    // Initialize page functionality
}

// In app.js
// Add to loadPageData function:
case 'new-page':
    if (typeof initNewPage === 'function') initNewPage();
    break;
```

## Android Development

### Project Structure

```
android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/livingai/
│   │   │   │   ├── activities/
│   │   │   │   ├── adapters/
│   │   │   │   ├── models/
│   │   │   │   ├── services/
│   │   │   │   └── utils/
│   │   │   └── res/
│   │   │       ├── layout/
│   │   │       ├── drawable/
│   │   │       └── values/
│   │   └── test/
│   └── build.gradle
├── gradle/
│   └── wrapper/
└── settings.gradle
```

### Key Components

- **MainActivity**: Primary activity for the app
- **AgentActivity**: Agent management interface
- **ToolActivity**: Tool selection and execution
- **TaskActivity**: Task creation and management
- **TerminalActivity**: Terminal interface

### Adding a New Activity

1. Create a new activity class
2. Create a layout file
3. Register in `AndroidManifest.xml`
4. Add navigation to the activity

**Example:**

```java
// NewActivity.java
package com.livingai;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;

public class NewActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_new);
        
        // Initialize activity
        initNewActivity();
    }
    
    private void initNewActivity() {
        // Activity initialization
    }
}
```

```xml
<!-- res/layout/activity_new.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">
    
    <!-- Layout content here -->
    
</LinearLayout>
```

```xml
<!-- AndroidManifest.xml -->
<activity android:name=".NewActivity" />
```

## Testing

### Backend Testing

Run tests for the Python backend:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=backend
```

### Web Interface Testing

Test the web interface manually or with automated tests:

```bash
# Run web tests
cd web
npm test

# Manual testing
npm run dev
# Open http://localhost:8080 in browser
```

### Android Testing

Run tests in Android Studio:

1. Open the android/ directory in Android Studio
2. Run unit tests: Right-click on test file > Run
3. Run instrumented tests: Run > Run 'All Tests'

## Debugging

### Backend Debugging

```bash
# Run with debug mode
python app.py --debug

# Or use debugger
python -m pdb app.py
```

### Web Interface Debugging

```bash
# Run with source maps
npm run dev

# Use browser dev tools
# Chrome: F12 or Ctrl+Shift+I
# Firefox: F12 or Ctrl+Shift+K
```

### Android Debugging

1. Connect device or use emulator
2. Run app in debug mode in Android Studio
3. Set breakpoints in code
4. Use Logcat for logging

## Contributing

We welcome contributions to LivingAI! Here's how to contribute:

### Reporting Issues

1. Check if the issue already exists in the [issue tracker](https://github.com/abdulraheemnohri/LivingAI/issues)
2. Create a new issue with:
   - Clear title
   - Detailed description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment information

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest` and `npm test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

Follow these code style guidelines:

- **Python**: PEP 8 style guide
- **JavaScript**: Standard JavaScript style
- **Java**: Google Java Style Guide
- **Commit Messages**: Conventional commits format

### Review Process

All pull requests will be reviewed by maintainers:

1. Code quality and style
2. Functionality and correctness
3. Documentation
4. Tests
5. Performance

## Versioning

LivingAI uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## License

LivingAI is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Community

Join the LivingAI community:

- **GitHub**: [abdulraheemnohari/LivingAI](https://github.com/abdulraheemnohri/LivingAI)
- **Discord**: Join our Discord server
- **Twitter**: Follow @LivingAI for updates
- **Email**: contact@livingai.dev

## Support

For support and questions:

1. Check the [documentation](https://github.com/abdulraheemnohri/LivingAI/docs)
2. Search the [issue tracker](https://github.com/abdulraheemnohri/LivingAI/issues)
3. Ask in the [Discord server](https://discord.gg/livingai)
4. Open a new issue for bugs or feature requests

## Roadmap

Check out our [roadmap](https://github.com/abdulraheemnohri/LivingAI/projects) for upcoming features and improvements.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.`
            }
        }
    };
}

// ============================================
// NAVIGATION
// ============================================

function initNavigation() {
    const navItems = document.querySelectorAll('.doc-nav a');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            if (section) {
                loadSection(section);
            }
        });
    });
}

function loadSection(section) {
    currentSection = section;
    
    // Update active nav item
    const navItems = document.querySelectorAll('.doc-nav a');
    navItems.forEach(item => {
        if (item.dataset.section === section) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    // Render section
    renderSection();
    
    // Scroll to top
    const docContainer = document.getElementById('documentation-container');
    if (docContainer) {
        docContainer.scrollTop = 0;
    }
}

function renderSection() {
    const docContainer = document.getElementById('documentation-container');
    if (!docContainer) return;
    
    const section = documentation.sections[currentSection];
    if (!section) return;
    
    // Render markdown content
    const content = renderMarkdown(section.content);
    
    docContainer.innerHTML = `
        <div class="doc-header">
            <h1><i class="fa ${section.icon}"></i> ${section.title}</h1>
            <p>${documentation.description}</p>
        </div>
        <div class="doc-content">
            ${content}
        </div>
    `;
    
    // Apply syntax highlighting
    applySyntaxHighlighting();
}

// ============================================
// MARKDOWN RENDERING
// ============================================

function renderMarkdown(markdown) {
    // Convert markdown to HTML
    // This is a simple implementation; consider using a library like marked for production
    
    // Headers
    let html = markdown
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^#### (.*$)/gm, '<h4>$1</h4>')
        .replace(/^##### (.*$)/gm, '<h5>$1</h5>')
        .replace(/^###### (.*$)/gm, '<h6>$1</h6>')
        
        // Bold and Italic
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        
        // Links
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
        
        // Images
        .replace(/!\\[(.*?)\\]\((.*?)\)/g, '<img src="$2" alt="$1">')
        
        // Lists
        .replace(/^\- (.*$)/gm, '<li>$1</li>')
        .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
        
        // Code blocks
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        
        // Tables
        .replace(/\|(.*?)\|/g, (match) => {
            return match.replace(/\|/g, '</td><td>');
        })
        .replace(/^\|.*\|$/gm, (match) => {
            return `<table><tr><td>${match.substring(1, match.length - 1).replace(/\|/g, '</td><td>')}</td></tr></table>`;
        })
        
        // Horizontal rules
        .replace(/^---$/gm, '<hr>')
        .replace(/^\*\*\*$/gm, '<hr>')
        .replace(/^___$/gm, '<hr>')
        
        // Blockquotes
        .replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>')
        
        // HTML entities
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // Wrap lists in ul/ol
    html = html.replace(/<li>(.*?)<\/li>/gs, (match) => {
        if (!match.includes('<ul>') && !match.includes('<ol>')) {
            return `<ul>${match}</ul>`;
        }
        return match;
    });
    
    return html;
}

// ============================================
// SEARCH
// ============================================

function initSearch() {
    const searchInput = document.getElementById('doc-search');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', (e) => {
        searchDocumentation(e.target.value);
    });
}

function buildSearchIndex() {
    searchIndex = [];
    
    Object.entries(documentation.sections).forEach(([sectionId, section]) => {
        // Add section title
        searchIndex.push({
            type: 'section',
            id: sectionId,
            title: section.title,
            content: section.content,
            weight: 10
        });
        
        // Add content (split into paragraphs)
        const paragraphs = section.content.split('\n\n');
        paragraphs.forEach((paragraph, index) => {
            if (paragraph.trim()) {
                searchIndex.push({
                    type: 'paragraph',
                    sectionId: sectionId,
                    content: paragraph,
                    weight: 5
                });
            }
        });
    });
}

function searchDocumentation(query) {
    if (!query) {
        renderSection();
        return;
    }
    
    const results = searchIndex
        .map(item => ({
            ...item,
            score: calculateScore(item, query)
        }))
        .filter(item => item.score > 0)
        .sort((a, b) => b.score - a.score);
    
    displaySearchResults(results, query);
}

function calculateScore(item, query) {
    const queryLower = query.toLowerCase();
    const contentLower = (item.title || item.content || '').toLowerCase();
    
    // Count occurrences
    const occurrences = (contentLower.match(new RegExp(queryLower, 'g')) || []).length;
    
    // Weight by type
    const typeWeight = item.type === 'section' ? 2 : 1;
    
    // Weight by position (earlier matches score higher)
    const positionWeight = 1 - (contentLower.indexOf(queryLower) / contentLower.length);
    
    return occurrences * item.weight * typeWeight * positionWeight;
}

function displaySearchResults(results, query) {
    const docContainer = document.getElementById('documentation-container');
    if (!docContainer) return;
    
    if (results.length === 0) {
        docContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa fa-search"></i>
                <p>No results found for "${query}"</p>
            </div>
        `;
        return;
    }
    
    const resultsHTML = results.map(result => {
        if (result.type === 'section') {
            return `
                <div class="search-result" onclick="loadSection('${result.id}')">
                    <h3><i class="fa fa-file-text"></i> ${highlightText(result.title, query)}</h3>
                    <p>${truncateText(highlightText(result.content, query), 200)}</p>
                    <span class="result-type">Section</span>
                </div>
            `;
        } else {
            return `
                <div class="search-result" onclick="loadSection('${result.sectionId}')">
                    <p>${highlightText(truncateText(result.content, 200), query)}</p>
                    <span class="result-type">In: ${documentation.sections[result.sectionId].title}</span>
                </div>
            `;
        }
    }).join('');
    
    docContainer.innerHTML = `
        <div class="search-results-header">
            <h2>Search Results for "${query}"</h2>
            <p>${results.length} results found</p>
        </div>
        <div class="search-results">
            ${resultsHTML}
        </div>
    `;
}

function highlightText(text, query) {
    if (!query) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

function truncateText(text, length) {
    if (text.length <= length) return text;
    
    // Find the last space before the limit
    const lastSpace = text.lastIndexOf(' ', length);
    
    if (lastSpace > 0) {
        return text.substring(0, lastSpace) + '...';
    }
    
    return text.substring(0, length) + '...';
}

// ============================================
// SYNTAX HIGHLIGHTING
// ============================================

function applySyntaxHighlighting() {
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const language = block.className.match(/language-(\w+)/)?.[1] || 'text';
        highlightCode(block, language);
    });
}

function highlightCode(element, language) {
    const code = element.textContent;
    
    // Simple syntax highlighting based on language
    let highlighted = code;
    
    switch (language) {
        case 'javascript':
        case 'js':
            highlighted = highlightJavaScript(code);
            break;
        case 'python':
        case 'py':
            highlighted = highlightPython(code);
            break;
        case 'java':
            highlighted = highlightJava(code);
            break;
        case 'bash':
        case 'sh':
            highlighted = highlightBash(code);
            break;
        case 'json':
            highlighted = highlightJson(code);
            break;
        case 'xml':
        case 'html':
            highlighted = highlightXml(code);
            break;
        default:
            highlighted = escapeHtml(code);
    }
    
    element.innerHTML = highlighted;
}

function highlightJavaScript(code) {
    return escapeHtml(code)
        .replace(/(\bfunction\b|\bconst\b|\blet\b|\bvar\b|\bif\b|\belse\b|\bfor\b|\bwhile\b|\breturn\b|\bclass\b|\bimport\b|\bexport\b)/g, '<span class="keyword">$1</span>')
        .replace(/(\btrue\b|\bfalse\b|\bnull\b|\bundefined\b)/g, '<span class="boolean">$1</span>')
        .replace(/(\b\d+\b)/g, '<span class="number">$1</span>')
        .replace(/("[^"]*"|'[^']*')/g, '<span class="string">$1</span>')
        .replace(/(\/\/[^\/]+\/)/g, '<span class="regex">$1</span>')
        .replace(/(\bnew\b\s+\w+)/g, '<span class="keyword">$1</span>');
}

function highlightPython(code) {
    return escapeHtml(code)
        .replace(/(\bdef\b|\bclass\b|\bif\b|\belse\b|\belif\b|\bfor\b|\bwhile\b|\bimport\b|\bfrom\b|\bas\b|\breturn\b|\btry\b|\bexcept\b|\bfinally\b)/g, '<span class="keyword">$1</span>')
        .replace(/(\bTrue\b|\bFalse\b|\bNone\b)/g, '<span class="boolean">$1</span>')
        .replace(/(\b\d+\b)/g, '<span class="number">$1</span>')
        .replace(/("""[^"""]*"""|"[^"]*"|'[^']*')/g, '<span class="string">$1</span>')
        .replace(/(\bself\b)/g, '<span class="keyword">$1</span>');
}

function highlightJava(code) {
    return escapeHtml(code)
        .replace(/(\bpublic\b|\bprivate\b|\bprotected\b|\bstatic\b|\bfinal\b|\bclass\b|\binterface\b|\bimport\b|\bpackage\b|\bif\b|\belse\b|\bfor\b|\bwhile\b|\breturn\b|\bnew\b|\bvoid\b|\btry\b|\bcatch\b|\bfinally\b)/g, '<span class="keyword">$1</span>')
        .replace(/(\btrue\b|\bfalse\b|\bnull\b)/g, '<span class="boolean">$1</span>')
        .replace(/(\b\d+\b)/g, '<span class="number">$1</span>')
        .replace(/("[^"]*"|'[^']*')/g, '<span class="string">$1</span>');
}

function highlightBash(code) {
    return escapeHtml(code)
        .replace(/(\bcd\b|\bls\b|\bcat\b|\bgrep\b|\bfind\b|\becho\b|\bexport\b|\bif\b|\bthen\b|\belse\b|\bfi\b|\bfor\b|\bwhile\b|\bdo\b|\bdone\b)/g, '<span class="command">$1</span>')
        .replace(/(\$\w+)/g, '<span class="variable">$1</span>')
        .replace(/(\-[a-zA-Z]+|\-\-[a-zA-Z]+)/g, '<span class="option">$1</span>');
}

function highlightJson(code) {
    try {
        const json = JSON.parse(code);
        return `<pre>${JSON.stringify(json, null, 2)}</pre>`;
    } catch {
        return escapeHtml(code);
    }
}

function highlightXml(code) {
    return escapeHtml(code)
        .replace(/(&lt;[^&]+&gt;)/g, '<span class="tag">$1</span>')
        .replace(/(\w+="[^"]*")/g, '<span class="attribute">$1</span>');
}

function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function showError(message) {
    if (window.livingAIApp) {
        window.livingAIApp.addNotification('Error', message, 'error');
    } else {
        console.error(message);
    }
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

window.initDocumentation = initDocumentation;
window.loadSection = loadSection;
window.searchDocumentation = searchDocumentation;
