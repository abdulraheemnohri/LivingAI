package com.livingai.app.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.livingai.app.models.TerminalCommand
import com.livingai.app.models.TerminalSession

/**
 * TerminalViewModel - ViewModel for managing terminal commands and sessions
 */
class TerminalViewModel : ViewModel() {

    private val _commands = MutableLiveData<List<TerminalCommand>>()
    val commands: LiveData<List<TerminalCommand>> = _commands

    private val _currentSession = MutableLiveData<TerminalSession?>()
    val currentSession: LiveData<TerminalSession?> = _currentSession

    private val _commandHistory = MutableLiveData<List<TerminalCommand>>()
    val commandHistory: LiveData<List<TerminalCommand>> = _commandHistory

    // Mock data
    private val mockHistory = mutableListOf(
        TerminalCommand(
            id = "1",
            command = "ls -la",
            timestamp = System.currentTimeMillis() - 3600000,
            output = "total 24\ndrwxr-xr-x  5 user user 4096 Jan 15 10:00 Documents\n-rw-r--r--  1 user user 1024 Jan 15 09:55 file.txt",
            isSuccess = true,
            error = null,
            executionTime = 15,
            workingDirectory = "/home/user",
            sessionId = "session_1"
        ),
        TerminalCommand(
            id = "2",
            command = "cd Documents",
            timestamp = System.currentTimeMillis() - 1800000,
            output = "",
            isSuccess = true,
            error = null,
            executionTime = 5,
            workingDirectory = "/home/user/Documents",
            sessionId = "session_1"
        ),
        TerminalCommand(
            id = "3",
            command = "cat file.txt",
            timestamp = System.currentTimeMillis() - 900000,
            output = "This is a sample text file content.",
            isSuccess = true,
            error = null,
            executionTime = 10,
            workingDirectory = "/home/user/Documents",
            sessionId = "session_1"
        ),
        TerminalCommand(
            id = "4",
            command = "python script.py",
            timestamp = System.currentTimeMillis() - 300000,
            output = "Hello, World!",
            isSuccess = true,
            error = null,
            executionTime = 25,
            workingDirectory = "/home/user/Documents",
            sessionId = "session_1"
        ),
        TerminalCommand(
            id = "5",
            command = "invalid_command",
            timestamp = System.currentTimeMillis() - 60000,
            output = "",
            isSuccess = false,
            error = "bash: invalid_command: command not found",
            executionTime = 2,
            workingDirectory = "/home/user/Documents",
            sessionId = "session_1"
        )
    )

    init {
        _commandHistory.value = mockHistory
        _commands.value = mockHistory
    }

    /**
     * Get command history
     */
    fun getCommandHistory(): List<TerminalCommand> {
        return mockHistory
    }

    /**
     * Execute a command
     */
    fun executeCommand(command: String, callback: (TerminalCommand) -> Unit) {
        // Simulate command execution
        val newCommand = TerminalCommand(
            id = System.currentTimeMillis().toString(),
            command = command,
            timestamp = System.currentTimeMillis(),
            output = "",
            isSuccess = true,
            error = null,
            executionTime = 0,
            workingDirectory = "/home/user",
            sessionId = "current"
        )

        // Simulate execution delay
        android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
            val result = if (command.contains("error") || command.contains("invalid")) {
                newCommand.copy(
                    isSuccess = false,
                    error = "Command failed: $command",
                    executionTime = 5
                )
            } else {
                newCommand.copy(
                    output = "Command executed successfully: $command",
                    isSuccess = true,
                    executionTime = 10
                )
            }

            // Add to history
            mockHistory.add(result)
            _commandHistory.value = mockHistory
            _commands.value = mockHistory

            // Call callback
            callback(result)
        }, 500)
    }

    /**
     * Add command to history
     */
    fun addCommandToHistory(command: TerminalCommand) {
        mockHistory.add(command)
        _commandHistory.value = mockHistory
        _commands.value = mockHistory
    }

    /**
     * Clear terminal
     */
    fun clearTerminal() {
        mockHistory.clear()
        _commands.value = mockHistory
    }

    /**
     * Start new session
     */
    fun newSession() {
        // Implementation for new session
    }

    /**
     * Save current session
     */
    fun saveSession() {
        // Implementation for saving session
    }

    /**
     * Load session
     */
    fun loadSession(sessionId: String) {
        // Implementation for loading session
    }

    /**
     * Get current session
     */
    fun getCurrentSession(): TerminalSession? {
        return _currentSession.value
    }

    /**
     * Refresh command history
     */
    fun refresh() {
        _commands.value = mockHistory
        _commandHistory.value = mockHistory
    }
}
