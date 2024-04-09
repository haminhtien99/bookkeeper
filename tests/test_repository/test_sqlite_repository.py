import pytest
import sqlite3
import os
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.repository.memory_repository import MemoryRepository

@pytest.fixture
def temp_db():
    # Create an in-memory database for testing
    conn = sqlite3.connect(':memory:')
    yield conn
    conn.close()

@pytest.fixture
def repo(custom_class):
    return SQLiteRepository(':memory:', custom_class)
@pytest.fixture
def custom_class():
    class Custom:
        pk: int = 0
        value1: Any = ''
        value2: Any = ''
    return Custom

def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.get(pk)
def test_get_all():
    repo.delete(1)
    objects = [Users(pk = i + 1) for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects
