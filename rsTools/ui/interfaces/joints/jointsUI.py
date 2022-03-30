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
from rsTools.ui.widgets.folderSelectWidget import FolderSelectWidget
from rsTools.ui.widgets.customImageWidget import CustomImageWidget
import rsTools.utils.osUtils.enviroments as env
import rsTools.utils.transforms.transforms as tUtils


#from .enviromentPage import EnviromentPageWidget
from rsTools.ui.interfaces.hub._hubEnviromentMenu import hubProjectMenu
from rsTools.ui.interfaces.hub._hubEnviromentMenu import hubProjectRootMenu
from rsTools.ui.interfaces.hub._hubEnviromentMenu import hubProjectAsset

from rsTools.utils.osUtils import shotBuild
from rsTools.utils.osUtils import osUtils
from rsTools.ui.widgets.stateDrivenWidgets.pickerWidget import PickerWidget


from rsTools.utils.openMaya import matrix, mesh, omWrappers, transform, curve
from rsTools.utils import joint


import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

header = {"textSize": 13,
          "textAlign": QtCore.Qt.AlignLeft,
          "background": False
          }

subHeader = {"textSize": 10,
             "textAlign": QtCore.Qt.AlignLeft,
             "background": False,
             "color": [255, 255, 0]
             }

__style__ = '''
                QGroupBox { 
                    background-color: rgba(100,160,200,15); 
                    padding-top:5px; 
                    border-radius: 6px; 
                    margin-top: 0.5em;
                }  '''


class JointUI(QtWidgets.QDialog):

    WINDOW_TITLE = "Joint Utils"

    def __init__(self, parent=qtWrap.getMayaMainWindow()):
        super(JointUI, self).__init__(parent)

        self.setObjectName("Joint Utils")
        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^
                                QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self._w = 500
        self._h = 200
        _r = float(self._w)/32.0

        self._mainButtonWidgets = list()

        self.setMinimumSize(self._w, self._h)

        self._page = 0

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):

        # create the side panel buttons
        self.createButtonPanelWidgets(["Create", "Orient", "Rename", "Extras"])

        # create all the widgets and stacked widgets
        self.createPageWidget = QtWidgets.QWidget()
        self.orientPageWidget = QtWidgets.QWidget()
        self.renamePageWidget = QtWidgets.QWidget()
        self.extrasPageWidget = QtWidgets.QWidget()

        self.stackedWidget = QtWidgets.QStackedWidget(self)
        self.stackedWidget.addWidget(self.createPageWidget)
        self.stackedWidget.addWidget(self.orientPageWidget)
        self.stackedWidget.addWidget(self.renamePageWidget)
        self.stackedWidget.addWidget(self.extrasPageWidget)

        self.buildCreateUI()
        self.buildOrientUI()
        self.buildRenameUI()
        self.buildExtrasUI()

        cmds.toggleAxis()

    def create_layout(self):

        self.createButtonPanelLayout()
        self._boxGroup.setLayout(self._mainButtonLayout)

        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.addWidget(self._boxGroup)
        self.mainLayout.addWidget(self.stackedWidget)

    def createButtonPanelWidgets(self, buttonLabels=None):

        self._boxGroup = QtWidgets.QGroupBox()
        self._boxGroup.setStyleSheet('''
                                        QGroupBox { 
                                            background-color: rgba(100,150,200,20); 
                                            padding-top:5px; 
                                            border-radius: 6px; 
                                            margin-top: 0.5em;
                                        }  ''')

        for i, name in enumerate(buttonLabels):
            widget = QtWidgets.QPushButton(name)
            widget.setCheckable(True)
            widget.setMinimumSize(50, self.height()/len(buttonLabels)*1.5)
            widget.clicked.connect(partial(self.event_setPage, i))
            self._mainButtonWidgets.append(widget)

            widget.setStyleSheet('''
                                            QPushButton { 
                                                background-color: rgba(100,150,200,20); 
                                                padding-top:5px; 
                                                border-radius: 2px; 
                                                margin-top: 0.5em;
                                            }  
                                            
                                            QPushButton::checked
                                            {
                                                background-color: rgba(200,150,200,50); 
                                            }
                                            
                                            ''')

    def createButtonPanelLayout(self):
        self._mainButtonLayout = QtWidgets.QVBoxLayout()
        for w in self._mainButtonWidgets:
            self._mainButtonLayout.addWidget(w)
        return self._mainButtonLayout

    def event_setPage(self, pageNum):
        self._page = pageNum

        for w in self._mainButtonWidgets:
            if not w == self._mainButtonWidgets[pageNum]:
                w.setChecked(False)

        self.populatePage(self._page)

    def populatePage(self, pageNum):
        self.stackedWidget.setCurrentIndex(pageNum)

    def buildCreateUI(self):
        # widgets
        kwargs = {"textSize": 13,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False
                  }

        __style__ = '''
                                        QGroupBox { 
                                            background-color: rgba(100,160,200,15); 
                                            padding-top:5px; 
                                            border-radius: 6px; 
                                            margin-top: 0.5em;
                                        }  '''

        mainLayout = QtWidgets.QVBoxLayout()

        boxGroupSelect = QtWidgets.QGroupBox()
        boxGroupSelect.setStyleSheet(__style__)

        boxGroupTwoPos = QtWidgets.QGroupBox()
        boxGroupTwoPos.setStyleSheet(__style__)

        boxGroupCurve = QtWidgets.QGroupBox()
        boxGroupCurve.setStyleSheet(__style__)

        boxGroupSelectOrient = QtWidgets.QGroupBox()
        boxGroupSelectOrient.setStyleSheet(__style__)

        # join select
        self.create_jointSelectLabel = CustomImageWidget(250, 22, text="Selection:", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **kwargs)
        self.create_button_jointSelect = QtWidgets.QPushButton("Build")
        jointSelectLayout = QtWidgets.QHBoxLayout()
        jointSelectLayout.addWidget(self.create_jointSelectLabel)
        jointSelectLayout.addWidget(self.create_button_jointSelect)
        boxGroupSelect.setLayout(jointSelectLayout)

        self.create_jointTwoPosLabel = CustomImageWidget(250, 22, text="Two Point Selection:", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **kwargs)

        self.create_lineEdit_jointTwoPos = QtWidgets.QLineEdit()
        self.create_lineEdit_jointTwoPos.setPlaceholderText("Num Of Joints")
        rx = QtCore.QRegExp("[0-9]+")
        validator = QtGui.QRegExpValidator(rx, self)
        self.create_lineEdit_jointTwoPos.setValidator(validator)
        self.create_lineEdit_jointTwoPos.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.create_button_jointTwoPos = QtWidgets.QPushButton("Build")
        jointTwoPLayout = QtWidgets.QHBoxLayout()
        jointTwoPLayout.addWidget(self.create_jointTwoPosLabel)
        jointTwoPLayout.addWidget(self.create_lineEdit_jointTwoPos)
        jointTwoPLayout.addWidget(self.create_button_jointTwoPos)
        boxGroupTwoPos.setLayout(jointTwoPLayout)

        self.create_jointCurveLabel = CustomImageWidget(250, 22, text="Along Curve:", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **kwargs)

        self.create_jointCurveLine = QtWidgets.QLineEdit()
        self.create_jointCurveLine.setPlaceholderText("Num Of Joints")
        rx = QtCore.QRegExp("[0-9]+")
        validator = QtGui.QRegExpValidator(rx, self)
        self.create_jointCurveLine.setValidator(validator)
        self.create_jointCurveLine.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.create_button_jointCurve = QtWidgets.QPushButton("Build")
        jointCurveLayout = QtWidgets.QHBoxLayout()
        jointCurveLayout.addWidget(self.create_jointCurveLabel)
        jointCurveLayout.addWidget(self.create_jointCurveLine)
        jointCurveLayout.addWidget(self.create_button_jointCurve)
        boxGroupCurve.setLayout(jointCurveLayout)

        # join select
        self.create_jointSelectOrientLabel = CustomImageWidget(250, 22, text="Selection (Orient) :", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **kwargs)
        self.create_button_jointSelectOrient = QtWidgets.QPushButton("Build")
        jointSelectOrientLayout = QtWidgets.QHBoxLayout()
        jointSelectOrientLayout.addWidget(self.create_jointSelectOrientLabel)
        jointSelectOrientLayout.addWidget(self.create_button_jointSelectOrient)
        boxGroupSelectOrient.setLayout(jointSelectOrientLayout)

        mainLayout.addWidget(boxGroupSelect)
        mainLayout.addWidget(boxGroupSelectOrient)
        mainLayout.addWidget(boxGroupTwoPos)
        mainLayout.addWidget(boxGroupCurve)

        mainLayout.setSpacing(5)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.createPageWidget.setLayout(mainLayout)

        self.create_button_jointCurve.clicked.connect(
            self.event_create_jointCurve)
        self.create_button_jointSelect.clicked.connect(
            self.event_create_jointSelect)
        self.create_button_jointSelectOrient.clicked.connect(
            self.event_create_jointSelectOrient)
        self.create_button_jointTwoPos.clicked.connect(
            self.event_create_jointTwoPos)

    def buildOrientUI(self):

        mainLayout = QtWidgets.QVBoxLayout()

        boxGroupOrient = QtWidgets.QGroupBox()
        boxGroupOrient.setStyleSheet(__style__)

        boxGroupOrientMatch = QtWidgets.QGroupBox()
        boxGroupOrientMatch.setStyleSheet(__style__)

        boxGroupMirror = QtWidgets.QGroupBox()
        boxGroupMirror.setStyleSheet(__style__)

        # join select
        self.orient_jointLabel = CustomImageWidget(100, 22, text="Orient:", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **header)

        self.orient_jointComboAimLabel = CustomImageWidget(70, 22, text="Aim Axis:", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **subHeader)

        self.orient_combo_jointAim = QtWidgets.QComboBox()
        self.orient_combo_jointAim.addItems(["x", "y", "z", "-x", "-y", "-z"])
        self.orient_combo_jointAim.setCurrentText("y")
        jointComboAimLayout = QtWidgets.QHBoxLayout()
        jointComboAimLayout.addWidget(self.orient_jointComboAimLabel)
        jointComboAimLayout.addWidget(self.orient_combo_jointAim)
        jointComboAimLayout.setSpacing(0)
        jointComboAimLayout.setAlignment(QtCore.Qt.AlignLeft)

        self.orient_jointComboUpLabel = CustomImageWidget(70, 22, text="Up Axis:", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **subHeader)
        self.orient_combo_jointUp = QtWidgets.QComboBox()
        self.orient_combo_jointUp.addItems(["x", "y", "z", "-x", "-y", "-z"])
        self.orient_combo_jointUp.setCurrentText("-z")
        jointComboUpLayout = QtWidgets.QHBoxLayout()
        jointComboUpLayout.addWidget(self.orient_jointComboUpLabel)
        jointComboUpLayout.addWidget(self.orient_combo_jointUp)
        jointComboUpLayout.setSpacing(0)
        jointComboUpLayout.setAlignment(QtCore.Qt.AlignLeft)

        self.orient_button_orientJoint = QtWidgets.QPushButton("Orient")

        orientJointLayout = QtWidgets.QHBoxLayout()
        orientJointLayout.addWidget(self.orient_jointLabel)
        orientJointLayout.addLayout(jointComboUpLayout)
        orientJointLayout.addLayout(jointComboAimLayout)
        orientJointLayout.addWidget(self.orient_button_orientJoint)

        boxGroupOrient.setLayout(orientJointLayout)

        # orient match
        self.orient_orientMatchLabel = CustomImageWidget(
            250, 22, text="Orient Match A->(a,b,c) :", imagePath=os.path.join(env.get_rsTools_img_path_shelf(), "default.svg"), **header)
        self.orient_button_orientMatch = QtWidgets.QPushButton("Match")

        orientMatchLayout = QtWidgets.QHBoxLayout()
        orientMatchLayout.addWidget(self.orient_orientMatchLabel)
        orientMatchLayout.addWidget(self.orient_button_orientMatch)

        boxGroupOrientMatch.setLayout(orientMatchLayout)

        # mirror chain
        self.orient_mirrorLabel = CustomImageWidget(250, 22, text="Mirror Chain :", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **header)
        self.orient_button_mirror = QtWidgets.QPushButton("Mirror")

        mirrorLayout = QtWidgets.QHBoxLayout()
        mirrorLayout.addWidget(self.orient_mirrorLabel)
        mirrorLayout.addWidget(self.orient_button_mirror)

        boxGroupMirror.setLayout(mirrorLayout)

        mainLayout.addWidget(boxGroupOrient)
        mainLayout.addWidget(boxGroupOrientMatch)
        mainLayout.addWidget(boxGroupMirror)
        mainLayout.setSpacing(5)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.orientPageWidget.setLayout(mainLayout)

        self.orient_button_mirror.clicked.connect(self.event_orient_mirror)
        self.orient_button_orientJoint.clicked.connect(
            self.event_orient_orientJoint)
        self.orient_button_orientMatch.clicked.connect(
            self.event_orient_orientMatch)

    def buildRenameUI(self):

        mainLayout = QtWidgets.QVBoxLayout()

        boxGroupRename = QtWidgets.QGroupBox()
        boxGroupRename.setStyleSheet(__style__)

        self.rename_label = CustomImageWidget(200, 22, text="Rename Chain:", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **header)

        hLayout = QtWidgets.QHBoxLayout()
        self.rename_jointComboSide = QtWidgets.QComboBox()
        self.rename_jointComboSide.setMaximumWidth(70)
        self.rename_jointComboSide.addItems(["none", "l", "r"])
        self.rename_lineEdit = QtWidgets.QLineEdit()
        self.rename_lineEdit.setPlaceholderText("BaseName")
        self.rename_lineEdit.setMaximumWidth(150)
        self.rename_jointComboSuffix = QtWidgets.QComboBox()
        self.rename_jointComboSuffix.addItems(["JNT", "FK", "IK"])
        self.rename_jointComboSuffix.setMaximumWidth(70)

        self.rename_button = QtWidgets.QPushButton("Rename")

        hLayout.addWidget(self.rename_jointComboSide)
        hLayout.addWidget(self.rename_lineEdit)
        hLayout.addWidget(self.rename_jointComboSuffix)
        hLayout.addWidget(self.rename_button)
        hLayout.setAlignment(QtCore.Qt.AlignLeft)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.rename_label)
        layout.addLayout(hLayout)
        layout.setSpacing(10)

        boxGroupRename.setLayout(layout)

        mainLayout.addWidget(boxGroupRename)
        mainLayout.setSpacing(5)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.renamePageWidget.setLayout(mainLayout)

        self.rename_button.clicked.connect(self.event_rename_button)

    def buildExtrasUI(self):

        mainLayout = QtWidgets.QVBoxLayout()

        boxGroupLRA = QtWidgets.QGroupBox()
        boxGroupLRA.setStyleSheet(__style__)

        boxGroupPolyLRA = QtWidgets.QGroupBox()
        boxGroupPolyLRA.setStyleSheet(__style__)

        # join select
        self.extras_lra_label = CustomImageWidget(200, 22, text="Local Rotation Axis :", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **header)

        self.extras_lra_enable = QtWidgets.QPushButton("Enable")
        self.extras_lra_disable = QtWidgets.QPushButton("Disable")

        extras_lra_layout = QtWidgets.QHBoxLayout()
        extras_lra_layout.addWidget(self.extras_lra_label)
        extras_lra_layout.addWidget(self.extras_lra_disable)
        extras_lra_layout.addWidget(self.extras_lra_enable)
        extras_lra_layout.setSpacing(10)
        boxGroupLRA.setLayout(extras_lra_layout)

        # joint cones
        self.extras_lraCones_label = CustomImageWidget(200, 22, text="Joint Cones :", imagePath=os.path.join(
            env.get_rsTools_img_path_shelf(), "default.svg"), **header)
        self.extras_lraCones_enable = QtWidgets.QPushButton("Create")

        extras_lraCones_layout = QtWidgets.QHBoxLayout()
        extras_lraCones_layout.addWidget(self.extras_lraCones_label)
        extras_lraCones_layout.addWidget(self.extras_lraCones_enable)

        boxGroupPolyLRA.setLayout(extras_lraCones_layout)

        mainLayout.addWidget(boxGroupLRA)
        mainLayout.addWidget(boxGroupPolyLRA)
        mainLayout.setSpacing(5)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.extrasPageWidget.setLayout(mainLayout)

    def event_create_jointCurve(self):
        ls = cmds.ls(sl=True)
        numJoints = self.create_jointCurveLine.text()
        #numJoints = int(numJoints)
        if ls and numJoints:
            if curve.isCurve(ls[0]):
                joint.createJointAlongCurve(str(ls[0]), int(numJoints))

    def event_create_jointSelect(self):
        ls = cmds.ls(sl=True, fl=True)
        if len(ls) == 1:
            joint.createJointAtObject(str(ls[0]), r=False)
        else:
            joint.createJointAtObject(ls, r=False)

    def event_create_jointSelectOrient(self):
        ls = cmds.ls(sl=True, fl=True)
        if len(ls) == 1:
            joint.createJointAtObject(str(ls[0]), r=True)
        else:
            joint.createJointAtObject(ls, r=True)

    def event_create_jointTwoPos(self):
        ls = cmds.ls(sl=True, fl=True)
        numJoints = self.create_lineEdit_jointTwoPos.text()

        if len(ls) > 1 and numJoints:
            joint.createJointBetweenTwoObjects(ls[0], ls[1], int(numJoints))

    def event_orient_mirror(self):
        ls = cmds.ls(sl=True, fl=True)
        if ls:
            if len(ls) == 1:
                joint.mirrorJointChain(str(ls[0]))
            else:
                for l in ls:
                    joint.mirrorJointChain(l)

    def event_orient_orientJoint(self):
        ls = cmds.ls(sl=True, fl=True)
        up = self.orient_combo_jointUp.currentText()
        aim = self.orient_combo_jointAim.currentText()
        if ls:
            if ls:
                if len(ls) == 1:
                    joint.orientChain(str(ls[0]), up, aim)
                else:
                    for l in ls:
                        joint.orientChain(l, up, aim)

    def event_orient_orientMatch(self):
        ls = cmds.ls(sl=True, fl=True)
        if ls:
            if len(ls) >= 2:
                targets = ls[1:]
                for t in targets:
                    joint.orientMatch(t, ls[0])

                cmds.select(ls[-1], r=True)

    def event_rename_button(self):

        prefix = self.rename_jointComboSide.currentText()
        suffix = self.rename_jointComboSuffix.currentText()
        coreName = self.rename_lineEdit.text()
        if prefix == "none":
            prefix = None

        ls = cmds.ls(sl=True, fl=True)
        if ls and coreName:
            joint.renameChain(ls[0], prefix=prefix,
                              coreName=coreName, suffix=suffix)


jointUI = None


def run():
    global jointUI
    if jointUI:
        jointUI.close()
    jointUI = JointUI(parent=qtWrap.getMayaMainWindow())
    jointUI.show()


if __name__ == "__main__":

    try:
        jointUI.close()  # pylint: disable=E0601
        jointUI.deleteLater()
    except:
        pass

    jointUI = JointUI()
    jointUI.show()
