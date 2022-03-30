from Qt import QtCore, QtGui, QtWidgets
import maya.cmds as cmds

'''
basic class for painting on images you want to insert

    self.title_label = CustomImageWidget(280, 60, image_path)
    self.title_label.set_background_color(QtCore.Qt.red)

'''


class FolderSelectWidget(QtWidgets.QWidget):

    lineEditChanged = QtCore.Signal()
    returnPressed = QtCore.Signal()

    def __init__(self, parent=None):
        super(FolderSelectWidget, self).__init__(parent)
        self.setObjectName("FolderSelectWidget")

        #global variables
        self._placeHolderText = "Select Root"
        self._text = self._placeHolderText
        self._initial_directory = cmds.internalVar(userPrefDir=True)

        # build guts
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self._lineEdit = QtWidgets.QLineEdit()
        if self._placeHolderText:
            self._lineEdit.setPlaceholderText(self._placeHolderText)

        rx = QtCore.QRegExp("[a-zA-Z]+")
        validator = QtGui.QRegExpValidator(rx, self)
        self._lineEdit.setValidator(validator)

        self._pushButton = QtWidgets.QPushButton()
        self._pushButton.setIcon(QtGui.QIcon(":fileOpen.png"))
        self._pushButton.setToolTip("Select Folder")

    def create_layout(self):
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.addWidget(self._lineEdit)
        self._layout.addWidget(self._pushButton)

    def create_connections(self):
        self._pushButton.clicked.connect(self.event_folderSelect)
        self._lineEdit.editingFinished.connect(self.event_lineEdit)
        self._lineEdit.returnPressed.connect(self.event_returnPressed)

    def event_returnPressed(self):
        txt = self._lineEdit.text()
        self.setPlaceholderText(txt)
        self.setText(txt)
        self.lineEditChanged.emit()

    # events
    def event_lineEdit(self):
        txt = self._lineEdit.text()
        self.setPlaceholderText(txt)
        self.setText(txt)
        self.lineEditChanged.emit()

    def event_folderSelect(self):

        fileDialog = QtWidgets.QFileDialog()
        new_directory = fileDialog.getExistingDirectory(
            self, "Select Root Folder", self._initial_directory)
        if new_directory:
            self._initial_directory = new_directory
            self._lineEdit.setText(new_directory)
            self._text = new_directory
            self.lineEditChanged.emit()

    def event_returnPressed(self):
        txt = self._lineEdit.text()
        self.setText(txt)
        self._returnPressed.emit()

    # placeHolder
    def getPlaceholderText(self):
        return self._placeHolderText

    def setPlaceholderText(self, name):
        self._placeHolderText = name

    # text
    def getText(self):
        return self._text

    def setText(self, name):
        self._text = name
