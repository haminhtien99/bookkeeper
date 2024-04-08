import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,QHeaderView, QSizePolicy, 
                               QLabel, QApplication, QPushButton,QTableWidgetItem, 
                               QAbstractItemView)

from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import show_warning_dialog
from bookkeeper.view.category_view import get_categories
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.view.change_expense_dialog import ChangeExpenseDialog
class ExpenseView(QWidget):
    """
    Виджет расхода в главном окне
    """
    def __init__(self, cat_repo: SQLiteRepository, 
                 exp_repo: SQLiteRepository)->None:
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.cat_repo = cat_repo
        self.categories = get_categories(cat_repo)

        self.exp_repo = exp_repo
        
        self.expense_table = QTableWidget()
        self.ls_pk = dict() # Список pk каждой строки таблцы в QTableWidget
        self.build_expense_widget()
        
        self.layout.addWidget(QLabel('Расходы'))
        self.layout.addWidget(self.expense_table)
        
        self.add_button = QPushButton("Новый расход")
        self.add_button.clicked.connect(self.add_expense_dialog)
        self.layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton('Удалить расход')
        self.delete_button.clicked.connect(self.delete_row)
        self.layout.addWidget(self.delete_button)

        self.edit_button = QPushButton('Редактировать')
        self.edit_button.clicked.connect(self.edit_expense_dialog)
        self.layout.addWidget(self.edit_button)

        self.setLayout(self.layout)

        self.changes = []       # История изменений

    def build_expense_widget(self)-> None:
        """
        Виджет для отображения таблицы расходов.
        """        
        columns = "Дата Сумма Категория Комментарий".split()
        
        
        self.expense_table.setColumnCount(4)
        self.expense_table.setRowCount(10)
        self.expense_table.setHorizontalHeaderLabels(columns)

        header = self.expense_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.expense_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.expense_table.verticalHeader().hide()

        if self.exp_repo.table_exists() is True:
            self.set_data()
        self.expense_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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

    def delete_row(self)-> None:
        """
        Удаляет выбранную строку из таблицы. Автоматически удаляет первую строку
        """
        selected_row = self.expense_table.currentRow()
        if self.is_row_empty(selected_row ) is True:
            show_warning_dialog(message='Выберите не пустую строку для удаления',
                                title='Delete')
            return
        if selected_row >= 0:

            self.expense_table.removeRow(selected_row)
            pk = self.ls_pk[selected_row]
            self.changes.append(('delete', pk))
            
            # Update self.ls_pk
            if selected_row < len(self.ls_pk) - 1:
                for i in range(selected_row, len(self.ls_pk) - 1):
                    self.ls_pk[i] = self.ls_pk[i+1]
            del self.ls_pk[len(self.ls_pk) - 1]
            
        else:
            show_warning_dialog(message='В таблице нет строки', title='Delete')

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
                print(self.expense_table.rowCount(), self.ls_pk)
                self.expense_table.insertRow(self.expense_table.rowCount())

            cat_info =  self.cat_repo.get(exp.category)
            cat = cat_info.name
            row = [exp.expense_date, str(exp.amount), cat, exp.comment]
            for j, value in enumerate(row):
                self.expense_table.setItem(max(self.ls_pk.keys()), j, QTableWidgetItem(value))

    def edit_expense_dialog(self)->None:
        """
        Открывает диалог редактирования строки таблицы.
        """
        selected_row = self.expense_table.currentRow()
        if self.is_row_empty(selected_row ) is True:
            show_warning_dialog(message='Выберите не пустую строку для редактирования',
                                title='Edit')
            return
        
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

    def save_button_click(self):
        """
        Сохраняет все изменения в таблицу.
        """
        if len(self.changes) == 0:
            show_warning_dialog(message='Нет изменения', title = 'Сохранение')
        else:
            for change in self.changes:
                if change[0] == 'add':
                    self.exp_repo.add(change[1])
                elif change[0] == 'delete':
                    self.exp_repo.delete(change[1])
                elif change[0] == 'update':
                    self.exp_repo.update(change[1])
            # show_warning_dialog(message='Успешно сохранить категории', title= 'Сохранение')
            self.changes = []
    def is_row_empty(self, selected_rơw:int)->bool:
        """
        Проверяет, пуста ли строка таблицы.
        """
        for j in range(self.expense_table.columnCount()):
            item = self.expense_table.item(selected_rơw, j)
            if item is not None and item.text():
                return False 
        return True
if __name__ == '__main__':
    app = QApplication(sys.argv)
    cat_repo = SQLiteRepository('bookkeeper/view/new_database.db', Category)
    exp_repo = SQLiteRepository('bookkeeper/view/new_database.db', Expense)
    
    
    window = ExpenseView(cat_repo, exp_repo)
    window.setWindowTitle('Category')
    window.resize(500,500)

    save_button = QPushButton('Сохранить')
    save_button.clicked.connect(window.save_button_click)
    window.layout.addWidget(save_button)

    window.setLayout(window.layout)
    window.show()

    sys.exit(app.exec())
