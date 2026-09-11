import pytest
from livingai.config import ConfigManager
from livingai.memory.manager import MemoryManager
from livingai.learning.engine import LearningEngine
from livingai.security.audit import AuditLogger


def test_learning_engine(tmp_path):
    config = ConfigManager(str(tmp_path / "config.yaml"))
    audit_logger = AuditLogger(str(tmp_path / "logs"))
    memory_manager = MemoryManager(str(tmp_path / "livingai.db"), config, audit_logger)

    learning_engine = LearningEngine(memory_manager, config, audit_logger)
    stats = learning_engine.get_stats()
    assert isinstance(stats, dict)
