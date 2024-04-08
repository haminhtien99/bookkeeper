from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                               QLineEdit, QTableWidget, QDialog, QTableWidgetItem)

from bookkeeper.utils import (v_widget_with_label, h_widget_with_label, 
                              show_warning_dialog, get_day_week_month)
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.budget import Budget
from bookkeeper.models.expense import Expense
from datetime import datetime
class SetBudgetDialog(QDialog):
    def __init__(self, budget_repo: SQLiteRepository,
                 budget_data: dict[str, float]|None = None,
                 )-> None:
        super().__init__()
        self.budget_repo = budget_repo
        
        self.setWindowTitle('Задать бюджет')
        self.setFixedSize(300, 350)
        self.layout = QVBoxLayout()
        
        self.edit_budget_daily = QLineEdit()
        if budget_data is not None:
            self.edit_budget_daily.setText(str(budget_data['day']))
        self.layout.addLayout(h_widget_with_label('Бюджет на день ', self.edit_budget_daily))

        self.edit_budget_weekly = QLineEdit()
        if budget_data is not None:
            self.edit_budget_weekly.setText(str(budget_data['week']))
        self.layout.addLayout( h_widget_with_label('Бюджет на неделю ', self.edit_budget_weekly))

        self.edit_budget_monthly = QLineEdit()
        if budget_data is not None:
            self.edit_budget_monthly.setText(str(budget_data['month']))
        self.layout.addLayout(h_widget_with_label('Бюджет на месяц ',self.edit_budget_monthly))
        
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
class BudgetView(QWidget):
    """
    Виджет отображает бюджет в главном окне
    """
    def __init__(self, budget_repo: SQLiteRepository|None = None,
                 exp_repo: SQLiteRepository|None = None)-> None:
        super().__init__()
        self.budget_repo = budget_repo
        self.layout = QVBoxLayout()
        
        self.budget_table = QTableWidget(2, 3)
        self.show_budget_widget()
        self.from_expense_repo(exp_repo)
        self.layout.addLayout(v_widget_with_label('Бюджет', self.budget_table))
        
        self.set_budget_button = QPushButton('Задать бюджет')
        self.set_budget_button.clicked.connect(self.set_budget_dialog)
        self.layout.addWidget(self.set_budget_button)
        
        self.setLayout(self.layout)
        self.change_budget = None
        
    def show_budget_widget(self)->None:
        
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
            if len(budget) == 0:
                self.budget_table.setItem(0, 1, QTableWidgetItem('0'))
                self.budget_table.setItem(1, 1, QTableWidgetItem('0'))
                self.budget_table.setItem(2, 1, QTableWidgetItem('0'))
            else:
                budget = budget[0]
                self.budget_table.setItem(0, 1, QTableWidgetItem(str(budget.day)))
                self.budget_table.setItem(1, 1, QTableWidgetItem(str(budget.week)))
                self.budget_table.setItem(2, 1, QTableWidgetItem(str(budget.month)))
        

    def set_budget_dialog(self)->None:
        month = self.budget_table.item(2, 1).text()
        weeek = self.budget_table.item(0, 1).text()
        day = self.budget_table.item(0, 1).text()
        
        dialog = SetBudgetDialog(budget_repo = self.budget_repo, 
                                 budget_data = {'month':month, 'week':weeek, 'day':day})
        
        dialog.exec()
        
        if dialog.budget is not None:    
            new_budget = dialog.budget
            
            self.budget_table.setItem(0, 1, QTableWidgetItem(str(new_budget.day)))
            self.budget_table.setItem(1, 1, QTableWidgetItem(str(new_budget.week)))
            self.budget_table.setItem(2, 1, QTableWidgetItem(str(new_budget.month)))
            self.change_budget= ('update-budget',dialog.budget)
    def from_expense_repo(self, exp_repo:SQLiteRepository|None = None)->None:
        """
        Получить расход за день, неделю, месяц из репозитории расходов
        """
        if exp_repo is None or exp_repo.table_exists() is False:
            self.budget_table.setItem(0, 0, QTableWidgetItem('0'))
            self.budget_table.setItem(1, 0, QTableWidgetItem('0'))
            self.budget_table.setItem(2, 0, QTableWidgetItem('0'))
        else:
            day_week_month = get_day_week_month()

            today = day_week_month['today'] 
            this_week = day_week_month['this_week']
            this_month = day_week_month['this_month']
            exps_day = exp_repo.get_all({'expense_date': today})
            exps_week = exp_repo.get_all({'expense_date': this_week}, 
                                          value_range = True)
            exps_month = exp_repo.get_all({'expense_date':this_month}, 
                                          value_range= True)
            day_sum = 0.
            for exp in exps_day:
                day_sum += exp.amount
            week_sum = 0.
            for exp in exps_week:
                week_sum += exp.amount
            month_sum = 0.
            for exp in exps_month:
                month_sum += exp.amount
            self.budget_table.setItem(0, 0, QTableWidgetItem(str(day_sum)))
            self.budget_table.setItem(1, 0, QTableWidgetItem(str(week_sum)))
            self.budget_table.setItem(2, 0, QTableWidgetItem(str(month_sum)))
    def from_expense_widget_table(self, exp_table:QTableWidget)->None:
        """
        Получить расход за день, неделю, месяц из таблицы расходов
        """
        day_week_month = get_day_week_month()

        today = day_week_month['today'] 
        this_week = day_week_month['this_week']
        this_month = day_week_month['this_month']

        day_sum = 0.
        for row in range(exp_table.rowCount()):
            item_date = exp_table.item(row, 0)
            item_amount = exp_table.item(row,1)

            if item_date is not None and item_amount is not None \
                and item_date.text() and item_amount.text():
                
                    item_date = item_date.text()
                    if today == item_date :
                        day_sum += float(exp_table.item(row, 1).text())

        week_sum = 0.
        for row in range(exp_table.rowCount()):
            item_date = exp_table.item(row, 0)
            item_amount = exp_table.item(row,1)

            if item_date is not None and item_amount is not None \
                and item_date.text() and item_amount.text():
                item_date = item_date.text()
                if this_week[0] <= item_date <= this_week[1]:
                    week_sum += float(exp_table.item(row, 1).text())
        month_sum = 0.
        for row in range(exp_table.rowCount()):
            item_date = exp_table.item(row, 0)
            item_amount = exp_table.item(row,1)

            if item_date is not None and item_amount is not None \
                and item_date.text() and item_amount.text():
                item_date = item_date.text()
                if this_month[0] <= item_date <= this_month[1]:
                    month_sum += float(exp_table.item(row, 1).text())

        self.budget_table.setItem(0, 0, QTableWidgetItem(str(day_sum)))
        self.budget_table.setItem(1, 0, QTableWidgetItem(str(week_sum)))
        self.budget_table.setItem(2, 0, QTableWidgetItem(str(month_sum)))       

    def save_button_click(self):
        """
        Сохранить бюджет
        """
        if self.change_budget is None:
            show_warning_dialog(message='Нет изменения', title = 'Сохранение')
        else:
             
            if self.budget_repo.table_exists() is False:
                self.budget_repo.create_table_db()
                
            if len(self.budget_repo.get_all()) == 0:
                self.budget_repo.add(self.change_budget[1])
            else:
                self.budget_repo.update(self.change_budget[1])
            # show_warning_dialog(message='Успешно сохранить бюджет', title= 'Сохранение')

            self.change_budget = None
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    budget_repo = SQLiteRepository(db_file = 'bookkeeper/view/new_database.db', cls = Budget)
    exp_repo = SQLiteRepository(db_file = 'bookkeeper/view/new_database.db', cls = Expense)
    window = BudgetView(budget_repo=budget_repo, exp_repo= exp_repo)
    window.setWindowTitle('Set Budget')
    window.resize(500,500)
    save_button = QPushButton('Save')
    save_button.clicked.connect(window.save_button_click)
    window.layout.addWidget(save_button)

    window.setLayout(window.layout)
    window.show()
    sys.exit(app.exec())