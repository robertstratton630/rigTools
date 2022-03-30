import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os
import pymel.core as pm
import rsTools.utils.path as path

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from rsTools.glob import *
from rsTools.utils import nurbs
from shiboken2 import wrapInstance

import logging
import rsTools.ui.qtWrap as qtWrap


import rsTools.utils.controls.curveData as csIO
import rsTools.utils.transforms.transforms as transform
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


# get main window

def mayaMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


# run UI command
win = None


def run():
    global win
    if win:
        win.close()
    win = controlShapeBuildUI(parent=mayaMainWindow())
    win.show()

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
        self.imageDict = {}

        super(controlShapeBuildUI, self).__init__(parent)

        self.gridLayout = QtWidgets.QGridLayout()
        self.vlo_main = QtWidgets.QVBoxLayout()

        # label
        self.conLabel = QtWidgets.QLabel('Simple Controller Library')
        self.vlo_main.addWidget(self.conLabel)

        # conName
        self.controlNameLayout = QtWidgets.QHBoxLayout()
        self.vlo_main.addLayout(self.controlNameLayout)

        self.controlNameLabel = QtWidgets.QLabel("ControlName: ")
        self.controlNameLayout.addWidget(self.controlNameLabel)
        self.conNameLineEdit = QtWidgets.QLineEdit()

        # add reg expression to naming
        # rx = QtCore.QRegExp("[0-9a-zA-Z_]+") # 0-9 and a to z + as many times
        rx = QtCore.QRegExp("[0-9a-z]+")
        validator = QtGui.QRegExpValidator(rx, self)
        self.conNameLineEdit.setValidator(validator)

        self.controlNameLayout.addWidget(self.conNameLineEdit)

        # saveButton
        self.saveConButton = QtWidgets.QPushButton("Save Controller")
        self.vlo_main.addWidget(self.saveConButton)

        # pixmap - can be added to labels  buttons
        self.defaultImg = os.path.join(imageFolderPath, "noImg.jpg")
        self.pixmap = QtGui.QPixmap(self.defaultImg)
        self.scalePixmap = self.pixmap.scaledToWidth(240)
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(self.scalePixmap)
        self.vlo_main.addWidget(self.imageLabel)

        # slider
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.scaleLabel = QtWidgets.QLabel("Scale:")
        self.horizontalLayout.addWidget(self.scaleLabel)
        self.scaleValLineEdit = QtWidgets.QLineEdit("1.0")
        self.horizontalLayout.addWidget(self.scaleValLineEdit)
        self.scaleSlider = QtWidgets.QSlider()
        self.scaleSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalLayout.addWidget(self.scaleSlider)
        self.vlo_main.addLayout(self.horizontalLayout)

        self.ui_colorButtons()

        # list
        self.conListWidget = QtWidgets.QListWidget()
        self.vlo_main.addWidget(self.conListWidget)

        # layering the layouts
        self.gridLayout.addLayout(self.vlo_main, 0, 0, 1, 1)
        self.setLayout(self.gridLayout)

        # MANY THINGS YOU HAVE TO ADD
        self.setWindowTitle("Controller Library")
        self.init_uiState()
        self.createConnections()

        self.show()

    def createLayout(self):
        pass
        #self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def createConnections(self):
        self.conListWidget.itemDoubleClicked.connect(self.conListDoubleClick)

    def ui_colorButtons(self):

        # create a grid layout inside the verical layout
        self.glo_colorButton = QtWidgets.QGridLayout()
        self.vlo_main.addLayout(self.glo_colorButton)

        # create a button Group
        rows = 4
        cols = 8
        qtWrap.createButtonGroup(
            self, groupID=0, rows=rows, cols=cols, spacing=0, widgetParent=self.vlo_main)

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

    def init_pixmap(self):
        self.conListWidget.itemClicked.connect(self.event_pixmap)

    def event_pixmap(self):
        item = self.conListWidget.currentItem()
        text = item.text()
        imgPath = os.path.join(imageFolderPath, "{0}.jpg".format(text))

        if not os.path.isfile(imgPath):
            imgPath = self.defaultImg

        pixmap = QtGui.QPixmap(imgPath)
        scaled = pixmap.scaledToWidth(240)
        self.imageLabel.setPixmap(scaled)

    # set default settings

    def init_scaleSlider(self):
        # slider
        self.scaleSlider.setMinimum(0.1)
        self.scaleSlider.setMaximum(100)
        self.scaleSlider.setValue(self.scaleVal)
        self.scaleSlider.valueChanged.connect(self.event_scaleSlider)

        # line edit
        val = unicode(1.0)
        self.scaleValLineEdit.setText(val)
        self.scaleValLineEdit.editingFinished.connect(self.event_scaleLineEdit)

    # set scaleSlider event
    def event_scaleSlider(self):
        sender = self.sender()
        val = unicode(sender.value()/10.0)
        self.scaleValLineEdit.setText(val)
        self.scaleVal = float(val)

    # update scale widget
    def event_scaleLineEdit(self):
        sender = self.sender()
        scale = sender.text()
        self.scale = float(scale)
        self.scaleSlider.setValue(self.scale*10)

    # update scale widget
    def event_scaleLineEdit(self):
        sender = self.sender()
        scale = sender.text()
        self.scale = float(scale)
        self.scaleSlider.setValue(self.scale*10)

    # nameLineEdit

    def init_nameLineEdit(self):
        self.saveConButton.clicked.connect(self.event_nameLineEdit)
        self.conNameLineEdit.setPlaceholderText("Diamond")

    def event_nameLineEdit(self):
        sel = cmds.ls(sl=True)
        build = True
        for s in sel:
            if not catch.isType(s, "nurbsCurve"):
                build = False

        if build:
            if(len(sel) > 1):
                curve = nurbs.combineShapes(sel, "tmp")
                curveName = self.conNameLineEdit.text()
                if not curveName:
                    _logger.error("No Curve Name Given")
                else:
                    csIO.saveControlData(curve, curveName, saveThumbnail=True)
                    self.updateListWidget()

        else:
            _logger.error("No Valid Object Selected")

    def init_uiState(self):
        self.updateListWidget()
        self.init_scaleSlider()
        self.init_nameLineEdit()
        self.init_pixmap()

    # update widget methods

    def updateListWidget(self):
        controlList = csIO.listControlsInLibrary()

        self.conListWidget.clear()
        for c in controlList:
            qlist = QtWidgets.QListWidgetItem(c)
            self.conListWidget.addItem(qlist)

    def conListDoubleClick(self):
        listWidget = self.sender()  # this gets a pointer to the function that called it
        item = listWidget.currentItem().text()

        # get color
        currentButton = self.widgetDict["ButtonGroup0"]["buttonGroup"].checkedButton(
        )
        if currentButton:
            color = int(currentButton.text())
            csIO.buildControlShape(
                item, item, scale=self.scaleVal, color=color)
        else:
            _logger.warning("Please Select Color")
