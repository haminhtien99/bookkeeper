"""Тест для модели Expense"""
from datetime import datetime
import pytest
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.expense import Expense


@pytest.fixture
def repo():
    """Create a repository for testing"""
    return MemoryRepository()


def test_create_with_full_args_list():
    """Test creating a expense with all arguments"""
    exp = Expense(amount=100,
                  category=1,
                  expense_date=datetime.now(),
                  added_date=datetime.now(),
                  comment='test',
                  pk=1)
    assert exp.amount == 100
    assert exp.category == 1


def test_create_brief():
    """Test creating a expense with arguments mount and category"""
    exp = Expense(100, 1)
    assert exp.amount == 100
    assert exp.category == 1


def test_can_add_to_repo(repo):
    """Test adding expense to repo"""
    exp = Expense(100, 1)
    pk = repo.add(exp)
    assert exp.pk == pk
