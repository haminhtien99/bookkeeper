"""Тест для диалогов изменения расходов"""
import pytest
from bookkeeper.view.change_expense_dialog import ChangeExpenseDialog
from bookkeeper.models.category import Category
from bookkeeper.repository.memory_repository import MemoryRepository
from PySide6 import QtWidgets
from datetime import datetime


@pytest.fixture
def dialog(qtbot):
    """Создание диалогового окна"""
    cat_repo = MemoryRepository()
    cat = Category(name='cat1')
    cat_repo.add(cat)
    title = "Add Expense"
    exp = None
    dialog = ChangeExpenseDialog(cat_repo, title, exp)
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_initialization(dialog):
    """Тест инициализации диалогового окна"""
    assert dialog.windowTitle() == "Add Expense"
    assert dialog.amount_line_edit.text() == ''
    assert dialog.combobox.count() == 1
    assert dialog.comment_line_edit.text() == ''


def test_auto_fill_date(dialog):
    """Тест автоматического заполнения даты"""
    dialog.auto_fill_date()
    assert dialog.expense_date_line_edit.text() == datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def test_apply_change(dialog):
    """Тест применения изменений"""
    dialog.amount_line_edit.setText('50')
    dialog.expense_date_line_edit.setText('2022-12-25 12:00:00')
    dialog.combobox.setCurrentIndex(0)
    dialog.apply_change()
    assert dialog.result() == QtWidgets.QDialog.Accepted
