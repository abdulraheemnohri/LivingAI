package com.livingai.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.models.MemoryEntry

/**
 * MemoryAdapter - RecyclerView adapter for displaying memory entries
 */
class MemoryAdapter(
    private var entries: MutableList<MemoryEntry> = mutableListOf(),
    private val onMemoryClick: (MemoryEntry) -> Unit = {},
    private val onMemoryDelete: (MemoryEntry) -> Unit = {}
) : RecyclerView.Adapter<MemoryAdapter.MemoryViewHolder>() {

    inner class MemoryViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val keyTextView: TextView = itemView.findViewById(R.id.tv_memory_key)
        val valueTextView: TextView = itemView.findViewById(R.id.tv_memory_value)
        val categoryTextView: TextView = itemView.findViewById(R.id.tv_memory_category)
        val typeTextView: TextView = itemView.findViewById(R.id.tv_memory_type)
        val createdTextView: TextView = itemView.findViewById(R.id.tv_memory_created)
        val deleteButton: View = itemView.findViewById(R.id.btn_delete)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MemoryViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_memory, parent, false)
        return MemoryViewHolder(view)
    }

    override fun onBindViewHolder(holder: MemoryViewHolder, position: Int) {
        val entry = entries[position]

        // Set entry data
        holder.keyTextView.text = entry.displayKey
        holder.valueTextView.text = entry.value
        holder.categoryTextView.text = entry.category
        holder.typeTextView.text = entry.type
        holder.createdTextView.text = entry.createdAt

        // Set click listeners
        holder.itemView.setOnClickListener { onMemoryClick(entry) }
        holder.deleteButton.setOnClickListener { onMemoryDelete(entry) }
    }

    override fun getItemCount(): Int = entries.size

    /**
     * Update the list of entries
     */
    fun updateEntries(newEntries: List<MemoryEntry>) {
        entries.clear()
        entries.addAll(newEntries)
        notifyDataSetChanged()
    }

    /**
     * Add an entry to the list
     */
    fun addEntry(entry: MemoryEntry) {
        entries.add(entry)
        notifyItemInserted(entries.size - 1)
    }

    /**
     * Remove an entry from the list
     */
    fun removeEntry(entry: MemoryEntry) {
        val index = entries.indexOf(entry)
        if (index >= 0) {
            entries.removeAt(index)
            notifyItemRemoved(index)
        }
    }

    /**
     * Update a specific entry
     */
    fun updateEntry(updatedEntry: MemoryEntry) {
        val index = entries.indexOfFirst { it.id == updatedEntry.id }
        if (index >= 0) {
            entries[index] = updatedEntry
            notifyItemChanged(index)
        }
    }
}
