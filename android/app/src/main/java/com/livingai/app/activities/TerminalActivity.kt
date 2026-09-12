package com.livingai.app.activities

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.inputmethod.EditorInfo
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.adapters.TerminalAdapter
import com.livingai.app.models.TerminalCommand
import com.livingai.app.utils.Constants
import com.livingai.app.viewmodels.TerminalViewModel

/**
 * TerminalActivity - Provides a terminal interface for executing commands
 */
class TerminalActivity : AppCompatActivity(), TextView.OnEditorActionListener {

    private lateinit var viewModel: TerminalViewModel
    private lateinit var terminalRecyclerView: RecyclerView
    private lateinit var inputEditText: EditText
    private lateinit var terminalAdapter: TerminalAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_terminal)

        // Initialize ViewModel
        viewModel = TerminalViewModel()

        // Initialize views
        initializeViews()

        // Setup RecyclerView
        setupRecyclerView()

        // Setup input
        setupInput()

        // Load history
        loadHistory()
    }

    /**
     * Initialize all views
     */
    private fun initializeViews() {
        terminalRecyclerView = findViewById(R.id.recycler_terminal)
        inputEditText = findViewById(R.id.et_terminal_input)
    }

    /**
     * Setup RecyclerView
     */
    private fun setupRecyclerView() {
        terminalRecyclerView.layoutManager = LinearLayoutManager(this).apply {
            stackFromEnd = true
        }
        terminalAdapter = TerminalAdapter(
            mutableListOf(),
            onCommandClick = { command ->
                // Re-run the command
                executeCommand(command.command)
            }
        )
        terminalRecyclerView.adapter = terminalAdapter
    }

    /**
     * Setup input
     */
    private fun setupInput() {
        inputEditText.setOnEditorActionListener(this)
        inputEditText.setOnKeyListener { _, _, event ->
            // Handle enter key
            if (event.action == android.view.KeyEvent.ACTION_DOWN &&
                event.keyCode == android.view.KeyEvent.KEYCODE_ENTER) {
                executeCommand(inputEditText.text.toString())
                true
            } else {
                false
            }
        }
    }

    /**
     * Load command history
     */
    private fun loadHistory() {
        val history = viewModel.getCommandHistory()
        terminalAdapter.updateCommands(history)
        terminalRecyclerView.scrollToPosition(history.size - 1)
    }

    /**
     * Execute a command
     */
    private fun executeCommand(command: String) {
        if (command.isBlank()) {
            return
        }

        // Clear input
        inputEditText.text.clear()

        // Add command to history
        val commandObj = TerminalCommand(
            id = System.currentTimeMillis().toString(),
            command = command,
            timestamp = System.currentTimeMillis(),
            output = "",
            isSuccess = false
        )

        // Add to adapter
        terminalAdapter.addCommand(commandObj)
        terminalRecyclerView.scrollToPosition(terminalAdapter.itemCount - 1)

        // Execute the command in background
        viewModel.executeCommand(command) { result ->
            runOnUiThread {
                // Update the command with result
                commandObj.output = result.output
                commandObj.isSuccess = result.isSuccess
                commandObj.error = result.error
                terminalAdapter.notifyItemChanged(terminalAdapter.itemCount - 1)
            }
        }
    }

    /**
     * Editor action listener
     */
    override fun onEditorAction(v: TextView?, actionId: Int, event: android.view.KeyEvent?): Boolean {
        if (actionId == EditorInfo.IME_ACTION_SEND ||
            actionId == EditorInfo.IME_ACTION_DONE) {
            executeCommand(inputEditText.text.toString())
            return true
        }
        return false
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_terminal, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_clear -> {
                // Clear terminal
                viewModel.clearTerminal()
                terminalAdapter.clearCommands()
                return true
            }
            R.id.action_new_session -> {
                // Start new session
                viewModel.newSession()
                terminalAdapter.clearCommands()
                return true
            }
            R.id.action_save -> {
                // Save session
                viewModel.saveSession()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    override fun onBackPressed() {
        // Check if we should exit or minimize
        if (inputEditText.text.isNotEmpty()) {
            // Clear input instead of exiting
            inputEditText.text.clear()
        } else {
            super.onBackPressed()
        }
    }
}
