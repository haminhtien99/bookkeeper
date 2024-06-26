"""
Test utils
"""
import tempfile
from textwrap import dedent
from datetime import datetime, timedelta
import pytest
import sqlite3
from unittest.mock import patch
from PySide6 import QtWidgets
from bookkeeper.utils import (read_tree,
                              get_day_week_month,
                              create_table_db,
                              get_categories,
                              show_warning_dialog,
                              set_data,
                              h_widget_with_label,
                              v_widget_with_label)
from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense
from bookkeeper.repository.memory_repository import MemoryRepository


def test_create_tree():
    text = dedent('''
        parent1
            child1
                grandchild
            child2
        parent2
    ''')
    assert read_tree(text.splitlines()) == [
        ('parent1', None),
        ('child1', 'parent1'),
        ('grandchild', 'child1'),
        ('child2', 'parent1'),
        ('parent2', None)
    ]


def test_ignore_empty_strings():
    text = dedent('''
        parent1
            child1
                grandchild

            child2

        parent2
    ''')
    assert read_tree(text.splitlines()) == [
        ('parent1', None),
        ('child1', 'parent1'),
        ('grandchild', 'child1'),
        ('child2', 'parent1'),
        ('parent2', None)
    ]


def test_indentation_error():
    text = dedent('''
        parent1
            child1
                grandchild
          child2
    ''')
    with pytest.raises(IndentationError):
        read_tree(text.splitlines())


def test_with_file():
    text = dedent('''
        parent1
            child1
                grandchild
            child2
        parent2
    ''')
    with tempfile.TemporaryFile('w+') as f:
        f.write(text)
        f.seek(0)
        assert read_tree(f) == [
            ('parent1', None),
            ('child1', 'parent1'),
            ('grandchild', 'child1'),
            ('child2', 'parent1'),
            ('parent2', None)
        ]


@patch('PySide6.QtWidgets.QMessageBox')
def test_show_warning_dialog(qtbot):
    message = "Test message"
    title = "Warning"
    show_warning_dialog(message=message,
                        title=title)
    assert qtbot.widget(QtWidgets.QMessageBox,
                        title=title, text=message)


def test_set_data(qtbot):
    tableWidget = QtWidgets.QTableWidget()
    tableWidget.setRowCount(2)
    tableWidget.setColumnCount(2)
    data = [['apple', 'banana'], ['orange', 'grape']]
    set_data(tableWidget, data)
    assert tableWidget.rowCount() == len(data)
    assert tableWidget.columnCount() == len(data[0])
    for i, row in enumerate(data):
        for j, x in enumerate(row):
            item = tableWidget.item(i, j)
            assert item is not None
            assert item.text() == x.capitalize()


def test_h_widget_with_label():
    text = "Label Text"
    widget = QtWidgets.QPushButton("Button")
    layout = h_widget_with_label(text, widget)
    assert isinstance(layout, QtWidgets.QHBoxLayout)
    assert layout.count() == 2
    label = layout.itemAt(0).widget()
    assert isinstance(label, QtWidgets.QLabel)
    assert label.text() == text
    button = layout.itemAt(1).widget()
    assert button == widget


def test_v_widget_with_label():
    text = "Label Text"
    widget = QtWidgets.QPushButton("Button")
    layout = v_widget_with_label(text, widget)
    assert isinstance(layout, QtWidgets.QVBoxLayout)
    assert layout.count() == 2
    label = layout.itemAt(0).widget()
    assert isinstance(label, QtWidgets.QLabel)
    assert label.text() == text
    button = layout.itemAt(1).widget()
    assert button == widget


def test_get_day_week_month():
    today = datetime.now().replace(microsecond=0)
    result = get_day_week_month()
    assert isinstance(result, dict)
    assert 'today' in result
    assert 'this_week' in result
    assert 'this_month' in result
    assert result['today'][0] <= today <= result['today'][1]
    for dates in result.values():
        assert len(dates) == 2
        assert isinstance(dates[0], datetime)
        assert isinstance(dates[1], datetime)
        assert dates[0] <= dates[1]


def test_create_table_db():
    test_db = "tests/test.db"
    create_table_db(test_db, cls=Category)
    create_table_db(test_db, cls=Budget)
    create_table_db(test_db, cls=Expense)
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    assert 'budget' in table_names
    assert 'category' in table_names
    assert 'expense' in table_names
    cursor.execute("PRAGMA table_info(budget);")
    budget_columns = cursor.fetchall()
    assert len(budget_columns) == 4
    cursor.execute("PRAGMA table_info(category);")
    category_columns = cursor.fetchall()
    assert len(category_columns) == 3
    cursor.execute("PRAGMA table_info(expense);")
    expense_columns = cursor.fetchall()
    assert len(expense_columns) == 6
    conn.commit()
    conn.close()


@pytest.fixture
def repo():
    category1 = Category(name="Category 1")
    category2 = Category(name="Category 2")
    repo = MemoryRepository()
    repo.add(category1)
    repo.add(category2)
    return repo


def test_get_categories(repo):
    result = get_categories(repo)
    assert result == ["Category 1", "Category 2"]

