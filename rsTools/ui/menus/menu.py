import collections
import operator
import re

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
from rsTools.rsGlobal import *
from rsTools.ui import qtWrap
from rsTools.ui.menus import actions as _Actions
from rsTools.ui.menus import thread as _Thread


class _ContextMenuEventFilter(QtCore.QObject):
    menuRequested = QtCore.Signal(QtCore.QPoint)

    def __init__(self, parent, button, mods):
        super(_ContextMenuEventFilter, self).__init__(parent)
        self._parent = parent
        self._button = button
        self._mods = int(reduce(operator.or_, [0]+mods))

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == self._button and int(event.modifiers()) == self._mods:
                self.menuRequested.emit(event.pos())
                return True

        return False


'''
A Description consists of:
    {"tearOff": False,
    "enabled": True,
    "items":[]}

Inside Items contains an array of things to add to the menuAction:

    label
    actionType
    widget
    command
    enabled
    checkable
    id
    icon
    separator
    toolTip
    state
    
'''


class ContextMenu(QtWidgets.QMenu):

    __defaults__ = {"tearOff": False,
                    "enabled": True,
                    "items": []}

    __actionsMatch__ = {"default": QtWidgets.QAction,
                        "button": _Actions.ButtonAction,
                        "html": _Actions.HTMLAction,
                        "text": _Actions.TextAction,
                        "custom": _Actions.CustomWidgetAction,
                        "folderSelect": _Actions.FolderSelectAction,
                        "assetPicker": _Actions.AssetPickerAction,
                        "skeletonAsset": _Actions.SkeletonAssetAction
                        }

    # border: 2px solid rgba (32,32,32,0.16); padding:5px 18px 4px 24px;
    __style__ = '''
                QMenu
                {
                    font-size: 11px;
                    font-family: Arial;
                    background: #333;
                    margin: 0px;
                    border: 2px solid;
                    border-color: rgba(32,32,32,200);
                }
                
                QMenu::item,QLabel
                {
                    padding: 5px 18px 4px 24px;
                    color:#CCC;
                    border-radius: 6px;
                }
                
                QMenu::item:disabled,QLabel:disabled
                {
                    background: #333;
                    color:#888;
                }
                
                QMenu::item:selected,QLabel:hover,QLabel:selected
                {
                    background: #555;
                    color:#EEE;
                }
                
                QMenu::item:disabled:selected
                {
                    background: #333;
                    color:#888;
                }
                
                QMenu::item:separator
                {   
                    height:1px,
                    background: #444;
                    margin: 2px 0px 2px 0px;
                }
        '''

    def __init__(self, description={}, parent=None, ids=None):
        super(ContextMenu, self).__init__(parent)
        self._provider = None
        self._defaultActions = list()
        self._staticActions = list()
        self._dynamicActions = list()

        self._ids = ids
        self._extend = False
        self._widget = None
        self._filter = None
        self._groups = list()
        self._separators = list()
        self._description = self.set_description(description)

        self.setStyleSheet(self.__style__)

        # aboutToShow is the main function to rebuild
        self.aboutToShow.connect(self._aboutToShow)

    '''
    --------------------------------------------------------------------------------------------------------------
       FUNCTIONS FOR SETTING DESCRIPTION
    --------------------------------------------------------------------------------------------------------------
       
    '''

    def get_description(self):
        return self._description

    def set_description(self, _description):
        if not isinstance(_description, collections.Mapping):
            raise "Description is not a collections.Mapping Object"

        # this appends all the default key values to the description if they dont exist
        self._description = {key: _description.get(
            key, self.__defaults__[key]) for key in self.__defaults__}

        # set some defaults
        self.setEnabled(self._description["enabled"])
        self.setTearOffEnabled(self._description["tearOff"])

        # add items to the actions
        if self._description["items"]:
            self._staticActions = self.addItemsFromDescription(
                self._description["items"])

    '''
    --------------------------------------------------------------------------------------------------------------
       FUNCTIONS FOR DISPLAYING ACTIONS
    --------------------------------------------------------------------------------------------------------------
       
    '''

    def _aboutToShow(self):
        self._showMenuActions()

    def _showMenuActions(self):
        # delete all existing defaultActions and rebuild the lists
        if self._extend:
            for a in self._defaultActions:
                a.deleteLater()
            self._build_default_actions()
            self._build_static_actions()

        self._build_dynamic_actions()
        self.update()

    def rebuildDescription(self, description):

        if self._defaultActions is not None:
            for a in self._defaultActions:
                a.deleteLater()

        if self._staticActions is not None:
            for a in self._staticActions:
                a.deleteLater()

        self._staticActions = None
        self.clear()
        self._description = {key: description.get(
            key, self.__defaults__[key]) for key in self.__defaults__}
        if self._description["items"]:
            self._staticActions = self.addItemsFromDescription(
                self._description["items"])

    def _build_static_actions(self):
        for action in self._staticActions:
            self.addAction(action)

    def _build_default_actions(self):
        self._defaultActions = list()
        if self._widget is not None:
            contextMenu = self._widget.createStandardContextMenu()
            # action in every children of
            for action in (c for c in contextMenu.children() if isinstance(c, QtWidgets.QWidget) and c.isVisable()):
                if not (action.isSeparator() and action.text() == "") or not action.isVisable():
                    continue
                action.setParent(self)
                self._defaultActions.append(action)
                self.addAction(action)

            self._defaultActions.append(self.addSeparator())

    def _build_dynamic_actions(self):
        if self._provider is not None:
            items = []

            if(self._dyanmicActions):
                for a in self._dyanmicActions:
                    a.deleteLater()
            try:
                items = self._provider
            except:
                print "Cannot Assign providerActions to list"
            finally:
                self._dynamicActions = self.addItemsFromDescription(items)

    '''
    --------------------------------------------------------------------------------------------------------------
       MAIN FUNCTIONS FOR ATTCHING MENUS BY USERS
    --------------------------------------------------------------------------------------------------------------
       
    '''

    def attachTo(self, widget, button=QtCore.Qt.RightButton, modifiers=[], extend=False):

        # check widget
        if isinstance(widget, basestring):
            widgetName = widget
            widget = qtWrap.getQtObject(widgetName)
            if widget is None:
                raise "Cannot Find Widget"
        elif not isinstance(widget, QtWidgets.QWidget):
            raise "Object is not type QWidget, Cannot Attach"

        # check button
        if isinstance(button, basestring):
            button = {"left": QtCore.Qt.LeftButton,
                      "right": QtCore.Qt.RightButton,
                      "middle": QtCore.Qt.MiddleButton}.get(button.lower().strip(), QtCore.Qt.RightButton)
        self._extend = extend
        self._widget = widget

        # get the "current" contextMenuPolicy
        self._attachPreviousContextMenuPolicy = self._widget.contextMenuPolicy()

        if extend:
            # if anything in the context menu is requested. build ui
            self._widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self._widget.customContextMenuRequested.connect(self.showMenu)
        else:
            # attach event filter to the widget itself which builds the ui
            self._widget.removeEventFilter(self._filter)
            self._filter = _ContextMenuEventFilter(
                self._widget, button, modifiers)

            self._widget.installEventFilter(self._filter)
            self._filter.menuRequested.connect(self.showMenu)
            return self

    '''
    --------------------------------------------------------------------------------------------------------------
       FUNCTIONS FOR INTERNALS
    --------------------------------------------------------------------------------------------------------------
       
    '''

    def showMenu(self, localPos=None):
        if self._widget is not None:
            self.popup(self._widget.mapToGlobal(localPos))

    def addItemsFromDescription(self, itemDescription):
        if not hasattr(itemDescription, "__iter__"):
            raise ("Attempting to add Item thats not iteratable")

        ret = [self._createActionFromItem(data) for data in itemDescription]
        return ret

    def getActionByID(self, id):
        return self._ids.get(id, None)

    def _createActionFromItem(self, data):
        # make sure to init new ids dict
        if self._ids is None:
            self._ids = dict()

        # if the item is a separator, add and return
        if data in ("separator", "|", "seperator"):
            _sep = self.addSeparator()
            self._separators.append(_sep)
            return _sep

        elif not isinstance(data, collections.Mapping):
            print "NOT MAPPING"

        label = data.get("label", "undefined")
        actionType = data.get("actionType", "default")

        if actionType == "group":
            action = _Actions.InlineActionGroup(
                self, label if label != "undefined" else None)
            action.setExclusive(False)
            action.setVisible(True)
            action.setActions([self._createActionFromItem(a)
                               for a in data.get("items", list())])

        # this is a submenu - recurvsive call
        elif "items" in data:
            subMenu = ContextMenu(data, parent=self, ids=self._ids)
            action = self.addAction(label)
            action.setMenu(subMenu)

        # no subMenu
        else:
            # add custom menu but also check the state
            if actionType == "custom":
                customWidget = data.get("widget", None)
                if customWidget is not None:
                    if issubclass(customWidget, _Actions.WidgetActionBase):
                        action = customWidget.widget()
                    else:
                        action = CustomWidgetAction(self, widget)
                        if issubclass(widget, _Actions.StateWidgetBase):
                            state = data.get("state", None)
                            if state is not None:
                                action.setState(state)

            else:
                action = self.__actionsMatch__.get(
                    actionType, QtWidgets.QAction)(self)

                # get status tip
                tip = data.get("toolTip", False)
                if tip:
                    action.setStatusTip(str(tip))

                # see if checkable
                _checkable = data.get("checkable", False)
                if _checkable:
                    action.setChecked(_checkable)

                if isinstance(action, _Actions.WidgetActionBase):
                    action.extraParse(data)

                command = data.get("command", False)
                if command:
                    action.triggered.connect(command)

                action.setText(label)
                self.addAction(action)

                action.setSeparator(data.get("separator", False))

        # add id
        _id = data.get("id", None)
        if _id:
            self._ids[_id] = action

        # add icon
        _icon = data.get("icon", None)
        if _icon:
            action.setIcon(_icon)

        # setEnabled
        action.setEnabled(data.get("enabled", True))
        return action

    @property
    def groups(self):
        return self._groups
