import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

import inspect
import weakref

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from shiboken2 import wrapInstance

import rsTools.ui.qtWrap as qtWrap
import rsTools.ui.shelves._icon as iconEngine

from rsTools.glob import *
from rsTools.utils import path

import logging
import os
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ShelfButton(QtCore.QObject):

    iconPath = os.path.join(g_rs_path_image_shelf, "default.svg")

    __defaultSettings__ = {"enableCommandRepeat": 1,
                           "width": 35,
                           "height": 35,
                           "manage": 1,
                           "visible": 1,
                           "preventOverride": 0,
                           "enableBackground": 0,
                           "align": "center",
                           "label": "",
                           "image": iconPath,
                           "style": "iconOnly",
                           "marginWidth": 1,
                           "marginHeight": 1,
                           "command": "press",
                           "sourceType": "python",
                           "commandRepeatable": 1,
                           "flat": 1
                           }

    _color = (90, 100, 120)
    _annotation = "ShelfButton"
    _title = "Button"
    _icon = None
    _enabled = True
    _command = None
    _parentShelf = None
    _widget = None

    def __init__(self, title=None, titleFontSize=None, parentShelf=None, name=None, color=None, icon=None, enabled=None, annotation=None, command=None):
        super(ShelfButton, self).__init__()

        self._name = name or self.__class__.__name__
        self._control = name
        self._title = title or self._title
        self._color = color or self._color
        self._icon = icon or self._icon
        self._enabled = enabled or self._enabled
        self._annotation = annotation or self._annotation
        self._command = command or self._annotation
        self._parentShelf = parentShelf or self._parentShelf
        self._status = "default"
        self._progress = None
        self._widget = None
        self._eventFilter = None
        self._titleFontSize = titleFontSize

    def __str__(self):
        return str(self._name)

    @property
    def getName(self):
        return self._name

    @property
    def exists(self):
        return self._widget is not None

    @property
    def parentShelf(self):
        return self._shelf

    @parentShelf.setter
    def parentShelf(self, shelf):
        self._shelf = shelf
        if self.exists:
            self.create()

    def refresh(self):
        self.widget.update()

    def destoryButton(self):
        if self.exists:
            try:
                self._widget.removeEventFilter(self._eventFilter)
            except:
                pass
        else:
            self._widget.deleteLater()
        self._widget = None

    def _refreshIcon(self):
        if self.exists:
            self._icon_engine = iconEngine.DefaultIcon(
                title=self._title, icon=self._icon, color=self._color, progress=self._progress, status=self._status, titleFontSize=self._titleFontSize)
            self._icon = QtGui.QIcon(self._icon_engine)
            self.widget.setIcon(self._icon)
            self.refresh()

    @property
    def name(self):
        return self._name

    @property
    def control(self):
        return self._control

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = [int(c) or 0 for c in color][0:3]
        self._refreshIcon()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, icon):
        self._icon = icon

    @property
    def name(self):
        return self._name

    @property
    def exists(self):
        return self.widget is not None

    @property
    def parentShelf(self):
        return self._shelf

    @parentShelf.setter
    def parentShelf(self, shelf):
        self._shelf = shelf
        if self.exists:
            self.create()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        self._widget.setEnabled(enabled)
        self.refresh()

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, command):
        if hasattr(command, "__call__"):
            self._command = command
        else:
            self._command = None

    @property
    def annotation(self):
        return self._annotation

    @annotation.setter
    def annotation(self, annotation):
        self._annotation = annotation
        self._widget.setToolTip(self._annotation)

    @property
    def widget(self):
        return self._widget

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status if status in [
            "default", "succuss", "warning", "error"] else "default"
        self._refreshIcon()

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, progress):
        if progress in None or progress < 0:
            self._progress = None
        else:
            self._progress = min(1.0, max(progress, 0.0))

        self._icon_engine = iconEngine.DefaultIcon(
            title=self._title, color=self._color, progress=self._progress, status=self._status)
        self._icon = QtGui.QIcon(self._icon_engine)
        if self.exists:
            self.widget.setIcon(self._icon)
            self.refresh()
        return self

    def _eventPressed(self, mb=None):
        if mb == QtCore.Qt.LeftButton:
            self.mousePressed()
        elif mb == QtCore.Qt.RightButton:
            self.rightMousePressed()

    def _eventReleased(self, mb=None):
        pass

    def eventFilter(self, target, event):
        if not target.isEnabled():
            return False
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.type() == QtCore.Qt.MiddleButton:
                return False
            self._eventPressed(mb=event.button())
            return True
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button == QtCore.Qt.MiddleButton:
                return False
            self._eventReleased(mb=event.button())
            return True
        return False

    ''' pure virtual procs '''

    def created(self):
        return

    def mouseReleased(self):
        return

    def rightMouseReleased(self):
        return

    def mousePressed(self):
        print "mousePressed base function called"
        print self.name
        return

    def rightMousePressed(self):
        print "RightMousePressed base function called"
        print self.name
        return

    def __del__(self):
        self._shelf = None
        self.destoryButton()

    def create(self):
        if self._shelf is not None and self._shelf.exists and not self.exists:
            buttonKargs = self.__defaultSettings__.copy()
            buttonKargs["enable"] = self._enabled
            buttonKargs["annotation"] = self._annotation
            self._control = cmds.shelfButton(
                self._name, p=self._parentShelf.name, **buttonKargs)
            self._widget = qtWrap.getQtObject(
                self._control, QtWidgets.QPushButton)[0]

            if self._widget is not None:
                _logger.debug("widget Attached to QObject")
                self._widget.setStyleSheet("""QWidget{background-color: transparent}
                                              QWidget::pressed{padding: 2px 2px 0px 2px; margin:0;border:2px solid transparent;}""")
                self._widget.installEventFilter(self)
                self._widget.setIconSize(QtCore.QSize(32, 32))
                self._refreshIcon()
                self.created()
