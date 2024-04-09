from bookkeeper.view.expense_view import ExpenseView
from bookkeeper.models.expense import Expense
from bookkeeper.repository.memory_repository import MemoryRepository
def test_input_expense(qtbot):
    exp_repo = MemoryRepository[Expense]()
    widget = ExpenseView()
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.amount_line_edit, '123')
    assert widget.amount_line_edit.text() == '123'
    assert widget.get_amount() == 123