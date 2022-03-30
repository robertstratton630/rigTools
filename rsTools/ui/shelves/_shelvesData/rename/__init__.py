from ... import shelf, shelfButton
from rsTools.glob import *
import os


class renameShelfButton(shelfButton.ShelfButton):
    _color = (197, 161, 237)
    _title = "ABC"
    _icon = os.path.join(g_rs_path_image_shelf, "default.svg")
    _annotation = "rename"
    _enabled = True

    # main overloading proc

    def created(self):
        pass
