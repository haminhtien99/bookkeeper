import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,QHeaderView, \
                               QSizePolicy, QLabel, QApplication, QPushButton)
from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent

from bookkeeper.view.view_utils import set_data
from functools import partial
from typing import Optional



class ExpenseWindow(QWidget):
    """
    Главное окно приложения.
    """
    def __init__(self, data_expense:list[list[str]])->None:
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.expense_widget_table= self.expense_widget(data_expense)
        self.layout.addWidget(QLabel('Расходы'))
        self.layout.addWidget(self.expense_widget_table)
        
        # self.layout.addLayout(widget_with_label('Сумма', QLineEdit('0')))
        
        # categories = {
        #     'parent1':[],
        #     'parent2': [],
        #     'parent3': ['child5', 'child6']
        # }
        # ls_categories = []
        # for item, value in categories.items():
        #     ls_categories.append(item)
        #     for i in value:
        #         ls_categories.append(i)
        
        
        self.add_button = QPushButton("Новый расход")
        self.add_button.clicked.connect(lambda:self.add_row(self.expense_widget_table))
        self.layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("Удалить расход")
        self.delete_button.clicked.connect(self.delete_row)
        self.layout.addWidget(self.delete_button)
        

        self.setLayout(self.layout)
    def expense_widget(self, data:list[list[str]])-> QTableWidget:
        """
        Виджет для отображения таблицы расходов.
        """
        expenses_table = QTableWidget(4, len(data))
        expenses_table.setColumnCount(4)
        expenses_table.setRowCount(len(data))
        
        expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split())

        header = expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        expenses_table.setEditTriggers(QTableWidget.DoubleClicked)
        expenses_table.verticalHeader().hide()

        set_data(expenses_table, data)
        expenses_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return expenses_table
        
       
    
        
    def add_row(self, table:QTableWidget)-> None:
        """
        Добавляет новую строку в таблицу.
        """
        row_count = table.rowCount()
        table.insertRow(row_count)
    def delete_row(self)-> None:
        """
        Удаляет выбранную строку из таблицы.
        """
        selected_row = self.expense_widget_table.currentRow()
        if selected_row >= 0:
            self.expense_widget_table.removeRow(selected_row)
        else:
            print("Выбери строку")
    


data1 = [row.split('|') for row in '''
2023-01-09 15:09:00|7.49|хозтовары|пакет на кассе
2023-01-09 15:09:00|104.99|кефир
2023-01-09 15:09:00|129.99|хлеб
2023-01-09 15:09:00|239.98|сладости|пряники
2023-01-09 15:09:00|139.99|сыр
2023-01-09 15:09:00|82.99|сметана
2023-01-06 20:32:02|5536.00|книги|книги по Python и PyQt
2023-01-05 23:01:38|478.00|телефон
'''.strip().splitlines()]
data2 = [row.split('|') for row in '''
123.3|1000
5678.6|7000
23000.5|30000
'''.strip().splitlines()]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExpenseWindow(data1)
    window.setWindowTitle('Category')
    window.resize(500,500)
    
    window.show()
    sys.exit(app.exec())
