import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QDialog, QPushButton
from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent

from bookkeeper.view.category_view import CategoryWindow, list_category_widget
from bookkeeper.view.budget_view import SetBudgetWindow, budget_main_window
from bookkeeper.view.expense_view import ExpenseWindow
from bookkeeper.view.view_utils import show_warning_dialog
from functools import partial
from typing import Optional

class CategoryDialog(QDialog):
    """
    Модальное окно для редактирования категорий.
    """
    def __init__(self, parent: Optional[QWidget]=None)->None:
        super().__init__(parent)
        self.setWindowTitle("Редактирование категорий")
        
        # Создаем экземпляр класса CategoryWindow и добавляем его в диалоговое окно
        self.category_window = CategoryWindow()
        self.resize(500, 500)
        layout = QVBoxLayout()
        layout.addWidget(self.category_window)
        self.setLayout(layout)

class BudgetDialog(QDialog):
    """
    Модальное окно для редактирования бюджетов.
    """
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Редактирование бюджетов")
        self.budget_window = SetBudgetWindow()
        self.resize(500, 500)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.budget_window)
        self.setLayout(self.layout)
class MainWindow(QWidget):
    """
    Главное окно приложения.
    """
    def __init__(self, data_expense:list[list[str]], data_budget:list[list[str]])->None:
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.expense_widget = ExpenseWindow(data_expense)
        self.layout.addWidget(self.expense_widget)

        self.budget_widget = budget_main_window(data_budget)
        self.layout.addLayout(self.budget_widget)

        self.edit_budget_button = QPushButton("Редактировать Бюджет")
        self.edit_budget_button.clicked.connect(self.edit_budget_dialog)
        self.layout.addWidget(self.edit_budget_button)

        categories = {
            'parent1':[],
            'parent2': [],
            'parent3': ['child5', 'child6']
        }
        ls_categories = []
        for item, value in categories.items():
            ls_categories.append(item)
            for i in value:
                ls_categories.append(i)
        self.show_category = list_category_widget(ls_categories)
        self.layout.addLayout(self.show_category)
        
        self.edit_category_button = QPushButton("Редактировать Категории")
        self.edit_category_button.clicked.connect(self.show_category_dialog)
        self.layout.addWidget(self.edit_category_button)

        self.setLayout(self.layout)
    def show_category_dialog(self):
        """
        Показывает диалог редактирования категорий.
        """
        dialog = CategoryDialog(self)
        dialog.exec()
    def edit_budget_dialog(self):
        """
        Показывает диалог редактирования бюджета.
        """
        dialog = BudgetDialog()
        dialog.exec()
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
app = QApplication(sys.argv)
window = MainWindow(data1, data2)
window.setWindowTitle('The Bookkeeper')
window.resize(500, 500)
window.show()

sys.exit(app.exec())