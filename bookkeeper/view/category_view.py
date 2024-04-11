"""
Виджет для показа списка категорий
"""
import sys
from PySide6 import QtWidgets
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.utils import show_warning_dialog, create_table_db
from bookkeeper.models.category import Category
from bookkeeper.view.category_dialogs import (AddCategoryDialog,
                                              EditCategoryDialog,
                                              DeleteConfirmationDialog)
class CategoryWindow(QtWidgets.QWidget):
    """Окно для управления категориями."""
    def __init__(self, cat_mem_repo: MemoryRepository[Category]) -> None:
        super().__init__()
        self.setWindowTitle('Категории')
        self.cat_mem_repo = cat_mem_repo
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
        self.deleted_cat = []
    def build_tree(self)->None:
        """ Дерево категорий """
        self.tree.clear()
        top_categories = self.cat_mem_repo.get_all(where={'parent':None})
        def build(parent_item:QtWidgets.QTreeWidgetItem, category:Category):
            """Дерево категорий первого уровня"""
            category_item = QtWidgets.QTreeWidgetItem(parent_item, [category.name])
            category_children = self.cat_mem_repo.get_all(where={'parent':category.pk})
            for sub_category in category_children:
                build(category_item, sub_category)
        for top_cat in top_categories:
            build(self.tree, top_cat)
    def edit_button_click(self)-> None:
        """Отображает диалог для редактирования существующей категории."""
        selected_item = self.tree.currentItem()
        if selected_item is not None:
            current_name = selected_item.text(0)
            selected_cat = self.cat_mem_repo.get_all(where={'name':current_name})[0]
            dialog = EditCategoryDialog(current_name, self)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                new_category_name = dialog.get_new_category_name()
                if new_category_name == current_name:
                    show_warning_dialog(message=' Нет изменений',
                                        title = 'Update category')
                elif self.check_new_name(new_category_name) is False:
                    show_warning_dialog(message='Название существует',
                                        title = 'Update category')
                else:
                    selected_item.setText(0, new_category_name)
                    selected_cat.name = new_category_name
                    self.cat_mem_repo.update(selected_cat)
    def add_button_click(self)->None:
        """Отображает диалог для добавления новой под-категории."""
        selected_item = self.tree.currentItem()
        if selected_item is not None:
            dialog = AddCategoryDialog(self)
            selected_name = selected_item.text(0)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                sub_category_name = dialog.get_category_name()
                if sub_category_name.strip():
                    if self.check_new_name(sub_category_name):
                        child_item = QtWidgets.QTreeWidgetItem([sub_category_name])
                        selected_item.addChild(child_item)
                        selected_item.setExpanded(True)
                        selected_cat = self.cat_mem_repo.get_all(where={'name':selected_name})[0]
                        category = Category(name = sub_category_name,
                                            parent = selected_cat.pk)
                        self.cat_mem_repo.add(category)
                    else:
                        show_warning_dialog(message='Название существовал',
                                            title = 'Add Category')
                else:
                    show_warning_dialog(message='Название не может быть пустым',
                                    title = 'Add Category')
    def add_button_root_click(self)-> None:
        """Отображает диалог для добавления новой категории первого уровня."""
        dialog = AddCategoryDialog(self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            sub_category_name = dialog.get_category_name()
            if sub_category_name.strip():
                if self.check_new_name(sub_category_name):
                    item = QtWidgets.QTreeWidgetItem(self.tree)
                    item.setText(0,sub_category_name)
                    category = Category(name = sub_category_name,
                                        parent = None)
                    self.cat_mem_repo.add(category)
                else:
                    show_warning_dialog(message='Название существовал',
                                        title = 'Add Category to Root')
            else:
                show_warning_dialog(message='Название не может быть пустым',
                                    title = 'Add Category to Root')
    def delete_button_click(self) ->None:
        """
        Диалог для удаления
        -----
        Если ветка не имеет дочерных узлов, удалить ее обычном способом,
        pk следующих (и возможно, их ) категорий уменьшается на 1 единицу
        Если дочерный узел существует, есть два варианта: удалить или оставить их.
        При удалении каждого узла, 
        сохранить информацию self.deleted_cat для обнавления таблицы расхода
        """
        selected_item = self.tree.currentItem()
        if selected_item is None:
            show_warning_dialog(message='Выбери категорию')
            return
        if selected_item.childCount() == 0:
            parent = selected_item.parent()
            if parent is not None:
                parent.removeChild(selected_item)
            else:
                index = self.tree.indexOfTopLevelItem(selected_item)
                self.tree.takeTopLevelItem(index)
            selected_name = selected_item.text(0)
            selected_cat = self.cat_mem_repo.get_all(where={'name': selected_name})[0]
            self.delele_cat(selected_cat)
            show_warning_dialog(message='Удалена')
            return
        dialog = DeleteConfirmationDialog(self)
        if dialog.exec():
            result = dialog.result
            selected_name = selected_item.text(0)
            selected_cat = self.cat_mem_repo.get_all(where={'name': selected_name})[0]
            if result == 'Delete All Children':
                parent = selected_item.parent()
                ls_child_items = self.get_all_children(selected_item)
                if parent is not None:
                    parent.removeChild(selected_item)
                else:
                    index = self.tree.indexOfTopLevelItem(selected_item)
                    self.tree.takeTopLevelItem(index)
                for item in ls_child_items:
                    item_name = item.text(0)
                    cat = self.cat_mem_repo.get_all(where={'name': item_name})[0]
                    self.delele_cat(cat)
            elif result == 'Delete Only This':
                parent = selected_item.parent()
                if parent is not None:
                    parent.removeChild(selected_item)
                    while selected_item.childCount() > 0:
                        child = selected_item.takeChild(0)
                        parent.addChild(child)
                else:
                    index = self.tree.indexOfTopLevelItem(selected_item)
                    self.tree.takeTopLevelItem(index)
                for child in self.cat_mem_repo.get_all(where={'parent':selected_cat.pk}):
                    child.parent = selected_cat.parent
                self.delele_cat(selected_cat)
            show_warning_dialog(message='Удалена')
    def check_new_name(self, name: str) -> bool:
        """
        Проверить, существует ли название в категориях
        """
        for cat in self.cat_mem_repo.get_all():
            if cat.name == name:
                return False
        return True
    def delele_cat(self, selected_cat: Category) -> None:
        """
        Удалить категорию и обновить репозиторию категорий
        """
        for cat in self.cat_mem_repo.get_all():
            if cat.pk > selected_cat.pk:
                cat.pk -= 1 
                if cat.parent != None and selected_cat.parent != None:
                    if cat.parent > selected_cat.parent:
                        if cat.parent > 1:
                            cat.parent -= 1
                        else: cat.parent = None
                self.cat_mem_repo.update(cat)
        self.cat_mem_repo.delete(pk=len(self.cat_mem_repo.get_all()))
        self.deleted_cat.append(selected_cat.pk)
    def get_all_children(self, item):
        """
        Получить все дочерние элементы в QTreeWidgetItem
        """
        children = []
        child_count = item.childCount()
        for i in range(child_count):
            child = item.child(i)
            children.append(child)
            children.extend(self.get_all_children(child))
        return children
if __name__ == '__main__':
    """
    Проверить работу CategoryWindow
    """
    DB_FILE = 'bookkeeper/view/new_database.db'
    category_repo = SQLiteRepository(db_file=DB_FILE, cls=Category)
    create_table_db(db_file=DB_FILE, cls=Category) # if table is not existing
    category_mem_repo = MemoryRepository[Category]()
    for cat in category_repo.get_all():
        cat.pk = 0
        category_mem_repo.add(cat)
    app = QtWidgets.QApplication(sys.argv)
    window = CategoryWindow(category_mem_repo)
    window.show()
    sys.exit(app.exec())
