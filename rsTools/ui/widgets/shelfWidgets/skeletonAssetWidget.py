from Qt import QtCore, QtGui, QtWidgets
import maya.cmds as cmds

'''

'''


class SkeletonAssetWidget(QtWidgets.QWidget):

    comboSelected = QtCore.Signal()
    returnPressed = QtCore.Signal()
    editingFinished = QtCore.Signal()

    def __init__(self, parent=None):
        super(SkeletonAssetWidget, self).__init__(parent)
        self.setObjectName("SkeletonAssetWidget")

        #global variables
        self._placeHolderText = "bearA"
        self._text = self._placeHolderText
        self._comboText = "LODa"

        # build guts
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self._combo_box = QtWidgets.QComboBox()
        self._combo_box.addItems(["LODa", "LODb", "LODc", "LODd", "LODe"])
        self._lineEdit = QtWidgets.QLineEdit()
        self._lineEdit.setPlaceholderText("bearA")

        rx = QtCore.QRegExp("[a-zA-Z]+")
        validator = QtGui.QRegExpValidator(rx, self)
        self._lineEdit.setValidator(validator)

    def create_layout(self):
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.addWidget(self._lineEdit)
        self._layout.addWidget(self._combo_box)

    def create_connections(self):
        self._combo_box.currentIndexChanged.connect(self.event_comboBox)
        self._lineEdit.editingFinished.connect(self.event_lineEdit)
        self._lineEdit.returnPressed.connect(self.event_returnPressed)

    # events
    def event_lineEdit(self):
        self._text = self._lineEdit.text()
        self.editingFinished.emit()

    def event_comboBox(self):
        self._comboText = self._combo_box.currentText()
        self.comboSelected.emit()

    def event_returnPressed(self):
        self._text = self._lineEdit.text()
        self._comboText = self._combo_box.currentText()
        self.returnPressed.emit()

    def getText(self):
        return self._text

    def getComboText(self):
        return self._comboText

    def setPlaceholderText(self, text):
        self._lineEdit.setPlaceholderText(text)
