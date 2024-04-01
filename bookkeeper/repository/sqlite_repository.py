"""
Модуль описывает репозиторий, работающий в БД SQLite
"""
import sqlite3
from itertools import count
from typing import Any, cast

from bookkeeper.repository.abstract_repository import AbstractRepository, T

from inspect import get_annotations
class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str = True)
        self.fields.pop('pk')
    def add(self, obj: T) -> int:
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f"INSERT INTO {self.table_name} ({names}) VALUES ({p})", values)
        cur.close()
        return obj.pk
    def get(self, pk: int) -> T | None:
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            names = ', '.join(self.fields.keys())
            query = f"SELECT {names} FROM {self.table_name} WHERE pk = {pk}"
            print(query)
            cur.execute(query)
            row = cur.fetchone()
            if row is None:
                return None
        cur.close()
        obj_dict = dict(zip(self.fields.keys(), row))
        for field, value in obj_dict.items():
            if not isinstance(value, self.fields[field]):
                # Если тип не соответствует ожидаемому, возвращаем None
                return None
        obj_dict['pk'] = pk
        
        return obj_dict

    def get_all(self, where: dict[str, Any]|None = None)->list[T]:
        
        with sqlite3.connect(self.db_file) as conn:
            if where is None:
                cur = conn.cursor()
                query = f"SELECT * FROM {self.table_name}"
                cur.execute(query)
                rows = cur.fetchall()
            else:
                cur = conn.cursor()
                query = f"SELECT * FROM {self.table_name} WHERE " + " AND ".join([f"{k} = ?" for k in where.keys()])
                cur.execute(query, tuple(where.values()))
                rows = cur.fetchall()
        cur.close()
        return rows
    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            values = [getattr(obj, x) for x in self.fields]
            names = ", ".join(self.fields.keys())
            query =f"UPDATE {self.table_name} SET {names} WHERE pk = {obj.pk}"
            cur.execute(query, values)
        cur.close()
    def delete(self,pk: int)-> None:
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {self.table_name} WHERE pk = {pk}")
        cur.close()

# class Users:
#     pk:int
#     def __init__(self, pk, username, email):
#         self.pk = pk
# repository:SQLiteRepository[Users]  = SQLiteRepository('/home/ha/Desktop/semester-10/Python/example.db', Users)
# print(type(repository.get(1)))


