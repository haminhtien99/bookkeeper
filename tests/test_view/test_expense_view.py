"""Тест для виджета расхода в главном окне"""
import pytest
from bookkeeper.view.expense_view import ExpenseView
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense


@pytest.fixture
def expense_view(qtbot):
    """Создание виджета расходов"""
    cat_repo = MemoryRepository()
    cat = Category(name='cat1')
    cat_repo.add(cat)
    exp_repo = MemoryRepository()
    exp = Expense(expense_date='2022-12-25',
                  amount=50.0,
                  category=1,
                  comment='Test Comment')
    exp_repo.add(exp)
    window = ExpenseView(exp_repo, cat_repo)
    qtbot.addWidget(window)
    return window


def test_build_expense_widget(expense_view):
    """Тест построения виджета расходов"""""
    expense_view.build_expense_widget()
    assert expense_view.expense_table.rowCount() == 10


def test_set_data(expense_view):
    """Тест установки данных"""""
    expense_view.set_data()
    assert expense_view.expense_table.item(0, 0).text() == '2022-12-25'


def test_delete_row(expense_view):
    """Тест удаления строки"""
    selected_row = expense_view.expense_table.currentRow()
    expense_view.delete_row()
    if selected_row == 0:
        assert len(expense_view.exp_mem_repo.get_all()) == 0
    else:
        assert len(expense_view.exp_mem_repo.get_all()) == 1


def test_add_expense_dialog(expense_view):
    """Тест диалога добавления расхода"""""
    expense_view.add_expense_dialog()
    expense_date = expense_view.expense_table.item(1, 0).text()
    amount = expense_view.expense_table.item(1, 1).text()
    category = expense_view.expense_table.item(1, 2).text()
    comment = expense_view.expense_table.item(1, 3).text()
    if expense_view.add_dialog.exp is not None:
        exp = expense_view.add_dialog.exp
        assert len(expense_view.exp_mem_repo.get_all()) == 2
        assert expense_view.exp_mem_repo.get_all()[-1] == exp
        assert exp.expense_date == expense_date
        assert exp.amount == float(amount)
        assert expense_view.cat_mem_repo.get(exp.category).name == category
        assert exp.comment == comment
    else:
        assert len(expense_view.exp_mem_repo.get_all()) == 1


def test_is_row_empty(expense_view):
    """Тест проверки пустой ли строка"""
    assert expense_view.is_row_empty(0) is False
