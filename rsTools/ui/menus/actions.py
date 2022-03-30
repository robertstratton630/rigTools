import re

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from rsTools.glob import *

from functools import partial
from rsTools.ui.widgets.folderSelectWidget import FolderSelectWidget
from rsTools.ui.widgets.shelfWidgets.assetPickerWidget import AssetPickerWidget
from rsTools.ui.widgets.shelfWidgets.skeletonAssetWidget import SkeletonAssetWidget

'''
    main event handler for menu items
        - hover & release
'''


class _MenuItemEventFilter(QtCore.QObject):
    targetHovered = QtCore.Signal()
    targetReleased = QtCore.Signal()

    def eventFilter(self, obj, event):
        _type = event.type()
        if _type == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.LeftButton:
                self.targetReleased.emit()
                return False
            else:
                return False
        elif _type == QtCore.QEvent.HoverEnter:
            self.targetHovered.emit()
            return False
        else:
            return False


class WidgetActionBase(QtWidgets.QWidgetAction):
    textUpdated = QtCore.Signal()
    _widget = QtWidgets.QWidget
    _style = ""

    def __init__(self, p=None):
        super(WidgetActionBase, self).__init__(p)
        self._text = ""
        self._defaultState = None
        self.widget = None
        self._eventFilter = _MenuItemEventFilter(self)

    ''' pure virtual procs '''

    def parseDefinition(self, description):
        return

    def widgetAdded(self, widget):
        return

    def widgetDeleting(self, widget):
        return

    def widget(self):
        if self._widget:
            return self._widget

    def setText(self, text):
        self._text = text

        if self.widget:
            print self.widget
            if hasattr(self.widget, "setText"):
                self.widget.setText(text)
            self.textUpdated.emit(text)

    def parseDefinition(self, description):
        return

    # this function is called whenever the action is added
    def createWidget(self, p):
        widget = self._widget(p)

        widget.setMinimumSize(162, 26)
        widget.installEventFilter(self._eventFilter)

        if self._style:
            widget.setStyleSheet(self._style)

        self.widget = widget
        self.widgetAdded(widget)
        return widget

    def deleteWidget(self, widget):
        super(WidgetActionBase, self).deleteWidget(widget)

    def extraParse(self, description):
        self._style += unicode(description.get("style", ""))
        for signal, slot in description.get("signals", dict()).iteritems():
            if hasattr(self, signal):
                getattr(self, signal).connect(slot)
            else:
                print "no Existing signal {0}".format(signal)


class CustomWidgetAction(WidgetActionBase):
    def __init__(self, p, widget):
        self._widget = widget
        super(CustomWidgetAction, self).__init__(p)


class HTMLAction(WidgetActionBase):
    _widget = QtWidgets.QLabel

    def __init__(self, p):
        super(HTMLAction, self).__init__(p)
        self._eventFilter.targetReleased.connect(self.trigger)


class TextAction(WidgetActionBase):
    _widget = QtWidgets.QLineEdit
    _style = """
                QLineEdit{border:none;
                border-radius:0;
                background-color:#222;
                
                }
            """
    textEdited = QtCore.Signal(str)

    def __init__(self, p):
        super(TextAction, self).__init__(p)
        self._value = ""
        self._accepts = None
        self._merge = None
        self._substitute = "_"

    def _conform(self, text):
        txt = unicode(text)
        if self._accepts is not None:
            txt = re.sub("[^{}]".format(self._accepts), self._substitute, txt)
        if self._merge is not None:
            for merge in self._merge:
                txt = re.sub("{}+".format(re.escape(merge)), sub, txt)
            return txt

    def event_textEdited(self):
        txtRaw = self.text()
        self._value = txtRaw
        self.textEdited.emit(txtRaw)

    def widgetAdded(self, w):
        w.setPlaceholderText(self._text)
        w.textEdited.connect(self.event_textEdited)
        w.returnPressed.connect(self.trigger)

        rx = QtCore.QRegExp("[a-zA-Z]+")
        validator = QtGui.QRegExpValidator(rx, self)
        w.setValidator(validator)

    def extraParse(self, description):
        super(TextAction, self).extraParse(description)
        self._accepts = description.get("accepts", None)
        self._merge = description.get("merge", None)
        self._substitute = description.get("substitute", "_")

    def text(self):
        return self.widget.text()

    def getText(self):
        return self._value


class ImagePreviewAction(WidgetActionBase):
    _widget = QtWidgets.QLabel

    def __init__(self, *args):
        super(ImagePreviewAction, self).__init__(*args)

    def createWidget(self, p):
        widget = self._widget(p)
        widget.installEventFilter(self._eventFilter)
        widget.setStyleSheet(self._style)
        self._widgets.append(widget)
        widget.setEnabled(all(w.isEnabled() for w in self._widgets))
        self.widgetAdded(widget)
        return widget

    def widgetAdded(self, widget):
        widget.setPixmap(self._img)

    def extraParse(self, description):
        super(ImagePreviewAction, self).__extraParse__(description)
        img = description.get("image", False)
        if not img:
            raise RunTimeError("No Image Assigned")
        self._img = QtGui.QPixmap(img).scaledToWidth(160)
        if self._img.height() > 110:
            self._img = self._img.scaledToHeight(110)


class ButtonAction(WidgetActionBase):
    _widget = QtWidgets.QPushButton
    _styles = """QPushButton {margin:1px;
                              opacity:1.0;
                              padding-top:5px;
                              padding-bottom:5px
                            }"""

    def __init__(self, *args):
        super(ButtonAction, self).__init__(*args)

    def extraParse(self, description):
        super(ButtonAction, self).__extraParse__(description)
        color = description.get("color", (90, 90, 90))
        if color:
            self._style += self.parse_color(color)

    def parse_color(self, color):
        c = QtGui.QColor(*color)

        if c.lightness() < 30:
            text_c = QtCore.Qt.white
        elif c.lightness() < 110:
            text_c = c.lighter(320)
        elif c.lightness() < 210:
            text_c = c.darker(400)
        else:
            text_c = QtCore.Qt.black

        return "QPushButton:disabled {{background-color:rgb(120,120,120);color:rgb(75,75,75);}} QPushButton{{background-color:rbg({},{},{});color:rgb({},{},{});}}".format(c.red(), c.green(), c.blue(), text_c.red(), text_c.green(), text_c.blue())


class InlineActionGroup(QtWidgets.QActionGroup):

    def __init__(self, parent, title=None):
        self._title = title
        super(_InlineActionGroup, self).__init__(parent)

    def clear(self):
        for c in self.children():
            c.deleteLater()

    def setActions(self, actions):
        self.clear()
        if self._title is not None:
            a = self.addAction(self._title)
            a.setActionGroup(self)
            a.setSeparator(True)
        for action in actions:
            a.setActionGroup(self)


class FolderSelectAction(WidgetActionBase):
    _widget = FolderSelectWidget
    _style = """
                QLineEdit{border:none;
                border-radius:0;
                background-color:#222;
                
                }
            """
    textEdited = QtCore.Signal(str)

    def __init__(self, p):
        super(FolderSelectAction, self).__init__(p)
        self._value = ""

    def extraParse(self, description):
        super(FolderSelectAction, self).extraParse(description)

    def event_textEdited(self):
        txtRaw = self.sender().getText()
        self._value = txtRaw
        self.textEdited.emit(txtRaw)

    def widgetAdded(self, w):
        w.setPlaceholderText(self._text)
        w.lineEditChanged.connect(self.event_textEdited)
        w.returnPressed.connect(self.trigger)

    def text(self):
        return self.widget.text()

    def getText(self):
        return self._value


class AssetPickerAction(WidgetActionBase):
    _widget = AssetPickerWidget
    _style = """
                QLineEdit{border:none;
                border-radius:0;
                background-color:#222;
                
                }
            """
    textEdited = QtCore.Signal(str)

    def __init__(self, p):
        super(AssetPickerAction, self).__init__(p)

    def extraParse(self, description):
        super(AssetPickerAction, self).extraParse(description)

    def event_textEdited(self):
        txtRaw = self.sender().getText()
        self.textEdited.emit(txtRaw)

    def widgetAdded(self, w):
        w.comboSelected.connect(self.event_textEdited)
        w.returnPressed.connect(self.trigger)
        w.editingFinished.connect(self.event_textEdited)

    def getText(self):
        return self.widget.getText()

    def getComboText(self):
        return self.widget.getComboText()


class SkeletonAssetAction(WidgetActionBase):
    _widget = SkeletonAssetWidget
    _style = """
                QLineEdit{border:none;
                border-radius:0;
                background-color:#222;
                
                }
            """
    textEdited = QtCore.Signal(str)

    def __init__(self, p):
        super(SkeletonAssetAction, self).__init__(p)

    def extraParse(self, description):
        super(SkeletonAssetAction, self).extraParse(description)

    def event_textEdited(self):
        txtRaw = self.sender().getText()
        self.textEdited.emit(txtRaw)

    def widgetAdded(self, w):
        w.comboSelected.connect(self.event_textEdited)
        w.returnPressed.connect(self.trigger)
        w.editingFinished.connect(self.event_textEdited)

    def getText(self):
        return self.widget.getText()

    def getComboText(self):
        return self.widget.getComboText()

    def setPlaceholderText(self, text):
        self.widget.setPlaceholderText(text)
