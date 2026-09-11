import pytest
from livingai.config import ConfigManager
from livingai.platform.termux import TermuxPlatform
from livingai.security.audit import AuditLogger
from livingai.ai.downloader import ModelDownloader


def test_model_downloader(tmp_path):
    config = ConfigManager(str(tmp_path / "config.yaml"))
    platform = TermuxPlatform()
    audit_logger = AuditLogger(str(tmp_path / "logs"))
    downloader = ModelDownloader(str(tmp_path / "models"), config, platform, audit_logger)

    assert downloader.get_expected_files() == [
        "config.json",
        "pytorch_model.bin",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.txt",
    ]
