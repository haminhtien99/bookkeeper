"""
Главное окно приложения.
"""
import sys
from typing import List
from PySide6 import QtWidgets
from bookkeeper.utils import (h_widget_with_label,
                              show_warning_dialog,
                              create_table_db,
                              get_categories)
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.view.category_view import CategoryWindow
from bookkeeper.view.budget_view import BudgetView
from bookkeeper.view.expense_view import ExpenseView
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
class MainWindow(QtWidgets.QMainWindow):
    """
    Главное окно приложения.
    """
    def __init__(self,
                 exp_sql_repo: AbstractRepository[Expense],
                 budget_sql_repo: AbstractRepository[Budget],
                 cat_sql_repo: AbstractRepository[Category]) ->None:
        super().__init__()
        self.setWindowTitle('The Bookkeeper')
        self.setGeometry(100, 100, 400, 200)
        centralWidget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout()
        self.exp_sql_repo = exp_sql_repo
        self.cat_sql_repo = cat_sql_repo
        self.budget_sql_repo = budget_sql_repo
        exp_mem_repo = MemoryRepository[Expense]()
        cat_mem_repo = MemoryRepository[Expense]()
        for exp in exp_sql_repo.get_all():
            exp.pk = 0
            exp_mem_repo.add(exp)
        for exp in cat_sql_repo.get_all():
            exp.pk = 0
            cat_mem_repo.add(exp)
        budget = Budget()
        if len(budget_sql_repo.get_all()) > 0:
            budget = budget_sql_repo.get(1)
        self.expense_widget = ExpenseView(exp_mem_repo=exp_mem_repo,
                                          cat_mem_repo=cat_mem_repo)
        self.layout.addWidget(self.expense_widget)
        self.budget_widget = BudgetView(budget, exp_mem_repo)
        self.expense_widget.expenseEdited.connect(self.update_budget_table)
        self.layout.addWidget(self.budget_widget)
        edit_category_button = QtWidgets.QPushButton('Редактировать категории')
        edit_category_button.clicked.connect(self.edit_category_dialog)
        self.category_window = CategoryWindow(cat_mem_repo)
        self.category_window.categoryEdited.connect(self.update_expense_table)
        self.category_window.categoryEdited.connect(self.update_category_list)
        self.layout.addWidget(edit_category_button)
        self.ls_categories = get_categories(cat_mem_repo).keys()
        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(self.ls_categories)
        self.layout.addLayout(h_widget_with_label('Категории', self.combobox))
        save_button = QtWidgets.QPushButton('Save')
        save_button.clicked.connect(self.save_button_click)
        self.layout.addWidget(save_button)
        centralWidget.setLayout(self.layout)
        self.setCentralWidget(centralWidget)
        self.budget_widget.check_warning_budget()
    def update_budget_table(self):
        """
        Обновляет таблицу бюджета при изменении таблицы расходов.
        """
        self.budget_widget.update_expense_column(self.expense_widget.exp_mem_repo)
        self.budget_widget.check_warning_budget()
    def edit_category_dialog(self):
        """
        Редактировать категории
        """
        self.category_window.show()
    def update_expense_table(self):
        """
        Обновляет таблицу расходов после обновления репозитории категорий
        """
        if len(self.category_window.deleted_cat) > 0:
            deleted_rows = []
            for i, exp in enumerate(self.expense_widget.exp_mem_repo.get_all()):
                if exp.category in self.category_window.deleted_cat:
                    deleted_rows.append(i)
                    self.expense_widget.expense_table.removeRow(i)
                    self.expense_widget.exp_mem_repo.delete(pk = exp.pk)
            deleted_rows.sort(reverse=True)  
            for i in deleted_rows:
                self.expense_widget.expense_table.removeRow(i)
            self.category_window.deleted_cat = []
        for exp in self.expense_widget.exp_mem_repo.get_all():
            for pk_del in self.category_window.deleted_cat:
                if exp.category > pk_del:
                    exp.category -= 1
            self.expense_widget.exp_mem_repo.update(exp)
        self.expense_widget.cat_mem_repo = self.category_window.cat_mem_repo
        self.expense_widget.set_data()
        self.budget_widget.update_expense_column(self.expense_widget.exp_mem_repo)
        self.budget_widget.check_warning_budget()
    def update_category_list(self):
        """
        Обновляет список категорий
        """
        self.combobox.clear()
        self.ls_categories = get_categories(self.category_window.cat_mem_repo).keys()
        self.combobox.addItems(self.ls_categories)
    def save_button_click(self):
        """
        Сохранить изменения MainWindow
        """
        self.save_cat_repo()
        self.save_budget_repo()
        self.save_exp_repo()
        show_warning_dialog(message='Saved')
    def save_cat_repo(self) -> None:
        """
        Save category
        """
        if len(self.cat_sql_repo.get_all()) > 0:
            for cat in self.cat_sql_repo.get_all():
                self.cat_sql_repo.delete(cat.pk)
        for cat in self.category_window.cat_mem_repo.get_all():
            self.cat_sql_repo.add(cat)
    def save_exp_repo(self):
        """
        Save expense table
        """
        if len(self.exp_sql_repo.get_all()) > 0:
            for exp in self.exp_sql_repo.get_all():
                self.exp_sql_repo.delete(exp.pk)
        for exp in self.expense_widget.exp_mem_repo.get_all():
            exp.pk = 0
            self.exp_sql_repo.add(exp)
    def save_budget_repo(self):
        """
        Save budget table
        """
        if len(self.budget_sql_repo.get_all()) > 0:
            for budget in self.budget_sql_repo.get_all():
                self.budget_sql_repo.delete(budget.pk)
        self.budget_sql_repo.add(self.budget_widget.budget)
if __name__ == '__main__':
    """
    Программа запускается
    """
    DB_FILE = 'bookkeeper/view/new_database.db'
    budget_repo = SQLiteRepository(db_file=DB_FILE, cls=Budget)
    expense_repo = SQLiteRepository(db_file=DB_FILE, cls = Expense)
    category_repo = SQLiteRepository(db_file=DB_FILE, cls = Category)
    create_table_db(db_file=DB_FILE, cls=Budget) # if table is not existing
    create_table_db(db_file=DB_FILE, cls=Expense)
    create_table_db(db_file=DB_FILE, cls=Category)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(budget_sql_repo=budget_repo,
                        exp_sql_repo=expense_repo,
                        cat_sql_repo=category_repo)
    window.setWindowTitle('The Bookkeeper')
    window.resize(500, 800)
    window.show()
    sys.exit(app.exec())
