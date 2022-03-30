from ... import shelf, shelfButton
from rsTools.glob import *
import os


class rigTagShelfButton(shelfButton.ShelfButton):
    _color = (197, 161, 237)
    _title = None
    _icon = os.path.join(g_rs_path_image_shelf, "tag.svg")
    _annotation = "connect"
    _enabled = True

    # main overloading proc

    def created(self):
        pass
