import datetime
from PySide6 import QtWidgets
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.utils import show_warning_dialog, h_widget_with_label, get_categories
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category


class ChangeExpenseDialog(QtWidgets.QDialog):
    """
    Диалог для добавлеяния или изменения расхода
    """

    def __init__(self,
                 cat_repo: MemoryRepository[Category],
                 title: str,
                 exp: Expense | None = None) -> None:
        super().__init__()
        self.setWindowTitle(title)
        self.exp = exp
        layout = QtWidgets.QVBoxLayout()
        date_hbox = self.hbox_of_date()
        layout.addLayout(date_hbox)
        self.amount_line_edit = QtWidgets.QLineEdit()
        if self.exp is not None:   # edit mode
            self.amount_line_edit.setText(str(self.exp.amount))
        layout.addLayout(h_widget_with_label('Сумма', self.amount_line_edit))
        self.cat_repo = cat_repo
        self.categories = get_categories(self.cat_repo)   # список категорий
        self.combobox = QtWidgets.QComboBox()
        self.combobox.addItems(self.categories)
        layout.addLayout(h_widget_with_label('Категории', self.combobox))
        self.comment_line_edit = QtWidgets.QLineEdit()
        if self.exp is not None:   # edit mode
            self.comment_line_edit.setText(self.exp.comment)
        layout.addLayout(h_widget_with_label('Комметарий', self.comment_line_edit))
        apply_change_button = QtWidgets.QPushButton('Apply')
        apply_change_button.clicked.connect(self.apply_change)
        layout.addWidget(apply_change_button)
        cancel_button = QtWidgets.QPushButton('Cancel', clicked=self.reject)
        layout.addWidget(cancel_button)
        self.setLayout(layout)

    def hbox_of_date(self) -> QtWidgets.QHBoxLayout:
        """
        Виджет для получения даты расхода
        """
        date_hbox = QtWidgets.QHBoxLayout()
        date_hbox.addWidget(QtWidgets.QLabel('Дата расхода(YYYY-MM-DD)'))
        self.expense_date_line_edit = QtWidgets.QLineEdit()
        if self.exp is not None:
            self.expense_date_line_edit.setText(self.exp.expense_date)
        date_hbox.addWidget(self.expense_date_line_edit)
        self.auto_fill_date_button = QtWidgets.QPushButton('Автозаполнить')
        self.auto_fill_date_button.clicked.connect(self.auto_fill_date)
        date_hbox.addWidget(self.auto_fill_date_button)
        return date_hbox

    def auto_fill_date(self) -> None:
        """
        Автоматическое заполнение даты
        """
        self.expense_date_line_edit.setText(datetime.datetime.now().strftime("%Y-%m-%d"))

    def apply_change(self):
        """
        Проверяет данные
        Если данные корректны, получить изменение и закрыть диалог
        """
        comment = self.comment_line_edit.text()
        amount = self.amount_line_edit.text().strip()
        expense_date = self.expense_date_line_edit.text().strip()
        category_obj = self.cat_repo.get(self.categories[self.combobox.currentText()])
        cat = category_obj.pk
        added_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if amount and expense_date:
            if self.validate_data(amount=amount, expense_date=expense_date):
                new_expense = Expense(comment=comment,
                                      amount=float(amount),
                                      category=cat,
                                      added_date=added_date,
                                      expense_date=expense_date)
                if self.exp is not None:
                    new_expense.pk = self.exp.pk
                self.exp = new_expense
                show_warning_dialog(message='Успешно!!', title='Edit')
                self.accept()
        else:
            show_warning_dialog(message='Ошибка! Сумма и дата должны быть заполнены',
                                title='Edit')

    def validate_date(self, expense_date: str) -> bool:
        """
        Проверяет введенную дату на корректность
        """
        try:
            datetime.datetime.strptime(expense_date, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_data(self, expense_date: str, amount: str) -> bool:
        """
        Проверяет введенные данные на корректность
        """
        if not self.validate_date(expense_date):
            show_warning_dialog(message='Ошибка! Неверный формат даты',
                                title='Apply Data')
            return False
        try:
            amount = float(amount)
        except ValueError:
            show_warning_dialog(message='Ошибка!  Сумма должна действительной',
                                title='Apply Data')
            return False
        if amount <= 0.:
            show_warning_dialog('Ошибка! Сумма должна быть положительной',
                                title='Apply Data')
            return False
        return True
