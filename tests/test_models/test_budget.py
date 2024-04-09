
import pytest

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_with_full_args_list():
    b = Budget(month = 1000, week  = 100, day = 10 , pk=1)
    assert b.month == 1000
    assert b.week == 100
    assert b.day == 10

    