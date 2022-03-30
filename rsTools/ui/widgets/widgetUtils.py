from Qt import QtCore, QtGui, QtWidgets


def nameExistsInTreeWidget(name, treeWidget):
    iterator = QtWidgets.QTreeWidgetItemIterator(treeWidget)
    while iterator.value():
        item = iterator.value()
        if item.text(0) == name:
            return True
        iterator += 1

    return False


def printWidgetChildren(widget):
    children = widget.children()
    print("------------------------------------")
    for child in children:
        print(child)
        print(child.objectName())
        print("---")
    print("------------------------------------")
