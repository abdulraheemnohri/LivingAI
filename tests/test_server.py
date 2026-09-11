import pytest
from livingai.config import ConfigManager
from livingai.security.audit import AuditLogger
from livingai.server.api import APIHandlers


class DummyApp:
    def get_status(self):
        return {"status": "ONLINE", "model": "SmolLM3-3B"}
    def process_query(self, query):
        return f"Echo: {query}"
    def run_doctor(self):
        return {"PASS": True}


def test_api_handlers():
    dummy = DummyApp()
    handlers = APIHandlers(dummy)
    status = handlers.handle_status()
    assert status["status"] == "ONLINE"

    chat_res = handlers.handle_chat({"query": "Hello AI"})
    assert chat_res["response"] == "Echo: Hello AI"
