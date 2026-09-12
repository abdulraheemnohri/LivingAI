package com.livingai.app.receivers

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData

/**
 * NetworkReceiver - Broadcast receiver for network connectivity changes
 */
class NetworkReceiver : BroadcastReceiver() {

    companion object {
        // LiveData for network status
        private val _networkStatus = MutableLiveData<Boolean>()
        val networkStatus: LiveData<Boolean> = _networkStatus

        // Current network status
        private var isConnected = false

        /**
         * Register network callback for API 21+
         */
        fun registerNetworkCallback(context: Context) {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val networkRequest = NetworkRequest.Builder()
                .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
                .build()

            val networkCallback = object : ConnectivityManager.NetworkCallback() {
                override fun onAvailable(network: Network) {
                    isConnected = true
                    _networkStatus.postValue(true)
                }

                override fun onLost(network: Network) {
                    isConnected = false
                    _networkStatus.postValue(false)
                }
            }

            connectivityManager.registerNetworkCallback(networkRequest, networkCallback)
        }

        /**
         * Check current network status
         */
        fun isNetworkAvailable(context: Context): Boolean {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val network = connectivityManager.activeNetwork ?: return false
            val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
            return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
        }
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == ConnectivityManager.CONNECTIVITY_ACTION) {
            isConnected = isNetworkAvailable(context)
            _networkStatus.postValue(isConnected)
        }
    }
}
