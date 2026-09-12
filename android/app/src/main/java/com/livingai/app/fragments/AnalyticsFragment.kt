package com.livingai.app.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.livingai.app.R
import com.livingai.app.viewmodels.AnalyticsViewModel

/**
 * AnalyticsFragment - Displays analytics data
 */
class AnalyticsFragment : Fragment() {

    private lateinit var viewModel: AnalyticsViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this).get(AnalyticsViewModel::class.java)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_analytics, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe LiveData
        observeLiveData()

        // Load data
        loadData()
    }

    /**
     * Observe LiveData
     */
    private fun observeLiveData() {
        viewModel.usageStats.observe(viewLifecycleOwner) { stats ->
            updateUsageStats(stats)
        }

        viewModel.performanceData.observe(viewLifecycleOwner) { data ->
            updatePerformanceData(data)
        }

        viewModel.systemHealth.observe(viewLifecycleOwner) { health ->
            updateSystemHealth(health)
        }
    }

    /**
     * Update usage statistics
     */
    private fun updateUsageStats(stats: Map<String, Any>) {
        view?.findViewById<TextView>(R.id.tv_total_sessions)?.text = stats["total_sessions"].toString()
        view?.findViewById<TextView>(R.id.tv_total_commands)?.text = stats["total_commands"].toString()
        view?.findViewById<TextView>(R.id.tv_total_agents)?.text = stats["total_agents"].toString()
        view?.findViewById<TextView>(R.id.tv_total_tasks)?.text = stats["total_tasks"].toString()
        view?.findViewById<TextView>(R.id.tv_avg_session_duration)?.text = stats["average_session_duration"].toString()
    }

    /**
     * Update performance data
     */
    private fun updatePerformanceData(data: Map<String, Any>) {
        view?.findViewById<TextView>(R.id.tv_avg_execution_time)?.text = data["average_execution_time"].toString()
        view?.findViewById<TextView>(R.id.tv_success_rate)?.text = data["success_rate"].toString()
        view?.findViewById<TextView>(R.id.tv_failure_rate)?.text = data["failure_rate"].toString()
        view?.findViewById<TextView>(R.id.tv_max_concurrent_tasks)?.text = data["max_concurrent_tasks"].toString()
    }

    /**
     * Update system health
     */
    private fun updateSystemHealth(health: Map<String, Any>) {
        view?.findViewById<TextView>(R.id.tv_system_status)?.text = health["status"].toString()
        view?.findViewById<TextView>(R.id.tv_cpu_usage)?.text = health["cpu_usage"].toString()
        view?.findViewById<TextView>(R.id.tv_memory_usage)?.text = health["memory_usage"].toString()
        view?.findViewById<TextView>(R.id.tv_storage_usage)?.text = health["storage_usage"].toString()
        view?.findViewById<TextView>(R.id.tv_network_status)?.text = health["network_status"].toString()
    }

    /**
     * Load data
     */
    private fun loadData() {
        viewModel.refresh()
    }
}
