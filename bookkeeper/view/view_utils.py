from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, \
                               QLabel, QTableWidgetItem, QPushButton,QDialog)



def show_warning_dialog(message: str)-> None:
    """Отображает диалог предупреждения."""
    dialog = QDialog()
    dialog.setWindowTitle("Внимание")
    dialog.resize(100, 80)
    label = QLabel(message)
    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)
    layout = QVBoxLayout()
    layout.addWidget(label)
    layout.addWidget(ok_button)
    dialog.setLayout(layout)
    dialog.exec()


def set_data(tableWidget, data: list[list[str]])->None:
    """
    Устанавливает данные в таблицу.
    """
    for i, row in enumerate(data):
        for j, x in enumerate(row):
            tableWidget.setItem(i, j, QTableWidgetItem(x.capitalize()))

def h_widget_with_label(text:str, widget:QWidget)->QHBoxLayout:
    """
    Возвращает горизонтальную раскладку, содержащую текст и виджет.
    """
    hl = QHBoxLayout()
    hl.addWidget(QLabel(text))
    hl.addWidget(widget)
    return hl
def v_widget_with_label(text:str, widget:QWidget)->QVBoxLayout:
    """
    Возвращает вертикальную раскладку, содержащую текст и виджет.
    """
    hl = QVBoxLayout()
    hl.addWidget(QLabel(text))
    hl.addWidget(widget)
    return hl