package com.livingai.client.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun ChatScreen() {
    val query = remember { mutableStateOf("") }
    val response = remember { mutableStateOf("") }

    Column(modifier = Modifier.padding(16.dp)) {
        Text(text = "LivingAI Assistant", style = androidx.compose.material3.MaterialTheme.typography.titleLarge)
        OutlinedTextField(
            value = query.value,
            onValueChange = { query.value = it },
            label = { Text("Ask LivingAI...") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)
        )
        Button(onClick = { /* Send chat request */ }) {
            Text("Send")
        }
        Text(text = response.value, modifier = Modifier.padding(top = 16.dp))
    }
}
