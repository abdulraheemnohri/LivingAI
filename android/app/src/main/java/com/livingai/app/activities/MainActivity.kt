package com.livingai.app.activities

import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.FrameLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentTransaction
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.google.android.material.navigation.NavigationView
import com.livingai.app.R
import com.livingai.app.fragments.DashboardFragment
import com.livingai.app.fragments.AgentsFragment
import com.livingai.app.fragments.TasksFragment
import com.livingai.app.fragments.ToolsFragment
import com.livingai.app.fragments.MemoryFragment
import com.livingai.app.fragments.SettingsFragment
import com.livingai.app.fragments.TerminalFragment
import com.livingai.app.fragments.AnalyticsFragment
import com.livingai.app.fragments.DocumentationFragment
import com.livingai.app.fragments.AboutFragment
import com.livingai.app.utils.Constants
import com.livingai.app.utils.PreferenceHelper

/**
 * MainActivity - Primary activity for the LivingAI app
 * Handles navigation between different sections of the app
 */
class MainActivity : AppCompatActivity(),
    NavigationView.OnNavigationItemSelectedListener,
    BottomNavigationView.OnNavigationItemSelectedListener {

    private lateinit var drawerLayout: DrawerLayout
    private lateinit var navigationView: NavigationView
    private lateinit var bottomNavigationView: BottomNavigationView
    private lateinit var toolbar: Toolbar
    private lateinit var fragmentContainer: FrameLayout
    private lateinit var fab: FloatingActionButton

    // Current fragment tag
    private var currentFragmentTag: String = Constants.FRAGMENT_DASHBOARD

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize views
        initializeViews()

        // Setup toolbar
        setupToolbar()

        // Setup navigation drawer
        setupNavigationDrawer()

        // Setup bottom navigation
        setupBottomNavigation()

        // Setup FAB
        setupFAB()

        // Load initial fragment
        if (savedInstanceState == null) {
            loadFragment(DashboardFragment(), Constants.FRAGMENT_DASHBOARD)
        } else {
            // Restore fragment state
            currentFragmentTag = savedInstanceState.getString("currentFragment", Constants.FRAGMENT_DASHBOARD)
        }

        // Update UI based on current theme
        updateThemeUI()
    }

    /**
     * Initialize all views
     */
    private fun initializeViews() {
        drawerLayout = findViewById(R.id.drawer_layout)
        navigationView = findViewById(R.id.navigation_view)
        bottomNavigationView = findViewById(R.id.bottom_navigation)
        toolbar = findViewById(R.id.toolbar)
        fragmentContainer = findViewById(R.id.fragment_container)
        fab = findViewById(R.id.fab)
    }

    /**
     * Setup the toolbar
     */
    private fun setupToolbar() {
        setSupportActionBar(toolbar)
        supportActionBar?.apply {
            title = getString(R.string.app_name)
            setDisplayHomeAsUpEnabled(true)
            setHomeAsUpIndicator(R.drawable.ic_menu)
        }
    }

    /**
     * Setup the navigation drawer
     */
    private fun setupNavigationDrawer() {
        navigationView.setNavigationItemSelectedListener(this)

        // Set header information
        val headerView = navigationView.getHeaderView(0)
        // Can be customized with user info
    }

    /**
     * Setup the bottom navigation
     */
    private fun setupBottomNavigation() {
        bottomNavigationView.setOnNavigationItemSelectedListener(this)

        // Select the initial item
        bottomNavigationView.selectedItemId = R.id.nav_dashboard
    }

    /**
     * Setup the Floating Action Button
     */
    private fun setupFAB() {
        fab.setOnClickListener {
            // Handle FAB click based on current fragment
            handleFABClick()
        }
    }

    /**
     * Handle FAB click based on current fragment
     */
    private fun handleFABClick() {
        when (currentFragmentTag) {
            Constants.FRAGMENT_DASHBOARD -> {
                // Start a new agent or task
                showCreateOptions()
            }
            Constants.FRAGMENT_AGENTS -> {
                // Create new agent
                val intent = Intent(this, CreateAgentActivity::class.java)
                startActivity(intent)
            }
            Constants.FRAGMENT_TASKS -> {
                // Create new task
                val intent = Intent(this, CreateTaskActivity::class.java)
                startActivity(intent)
            }
            Constants.FRAGMENT_TOOLS -> {
                // Refresh tools
                Toast.makeText(this, "Refreshing tools...", Toast.LENGTH_SHORT).show()
            }
            else -> {
                // Default action
                showCreateOptions()
            }
        }
    }

    /**
     * Show create options dialog
     */
    private fun showCreateOptions() {
        // Implementation for showing create options
        Toast.makeText(this, "Create options", Toast.LENGTH_SHORT).show()
    }

    /**
     * Load a fragment into the container
     */
    private fun loadFragment(fragment: Fragment, tag: String) {
        val transaction: FragmentTransaction = supportFragmentManager.beginTransaction()
        transaction.replace(R.id.fragment_container, fragment, tag)
        transaction.addToBackStack(null)
        transaction.commit()
        currentFragmentTag = tag
    }

    /**
     * Navigation item selected listener for drawer
     */
    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.nav_dashboard -> {
                loadFragment(DashboardFragment(), Constants.FRAGMENT_DASHBOARD)
            }
            R.id.nav_agents -> {
                loadFragment(AgentsFragment(), Constants.FRAGMENT_AGENTS)
            }
            R.id.nav_tools -> {
                loadFragment(ToolsFragment(), Constants.FRAGMENT_TOOLS)
            }
            R.id.nav_tasks -> {
                loadFragment(TasksFragment(), Constants.FRAGMENT_TASKS)
            }
            R.id.nav_memory -> {
                loadFragment(MemoryFragment(), Constants.FRAGMENT_MEMORY)
            }
            R.id.nav_settings -> {
                loadFragment(SettingsFragment(), Constants.FRAGMENT_SETTINGS)
            }
            R.id.nav_terminal -> {
                loadFragment(TerminalFragment(), Constants.FRAGMENT_TERMINAL)
            }
            R.id.nav_analytics -> {
                loadFragment(AnalyticsFragment(), Constants.FRAGMENT_ANALYTICS)
            }
            R.id.nav_documentation -> {
                loadFragment(DocumentationFragment(), Constants.FRAGMENT_DOCUMENTATION)
            }
            R.id.nav_about -> {
                loadFragment(AboutFragment(), Constants.FRAGMENT_ABOUT)
            }
            R.id.nav_exit -> {
                finishAffinity()
                return true
            }
        }
        drawerLayout.closeDrawer(GravityCompat.START)
        return true
    }

    /**
     * Bottom navigation item selected listener
     */
    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.nav_dashboard -> {
                loadFragment(DashboardFragment(), Constants.FRAGMENT_DASHBOARD)
                return true
            }
            R.id.nav_agents -> {
                loadFragment(AgentsFragment(), Constants.FRAGMENT_AGENTS)
                return true
            }
            R.id.nav_tools -> {
                loadFragment(ToolsFragment(), Constants.FRAGMENT_TOOLS)
                return true
            }
            R.id.nav_tasks -> {
                loadFragment(TasksFragment(), Constants.FRAGMENT_TASKS)
                return true
            }
            R.id.nav_memory -> {
                loadFragment(MemoryFragment(), Constants.FRAGMENT_MEMORY)
                return true
            }
        }
        return false
    }

    /**
     * Update UI based on current theme
     */
    private fun updateThemeUI() {
        val theme = PreferenceHelper.getTheme()
        when (theme) {
            PreferenceHelper.THEME_DARK -> {
                // Apply dark theme
            }
            PreferenceHelper.THEME_LIGHT -> {
                // Apply light theme
            }
            PreferenceHelper.THEME_SYSTEM -> {
                // Apply system theme
            }
        }
    }

    /**
     * Toggle navigation drawer
     */
    fun toggleDrawer() {
        if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            drawerLayout.openDrawer(GravityCompat.START)
        }
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            android.R.id.home -> {
                toggleDrawer()
                return true
            }
        }
        return super.onOptionsItemSelected(item)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("currentFragment", currentFragmentTag)
    }

    override fun onBackPressed() {
        if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            // Handle back press based on fragment stack
            if (supportFragmentManager.backStackEntryCount > 1) {
                supportFragmentManager.popBackStack()
            } else {
                super.onBackPressed()
            }
        }
    }
}
