"""
Тесты для категорий расходов
"""
from inspect import isgenerator
import pytest
from bookkeeper.models.category import Category
from bookkeeper.repository.memory_repository import MemoryRepository


@pytest.fixture
def repo():
    """Create a repository for testing"""
    return MemoryRepository()


def test_create_object():
    """Тест создания объекта"""
    cat = Category('name')
    assert cat.name == 'name'
    assert cat.pk == 0
    assert cat.parent is None
    cat = Category(name='name', parent=1, pk=2)
    assert cat.name == 'name'
    assert cat.parent == 1
    assert cat.pk == 2


def test_reassign():
    """
    class should not be frozen
    """
    cat = Category('name')
    cat.name = 'test'
    cat.pk = 1
    assert cat.name == 'test'
    assert cat.pk == 1


def test_eq():
    """
    class should implement __eq__ method
    """
    cat1 = Category(name='name', parent=1, pk=2)
    cat2 = Category(name='name', parent=1, pk=2)
    assert cat1 == cat2


def test_get_parent(repo):
    """"Тест получения родителя"""
    cat1 = Category(name='parent')
    pk = repo.add(cat1)
    cat2 = Category(name='name', parent=pk)
    repo.add(cat2)
    assert cat2.get_parent(repo) == cat1


def test_get_all_parents(repo):
    """Тест получения всех родителей"""
    parent_pk = None
    for i in range(5):
        cat = Category(str(i), parent=parent_pk)
        parent_pk = repo.add(cat)
    gen = cat.get_all_parents(repo)
    assert isgenerator(gen)
    assert [cat.name for cat in gen] == ['3', '2', '1', '0']


def test_get_subcategories(repo: MemoryRepository[Category]):
    """Тест получения подкатегорий"""""
    parent_pk = None
    for i in range(5):
        cat = Category(str(i), parent=parent_pk)
        parent_pk = repo.add(cat)
    cat = repo.get_all({'name': '0'})[0]
    gen = cat.get_subcategories(repo)
    assert isgenerator(gen)
    assert {cat.name for cat in gen} == {'1', '2', '3', '4'}


def test_get_subcategories_complicated(repo: MemoryRepository[Category]):
    """Тест получения подкатегорий сложной структуры"""
    root = Category('0')
    root_pk = repo.add(root)
    repo.add(Category('1', root_pk))
    pk2 = repo.add(Category('2', root_pk))
    repo.add(Category('3', pk2))
    repo.add(Category('4', pk2))
    gen = root.get_subcategories(repo)
    assert isgenerator(gen)
    assert {cat.name for cat in gen} == {'1', '2', '3', '4'}


def test_create_from_tree(repo):
    """Тест создания из дерева"""
    tree = [('parent', None), ('1', 'parent'), ('2', '1')]
    cats = Category.create_from_tree(tree, repo)
    assert len(cats) == len(tree)
    parent = next(cat for cat in cats if cat.name == 'parent')
    assert parent.parent is None
    cat1 = next(cat for cat in cats if cat.name == '1')
    assert cat1.parent == parent.pk
    cat2 = next(cat for cat in cats if cat.name == '2')
    assert cat2.parent == cat1.pk


def test_create_from_tree_error(repo):
    """Тест создания из дерева с ошибкой"""
    tree = [('1', 'parent'), ('parent', None)]
    with pytest.raises(KeyError):
        Category.create_from_tree(tree, repo)
