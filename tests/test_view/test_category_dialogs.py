"""
Тест для диалогов AddCategoryDialog, 
DeleteConfirmationDialog, EditCategoryDialog
"""
import pytest
import sys
from PySide6 import QtCore
from PySide6 import QtWidgets
from bookkeeper.view.category_dialogs import (AddCategoryDialog,
                                              DeleteConfirmationDialog, 
                                              EditCategoryDialog)
@pytest.fixture
def setup_add_category_dialog():
    app = QtWidgets.QApplication(sys.argv)
    add_dialog = AddCategoryDialog()
    yield add_dialog
    add_dialog.close()
    del app
def test_add_category_dialog(setup_add_category_dialog):
    add_dialog = setup_add_category_dialog
    assert add_dialog.windowTitle() == "Добавить категорию"
    assert add_dialog.input_field.text() == ""
    add_dialog.input_field.setText("New Category")
    add_dialog.accept()
    assert add_dialog.get_category_name() == "New Category"

@pytest.fixture(scope="module")
def app():
    application = QtWidgets.QApplication(sys.argv)
    yield application
    application.quit()
@pytest.fixture
def setup_delete_confirmation_dialog():
    delete_dialog = DeleteConfirmationDialog()
    yield delete_dialog
    delete_dialog.close()
def test_delete_confirmation_dialog(setup_delete_confirmation_dialog, qtbot):
    delete_dialog = setup_delete_confirmation_dialog
    assert delete_dialog.windowTitle() == "Delete Confirmation"
    qtbot.mouseClick(delete_dialog.delete_all_children_button, QtCore.Qt.LeftButton)
    assert delete_dialog.result == "Delete All Children"
    qtbot.mouseClick(delete_dialog.delete_only_this_button, QtCore.Qt.LeftButton)
    assert delete_dialog.result == "Delete Only This"

@pytest.fixture(scope="module")
def app():
    application = QtWidgets.QApplication(sys.argv)
    yield application
    application.quit()
@pytest.fixture
def setup_edit_category_dialog():
    edit_dialog = EditCategoryDialog(current_name="Current Name")
    yield edit_dialog
    edit_dialog.close()
def test_edit_category_dialog(setup_edit_category_dialog):
    edit_dialog = setup_edit_category_dialog
    assert edit_dialog.windowTitle() == "edit category"
    assert edit_dialog.input_field.text() == "Current Name"
    edit_dialog.input_field.setText("New Name")
    edit_dialog.accept()
    assert edit_dialog.get_new_category_name() == "New Name"
    