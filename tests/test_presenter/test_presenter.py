import sys
from PySide6.QtWidgets import QApplication
from unittest.mock import MagicMock
from bookkeeper.presenter.presenter import MainWindow
def test_main_window(qtbot, mocker):
    exp_sql_repo_mock = MagicMock()
    budget_sql_repo_mock = MagicMock()
    cat_sql_repo_mock = MagicMock()
    window = MainWindow(exp_sql_repo=exp_sql_repo_mock,
                        budget_sql_repo=budget_sql_repo_mock,
                        cat_sql_repo=cat_sql_repo_mock)
    window.show()
    assert window.windowTitle() == 'The Bookkeeper'
    assert window.isVisible()
    assert window.layout.count() == 5 
    window.close()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    test_main_window()
    sys.exit(app.exec())