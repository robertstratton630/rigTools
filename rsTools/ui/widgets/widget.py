from Qt import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import pymel.core as pm
import os


def createButtonGroup(self, groupID=0, rows=2, cols=2, spacing=0, widgetParent=None):
    data = {}
    data["layout"] = QtWidgets.QGridLayout()
    data["layout"].setHorizontalSpacing(spacing)
    data["layout"].setVerticalSpacing(spacing)
    widgetParent.addLayout(data["layout"])

    data["buttonGroup"] = QtWidgets.QButtonGroup()

    id = 0
    for i in range(rows):
        for j in range(cols):
            buttonName = "button"+str(id)
            data[buttonName] = QtWidgets.QPushButton("{0}".format(id))

            data[buttonName].setMaximumSize(30, 30)
            data[buttonName].setCheckable(True)

            data["buttonGroup"].addButton(data[buttonName])
            data["layout"].addWidget(data[buttonName], i, j)
            id += 1

    self.widgetDict["ButtonGroup"+str(groupID)] = data


def createSelectionWidget():
    pass


def createSliderWidget():
    pass


def createHButtonsWidget(buttonLabels=None):
    data = {}
    data["layout"] = QtWidgets.QHBoxLayout()

    for i, label in enumerate(buttonLabels):
        buttonName = "button_"+label
        data[buttonName] = QtWidgets.QPushButton(label)
        data["layout"].addWidget(data[buttonName])

    return data


def createVButtonsWidget(buttonLabels=None):
    data = {}
    data["layout"] = QtWidgets.QVBoxLayout()

    for i, label in enumerate(buttonLabels):
        buttonName = "button"+label
        data[buttonName] = QtWidgets.QPushButton(label)
        data["layout"].addWidget(data[buttonName])

    return data


def createFolderSelectWidget(labelName="Folder: ", spacing=10, widgetParent=None):
    data = {}

    data["lineEdit"] = QtWidgets.QLineEdit()
    data["button"] = QtWidgets.QPushButton()
    data["button"].setIcon(QtGui.QIcon(":fileOpen.png"))
    data["button"].setToolTip("Select Folder")
    data["text"] = QtWidgets.QLabel(labelName)

    data["layout"] = QtWidgets.QHBoxLayout()
    data["layout"].addWidget(data["text"])
    data["layout"].addWidget(data["lineEdit"])
    data["layout"].addWidget(data["button"])

    try:
        widgetParent.addLayout(data["layout"])
    except:
        pass

    return data
