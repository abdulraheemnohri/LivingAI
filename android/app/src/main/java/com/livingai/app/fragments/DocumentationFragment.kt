package com.livingai.app.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.livingai.app.R
import com.livingai.app.viewmodels.DocumentationViewModel

/**
 * DocumentationFragment - Displays app documentation
 */
class DocumentationFragment : Fragment() {

    private lateinit var viewModel: DocumentationViewModel
    private lateinit var webView: WebView
    private lateinit var sectionsRecyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this).get(DocumentationViewModel::class.java)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_documentation, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize views
        webView = view.findViewById(R.id.web_view)
        sectionsRecyclerView = view.findViewById(R.id.recycler_sections)

        // Setup WebView
        setupWebView()

        // Setup RecyclerView
        setupRecyclerView()

        // Observe LiveData
        observeLiveData()

        // Load initial content
        loadContent("overview")
    }

    /**
     * Setup WebView
     */
    private fun setupWebView() {
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                return true
            }
        }
    }

    /**
     * Setup RecyclerView
     */
    private fun setupRecyclerView() {
        sectionsRecyclerView.layoutManager = LinearLayoutManager(requireContext())
        sectionsRecyclerView.adapter = object : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
            override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
                val view = LayoutInflater.from(parent.context)
                    .inflate(android.R.layout.simple_list_item_1, parent, false)
                return object : RecyclerView.ViewHolder(view) {}
            }

            override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
                val sections = viewModel.getSectionTitles()
                (holder.itemView as TextView).text = sections.getOrNull(position) ?: ""
                holder.itemView.setOnClickListener {
                    loadContent(sections.getOrNull(position) ?: "")
                }
            }

            override fun getItemCount(): Int = viewModel.getSectionTitles().size
        }
    }

    /**
     * Observe LiveData
     */
    private fun observeLiveData() {
        viewModel.currentSection.observe(viewLifecycleOwner) { section ->
            loadContent(section)
        }
    }

    /**
     * Load documentation content
     */
    private fun loadContent(section: String) {
        val content = viewModel.getSectionContent(section) ?: ""
        webView.loadData(content, "text/html", "UTF-8")
    }

    /**
     * Search documentation
     */
    fun search(query: String) {
        viewModel.search(query)
    }
}
