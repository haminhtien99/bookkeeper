"""
Главное окно приложения.
"""
import sys
from datetime import datetime
from PySide6 import QtWidgets
from bookkeeper.utils import (h_widget_with_label,
                              show_warning_dialog,
                              create_table_db,
                              get_categories)
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.view.category_window import CategoryWindow
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
                 cat_sql_repo: AbstractRepository[Category]) -> None:
        super().__init__()
        self.setWindowTitle('The Bookkeeper')
        self.setGeometry(100, 100, 400, 200)
        centralWidget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        self.exp_sql_repo = exp_sql_repo
        self.cat_sql_repo = cat_sql_repo
        self.budget_sql_repo = budget_sql_repo
        exp_mem_repo = MemoryRepository[Expense]()
        cat_mem_repo = MemoryRepository[Category]()
        for exp in exp_sql_repo.get_all():
            exp.pk = 0
            if isinstance(exp.added_date, str):
                exp.added_date = datetime.strptime(exp.added_date,
                                                   '%Y-%m-%d %H:%M:%S')
            if isinstance(exp.expense_date, str):
                exp.expense_date = datetime.strptime(exp.expense_date,
                                                     '%Y-%m-%d %H:%M:%S')
            exp_mem_repo.add(exp)
        for cat in cat_sql_repo.get_all():
            cat.pk = 0
            cat_mem_repo.add(cat)
        if len(budget_sql_repo.get_all()) > 0:
            budget = budget_sql_repo.get_all()[0]
        else:
            budget = Budget()
        self.expense_widget = ExpenseView(exp_mem_repo=exp_mem_repo,
                                          cat_mem_repo=cat_mem_repo)
        layout.addWidget(self.expense_widget)
        self.budget_widget = BudgetView(budget, exp_mem_repo)
        self.expense_widget.expenseEdited.connect(self.update_budget_table)
        layout.addWidget(self.budget_widget)
        edit_category_button = QtWidgets.QPushButton('Редактировать категории')
        edit_category_button.clicked.connect(self.edit_category_dialog)
        self.category_window = CategoryWindow(cat_mem_repo)
        self.category_window.categoryEdited.connect(self.update_expense_table)
        self.category_window.categoryEdited.connect(self.update_category_list)
        layout.addWidget(edit_category_button)
        self.ls_categories = get_categories(cat_mem_repo)
        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(self.ls_categories)
        layout.addLayout(h_widget_with_label('Категории', self.combobox))
        save_button = QtWidgets.QPushButton('Save')
        save_button.clicked.connect(self.save_button_click)
        layout.addWidget(save_button)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.budget_widget.check_warning_budget()

    def update_budget_table(self) -> None:
        """
        Обновляет таблицу бюджета при изменении таблицы расходов.
        """
        self.budget_widget.update_expense_column(self.expense_widget.exp_mem_repo)
        self.budget_widget.check_warning_budget()

    def edit_category_dialog(self) -> None:
        """
        Редактировать категории
        """
        self.category_window.show()

    def update_expense_table(self) -> None:
        """
        Обновляет таблицу расходов после обновления репозитории категорий
        """
        if len(self.category_window.deleted_cat) > 0:
            deleted_rows = []
            for i, exp in enumerate(self.expense_widget.exp_mem_repo.get_all()):
                if exp.category in self.category_window.deleted_cat:
                    deleted_rows.append(i)
                    self.expense_widget.expense_table.removeRow(i)
                    self.expense_widget.exp_mem_repo.delete(pk=exp.pk)
            deleted_rows.sort(reverse=True)
            for i in deleted_rows:
                self.expense_widget.expense_table.removeRow(i)
        for exp in self.expense_widget.exp_mem_repo.get_all():
            for pk_del in self.category_window.deleted_cat:
                if exp.category > pk_del:
                    exp.category -= 1
            self.expense_widget.exp_mem_repo.update(exp)
        # После удаления строк расхода, обнулить список удаленных категорий
        self.category_window.deleted_cat = []
        self.expense_widget.cat_mem_repo = self.category_window.cat_mem_repo
        self.expense_widget.set_data()
        # Обнавить таблицу бюджета после изменения таблицы расходов
        self.update_budget_table()

    def update_category_list(self) -> None:
        """
        Обновляет список категорий
        """
        self.combobox.clear()
        self.ls_categories = get_categories(self.category_window.cat_mem_repo)
        self.combobox.addItems(self.ls_categories)

    def save_button_click(self) -> None:
        """
        Сохранить изменения MainWindow
        """
        self.save_cat_repo()
        self.save_budget_repo()
        self.save_exp_repo()
        show_warning_dialog(message='Saved')

    def save_cat_repo(self) -> None:
        """
        Save category table
        """
        if len(self.cat_sql_repo.get_all()) > 0:
            for cat in self.cat_sql_repo.get_all():
                self.cat_sql_repo.delete(cat.pk)
        if len(self.category_window.cat_mem_repo.get_all()):
            for cat in self.category_window.cat_mem_repo.get_all():
                self.cat_sql_repo.add(cat)

    def save_exp_repo(self) -> None:
        """
        Save expense table
        """
        if len(self.exp_sql_repo.get_all()) > 0:
            for exp in self.exp_sql_repo.get_all():
                self.exp_sql_repo.delete(exp.pk)
        if len(self.expense_widget.exp_mem_repo.get_all()) > 0:
            for exp in self.expense_widget.exp_mem_repo.get_all():
                exp.pk = 0
                self.exp_sql_repo.add(exp)

    def save_budget_repo(self) -> None:
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
    budget_repo: SQLiteRepository[Budget] = SQLiteRepository(db_file=DB_FILE,
                                                             cls=Budget)
    expense_repo: SQLiteRepository[Expense] = SQLiteRepository(db_file=DB_FILE,
                                                               cls=Expense)
    category_repo: SQLiteRepository[Category] = SQLiteRepository(db_file=DB_FILE,
                                                                 cls=Category)
    create_table_db(db_file=DB_FILE, cls=Budget)   # if table is not existing
    create_table_db(db_file=DB_FILE, cls=Expense)
    create_table_db(db_file=DB_FILE, cls=Category)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(budget_sql_repo=budget_repo,
                        exp_sql_repo=expense_repo,
                        cat_sql_repo=category_repo)
    window.setWindowTitle('The Bookkeeper')
    window.resize(500, 700)
    window.show()
    sys.exit(app.exec())
