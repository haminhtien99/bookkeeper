import sys
import random
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,QHeaderView, \
    QAbstractItemView, QSizePolicy, QLabel, QTableWidgetItem, QApplication, \
    QPushButton,QDialog, QLineEdit, QComboBox)
class EditDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование Категорий")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.resize(500,500)
        
        
class MyWindow(QWidget):
    def __init__(self, data_expense:list[list[str]], data_budger:list[list[str]]):
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.expense_widget_table= self.expense_widget(data_expense)
        self.layout.addLayout(widget_with_label("Расходы", self.expense_widget_table))
        
        self.budget_widget_table = self.budget_widget(data_budger)
        self.layout.addLayout(widget_with_label("Бюджет", self.budget_widget_table))
        
        self.layout.addLayout(widget_with_label('Сумма', QLineEdit('0')))
        
        self.edit_button = QPushButton("Редактировать Категории")
        self.edit_button.clicked.connect(self.edit_category)
        self.layout.addWidget(self.edit_button)
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(lambda:self.add_row(self.expense_widget_table))
        self.layout.addWidget(self.add_button)
        
        
        self.setLayout(self.layout)
    def expense_widget(self, data:list[list[str]])-> QTableWidget:
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
        
    def budget_widget(self, data:list[list[str]])->QTableWidget:
        budget_table = QTableWidget(2, 3)
        
        budget_table.setColumnCount(2)
        budget_table.setRowCount(3)
        budget_table.setHorizontalHeaderLabels(['Сумма', 'Бюджет'])
        budget_table.setVerticalHeaderLabels(['День', 'Неделя', 'Месяц'])
        budget_table.setEditTriggers(QTableWidget.DoubleClicked)
        
        set_data(budget_table, data)
        budget_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        return budget_table    
    
    def edit_category(self):
        edit_dialog = EditDialog(self)
        edit_dialog.exec()
        
    def add_row(self, table:QTableWidget)-> None:
        row_count = table.rowCount()
        table.insertRow(row_count)
        
      
def set_data(tableWidget, data: list[list[str]])->None:
    for i, row in enumerate(data):
        for j, x in enumerate(row):
            tableWidget.setItem(i, j, QTableWidgetItem(x.capitalize()))
def widget_with_label(text:str, widget:QWidget)->QHBoxLayout:
    hl = QHBoxLayout()
    hl.addWidget(QLabel(text))
    hl.addWidget(widget)
    return hl
data1 = [row.split('|') for row in '''
2023-01-09 15:09:00|7.49|хозтовары|пакет на кассе
2023-01-09 15:09:00|104.99|кефир
2023-01-09 15:09:00|129.99|хлеб
2023-01-09 15:09:00|239.98|сладости|пряники
2023-01-09 15:09:00|139.99|сыр
2023-01-09 15:09:00|82.99|сметана
2023-01-06 20:32:02|5536.00|книги|книги по Python и PyQt
2023-01-05 23:01:38|478.00|телефон
2023-01-03 14:18:00|78.00|продукты
2023-01-03 14:18:00|1112.00|рыба
2023-01-03 14:18:00|1008.00|рыба
2023-01-03 14:18:00|156.00|рыба
2023-01-03 14:18:00|168.00|сладости
2023-01-03 14:18:00|236.73|фрукты
2023-01-03 14:18:00|16.00|хозтовары
2023-01-03 13:59:00|259.73|книги
2023-01-03 13:59:00|119.86|хлеб
2023-01-03 13:59:00|159.82|крупы
2023-01-03 13:59:00|79.91|макароны
2023-01-03 13:59:00|479.48|овощи
'''.strip().splitlines()]
data2 = [row.split('|') for row in '''
123.3|1000
5678.6|7000
23000.5|30000
'''.strip().splitlines()]


app = QApplication(sys.argv)
window = MyWindow(data1, data2)
window.setWindowTitle('hello')
window.resize(500,500)

window.show()
sys.exit(app.exec())
