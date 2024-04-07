"""
Вспомогательные функции
"""

from typing import Iterable, Iterator
from bookkeeper.models.budget import Budget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import T
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QTableWidgetItem, QMessageBox)
from datetime import datetime, timedelta
import sqlite3


def _get_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _lines_with_indent(lines: Iterable[str]) -> Iterator[tuple[int, str]]:
    for line in lines:
        if not line or line.isspace():
            continue
        yield _get_indent(line), line.strip()


def read_tree(lines: Iterable[str]) -> list[tuple[str, str | None]]:
    """
    Прочитать структуру дерева из текста на основе отступов. Вернуть список
    пар "потомок-родитель" в порядке топологической сортировки. Родитель
    элемента верхнего уровня - None.

    Пример. Следующий текст:
    parent
        child1
            child2
        child3

    даст такое дерево:
    [('parent', None), ('child1', 'parent'),
     ('child2', 'child1'), ('child3', 'parent')]

    Пустые строки игнорируются.

    Parameters
    ----------
    lines - Итерируемый объект, содержащий строки текста (файл или список строк)

    Returns
    -------
    Список пар "потомок-родитель"
    """
    parents: list[tuple[str | None, int]] = []
    last_indent = -1
    last_name = None
    result: list[tuple[str, str | None]] = []
    for i, (indent, name) in enumerate(_lines_with_indent(lines)):
        if indent > last_indent:
            parents.append((last_name, last_indent))
        elif indent < last_indent:
            while indent < last_indent:
                _, last_indent = parents.pop()
            if indent != last_indent:
                raise IndentationError(
                    f'unindent does not match any outer indentation '
                    f'level in line {i}:\n'
                )
        result.append((name, parents[-1][0]))
        last_name = name
        last_indent = indent
    return result


def show_warning_dialog(message: str, title:str = 'Warning')-> None:
    """Отображает диалог предупреждения."""
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()

def set_data(tableWidget, data: list[list[str]])->None:
    """
    Устанавливает данные в таблицу.
    """
    for i, row in enumerate(data):
        for j, x in enumerate(row):
            tableWidget.setItem(i, j, QTableWidgetItem(x.capitalize()))

def h_widget_with_label(text:str, widget:QWidget)->QHBoxLayout:
    """
    Возвращает горизонтальную раскладку, содержащую текст и виджет.
    """
    hl = QHBoxLayout()
    hl.addWidget(QLabel(text))
    hl.addWidget(widget)
    return hl
def v_widget_with_label(text:str, widget:QWidget)->QVBoxLayout:
    """
    Возвращает вертикальную раскладку, содержащую текст и виджет.
    """
    hl = QVBoxLayout()
    hl.addWidget(QLabel(text))
    hl.addWidget(widget)
    return hl

def get_day_week_month():
    """
    Возвращает текущий день, неделю и месяц.
    """
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = today + timedelta(days=6)

    start_of_month = today.replace(day=1)
    next_month = start_of_month.replace(month =start_of_month.month+ 1)
    end_of_month = next_month - timedelta(days = 1)
    return {'today':today.strftime('%Y-%m-%d'),
            'this_week': [start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')],
            'this_month': [start_of_month.strftime('%Y-%m-%d'), end_of_month.strftime('%Y-%m-%d')]}

