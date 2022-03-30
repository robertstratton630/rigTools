import logging
from Qt import QtCore, QtGui, QtWidgets
import maya.cmds as cmds
from functools import partial

import rsTools.utils.hashMap._iconMap as ic
iconMap = ic.get_icon_map()

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class PickerWidget(QtWidgets.QWidget):

    pickChanged = QtCore.Signal()
    lineEditChanged = QtCore.Signal()

    def __init__(self, parent=None, labelName="Select"):
        super(PickerWidget, self).__init__(parent)
        self.setObjectName("PickerWidget")
        self._sel = None
        self._name = labelName

        self._lineText = ""

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        icon = QtGui.QIcon(iconMap["picker"])
        self._button = QtWidgets.QPushButton(icon, "")
        self._button.setIconSize(QtCore.QSize(20, 20))
        self._button.setFlat(True)

        self._lineEdit = QtWidgets.QLineEdit()
        self._lineEdit.setMaximumHeight(20)

        self._label = QtWidgets.QLabel(self._name)
        self._label.setMaximumHeight(20)

    def create_layout(self):
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.addWidget(self._label)
        self.mainLayout.addWidget(self._button)
        self.mainLayout.addWidget(self._lineEdit)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setAlignment(QtCore.Qt.AlignRight)

    def create_connections(self):
        self._button.clicked.connect(self._event_button)
        self._lineEdit.editingFinished.connect(self._event_lineEdit)

    def _event_button(self):
        self.pickChanged.emit()
        self.getSeletion()

    def _event_lineEdit(self):
        self.lineEditChanged.emit()

    #setters and getters
    def setPlaceHolderText(self, text):
        self._lineEdit.setPlaceholderText(text)

    def setText(self, text):
        self._lineEdit.setText(text)

    def setLineSize(self, w, h):
        self._lineEdit.setMaximumSize(w, h)

    def getText(self):
        txt = self._lineEdit.text()
        return txt

    def text(self):
        return self._lineEdit.text()

    @property
    def button(self):
        return self._button

    @property
    def lineEdit(self):
        return self._lineEdit

    def getSeletion(self):
        item = cmds.ls(sl=True)
        if item:
            self._lineEdit.setText(item[0])
        else:
            _logger.warning("Please Select Something")
