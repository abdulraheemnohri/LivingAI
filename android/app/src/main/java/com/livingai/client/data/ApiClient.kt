package com.livingai.client.data

import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject

class ApiClient(private val baseUrl: String = "http://127.0.0.1:8080") {

    fun getStatus(): String {
        val url = URL("$baseUrl/api/status")
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "GET"
        return conn.inputStream.bufferedReader().use { it.readText() }
    }

    fun sendChat(query: String): String {
        val url = URL("$baseUrl/api/chat")
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.setRequestProperty("Content-Type", "application/json")
        conn.doOutput = true

        val json = JSONObject().apply { put("query", query) }
        conn.outputStream.bufferedWriter().use { it.write(json.toString()) }

        return conn.inputStream.bufferedReader().use { it.readText() }
    }
}
