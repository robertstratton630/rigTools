import maya.OpenMaya as om
import maya.cmds as cmds

import rsTools.utils.data.string as sUtils
import rsTools.utils.data.IO.deformerSaveLoad as dIO
import rsTools.utils.data.geometrySaveLoad as gIO

from rsTools.utils.deformers.deformerBase import DeformerBase


class Skincluster(DeformerBase):
    def __init__(self, mesh=None, joints=[], debug=False):
        mesh = mesh or [str(m) for m in cmds.ls(
            sl=True) if meshUtils.isMesh(m)][0]
        nodeName = mesh+"_skinCluster"
        self._data = None
        self._joints = None or joints

        # lets do and check and rename if skincluster exists on mesh
        sk = skinUtils.findRelatedSkinCluster(mesh)
        if sk:
            cmds.rename(sk, nodeName)
            self._joints = skinUtils.getSkinClusterInfluences(nodeName)

        super(Skincluster, self).__init__(nodeName, mesh)

    ''' VIRTUAL '''

    def buildNode(self):
        meshExists = False
        if self._mesh:
            if meshUtils.isMesh(self._mesh):
                meshExists = True

        if meshExists:
            if self._joints:
                self._node = self._buildSkinCluster(self._mesh, self._joints)

        else:
            ls = cmds.ls(sl=True)
            if ls:
                joints = []
                mesh = None

                for item in ls:
                    if meshUtils.isMesh(item):
                        mesh = item
                    if jUtils.isJoint(item):
                        joints.append(item)

                if mesh and joints:
                    self._mesh = mesh
                    self._joints = joints
                    self._node = self._buildSkinCluster(
                        self._mesh, self._joints)
                else:
                    _logger.warning(
                        "Cannot create skincluster, pelase make sure you have joints")

    def _buildSkinCluster(self, mesh, jntList):
        for i, jnt in enumerate(jntList):
            if not cmds.objExists(jnt):
                _logger.warning(
                    'Joint "'+jnt+'" does not exist, Creating Joint !')
                jntList[i] = cmds.createNode("joint", name=jnt)

        if cmds.objExists(self._node):
            cmds.delete(self._node)

        skinCluster = cmds.skinCluster(
            jntList, mesh, toSelectedBones=True, rui=False, n=self._node)[0]
        return skinCluster

    def loadData(self, version=-1, weights=True, uvMode=False, attributes=True, verbose=True):
        if weights:
            # load deformer attributes and info
            _data = dIO.loadDeformerInformation(
                self._node, version, nodeType="skinCluster")

            self._joints = _data.get("joints")

            self._node = self._buildSkinCluster(self._mesh, self._joints)

            _attributes = _data.get("attributes")
            # load attributes
            if attributes:
                attributes = _data.get("attributes")
                for a in attributes:
                    cmds.setAttr(a[0], a[1])

            dIO.loadDeformerWeightsCpp(
                self._node, version=version, doUV=uvMode, verbose=verbose)

    '''PUBLIC'''

    def reset(self):
        if self._node:
            self._node = skinUtils.reset(self._mesh)

    def getNode(self):
        return self._node

    def copy(self, otherMesh, uvMode=False):
        if isinstance(otherMesh, unicode):
            otherMesh = str(otherMesh)
        if isinstance(otherMesh, str):
            try:
                print self._joints
                otherskin = Skincluster(otherMesh, self._joints)

                if uvMode:
                    cmds.copySkinWeights(self._mesh, otherMesh, noMirror=True, surfaceAssociation="closestPoint", uvSpace=[
                                         "map1", "map1"], influenceAssociation="oneToOne", normalize=True)
                else:
                    cmds.copySkinWeights(self._mesh, otherMesh, noMirror=True,
                                         surfaceAssociation="closestPoint", influenceAssociation="oneToOne", normalize=True)
                return otherskin
            except:
                return None

        else:
            allSkins = []
            for i in node:
                items = self.copy(i, uvMode)
                if items:
                    allSkins += items
            return allSkins


skinaa = Skincluster("pSphere1")
# skinaa.saveData(geometry=True)
newSkin = skinaa.copy("pSphere2", uvMode=True)


skinaa.loadData(uvMode=True)
# skinaa.loadData()
