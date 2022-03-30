import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os
import pymel.core as pm

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from rsTools.utils.transforms import nurbs
from shiboken2 import wrapInstance

import logging
import rsTools.ui.qtWrap as qtWrap
import rsTools.utils.data.curveData as curveData
import rsTools.utils.data.osUtils as osUtils
import rsTools.utils.transforms.transforms as transform

from rsTools.ui.widgets.customImageWidget import CustomImageWidget

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# get main window


def mayaMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


# run UI command
controlLibUI = None


def run():
    global controlLibUI
    if controlLibUI:
        controlLibUI.close()
    controlLibUI = controlShapeBuildUI(parent=mayaMainWindow())
    controlLibUI.show()

# main UI class


class controlShapeBuildUI(QtWidgets.QDialog):

    def __init__(self, parent=mayaMainWindow()):

        ##################################################################
        # init all local variables
        ##################################################################

        self.scaleVal = 1.0
        # remapping maya colors into rbg for QPixMap widgets
        self.rbgColorMap = transform.rbgColorMap()

        ##################################################################
        self.widgetDict = {}

        super(controlShapeBuildUI, self).__init__(parent)

        # MANY THINGS YOU HAVE TO ADD
        self.setWindowTitle("Control Shape Library")
        self.createWidgets()
        self.createConnections()
        self.createLayout()

        self.updateListWidget()

        self.show()

    def createWidgets(self):
        kwargs = {"textSize": 13,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False
                  }
        self.controlSelect_label = CustomImageWidget(230, 30, text="Existing Library Controls: ", imagePath=os.path.join(
            osUtils.get_rsTools_img_path_shelf(), "default.svg"), **kwargs)
        self.controlListWidget = QtWidgets.QListWidget()
        self.controlSelectBox = QtWidgets.QGroupBox()
        controlSelectLayout = QtWidgets.QVBoxLayout()
        controlSelectLayout.addWidget(self.controlSelect_label)
        controlSelectLayout.addWidget(self.controlListWidget)
        controlSelectLayout.setSpacing(5)
        controlSelectLayout.setContentsMargins(8, 8, 8, 8)
        self.controlSelectBox.setLayout(controlSelectLayout)

        self.controlListWidget.itemSelectionChanged.connect(
            self.event_listSelection)

        self.controlSelectBox.setStyleSheet('''
                                        QGroupBox { 
                                            background-color: rgba(100,150,200,20); 
                                            padding-top:5px; 
                                            border-radius: 6px; 
                                            margin-top: 0.5em;
                                        }  ''')

        self.buildSaveWidgets()
        self.buildLoadWidgets()
        self.buildEditWidgets()

    def createConnections(self):
        # self.conListWidget.itemDoubleClicked.connect(self.conListDoubleClick)
        pass

    def createLayout(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(self.controlSelectBox)
        self.mainLayout.addWidget(self.saveBox)
        self.mainLayout.addWidget(self.loadBox)
        self.mainLayout.addWidget(self.editBox)

    def buildSaveWidgets(self):
        # label
        kwargs = {"textSize": 10,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False
                  }

        # save UI - widgets
        self.save_label = CustomImageWidget(230, 30, text="Save Selected Nurb(s) Curves", imagePath=os.path.join(
            osUtils.get_rsTools_img_path_shelf(), "default.svg"), **kwargs)
        self.save_lineEdit = QtWidgets.QLineEdit()
        self.save_controlNameLabel = QtWidgets.QLabel("Library Name: ")
        self.save_pushButton = QtWidgets.QPushButton("Save Controller")

        rx = QtCore.QRegExp("[A-Za-z]+")
        validator = QtGui.QRegExpValidator(rx, self)
        self.save_lineEdit.setValidator(validator)
        self.save_lineEdit.setPlaceholderText("diamond")

        lineEditLayout = QtWidgets.QHBoxLayout()
        lineEditLayout.addWidget(self.save_controlNameLabel)
        lineEditLayout.addWidget(self.save_lineEdit)

        self.saveBox = QtWidgets.QGroupBox()
        self.saveBoxLayout = QtWidgets.QVBoxLayout()
        self.saveBoxLayout.addWidget(self.save_label)
        self.saveBoxLayout.addLayout(lineEditLayout)
        self.saveBoxLayout.addWidget(self.save_pushButton)
        self.saveBoxLayout.setSpacing(5)
        self.saveBoxLayout.setContentsMargins(8, 8, 8, 8)
        self.saveBox.setLayout(self.saveBoxLayout)

        # box group
        self.saveBox.setStyleSheet('''
                                        QGroupBox { 
                                            background-color: rgba(100,150,200,20); 
                                            padding-top:5px; 
                                            border-radius: 6px; 
                                            margin-top: 0.5em;
                                        }  ''')

        self.save_pushButton.clicked.connect(self.event_savePushButton)

    def buildLoadWidgets(self):
        # label
        kwargs = {"textSize": 10,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False
                  }

        # save UI - widgets
        self.load_label = CustomImageWidget(230, 30, text="Load Shape", imagePath=os.path.join(
            osUtils.get_rsTools_img_path_shelf(), "default.svg"), **kwargs)

        self.load_libraryNameLabel = QtWidgets.QLabel("Library Name: ")
        self.load_controlNameLabel = QtWidgets.QLabel("Control Name:")
        self.load_pushButton = QtWidgets.QPushButton("Load Controller")

        self.load_lineEdit = QtWidgets.QLineEdit()
        rx = QtCore.QRegExp("[a-zA-Z]+")
        validator = QtGui.QRegExpValidator(rx, self)
        self.load_lineEdit.setValidator(validator)
        self.load_lineEdit.setPlaceholderText("diamond")

        self.load_lineEditControlName = QtWidgets.QLineEdit()
        rx = QtCore.QRegExp("[a-zA-Z0-9_]+")
        validator = QtGui.QRegExpValidator(rx, self)
        self.load_lineEditControlName.setValidator(validator)
        self.load_lineEditControlName.setPlaceholderText("l_foot_CTRL")

        lineEditLayout = QtWidgets.QHBoxLayout()
        lineEditLayout.addWidget(self.load_libraryNameLabel)
        lineEditLayout.addWidget(self.load_lineEdit)

        lineEditControlLayout = QtWidgets.QHBoxLayout()
        lineEditControlLayout.addWidget(self.load_controlNameLabel)
        lineEditControlLayout.addWidget(self.load_lineEditControlName)

        self.loadBox = QtWidgets.QGroupBox()
        loadBoxLayout = QtWidgets.QVBoxLayout()
        loadBoxLayout.addWidget(self.load_label)
        loadBoxLayout.addLayout(lineEditLayout)
        loadBoxLayout.addLayout(lineEditControlLayout)
        loadBoxLayout.addWidget(self.load_pushButton)

        loadBoxLayout.setSpacing(5)
        loadBoxLayout.setContentsMargins(8, 8, 8, 8)
        self.loadBox.setLayout(loadBoxLayout)

        # box group
        self.loadBox.setStyleSheet('''
                                        QGroupBox { 
                                            background-color: rgba(100,150,200,20); 
                                            padding-top:5px; 
                                            border-radius: 6px; 
                                            margin-top: 0.5em;
                                        }  ''')

        self.load_pushButton.clicked.connect(self.event_loadPushButton)

    def buildEditWidgets(self):
        # label
        kwargs = {"textSize": 10,
                  "textAlign": QtCore.Qt.AlignLeft,
                  "background": False
                  }

        # save UI - widgets
        self.edit_label = CustomImageWidget(230, 30, text="Edit Shape", imagePath=os.path.join(
            osUtils.get_rsTools_img_path_shelf(), "default.svg"), **kwargs)

        self.buildColorButtons()

        self.editBox = QtWidgets.QGroupBox()
        editBoxLayout = QtWidgets.QVBoxLayout()
        editBoxLayout.addWidget(self.edit_label)
        editBoxLayout.addLayout(self.widgetDict["ButtonGroup0"]["layout"])
        editBoxLayout.setSpacing(5)
        editBoxLayout.setContentsMargins(8, 8, 8, 8)
        self.editBox.setLayout(editBoxLayout)

        self.editBox.setStyleSheet('''
                                        QGroupBox { 
                                            background-color: rgba(100,150,200,20); 
                                            padding-top:5px; 
                                            border-radius: 6px; 
                                            margin-top: 0.5em;
                                        }  ''')

    def buildColorButtons(self):
        # create a button Group
        rows = 4
        cols = 8
        self.createButtonGroup(groupID=0, rows=rows, cols=cols, spacing=0)

        # color code the buttons
        numButtons = rows*cols
        buttonGroup = self.widgetDict["ButtonGroup0"]
        for i in range(0, numButtons):

            if(i == 0):
                buttonGroup["button"+str(i)].setDisabled(True)
                buttonGroup["button"+str(i)].setText("")

            else:
                rgb = self.rbgColorMap.get(i)
                buttonGroup["button"+str(i)].setStyleSheet(
                    'QPushButton {background-color: rgb(%d,%d,%d); color:white;}' % rgb)
            buttonGroup["button" +
                        str(i)].clicked.connect(self.event_colorButton)

    def createButtonGroup(self, groupID=0, rows=2, cols=2, spacing=0, widgetParent=None):
        data = {}
        data["layout"] = QtWidgets.QGridLayout()
        data["layout"].setHorizontalSpacing(spacing)
        data["layout"].setVerticalSpacing(spacing)

        try:
            widgetParent.addLayout(data["layout"])
        except:
            pass

        data["buttonGroup"] = QtWidgets.QButtonGroup()
        id = 0
        for i in range(rows):
            for j in range(cols):
                buttonName = "button"+str(id)
                data[buttonName] = QtWidgets.QPushButton("{0}".format(id))
                data[buttonName].setProperty("colorID", id)

                data[buttonName].setMaximumSize(30, 30)

                data["buttonGroup"].addButton(data[buttonName])
                data["layout"].addWidget(data[buttonName], i, j)
                id += 1

        self.widgetDict["ButtonGroup"+str(groupID)] = data

    def event_colorButton(self):
        sender = self.sender()
        currentButton = sender.property("colorID")
        if currentButton:
            color = int(currentButton)

            sel = cmds.ls(sl=True)
            build = True
            for s in sel:
                if not catch.isType(s, "nurbsCurve"):
                    build = False
            if build:
                transform.enableDrawOverrides(sel)
                transform.setColorIndex(sel, color)

    def event_savePushButton(self):
        sel = cmds.ls(sl=True)
        build = True
        for s in sel:
            if not catch.isType(s, "nurbsCurve"):
                build = False
        if build:
            curve = nurbs.combineShapes(sel, "tmp")
            libName = self.save_lineEdit.text()
            if not libName:
                _logger.error("No Curve Name Given")
            else:
                curveData.saveControlData(curve, libName, saveThumbnail=False)
                self.updateListWidget()

        else:
            _logger.error("No Valid Object Selected")

    def event_loadPushButton(self):
        item = self.controlListWidget.currentItem(
        ).text() or self.load_libraryNameLabel.text()
        controlName = self.load_lineEditControlName.text()

        if item and controlName:
            curveData.buildControlShape(controlName, item, color=14)

    def updateListWidget(self):
        shapes = curveData.listControlsInLibrary()
        self.controlListWidget.clear()

        try:
            self.controlListWidget.addItems(shapes)
        except:
            pass

    def event_listSelection(self):
        item = self.controlListWidget.currentItem().text()
        self.load_lineEdit.setText(item)
