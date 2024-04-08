import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QDialog, QPushButton
from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent

from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.view.category_view import CategoryWindow, list_category_widget
from bookkeeper.view.budget_view import BudgetView
from bookkeeper.view.expense_view import ExpenseView
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.utils import show_warning_dialog
from functools import partial
from typing import Optional

class MainWindow(QWidget):
    """
    Главное окно приложения.
    """
    def __init__(self, 
                 exp_repo:SQLiteRepository, 
                 budget_repo:SQLiteRepository, 
                 cat_repo: SQLiteRepository)->None:
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.expense_widget = ExpenseView(exp_repo= exp_repo, 
                                          cat_repo = cat_repo)
        self.layout.addWidget(self.expense_widget)

        self.budget_widget = BudgetView(budget_repo)
        self.budget_widget.from_expense_repo(exp_repo)
        self.expense_widget.expense_table.itemChanged.connect(self.update_budget_table)
        self.layout.addWidget(self.budget_widget)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_button_click)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)
        self.main_changes = []    
    def update_budget_table(self):
        """
        Обновляет таблицу бюджета при изменении таблицы расходов.
        """
        
        self.budget_widget.from_expense_widget_table(self.expense_widget.expense_table)
    def save_button_click(self):
        """
        Сохранить изменения MainWindow
        """
        if len(self.expense_widget.changes) == 0 and self.expense_widget.change is None:
            show_warning_dialog(message='Нет изменений', title = 'Сохранение')
        else:
            self.expense_widget.save_button_click()
            self.budget_widget.save_button_click()
            show_warning_dialog(message='Успешно сохранить', title= 'Сохранение')


budget_repo = SQLiteRepository(db_file = 'bookkeeper/view/new_database.db', cls = Budget)
exp_repo = SQLiteRepository(db_file = 'bookkeeper/view/new_database.db', cls = Expense)
cat_repo = SQLiteRepository('bookkeeper/view/new_database.db', Category)
app = QApplication(sys.argv)
window = MainWindow(budget_repo=budget_repo, exp_repo=exp_repo, cat_repo=cat_repo)
window.setWindowTitle('The Bookkeeper')
window.resize(500, 500)
window.show()

sys.exit(app.exec())