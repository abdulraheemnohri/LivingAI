import pytest
from livingai.config import ConfigManager
from livingai.security.audit import AuditLogger
from livingai.skills.sandbox import SkillSandbox
from livingai.skills.validator import SkillValidator


def test_skill_sandbox(tmp_path):
    config = ConfigManager(str(tmp_path / "config.yaml"))
    audit_logger = AuditLogger(str(tmp_path / "logs"))
    sandbox = SkillSandbox(config, audit_logger)

    code = "result = 2 + 2"
    result = sandbox.execute(code, {}, {"enabled": True})
    assert result["status"] == "success"
    assert result["output"] == 4


def test_skill_validator(tmp_path):
    config = ConfigManager(str(tmp_path / "config.yaml"))
    audit_logger = AuditLogger(str(tmp_path / "logs"))
    validator = SkillValidator(config, audit_logger)
    valid, errors = validator.validate_code("x = 10")
    assert valid is True
    assert len(errors) == 0
