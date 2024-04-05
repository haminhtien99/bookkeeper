from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QWidget, \
    QVBoxLayout, QPushButton, QDialog, QLineEdit, QDialogButtonBox, \
        QHBoxLayout, QComboBox
from typing import Optional, List
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.view.view_utils import show_warning_dialog, h_widget_with_label
class AddCategoryDialog(QDialog):
    """
    Модальное окно для добавления новой категории
    """
    def __init__(self, parent: Optional[QWidget] = None)->None:
        super().__init__(parent)
        self.setWindowTitle('Добавить категорию')
        
        self.input_field = QLineEdit()
        self.ok_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ok_button.accepted.connect(self.accept)
        self.ok_button.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.ok_button)
        
        self.setLayout(layout)

    def get_category_name(self)-> str:
        """Возвращает название новой категории."""
        return self.input_field.text()
    
class EditCategoryDialog(QDialog):
    """
    Модальное окно для редактирования существующей категории.
    """
    def __init__(self, current_name:str, parent: Optional[QWidget]= None)->None:
        super().__init__(parent)
        self.setWindowTitle('edit category')
        
        self.input_field = QLineEdit(current_name)
        self.ok_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ok_button.accepted.connect(self.accept)
        self.ok_button.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.ok_button)
        
        self.setLayout(layout)
    def get_new_category_name(self)->str:
        """Возвращает название новой категории."""
        return self.input_field.text()
class CategoryWindow(QWidget):
    """Окно для управления категориями."""
    def __init__(self)->None:
        super().__init__()
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(['Категории'])

        self.add_button = QPushButton('Добавить')
        self.add_button.clicked.connect(self.add_category_dialog)
        
        self.edit_button = QPushButton('Переименовывать')
        self.edit_button.clicked.connect(self.rename_category_dialog)

        self.delete_button = QPushButton('Удалить')
        self.delete_button.clicked.connect(self.delete_category)

        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.add_button)
        
        self.setLayout(layout)

        self.categories = {
            'parent1':[],
            'parent2': [],
            'parent3': ['child5', 'child6']
        }

        self.selected_item = None
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.populate_tree()

    
    
    def add_category_dialog(self)->None:
        """Отображает диалог для добавления новой категории."""
        if self.selected_item is not None:
            dialog = AddCategoryDialog(self)
            if dialog.exec() == QDialog.Accepted:
                category_name = dialog.get_category_name()
                if category_name:
                    child_item = QTreeWidgetItem([category_name])
                    self.selected_item.addChild(child_item)
                    self.selected_item.setExpanded(True)

    def on_item_clicked(self, item: QTreeWidgetItem)-> None:
        """Обрабатывает событие нажатия на элемент."""
        self.selected_item = item


    def rename_category_dialog(self)-> None:
        if self.selected_item is not None:
            current_name = self.selected_item.text(0)
            if self.selected_item.parent() is None:
                # Если выбранный элемент является корневым элементом, показываем модальное окно
                show_warning_dialog("Нельзя изменить название корневого элемента.")

            else:
                # Иначе открываем диалог редактирования категории
                dialog = EditCategoryDialog(current_name, self)
                if dialog.exec() == QDialog.Accepted:
                    new_category_name = dialog.get_new_category_name()
                    if new_category_name:
                        self.selected_item.setText(0, new_category_name)
    
    def populate_tree(self)->None:
        """ Дерево категорий """
        self.tree.clear()
        root_item = QTreeWidgetItem(['categories'])
        self.tree.addTopLevelItem(root_item)
        for category, values in self.categories.items():
            item = QTreeWidgetItem([category])
            root_item.addChild(item)
            self.create_items(values, item)
        

    def create_items(self, categories: List[str], parent_item: QTreeWidgetItem)->None:
        """ Создавать элементы-потомков для parent_item """
        for category in categories:
            item = QTreeWidgetItem([category])
            parent_item.addChild(item)

    def delete_category(self)->None:
        """ Удалить выбранную категорию"""
        if self.selected_item is not None:
            parent_item = self.selected_item.parent()
            if parent_item is not None:
                parent_index = parent_item.indexOfChild(self.selected_item)
                if parent_index >= 0:
                    parent_item.takeChild(parent_index)
                    # Удалить категорию из списка категорий на уровне родителя
                    parent_category = parent_item.text(0)
                    self.remove_category_from_parent(parent_category)
            else:
                show_warning_dialog('Нельзя удалить корневой элемент')


    def remove_category_from_parent(self, parent_category:str)->None:
        """Удалить категорию из списка категорий на уровне родителя """
        if parent_category in self.categories:
            if self.selected_item.text(0) in self.categories[parent_category]:
                self.categories[parent_category].remove(self.selected_item.text(0))
def get_categories(cat_repo: SQLiteRepository)->List[str]:
    """
    Получить список категорий из репозитория
    """
    categories = cat_repo.get_all()
    dict_categories = {}
    for category in categories:
        
        dict_categories[category.name] = category.pk
    return dict_categories


def list_category_widget(cat_repo: SQLiteRepository)-> QHBoxLayout:
    """
    Отображает список категорий в главном окне
    """
    ls_categories = get_categories(cat_repo).keys()
    combobox = QComboBox()
    combobox.addItems(ls_categories)
    return h_widget_with_label('Категории', combobox)


if __name__ == '__main__':
    
    app = QApplication([])
    window = CategoryWindow()
    window.show()
    app.exec()