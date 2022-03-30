from ... import shelf, shelfButton
from rsTools.glob import *
import os


class AssetCheckerShelfButton(shelfButton.ShelfButton):
    _color = (255, 242, 0)
    _title = None
    _name = "AssetChecker"
    _icon = os.path.join(g_rs_path_image_shelf, "assetChecker.svg")
    _annotation = "AssetChecker"
    _enabled = True
    _titleFontSize = 5

    def mousePressed(self):
        import rsTools.ui.interfaces.modelCompare.modelCompareUI as modelCompare
        modelCompare.run()
