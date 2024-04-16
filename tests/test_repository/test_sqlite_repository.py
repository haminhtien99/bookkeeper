"""
Тест для SQLiteRepository
"""
import sqlite3
import pytest
from typing import Any
from bookkeeper.repository.sqlite_repository import SQLiteRepository


def create_db() -> None:
    """Создать базу данных для тестирования"""
    conn = sqlite3.connect('tests/test.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE users")
    query = '''CREATE TABLE IF NOT EXISTS users (pk INTEGER PRIMARY KEY,
    name STRING,
    value INTEGER)'''
    cursor.execute(query)
    conn.commit()
    conn.close()


class Users:
    """Класс для тестирования"""
    name: str = ''
    value: int = 0
    pk: int = 0

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __eq__(self, other: Any) -> Any:
        return self.pk == other.pk and \
            self.name == other.name and \
            self.value == other.value


create_db()

TEST_DB = "tests/test.db"

repo = SQLiteRepository(TEST_DB, Users)


def test_add() -> None:
    """Тест добавления"""
    obj = Users(pk=1, name="Test", value=100)
    pk = repo.add(obj)
    assert pk == 1


def test_delete() -> None:
    """Тест удаления"""
    with pytest.raises(ValueError):
        repo.delete(0)


def test_update() -> None:
    """Тест обновления"""
    obj = Users(pk=0)
    with pytest.raises(ValueError):
        repo.update(obj)


def test_get() -> None:
    """Тест получения"""""
    pk = 100
    with pytest.raises(ValueError):
        repo.get(pk)


def test_get_all() -> None:
    """Тест получения всех"""
    repo.delete(1)
    objects = [Users(pk=i + 1) for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects
