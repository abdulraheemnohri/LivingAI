package com.livingai.app.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.widget.EditText
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.adapters.TerminalAdapter
import com.livingai.app.viewmodels.TerminalViewModel

/**
 * TerminalFragment - Provides terminal functionality
 */
class TerminalFragment : Fragment(), android.widget.TextView.OnEditorActionListener {

    private lateinit var viewModel: TerminalViewModel
    private lateinit var terminalRecyclerView: RecyclerView
    private lateinit var inputEditText: EditText
    private lateinit var terminalAdapter: TerminalAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this).get(TerminalViewModel::class.java)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_terminal, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize views
        terminalRecyclerView = view.findViewById(R.id.recycler_terminal)
        inputEditText = view.findViewById(R.id.et_terminal_input)

        // Setup RecyclerView
        setupRecyclerView()

        // Setup input
        setupInput()

        // Observe LiveData
        observeLiveData()

        // Load history
        loadHistory()
    }

    /**
     * Setup RecyclerView
     */
    private fun setupRecyclerView() {
        terminalRecyclerView.layoutManager = LinearLayoutManager(requireContext()).apply {
            stackFromEnd = true
        }
        terminalAdapter = TerminalAdapter(
            mutableListOf(),
            onCommandClick = { command ->
                // Re-run the command
                inputEditText.setText(command.command)
            }
        )
        terminalRecyclerView.adapter = terminalAdapter
    }

    /**
     * Setup input
     */
    private fun setupInput() {
        inputEditText.setOnEditorActionListener(this)
    }

    /**
     * Observe LiveData
     */
    private fun observeLiveData() {
        viewModel.commands.observe(viewLifecycleOwner) { commands ->
            terminalAdapter.updateCommands(commands)
            terminalRecyclerView.scrollToPosition(commands.size - 1)
        }
    }

    /**
     * Load command history
     */
    private fun loadHistory() {
        viewModel.refresh()
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

        // Execute command
        viewModel.executeCommand(command) { result ->
            // Command execution handled by ViewModel
        }
    }

    /**
     * Editor action listener
     */
    override fun onEditorAction(v: android.widget.TextView?, actionId: Int, event: android.view.KeyEvent?): Boolean {
        if (actionId == EditorInfo.IME_ACTION_SEND ||
            actionId == EditorInfo.IME_ACTION_DONE) {
            executeCommand(inputEditText.text.toString())
            return true
        }
        return false
    }
}
