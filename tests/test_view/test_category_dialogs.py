"""
Тест для диалогов AddCategoryDialog,
DeleteConfirmationDialog, EditCategoryDialog
"""
import pytest
from PySide6 import QtCore
from PySide6 import QtWidgets
from bookkeeper.view.category_dialogs import (AddCategoryDialog,
                                              DeleteConfirmationDialog,
                                              EditCategoryDialog)


def test_add_category_dialog(qtbot):
    """Тест диалога AddCategoryDialog"""
    dialog = AddCategoryDialog()
    assert dialog.windowTitle() == 'Добавить категорию'
    input_field = dialog.findChild(QtWidgets.QLineEdit)
    assert input_field is not None
    ok_button = dialog.findChild(QtWidgets.QDialogButtonBox)
    assert ok_button is not None
    input_field.setText('New Category')
    assert dialog.get_category_name() == 'New Category'


@pytest.fixture
def setup_delete_confirmation_dialog():
    """Create a dialog for testing"""
    delete_dialog = DeleteConfirmationDialog()
    yield delete_dialog
    delete_dialog.close()


def test_delete_confirmation_dialog(setup_delete_confirmation_dialog, qtbot):
    """Тест диалога DeleteConfirmationDialog"""
    delete_dialog = setup_delete_confirmation_dialog
    assert delete_dialog.windowTitle() == "Delete Confirmation"
    qtbot.mouseClick(delete_dialog.delete_all_children_button, QtCore.Qt.LeftButton)
    assert delete_dialog.choose == "Delete All Children"
    qtbot.mouseClick(delete_dialog.delete_only_this_button, QtCore.Qt.LeftButton)
    assert delete_dialog.choose == "Delete Only This"


@pytest.fixture
def setup_edit_category_dialog():
    """Create a dialog for testing"""
    edit_dialog = EditCategoryDialog(current_name="Current Name")
    yield edit_dialog
    edit_dialog.close()


def test_edit_category_dialog(setup_edit_category_dialog):
    """Тест диалога EditCategoryDialog"""
    edit_dialog = setup_edit_category_dialog
    assert edit_dialog.windowTitle() == "edit category"
    assert edit_dialog.input_field.text() == "Current Name"
    edit_dialog.input_field.setText("New Name")
    edit_dialog.accept()
    assert edit_dialog.get_new_category_name() == "New Name"
