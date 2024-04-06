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
class ChangeExpenseDialog(QDialog):
    """
    Диалог для добавлеяния или изменения расхода
    """
    def __init__(self,
                 cat_repo: SQLiteRepository,
                 title:str,
                 data_row: dict[str, str|float|int]| None = None )-> None:
        super().__init__()
        self.setWindowTitle(title)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.data_row = data_row
        self.expense_date_line_edit = QLineEdit()
        if self.data_row is not None:
            self.expense_date_line_edit.setText(self.data_row['expense_date'])
        layout.addLayout(h_widget_with_label('Дата расхода(YYYY-MM-DD)',self.expense_date_line_edit))

        self.amount_line_edit = QLineEdit()
        if self.data_row is not None:
            self.amount_line_edit.setText(str(self.data_row['amount']))
        layout.addLayout(h_widget_with_label('Сумма',self.amount_line_edit))
        
        self.cat_repo = cat_repo
        self.categories = get_categories(self.cat_repo)
        self.combobox = QComboBox()
        self.combobox.addItems(self.categories)
        self.category_widget = list_category_widget(cat_repo)
        layout.addLayout(self.category_widget)
        
        self.comment_line_edit = QLineEdit()
        if self.data_row is not None:
            self.comment_line_edit.setText(self.data_row['comment'])
        layout.addLayout(h_widget_with_label('Комметарий',self.comment_line_edit))

        
        apply_change_button = QPushButton('Применять')
        apply_change_button.clicked.connect(self.apply_change)
        layout.addWidget(apply_change_button)
        
        return_button = QPushButton('Вернуть', clicked=self.reject)
        layout.addWidget(return_button)
        
        

        self.change = None # История изменения

    def apply_change(self):
        comment = self.comment_line_edit.text()
        amount = self.amount_line_edit.text().strip()
        expense_date = self.expense_date_line_edit.text().strip()
        if amount:
            print('True')
        else:
            print('False')
        if amount is None or expense_date is None:
            show_warning_dialog('Ошибка! Дата и сумма должны не пусты')
            return
        else:
            if not self.validate_date(expense_date):
                show_warning_dialog('Ошибка! Неверный формат даты')
                return
            try:
                amount = float(amount)
            except ValueError:
                show_warning_dialog('Ошибка!  Сумма должна действительной')
                return
        self.accept()
        category_obj = self.cat_repo.get(self.categories[self.combobox.currentText()])
        cat  = category_obj.pk
        added_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # if amount:
        #     new_expense = Expense(comment = comment, 
        #                           amount = amount, 
        #                           category = cat,
        #                           added_date = added_date, 
        #                           expense_date = expense_date)
        #     if self.data_row is not None:
        #         new_expense.pk = self.data_row['pk']
        #         self.change = ('update', new_expense)
        #     else:
        #         self.change = ('add', new_expense)
        #     self.accept()
        # else:
        #     show_warning_dialog('Ошибка! Дата и Сумма не заполнены. Нет изменения')
    def validate_date(self, date_str: str)->bool:
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
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

        self.edit_button = QPushButton('Редактировать')
        self.edit_button.clicked.connect(self.edit_expense_dialog)
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
        dialog = ChangeExpenseDialog(cat_repo = self.cat_repo,
                                     title = 'Add')
        dialog.exec()
        
        if dialog.change is not None:
            self.changes.append(dialog.change)
            exp = dialog.change[1]
            # Задавать автомотически pk у нового расхода - max(self.ls_pk.values()) + 1
            exp.pk = 1 if len(self.ls_pk) == 0 else max(self.ls_pk.values()) + 1
            self.ls_pk[len(self.ls_pk)] = exp.pk
            
            if len(self.ls_pk) > self.expense_table.rowCount():
                self.expense_table.insertRow(self.expense_table.rowCount())

            cat_info =  self.cat_repo.get(exp.category)
            cat = cat_info.name
            row = [exp.expense_date, str(exp.amount), cat, exp.comment]
            for j, value in enumerate(row):
                self.expense_table.setItem(max(self.ls_pk.values()) - 1, j, QTableWidgetItem(value))

    def edit_expense_dialog(self)->None:
        """
        Открывает диалог редактирования строки таблицы.
        """
        selected_row = self.expense_widget_table.currentRow()

        # if selected_row :
        pk = self.ls_pk[selected_row] 
        expense_date = self.expense_table.item(selected_row, 0).text()
        amount = float(self.expense_table.item(selected_row, 1).text())
        comment = self.expense_table.item(selected_row, 3).text()
        
        data_row = {'pk':pk, 'amount':amount, 
                    'expense_date':expense_date, 'comment':comment}
        dialog = ChangeExpenseDialog(cat_repo = self.cat_repo,
                                        title = 'Edit',
                                        data_row = data_row)
        dialog.exec()
        if dialog.change is not None:
            self.changes.append(dialog.change)
            exp = dialog.change[1]
            cat_info =  self.cat_repo.get(exp.category)
            cat = cat_info.name
            row = [exp.expense_date, str(exp.amount), cat, exp.comment]
            for j, value in enumerate(row):
                self.expense_table.setItem(selected_row, j, QTableWidgetItem(value))

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cat_repo = SQLiteRepository('bookkeeper/view/new_database.db', Category)
    exp_repo = SQLiteRepository('bookkeeper/view/new_database.db', Expense)
    
    
    window = ExpenseWindow(cat_repo, exp_repo)
    window.setWindowTitle('Category')
    window.resize(500,500)
    
    window.show()

    sys.exit(app.exec())
