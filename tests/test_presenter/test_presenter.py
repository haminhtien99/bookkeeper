import sys
from PySide6.QtWidgets import QApplication
from PySide6 import QtWidgets
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from unittest.mock import MagicMock
from bookkeeper.presenter.presenter import MainWindow

def test_main_window(qtbot, mocker):
    # Mock repositories
    exp_sql_repo_mock = MagicMock()
    budget_sql_repo_mock = MagicMock()
    cat_sql_repo_mock = MagicMock()

    # Create main window
    window = MainWindow(exp_sql_repo=exp_sql_repo_mock,
                        budget_sql_repo=budget_sql_repo_mock,
                        cat_sql_repo=cat_sql_repo_mock)
    window.show()
    # Test window title
    assert window.windowTitle() == 'The Bookkeeper'

    # Test widget visibility
    assert window.isVisible()

    # Test widget layout
    assert window.layout().count() == 5 # Assuming 5 widgets are added in the layout

    # Test edit category button functionality
    mocker.patch.object(window, 'edit_category_dialog')
    QTest.mouseClick(window.findChild(QtWidgets.QPushButton, 'edit_category_button'), Qt.LeftButton)
    window.edit_category_dialog.assert_called_once()

    # Test save button functionality
    mocker.patch.object(window, 'save_button_click')
    QTest.mouseClick(window.findChild(QtWidgets.QPushButton, 'save_button'), Qt.LeftButton)
    window.save_button_click.assert_called_once()

    # Test combo box functionality
    combo_box = window.findChild(QtWidgets.QComboBox, 'combobox')
    combo_box.setCurrentIndex(0)
    assert combo_box.currentText() == combo_box.itemText(0)

    # Close the window
    window.close()

if __name__ == '__main__':
    # Initialize QApplication
    app = QApplication(sys.argv)

    # Run the tests
    test_main_window()

    # Exit the application

    sys.exit(app.exec())