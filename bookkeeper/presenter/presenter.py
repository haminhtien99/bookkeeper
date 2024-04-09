"""
Главное окно приложения.
"""
import sys
from PySide6 import QtWidgets
from bookkeeper.utils import h_widget_with_label
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.view.category_view import (CategoryWindow,
                                           get_categories)
from bookkeeper.view.budget_view import BudgetView
from bookkeeper.view.expense_view import ExpenseView
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.utils import show_warning_dialog
class MainWindow(QtWidgets.QWidget):
    """
    Главное окно приложения.
    """
    def __init__(self,
                 exp_repo:SQLiteRepository,
                 budget_repo:SQLiteRepository,
                 cat_repo: SQLiteRepository) ->None:
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.expense_widget = ExpenseView(exp_repo= exp_repo,
                                          cat_repo = cat_repo)
        self.cat_repo = cat_repo
        self.layout.addWidget(self.expense_widget)
        self.budget_widget = BudgetView(budget_repo)
        self.budget_widget.from_expense_repo(exp_repo)
        self.expense_widget.expense_table.itemChanged.connect(self.update_budget_table)
        self.layout.addWidget(self.budget_widget)
        edit_category_button = QtWidgets.QPushButton('Редактировать категории')
        edit_category_button.clicked.connect(self.edit_category_dialog)
        self.layout.addWidget(edit_category_button)
        self.ls_categories = get_categories(self.cat_repo).keys()
        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(self.ls_categories)
        self.layout.addLayout(h_widget_with_label('Категории', self.combobox))
        save_button = QtWidgets.QPushButton('Save')
        save_button.clicked.connect(self.save_button_click)
        self.layout.addWidget(save_button)
        self.setLayout(self.layout)
        self.main_changes = []
    def update_budget_table(self):
        """
        Обновляет таблицу бюджета при изменении таблицы расходов.
        """
        self.budget_widget.from_expense_widget_table(self.expense_widget.expense_table)
    def edit_category_dialog(self):
        """
        Редактировать категории
        """
        category_window = CategoryWindow(self.cat_repo)
        save_button_category = QtWidgets.QPushButton('Save')
        save_button_category.clicked.connect(category_window.save_button_click)
        save_button_category.clicked.connect(self.update_expense_table)
        save_button_category.clicked.connect(self.update_category_list)
        category_window.layout.addWidget(save_button_category)
        category_window.show()
    def save_button_click(self):
        """
        Сохранить изменения MainWindow
        """
        if len(self.expense_widget.changes) == 0 and self.expense_widget.changes is None:
            show_warning_dialog(message='Нет изменений', title = 'Сохранение')
        else:
            self.expense_widget.save_button_click()
            self.budget_widget.save_button_click()
            show_warning_dialog(message='Успешно сохранить', title= 'Сохранение')
    def update_expense_table(self):
        """
        Обновляет таблицу расходов
        """
        self.expense_widget.build_expense_widget()
    def update_category_list(self):
        """
        Обновляет список категорий
        """
        self.ls_categories = get_categories(self.cat_repo).keys()
        self.combobox.addItems(self.ls_categories)
budget_repo = SQLiteRepository(db_file = 'bookkeeper/view/new_database.db', cls = Budget)
expense_repo = SQLiteRepository(db_file = 'bookkeeper/view/new_database.db', cls = Expense)
category_repo = SQLiteRepository(db_file = 'bookkeeper/view/new_database.db', cls = Category)
expense_repo.create_table_db()
budget_repo.create_table_db()
category_repo.create_table_db()
app = QtWidgets.QApplication(sys.argv)
window = MainWindow(budget_repo=budget_repo, exp_repo=expense_repo, cat_repo=category_repo)
window.setWindowTitle('The Bookkeeper')
window.resize(500, 800)
window.show()
sys.exit(app.exec())
