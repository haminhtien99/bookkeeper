import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,QHeaderView, \
                               QSizePolicy, QLabel, QApplication, QPushButton, \
                                QTableWidgetItem, QDialog, QLineEdit, QComboBox, \
                                    QHBoxLayout)
from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent

from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.view.view_utils import show_warning_dialog, h_widget_with_label
from bookkeeper.view.category_view import list_category_widget, get_categories
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.view.category_view import AddCategoryDialog
from functools import partial
from typing import Optional
import datetime
class AddExpenseDialog(QDialog):
    def __init__(self, exp_repo: SQLiteRepository, cat_repo: SQLiteRepository)-> None:
        super().__init__()
        self.setWindowTitle('Add Expense')
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.expense_date_line_edit = QLineEdit()
        layout.addLayout(h_widget_with_label('Дата расхода',self.expense_date_line_edit))

        self.amount_line_edit = QLineEdit()
        layout.addLayout(h_widget_with_label('Сумма',self.amount_line_edit))
        
        self.cat_repo = cat_repo
        self.exp_repo = exp_repo
        
        
        
        self.categories = get_categories(cat_repo)
        self.combobox = QComboBox()
        
        # print(self.categories,self.categories.keys())
        
        self.combobox.addItems(self.categories.keys())
        h_box = QHBoxLayout()
        h_box.addLayout(h_widget_with_label('Категории', self.combobox))
        
        add_category_button = QPushButton('Новая категория')
        add_category_button.clicked.connect(self.add_category)

        h_box.addWidget(add_category_button)
        layout.addLayout(h_box)
        
        self.comment_line_edit = QLineEdit()
        layout.addLayout(h_widget_with_label('Комметарий',self.comment_line_edit))

        
        add_expenses_button = QPushButton('Add')
        add_expenses_button.clicked.connect(self.add_expense)
        layout.addWidget(add_expenses_button)

    def add_expense(self):
        comment = self.comment_line_edit.text()
        amount = self.amount_line_edit.text()
        category = self.categories[self.combobox.currentText()] 
        expense_date = str(self.expense_date_line_edit.text())
        added_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if added_date and amount:
            new_expense = Expense(comment = comment, amount = amount, category = category,
                                added_date = added_date, expense_date = expense_date)
            self.exp_repo.add(new_expense)
            self.accept()
    def add_category(self):
        pass
        
class ExpenseWindow(QWidget):
    """
    Главное окно приложения.
    """
    def __init__(self, cat_repo: SQLiteRepository, 
                 exp_repo: SQLiteRepository)->None:
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.cat_repo = cat_repo
        self.exp_repo = exp_repo
        self.ls_pk = dict()
        
        self.expense_widget_table= self.expense_widget()
        
        self.layout.addWidget(QLabel('Расходы'))
        self.layout.addWidget(self.expense_widget_table)
        
        # self.layout.addLayout(widget_with_label('Сумма', QLineEdit('0')))
        
        self.add_button = QPushButton("Новый расход")
        self.add_button.clicked.connect(self.add_expense_dialog)
        self.layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("Удалить расход")
        self.delete_button.clicked.connect(self.delete_row)
        self.layout.addWidget(self.delete_button)
        

        self.setLayout(self.layout)
    def expense_widget(self)-> QTableWidget:
        """
        Виджет для отображения таблицы расходов.
        """
        
        
        columns = "Дата Сумма Категория Комментарий".split()
        
        expenses_table = QTableWidget()
        expenses_table.setColumnCount(4)
        expenses_table.setRowCount(10)
        expenses_table.setHorizontalHeaderLabels(columns)

        header = expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        expenses_table.setEditTriggers(QTableWidget.DoubleClicked)
        expenses_table.verticalHeader().hide()

        self.set_data(expenses_table)
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
    
    def set_data(self, table: QTableWidget)-> None:
        """
        Устанавливает данные в таблицу.
        """
        expenses = self.exp_repo.get_all()
        for i, exp in enumerate(expenses):
            if i == table.rowCount():
                table.insertRow(i)

            self.ls_pk[i] = exp.pk

            cat_info =  self.cat_repo.get(exp.category)
            cat = cat_info.name
            row = [exp.expense_date, str(exp.amount), cat, exp.comment]
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(value.capitalize()))

    def add_expense_dialog(self)->None:
        """
        Открывает диалог добавления нового расхода.
        """
        dialog = AddExpenseDialog(self.exp_repo, self.cat_repo)
        dialog.exec()
        self.set_data(self.expense_widget_table)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    cat_repo = SQLiteRepository('bookkeeper/view/new_database.db', Category)
    exp_repo = SQLiteRepository('bookkeeper/view/new_database.db', Expense)
    
    
    window = ExpenseWindow(cat_repo, exp_repo)
    window.setWindowTitle('Category')
    window.resize(500,500)
    
    window.show()
    sys.exit(app.exec())
