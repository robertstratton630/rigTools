from ... import shelf, shelfButton
from rsTools.glob import *
import os


class poseShelfButton(shelfButton.ShelfButton):
    _color = (164, 181, 222)
    _title = None
    _icon = os.path.join(g_rs_path_image_shelf, "pose.svg")
    _annotation = "pose"
    _enabled = True

    def mousePressed(self):
        import rsTools.ui.interfaces.jointPose.jointPoseUI as ui
        ui.run()
