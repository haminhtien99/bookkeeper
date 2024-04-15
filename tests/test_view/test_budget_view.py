"""
Тест для класса BudgetView
"""
import pytest
from bookkeeper.view.budget_view import BudgetView
from bookkeeper.models.budget import Budget
from bookkeeper.repository.memory_repository import MemoryRepository


@pytest.fixture
def budget_view():
    """Create a BudgetView for testing"""
    budget = Budget()
    exp_mem_repo_mock = MemoryRepository()
    view = BudgetView(budget, exp_mem_repo_mock)
    view.setWindowTitle('Set Budget')
    view.show()
    yield view
    view.close()


def test_budget_view_title(budget_view, qtbot):
    """Test BudgetView title"""""
    assert budget_view.windowTitle() == 'Set Budget'


def test_budget_view_visibility(budget_view, qtbot):
    """Test BudgetView visibility"""
    assert budget_view.isVisible()


def test_show_budget_widget(budget_view, qtbot):
    """Test BudgetView show_budget_widget"""
    budget_view.show_budget_widget()
    assert budget_view.budget_table.rowCount() == 3
    assert budget_view.budget_table.columnCount() == 2


def test_update_budget_column(budget_view, qtbot):
    """Test BudgetView update_budget_column"""
    budget_view.budget.day = 1
    budget_view.budget.week = 2
    budget_view.budget.month = 3
    budget_view.update_budget_column()
    assert budget_view.budget_table.item(0, 1).text() == '1'
    assert budget_view.budget_table.item(1, 1).text() == '2'
    assert budget_view.budget_table.item(2, 1).text() == '3'
