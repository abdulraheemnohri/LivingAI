package com.livingai.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.models.Agent
import com.livingai.app.utils.Constants

/**
 * AgentAdapter - RecyclerView adapter for displaying agents
 */
class AgentAdapter(
    private var agents: MutableList<Agent> = mutableListOf(),
    private val onAgentClick: (Agent) -> Unit = {},
    private val onAgentStart: (Agent) -> Unit = {},
    private val onAgentStop: (Agent) -> Unit = {},
    private val onAgentDelete: (Agent) -> Unit = {}
) : RecyclerView.Adapter<AgentAdapter.AgentViewHolder>() {

    inner class AgentViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val nameTextView: TextView = itemView.findViewById(R.id.tv_agent_name)
        val typeTextView: TextView = itemView.findViewById(R.id.tv_agent_type)
        val statusTextView: TextView = itemView.findViewById(R.id.tv_agent_status)
        val descriptionTextView: TextView = itemView.findViewById(R.id.tv_agent_description)
        val iconImageView: ImageView = itemView.findViewById(R.id.iv_agent_icon)
        val startButton: View = itemView.findViewById(R.id.btn_start)
        val stopButton: View = itemView.findViewById(R.id.btn_stop)
        val deleteButton: View = itemView.findViewById(R.id.btn_delete)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AgentViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_agent, parent, false)
        return AgentViewHolder(view)
    }

    override fun onBindViewHolder(holder: AgentViewHolder, position: Int) {
        val agent = agents[position]

        // Set agent data
        holder.nameTextView.text = agent.displayName
        holder.typeTextView.text = agent.type
        holder.statusTextView.text = agent.status
        holder.descriptionTextView.text = agent.description

        // Set icon based on type
        val iconRes = when (agent.type) {
            Constants.AGENT_TYPE_RESEARCH -> R.drawable.ic_research
            Constants.AGENT_TYPE_DEVELOPMENT -> R.drawable.ic_development
            Constants.AGENT_TYPE_ANALYSIS -> R.drawable.ic_analysis
            Constants.AGENT_TYPE_CREATIVE -> R.drawable.ic_creative
            else -> R.drawable.ic_agent
        }
        holder.iconImageView.setImageResource(iconRes)

        // Set status color
        val statusColor = when (agent.status) {
            Constants.AGENT_STATUS_ACTIVE -> R.color.status_active
            Constants.AGENT_STATUS_INACTIVE -> R.color.status_inactive
            Constants.AGENT_STATUS_PAUSED -> R.color.status_paused
            Constants.AGENT_STATUS_ERROR -> R.color.status_error
            else -> R.color.status_unknown
        }
        holder.statusTextView.setTextColor(holder.itemView.context.getColor(statusColor))

        // Set click listeners
        holder.itemView.setOnClickListener { onAgentClick(agent) }
        holder.startButton.setOnClickListener { onAgentStart(agent) }
        holder.stopButton.setOnClickListener { onAgentStop(agent) }
        holder.deleteButton.setOnClickListener { onAgentDelete(agent) }

        // Show/hide buttons based on status
        holder.startButton.visibility = if (agent.status == Constants.AGENT_STATUS_INACTIVE) View.VISIBLE else View.GONE
        holder.stopButton.visibility = if (agent.status == Constants.AGENT_STATUS_ACTIVE) View.VISIBLE else View.GONE
    }

    override fun getItemCount(): Int = agents.size

    /**
     * Update the list of agents
     */
    fun updateAgents(newAgents: List<Agent>) {
        agents.clear()
        agents.addAll(newAgents)
        notifyDataSetChanged()
    }

    /**
     * Add an agent to the list
     */
    fun addAgent(agent: Agent) {
        agents.add(agent)
        notifyItemInserted(agents.size - 1)
    }

    /**
     * Remove an agent from the list
     */
    fun removeAgent(agent: Agent) {
        val index = agents.indexOf(agent)
        if (index >= 0) {
            agents.removeAt(index)
            notifyItemRemoved(index)
        }
    }

    /**
     * Update a specific agent
     */
    fun updateAgent(updatedAgent: Agent) {
        val index = agents.indexOfFirst { it.id == updatedAgent.id }
        if (index >= 0) {
            agents[index] = updatedAgent
            notifyItemChanged(index)
        }
    }
}
