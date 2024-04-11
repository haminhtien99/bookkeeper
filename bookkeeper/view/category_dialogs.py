"""
Диалоги для виджета CategoryWindow
"""
from typing import Optional
from PySide6 import QtWidgets
class AddCategoryDialog(QtWidgets.QDialog):
    """
    Модальное окно для добавления новой категории
    """
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None)->None:
        super().__init__(parent)
        self.setWindowTitle('Добавить категорию')
        self.input_field = QtWidgets.QLineEdit()
        self.ok_button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | \
            QtWidgets.QDialogButtonBox.Cancel)
        self.ok_button.accepted.connect(self.accept)
        self.ok_button.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)
    def get_category_name(self)-> str:
        """Возвращает название новой категории."""
        return self.input_field.text()
class EditCategoryDialog(QtWidgets.QDialog):
    """
    Модальное окно для редактирования существующей категории.
    """
    def __init__(self, current_name:str,
                 parent: Optional[QtWidgets.QWidget]= None)->None:
        super().__init__(parent)
        self.setWindowTitle('edit category')
        self.input_field = QtWidgets.QLineEdit(current_name)
        self.ok_button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | \
            QtWidgets.QDialogButtonBox.Cancel)
        self.ok_button.accepted.connect(self.accept)
        self.ok_button.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)
    def get_new_category_name(self)->str:
        """Возвращает название новой категории."""
        return self.input_field.text()
class DeleteConfirmationDialog(QtWidgets.QDialog):
    """
    Диалог для подтверждения удаления.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Confirmation")
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("What do you want to delete?")
        layout.addWidget(self.label)
        self.delete_all_children_button = QtWidgets.QPushButton("Delete All Children")
        self.delete_all_children_button.clicked.connect(self.delete_all_children)
        layout.addWidget(self.delete_all_children_button)
        self.delete_only_this_button = QtWidgets.QPushButton("Delete Only This")
        self.delete_only_this_button.clicked.connect(self.delete_only_this)
        layout.addWidget(self.delete_only_this_button)
        self.setLayout(layout)
        self.result = None
    def delete_all_children(self):
        """Удалить все дочерние категории."""
        self.result = "Delete All Children"
        self.accept()
    def delete_only_this(self):
        """Удалить только эту категорию."""
        self.result = "Delete Only This"
        self.accept()
