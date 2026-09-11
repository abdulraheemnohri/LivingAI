import pytest
from livingai.memory.database import MemoryDatabase
from livingai.memory.models import Memory, MemoryType, MemoryImportance


def test_memory_database(tmp_path):
    db_path = str(tmp_path / "livingai.db")
    db = MemoryDatabase(db_path)

    memory = Memory(
        content="Test preference: user prefers dark mode",
        memory_type=MemoryType.PREFERENCE,
        importance=MemoryImportance.HIGH
    )
    mem_id = db.create(memory)
    assert mem_id is not None

    retrieved = db.read(mem_id)
    assert retrieved is not None
    assert retrieved.content == "Test preference: user prefers dark mode"
    assert db.count() == 1
