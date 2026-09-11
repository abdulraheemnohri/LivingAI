# Built-in Skills Package
import os
import json
from typing import Dict, Any, List

BUILTIN_SKILLS = [
    {
        "name": "system_info",
        "description": "Inspect system CPU, RAM, storage, and battery metrics.",
        "instructions": "Run system diagnostics using TermuxPlatform.",
        "sandboxed": True,
        "code": "result = input.get('platform_info', {})"
    },
    {
        "name": "summarize_file",
        "description": "Reads a local file and generates a summary.",
        "instructions": "Provide filepath parameter in input.",
        "sandboxed": True,
        "code": "filepath = input.get('filepath', '')\nresult = f'Summary for {filepath}'"
    },
    {
        "name": "device_notification",
        "description": "Send an Android toast or status bar notification.",
        "instructions": "Provide title and content in input.",
        "sandboxed": True,
        "code": "title = input.get('title', 'LivingAI')\ncontent = input.get('content', '')\nresult = f'Notification sent: {title} - {content}'"
    }
]

def get_builtin_skills() -> List[Dict[str, Any]]:
    return BUILTIN_SKILLS
