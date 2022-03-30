from ... import shelf, shelfButton
from rsTools.glob import *
import os


class weightmapShelfButton(shelfButton.ShelfButton):
    _color = (156, 237, 57)
    _title = None
    _icon = os.path.join(g_rs_path_image_shelf, "weights.svg")
    _annotation = "skin"
    _enabled = True

    # main overloading proc

    def created(self):
        pass
