from Qt import QtCore, QtGui, QtWidgets
from rsTools.rsGlobal import *
from rsTools.utils import catch
import rsTools.ui.qtWrap as qtWrap
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from functools import partial

'''



'''


class SimpleOutliner(QtWidgets.QDialog):

    WINDOW_TITLE = "Quick Select"

    def __init__(self, parent=qtWrap.getMayaMainWindow()):
        super(SimpleOutliner, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^
                                QtCore.Qt.WindowContextHelpButtonHint)

        self.shapeNodes = []
        self.setMinimumWidth(300)

        self.scriptJobID = -1

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        # use your own context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.clear_tree_widget()

    def create_actions(self):
        self.about_action = QtWidgets.QAction("About", self)

        self.displayShapeAction = QtWidgets.QAction("Shapes", self)
        self.displayShapeAction.setCheckable(True)
        self.displayShapeAction.setChecked(True)
        self.displayShapeAction.setShortcut(QtGui.QKeySequence("Ctrl+Shift+H"))

    def create_widgets(self):
        self.menuBar = QtWidgets.QMenuBar()
        display_menu = self.menuBar.addMenu("Display")
        display_menu.addAction(self.displayShapeAction)
        help_menu = self.menuBar.addMenu("Help")
        help_menu.addAction(self.about_action)

        self.treeWidget = QtWidgets.QTreeWidget()
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)  # multi selection
        #header = self.treeWidget.headerItem()
        #header.setText(0,"Column 0 Text")

        self.add_btn = QtWidgets.QPushButton("Add")
        self.clear_btn = QtWidgets.QPushButton("Clear")

    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.clear_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.setMenuBar(self.menuBar)
        main_layout.addWidget(self.treeWidget)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.about_action.triggered.connect(self.about)
        self.displayShapeAction.toggled.connect(self.nodesVis)

        self.treeWidget.itemCollapsed.connect(self.updateIcon)
        self.treeWidget.itemExpanded.connect(self.updateIcon)
        self.treeWidget.itemSelectionChanged.connect(self.selectTreeItems)

        self.add_btn.clicked.connect(self.add_treeItem)
        self.clear_btn.clicked.connect(self.clear_tree_widget)

    def clear_tree_widget(self):
        self.treeWidget.clear()  # make sure we clear the treeWidget
        self.shapeNodes = []

    def add_treeItem(self):
        ls = cmds.ls(sl=True)
        for name in ls:
            print name
            item = self.createItem(name)
            self.treeWidget.addTopLevelItem(item)
        self.sceneToTreeSelection()

    # creates a tree item
    def createItem(self, name):

        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            if item.text(0) == name:
                return
            iterator += 1

        item = QtWidgets.QTreeWidgetItem([name])  # add the main item
        self.addChildren(item)  # add all the children
        self.updateIcon(item)

        is_shape = catch.isShape(name)
        item.setData(0, QtCore.Qt.UserRole, is_shape)

        return item

    def addChildren(self, item):
        children = cmds.listRelatives(item.text(0), children=True)
        if children:
            for child in children:
                child_item = self.createItem(child)
                self.updateIcon(child_item)
                item.addChild(child_item)

    def updateIcon(self, item):
        object_type = ""
        object_type = catch.objectType(item.text(0))
        item.setIcon(0, QtGui.QIcon(g_icon[object_type]))

    def selectTreeItems(self):
        items = self.treeWidget.selectedItems()
        names = [w.text(0) for w in items]
        cmds.select(names, replace=True)

    def about(self):
        QtWidgets.QMessageBox.about(
            self, "About", "This is a simple about dialog")

    def nodesVis(self, visible):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            is_shape = item.data(0, QtCore.Qt.UserRole)
            if is_shape:
                item.setHidden(not visible)
            iterator += 1

    # point is where you clicked
    def show_context_menu(self, point):
        contextMenu = QtWidgets.QMenu()                 # create a menu
        # add our actions to the menu
        contextMenu.addAction(self.displayShapeAction)
        contextMenu.addSeparator()                      # add separator
        contextMenu.addAction(self.about_action)        # add another action
        # spawn the point at the global position
        contextMenu.exec_(self.mapToGlobal(point))

    def sceneToTreeSelection(self):
        ls = cmds.ls(sl=True)
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            is_sel = item.text(0) in ls
            item.setSelected(is_sel)
            iterator += 1

    def setScriptJobEnabled(self, enabled):
        if enabled and self.scriptJobID < 0:
            self.scriptJobID = cmds.scriptJob(
                event=["SelectionChanged", partial(self.sceneToTreeSelection)], protected=True)
        elif not enabled and self.scriptJobID >= 0:
            cmds.scriptJob(kill=self.scriptJobID, force=True)
            self.scriptJobID = -1

    # these are virutal functions .. attach to the showevent of the dialog
    def showEvent(self, event):
        super(SimpleOutliner, self).showEvent(event)
        self.setScriptJobEnabled(True)

    def closeEvent(self, event):
        if isinstance(self, SimpleOutliner):
            super(SimpleOutliner, self).closeEvent(event)
            self.setScriptJobEnabled(False)


if __name__ == "__main__":

    try:
        SimpleOutliner.setScriptJobEnabled(False)
        simple_outliner.close()  # pylint: disable=E0601
        simple_outliner.deleteLater()
    except:
        pass

    simple_outliner = SimpleOutliner()
    simple_outliner.show()
