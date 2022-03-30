import maya.cmds as cmds
import rsTools.utils.openMaya.transform as transform
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.omWrappers as omUtils


class TwistChain(object):
    def __init__(self, nodeName=None, startTransform=None, endTransform=None, numJoints=5):
        self._startTransform = startTransform
        self._endTransform = endTransform
        self._jointCount = numJoints

        self._name = sUtils.getBase(nodeName)
        self._node = nodeName
        self._twistJoints = []
        self._startOffsetGroup = None
        self._endOffsetGroup = None
        self._startLocator = None
        self._endLocator = None

        self._topNode = None
        self._globalTopNode = tUtils.transformCreate(
            "", "twistChain", parent="rig_GRP")
        cmds.setAttr(self._globalTopNode+".it", 0)

        if not cmds.objExists(self._node):
            self._buildDriverGroups()
            self._buildNode()

        else:
            self._populateData()

    def _buildDriverGroups(self):

        self._side = sUtils.getSide(self._startTransform)
        self._topNode = tUtils.transformCreate(
            self._side, self._name+"TwistRig", parent=self._globalTopNode)

        self._locatorGroup = tUtils.transformCreate(
            self._side, self._name+"TwistLocator", parent=self._topNode)
        self._jointGroup = tUtils.transformCreate(
            self._side, self._name+"TwistJoint", parent=self._topNode)

        self._startOffsetGroup = tUtils.transformCreate(
            self._side, self._name+"TwistStartOffset", parent=self._locatorGroup, transformMatch=self._startTransform)
        self._endOffsetGroup = tUtils.transformCreate(
            self._side, self._name+"TwistEndOffset", parent=self._locatorGroup, transformMatch=self._endTransform)

        startMat = omUtils.getMatrix(self._startTransform)
        mUtils.matchTransformToMatrix(
            self._startOffsetGroup, startMat, t=False)
        mUtils.matchTransformToMatrix(self._endOffsetGroup, startMat, t=False)

        self._startLocator = tUtils.transformCreate(
            self._side, self._name+"TwistStart", "LOC", parent=self._startOffsetGroup, transformMatch=self._startOffsetGroup)
        self._endLocator = tUtils.transformCreate(
            self._side, self._name+"TwistEnd", "LOC", parent=self._endOffsetGroup, transformMatch=self._endOffsetGroup)

        tUtils.setColorIndex(self._startLocator, 17)
        tUtils.setColorIndex(self._endLocator, 17)
        startShape = cmds.listRelatives(self._startLocator, s=True)[0]
        endShape = cmds.listRelatives(self._endLocator, s=True)[0]

        cmds.setAttr(startShape+".localScaleX", 0.4)
        cmds.setAttr(startShape+".localScaleY", 0.4)
        cmds.setAttr(startShape+".localScaleZ", 0.4)
        cmds.setAttr(endShape+".localScaleX", 0.4)
        cmds.setAttr(endShape+".localScaleY", 0.4)
        cmds.setAttr(endShape+".localScaleZ", 0.4)

        cmds.parentConstraint(self._startTransform, self._startLocator, mo=1)
        cmds.parentConstraint(self._endTransform, self._endLocator, mo=1)

    def _buildNode(self):
        self._node = cmds.createNode("rig_twistChain", name=self._node)
        attr = tUtils.attrAdd(self._topNode, "reverse",
                              minVal=0.0, maxVal=1.0, typ="short")
        cmds.connectAttr(attr, self._node+".reverse")

        cmds.connectAttr(self._startLocator +
                         ".worldMatrix[0]", self._node+".inMatrix")
        cmds.connectAttr(self._endLocator +
                         ".worldMatrix[0]", self._node+".inEndMatrix")

        for i in range(self._jointCount):
            self._twistJoints.append(self.addJoint())

    def addJoint(self):
        index = len(self._twistJoints)
        alpha = sUtils.alpha(index).capitalize()
        joint = tUtils.transformCreate(
            self._side, self._name+"TwistJ"+alpha, "JNT", parent=self._jointGroup)

        cmds.connectAttr(
            self._node+".outTranslate[{0}]".format(str(index)), joint+".translate")
        cmds.connectAttr(
            self._node+".outRotate[{0}]".format(str(index)), joint+".rotate")
        tUtils.setColorIndex(joint, 13)
        return joint

    def connectToWorldScale(self):
        topNode = topUtils.getTopNodes(assetType="rigBound")
        if topNode:
            globalControl = tUtils.findObjectsUnderNode(
                topNode, "transform", "global_CTRL")
            if globalControl:
                for j in self._twistJoints:
                    cmds.connectAttr(globalControl[0]+".sx", j+".sx")
                    cmds.connectAttr(globalControl[0]+".sy", j+".sy")
                    cmds.connectAttr(globalControl[0]+".sz", j+".sz")

    def _populateData():
        pass
