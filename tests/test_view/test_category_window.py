"""Тест для окна категорий"""
import pytest
from PySide6 import QtWidgets
from bookkeeper.view.category_window import CategoryWindow
from bookkeeper.models.category import Category
from bookkeeper.repository.memory_repository import MemoryRepository


@pytest.fixture
def category_window(qtbot):
    """Создание окна категорий"""
    cat_repo = MemoryRepository()
    cat1 = Category('Category1', None)
    cat2 = Category('Category2', None)
    cat_repo.add(cat1)
    cat_repo.add(cat2)
    window = CategoryWindow(cat_repo)
    return window


def test_title(category_window):
    """Тест заголовка окна"""
    assert category_window.windowTitle() == 'Категории'


def test_build_tree(category_window):
    """Тест построения дерева"""
    category_window.build_tree()
    assert category_window.tree.topLevelItemCount() == 2


def test_edit_button_click(category_window, qtbot):
    """Тест клика по кнопке редактирования"""
    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, 'Category1')
    category_window.tree.addTopLevelItem(item)
    category_window.tree.setCurrentItem(item)
    category_window.edit_button_click()
    new_name = category_window.edit_dialog.input_field.text()
    if new_name == 'Category2':
        assert category_window.cat_mem_repo.get_all()[0].name == 'Category1'
    assert category_window.cat_mem_repo.get_all()[0].name == new_name


def test_add_button_click(category_window, qtbot):
    """Тест клика по кнопке добавления"""
    item = QtWidgets.QTreeWidgetItem()
    item.setText(0, 'Category1')
    category_window.tree.addTopLevelItem(item)
    category_window.tree.setCurrentItem(item)
    category_window.add_button_click()
    new_name = category_window.add_dialog.input_field.text()
    if new_name.strip():
        if new_name in ['Category1', 'Category']:
            assert len(category_window.cat_mem_repo.get_all()) == 2
        else:
            assert category_window.cat_mem_repo.get_all()[-1].name == new_name
    else:
        assert len(category_window.cat_mem_repo.get_all()) == 2
