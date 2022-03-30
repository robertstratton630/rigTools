from rsTools.ui.menus import menu
import os
from Qt import QtCore, QtWidgets, QtGui
from rsTools.utils.data.osUtils import osUtils
from functools import partial


from rsTools.ui.menus.actions import FolderSelectAction
########################################################################################################################################################
# PROJECT
########################################################################################################################################################


class hubProjectMenu(QtCore.QObject):
    update = QtCore.Signal()

    def __init__(self, parent=None, shows=[]):
        super(hubProjectMenu, self).__init__()
        self._widget = parent
        self._shows = shows
        self._showMenuItems = []
        self._currentShow = g_project_show
        self.attach()

    def attach(self):
        self._populateItems()
        _menuItems = {"tearOff": False,
                      "enabled": True,
                      "items_provider": None,
                      "async": False,
                      "cache": 0,
                      "items": self._showMenuItems
                      }

        self._menu = menu.ContextMenu(_menuItems)
        self._menu.attachTo(self._widget, button="right")

    def _populateItems(self):

        projects = osUtils.listAllProjects()
        self._showMenuItems = []
        self._showMenuItems.append({"label": "Select Show", "enabled": False})

        for show in projects:
            self._showMenuItems.append({"label": show, "command": partial(
                self._setShowEvent, show), "toolTip": "setShow"})

        self._showMenuItems.append({"label": "Enter New Show", "actionType": "text",
                                    "toolTip": "setShow", "id": "lineEditID", "command": lambda: self._addNewShow()})

    def _setShowEvent(self, show):
        osUtils.set_project_show(show)
        self.update.emit()

    # add new show... get name/build rootDir/ updates lists/emit update for label

    def _addNewShow(self):
        obb = self._menu.getActionByID("lineEditID")
        newShow = obb.getText()
        osUtils.set_project_show(newShow)
        self.rebuild()
        self.update.emit()

    def rebuild(self):
        self._populateItems()
        _menuItems = {"tearOff": False,
                      "enabled": True,
                      "items_provider": None,
                      "async": False,
                      "cache": 0,
                      "items": self._showMenuItems
                      }
        self._menu.rebuildDescription(_menuItems)


########################################################################################################################################################
# PROJECT ROOT
########################################################################################################################################################

class hubProjectRootMenu(QtCore.QObject):
    update = QtCore.Signal()

    def __init__(self, parent=None):
        super(hubProjectRootMenu, self).__init__(parent)
        self._widget = parent
        self._populateShowsItems()
        self.attach()
        self._rootPath = ""

    def attach(self):
        _menuItems = {"tearOff": False,
                      "enabled": True,
                      "items_provider": None,
                      "async": False,
                      "cache": 0,
                      "items": self._showMenuItems
                      }

        self._menu = menu.ContextMenu(_menuItems)
        self._menu.attachTo(self._widget, button="right")

    def _updateRoot(self):
        path = os.path.normpath(self.sender().getText())
        osUtils.set_project_rootpath(path)
        self.update.emit()

    def _populateShowsItems(self):
        self._showMenuItems = []
        self._showMenuItems.append(
            {"label": "Select Root Directory", "enabled": False})
        self._showMenuItems.append({"label": "Root Path", "actionType": "folderSelect",
                                    "id": "folderSelect", "signals": {"textEdited": self._updateRoot}})


########################################################################################################################################################
# PROJECT ROOT
########################################################################################################################################################

class hubProjectAsset(QtCore.QObject):
    update = QtCore.Signal()

    def __init__(self, parent=None):
        super(hubProjectAsset, self).__init__(parent)
        self._widget = parent
        self.attach()

    def attach(self):
        self._populateItems()

        _menuItems = {"tearOff": False,
                      "enabled": True,
                      "items_provider": None,
                      "async": False,
                      "cache": 0,
                      "items": self._showMenuItems
                      }

        self._menu = menu.ContextMenu(_menuItems)
        self._menu.attachTo(self._widget, button="right")

    def _populateItems(self):
        self._showMenuItems = []
        self._showMenuItems.append({"label": "Select Asset", "enabled": False})

        assets = osUtils.listAllAssets()

        for asset in assets:
            self._showMenuItems.append({"label": asset, "command": partial(
                self._setAssetEvent, asset), "toolTip": "setShow"})

        self._showMenuItems.append("separator")
        self._showMenuItems.append(
            {"label": "Create New Asset", "enabled": False})
        self._showMenuItems.append({"label": "New Asset", "actionType": "assetPicker",
                                    "toolTip": "setShow", "id": "actionPickerID", "command": lambda: self._addNewAsset()})

    def _setAssetEvent(self, asset):
        osUtils.set_project_show_asset(asset)
        self.update.emit()

        # add new show... get name/build rootDir/ updates lists/emit update for label
    def _addNewAsset(self):
        obb = self._menu.getActionByID("actionPickerID")
        assetName = obb.getText()
        assetType = obb.getComboText()
        niceName = assetType+assetName

        # create new project skeleton folders
        osUtils.set_project_show_asset(niceName)
        shotBuild.buildAssetProjectRoot(niceName)

        self.rebuild()
        self.update.emit()

    def rebuild(self):
        self._populateItems()
        _menuItems = {"tearOff": False,
                      "enabled": True,
                      "items_provider": None,
                      "async": False,
                      "cache": 0,
                      "items": self._showMenuItems
                      }

        self._menu.rebuildDescription(_menuItems)
