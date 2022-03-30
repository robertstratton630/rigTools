from ... import shelf, shelfButton
from rsTools.glob import *
import os


class rigConnectShelfButton(shelfButton.ShelfButton):
    _color = (197, 161, 237)
    _title = None
    _icon = os.path.join(g_rs_path_image_shelf, "connection.svg")
    _annotation = "connect"
    _enabled = True

    # main overloading proc

    def created(self):
        pass
