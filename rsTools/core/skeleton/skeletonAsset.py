import maya.cmds as cmds
import rsTools.utils.data.osUtils as osUtils
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.curveData as curveData
import logging



class SkeletonAsset(object):

    def __init__(self, topNode="library_rigSkeleton_bearALODa_GRP",
                 rootJoint=None,
                 project=None,
                 asset=None):

        self._project = project or osUtils.get_project_show()
        self._asset = asset or osUtils.get_project_show_asset()

        self._topNode = topNode
        self._element = self._topNode.split("_")[-2]

        self._rootJoint = rootJoint
        self._jointGroup = None
        self._globalControl = None
        self._mainSet = None
        self._skeletonCacheSet = None

        if cmds.objExists(self._topNode):
            self._populateData()
            _logger.info("Populating RigSkeleton Data")
        else:
            if not self._rootJoint:
                _logger.warning("Joint Group Doesn't Exist")
                return
            self._buildAsset()
            _logger.info("Built RigSkeleton Asset")

    # remember nameSpace
    def _populateData(self):
        if not self._jointGroup:
            self._jointGroup = tUtils.findObjectsUnderNode(
                self._topNode, "transform", "skeleton_GRP")

        if not self._globalControl:
            self._jointGroup = tUtils.findObjectsUnderNode(
                self._topNode, "transform", "global")

        if not self._mainSet:
            self._mainSet = "rigHubSet_rigSkeleton_{0}".format(self._element)

        if not self._skeletonCacheSet:
            self._skeletonCacheSet = "rigHubSet_rigSkeleton_skeletonCache"

        if not self._rootJoint:
            joints = tUtils.findObjectsUnderNode(self._jointGroup, "joint")
            if joints:
                self._rootJoint = joints[-1]

    def _buildAsset(self):
        self._buildTopNode()
        self._buildGlobalContorl()
        self._buildSkeletonGroup()
        self._buildSets()

    def _buildTopNode(self):
        self._topNode = cmds.group(em=True, name=self._topNode)
        tUtils.addSeparator(self._topNode, "rigData")
        rigTypeAttr = tUtils.attrAdd(
            self._topNode, "rigType", "rigSkeleton", typ="enum", **{"locked": True})
        version = tUtils.attrAdd(
            self._topNode, "version", -1, **{"locked": True})

    def _buildGlobalContorl(self):
        if self._topNode:
            control = curveData.buildControlShape(
                "global_CTRL", "global", color=17)
            self._globalControl = cmds.parent(control, self._topNode)[0]

    def _buildSkeletonGroup(self):
        if self._topNode:
            self._jointGroup = tUtils.transformCreate(
                "", "skeleton", parent=self._globalControl)
            self._rootJoint = cmds.parent(self._rootJoint, self._jointGroup)[0]

            # attributes
            tUtils.addSeparator(self._globalControl, "displaySettings")
            skeletonMode = tUtils.attrAdd(self._globalControl, "skeletonMode", [
                                          "normal", "template", "reference"], typ="enum", **{"locked": False})
            tUtils.enableDrawOverrides(self._jointGroup)

            cmds.connectAttr(skeletonMode, self._jointGroup +
                             ".overrideDisplayType")

    def _buildSets(self):
        if self._topNode:
            self._mainSet = shotBuild.createSet(
                "rigSkeleton", self._element, self._topNode)
            joints = tUtils.findObjectsUnderNode(self._jointGroup, "joint")
            self._skeletonCacheSet = cmds.sets(
                joints, name="rigHubSet_rigSkeleton_skeletonCache")
            shotBuild.addSetItem(self._skeletonCacheSet, self._mainSet)

    ''' cache item setters '''
    def addCacheItem(items):
        shotBuild.addSetItem(items, self._skeletonCacheSet)

    def removeCacheItem(items):
        shotBuild.removeSetItem(items, self._skeletonCacheSet)

    def deleteSets(self):
        cmds.delete(self._skeletonCacheSet)
        cmds.delete(self._mainSet)

    '''getters'''

    def getTopNode(self):
        return self._topNode

    def getElement(self):
        return self._element

    def getSkeletonGroup(self):
        return self.skeletonGroup

    def getGlobalControl(self):
        return self._globalControl

    def getMainSet(self):
        return self._mainSet

    def getSkeletonCacheSet(self):
        return self._skeletonCacheSet

    def getRootJoint(self):
        return self._rootJoint
