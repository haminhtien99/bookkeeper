import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,QHeaderView, \
                               QSizePolicy, QLabel, QApplication, QPushButton, \
                                QTableWidgetItem, QDialog, QLineEdit, QComboBox, \
                                    QHBoxLayout, QInputDialog, QAbstractItemView)
from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent

from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.view.view_utils import show_warning_dialog, h_widget_with_label
from bookkeeper.view.category_view import list_category_widget, get_categories
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.view.category_view import AddCategoryDialog
from functools import partial
from typing import List
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

        self.changes_add = None
    def add_expense(self)-> None:
        comment = self.comment_line_edit.text()
        amount = float(self.amount_line_edit.text())
        category = self.cat_repo.get(self.categories[self.combobox.currentText()]) 
        expense_date = str(self.expense_date_line_edit.text())
        added_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if added_date and amount:
            new_expense = Expense(comment = comment, 
                                  amount = amount, 
                                  category = category,
                                  added_date = added_date, 
                                  expense_date = expense_date)
            
            self.change_add = ('add', new_expense)
            self.accept()
        else:
            show_warning_dialog('Ошибка! Дата и Сумма не заполнены. Нет изменения')

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
        self.categories = get_categories(cat_repo)

        self.exp_repo = exp_repo
        self.ls_pk = dict()
        
        self.expense_widget_table= self.expense_widget()
        
        self.layout.addWidget(QLabel('Расходы'))
        self.layout.addWidget(self.expense_widget_table)
        
        # self.layout.addLayout(widget_with_label('Сумма', QLineEdit('0')))
        
        self.add_button = QPushButton("Новый расход")
        self.add_button.clicked.connect(self.add_expense_dialog)
        self.layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton('Удалить расход')
        self.delete_button.clicked.connect(self.delete_row)
        self.layout.addWidget(self.delete_button)

        self.edit_button = QPushButton('Редактировать ячейку')
        self.edit_button.clicked.connect(self.edit_cell)
        self.layout.addWidget(self.edit_button)

        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)
        
        self.setLayout(self.layout)
        

        self.changes = []       

    def expense_widget(self)-> QTableWidget:
        """
        Виджет для отображения таблицы расходов.
        """
        
        
        columns = "Дата Сумма Категория Комментарий".split()
        
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(4)
        self.expense_table.setRowCount(10)
        self.expense_table.setHorizontalHeaderLabels(columns)

        header = self.expense_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.expense_table.setEditTriggers(QAbstractItemView.SelectedClicked)
        self.expense_table.verticalHeader().hide()

        if self.exp_repo.table_exists() is True:
            self.set_data()
        self.expense_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return self.expense_table
        
    
    def delete_row(self)-> None:
        """
        Удаляет выбранную строку из таблицы. Автоматически удаляет первую строку
        """
        selected_row = self.expense_widget_table.currentRow()
        if selected_row >= 0:
            self.expense_widget_table.removeRow(selected_row)
            pk = self.ls_pk[selected_row]
            self.changes.append(('delete', pk))
        else:
            show_warning_dialog("В таблице нет строки")
    
    def set_data(self)-> None:
        """
        Устанавливает данные в таблицу.
        """
        expenses = self.exp_repo.get_all()
        for i, exp in enumerate(expenses):
            if i == self.expense_table.rowCount():
                self.expense_table.insertRow(i)

            self.ls_pk[i] = exp.pk

            cat_info =  self.cat_repo.get(exp.category)
            cat = cat_info.name
            row = [exp.expense_date, str(exp.amount), cat, exp.comment]
            for j, value in enumerate(row):
                self.expense_table.setItem(i, j, QTableWidgetItem(value))

    def add_expense_dialog(self)->None:
        """
        Открывает диалог добавления нового расхода.
        """
        dialog = AddExpenseDialog(self.exp_repo, self.cat_repo)
        dialog.exec()
        self.changes.append(dialog.change_add)
        if dialog.change_add is not None:
            exp = dialog.change_add[1]
            # Задавать автомотически pk у нового расхода - max(self.ls_pk.values()) + 1
            self.ls_pk[self.expense_table.rowCount()] = max(self.ls_pk.values()) + 1
            if self.ls_pk[self.expense_table.rowCount()] > self.expense_table.rowCount():
                self.expense_table.insertRow(self.expense_table.rowCount())
            cat_info =  self.cat_repo.get(exp.category)
            cat = cat_info.name
            row = [exp.expense_date, str(exp.amount), cat, exp.comment]
            for j, value in enumerate(row):
                self.expense_table.setItem(max(self.ls_pk.values()) - 1, j, QTableWidgetItem(value))

    def edit_cell(self)->None:
        """
        Открывает диалог редактирования ячейки таблицы.
        """
        selected_row = self.expense_widget_table.currentRow()
        selected_column = self.expense_widget_table.currentColumn()

        if selected_row :
            item = self.expense_table.item(selected_row, selected_column)
            new_value, ok = QInputDialog.getText(self,'Изменить данные', "Новое значение")
            if ok:
                item.setText(new_value)
                pk = self.ls_pk[selected_row] 
                expense_date = self.expense_table.item(selected_row, 0).text()
                amount = float(self.expense_table.item(selected_row, 1).text())
                name_cat = self.expense_table.item(selected_row, 2).text()
                category = self.cat_repo.get(self.categories[name_cat]) 
                comment = self.expense_table.item(selected_row, 3).text()
                added_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_expense = Expense(comment = comment, 
                                      amount = amount, 
                                      category = category,
                                      added_date = added_date, 
                                      expense_date = expense_date, 
                                      pk = pk)
                self.changes.append(('update', new_expense))
    def save_changes(self):
        """
        Сохраняет все изменения в таблицу.
        """
        if len(self.changes) == 0:
            show_warning_dialog('Нет изменения')
        else:
            for change in self.changes:
                if change[0] == 'add':
                    self.exp_repo.add(change[1])
                elif change[0] == 'delete':
                    self.exp_repo.delete(change[1])
            show_warning_dialog('Успешно сохранить категории')
            self.changes = []
            # elif change[0] == 'edit':
            #     self.exp_repo.edit(change[1])   
if __name__ == '__main__':
    app = QApplication(sys.argv)
    cat_repo = SQLiteRepository('bookkeeper/view/new_database.db', Category)
    exp_repo = SQLiteRepository('bookkeeper/view/new_database.db', Expense)
    
    
    window = ExpenseWindow(cat_repo, exp_repo)
    window.setWindowTitle('Category')
    window.resize(500,500)
    
    window.show()
    sys.exit(app.exec())
