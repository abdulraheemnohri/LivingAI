package com.livingai.app.adapters

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.models.TerminalCommand

/**
 * TerminalAdapter - RecyclerView adapter for displaying terminal commands and output
 */
class TerminalAdapter(
    private var commands: MutableList<TerminalCommand> = mutableListOf(),
    private val onCommandClick: (TerminalCommand) -> Unit = {}
) : RecyclerView.Adapter<TerminalAdapter.TerminalViewHolder>() {

    companion object {
        private const val TYPE_COMMAND = 0
        private const val TYPE_OUTPUT = 1
        private const val TYPE_ERROR = 2
    }

    inner class TerminalViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val contentTextView: TextView = itemView.findViewById(R.id.tv_content)
        val timestampTextView: TextView = itemView.findViewById(R.id.tv_timestamp)
    }

    override fun getItemViewType(position: Int): Int {
        return when {
            commands[position].hasError -> TYPE_ERROR
            commands[position].hasOutput -> TYPE_OUTPUT
            else -> TYPE_COMMAND
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TerminalViewHolder {
        val layoutRes = when (viewType) {
            TYPE_COMMAND -> R.layout.item_terminal_command
            TYPE_OUTPUT -> R.layout.item_terminal_output
            TYPE_ERROR -> R.layout.item_terminal_error
            else -> R.layout.item_terminal_command
        }

        val view = LayoutInflater.from(parent.context)
            .inflate(layoutRes, parent, false)
        return TerminalViewHolder(view)
    }

    override fun onBindViewHolder(holder: TerminalViewHolder, position: Int) {
        val command = commands[position]

        // Set content
        holder.contentTextView.text = when {
            command.hasError -> command.error
            command.hasOutput -> command.output
            else -> "$ ${command.command}"
        }

        // Set timestamp
        holder.timestampTextView.text = command.displayTime

        // Set text color based on type
        val textColor = when {
            command.hasError -> Color.RED
            command.hasOutput -> Color.GREEN
            else -> Color.WHITE
        }
        holder.contentTextView.setTextColor(textColor)

        // Set click listener
        holder.itemView.setOnClickListener { onCommandClick(command) }
    }

    override fun getItemCount(): Int = commands.size

    /**
     * Add a command to the list
     */
    fun addCommand(command: TerminalCommand) {
        commands.add(command)
        notifyItemInserted(commands.size - 1)
    }

    /**
     * Update a specific command
     */
    fun updateCommand(updatedCommand: TerminalCommand) {
        val index = commands.indexOfFirst { it.id == updatedCommand.id }
        if (index >= 0) {
            commands[index] = updatedCommand
            notifyItemChanged(index)
        }
    }

    /**
     * Clear all commands
     */
    fun clearCommands() {
        commands.clear()
        notifyDataSetChanged()
    }

    /**
     * Update all commands
     */
    fun updateCommands(newCommands: List<TerminalCommand>) {
        commands.clear()
        commands.addAll(newCommands)
        notifyDataSetChanged()
    }
}
