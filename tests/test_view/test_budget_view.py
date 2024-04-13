import sys
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import MagicMock
from bookkeeper.view.budget_view import BudgetView

@pytest.fixture
def budget_view(qtbot, mocker):
    # Mock repositories
    budget = MagicMock()
    exp_mem_repo_mock = MagicMock()

    # Create budget view
    view = BudgetView(budget, exp_mem_repo_mock)
    view.setWindowTitle('Set Budget')
    view.show()

    yield view

    # Close the window after the test
    view.close()

def test_budget_view_title(budget_view):
    assert budget_view.windowTitle() == 'Set Budget'

def test_budget_view_visibility(budget_view):
    assert budget_view.isVisible()

def test_update_budget_column(budget_view):
    # Set the return values of MagicMock objects
    budget_view.budget.day.return_value = '0'
    budget_view.budget.week.return_value = '0'
    budget_view.budget.month.return_value = '0'

    # Call the method to update the budget column
    budget_view.update_budget_column()

    # Check if the QTableWidgetItem objects have the expected text
    assert budget_view.budget_table.item(0, 1).text() == '0'
    assert budget_view.budget_table.item(1, 1).text() == '0'
    assert budget_view.budget_table.item(2, 1).text() == '0'

# Add more tests as needed

if __name__ == '__main__':
    # Initialize QApplication
    app = QApplication(sys.argv)

    # Run the tests
    pytest.main(args=sys.argv)

    # Exit the application
    sys.exit(app.exec())
