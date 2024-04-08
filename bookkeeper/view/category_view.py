from PySide6 import QtWidgets
import sys
from typing import Optional, List
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import show_warning_dialog, h_widget_with_label
from bookkeeper.models.category import Category
class AddCategoryDialog(QtWidgets.QDialog):
    """
    Модальное окно для добавления новой категории
    """
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None)->None:
        super().__init__(parent)
        self.setWindowTitle('Добавить категорию')
        self.input_field = QtWidgets.QLineEdit()
        self.ok_button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
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
        self.ok_button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.ok_button.accepted.connect(self.accept)
        self.ok_button.rejected.connect(self.reject)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)
    def get_new_category_name(self)->str:
        """Возвращает название новой категории."""
        return self.input_field.text()
class CategoryWindow(QtWidgets.QWidget):
    """Окно для управления категориями."""
    def __init__(self, cat_repo: SQLiteRepository[Category])->None:
        super().__init__()
        self.cat_repo = cat_repo
        if self.cat_repo.table_exists() is False:
            self.cat_repo.create_table()
        self.dict_categories = self.get_dict_categories()
        self.layout = QtWidgets.QVBoxLayout()
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Categories"])
        self.build_tree()
        self.layout.addWidget(self.tree)
        edit_button = QtWidgets.QPushButton('Переименовывать')
        edit_button.clicked.connect(self.edit_button_click)
        self.layout.addWidget(edit_button)
        add_button = QtWidgets.QPushButton('Добавить')
        add_button.clicked.connect(self.add_button_click)
        add_button_root = QtWidgets.QPushButton('Добавить в корень')
        add_button_root.clicked.connect(self.add_button_root_click)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(add_button)
        hbox.addWidget(add_button_root)
        self.layout.addLayout(hbox)
        delete_button = QtWidgets.QPushButton('Удалить')
        delete_button.clicked.connect(self.delete_button_click)
        self.layout.addWidget(delete_button)
        self.setLayout(self.layout)
        self.changes = []
        if len(self.dict_categories) == 0:
            self.max_pk = 0
        else:
            self.max_pk = max(self.dict_categories.keys())
    def get_dict_categories(self):
        """Возвращает словарь категорий."""
        return {cat.pk:cat for cat in self.cat_repo.get_all()}
    def build_tree(self)->None:
        """ Дерево категорий """
        self.tree.clear()
        root_subcategories = []
        for cat in self.dict_categories.values():
            if cat.parent is None:
                root_subcategories.append(cat)
        def build(parent_item:QtWidgets.QTreeWidgetItem, category:Category):
            category_item = QtWidgets.QTreeWidgetItem(parent_item, [category.name])
            for sub_category in category.get_children_first_node(self.cat_repo):
                build(category_item, sub_category)
        for root_sub in root_subcategories:
            build(self.tree, root_sub)
    def edit_button_click(self)-> None:
        """Отображает диалог для редактирования существующей категории."""
        selected_item = self.tree.currentItem()
        if selected_item is not None:
            current_name = selected_item.text(0)
            selected_cat = self.get_category_by_name(current_name)
            dialog = EditCategoryDialog(current_name, self)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                new_category_name = dialog.get_new_category_name()
                if new_category_name != current_name and self.check_new_name(new_category_name):
                    selected_item.setText(0, new_category_name)
                    selected_cat.name = new_category_name
                    self.dict_categories[selected_cat.pk] = selected_cat
                    self.changes.append(('update', selected_cat))
                elif new_category_name == current_name:
                    show_warning_dialog(message=' Нет изменений',
                                        title = 'Update category')
                else:
                    show_warning_dialog(message='Название существовал',
                                        title = 'Update Category')
    def add_button_click(self)->None:
        """Отображает диалог для добавления новой под-категории."""
        selected_item = self.tree.currentItem()
        if selected_item is not None:
            dialog = AddCategoryDialog(self)
            selected_name = selected_item.text(0)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                category_name = dialog.get_category_name()
                if self.check_new_name(category_name):
                    child_item = QtWidgets.QTreeWidgetItem([category_name])
                    selected_item.addChild(child_item)
                    selected_item.setExpanded(True)
                    self.max_pk += 1
                    cat = self.get_category_by_name(selected_name)
                    category = Category(name = category_name,
                                        parent = cat.pk,
                                        pk = self.max_pk)
                    self.dict_categories[self.max_pk] = category
                    self.changes.append(('add', category))
                else:
                    show_warning_dialog(message='Название существовал',
                                        title = 'Add Category')
    def add_button_root_click(self)-> None:
        """Отображает диалог для добавления новой категории первого уровня."""
        dialog = AddCategoryDialog(self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            category_name = dialog.get_category_name()
            if category_name.strip():
                if self.check_new_name(category_name):
                    item = QtWidgets.QTreeWidgetItem(self.tree)
                    item.setText(0,category_name)
                    self.max_pk += 1
                    category = Category(name = category_name,
                                        parent = None,
                                        pk = self.max_pk)
                    self.changes.append(('add', category))
                    self.dict_categories[self.max_pk] = category
                else:
                    show_warning_dialog(message='Название существовал',
                                        title = 'Add Category to Root')
            else:
                show_warning_dialog(message='Название не может быть пустым',
                                    title = 'Add Category to Root')
    def delete_button_click(self)->None:
        """ 
        Удалить выбранную категорию и все под-категории        
        """
        selected_item = self.tree.currentItem()
        if selected_item is not None:
            selected_name = selected_item.text(0)
            selected_cat = self.get_category_by_name(selected_name)
            selected_items = self.tree.selectedItems()
            if selected_items:
                selected_item = selected_items[0]  # assuming only one item is selected
                all_children = self.get_all_children(selected_item)
                child_names = [child.text(0) for child in all_children]
                self.tree.parent().removeChild(selected_item)
                self.changes.append(('delete', selected_cat.pk))
                self.dict_categories.pop(selected_cat.pk)
                for name in child_names:
                    cat = self.get_category_by_name(name)
                    self.changes.append(('delete', cat.pk))
                    self.dict_categories.pop(cat.pk)
                show_warning_dialog(message='Удалено',
                                    title = 'Delete Category')
            else:
                show_warning_dialog('No selected items')
    def save_button_click(self):
        """
        Save category
        """
        for change in self.changes:
            if change[0] == 'add':
                self.cat_repo.add(change[1])
            elif change[0] == 'update':
                self.cat_repo.update(change[1])
            elif change[0] == 'delete':
                self.cat_repo.delete(change[1])
        show_warning_dialog('Saved')
        self.changes = []
    def get_category_by_name(self, name:str):
        """
        Получить номер pk категории по названию
        """
        for cat in self.dict_categories.values():
            if cat.name == name:
                return cat
        return 0
    def check_new_name(self, name:str)-> bool:
        for cat in self.dict_categories.values():
            if cat.name == name:
                return False
        return True
    def get_all_children(self, item):
        children = []
        child_count = item.childCount()
        for i in range(child_count):
            child = item.child(i)
            children.append(child)
            children.extend(self.get_all_children(child))
        return children
def get_categories(cat_repo: SQLiteRepository[Category])->dict[str: int]:
    """
    Получить словарь из ключа и названия 
    """
    categories = cat_repo.get_all()
    dict_categories = {}
    for category in categories:
        dict_categories[category.name] = category.pk
    return dict_categories
def list_category_widget(cat_repo: SQLiteRepository[Category])-> QtWidgets.QHBoxLayout:
        """
        Отображает список категорий в виджет ComboBox
        """
        ls_categories = get_categories(cat_repo).keys()
        combobox = QtWidgets.QComboBox()
        combobox.addItems(ls_categories)
        return h_widget_with_label('Категории', combobox)
if __name__ == '__main__':
    repo = SQLiteRepository(db_file = 'bookkeeper/view/new_database.db', cls = Category)
    app = QtWidgets.QApplication(sys.argv)
    window = CategoryWindow(repo)
    save_button = QtWidgets.QPushButton('Save')
    save_button.clicked.connect(window.save_button_click)
    window.layout.addWidget(save_button)
    window.setLayout(window.layout)
    window.show()
    sys.exit(app.exec())