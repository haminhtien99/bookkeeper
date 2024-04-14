import pytest
from PySide6 import QtWidgets
from PySide6 import QtCore
from bookkeeper.view.set_budget_dialog import SetBudgetDialog
from bookkeeper.models.budget import Budget
@pytest.fixture(scope="module")
def app():
    application = QtWidgets.QApplication([])
    yield application
    application.quit()
@pytest.fixture
def setup_set_budget_dialog():
    budget = Budget(day=50, week=300, month=1000)
    set_budget_dialog = SetBudgetDialog(budget)
    yield set_budget_dialog
    set_budget_dialog.close()
def test_set_budget_dialog(setup_set_budget_dialog, qtbot):
    set_budget_dialog = setup_set_budget_dialog
    assert set_budget_dialog.windowTitle() == "Задать бюджет"
    assert set_budget_dialog.edit_budget_daily.text() == "50"
    assert set_budget_dialog.edit_budget_weekly.text() == "300"
    assert set_budget_dialog.edit_budget_monthly.text() == "1000"
