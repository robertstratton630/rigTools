from Qt import QtCore, QtGui, QtWidgets
import maya.cmds as cmds
from functools import partial

'''


'''


class ButtonStackWidget(QtWidgets.QWidget):

    buttonPressed = QtCore.Signal()

    def __init__(self, layout="vertical", labels=[], boxGroup=False, parent=None):
        super(ButtonStackWidget, self).__init__(parent)
        self.setObjectName("ButtonStackWidget")

        self._labels = labels
        self._layoutMode = layout
        self._widgets = list()
        self.currentButton = labels[0]

        self._doBox = boxGroup
        self._boxGroup = None

        # build guts
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        for i, label in enumerate(self._labels):
            widget = QtWidgets.QPushButton(label)

            if self._layoutMode == "vertical":
                widget.setMinimumSize(50, self.height()/len(self._labels))
                widget.setSizeIncrement
            else:
                widget.setMinimumSize(self.width()/len(self._labels), 50)

            self._widgets.append(widget)

        if self._doBox:
            self._boxGroup = QtWidgets.QGroupBox(self)

    def create_layout(self):
        self._layout = None

        if self._layoutMode in ["vertical", "Vertical", "v"]:
            self._layout = QtWidgets.QVBoxLayout(self)
        else:
            self._layout = QtWidgets.QHBoxLayout(self)

        for w in self._widgets:
            self._layout.addWidget(w)

        if self._doBox:
            self._boxGroup.setLayout(self._layout)

    def create_connections(self):
        for i, button in enumerate(self._widgets):
            button.clicked.connect(partial(self.event_signals, i))

    def event_signals(self, slot):
        self.currentButton = labels[slot]
        self.buttonPressed.emit()
