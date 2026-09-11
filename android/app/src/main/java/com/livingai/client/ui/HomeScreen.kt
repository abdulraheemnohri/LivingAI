package com.livingai.client.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun HomeScreen() {
    val statusText = remember { mutableStateOf("● Connected to LivingAI Core") }

    Column(modifier = Modifier.padding(16.dp)) {
        Text(text = "✦ LivingAI Android Client", style = androidx.compose.material3.MaterialTheme.typography.headlineMedium)
        Text(text = statusText.value, modifier = Modifier.padding(vertical = 8.dp))
        Button(onClick = { /* Refresh status */ }) {
            Text("Refresh Status")
        }
    }
}
