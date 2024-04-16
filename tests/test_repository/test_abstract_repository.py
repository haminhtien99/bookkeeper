"""
Тест для AbstractRepository
"""
import pytest
from bookkeeper.repository.abstract_repository import AbstractRepository


def test_cannot_create_abstract_repository():
    """Test cannot create abstract repository"""
    with pytest.raises(TypeError):
        AbstractRepository()


def test_can_create_subclass():
    """Test can create subclass"""
    class Test(AbstractRepository):
        """AbstractRepository Test """
        def add(self, obj):
            pass
        def get(self, pk):
            pass
        def get_all(self, where=None):
            pass
        def update(self, obj):
            pass
        def delete(self, pk):
            pass

    test = Test()
    assert isinstance(test, AbstractRepository)
