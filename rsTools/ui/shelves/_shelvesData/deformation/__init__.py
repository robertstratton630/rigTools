from ... import shelf, shelfButton
from rsTools.glob import *
import os


class deformersShelfButton(shelfButton.ShelfButton):
    _color = (255, 157, 0)
    _title = None
    _icon = os.path.join(g_rs_path_image_shelf, "bound.svg")
    _annotation = "bound"
    _enabled = True

    # main overloading proc

    def created(self):
        pass
