import maya.cmds as cmds
import os

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from  import *
from rsTools.ui.widgets.customImageWidget import CustomImageWidget
from rsTools.ui.widgets.folderSelectWidget import FolderSelectWidget


class EnviromentPageWidget(QtWidgets.QWidget):

    lineEditChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(EnviromentPageWidget, self).__init__(parent)
        self.setObjectName("enviromentPage")
        # build guts
        self.createWidgets()
        self.createLayout()
        self.createConnections()

    def createWidgets(self):
        iconPath = os.path.join(g_imgShelf, "default.svg")
        self._imgWidget = CustomImageWidget(
            400, 200, imagePath=os.path.join(g_imgUI, "assetManager.png"))
        #self._imgWidget = CustomImageWidget(32,32,text="Hub", imagePath = os.path.join(g_imgShelf,"default.svg"))
        self._folderSelect = FolderSelectWidget(
            placeHolder="Please Enter Root Folder")

    def createLayout(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.addWidget(self._imgWidget)
        self._layout.addWidget(self._folderSelect)

    def createConnections(self):
        pass
