import maya.cmds as cmds
import maya.OpenMaya as om
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.deformer as dUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.shaders as shader

import rsTools.utils.deformers.deformerIO.deformerSaveLoad as dIO
import rsTools.utils.deformers.deformerIO.geometrySaveLoad as gIO
from rsTools.utils.deformers.deformerBase import DeformerBase

import rsTools.utils.meshSolvers.UVToUVKDSolver as UVToUVKDSolver

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class UVBlendShape(DeformerBase):
    def __init__(self, nodeName="uvBlendShape#", mesh=None, targetMesh=None, debug=False):
        self._data = None
        self._targetMesh = targetMesh
        super(UVBlendShape, self).__init__(nodeName, mesh)

    ''' VIRTUAL '''

    def buildNode(self):
        if self._mesh:
            if meshUtils.isMesh(self._mesh):
                self._node = cmds.deformer(
                    self._mesh, typ="rig_uvBlendshape", n=self._node)[0]
        else:
            ls = cmds.ls(sl=True)
            if ls:
                if meshUtils.isMesh(ls[0]):
                    self._mesh = str(ls[0])
                    self._node = cmds.deformer(
                        ls[0], typ="rig_uvBlendshape", n=self._node)[0]

        if self._targetMesh:
            print self._targetMesh
            self.connectTargetMesh(self._targetMesh)

    def getBuildString(self, includePath=False):
        if self._node:
            debugLoc = self.getDebugLocator()
            importPath = "from rsTools.utils.deformers.uvBlendshape import UVBlendShape \n"

            bString = 'node = UVBlendShape("{0}","{1}")'.format(
                self._node, str(self._mesh))
            if debugLoc:
                bString = 'node = UVBlendShape("{0}","{1}",debug=True)'.format(
                    self._node, str(self._mesh))

            if includePath:
                bString = importPath + bString

            print bString
            return bString

    def connectTargetMesh(self, targetMesh):
        if meshUtils.isMesh(targetMesh) and self._node:
            self._targetMesh = targetMesh
            cmds.connectAttr(targetMesh+".outMesh",
                             self._node+".targetMesh", force=True)


'''
node = UVBlendShape("uvBlendShape","pPlane1",debug=False)
node.connectTargetMesh("pSphere1")
node.connectTargetMesh("pTorus1")
node.connectTargetMesh("pCylinder1")
'''


# rig_saveLoadWeights("C:\3D\riggingTools\rsTools\_data\_cacheData\envCache.json")
# node.getBuildString()
