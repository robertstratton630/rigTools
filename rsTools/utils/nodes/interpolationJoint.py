import maya.cmds as cmds
import rsTools.utils.openMaya.transform as transform
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.scene.topNode as topUtils


class InterpolationJoint(object):
    def __init__(self, nodeName=None, sourceTransform=None, parentTransform=None):
        self._source = sourceTransform
        self._parent = parentTransform
        self._joint = None

        # get the nodeName
        side = sUtils.getSide(self._source)
        base = sUtils.getBase(self._source)
        baseParent = sUtils.capitalize(sUtils.getBase(self._parent))
        self._node = nodeName or sUtils.nameBuild(
            side, base+baseParent, "InterpNode")

        self._topNode = tUtils.transformCreate(
            "", "interpolationJoint", parent="rig_GRP")
        cmds.setAttr(self._topNode+".it", 0)

        if not cmds.objExists(self._node):
            self.buildNode()
            self.connectSource(self._source)
            self.setBaseMatrix(self._source)

            self.connectParent(self._parent)
            self.setBaseParentMatrix(self._parent)
            self.connectToWorldScale()

        else:
            self._populateData()

    def buildNode(self):
        side = sUtils.getSide(self._source)
        base = sUtils.getBase(self._source)
        baseParent = sUtils.capitalize(sUtils.getBase(self._parent))

        self._node = cmds.createNode(
            "rig_interpolateTransform", name=self._node)

        self._joint = tUtils.transformCreate(
            side, base+"Interp", "JNT", self._topNode)
        tUtils.setColorIndex(self._joint, 31)
        cmds.connectAttr(self._node+".outTranslate", self._joint+".translate")
        cmds.connectAttr(self._node+".outRotate", self._joint+".rotate")

        attr = tUtils.attrAdd(self._joint, "blend",
                              minVal=0.0, maxVal=1.0, defaultVal=0.5)
        cmds.connectAttr(attr, self._node+".interpolateValue")
        cmds.setAttr(self._joint+".radius", 2.0)

    def connectSource(self, _transform):
        if self._node:
            if transform.isTransform(_transform):
                cmds.connectAttr(
                    _transform+".worldMatrix[0]", self._node+".inMatrix")
                self._source = _transform

    def connectParent(self, _transform):
        if self._node:
            if transform.isTransform(_transform):
                cmds.connectAttr(
                    _transform+".worldMatrix[0]", self._node+".inParentMatrix")
                self._target = _transform

    def setBaseMatrix(self, _transform):
        if self._node:
            if transform.isTransform(_transform):
                mat = omUtils.getMatrix(_transform)
                matList = mUtils.asList(mat)
                cmds.setAttr(self._node+".basePoseMatrix",
                             matList, type="matrix")

    def setBaseParentMatrix(self, _transform):
        if self._node:
            if transform.isTransform(_transform):

                mat = omUtils.getMatrix(_transform)
                matList = mUtils.asList(mat)
                cmds.setAttr(self._node+".basePoseParentMatrix",
                             matList, type="matrix")

    def connectToWorldScale(self):
        topNode = topUtils.getTopNodes(assetType="rigBound")
        if topNode:
            globalControl = tUtils.findObjectsUnderNode(
                topNode, "transform", "global_CTRL")
            if globalControl:
                cmds.connectAttr(globalControl[0]+".sx", self._joint+".sx")
                cmds.connectAttr(globalControl[0]+".sy", self._joint+".sy")
                cmds.connectAttr(globalControl[0]+".sz", self._joint+".sz")

    def getSourceTransform(self):
        pass

    def getParentTransform(self):
        pass

    def _populateData(self):
        pass
