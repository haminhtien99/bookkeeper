import sys
from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QPushButton, QVBoxLayout, QWidget

def removeNodeAndKeepChildren(treeWidget, node):
    # Lấy vị trí của nút trong cây
    nodeIndex = treeWidget.indexOfTopLevelItem(node)

    # Nếu không phải là nút gốc thì không thể xóa
    if nodeIndex == -1:
        return

    # Di chuyển tất cả các nút con của nút được xóa lên một cấp độ
    while node.childCount() > 0:
        childItem = node.takeChild(0)
        treeWidget.insertTopLevelItem(nodeIndex, childItem)

    # Xóa nút gốc
    treeWidget.takeTopLevelItem(nodeIndex)

def main():
    app = QApplication(sys.argv)

    # Tạo cây QTreeWidget
    treeWidget = QTreeWidget()
    treeWidget.setColumnCount(1)  # Chỉ cần một cột để hiển thị

    # Tạo nút gốc và thêm vào cây
    rootNode1 = QTreeWidgetItem(treeWidget)
    rootNode1.setText(0, "Root Node 1")

    # Thêm một số nút con cho nút gốc 1
    for i in range(3):
        childNode = QTreeWidgetItem(rootNode1)
        childNode.setText(0, f"Child Node 1-{i+1}")
        # Thêm một số nút con cho mỗi nút con của nút gốc 1
        for j in range(2):
            grandChildNode = QTreeWidgetItem(childNode)
            grandChildNode.setText(0, f"Grandchild Node 1-{i+1}-{j+1}")

    # Hiển thị cây
    treeWidget.show()

    # Tạo một nút xóa để thử nghiệm
    removeButton = QPushButton("Remove Root Node 1")
    removeButton.clicked.connect(lambda: removeNodeAndKeepChildren(treeWidget, rootNode1))

    # Tạo layout chứa cây và nút xóa
    layout = QVBoxLayout()
    layout.addWidget(treeWidget)
    layout.addWidget(removeButton)

    # Tạo một widget gốc và thiết lập layout của nó
    widget = QWidget()
    widget.setLayout(layout)
    widget.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()