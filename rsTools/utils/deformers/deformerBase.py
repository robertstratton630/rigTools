import maya.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel

import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.skincluster as skinUtils
import rsTools.utils.data.IO.deformerSaveLoad as dIO
import rsTools.utils.data.geometrySaveLoad as gIO

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class DeformerBase(object):
    def __init__(self, nodeName="nodeName", mesh=None, debug=False):
        self._node = nodeName
        self._debugLocator = None
        self._mesh = mesh
        self._data = None

        # create the node
        if cmds.objExists(self._node):
            self._populateData()
        else:
            self.buildNode()
            if debug:
                self.addDebugLocator()

    def _populateData(self):
        self._populateDebugLocator()
        self._populateMesh()

    # getters

    def getDebugLocator(self):
        return self._debugLocator

    def getMesh(self):
        return self._mesh

    def getNodeName(self):
        return self._node

    ''' VIRUTAL '''

    def buildNode(self):
        pass

    def getBuildString(self, includePath=False):
        pass

    ''' populate '''

    def _populateDebugLocator(self):
        if cmds.objExists(self._node) and not skinUtils.isSkinCluster(self._node):
            loc = cmds.listConnections(self._node+".debugConnect", s=0, d=1)
            if loc:
                self._debugLocator = loc[0]
                self._debugLocatorShape = cmds.listRelatives(loc[0], p=True)

    def _populateMesh(self):
        if cmds.objExists(self._node):
            data = cmds.deformer(self._node, q=True, g=True)
            if data:
                mesh = cmds.listRelatives(data[0], p=True)[0]
                self._mesh = str(mesh)

    ''' PUBLIC '''

    def addDebugLocator(self):
        if self._node and not skinUtils.isSkinCluster(self._node):
            self._debugLocatorShape = self._node+"DEBUG_LOCShape"
            if not self._debugLocatorShape:
                self._debugLocatorShape = cmds.createNode(
                    "rig_debugLocator", n=self._debugLocatorShape)

            self._debugLocator = cmds.listRelatives(
                self._debugLocatorShape, p=True)[0]
            self._debugLocator = cmds.rename(
                self._debugLocator, self._node+"DEBUG_LOC")
            cmds.connectAttr(self._node+".debugConnect",
                             self._debugLocatorShape+".debugConnect", force=True)

    def saveData(self, deformer=True, geometry=False):
        if self._node:
            if deformer:
                dIO.saveDeformerDataCpp(self._node)
            if geometry:
                gIO.saveGeometryDataCpp(self._mesh)

    def loadData(self, version=-1, weights=True, uvMode=False, attributes=True, verbose=True):
        if weights:
            # load deformer attributes and info
            _data = dIO.loadDeformerInformation(self._node, version)
            _attributes = _data.get("attributes")

            # load attributes
            if attributes:
                attributes = _data.get("attributes")
                for a in attributes:
                    cmds.setAttr(a[0], a[1])

            if cmds.nodeType(deformer) == "skinCluster":
                joints = getSkinClusterInfluences(deformer)
                data["joints"] = joints

            dIO.loadDeformerWeightsCpp(
                self._node, version=version, doUV=uvMode, verbose=verbose)
