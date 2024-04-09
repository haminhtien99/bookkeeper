import pytest
import sqlite3
import os
from typing import Any
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.repository.memory_repository import MemoryRepository

@pytest.fixture
def temp_db():
    # Create an in-memory database for testing
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Create your table(s) here
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cutom (
            pk INTEGER PRIMARY KEY,
            value1 TEXT,
            value2 TEXT
        )
    """)
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
    print(obj)
    with pytest.raises(ValueError):
        repo.add(obj)


# def test_cannot_add_with_pk(repo, custom_class):
#     obj = custom_class()
#     obj.pk = 1
#     with pytest.raises(ValueError):
#         repo.add(obj)


# def test_cannot_add_without_pk(repo):
#     with pytest.raises(ValueError):
#         repo.add(0)


# def test_cannot_delete_unexistent(repo):
#     with pytest.raises(KeyError):
#         repo.delete(1)


# def test_cannot_update_without_pk(repo, custom_class):
#     obj = custom_class()
#     with pytest.raises(ValueError):
#         repo.update(obj)


# def test_get_all(repo, custom_class):
#     objects = [custom_class() for i in range(5)]
#     for o in objects:
#         repo.add(o)
#     assert repo.get_all() == objects


# def test_get_all_with_condition(repo, custom_class):
#     objects = []
#     for i in range(5):
#         o = custom_class()
#         o.name = str(i)
#         o.test = 'test'
#         repo.add(o)
#         objects.append(o)
#     assert repo.get_all({'name': '0'}) == [objects[0]]
#     assert repo.get_all({'test': 'test'}) == objects

