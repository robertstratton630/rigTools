from rsTools.utils.transform import joint
from rsTools.utils.data import string
from rsTools.utils.transforms import nurbs
from Qt import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import pymel.core as pm

from rsTools.ui.widgets.customImageWidget import CustomImageWidget

import rsTools.utils.data.curveData as curveData
import rsTools.utils.transforms.transforms as transform
import rsTools.utils.data.osUtils as osUtils

import rsTools.ui.qtWrap as qtWrap
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)



# some default settings

__boxGroupStyle__ = '''
                        QGroupBox { 
                            background-color: rgba(100,160,200,20); 
                            padding-top:5px; 
                            border-radius: 6px; 
                            margin-top: 0.5em;
                        } 
                        
                        QGroupBox::title { 
                                                    subcontrol-origin: margin; 
                                                    left: 10px; 
                                                    padding: 0 3px 0 3px;
                                            } 
                    '''

__pushButtonStyleSave__ = '''
                        QPushButton { 
                            background-color: rgba(100,200,200,100); 
                            padding:5px; 
                            border-radius: 2px; 
                        }  

                        QPushButton::pressed
                        {
                            background-color: rgba(50,50,50,50);
                            border-style: inset;
                        }
                        
                        '''

__pushButtonStyleLoad__ = '''
                        QPushButton { 
                            background-color: rgba(200,200,100,100); 
                            padding:5px; 
                            border-radius: 2px; 
                        }  

                        QPushButton::pressed
                        {
                            background-color: rgba(50,50,50,50);
                            border-style: inset;
                        }
                        
                        '''
__pushButtonStyleSelection__ = '''
                        QPushButton { 
                            background-color: rgba(50,50,50,100); 
                            padding:4px; 
                            border-radius: 10px; 
                        }  

                        QPushButton::checked
                        {
                            background-color: rgba(255,200,100,100); 
                            border-style: inset;
                        }
                        
                        '''

__pushButtonStyleRed__ = '''
                        QPushButton { 
                            background-color: rgba(250,100,100,80); 
                            padding:5px; 
                            border-radius: 2px; 
                        }  

                        QPushButton::pressed
                        {
                            background-color: rgba(50,50,50,50);
                            border-style: inset;
                        }
                        
                        '''


header = {"textSize": 13,
          "textAlign": QtCore.Qt.AlignLeft,
          "background": False
          }

subHeader = {"textSize": 10,
             "textAlign": QtCore.Qt.AlignLeft,
             "background": False,
             "color": [255, 255, 0]
             }


# run UI command
jointPoseUIRun = None


def run():
    global jointPoseUIRun
    if jointPoseUIRun:
        jointPoseUIRun.close()
    jointPoseUIRun = jointPoseUI()
    jointPoseUIRun.show()

# main UI class


class jointPoseUI(QtWidgets.QDialog):

    def __init__(self, parent=qtWrap.getMayaMainWindow()):
        super(jointPoseUI, self).__init__(parent)

        self._w = 200
        self._h = 500
        self.setMinimumSize(self._w, self._h)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^
                                QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        # MANY THINGS YOU HAVE TO ADD
        self.setWindowTitle("Joint Pose UI")
        self.createWidgets()
        self.createLayout()

        self._saveChildren = True
        self._loadChildren = True

        self.show()

    def createWidgets(self):
        kwargs = {"textSize": 13,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False
                  }
        self.saveLoadPoseWidget = QtWidgets.QWidget()

        self.savePoseWidget()

    def createLayout(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(self.saveLoadPoseWidget)

    def savePoseWidget(self):

        # save
        boxGroupSave = QtWidgets.QGroupBox()
        boxGroupSave.setTitle("Save")
        boxGroupSave.setStyleSheet(__boxGroupStyle__)

        saveModeLayout = QtWidgets.QHBoxLayout()
        self.savePose_button_selection = QtWidgets.QPushButton("Selection")
        self.savePose_button_children = QtWidgets.QPushButton("AllChildren")
        self.savePose_button_selection.setStyleSheet(
            __pushButtonStyleSelection__)
        self.savePose_button_children.setStyleSheet(
            __pushButtonStyleSelection__)
        self.savePose_button_selection.setCheckable(True)
        self.savePose_button_children.setCheckable(True)
        self.savePose_button_children.setChecked(True)
        saveModeLayout.addWidget(self.savePose_button_selection)
        saveModeLayout.addWidget(self.savePose_button_children)

        self.savePose_button_selection.clicked.connect(
            self.event_savePose_button_selection)
        self.savePose_button_children.clicked.connect(
            self.event_savePose_button_children)

        self.savePose_button_tPose = QtWidgets.QPushButton("Save T-Pose")
        self.savePose_button_projPose = QtWidgets.QPushButton(
            "Save Projection Pose")
        self.savePose_button_bindPose = QtWidgets.QPushButton("Save Bind Pose")

        saveABCLayout = QtWidgets.QHBoxLayout()
        self.savePose_button_aPose = QtWidgets.QPushButton("A")
        self.savePose_button_bPose = QtWidgets.QPushButton("B")
        self.savePose_button_cPose = QtWidgets.QPushButton("C")
        saveABCLayout.addWidget(self.savePose_button_aPose)
        saveABCLayout.addWidget(self.savePose_button_bPose)
        saveABCLayout.addWidget(self.savePose_button_cPose)

        self.savePose_button_tPose.setStyleSheet(__pushButtonStyleSave__)
        self.savePose_button_projPose.setStyleSheet(__pushButtonStyleSave__)
        self.savePose_button_bindPose.setStyleSheet(__pushButtonStyleSave__)
        self.savePose_button_aPose.setStyleSheet(__pushButtonStyleSave__)
        self.savePose_button_bPose.setStyleSheet(__pushButtonStyleSave__)
        self.savePose_button_cPose.setStyleSheet(__pushButtonStyleSave__)

        self.savePose_button_tPose.setProperty("save", True)
        self.savePose_button_projPose.setProperty("save", True)
        self.savePose_button_bindPose.setProperty("save", True)
        self.savePose_button_aPose.setProperty("save", True)
        self.savePose_button_bPose.setProperty("save", True)
        self.savePose_button_cPose.setProperty("save", True)

        self.savePose_button_tPose.setProperty("pose", "tPose")
        self.savePose_button_projPose.setProperty("pose", "projPose")
        self.savePose_button_bindPose.setProperty("pose", "bindPose")
        self.savePose_button_aPose.setProperty("pose", "aPose")
        self.savePose_button_bPose.setProperty("pose", "bPose")
        self.savePose_button_cPose.setProperty("pose", "cPose")

        saveLayout = QtWidgets.QVBoxLayout()
        saveLayout.addLayout(saveModeLayout)
        saveLayout.addWidget(self.savePose_button_tPose)
        saveLayout.addWidget(self.savePose_button_projPose)
        saveLayout.addWidget(self.savePose_button_bindPose)
        saveLayout.addLayout(saveABCLayout)
        saveLayout.setSpacing(4)
        saveLayout.setAlignment(QtCore.Qt.AlignTop)
        boxGroupSave.setLayout(saveLayout)

        # load
        boxGroupLoad = QtWidgets.QGroupBox()
        boxGroupLoad.setTitle("Load")
        boxGroupLoad.setStyleSheet(__boxGroupStyle__)

        loadModeLayout = QtWidgets.QHBoxLayout()
        self.loadPose_button_selection = QtWidgets.QPushButton("Selection")
        self.loadPose_button_children = QtWidgets.QPushButton("AllChildren")
        self.loadPose_button_selection.setStyleSheet(
            __pushButtonStyleSelection__)
        self.loadPose_button_children.setStyleSheet(
            __pushButtonStyleSelection__)
        self.loadPose_button_selection.setCheckable(True)
        self.loadPose_button_children.setCheckable(True)
        self.loadPose_button_children.setChecked(True)
        loadModeLayout.addWidget(self.loadPose_button_selection)
        loadModeLayout.addWidget(self.loadPose_button_children)

        self.loadPose_button_selection.clicked.connect(
            self.event_loadPose_button_selection)
        self.loadPose_button_children.clicked.connect(
            self.event_loadPose_button_children)

        self.loadPose_button_tPose = QtWidgets.QPushButton("Load T-Pose")
        self.loadPose_button_projPose = QtWidgets.QPushButton(
            "Load Projection Pose")
        self.loadPose_button_bindPose = QtWidgets.QPushButton("Load Bind Pose")

        loadABCLayout = QtWidgets.QHBoxLayout()
        self.loadPose_button_aPose = QtWidgets.QPushButton("A")
        self.loadPose_button_bPose = QtWidgets.QPushButton("B")
        self.loadPose_button_cPose = QtWidgets.QPushButton("C")
        loadABCLayout.addWidget(self.loadPose_button_aPose)
        loadABCLayout.addWidget(self.loadPose_button_bPose)
        loadABCLayout.addWidget(self.loadPose_button_cPose)

        self.loadPose_button_tPose.setProperty("save", False)
        self.loadPose_button_projPose.setProperty("save", False)
        self.loadPose_button_bindPose.setProperty("save", False)
        self.loadPose_button_aPose.setProperty("save", False)
        self.loadPose_button_bPose.setProperty("save", False)
        self.loadPose_button_cPose.setProperty("save", False)

        self.loadPose_button_tPose.setProperty("pose", "tPose")
        self.loadPose_button_projPose.setProperty("pose", "projPose")
        self.loadPose_button_bindPose.setProperty("pose", "bindPose")
        self.loadPose_button_aPose.setProperty("pose", "aPose")
        self.loadPose_button_bPose.setProperty("pose", "bPose")
        self.loadPose_button_cPose.setProperty("pose", "cPose")

        self.loadPose_button_tPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_projPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_bindPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_aPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_bPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_cPose.setStyleSheet(__pushButtonStyleLoad__)

        self.loadPose_button_tPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_projPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_bindPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_aPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_bPose.setStyleSheet(__pushButtonStyleLoad__)
        self.loadPose_button_cPose.setStyleSheet(__pushButtonStyleLoad__)

        loadLayout = QtWidgets.QVBoxLayout()
        loadLayout.addLayout(loadModeLayout)
        loadLayout.addWidget(self.loadPose_button_tPose)
        loadLayout.addWidget(self.loadPose_button_projPose)
        loadLayout.addWidget(self.loadPose_button_bindPose)
        loadLayout.addLayout(loadABCLayout)
        loadLayout.setSpacing(4)
        loadLayout.setAlignment(QtCore.Qt.AlignTop)
        boxGroupLoad.setLayout(loadLayout)

        # Utils
        utilsBoxGroup = QtWidgets.QGroupBox()
        utilsBoxGroup.setTitle("Utils")
        utilsBoxGroup.setStyleSheet(__boxGroupStyle__)

        orientModeLayout = QtWidgets.QHBoxLayout()
        self.orientPose_button_selection = QtWidgets.QPushButton("Selection")
        self.orientPose_button_children = QtWidgets.QPushButton("AllChildren")
        self.orientPose_button_selection.setStyleSheet(
            __pushButtonStyleSelection__)
        self.orientPose_button_children.setStyleSheet(
            __pushButtonStyleSelection__)
        self.orientPose_button_selection.setCheckable(True)
        self.orientPose_button_children.setCheckable(True)
        self.orientPose_button_children.setChecked(True)
        orientModeLayout.addWidget(self.orientPose_button_selection)
        orientModeLayout.addWidget(self.orientPose_button_children)
        self.orientPose_button_selection.clicked.connect(
            self.event_orientPose_button_selection)
        self.orientPose_button_children.clicked.connect(
            self.event_orientPose_button_children)

        self.utils_button_orient = QtWidgets.QPushButton("Convert To Orient")
        self.utils_button_rotation = QtWidgets.QPushButton(
            "Convert To Rotation")
        self.utils_button_mirror = QtWidgets.QPushButton("Mirror")
        self.utils_button_axisCones = QtWidgets.QPushButton("Poly Axis")

        self.utils_button_orient.setStyleSheet(__pushButtonStyleRed__)
        self.utils_button_rotation.setStyleSheet(__pushButtonStyleRed__)
        self.utils_button_mirror.setStyleSheet(__pushButtonStyleRed__)
        self.utils_button_axisCones.setStyleSheet(__pushButtonStyleRed__)

        utilsLayout = QtWidgets.QVBoxLayout()
        utilsLayout.addLayout(orientModeLayout)
        utilsLayout.addWidget(self.utils_button_orient)
        utilsLayout.addWidget(self.utils_button_rotation)
        utilsLayout.addWidget(self.utils_button_mirror)
        utilsLayout.addWidget(self.utils_button_axisCones)
        utilsLayout.setSpacing(4)
        utilsLayout.setAlignment(QtCore.Qt.AlignTop)
        utilsBoxGroup.setLayout(utilsLayout)

        # Mode
        modeBoxGroup = QtWidgets.QGroupBox()
        modeBoxGroup.setTitle("Mode")
        modeBoxGroup.setStyleSheet(__boxGroupStyle__)

        self.mode_button_t = QtWidgets.QPushButton("T")
        self.mode_button_r = QtWidgets.QPushButton("R")
        self.mode_button_s = QtWidgets.QPushButton("S")
        self.mode_button_o = QtWidgets.QPushButton("JO")

        self.mode_button_t.setCheckable(True)
        self.mode_button_r.setCheckable(True)
        self.mode_button_s.setCheckable(True)
        self.mode_button_o.setCheckable(True)

        self.mode_button_t.setChecked(True)
        self.mode_button_r.setChecked(True)
        self.mode_button_s.setChecked(True)
        self.mode_button_o.setChecked(True)

        self.mode_button_t.setStyleSheet(__pushButtonStyleSelection__)
        self.mode_button_r.setStyleSheet(__pushButtonStyleSelection__)
        self.mode_button_s.setStyleSheet(__pushButtonStyleSelection__)
        self.mode_button_o.setStyleSheet(__pushButtonStyleSelection__)

        modeLayout = QtWidgets.QHBoxLayout()
        modeLayout.addWidget(self.mode_button_t)
        modeLayout.addWidget(self.mode_button_r)
        modeLayout.addWidget(self.mode_button_s)
        modeLayout.addWidget(self.mode_button_o)
        modeLayout.setSpacing(4)
        modeLayout.setAlignment(QtCore.Qt.AlignTop)
        modeBoxGroup.setLayout(modeLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(boxGroupSave)
        mainLayout.addWidget(boxGroupLoad)
        mainLayout.addWidget(utilsBoxGroup)
        mainLayout.addWidget(modeBoxGroup)
        mainLayout.setSpacing(10)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.saveLoadPoseWidget.setLayout(mainLayout)

        # connections
        self.savePose_button_tPose.clicked.connect(self.event_pose)
        self.savePose_button_projPose.clicked.connect(self.event_pose)
        self.savePose_button_bindPose.clicked.connect(self.event_pose)
        self.savePose_button_aPose.clicked.connect(self.event_pose)
        self.savePose_button_bPose.clicked.connect(self.event_pose)
        self.savePose_button_cPose.clicked.connect(self.event_pose)

        self.loadPose_button_tPose.clicked.connect(self.event_pose)
        self.loadPose_button_projPose.clicked.connect(self.event_pose)
        self.loadPose_button_bindPose.clicked.connect(self.event_pose)
        self.loadPose_button_aPose.clicked.connect(self.event_pose)
        self.loadPose_button_bPose.clicked.connect(self.event_pose)
        self.loadPose_button_cPose.clicked.connect(self.event_pose)

        self.utils_button_orient.clicked.connect(self.event_utils_orient)
        self.utils_button_rotation.clicked.connect(self.event_utils_rotate)
        self.utils_button_mirror.clicked.connect(self.event_utils_mirror)
        self.utils_button_axisCones.clicked.connect(self.event_utils_axisCones)

    def event_loadPose_button_selection(self):
        self.loadPose_button_children.setChecked(False)
        self.loadPose_button_selection.setChecked(True)

    def event_loadPose_button_children(self):
        self.loadPose_button_children.setChecked(True)
        self.loadPose_button_selection.setChecked(False)

    def event_savePose_button_selection(self):
        self.savePose_button_children.setChecked(False)
        self.savePose_button_selection.setChecked(True)

    def event_savePose_button_children(self):
        self.savePose_button_children.setChecked(True)
        self.savePose_button_selection.setChecked(False)

    def event_orientPose_button_selection(self):
        self.orientPose_button_children.setChecked(False)
        self.orientPose_button_selection.setChecked(True)

    def event_orientPose_button_children(self):
        self.orientPose_button_children.setChecked(True)
        self.orientPose_button_selection.setChecked(False)

    def event_pose(self):
        sender = self.sender()
        save = sender.property("save")
        pose = sender.property("pose")

        t = self.mode_button_t.isChecked()
        r = self.mode_button_r.isChecked()
        s = self.mode_button_s.isChecked()
        jo = self.mode_button_o.isChecked()

        items = cmds.ls(sl=True, typ="joint")
        if len(items) == 1:
            items = items[0]

        if items:
            if save:

                choice = QtWidgets.QMessageBox()
                choice.setWindowTitle("Save {0}".format(pose))
                choice.setText(
                    "<center>Saving {0}</center> \n\n <center>Continue?</center>".format(pose))
                choice.setStandardButtons(
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                pop_up_pos = self.mapToGlobal(
                    QtCore.QPoint(self.width()*-1, 0))
                choice.move(pop_up_pos)
                YesNo = choice.exec_()

                if YesNo == QtWidgets.QMessageBox.Yes:

                    allChildren = self.savePose_button_children.isChecked()
                    if allChildren:
                        if isinstance(items, unicode):
                            items = str(items)
                        if isinstance(items, str):
                            objs = transform.findObjectsUnderNode(
                                items, "joint", match="")
                            objs.append(items)
                            jointPose.savePose(objs, poseName=pose)

                        else:
                            for i in items:
                                objs = transform.findObjectsUnderNode(
                                    i, "joint", match="")
                                objs.append(i)
                                jointPose.savePose(objs, poseName=pose)
                        _logger.info(
                            "Saved AllChildrenData for {0}".format(pose))

                    else:
                        if isinstance(items, unicode):
                            items = str(items)
                        if isinstance(items, str):
                            jointPose.savePose(items, poseName=pose)
                        else:
                            if len(items > 1):
                                for i in items:
                                    jointPose.savePose(i, poseName=pose)
                            else:
                                jointPose.savePose(items[0], poseName=pose)

                        _logger.info(
                            "Saved SelectionData for {0}".format(pose))

            if not save:
                allChildren = self.loadPose_button_children.isChecked()
                if allChildren:
                    if isinstance(items, unicode):
                        items = str(items)
                    if isinstance(items, str):
                        objs = transform.findObjectsUnderNode(
                            items, "joint", match="")
                        objs.append(items)
                        jointPose.loadPose(
                            objs, poseName=pose, t=t, r=r, s=s, ro=jo)

                    else:
                        for i in items:
                            objs = transform.findObjectsUnderNode(
                                i, "joint", match="")
                            objs.append(i)
                            jointPose.loadPose(
                                objs, poseName=pose, t=t, r=r, s=s, ro=jo)
                    _logger.info("Loaded AllChildrenData for {0}".format(pose))

                else:
                    if isinstance(items, unicode):
                        items = str(items)
                    if isinstance(items, str):
                        jointPose.loadPose(
                            items, poseName=pose, t=t, r=r, s=s, ro=jo)
                    else:
                        for i in items:
                            jointPose.loadPose(
                                i, poseName=pose, t=t, r=r, s=s, ro=jo)

                    _logger.info("Loaded SelectionData for {0}".format(pose))

    def event_utils_orient(self):
        items = cmds.ls(sl=True, typ="joint")
        if len(items) == 1:
            items = items[0]

        if items:
            allChildren = self.orientPose_button_children.isChecked()
            if allChildren:
                if isinstance(items, unicode):
                    items = str(items)
                if isinstance(items, str):
                    objs = transform.findObjectsUnderNode(
                        items, "joint", match="")
                    objs.append(items)
                    jointPose.rotToOrient(objs)

            else:
                if isinstance(items, unicode):
                    items = str(items)
                if isinstance(items, str):
                    jointPose.rotToOrient(items)
                else:
                    for i in items:
                        objs = transform.findObjectsUnderNode(
                            i, "joint", match="")
                        objs.append(i)
                        jointPose.rotToOrient(objs)

    def event_utils_rotate(self):
        items = cmds.ls(sl=True, typ="joint")
        if len(items) == 1:
            items = items[0]

        if items:
            allChildren = self.orientPose_button_children.isChecked()
            if allChildren:
                if isinstance(items, unicode):
                    items = str(items)
                if isinstance(items, str):
                    objs = transform.findObjectsUnderNode(
                        items, "joint", match="")
                    objs.append(items)
                    jointPose.orientToRot(objs)

            else:
                if isinstance(items, unicode):
                    items = str(items)
                if isinstance(items, str):
                    jointPose.orientToRot(items)
                else:
                    for i in items:
                        objs = transform.findObjectsUnderNode(
                            i, "joint", match="")
                        objs.append(i)
                        jointPose.orientToRot(objs)

    def event_utils_mirror(self):
        items = cmds.ls(sl=True, typ="joint")
        if len(items) == 1:
            items = str(items[0])

        if items:
            allChildren = self.orientPose_button_children.isChecked()

            if allChildren:
                joint.mirrorJointChain(items)
            else:
                joint.mirrorOrient(items, "x")

    def event_utils_axisCones(self):
        items = cmds.ls(sl=True, typ="joint")

        if len(items) == 1:
            items = str(items[0])

        if items:
            allChildren = self.orientPose_button_children.isChecked()

            if allChildren:
                if isinstance(items, list):
                    objs = transform.findObjectsUnderNode(
                        items, "joint", match="")
                    objs.append(items)
                    transform.createTransformAxisCone(objs)
                else:
                    transform.createTransformAxisCone(items)
            else:
                transform.createTransformAxisCone(cmds.ls(sl=True))
