"""Тест диалога задания бюджета"""
import pytest
from bookkeeper.view.set_budget_dialog import SetBudgetDialog
from bookkeeper.models.budget import Budget


@pytest.fixture
def dialog(qtbot):
    """Создание диалогового окна"""""
    budget = Budget(month=1000, week=250, day=50)
    dialog = SetBudgetDialog(budget)
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_initialization(dialog):
    """Тест инициализации диалогового окна"""
    assert dialog.windowTitle() == 'Задать бюджет'
    assert dialog.edit_budget_daily.text() == '50'
    assert dialog.edit_budget_weekly.text() == '250'
    assert dialog.edit_budget_monthly.text() == '1000'


def test_validation_invalid_data(dialog, qtbot):
    """Тест валидации неверных данных"""""
    qtbot.keyClicks(dialog.edit_budget_daily, '-70')
    qtbot.keyClicks(dialog.edit_budget_weekly, '300')
    qtbot.keyClicks(dialog.edit_budget_monthly, '1200')
    dialog.apply_button_click()
    assert dialog.budget.day == 50


def test_validation_valid_data(dialog, qtbot):
    """Тест валидации верных данных"""
    dialog.edit_budget_daily.clear()
    dialog.edit_budget_weekly.clear()
    dialog.edit_budget_monthly.clear()
    qtbot.keyClicks(dialog.edit_budget_daily, '70')
    qtbot.keyClicks(dialog.edit_budget_weekly, '300')
    qtbot.keyClicks(dialog.edit_budget_monthly, '1200')
    dialog.apply_button_click()
    assert dialog.budget.day == float(70)
    assert dialog.budget.week == float(300)
    assert dialog.budget.month == float(1200)
