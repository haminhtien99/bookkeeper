"""
Модуль описывает репозиторий, работающий в БД SQLite
"""
import sqlite3
from typing import Any, Optional
from inspect import get_annotations
from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий для работы с БД SQLite
    """
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls

    def add(self, obj: T) -> int:
        names = ', '.join(self.fields.keys())
        set_clause = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            query = f"INSERT INTO {self.table_name} ({names}) VALUES ({set_clause})"
            cur.execute(query, values)
        conn.close()
        return obj.pk

    def get(self, pk: int) -> Optional[T]:
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            names = ', '.join(self.fields.keys())
            query = f"SELECT {names} FROM {self.table_name} WHERE pk = {pk}"
            cur.execute(query)
            row = cur.fetchone()
            if row is None:
                raise ValueError('attempt to get object with unknown primary key')
        conn.close()
        obj_dict = dict(zip(self.fields.keys(), row))
        for field, value in obj_dict.items():
            if not isinstance(value, self.fields[field]):
                # Если тип не соответствует ожидаемому, возвращаем None
                return None
        obj_dict['pk'] = pk
        obj = self.cls(**obj_dict)
        return obj

    def get_all(self,
                where: dict[str, Any] | None = None,
                value_range=False) -> list[T]:
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(f"PRAGMA table_info({self.table_name})")
            columns_info = cur.fetchall()
            column_names = [column[1] for column in columns_info]
            if where is None:
                query = f"SELECT * FROM {self.table_name}"
                cur.execute(query)
                rows = cur.fetchall()
            elif value_range is True:   # Найти значения в определенном диапазоне
                key = next(iter(where.keys()))
                query = f"""
                SELECT * FROM {self.table_name}
                WHERE {key} >=? AND {key} <=?
                """
                cur.execute(query, tuple(where[key]))
                rows = cur.fetchall()
            else:
                keys = [f"{k} = ?" for k in where.keys()]
                query = f"SELECT * FROM {self.table_name} WHERE " + " AND ".join(keys)
                cur.execute(query, tuple(where.values()))
                rows = cur.fetchall()
        conn.close()
        list_obj_dict = []
        for row in rows:
            obj_dict = dict(zip(column_names, row))
            obj_dict['pk'] = row[0]
            obj = self.cls(**obj_dict)
            list_obj_dict.append(obj)
        return list_obj_dict

    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            values = [getattr(obj, x) for x in self.fields]
            set_clause = ', '.join(f'{field} = ?' for field in self.fields.keys())
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE pk = {obj.pk}"
            cur.execute(query, values)
        conn.close()

    def delete(self, pk: int) -> None:
        self.get(pk)
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {self.table_name} WHERE pk = {pk}")
        cur.close()
