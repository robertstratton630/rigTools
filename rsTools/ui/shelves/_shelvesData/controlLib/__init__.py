from ... import shelf, shelfButton
from rsTools.glob import *
import os


class controlLibShelfButton(shelfButton.ShelfButton):
    _color = (255, 157, 0)
    _title = None
    _name = "controlLibrary"
    _icon = os.path.join(g_rs_path_image_shelf, "controlLib.svg")
    _annotation = "controlLibrary"
    _enabled = True
    _titleFontSize = 5

    def mousePressed(self):
        import rsTools.ui.interfaces.controlBuilder.controlBuilder as ui
        ui.run()
