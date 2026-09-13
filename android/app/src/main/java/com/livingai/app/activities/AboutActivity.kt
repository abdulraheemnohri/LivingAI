package com.livingai.app.activities

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.livingai.app.databinding.ActivityAboutBinding

class AboutActivity : AppCompatActivity() {
    private lateinit var binding: ActivityAboutBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAboutBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupUI()
        setupListeners()
    }
    
    private fun setupUI() {
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = getString(R.string.about)
        
        binding.tvVersion.text = String.format(getString(R.string.version_format), BuildConfig.VERSION_NAME)
    }
    
    private fun setupListeners() {
        binding.btnBack.setOnClickListener { onBackPressed() }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}
