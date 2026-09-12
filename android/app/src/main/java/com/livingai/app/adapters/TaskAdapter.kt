package com.livingai.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.models.Task
import com.livingai.app.utils.Constants

/**
 * TaskAdapter - RecyclerView adapter for displaying tasks
 */
class TaskAdapter(
    private var tasks: MutableList<Task> = mutableListOf(),
    private val onTaskClick: (Task) -> Unit = {},
    private val onTaskRetry: (Task) -> Unit = {},
    private val onTaskCancel: (Task) -> Unit = {},
    private val onTaskDelete: (Task) -> Unit = {}
) : RecyclerView.Adapter<TaskAdapter.TaskViewHolder>() {

    inner class TaskViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val nameTextView: TextView = itemView.findViewById(R.id.tv_task_name)
        val statusTextView: TextView = itemView.findViewById(R.id.tv_task_status)
        val priorityTextView: TextView = itemView.findViewById(R.id.tv_task_priority)
        val agentTextView: TextView = itemView.findViewById(R.id.tv_task_agent)
        val createdTextView: TextView = itemView.findViewById(R.id.tv_task_created)
        val iconImageView: ImageView = itemView.findViewById(R.id.iv_task_icon)
        val retryButton: View = itemView.findViewById(R.id.btn_retry)
        val cancelButton: View = itemView.findViewById(R.id.btn_cancel)
        val deleteButton: View = itemView.findViewById(R.id.btn_delete)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TaskViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_task, parent, false)
        return TaskViewHolder(view)
    }

    override fun onBindViewHolder(holder: TaskViewHolder, position: Int) {
        val task = tasks[position]

        // Set task data
        holder.nameTextView.text = task.displayName
        holder.statusTextView.text = task.status
        holder.priorityTextView.text = task.priority
        holder.agentTextView.text = task.agentName
        holder.createdTextView.text = task.createdAt

        // Set icon based on priority
        val iconRes = when (task.priority) {
            Constants.PRIORITY_CRITICAL -> R.drawable.ic_priority_critical
            Constants.PRIORITY_HIGH -> R.drawable.ic_priority_high
            Constants.PRIORITY_MEDIUM -> R.drawable.ic_priority_medium
            Constants.PRIORITY_LOW -> R.drawable.ic_priority_low
            else -> R.drawable.ic_task
        }
        holder.iconImageView.setImageResource(iconRes)

        // Set status color
        val statusColor = when (task.status) {
            Constants.TASK_STATUS_COMPLETED -> R.color.status_completed
            Constants.TASK_STATUS_IN_PROGRESS -> R.color.status_in_progress
            Constants.TASK_STATUS_PENDING -> R.color.status_pending
            Constants.TASK_STATUS_FAILED -> R.color.status_failed
            Constants.TASK_STATUS_CANCELLED -> R.color.status_cancelled
            else -> R.color.status_unknown
        }
        holder.statusTextView.setTextColor(holder.itemView.context.getColor(statusColor))

        // Set click listeners
        holder.itemView.setOnClickListener { onTaskClick(task) }
        holder.retryButton.setOnClickListener { onTaskRetry(task) }
        holder.cancelButton.setOnClickListener { onTaskCancel(task) }
        holder.deleteButton.setOnClickListener { onTaskDelete(task) }

        // Show/hide buttons based on status
        holder.retryButton.visibility = if (task.isFailed || task.isCancelled) View.VISIBLE else View.GONE
        holder.cancelButton.visibility = if (task.isRunning || task.isPending) View.VISIBLE else View.GONE
    }

    override fun getItemCount(): Int = tasks.size

    /**
     * Update the list of tasks
     */
    fun updateTasks(newTasks: List<Task>) {
        tasks.clear()
        tasks.addAll(newTasks)
        notifyDataSetChanged()
    }

    /**
     * Add a task to the list
     */
    fun addTask(task: Task) {
        tasks.add(task)
        notifyItemInserted(tasks.size - 1)
    }

    /**
     * Remove a task from the list
     */
    fun removeTask(task: Task) {
        val index = tasks.indexOf(task)
        if (index >= 0) {
            tasks.removeAt(index)
            notifyItemRemoved(index)
        }
    }

    /**
     * Update a specific task
     */
    fun updateTask(updatedTask: Task) {
        val index = tasks.indexOfFirst { it.id == updatedTask.id }
        if (index >= 0) {
            tasks[index] = updatedTask
            notifyItemChanged(index)
        }
    }
}
