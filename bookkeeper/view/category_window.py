"""
Виджет для показа списка категорий
"""
import sys
from typing import List
from PySide6 import QtWidgets
from PySide6 import QtCore
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.utils import show_warning_dialog, create_table_db
from bookkeeper.models.category import Category
from bookkeeper.view.category_dialogs import (AddCategoryDialog,
                                              EditCategoryDialog,
                                              DeleteConfirmationDialog)


class CategoryWindow(QtWidgets.QMainWindow):
    """Окно для управления категориями."""
    categoryEdited = QtCore.Signal()  # Сигнал изменения данных категории

    def __init__(self, cat_mem_repo: MemoryRepository[Category]) -> None:
        super().__init__()
        self.setWindowTitle('Категории')
        self.cat_mem_repo = cat_mem_repo
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout()
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Categories"])
        self.build_tree()
        layout.addWidget(self.tree)
        edit_button = QtWidgets.QPushButton('Переименовывать')
        edit_button.clicked.connect(self.edit_button_click)
        layout.addWidget(edit_button)
        add_button = QtWidgets.QPushButton('Добавить подкатегорию')
        add_button.clicked.connect(self.add_button_click)
        add_button_root = QtWidgets.QPushButton('Добавить в корень')
        add_button_root.clicked.connect(self.add_button_root_click)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(add_button)
        hbox.addWidget(add_button_root)
        layout.addLayout(hbox)
        delete_button = QtWidgets.QPushButton('Удалить')
        delete_button.clicked.connect(self.delete_button_click)
        layout.addWidget(delete_button)
        central_widget.setLayout(layout)
        self.deleted_cat: List[int] = []
        # Диалоги редактирования категорий
        self.edit_dialog = EditCategoryDialog('', self)
        self.add_dialog = AddCategoryDialog(self)
        self.add_to_root_dialog = AddCategoryDialog(self)
        self.delete_cat_dialog = DeleteConfirmationDialog(self)

    def build_tree(self) -> None:
        """ Дерево категорий """
        self.tree.clear()
        top_categories = self.cat_mem_repo.get_all(where={'parent': None})

        def build(parent_item: QtWidgets.QTreeWidgetItem | QtWidgets.QTreeWidget,
                  category: Category) -> None:
            """Дерево категорий первого уровня"""
            category_item = QtWidgets.QTreeWidgetItem(parent_item, [category.name])
            category_children = self.cat_mem_repo.get_all(where={'parent': category.pk})
            for sub_category in category_children:
                build(category_item, sub_category)
        for top_cat in top_categories:
            build(self.tree, top_cat)

    def edit_button_click(self) -> None:
        """Отображает диалог для редактирования существующей категории."""
        selected_item = self.tree.currentItem()
        if selected_item is not None:
            current_name = selected_item.text(0)
            selected_cat = self.cat_mem_repo.get_all(where={'name': current_name})[0]
            self.edit_dialog = EditCategoryDialog(current_name, self)
            if self.edit_dialog.exec() == QtWidgets.QDialog.Accepted:
                new_category_name = self.edit_dialog.get_new_category_name()
                if new_category_name == current_name:
                    show_warning_dialog(message=' Нет изменений',
                                        title='Update category')
                elif self.check_new_name(new_category_name) is False:
                    show_warning_dialog(message='Название существует',
                                        title='Update category')
                else:
                    selected_item.setText(0, new_category_name)
                    selected_cat.name = new_category_name
                    self.cat_mem_repo.update(selected_cat)
                    self.categoryEdited.emit()

    def add_button_click(self) -> None:
        """Отображает диалог для добавления новой под-категории."""
        selected_item = self.tree.currentItem()
        if selected_item is not None:
            self.add_dialog = AddCategoryDialog(self)
            selected_name = selected_item.text(0)
            if self.add_dialog.exec() == QtWidgets.QDialog.Accepted:
                sub_category_name = self.add_dialog.get_category_name()
                if sub_category_name.strip():
                    if self.check_new_name(sub_category_name):
                        child_item = QtWidgets.QTreeWidgetItem([sub_category_name])
                        selected_item.addChild(child_item)
                        selected_item.setExpanded(True)
                        where = {'name': selected_name}
                        selected_cat = self.cat_mem_repo.get_all(where=where)[0]
                        category = Category(name=sub_category_name,
                                            parent=selected_cat.pk)
                        self.cat_mem_repo.add(category)
                        self.categoryEdited.emit()
                    else:
                        show_warning_dialog(message='Название существовал',
                                            title='Add SubCategory')
                else:
                    show_warning_dialog(message='Название не может быть пустым',
                                        title='Add SubCategory')

    def add_button_root_click(self) -> None:
        """Отображает диалог для добавления новой категории первого уровня."""
        self.add_to_root_dialog = AddCategoryDialog(self)
        if self.add_to_root_dialog.exec() == QtWidgets.QDialog.Accepted:
            sub_category_name = self.add_to_root_dialog.get_category_name()
            if sub_category_name.strip():
                if self.check_new_name(sub_category_name):
                    new_item = QtWidgets.QTreeWidgetItem(self.tree)
                    new_item.setText(0, sub_category_name)
                    self.tree.insertTopLevelItem(0, new_item)
                    category = Category(name=sub_category_name,
                                        parent=None)
                    self.cat_mem_repo.add(category)
                    self.categoryEdited.emit()
                else:
                    show_warning_dialog(message='Название существовал',
                                        title='Add Category to Root')
            else:
                show_warning_dialog(message='Название не может быть пустым',
                                    title='Add Category to Root')

    def delete_button_click(self) -> None:
        """
        Диалог для удаления
        -----
        Если ветка не имеет дочерных узлов, удалить ее обычном способом
        Если дочерный узел существует, есть два варианта: удалить или оставить их.
        При удалении каждого узла,
        сохранить информацию self.deleted_cat для обнавления таблицы расхода
        """
        selected_item = self.tree.currentItem()
        if selected_item is None:
            show_warning_dialog(message='Выбери категорию')
            return
        # Удаление категории без дочерних
        if selected_item.childCount() == 0:
            parent = selected_item.parent()
            if parent is not None:
                parent.removeChild(selected_item)
            else:
                index = self.tree.indexOfTopLevelItem(selected_item)
                self.tree.takeTopLevelItem(index)
            selected_name = selected_item.text(0)
            selected_cat = self.cat_mem_repo.get_all(where={'name': selected_name})[0]
            self.deleted_cat = [selected_cat.pk]
            self.cat_mem_repo.delete(selected_cat.pk)
            self.update_cat_mem_repo()
            self.categoryEdited.emit()
            show_warning_dialog(message='Удалена')
            return
        # Удаление категории с дочерними
        self.delete_cat_dialog = DeleteConfirmationDialog(self)
        if self.delete_cat_dialog.exec():
            choose = self.delete_cat_dialog.choose
            selected_name = selected_item.text(0)
            selected_cat = self.cat_mem_repo.get_all(where={'name': selected_name})[0]
            if choose == 'Delete All Children':
                parent = selected_item.parent()
                if parent is not None:
                    parent.removeChild(selected_item)
                else:
                    index = self.tree.indexOfTopLevelItem(selected_item)
                    self.tree.takeTopLevelItem(index)
                for cat in selected_cat.get_subcategories(self.cat_mem_repo):
                    self.cat_mem_repo.delete(cat.pk)
                    self.deleted_cat.append(cat.pk)
                self.cat_mem_repo.delete(selected_cat.pk)
                self.update_cat_mem_repo()
                self.categoryEdited.emit()
            elif choose == 'Delete Only This':
                parent = selected_item.parent()
                for child in self.cat_mem_repo.get_all(where={'parent': selected_cat.pk}):
                    child.parent = selected_cat.parent
                self.deleted_cat = [selected_cat.pk]
                self.cat_mem_repo.delete(selected_cat.pk)
                self.update_cat_mem_repo()
                self.tree.clear()
                self.build_tree()
                self.categoryEdited.emit()
            show_warning_dialog(message='Удалена')

    def check_new_name(self, name: str) -> bool:
        """
        Проверить, существует ли название в категориях
        """
        for cat in self.cat_mem_repo.get_all():
            if cat.name == name:
                return False
        return True

    def update_cat_mem_repo(self) -> None:
        """
        Update MemoryRepository Category
        после удаления некоторой категории в QTreewidget
        """
        copy_cat_repo = self.cat_mem_repo
        self.cat_mem_repo = MemoryRepository[Category]()
        for cat in copy_cat_repo.get_all():
            old_pk = cat.pk
            cat.pk = 0
            new_pk = self.cat_mem_repo.add(cat)
            if old_pk != new_pk:
                sub_cats = copy_cat_repo.get_all(where={'parent': old_pk})
                for subcat in sub_cats:
                    subcat.parent = new_pk


if __name__ == '__main__':
    """
    Проверить работу CategoryWindow
    """
    DB_FILE = 'bookkeeper/view/new_database.db'
    category_repo: SQLiteRepository[Category] = SQLiteRepository(db_file=DB_FILE,
                                                                 cls=Category)
    create_table_db(db_file=DB_FILE, cls=Category)   # if table is not existing
    category_mem_repo = MemoryRepository[Category]()
    for cat in category_repo.get_all():
        cat.pk = 0
        category_mem_repo.add(cat)
    app = QtWidgets.QApplication(sys.argv)
    window = CategoryWindow(category_mem_repo)
    window.show()
    sys.exit(app.exec())
