from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                               QLineEdit, QTableWidget, QDialog, QTableWidgetItem)

from typing import Optional, List
from bookkeeper.utils import v_widget_with_label, h_widget_with_label, show_warning_dialog
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.budget import Budget
class SetBudgetDialog(QDialog):
    def __init__(self, budget_repo: SQLiteRepository,
                 budget_data: dict[str, float]|None = None,
                 )-> None:
        super().__init__()
        self.budget_repo = budget_repo
        
        self.setWindowTitle('Задать бюджет')
        self.setFixedSize(300, 350)
        self.layout = QVBoxLayout()
        
        self.edit_budget_monthly = QLineEdit()
        if budget_data is not None:
            self.edit_budget_monthly.setText(str(budget_data['month']))
        self.layout.addLayout(h_widget_with_label('Бюджет на месяц ',self.edit_budget_monthly))
        
        self.edit_budget_weekly = QLineEdit()
        if budget_data is not None:
            self.edit_budget_weekly.setText(str(budget_data['week']))
        self.layout.addLayout( h_widget_with_label('Бюджет на неделю ', self.edit_budget_weekly))

        self.edit_budget_daily = QLineEdit()
        if budget_data is not None:
            self.edit_budget_daily.setText(str(budget_data['day']))
        self.layout.addLayout(h_widget_with_label('Бюджет на день ', self.edit_budget_daily))

        self.apply_button = QPushButton('Apply')
        self.layout.addWidget(self.apply_button)
        self.apply_button.clicked.connect(self.apply_button_click)

        self.setLayout(self.layout)
        self.budget = None

    def apply_button_click(self)->None:
        """
        Проверяет введенные данные на корректность
        """
        if self.validate_data():
            
            self.budget = Budget(pk = 1,
                            month = self.budget_dict['month'],
                            week= self.budget_dict['week'],
                            day = self.budget_dict['day'])
            show_warning_dialog(message='Успешно!!', title='Edit')
            self.accept()
            
    def validate_data(self):
        month = self.edit_budget_monthly.text().strip()
        week = self.edit_budget_weekly.text().strip()
        day = self.edit_budget_daily.text().strip()
        try :
            month = float(month)
            week = float(week)
            day = float(day)
        except ValueError:
            show_warning_dialog(message= 'Неверный тип данных',
                                titlee = 'Set Budget')
            return False
        if month < 0 or week < 0 or day < 0:
            show_warning_dialog(message='Бюджет не может быть отрицательным',
                                title = 'Set Budget')
            return False
        if day > week :
            show_warning_dialog(message='Бюджет дня должен быть меньше Бюджета недели', 
                                title = 'Set Budget')
            return False
        if week > month :
            show_warning_dialog(message='Бюджет недели должен быть меньше Бюджета месяца',
                                title = 'Set Budget')
            return False
        
        self.budget_dict = {'week':week,'month':month, 'day':day}
        return True
class BudgetWindow(QWidget):
    """
    Виджет отображает бюджет в главном окне
    """
    def __init__(self, budget_repo: SQLiteRepository|None = None)-> None:
        super().__init__()
        self.budget_repo = budget_repo
        self.layout = QVBoxLayout()
        
        self.budget_table = QTableWidget(2, 3)
        self.build_budget_widget()
        self.layout.addLayout(v_widget_with_label('Бюджет', self.budget_table))
        
        self.set_budget_button = QPushButton('Задать бюджет')
        self.set_budget_button.clicked.connect(self.set_budget_dialog)
        self.layout.addWidget(self.set_budget_button)
        
        self.setLayout(self.layout)
        self.change_budget = None
        
    def build_budget_widget(self)->None:
        
        self.budget_table.setColumnCount(2)
        self.budget_table.setRowCount(3)
        self.budget_table.setHorizontalHeaderLabels(['Сумма', 'Бюджет'])
        self.budget_table.setVerticalHeaderLabels(['День', 'Неделя', 'Месяц'])
        self.budget_table.setEditTriggers(QTableWidget.NoEditTriggers)

        if self.budget_repo is None or self.budget_repo.table_exists() is False:
            self.budget_table.setItem(0, 1, QTableWidgetItem('0'))
            self.budget_table.setItem(1, 1, QTableWidgetItem('0'))
            self.budget_table.setItem(2, 1, QTableWidgetItem('0'))
        else:
            budget = self.budget_repo.get_all()
            self.budget_table.setItem(0, 1, QTableWidgetItem(budget.day))
            self.budget_table.setItem(1, 1, QTableWidgetItem(budget.week))
            self.budget_table.setItem(2, 1, QTableWidgetItem(budget.month))
        

    def set_budget_dialog(self)->None:
        month = self.budget_table.item(2, 1).text()
        weeek = self.budget_table.item(0, 1).text()
        day = self.budget_table.item(0, 1).text()
        
        dialog = SetBudgetDialog(budget_repo = self.budget_repo, 
                                 budget_data = {'month':month, 'week':weeek, 'day':day})
        
        
        dialog.exec()
        if dialog.budget is not None:
            
            new_budget = dialog.budget
            self.budget_table.setItem(0, 1, QTableWidgetItem(new_budget.day))
            self.budget_table.setItem(1, 1, QTableWidgetItem(new_budget.week))
            self.budget_table.setItem(2, 1, QTableWidgetItem(new_budget.month))
            self.change_budget= ('update-budget', new_budget)
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = BudgetWindow()
    window.setWindowTitle('Set Budget')
    window.resize(500,500)

    window.show()
    sys.exit(app.exec())