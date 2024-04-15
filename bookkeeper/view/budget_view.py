"""
Виджет для бюджета
"""
import sys
from PySide6 import QtWidgets
from bookkeeper.utils import (v_widget_with_label, create_table_db,
                              show_warning_dialog, get_day_week_month)
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense
from bookkeeper.view.set_budget_dialog import SetBudgetDialog


class BudgetView(QtWidgets.QWidget):
    """
    Виджет отображает бюджет в главном окне
    """
    def __init__(self,
                 budget: Budget,
                 exp_mem_repo: MemoryRepository[Expense]) -> None:
        super().__init__()
        self.budget = budget
        self.layout = QtWidgets.QVBoxLayout()
        self.budget_table = QtWidgets.QTableWidget(2, 3)
        self.show_budget_widget(exp_mem_repo)
        self.layout.addLayout(v_widget_with_label('Бюджет', self.budget_table))
        self.set_budget_button = QtWidgets.QPushButton('Задать бюджет')
        self.set_budget_button.clicked.connect(self.set_budget_dialog)
        self.layout.addWidget(self.set_budget_button)
        self.setLayout(self.layout)

    def show_budget_widget(self,
                           exp_mem_repo: MemoryRepository[Expense] | None = None) -> None:
        """
        Показывает виджет с бюджетом
        """
        self.budget_table.setColumnCount(2)
        self.budget_table.setRowCount(3)
        self.budget_table.setHorizontalHeaderLabels(['Сумма', 'Бюджет'])
        self.budget_table.setVerticalHeaderLabels(['День', 'Неделя', 'Месяц'])
        self.budget_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.update_budget_column()
        self.update_expense_column(exp_mem_repo=exp_mem_repo)
        self.check_warning_budget()

    def update_budget_column(self):
        """Показать столбец бюджета таблицы Бюджета"""
        self.budget_table.setItem(0,
                                  1,
                                  QtWidgets.QTableWidgetItem(str(self.budget.day)))
        self.budget_table.setItem(1,
                                  1,
                                  QtWidgets.QTableWidgetItem(str(self.budget.week)))
        self.budget_table.setItem(2,
                                  1,
                                  QtWidgets.QTableWidgetItem(str(self.budget.month)))

    def update_expense_column(self,
                              exp_mem_repo: MemoryRepository[Expense] | None = None
                              ) -> None:
        """
        Получить расход за день, неделю, месяц из репозитории расходов
        """
        if exp_mem_repo is not None and len(exp_mem_repo.get_all()) != 0:
            day_week_month = get_day_week_month()
            today = day_week_month['today']
            this_week = day_week_month['this_week']
            this_month = day_week_month['this_month']
            exps_day = exp_mem_repo.get_all({'expense_date': today})
            exps_week = exp_mem_repo.get_all({'expense_date': this_week},
                                             value_range=True)
            exps_month = exp_mem_repo.get_all({'expense_date': this_month},
                                              value_range=True)
            day_sum = 0.
            for exp in exps_day:
                day_sum += exp.amount
            week_sum = 0.
            for exp in exps_week:
                week_sum += exp.amount
            month_sum = 0.
            for exp in exps_month:
                month_sum += exp.amount
            self.budget_table.setItem(0, 0, QtWidgets.QTableWidgetItem(str(day_sum)))
            self.budget_table.setItem(1, 0, QtWidgets.QTableWidgetItem(str(week_sum)))
            self.budget_table.setItem(2, 0, QtWidgets.QTableWidgetItem(str(month_sum)))
        else:
            self.budget_table.setItem(0, 0, QtWidgets.QTableWidgetItem('0'))
            self.budget_table.setItem(1, 0, QtWidgets.QTableWidgetItem('0'))
            self.budget_table.setItem(2, 0, QtWidgets.QTableWidgetItem('0'))

    def check_warning_budget(self):
        """
        Вывести предупреждение о бюджете
        """
        day_sum = float(self.budget_table.item(0, 0).text())
        day_budget = float(self.budget_table.item(0, 1).text())
        week_sum = float(self.budget_table.item(1, 0).text())
        week_budget = float(self.budget_table.item(1, 1).text())
        month_sum = float(self.budget_table.item(2, 0).text())
        month_budget = float(self.budget_table.item(2, 1).text())
        if day_sum > day_budget:
            show_warning_dialog(message='Расход в течение дня превышают бюджета')
        if week_sum > week_budget:
            show_warning_dialog(message='Расход в течение недели превышает бюджета')
        if month_sum > month_budget:
            show_warning_dialog(message='Расход в течение месяца превышает бюджета')

    def set_budget_dialog(self) -> None:
        """
        Открыть диалог для задания бюджета
        """
        dialog = SetBudgetDialog(self.budget)
        dialog.exec()
        if dialog.budget is not None:
            self.budget = dialog.budget
            self.update_budget_column()


if __name__ == '__main__':
    """
    Run the budget window
    """
    DB_FILE = 'bookkeeper/view/new_database.db'
    app = QtWidgets.QApplication(sys.argv)
    budget_sql_repo = SQLiteRepository(db_file=DB_FILE, cls=Budget)
    expense_sql_repo = SQLiteRepository(db_file=DB_FILE, cls=Expense)
    create_table_db(db_file=DB_FILE, cls=Budget)
    create_table_db(db_file=DB_FILE, cls=Expense)
    expense_mem_repo = MemoryRepository[Expense]()
    budget = Budget(day=0., week=0., month=0.)
    if len(budget_sql_repo.get_all()) > 0:
        budget = budget_sql_repo.get(1)
    if len(expense_sql_repo.get_all()) > 0:
        for exp in expense_sql_repo.get_all():
            exp.pk = 0
            expense_mem_repo.add(exp)
    window = BudgetView(budget=budget, exp_mem_repo=expense_mem_repo)
    window.setWindowTitle('Set Budget')
    window.resize(500, 500)
    window.setLayout(window.layout)
    window.show()
    sys.exit(app.exec())
