from rsTools.ui.menus import menu
from ... import shelf, shelfButton
from rsTools.glob import *
import os
import rsTools.utils.osUtils.enviroments as env
import maya.cmds as cmds
from rsTools.core.skeleton import skeletonAsset


class skeletonShelfButton(shelfButton.ShelfButton):
    _color = (255, 157, 0)
    _title = None
    _icon = os.path.join(g_rs_path_image_shelf, "bones.svg")
    _annotation = "anim"
    _enabled = True

    # main overloading proc
    def created(self):

        _menuItems = {"tearOff": False,
                      "enabled": True,
                      "items_provider": None,
                      "async": False,
                      "cache": 0,
                      "items": [{"label": "QuickUI", "enabled": False},
                                {"label": "joint Tool Box", "command": lambda: self._buildJointToolBox(
                                ), "toolTip": "NICE"},
                                {"label": "joint Pose UI", "command": lambda: self._buildJointPoseUI(
                                ), "toolTip": "NICE"},
                                "separator",
                                {"label": "rigSkeleton Build", "enabled": False},
                                {"label": "rigSkeleton", "actionType": "skeletonAsset", "id": "skeletonAction",
                                    "command": lambda: self._createRigSkeleton(), "toolTip": "Create rigSkeletonAsset"},
                                ]
                      }

        self._menu = menu.ContextMenu(_menuItems)
        self._menu.attachTo(self._widget, button="right")

    def _buildJointToolBox(self):
        import rsTools.ui.interfaces.joints.jointsUI as jointUI
        jointUI.run()

    def _buildJointPoseUI(self):
        import rsTools.ui.interfaces.jointPose.jointPoseUI as jointUI
        jointUI.run()

    def _createRigSkeleton(self):

        ls = cmds.ls(sl=True)
        if ls:
            obb = self._menu.getActionByID("skeletonAction")
            assetName = obb.getText()
            lod = obb.getComboText()

            project = env.get_project_show()
            topNodeName = project+"_rigSkeleton_"+assetName+lod+"_GRP"
            rigSkeletonAsset = skeletonAsset.SkeletonAsset(topNodeName, ls[0])
            obb.setPlaceholderText("bearA")

    def mousePressed(self):
        import rsTools.ui.interfaces.joints.jointsUI as ui
        ui.run()
