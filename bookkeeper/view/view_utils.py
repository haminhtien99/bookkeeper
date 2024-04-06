from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, \
                               QLabel, QTableWidgetItem, QMessageBox)



def show_warning_dialog(message: str)-> None:
    """Отображает диалог предупреждения."""
    msg_box = QMessageBox()
    msg_box.setText(message)
    msg_box.exec()


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