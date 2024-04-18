"""
Диалог для задания бюджета
"""
from PySide6 import QtWidgets
from bookkeeper.models.budget import Budget
from bookkeeper.utils import h_widget_with_label, show_warning_dialog


class SetBudgetDialog(QtWidgets.QDialog):
    """
    Диалог для задания бюджета
    """

    def __init__(self, budget: Budget) -> None:
        super().__init__()
        self.budget = budget
        self.setWindowTitle('Задать бюджет')
        self.setFixedSize(300, 350)
        layout = QtWidgets.QVBoxLayout()
        self.edit_budget_daily = QtWidgets.QLineEdit()
        self.edit_budget_daily.setText(str(budget.day))
        layout.addLayout(h_widget_with_label('Бюджет на день ',
                                             self.edit_budget_daily))
        self.edit_budget_weekly = QtWidgets.QLineEdit()
        self.edit_budget_weekly.setText(str(budget.week))
        layout.addLayout(h_widget_with_label('Бюджет на неделю ',
                                             self.edit_budget_weekly))
        self.edit_budget_monthly = QtWidgets.QLineEdit()
        self.edit_budget_monthly.setText(str(budget.month))
        layout.addLayout(h_widget_with_label('Бюджет на месяц ',
                                             self.edit_budget_monthly))
        apply_button = QtWidgets.QPushButton('Apply')
        layout.addWidget(apply_button)
        apply_button.clicked.connect(self.apply_button_click)
        self.setLayout(layout)

    def apply_button_click(self) -> None:
        """
        Проверяет введенные данные на корректность
        и подтвердить изменения
        """
        month = self.edit_budget_monthly.text().strip()
        week = self.edit_budget_weekly.text().strip()
        day = self.edit_budget_daily.text().strip()
        try:
            month_ = float(month)
            week_ = float(week)
            day_ = float(day)
        except ValueError:
            show_warning_dialog(message='Неверный тип данных',
                                title='Set Budget')
            return
        if month_ < 0 or week_ < 0 or day_ < 0:
            show_warning_dialog(message='Бюджет не может быть отрицательным',
                                title='Set Budget')
            return
        if day_ > week_:
            show_warning_dialog(message='Бюджет дня должен быть меньше Бюджета недели',
                                title='Set Budget')
            return
        if week_ > month_:
            show_warning_dialog(message='Бюджет недели должен быть меньше Бюджета месяца',
                                title='Set Budget')
            return
        self.budget = Budget(pk=1,
                             month=month_,
                             week=week_,
                             day=day_)
        show_warning_dialog(message='Успешно!!', title='Edit')
        self.accept()
