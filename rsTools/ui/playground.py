from Qt import QtCore, QtGui, QtWidgets
from rsTools.ui.widgets.assetPickerWidget import AssetPickerWidget
from rsTools.ui.widgets.folderSelectWidget import FolderSelectWidget
from rsTools.ui.widgets.buttonStackWidget import ButtonStackWidget
from rsTools.ui.widgets.stateDrivenWidgets.pickerWidget import PickerWidget
from rsTools.ui import qtWrap
from rsTools.utils import nurbs
from rsTools.rsGlobal import *
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import os
from shiboken2 import wrapInstance
for module in sorted([mod for mod in sys.modules.keys() if mod.find("rsTools") != -1]):
    print module
    del sys.modules[module]


# get path info


class Playground(QtWidgets.QDialog):

    WINDOW_TITLE = "Widget Playground"

    def __init__(self, parent=qtWrap.getMayaMainWindow()):
        super(Playground, self).__init__(parent)

        self.setObjectName("Playground")
        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^
                                QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumSize(400, 400)
        self.setMaximumSize(400, 400)

        self.create_widgets()
        self.create_layout()
        # self.create_connections()

    def create_widgets(self):
        self._folderSelect = FolderSelectWidget()
        #text = self._folderSelect.getPlaceHolderText()
        #self._enviromentPage = EnviromentPageWidget()

        #self._buttonStack = ButtonStackWidget(layout = "vertical",labels = ["ok","cancel","maybe"],boxGroup=True)

        self._buttonStack = AssetPickerWidget()

        self._picker = PickerWidget()

        self.label = QtWidgets.QLabel("ewe")

    def create_layout(self):

        #folder_layout = QtWidgets.QHBoxLayout()
        # folder_layout.addWidget(self._folderSelect)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
       # main_layout.addWidget(self._enviromentPage)

        # self.main_layout.addWidget(self.label)
        # self.main_layout.addWidget(self._picker)
        # self.main_layout.addWidget(self._folderSelect)
        self.main_layout.addWidget(self._buttonStack)

        # main_layout.addStretch()

    '''
    def create_connections(self):
        self._folderSelect.lineEditChanged.connect(self.eventLine)
        
    def eventLine(self):
        line = self._folderSelect.getText()
        print line
'''


if __name__ == "__main__":

    try:
        test.close()  # pylint: disable=E0601
        test.deleteLater()
    except:
        pass

    test = Playground()
    test.show()
