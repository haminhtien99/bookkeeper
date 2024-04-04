from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
                               QLineEdit, QTableWidget, QSizePolicy)
from typing import Optional, List
from bookkeeper.view.view_utils import set_data, v_widget_with_label
class SetBudgetWindow(QMainWindow):
    def __init__(self)-> None:
        super().__init__()

        # self.controller: Optional[Controller] = None
        self.setWindowTitle("Программа для ведения бюджета")
        self.setFixedSize(300, 350)

        self.layout = QVBoxLayout()

        self.budget_monthly = QLabel('Бюджет на месяц: ')
        self.budget_weekly = QLabel('Бюджет на неделю: ')
        self.budget_daily = QLabel('Бюджет на день: ')
        self.layout.addWidget(self.budget_monthly)
        self.edit_budget_monthly = QLineEdit()
        self.layout.addWidget(self.edit_budget_monthly)
        self.layout.addWidget(self.budget_weekly)
        self.edit_budget_weekly = QLineEdit()
        self.layout.addWidget(self.edit_budget_weekly)
        self.layout.addWidget(self.budget_daily)
        self.edit_budget_daily = QLineEdit()
        self.layout.addWidget(self.edit_budget_daily)

        self.budget_button = QPushButton('Задать бюджет')
        self.layout.addWidget(self.budget_button)
        self.budget_button.clicked.connect(self.on_budget_button_click)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

    # def set_controller(self, controller):
    #     self.controller = controller

    def refresh_budgets(self)-> None:
        pass
        # bdgt = self.controller.read('Budget')
        # self.budget_monthly.setText('Бюджет на месяц: ' + str(bdgt[0]))
        # self.budget_weekly.setText('Бюджет на неделю: ' + str(bdgt[1]))
        # self.budget_daily.setText('Бюджет на день: ' + str(bdgt[2]))


    def on_budget_button_click(self)->None:
        # self.controller.update('Budget', {'monthly': float(self.edit_budget_monthly.text()),
        #                                   'weekly': float(self.edit_budget_weekly.text()),
        #                                   'daily': float(self.edit_budget_daily.text())})
        print('Updated')
        self.refresh_budgets()
def budget_main_window(data: List[List[float]])->QVBoxLayout:
    """
    Виджет отображает бюджет в главном окне
    """
    

    budget_table = QTableWidget(2, 3)
    budget_table.setColumnCount(2)
    budget_table.setRowCount(3)
    budget_table.setHorizontalHeaderLabels(['Сумма', 'Бюджет'])
    budget_table.setVerticalHeaderLabels(['День', 'Неделя', 'Месяц'])
    budget_table.setEditTriggers(QTableWidget.DoubleClicked)

    set_data(budget_table, data)
    budget_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    return v_widget_with_label('Бюджет', budget_table)  
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = SetBudgetWindow()
    window.setWindowTitle('hello')
    window.resize(500,500)

    window.show()
    sys.exit(app.exec())