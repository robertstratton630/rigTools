import maya.OpenMaya as om
import maya.cmds as cmds

import rsTools.utils.data.string as sUtils
import rsTools.utils.data.IO.deformerSaveLoad as dIO
import rsTools.utils.data.geometrySaveLoad as gIO

from rsTools.utils.deformers.deformerBase import DeformerBase


class NormalPush(DeformerBase):
    def __init__(self, nodeName="d_normalPush_arm", mesh=None, debug=False):
        super(NormalPush, self).__init__(nodeName, mesh)
        self._data = None

    ''' VIRTUAL '''

    def buildNode(self):
        if self._mesh:
            if meshUtils.isMesh(self._mesh):
                self._node = cmds.deformer(
                    self._mesh, typ="rig_normalPush", n=self._node)[0]
        else:
            ls = cmds.ls(sl=True)
            if ls:
                if meshUtils.isMesh(ls[0]):
                    self._mesh = str(ls[0])
                    self._node = cmds.deformer(
                        ls[0], typ="rig_normalPush", n=self._node)[0]

    def getBuildString(self, includePath=False, rawPath=False, printResult=True):
        if self._node:
            debugLoc = self.getDebugLocator()
            importPath = "from rsTools.utils.deformers.normalPush import NormalPush \n"

            bString = 'node = NormalPush("{0}","{1}")'.format(
                self._node, str(self._mesh))
            if debugLoc:
                bString = 'node = NormalPush("{0}","{1}",debug=True)'.format(
                    self._node, str(self._mesh))

            if includePath:
                bString = importPath + bString

            if rawPath:
                bString = 'NormalPush("{0}","{1}")'.format(
                    self._node, str(self._mesh))

            print bString
            return bString
