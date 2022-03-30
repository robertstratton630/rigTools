import _shelvesData
import shelfButton as _button

import inspect
import maya.OpenMayaUI as omm
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import os
import pymel.core as pm
import pymel.core as pm
import weakref

from rsTools.glob import *


'''
    generating basic shelf:
        shelf = shelf.Shelf("myShelf")
        shelf.createShelf()
        shelf.destroyShelf()
        shelf.exists()
    
    
    generating basic button / shelf: 
        shelf = shelf.Shelf("ewqe")
        class CustomButton(shelfButton.ShelfButton):
                _color = (190,190,190)
                _title = "red"    
        shelf.addButton(CustomButton)
        shelf.createShelf()
        
    
'''
import logging
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class Shelf(object):
    def __init__(self, shelfName, parent=None):
        super(Shelf, self).__init__()
        self._name = shelfName
        self._topShelf = mel.eval("$temp = $gShelfTopLevel")
        self._items = list()
        self._callbackID = -1

        self.parent = parent or self._topShelf

    # returns name
    def __str__(self):
        return self._name

    # destory ui
    def __del__(self):
        self.destroy_shelf()

    # build shelf
    def create_shelf(self):
        if self.exists:  # if shelf exists destory it
            self.destroy_shelf()

        cmds.shelfLayout(self._name, p=self.parent)
        for ch in cmds.shelfLayout(self.name, q=True, ca=True) or []:
            cmds.deleteUI(ch)

        self._callbackID = omui.MUiMessage.addUiDeletedCallback(
            self._name, self.destroy_shelf)
        _logger.debug("building shelf")
        self.build_items()

    # build the items for the shelf
    def build_items(self):
        for item in self._items:
            if isinstance(item, _button.ShelfButton):
                item._shelf = self
                item.create()
            elif item == "separator":
                item = self._separator(self._name)
            else:
                pass

    # destory the shielf

    def destroy_shelf(self):
        _logger.debug("---Destorying Existing Shelf---")
        self.destory_buttons()  # destory all the buttons
        _logger.debug("--Destoried Buttons--")
        if self._callbackID != -1:
            try:
                omui.MUiMessage.removeCallback(self._callbackID)
            except:
                pass
        _logger.debug("--Destoried CallBack--")
        if self.exists:  # if ui still exists, delete the main shelf
            try:
                cmds.deleteUI(self._name)
            except:
                pass
        _logger.warn("Destorying Existing Shelf END")

    @staticmethod
    def _separator(p):
        image = "{0}".format(os.path.join(
            g_rs_path_image_shelf, "separator.svg"))
        return cmds.shelfButton(width=2, parent=p, image=image, style="iconOnly")

    @property
    def name(self):
        return self._name

    @property
    def buttons(self):
        return dict([btn for btn in self._items if btn != "separator"])

    @property
    def exists(self):
        return cmds.shelfLayout(self._name, q=True, exists=True)

    def destory_buttons(self):
        if self.exists:  # if layout exists
            # get all buttons of shelf
            for c in cmds.layout(self._name, q=True, ca=True) or []:
                cmds.deleteUI(c)  # delete buttons
            for item in self._items:  # if shelfButton object then destory
                if isinstance(item, _button.ShelfButton):
                    try:
                        item.destoryButton()
                    except:
                        pass

    # add separator
    def add_separator(self):
        if(len(self._items) > 0 and self._items[-1] != "separator"):
            self._separator(self._name)
            self._items.append("separator")

    def add_button(self, button="Button", name="Name", color=(90, 90, 90), annotation=None, command=None):
        if type(button) in (str, unicode):
            name = name or "{}_ShelfButton{}".format(
                self._name.split("|")[-1], len(self._items))
            _logger.debug("Adding Button From Str {0}".format(name))
            self._items.append(_button.ShelfButton(
                parentShelf=self, name=name, color=color, annotation=annotation, command=command))

        elif isinstance(button, _button.ShelfButton):
            _logger.debug("Adding Button From Class{0}".format(button))
            self._items.append(button)
            button.parentShelf = self
        elif inspect.isclass(button) and issubclass(button, _button.ShelfButton):
            _logger.debug("Adding Button {0} From Inspect".format(button))
            self._items.append(button(parentShelf=self))

        else:
            print("Invalid Button Name")

        return weakref.ref(self._items[-1])
