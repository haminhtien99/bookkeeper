"""
Виджет для расхода
"""
import sys
from PySide6 import QtWidgets, QtCore
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import show_warning_dialog, create_table_db
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.view.change_expense_dialog import ChangeExpenseDialog


class ExpenseView(QtWidgets.QWidget):
    """
    Виджет расхода в главном окне
    """
    expenseEdited = QtCore.Signal()   # Сигнал изменения данных расхода

    def __init__(self,
                 exp_mem_repo: MemoryRepository[Expense],
                 cat_mem_repo: MemoryRepository[Category]) -> None:
        super().__init__()
        self.cat_mem_repo = cat_mem_repo
        self.exp_mem_repo = exp_mem_repo
        self.layout = QtWidgets.QVBoxLayout()
        self.expense_table = QtWidgets.QTableWidget()
        self.build_expense_widget()
        self.layout.addWidget(QtWidgets.QLabel('Расходы'))
        self.layout.addWidget(self.expense_table)
        self.add_button = QtWidgets.QPushButton("Новый расход")
        self.add_button.clicked.connect(self.add_expense_dialog)
        self.layout.addWidget(self.add_button)
        self.delete_button = QtWidgets.QPushButton('Удалить расход')
        self.delete_button.clicked.connect(self.delete_row)
        self.layout.addWidget(self.delete_button)
        self.edit_button = QtWidgets.QPushButton('Редактировать')
        self.edit_button.clicked.connect(self.edit_expense_dialog)
        self.layout.addWidget(self.edit_button)
        self.setLayout(self.layout)
        self.edit_dialog = ChangeExpenseDialog(cat_repo=self.cat_mem_repo,
                                               title='Edit')
        self.add_dialog = ChangeExpenseDialog(cat_repo=self.cat_mem_repo,
                                              title='Add')

    def build_expense_widget(self) -> None:
        """
        Виджет для отображения таблицы расходов.
        """
        columns = "Дата Сумма Категория Комментарий".split()
        self.expense_table.setColumnCount(4)
        self.expense_table.setRowCount(10)
        self.expense_table.setHorizontalHeaderLabels(columns)
        header = self.expense_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.expense_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.expense_table.verticalHeader().hide()
        self.set_data()
        self.expense_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                         QtWidgets.QSizePolicy.Expanding)

    def set_data(self) -> None:
        """
        Устанавливает данные в таблицу.
        """
        expenses = self.exp_mem_repo.get_all()
        for i, exp in enumerate(expenses):
            if i == self.expense_table.rowCount():
                self.expense_table.insertRow(i)
            cat = self.cat_mem_repo.get(exp.category)
            row = [exp.expense_date, str(exp.amount), cat.name, exp.comment]
            for j, value in enumerate(row):
                self.expense_table.setItem(i, j, QtWidgets.QTableWidgetItem(value))

    def delete_row(self) -> None:
        """
        Удаляет выбранную строку из таблицы. Автоматически удаляет первую строку
        pk следующих строк уменьшается на 1 единицу и удаляется последний pk
        """
        selected_row = self.expense_table.currentRow()
        if self.is_row_empty(selected_row) is True:
            show_warning_dialog(message='Выберите не пустую строку для удаления',
                                title='Delete')
            return
        if selected_row >= 0:
            self.expense_table.removeRow(selected_row)
            for i, exp in enumerate(self.exp_mem_repo.get_all()):
                if i == selected_row:
                    self.exp_mem_repo.delete(pk=exp.pk)
                    break
            self.expenseEdited.emit()
            show_warning_dialog(message='Удалена')
        else:
            show_warning_dialog(message='В таблице нет строки', title='Delete')

    def add_expense_dialog(self) -> None:
        """
        Открывает диалог добавления нового расхода.
        """
        self.add_dialog = ChangeExpenseDialog(cat_repo=self.cat_mem_repo,
                                              title='Add')
        self.add_dialog.exec()
        if self.add_dialog.exp is not None:
            cat = self.cat_mem_repo.get(self.add_dialog.exp.category)
            row = [self.add_dialog.exp.expense_date,
                   str(self.add_dialog.exp.amount),
                   cat.name,
                   self.add_dialog.exp.comment]
            self.exp_mem_repo.add(self.add_dialog.exp)
            len_exp_repo = len(self.exp_mem_repo.get_all())
            if len_exp_repo > self.expense_table.rowCount():
                self.expense_table.insertRow(self.expense_table.rowCount())
            for j, value in enumerate(row):
                self.expense_table.setItem(len_exp_repo - 1, j,
                                           QtWidgets.QTableWidgetItem(value))
            self.expenseEdited.emit()

    def edit_expense_dialog(self) -> None:
        """
        Открывает диалог редактирования строки таблицы.
        """
        selected_row = self.expense_table.currentRow()
        if self.is_row_empty(selected_row) is True:
            show_warning_dialog(message='Выберите не пустую строку для редактирования',
                                title='Edit')
            return
        exp_current_row = self.exp_mem_repo.get_all()[selected_row]
        self.edit_dialog = ChangeExpenseDialog(cat_repo=self.cat_mem_repo,
                                               title='Edit',
                                               exp=exp_current_row)
        self.edit_dialog.exec()
        if self.edit_dialog.exp is not None:
            exp = self.edit_dialog.exp
            cat = self.cat_mem_repo.get(exp.category)
            row = [exp.expense_date, str(exp.amount), cat.name, exp.comment]
            for j, value in enumerate(row):
                self.expense_table.setItem(selected_row, j,
                                           QtWidgets.QTableWidgetItem(value))
            self.exp_mem_repo.update(exp)
            self.expenseEdited.emit()

    def is_row_empty(self, selected_row: int) -> bool:
        """
        Проверяет, пуста ли строка таблицы.
        """
        for j in range(self.expense_table.columnCount()):
            item = self.expense_table.item(selected_row, j)
            if item is not None and item.text():
                return False
        return True


if __name__ == '__main__':
    DB_FILE = 'bookkeeper/view/new_database.db'
    app = QtWidgets.QApplication(sys.argv)
    category_repo = SQLiteRepository(db_file=DB_FILE, cls=Category)
    expense_repo = SQLiteRepository(db_file=DB_FILE, cls=Expense)
    create_table_db(db_file=DB_FILE, cls=Category)
    create_table_db(db_file=DB_FILE, cls=Expense)
    category_mem_repo = MemoryRepository[Category]()
    expense_mem_repo = MemoryRepository[Expense]()
    for cat in category_repo.get_all():
        cat.pk = 0
        category_mem_repo.add(cat)
    for exp in expense_repo.get_all():
        exp.pk = 0
        expense_mem_repo.add(exp)
    window = ExpenseView(exp_mem_repo=expense_mem_repo,
                         cat_mem_repo=category_mem_repo)
    window.setWindowTitle('Expense View')
    window.resize(500, 500)
    window.setLayout(window.layout)
    window.show()
    sys.exit(app.exec())
