import tempfile
from textwrap import dedent
from datetime import datetime, timedelta
import pytest
import sqlite3
from unittest.mock import Mock
from bookkeeper.utils import (read_tree, 
                              get_day_week_month,
                              create_table_db,
                              get_categories)
from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense
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
def test_get_day_week_month():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = today + timedelta(days=6)
    start_of_month = today.replace(day=1)
    next_month = start_of_month.replace(month=start_of_month.month + 1)
    end_of_month = next_month - timedelta(days=1)
    expected_result = {
        'today': today.strftime('%Y-%m-%d'),
        'this_week': [start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')],
        'this_month': [start_of_month.strftime('%Y-%m-%d'), end_of_month.strftime('%Y-%m-%d')]
    }
    assert get_day_week_month() == expected_result

def test_create_table_db():
    test_db = "test.db"
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




def test_get_categories():
    category1 = Category(name="Category 1", pk=1)
    category2 = Category(name="Category 2", pk=2)
    mock_repo = Mock()
    mock_repo.get_all.return_value = [category1, category2]
    result = get_categories(mock_repo)
    assert result == {"Category 1": 1, "Category 2": 2}
    mock_repo.get_all.assert_called_once()
