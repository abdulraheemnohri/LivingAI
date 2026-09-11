import pytest
from livingai.config import ConfigManager
from livingai.platform.termux import TermuxPlatform
from livingai.security.audit import AuditLogger
from livingai.ai.model_manager import ModelManager


def test_model_manager_init(tmp_path):
    config = ConfigManager(str(tmp_path / "config.yaml"))
    platform = TermuxPlatform()
    audit_logger = AuditLogger(str(tmp_path / "logs"))
    manager = ModelManager(
        model_dir=str(tmp_path / "models"),
        config=config,
        platform=platform,
        audit_logger=audit_logger
    )
    status = manager.get_status()
    assert status["repository"] == "HuggingFaceTB/SmolLM3-3B"
    assert status["loaded"] is False
