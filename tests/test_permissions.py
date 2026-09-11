import pytest
from livingai.security.permissions import PermissionManager


def test_permission_manager():
    pm = PermissionManager()
    assert pm.is_android_permission_granted("storage") is True
    assert pm.is_android_permission_granted("camera") is False

    pm.grant_permission("camera")
    assert pm.is_android_permission_granted("camera") is True

    summary = pm.get_permission_summary()
    assert "camera" in summary
    assert summary["camera"] is True
