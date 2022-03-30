from rsTools.ui.menus import menu
from ... import shelf, shelfButton
from rsTools.glob import *
import os
from Qt import QtCore, QtGui, QtWidgets


'''
    main overloaders:
        mouseReleased(self):
        rightMouseReleased(self):
        mousePressed(self):
        rightMousePressed(self):     
        
        
    what defines a menu?
       label
            item
            
        
        
    label = label name in menu
    type = defines the action type
    widget = needed onmly if custom action type
    id = links id to button for shared         
'''


class aboutShelfButton(shelfButton.ShelfButton):
    _color = (200, 20, 0)
    _title = "about"
    _name = "aboutButton"
    _icon = os.path.join(g_rs_path_image_shelf, "default.svg")
    _annotation = "about"
    _enabled = True

    # main overloading proc
    def created(self):

        _menuItems = {"tearOff": False,
                      "enabled": True,
                      "items_provider": None,
                      "async": False,
                      "cache": 0,
                      "items": [
                          {"label": "about", "command": lambda: self._printAbout(),
                           "toolTip": "NICE"},
                          {"label": "aboutRob", "enabled": False}
                      ]
                      }

        self._menu = menu.ContextMenu(_menuItems)
        self._menu.attachTo(self._widget, button="right")

    def mousePressed(self):
        QtWidgets.QMessageBox.about(
            self._widget, "About Me", "Lets Go Down To Funky Town")
