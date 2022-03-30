from Qt import QtCore, QtGui, QtWidgets

from shiboken2 import wrapInstance
import os
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds

# get path info
from rsTools.rsGlobal import *
from rsTools.utils import nurbs
from rsTools.ui import qtWrap
from rsTools.ui.widgets import widget as rsWidget

# run UI command
win = None


def run():
    global win
    if win:
        win.close()
    win = OpenImportDialog(parent=qtWrap.getMayaMainWindow())
    win.show()


class OpenImportDialog(QtWidgets.QDialog):

    FILE_FILTERS = "Maya (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    selected_filter = "Maya (*ma *.mb)"

    def __init__(self, parent=qtWrap.getMayaMainWindow()):
        super(OpenImportDialog, self).__init__(parent)

        self.initial_directory = cmds.internalVar(userPrefDir=True)
        self.initial_color = QtGui.QColor(255, 0, 0)

        self.folderSelectWidget = {}

        self.setWindowTitle("Asset Manager")
        self.setMinimumSize(600, 300)
        self.setMaximumSize(600, 300)
        self.setWindowFlags(self.windowFlags() ^
                            QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.create_title_label()

        self.filepath_le = QtWidgets.QLineEdit()
        self.select_folder_path_btn = QtWidgets.QPushButton()
        self.select_folder_path_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.select_folder_path_btn.setToolTip("Select File")
        self.label = QtWidgets.QLabel("Folder")

        self.apply_btn = QtWidgets.QPushButton("Continue")
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_title_label(self):
        image_path = os.path.join(g_imgUI, "assetManager.png")

        image = QtGui.QImage(image_path)
        size = image.size()
        print size
        image = image.scaled(
            600, 200, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)

        self.title_label = QtWidgets.QLabel()
        self.title_label.setPixmap(pixmap)

    def show_folder_select(self):
        new_directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Root Folder", self.initial_directory)
        if new_directory:
            self.initial_directory = new_directory

    def create_layout(self):

        self.folderSelectWidget = rsWidget.createFolderSelectWidget(
            labelName="Asset Root Folder:")

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.title_label)
        main_layout.setSpacing(10)
        main_layout.addLayout(self.folderSelectWidget["layout"])
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.folderSelectWidget["button"].clicked.connect(
            self.show_folder_select)
        # self.apply_btn.clicked.connect(self.load_file)
        self.close_btn.clicked.connect(self.close)


if __name__ == "__main__":

    try:
        open_import_dialog.close()  # pylint: disable=E0601
        open_import_dialog.deleteLater()
    except:
        pass

    open_import_dialog = OpenImportDialog()
    open_import_dialog.show()
