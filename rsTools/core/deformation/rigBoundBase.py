import logging
import maya.cmds as cmds
import os

import rsTools.utils.data.string as string
import rsTools.utils.data.curveData as curveData
import rsTools.utils.data.osUtils as osUtils
import rsTools.utils.data.scene.topNode as topUtils
import rsTools.utils.transforms.transforms as tUtils

from rsTools.core.model.modelAsset import ModelAsset
from rsTools.core.skeleton.skeletonAsset import SkeletonAsset
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


"""
        base abstract class for building deformation rigSkeleton

        topnode = topnode of rig
        project = current project name
        asset   = asset name
        rigBOundElement = lod
"""


class RigBoundBase(object):
    def __init__(self, topNode=None,
                 project=None,
                 asset=None,
                 rigBoundElement=None,
                 **kwargs):

        # set the default parameters
        self._project = project or osUtils.get_project_show()
        self._asset = asset or osUtils.get_project_show_asset()
        self._rigBoundElement = rigBoundElement or str(
            self._asset[4:].lower()+"ALODa")
        self._topNode = topNode or self._project + \
            "_rigBound_"+self._rigBoundElement+"_GRP"

        # main things for gathering
        self._rigSkeletonElement = kwargs.get(
            "skeletonElement", self._rigBoundElement)
        self._rigSkeletonVersion = kwargs.get("skeletonVersion", -1)

        self._modelElement = kwargs.get("modelElement", self._rigBoundElement)
        self._modelVersion = kwargs.get("modelVersion", -1)

        # maya transforms / nodes
        self._rootJoint = kwargs.get("rootJoint", None)

        self._mainSet = None
        self._skeletonCacheSet = None
        self._modelCacheSet = None

        # build or populate
        if not cmds.objExists(self._topNode):
            self._buildAsset()
        else:
            self._populateData()

    def __upgrade__():
        pass

        # load rigging meshes

        # apply skinclusters

        # im just testing sublime merge UI
        # im just adding another line in

    ''' internals '''

    def _buildAsset(self):
        self._buildTopNode()
        self._buildGlobalContorl()
        self._buildMainGroups()
        self._gatherRigSkeleton()
        self._gatherModel()

    def _populateData(self):
        pass

    """ build top node for meta data"""

    def _buildTopNode(self):
        self._topNode = cmds.group(em=True, name=self._topNode)
        tUtils.addSeparator(self._topNode, "rigData")
        rigTypeAttr = tUtils.attrAdd(
            self._topNode, "rigType", "rigBound", typ="enum", **{"locked": True})
        element = tUtils.attrAdd(self._topNode, "element", str(
            self._rigBoundElement), typ="enum", **{"locked": True})
        version = tUtils.attrAdd(
            self._topNode, "version", "-v1", typ="enum", **{"locked": True})
        self._mainSet = shotBuild.createSet(
            "rigBound", self._rigBoundElement, self._topNode)

    """ build global control """

    def _buildGlobalContorl(self):
        if self._topNode:
            control = curveData.buildControlShape(
                "global_CTRL", "global", color=17)
            self._globalControl = cmds.parent(control, self._topNode)[0]

    """ build all the core groups """

    def _buildMainGroups(self):
        if self._topNode:
            self._jointGroup = tUtils.transformCreate(
                "", "skeleton", parent=self._globalControl)
            self._modelGroup = tUtils.transformCreate(
                "", "model", parent=self._topNode)
            self._rigModelGroup = tUtils.transformCreate(
                "", "rigModel", parent=self._topNode)
            self._rigGroup = tUtils.transformCreate(
                "", "rig", parent=self._globalControl)

            # attributes
            tUtils.addSeparator(self._globalControl, "displaySettings")
            skeletonMode = tUtils.attrAdd(self._globalControl, "skeletonMode", [
                "normal", "template", "reference"], typ="enum", **{"locked": False})
            tUtils.enableDrawOverrides(self._jointGroup)
            cmds.connectAttr(skeletonMode, self._jointGroup +
                             ".overrideDisplayType")

            modelMode = tUtils.attrAdd(self._globalControl, "modelMode", [
                "normal", "template", "reference"], typ="enum", **{"locked": False})
            tUtils.enableDrawOverrides(self._modelGroup)
            cmds.connectAttr(modelMode, self._modelGroup +
                             ".overrideDisplayType")

    """ gather rig skeleton """

    def _gatherRigSkeleton(self):

        # check file path
        basePath = os.path.join(osUtils.get_project_show_asset_path(
        ), "Release", "rigSkeleton", self._rigSkeletonElement)
        if self._rigSkeletonVersion == -1:
            versions = array.sort(osUtils.getSubdirs(basePath))
            self._rigSkeletonVersion = versions[-1]

        # got match
        if os.path.exists(basePath):
            # get file
            fileName = "{0}_{1}.ma".format(
                self._rigSkeletonElement, self._rigSkeletonVersion)
            fullPath = os.path.join(
                basePath, self._rigSkeletonVersion, fileName)
            shotBuild.importScene(fullPath)

            #import skeleton
            rigSkeleton = SkeletonAsset(
                topUtils.getTopNodes(assetType="rigSkeleton")[0])
            self._rootJoint = rigSkeleton.getRootJoint()
            skeletonTopNode = rigSkeleton.getTopNode()

            # reparent rootJoint
            jointGroupLong = tUtils.findObjectsUnderNode(
                self._topNode, "transform", self._jointGroup)
            self._rootJoint = cmds.parent(self._rootJoint, jointGroupLong)[0]

            # delete sets and delete topNode
            rigSkeleton.deleteSets()
            cmds.delete(skeletonTopNode)

            joints = tUtils.findObjectsUnderNode(self._jointGroup, "joint")
            self._skeletonCacheSet = cmds.sets(
                joints, name="rigHubSet_rigBound_skeletonCache")
            shotBuild.addSetItem(self._skeletonCacheSet, self._mainSet)

            element = tUtils.attrAdd(self._topNode, "skeletonElement", str(
                self._rigSkeletonElement), typ="enum", **{"locked": True})
            v = tUtils.attrAdd(self._topNode, "skeletonVersion", str(
                self._rigSkeletonVersion), typ="enum", **{"locked": True})

    def _gatherModel(self):
        # find file path
        basePath = os.path.join(
            osUtils.get_project_show_asset_path(), "Release", "model", self._modelElement)
        if self._modelVersion == -1:
            versions = array.sort(osUtils.getSubdirs(basePath))
            self._modelVersion = versions[-1]

        # check base paths
        if os.path.exists(basePath):
            fileName = "{0}_{1}.ma".format(
                self._modelElement, self._modelVersion)
            fullPath = os.path.join(basePath, self._modelVersion, fileName)
            shotBuild.importScene(fullPath)

            # gather model
            modelAsset = ModelAsset(topUtils.getTopNodes(assetType="model")[0])
            modelGroup = modelAsset.getModelGroup()
            items = cmds.listRelatives(
                modelGroup, f=True, c=True, typ="transform")

            rBoundModelGroup = tUtils.findObjectsUnderNode(
                self._topNode, "transform", "model_GRP")[0]
            cmds.parent(items, rBoundModelGroup)

            modelAsset.deleteSets()
            cmds.delete(modelAsset.getTopNode())

            groups = tUtils.findObjectsUnderNode(
                "model_GRP", "transform", "_GRP", True)
            for g in groups:
                longNameOld = tUtils.findObjectsUnderNode(
                    "model_GRP", "transform", g, False)[0]
                longName = longNameOld[:-4] + "Model" + longNameOld[-4:]
                cmds.rename(longNameOld, sUtils.getNameShort(longName))

            element = tUtils.attrAdd(self._topNode, "modelElement", str(
                self._modelElement), typ="enum", **{"locked": True})
            v = tUtils.attrAdd(self._topNode, "modelVersion", str(
                self._modelVersion), typ="enum", **{"locked": True})
