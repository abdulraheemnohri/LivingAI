import pytest
from livingai.config import ConfigManager
from livingai.security.audit import AuditLogger
from livingai.actions.policy import ActionPolicy
from livingai.actions.executor import ActionExecutor


def test_action_policy(tmp_path):
    config = ConfigManager(str(tmp_path / "config.yaml"))
    audit_logger = AuditLogger(str(tmp_path / "logs"))
    policy = ActionPolicy(config, audit_logger)

    assert policy.get_risk_level("ls -la") == "LOW"
    assert policy.get_risk_level("rm -rf /") == "CRITICAL"


def test_action_executor(tmp_path):
    config = ConfigManager(str(tmp_path / "config.yaml"))
    audit_logger = AuditLogger(str(tmp_path / "logs"))
    executor = ActionExecutor(config, audit_logger)

    res = executor.execute({"command": "echo", "args": ["hello"]})
    assert res["status"] == "completed"
    assert "hello" in res["stdout"]
