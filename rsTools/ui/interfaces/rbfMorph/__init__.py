from Qt import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance
import os
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from functools import partial

# get path info
from rsTools.glob import *
from rsTools.utils import nurbs
from rsTools.ui import qtWrap
import rsTools.utils.osUtils.enviroments as env


class Hub(QtWidgets.QDialog):

    WINDOW_TITLE = "Hub"

    def __init__(self, parent=qtWrap.getMayaMainWindow()):
        super(Hub, self).__init__(parent)

        self.setObjectName("RBF Morph")
        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^
                                QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self._w = 100
        self._h = 200
        _r = float(self._w)/32.0

        self._mainButtonWidgets = list()

        self.setMinimumSize(self._w, self._h)

        self._page = 0

        self.create_widgets()
        self.create_layout()
        self.create_contextMenus()

    def create_widgets(self):
        self._projectLabel = CustomImageWidget(self.width()/2.5, 22, text="PROJECT: {0}".format(
            g_project_show), imagePath=os.path.join(g_rs_path_image_shelf, "default.svg"), **kwargs)

    def create_layout(self):
        self._labelLayout = QtWidgets.QVBoxLayout()
        self._labelLayout.addWidget(self._projectLabel)
        self._labelLayout.setContentsMargins(0, 0, 0, 0)
        self._labelLayout.setSpacing(0)
        self._labelLayout.setAlignment(QtCore.Qt.AlignCenter)

        # main layout
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.addLayout(self._labelLayout)

    ###################################################################################################
    # CONTEXT MENUS
    ###################################################################################################

    def create_contextMenus(self):
        # add the policy & requect
        self._projectLabel.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._projectLabel.customContextMenuRequested.connect(
            self.show_project_context_menu)

        # create action and action connection
        self.project_action_setProject = QtWidgets.QAction("setProject", self)
        self.project_action_createProject = QtWidgets.QAction(
            "createProject", self)
        self.project_action_setProject.triggered.connect(self.setProject)
        self.project_action_createProject.triggered.connect(self.setProject)

    def show_project_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.project_action_setProject)
        context_menu.addAction(self.project_action_createProject)
        context_menu.exec_(self.mapToGlobal(point))
        print self._page

    def show_asset_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.project_action_setProject)
        context_menu.addAction(self.project_action_createProject)
        context_menu.exec_(self.mapToGlobal(point))
        print self._page

    def setProject(self):

        self._projectLabel.setText()


win = None


def run():
    global win
    if win:
        win.close()
    win = Hub(parent=qtWrap.getMayaMainWindow())
    win.show()


if __name__ == "__main__":

    try:
        test.close()  # pylint: disable=E0601
        test.deleteLater()
    except:
        pass

    test = Hub()
    test.show()
