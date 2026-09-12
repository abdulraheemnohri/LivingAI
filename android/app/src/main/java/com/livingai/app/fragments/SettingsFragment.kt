package com.livingai.app.fragments

import android.os.Bundle
import androidx.preference.PreferenceFragmentCompat
import com.livingai.app.R

/**
 * SettingsFragment - Displays app settings
 */
class SettingsFragment : PreferenceFragmentCompat() {

    override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
        setPreferencesFromResource(R.xml.preferences, rootKey)
    }
}
