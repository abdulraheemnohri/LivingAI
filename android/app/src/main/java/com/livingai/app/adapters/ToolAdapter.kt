package com.livingai.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.models.Tool
import com.livingai.app.utils.Constants

/**
 * ToolAdapter - RecyclerView adapter for displaying tools
 */
class ToolAdapter(
    private var tools: MutableList<Tool> = mutableListOf(),
    private val onToolClick: (Tool) -> Unit = {},
    private val onToolToggle: (Tool) -> Unit = {}
) : RecyclerView.Adapter<ToolAdapter.ToolViewHolder>() {

    inner class ToolViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val nameTextView: TextView = itemView.findViewById(R.id.tv_tool_name)
        val categoryTextView: TextView = itemView.findViewById(R.id.tv_tool_category)
        val statusTextView: TextView = itemView.findViewById(R.id.tv_tool_status)
        val descriptionTextView: TextView = itemView.findViewById(R.id.tv_tool_description)
        val iconImageView: ImageView = itemView.findViewById(R.id.iv_tool_icon)
        val toggleSwitch: View = itemView.findViewById(R.id.switch_enabled)
        val usageTextView: TextView = itemView.findViewById(R.id.tv_tool_usage)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ToolViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_tool, parent, false)
        return ToolViewHolder(view)
    }

    override fun onBindViewHolder(holder: ToolViewHolder, position: Int) {
        val tool = tools[position]

        // Set tool data
        holder.nameTextView.text = tool.displayName
        holder.categoryTextView.text = tool.category
        holder.statusTextView.text = tool.status
        holder.descriptionTextView.text = tool.description
        holder.usageTextView.text = holder.itemView.context.getString(R.string.usage_count, tool.usageCount)

        // Set icon based on category
        val iconRes = when (tool.category) {
            Constants.TOOL_CATEGORY_CODE -> R.drawable.ic_code
            Constants.TOOL_CATEGORY_ANALYSIS -> R.drawable.ic_analysis
            Constants.TOOL_CATEGORY_CREATIVE -> R.drawable.ic_creative
            Constants.TOOL_CATEGORY_DATA -> R.drawable.ic_data
            Constants.TOOL_CATEGORY_SYSTEM -> R.drawable.ic_system
            Constants.TOOL_CATEGORY_UTILITY -> R.drawable.ic_utility
            Constants.TOOL_CATEGORY_NETWORK -> R.drawable.ic_network
            Constants.TOOL_CATEGORY_FILE -> R.drawable.ic_file
            Constants.TOOL_CATEGORY_DATABASE -> R.drawable.ic_database
            Constants.TOOL_CATEGORY_AI -> R.drawable.ic_ai
            else -> R.drawable.ic_tool
        }
        holder.iconImageView.setImageResource(iconRes)

        // Set status color
        val statusColor = when {
            !tool.isAvailable -> R.color.status_disabled
            tool.status == Constants.TOOL_STATUS_ERROR -> R.color.status_error
            else -> R.color.status_enabled
        }
        holder.statusTextView.setTextColor(holder.itemView.context.getColor(statusColor))

        // Set toggle switch state
        if (holder.toggleSwitch is android.widget.Switch) {
            (holder.toggleSwitch as android.widget.Switch).isChecked = tool.isEnabled
        }

        // Set click listeners
        holder.itemView.setOnClickListener { onToolClick(tool) }
        holder.toggleSwitch.setOnClickListener { onToolToggle(tool) }
    }

    override fun getItemCount(): Int = tools.size

    /**
     * Update the list of tools
     */
    fun updateTools(newTools: List<Tool>) {
        tools.clear()
        tools.addAll(newTools)
        notifyDataSetChanged()
    }

    /**
     * Add a tool to the list
     */
    fun addTool(tool: Tool) {
        tools.add(tool)
        notifyItemInserted(tools.size - 1)
    }

    /**
     * Remove a tool from the list
     */
    fun removeTool(tool: Tool) {
        val index = tools.indexOf(tool)
        if (index >= 0) {
            tools.removeAt(index)
            notifyItemRemoved(index)
        }
    }

    /**
     * Update a specific tool
     */
    fun updateTool(updatedTool: Tool) {
        val index = tools.indexOfFirst { it.id == updatedTool.id }
        if (index >= 0) {
            tools[index] = updatedTool
            notifyItemChanged(index)
        }
    }
}
