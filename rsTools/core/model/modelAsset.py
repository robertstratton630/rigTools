import maya.cmds as cmds
import rsTools.utils.data.osUtils as osUtils
import rsTools.utils.transforms.transforms as tUtils

class ModelAsset(object):

    def __init__(self, topNode="library_model_bearALODa_GRP",
                 modelGroup="model_GRP",
                 project=None,
                 asset=None):

        self._project = project or osUtils.get_project_show()
        self._asset = asset or osUtils.get_project_show_asset()

        self._topNode = topNode
        self._element = self._topNode.split("_")[-2]

        self._mainSet = None
        self._geometryCacheSet = None
        self._modelGroup = modelGroup

        if cmds.objExists(self._topNode):
            self._populateData()
        else:
            self._buildAsset()

    # remember nameSpace
    def _populateData(self):
        self._modelGroup = tUtils.findObjectsUnderNode(
            self._topNode, "transform", "model_GRP")[0]

        if not self._mainSet:
            self._mainSet = "rigHubSet_model_{0}".format(self._element)

        if not self._geometryCacheSet:
            self._geometryCacheSet = [items for items in cmds.sets(
                self._mainSet, q=True) if "geometryCache" in items][0]

    def _buildAsset(self):
        self._buildTopNode()
        self._buildModelGroup()
        self._buildSets()

    def _buildTopNode(self):
        self._topNode = cmds.group(em=True, name=self._topNode)
        tUtils.addSeparator(self._topNode, "rigData")
        rigTypeAttr = tUtils.attrAdd(
            self._topNode, "rigType", "model", typ="enum", **{"locked": True})
        version = tUtils.attrAdd(
            self._topNode, "version", -1, **{"locked": True})

    def _buildModelGroup(self):
        if self._topNode:
            if not cmds.objExists(self._modelGroup):
                self._modelGroup = cmds.group(self._topNode, name="model_GRP")

            self._modelGroup = cmds.parent(self._modelGroup, self._topNode)[0]

            # attributes
            mode = tUtils.attrAdd(self._topNode, "modelMode", [
                                  "normal", "template", "reference"], typ="enum", **{"locked": False})
            tUtils.enableDrawOverrides(self._modelGroup)
            cmds.connectAttr(mode, self._modelGroup+".overrideDisplayType")

    def _buildSets(self):
        if self._topNode:
            self._mainSet = shotBuild.createSet(
                "model", self._element, self._topNode)
            meshes = tUtils.findObjectsUnderNode(self._modelGroup, "transform")
            self._geometryCacheSet = cmds.sets(
                meshes, name="rigHubSet_model_geometryCache")
            shotBuild.addSetItem(self._geometryCacheSet, self._mainSet)

    ''' cache item setters '''
    def addCacheItem(items):
        shotBuild.addSetItem(items, self._geometryCacheSet)

    def removeCacheItem(items):
        shotBuild.removeSetItem(items, self._geometryCacheSet)

    def deleteSets(self):
        cmds.delete(self._geometryCacheSet)
        cmds.delete(self._mainSet)

    '''getters'''

    def getTopNode(self):
        return self._topNode

    def getElement(self):
        return self._element

    def getModelGroup(self):
        return self._modelGroup

    def getMainSet(self):
        return self._mainSet

    def getGeometryCacheSet(self):
        return self._geometryCacheSet
