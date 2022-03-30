from ... import shelf, shelfButton
from rsTools.glob import *
import os


class hubShelfButton(shelfButton.ShelfButton):
    _color = (255, 242, 0)
    _title = None
    _name = "hubButton"
    _icon = os.path.join(g_rs_path_image_shelf, "hub.svg")
    _annotation = "hub"
    _enabled = True
    _titleFontSize = 5

    def mousePressed(self):
        import rsTools.ui.interfaces.hub.hubMain as hub
        hub.run()
