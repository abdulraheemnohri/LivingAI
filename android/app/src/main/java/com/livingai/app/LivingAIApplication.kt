package com.livingai.app

import android.app.Application
import android.content.Context
import androidx.multidex.MultiDex

class LivingAIApplication : Application() {
    
    companion object {
        private lateinit var instance: LivingAIApplication
        fun getContext(): Context = instance.applicationContext
    }
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        MultiDex.install(this)
    }
    
    override fun attachBaseContext(base: Context) {
        super.attachBaseContext(base)
        MultiDex.install(this)
    }
}
