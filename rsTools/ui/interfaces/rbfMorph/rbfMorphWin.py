import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from functools import partial
from shiboken2 import wrapInstance

# get path info
import rsTools.utils.data.osUtils as osUtils

from rsTools.glob import *
from rsTools.ui import qtWrap
from rsTools.ui.widgets.customImageWidget import CustomImageWidget
from rsTools.ui.widgets.stateDrivenWidgets.pickerWidget import PickerWidget
from rsTools.utils.transforms import nurbs

from rsTools.utils.commands.rbfMorphCommand import rbfMorph


import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class rbfMoprhWin(QtWidgets.QDialog):

    WINDOW_TITLE = "RBF Morph"

    def __init__(self, parent=qtWrap.getMayaMainWindow()):
        super(rbfMoprhWin, self).__init__(parent)

        self.setObjectName("RBF Morph")
        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^
                                QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self._w = 350
        self._h = 200
        r = float(self._w)/32.0

        self.setMinimumSize(self._w, self._h)

        self.createWidgets()
        self.createLayout()
        self.createConnections()

    def createWidgets(self):
        self._projectLabel = CustomImageWidget(
            300, 50, text="RBF MORPH", imagePath=os.path.join(g_rs_path_image_shelf, "default.svg"))

        self._pickTarget = PickerWidget(labelName="Target")
        self._pickTarget.setPlaceHolderText("select TargetMesh")
        self._pickTarget.setLineSize(260, 20)

        self._pickBase = PickerWidget(labelName="Base")
        self._pickBase.setPlaceHolderText("select BaseMesh")
        self._pickBase.setLineSize(260, 20)

        self._process = QtWidgets.QPushButton("Process")
        self._process.setMinimumHeight(40)

    def createLayout(self):
        self._labelLayout = QtWidgets.QVBoxLayout()
        self._labelLayout.addWidget(self._projectLabel)
        self._labelLayout.setContentsMargins(0, 0, 0, 0)
        self._labelLayout.setSpacing(0)
        self._labelLayout.setAlignment(QtCore.Qt.AlignTop)

        self._buttonLayout = QtWidgets.QVBoxLayout()
        self._buttonLayout.setSpacing(0)
        self._buttonLayout.setContentsMargins(0, 0, 0, 0)
        self._buttonLayout.addWidget(self._pickBase)
        self._buttonLayout.addWidget(self._pickTarget)
        self._buttonLayout.addWidget(self._process)

        # main layout
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.addLayout(self._labelLayout)
        self._layout.addLayout(self._buttonLayout)

    def createConnections(self):
        self._process.clicked.connect(self.runCommand)

    def runCommand(self):

        baseMesh = self._pickBase.getText()
        targetMesh = self._pickTarget.getText()

        sel = cmds.ls(sl=True)

        if not sel:
            _logger.warning("No Items Selected")

        rbfMorph(baseMesh, targetMesh, sel)


win = None


def run():
    global win
    if win:
        win.close()
    win = rbfMoprhWin(parent=qtWrap.getMayaMainWindow())
    win.show()


if __name__ == "__main__":

    try:
        test.close()  # pylint: disable=E0601
        test.deleteLater()
    except:
        pass

    test = rbfMoprhWin()
    test.show()
