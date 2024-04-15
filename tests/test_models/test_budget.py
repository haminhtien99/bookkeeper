"""
Тест модели Budget
"""
import pytest
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget


@pytest.fixture
def repo():
    """Create a repository for testing"""
    return MemoryRepository()


def test_create_with_full_args_list():
    """Test creating a budget with all arguments"""
    buget = Budget(month=1000, week=100, day=10, pk=1)
    assert buget.month == 1000
    assert buget.week == 100
    assert buget.day == 10
