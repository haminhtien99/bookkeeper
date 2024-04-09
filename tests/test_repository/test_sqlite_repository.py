import pytest
import sqlite3
import os
from bookkeeper.repository.sqlite_repository import SQLiteRepository
def create_db():
    conn = sqlite3.connect('tests/test.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE users")
    cursor.execute("CREATE TABLE IF NOT EXISTS users (pk INTEGER PRIMARY KEY, name STRING, value INTEGER)")
    conn.commit()
    conn.close()
    
class Users:
    name: str = ''
    value: int = 0
    pk: int = 0
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def __eq__(self, other):
        return self.pk == other.pk and self.name == other.name and self.value == other.value
create_db()
test_db = "tests/test.db"
repo = SQLiteRepository(test_db, Users)
def test_add():
    obj = Users(pk=1, name="Test", value=100)
    pk = repo.add(obj)
    assert pk == 1
def test_delete():
    with pytest.raises(ValueError):
        repo.delete(0)
def test_update():
    obj = Users(pk = 0)
    with  pytest.raises(ValueError):
        repo.update(obj)
def test_get():
    pk = 100
    with pytest.raises(ValueError):
        repo.get(pk)
def test_get_all():
    repo.delete(1)
    objects = [Users(pk = i + 1) for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects
