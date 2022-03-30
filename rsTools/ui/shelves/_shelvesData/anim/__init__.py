from ... import shelf, shelfButton
from rsTools.glob import *
import os


class animShelfButton(shelfButton.ShelfButton):
    _color = (255, 157, 0)
    _title = None
    _icon = os.path.join(g_rs_path_image_shelf, "face.svg")
    _annotation = "anim"
    _enabled = True

    # main overloading proc

    def created(self):
        pass
