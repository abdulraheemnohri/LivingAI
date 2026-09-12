/**
 * LivingAI - Terminal Emulator JavaScript
 * =====================================
 * Terminal emulator with command execution, history, and syntax highlighting
 */

// ============================================
// TERMINAL INITIALIZATION
// ============================================

let commandHistory = [];
let historyIndex = -1;
let currentCommand = '';

function initTerminal() {
    console.log('Initializing Terminal Module...');
    
    // Initialize terminal
    initTerminalUI();
    
    // Load command history
    loadCommandHistory();
    
    // Initialize event listeners
    initEventListeners();
    
    // Print welcome message
    printWelcomeMessage();
    
    // Focus on input
    focusTerminalInput();
    
    console.log('Terminal Module Initialized');
}

// ============================================
// TERMINAL UI INITIALIZATION
// ============================================

function initTerminalUI() {
    const terminal = document.getElementById('terminal');
    if (!terminal) return;
    
    // Clear existing content
    terminal.innerHTML = '';
    
    // Create terminal output area
    const terminalOutput = document.createElement('div');
    terminalOutput.className = 'terminal-output';
    terminalOutput.id = 'terminal-output';
    
    // Create terminal input area
    const terminalInputContainer = document.createElement('div');
    terminalInputContainer.className = 'terminal-input-container';
    
    const terminalPrompt = document.createElement('span');
    terminalPrompt.className = 'terminal-prompt';
    terminalPrompt.textContent = 'livingai@terminal:~$ ';
    
    const terminalInput = document.createElement('input');
    terminalInput.className = 'terminal-input';
    terminalInput.id = 'terminal-input';
    terminalInput.type = 'text';
    terminalInput.autocomplete = 'off';
    terminalInput.spellcheck = 'false';
    terminalInput.placeholder = 'Type a command...';
    
    terminalInputContainer.appendChild(terminalPrompt);
    terminalInputContainer.appendChild(terminalInput);
    
    terminal.appendChild(terminalOutput);
    terminal.appendChild(terminalInputContainer);
    
    // Store references
    terminal.dataset.terminalOutputId = 'terminal-output';
    terminal.dataset.terminalInputId = 'terminal-input';
}

function focusTerminalInput() {
    const input = document.getElementById('terminal-input');
    if (input) {
        input.focus();
    }
}

// ============================================
// COMMAND HISTORY
// ============================================

function loadCommandHistory() {
    commandHistory = JSON.parse(localStorage.getItem('livingai-command-history') || '[]');
}

function saveCommandHistory() {
    localStorage.setItem('livingai-command-history', JSON.stringify(commandHistory));
}

function addToHistory(command) {
    if (!command || command.trim() === '') return;
    
    // Add to beginning of history
    commandHistory.unshift(command);
    
    // Keep only last 100 commands
    if (commandHistory.length > 100) {
        commandHistory = commandHistory.slice(0, 100);
    }
    
    saveCommandHistory();
}

// ============================================
// WELCOME MESSAGE
// ============================================

function printWelcomeMessage() {
    const output = document.getElementById('terminal-output');
    if (!output) return;
    
    const welcomeMessage = `
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ██╗     ██╗██████╗ ██████╗ ███╗   ██╗██╗███████╗                               │
│   ██║     ██║██╔══██╗██╔══██╗████╗  ██║██║██╔════╝                               │
│   ██║     ██║██████╔╝██████╔╝██╔██╗ ██║██║███████╗                               │
│   ██║     ██║██╔══██╗██╔══██╗██║╚██╗██║██║╚════██║                               │
│   ███████╗██║██║  ██║██║  ██║██║ ╚████║██║███████║                               │
│   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝                               │
│                                                                             │
│   LivingAI - Local AI Operating System                                    │
│   Type 'help' for available commands                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

`;
    
    printToTerminal(welcomeMessage, 'welcome');
}

// ============================================
// EVENT LISTENERS
// ============================================

function initEventListeners() {
    const input = document.getElementById('terminal-input');
    if (!input) return;
    
    // Command submission
    input.addEventListener('keydown', (e) => {
        switch (e.key) {
            case 'Enter':
                e.preventDefault();
                executeCommand(input.value);
                input.value = '';
                break;
            case 'ArrowUp':
                e.preventDefault();
                navigateHistory(-1, input);
                break;
            case 'ArrowDown':
                e.preventDefault();
                navigateHistory(1, input);
                break;
            case 'Tab':
                e.preventDefault();
                autoComplete(input);
                break;
        }
    });
    
    // Click to focus
    const terminal = document.getElementById('terminal');
    if (terminal) {
        terminal.addEventListener('click', () => {
            input.focus();
        });
    }
}

function navigateHistory(direction, input) {
    if (commandHistory.length === 0) return;
    
    if (direction === -1) {
        // Up arrow - go back in history
        if (historyIndex < commandHistory.length - 1) {
            historyIndex++;
            if (historyIndex === 0) {
                currentCommand = input.value;
            }
            input.value = commandHistory[historyIndex];
        }
    } else {
        // Down arrow - go forward in history
        if (historyIndex > 0) {
            historyIndex--;
            input.value = historyIndex === 0 ? currentCommand : commandHistory[historyIndex];
        } else if (historyIndex === 0) {
            historyIndex = -1;
            input.value = '';
        }
    }
}

function autoComplete(input) {
    const value = input.value;
    const commands = getAvailableCommands();
    
    // Find matching commands
    const matches = commands.filter(cmd => cmd.startsWith(value));
    
    if (matches.length === 1) {
        input.value = matches[0] + ' ';
    } else if (matches.length > 1) {
        // Show suggestions
        printToTerminal(`\nPossible commands: ${matches.join(', ')}`, 'info');
        printPrompt();
    }
}

// ============================================
// COMMAND EXECUTION
// ============================================

function executeCommand(command) {
    const input = document.getElementById('terminal-input');
    const output = document.getElementById('terminal-output');
    
    if (!input || !output) return;
    
    // Clear current command display
    currentCommand = '';
    historyIndex = -1;
    
    // Add to history
    addToHistory(command);
    
    // Print command
    printToTerminal(`livingai@terminal:~$ ${command}`, 'command');
    
    // Parse and execute
    const trimmedCommand = command.trim();
    if (trimmedCommand) {
        processCommand(trimmedCommand);
    }
    
    // Print prompt
    printPrompt();
    
    // Focus back on input
    input.focus();
}

function printPrompt() {
    const output = document.getElementById('terminal-output');
    if (output) {
        const prompt = document.createElement('div');
        prompt.className = 'terminal-line prompt';
        prompt.innerHTML = '<span class="terminal-prompt">livingai@terminal:~$ </span>';
        output.appendChild(prompt);
    }
}

function printToTerminal(text, type = 'default') {
    const output = document.getElementById('terminal-output');
    if (!output) return;
    
    const lines = text.split('\n');
    lines.forEach((line, index) => {
        if (line.trim() === '') {
            // Empty line
            const emptyLine = document.createElement('div');
            emptyLine.className = 'terminal-line';
            output.appendChild(emptyLine);
        } else {
            const lineElement = document.createElement('div');
            lineElement.className = `terminal-line ${type}`;
            lineElement.textContent = line;
            output.appendChild(lineElement);
        }
    });
    
    // Scroll to bottom
    output.scrollTop = output.scrollHeight;
}

// ============================================
// COMMAND PROCESSING
// ============================================

function processCommand(command) {
    const parts = command.split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);
    
    switch (cmd) {
        case 'help':
            showHelp(args);
            break;
        case 'clear':
        case 'cls':
            clearTerminal();
            break;
        case 'ls':
            listFiles(args);
            break;
        case 'cd':
            changeDirectory(args);
            break;
        case 'pwd':
            printWorkingDirectory();
            break;
        case 'cat':
            catFile(args);
            break;
        case 'echo':
            echoText(args);
            break;
        case 'date':
            showDate();
            break;
        case 'time':
            showTime();
            break;
        case 'agents':
            listAgents();
            break;
        case 'tools':
            listTools();
            break;
        case 'tasks':
            listTasks();
            break;
        case 'memory':
            showMemoryInfo();
            break;
        case 'version':
        case '--version':
        case '-v':
            showVersion();
            break;
        case 'exit':
        case 'quit':
            exitTerminal();
            break;
        case '':
            // Empty command
            break;
        default:
            printToTerminal(`Command not found: ${cmd}`, 'error');
            printToTerminal('Type "help" for available commands.', 'info');
    }
}

function getAvailableCommands() {
    return [
        'help', 'clear', 'cls', 'ls', 'cd', 'pwd', 'cat', 'echo',
        'date', 'time', 'agents', 'tools', 'tasks', 'memory',
        'version', '--version', '-v', 'exit', 'quit'
    ];
}

// ============================================
// COMMAND IMPLEMENTATIONS
// ============================================

function showHelp(args) {
    const helpText = `
Available commands:

  General:
    help [command]    Show help for commands
    clear, cls        Clear the terminal
    exit, quit        Exit the terminal

  Navigation:
    ls [path]         List files and directories
    cd [path]         Change directory
    pwd               Print working directory
    cat [file]        Display file content

  Text:
    echo [text]       Display text

  System:
    date              Show current date
    time              Show current time
    version, -v       Show LivingAI version

  LivingAI:
    agents            List all AI agents
    tools             List all available tools
    tasks             List all tasks
    memory            Show memory information

Type 'help <command>' for detailed information about a specific command.
`;
    
    if (args.length > 0) {
        showCommandHelp(args[0]);
    } else {
        printToTerminal(helpText, 'help');
    }
}

function showCommandHelp(command) {
    const helpMessages = {
        help: 'Usage: help [command]\n\nShow help for all commands or a specific command.',
        clear: 'Usage: clear, cls\n\nClear the terminal screen.',
        ls: 'Usage: ls [path]\n\nList files and directories in the specified path or current directory.',
        cd: 'Usage: cd [path]\n\nChange the current working directory.',
        pwd: 'Usage: pwd\n\nPrint the current working directory.',
        cat: 'Usage: cat [file]\n\nDisplay the content of a file.',
        echo: 'Usage: echo [text]\n\nDisplay the specified text.',
        date: 'Usage: date\n\nShow the current date.',
        time: 'Usage: time\n\nShow the current time.',
        agents: 'Usage: agents\n\nList all available AI agents with their status.',
        tools: 'Usage: tools\n\nList all available tools with their descriptions.',
        tasks: 'Usage: tasks\n\nList all tasks with their status.',
        memory: 'Usage: memory\n\nShow memory usage and statistics.',
        version: 'Usage: version, --version, -v\n\nShow LivingAI version information.'
    };
    
    const message = helpMessages[command.toLowerCase()] || `No help available for command: ${command}`;
    printToTerminal(message, 'help');
}

function clearTerminal() {
    const output = document.getElementById('terminal-output');
    if (output) {
        output.innerHTML = '';
    }
    printWelcomeMessage();
}

function listFiles(args) {
    const path = args[0] || '.';
    
    // Simulate file listing
    const files = [
        { name: 'agents', type: 'directory', size: '10 KB' },
        { name: 'tools', type: 'directory', size: '15 KB' },
        { name: 'tasks', type: 'directory', size: '8 KB' },
        { name: 'memory', type: 'directory', size: '12 KB' },
        { name: 'config.json', type: 'file', size: '2 KB' },
        { name: 'README.md', type: 'file', size: '4 KB' }
    ];
    
    let output = `Contents of ${path}:\n\n`;
    
    files.forEach(file => {
        const icon = file.type === 'directory' ? '📁' : '📄';
        output += `${icon}  ${file.name.padEnd(20)} ${file.size}\n`;
    });
    
    output += `\n${files.length} items total`;
    
    printToTerminal(output, 'output');
}

function changeDirectory(args) {
    const path = args[0] || '~';
    printToTerminal(`Changed directory to: ${path}`, 'output');
}

function printWorkingDirectory() {
    printToTerminal('/home/user/livingai', 'output');
}

function catFile(args) {
    const fileName = args[0];
    
    if (!fileName) {
        printToTerminal('Usage: cat [file]', 'error');
        return;
    }
    
    // Simulate file content
    const fileContents = {
        'config.json': JSON.stringify({
            version: '1.0.0',
            name: 'LivingAI',
            description: 'Local AI Operating System'
        }, null, 2),
        'README.md': `# LivingAI

Local AI Operating System for Android Terminal.

## Features

- AI Agent Management
- Tool Integration
- Task Automation
- Memory System

## Usage

Run commands in the terminal to interact with LivingAI.`
    };
    
    if (fileContents[fileName]) {
        printToTerminal(fileContents[fileName], 'output');
    } else {
        printToTerminal(`File not found: ${fileName}`, 'error');
    }
}

function echoText(args) {
    const text = args.join(' ');
    printToTerminal(text, 'output');
}

function showDate() {
    const date = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    printToTerminal(date.toLocaleDateString('en-US', options), 'output');
}

function showTime() {
    const date = new Date();
    const options = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    printToTerminal(date.toLocaleTimeString('en-US', options), 'output');
}

function listAgents() {
    // Get agents from the agents module
    const agents = window.agents || [];
    
    if (agents.length === 0) {
        printToTerminal('No agents found. Create agents in the Agents section.', 'info');
        return;
    }
    
    let output = 'Available AI Agents:\n\n';
    
    agents.forEach(agent => {
        const status = agent.status === 'active' ? '🟢 Active' : '🔴 Inactive';
        output += `  • ${agent.name.padEnd(20)} ${status.padEnd(15)} ${agent.type}\n`;
    });
    
    output += `\nTotal: ${agents.length} agents`;
    
    printToTerminal(output, 'output');
}

function listTools() {
    // Get tools from the tools module
    const tools = window.tools || [];
    
    if (tools.length === 0) {
        printToTerminal('No tools found.', 'info');
        return;
    }
    
    let output = 'Available Tools:\n\n';
    
    tools.forEach(tool => {
        const status = tool.isEnabled ? '✓' : '✗';
        output += `  ${status} ${tool.name.padEnd(20)} ${tool.description}\n`;
    });
    
    output += `\nTotal: ${tools.length} tools`;
    
    printToTerminal(output, 'output');
}

function listTasks() {
    // Simulate task listing
    const tasks = [
        { id: 1, name: 'Data Analysis', status: 'completed', agent: 'Analysis Agent' },
        { id: 2, name: 'Web Research', status: 'in-progress', agent: 'Research Agent' },
        { id: 3, name: 'Code Generation', status: 'pending', agent: 'Development Agent' }
    ];
    
    let output = 'Recent Tasks:\n\n';
    
    tasks.forEach(task => {
        const status = task.status === 'completed' ? '✓' : 
                       task.status === 'in-progress' ? '⏳' : '⏸️';
        output += `  ${status} ${task.name.padEnd(25)} ${task.agent}\n`;
    });
    
    output += `\nTotal: ${tasks.length} tasks`;
    
    printToTerminal(output, 'output');
}

function showMemoryInfo() {
    // Simulate memory info
    const memoryInfo = {
        totalEntries: 843,
        usedSpace: '12.5 MB',
        availableSpace: '87.5 MB',
        categories: ['Knowledge', 'Conversations', 'Settings', 'Cache']
    };
    
    let output = 'Memory Information:\n\n';
    output += `  Total Entries: ${memoryInfo.totalEntries}\n`;
    output += `  Used Space: ${memoryInfo.usedSpace}\n`;
    output += `  Available Space: ${memoryInfo.availableSpace}\n`;
    output += `\nCategories:\n`;
    memoryInfo.categories.forEach(cat => {
        output += `  - ${cat}\n`;
    });
    
    printToTerminal(output, 'output');
}

function showVersion() {
    printToTerminal('LivingAI v1.0.0', 'output');
    printToTerminal('Local AI Operating System for Android Terminal', 'output');
    printToTerminal('Build: 2024-01-20', 'output');
}

function exitTerminal() {
    printToTerminal('Goodbye!', 'output');
    
    // Navigate back to dashboard
    setTimeout(() => {
        if (window.livingAIApp) {
            window.livingAIApp.navigateTo('dashboard');
        }
    }, 500);
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

window.initTerminal = initTerminal;
window.executeCommand = executeCommand;
window.printToTerminal = printToTerminal;
