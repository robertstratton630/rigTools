import maya.cmds as cmds
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.data.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.transform.joint as joint

__rotDefaults__ = {"x": [0, 0, -90],
                   "-x": [0, 0, 90],
                   "y": [0, 0, 0],
                   "-y": [180, 0, 0],
                   "z": [90, 0, 0],
                   "-z": [-90, 0, 0],
                   }


class InterpolatePush(object):
    def __init__(self, nodeName=None, startTransform=None, parentTransform=None, numJoints=0):

        self._startTransform = startTransform
        self._parentTransform = parentTransform

        self._side = sUtils.getSide(self._startTransform)
        self._base = sUtils.getBase(self._startTransform)
        baseParent = sUtils.capitalize(sUtils.getBase(self._parentTransform))
        self._node = nodeName or sUtils.nameBuild(
            self._side, self._base+baseParent, "InterpPushNode")

        # x,y,z input
        if isinstance(numJoints, list):
            self._jointCount = len(numJoints)
            self._axis = numJoints
        else:
            self._jointCount = numJoints

        self._joints = []
        self._startOffsetGroup = None
        self._endOffsetGroup = None
        self._startLocator = None
        self._endLocator = None

        self._topNode = None
        self._globalTopNode = tUtils.transformCreate(
            "", "interpolatePushRig", parent="rig_GRP")
        cmds.setAttr(self._globalTopNode+".it", 0)

        if not cmds.objExists(self._node):
            self._buildDriverGroups()
            self._buildNode()

            # if you pass in x,y,z ect then build the default axis stuff
            if isinstance(numJoints, list):
                self._setDefaultRotations()

        else:
            self._populateData()

    def _buildDriverGroups(self):
        self._topNode = tUtils.transformCreate(
            self._side, self._base+"interpPushRig", parent=self._globalTopNode)
        self._locatorGroup = tUtils.transformCreate(
            self._side, self._base+"interpPushLocator", parent=self._topNode)
        self._jointGroup = tUtils.transformCreate(
            self._side, self._base+"interpPushJoint", parent=self._topNode)

        self._startOffsetGroup = tUtils.transformCreate(
            self._side, self._base+"interpPushOffset", parent=self._locatorGroup, transformMatch=self._startTransform)
        self._parentOffsetGroup = tUtils.transformCreate(
            self._side, self._base+"interpPushParentOffset", parent=self._locatorGroup, transformMatch=self._parentTransform)

        startMat = omUtils.getMatrix(self._startTransform)
        mUtils.matchTransformToMatrix(
            self._startOffsetGroup, startMat, t=False)
        mUtils.matchTransformToMatrix(
            self._parentOffsetGroup, startMat, t=False)

        self._startLocator = tUtils.transformCreate(
            self._side, self._base+"interpPush", "LOC", parent=self._startOffsetGroup, transformMatch=self._startOffsetGroup)
        self._parentLocator = tUtils.transformCreate(
            self._side, self._base+"interpPushParent", "LOC", parent=self._parentOffsetGroup, transformMatch=self._parentOffsetGroup)

        tUtils.setColorIndex(self._startLocator, 17)
        tUtils.setColorIndex(self._parentLocator, 17)
        startShape = cmds.listRelatives(self._startLocator, s=True)[0]
        endShape = cmds.listRelatives(self._parentLocator, s=True)[0]
        cmds.setAttr(startShape+".localScaleX", 0.4)
        cmds.setAttr(startShape+".localScaleY", 0.4)
        cmds.setAttr(startShape+".localScaleZ", 0.4)
        cmds.setAttr(endShape+".localScaleX", 0.4)
        cmds.setAttr(endShape+".localScaleY", 0.4)
        cmds.setAttr(endShape+".localScaleZ", 0.4)

        cmds.parentConstraint(self._startTransform, self._startLocator, mo=1)
        cmds.parentConstraint(self._parentTransform, self._parentLocator, mo=1)

    def _buildNode(self):
        self._node = cmds.createNode(
            "rig_volumeInterpolateNew", name=self._node)

        cmds.connectAttr(self._startLocator +
                         ".worldMatrix[0]", self._node+".inMatrix")
        cmds.connectAttr(self._parentLocator +
                         ".worldMatrix[0]", self._node+".inBlendMatrix")
        cmds.connectAttr(self._parentLocator +
                         ".worldMatrix[0]", self._node+".inReferenceMatrix")

        # extra attributes
        worldScale = tUtils.attrAdd(self._topNode, "worldScale", 1)
        blend = tUtils.attrAdd(self._topNode, "blend", 0.5, minVal=0, maxVal=1)
        blendTangent = tUtils.attrAdd(self._topNode, "blendInterpTangent", 1.5)
        cmds.connectAttr(worldScale, self._node+".worldScale")
        cmds.connectAttr(blend, self._node+".inBlendAmount")
        cmds.connectAttr(blendTangent, self._node+".inBlendTangent")

        for i in range(self._jointCount):
            self._joints.append(self.addJoint())

    def addJoint(self):
        index = len(self._joints)
        alpha = sUtils.alpha(index).capitalize()
        joint = tUtils.transformCreate(
            self._side, self._base+"PushJ"+alpha, "JNT", parent=self._jointGroup)
        jointEnd = tUtils.transformCreate(
            self._side, self._base+"PushJ"+alpha+"End", "JNT", parent=joint)
        cmds.setAttr(jointEnd+".ty", 0.25)
        cmds.setAttr(joint+".radius", 0)

        cmds.connectAttr(
            self._node+".outTranslate[{0}]".format(str(index)), joint+".translate")
        cmds.connectAttr(
            self._node+".outRotate[{0}]".format(str(index)), joint+".rotate")
        cmds.connectAttr(
            self._node+".outScale[{0}]".format(str(index)), joint+".scale")

        # add all the attributes to the endJoint
        # pre settings
        tUtils.addSeparator(jointEnd, "preSettings")
        prePush = tUtils.attrAdd(jointEnd, "prePush", 0)
        offsetX = tUtils.attrAdd(jointEnd, "offsetX", 0)
        offsetY = tUtils.attrAdd(jointEnd, "offsetY", 0)
        offsetZ = tUtils.attrAdd(jointEnd, "offsetZ", 0)

        cmds.connectAttr(prePush, self._node +
                         ".prePushAmount[{0}]".format(index))
        cmds.connectAttr(offsetX, self._node +
                         ".inOffsetRotateX[{0}]".format(index))
        cmds.connectAttr(offsetY, self._node +
                         ".inOffsetRotateY[{0}]".format(index))
        cmds.connectAttr(offsetZ, self._node +
                         ".inOffsetRotateZ[{0}]".format(index))

        # x attributes
        tUtils.addSeparator(jointEnd, "__angleX")
        xPush = tUtils.attrAdd(jointEnd, "xPush", 0)
        xScaleX = tUtils.attrAdd(jointEnd, "xScaleOffsetX", 0)
        xScaleY = tUtils.attrAdd(jointEnd, "xScaleOffsetY", 0)
        xScaleZ = tUtils.attrAdd(jointEnd, "xScaleOffsetZ", 0)

        cmds.connectAttr(xPush, self._node +
                         ".inPushAmountDeltaX[{0}]".format(index))
        cmds.connectAttr(xScaleX, self._node +
                         ".inScaleXDeltaX[{0}]".format(index))
        cmds.connectAttr(xScaleY, self._node +
                         ".inScaleYDeltaX[{0}]".format(index))
        cmds.connectAttr(xScaleZ, self._node +
                         ".inScaleZDeltaX[{0}]".format(index))

        # neg x
        tUtils.addSeparator(jointEnd, "__angleNegX")
        xNegPush = tUtils.attrAdd(jointEnd, "xNegPush", 0)
        xNegScaleX = tUtils.attrAdd(jointEnd, "xNegScaleOffsetX", 0)
        xNegScaleY = tUtils.attrAdd(jointEnd, "xNegScaleOffsetY", 0)
        xNegScaleZ = tUtils.attrAdd(jointEnd, "xNegScaleOffsetZ", 0)

        cmds.connectAttr(xNegPush, self._node +
                         ".inPushAmountDeltaNegX[{0}]".format(index))
        cmds.connectAttr(xNegScaleX, self._node +
                         ".inScaleXDeltaXNeg[{0}]".format(index))
        cmds.connectAttr(xNegScaleY, self._node +
                         ".inScaleYDeltaXNeg[{0}]".format(index))
        cmds.connectAttr(xNegScaleZ, self._node +
                         ".inScaleZDeltaXNeg[{0}]".format(index))

        # y axis
        tUtils.addSeparator(jointEnd, "__angleY")
        yPush = tUtils.attrAdd(jointEnd, "yPush", 0)
        yScaleX = tUtils.attrAdd(jointEnd, "yScaleOffsetX", 0)
        yScaleY = tUtils.attrAdd(jointEnd, "yScaleOffsetY", 0)
        yScaleZ = tUtils.attrAdd(jointEnd, "yScaleOffsetZ", 0)

        cmds.connectAttr(yPush, self._node +
                         ".inPushAmountDeltaY[{0}]".format(index))
        cmds.connectAttr(yScaleX, self._node +
                         ".inScaleXDeltaY[{0}]".format(index))
        cmds.connectAttr(yScaleY, self._node +
                         ".inScaleYDeltaY[{0}]".format(index))
        cmds.connectAttr(yScaleZ, self._node +
                         ".inScaleZDeltaY[{0}]".format(index))

        # neg y
        tUtils.addSeparator(jointEnd, "__angleNegY")
        yNegPush = tUtils.attrAdd(jointEnd, "yNegPush", 0)
        yNegScaleX = tUtils.attrAdd(jointEnd, "yNegScaleOffsetX", 0)
        yNegScaleY = tUtils.attrAdd(jointEnd, "yNegScaleOffsetY", 0)
        yNegScaleZ = tUtils.attrAdd(jointEnd, "yNegScaleOffsetZ", 0)

        cmds.connectAttr(yNegPush, self._node +
                         ".inPushAmountDeltaNegY[{0}]".format(index))
        cmds.connectAttr(yNegScaleX, self._node +
                         ".inScaleXDeltaYNeg[{0}]".format(index))
        cmds.connectAttr(yNegScaleY, self._node +
                         ".inScaleYDeltaYNeg[{0}]".format(index))
        cmds.connectAttr(yNegScaleZ, self._node +
                         ".inScaleZDeltaYNeg[{0}]".format(index))

        # z axis
        tUtils.addSeparator(jointEnd, "__angleZ")
        zPush = tUtils.attrAdd(jointEnd, "zPush", 0)
        zScaleX = tUtils.attrAdd(jointEnd, "zScaleOffsetX", 0)
        zScaleY = tUtils.attrAdd(jointEnd, "zScaleOffsetY", 0)
        zScaleZ = tUtils.attrAdd(jointEnd, "zScaleOffsetZ", 0)

        cmds.connectAttr(zPush, self._node +
                         ".inPushAmountDeltaZ[{0}]".format(index))
        cmds.connectAttr(zScaleX, self._node +
                         ".inScaleXDeltaZ[{0}]".format(index))
        cmds.connectAttr(zScaleY, self._node +
                         ".inScaleYDeltaZ[{0}]".format(index))
        cmds.connectAttr(zScaleZ, self._node +
                         ".inScaleZDeltaZ[{0}]".format(index))

        # z minus axis
        tUtils.addSeparator(jointEnd, "__angleNegZ")
        zNegPush = tUtils.attrAdd(jointEnd, "zNegPush", 0)
        zNegScaleX = tUtils.attrAdd(jointEnd, "zNegScaleOffsetX", 0)
        zNegScaleY = tUtils.attrAdd(jointEnd, "zNegScaleOffsetY", 0)
        zNegScaleZ = tUtils.attrAdd(jointEnd, "zNegScaleOffsetZ", 0)

        cmds.connectAttr(zNegPush, self._node +
                         ".inPushAmountDeltaNegZ[{0}]".format(index))
        cmds.connectAttr(zNegScaleX, self._node +
                         ".inScaleXDeltaZNeg[{0}]".format(index))
        cmds.connectAttr(zNegScaleY, self._node +
                         ".inScaleYDeltaZNeg[{0}]".format(index))
        cmds.connectAttr(zNegScaleZ, self._node +
                         ".inScaleZDeltaZNeg[{0}]".format(index))

        if self._side == "l":
            tUtils.setColorIndex(joint, 18)
            tUtils.setColorIndex(jointEnd, 18)

        elif self._side == "r":
            tUtils.setColorIndex(joint, 18)
            tUtils.setColorIndex(jointEnd, 20)
        else:
            tUtils.setColorIndex(joint, 18)
            tUtils.setColorIndex(jointEnd, 21)

        cmds.setAttr(joint+".overrideDisplayType", 1)
        return jointEnd

    def _setDefaultRotations(self):
        for i, axis in enumerate(self._axis):
            axisData = __rotDefaults__[axis]
            offsetX = axisData[0]
            offsetY = axisData[1]
            offsetZ = axisData[2]
            cmds.setAttr(self._joints[i]+".offsetX", offsetX)
            cmds.setAttr(self._joints[i]+".offsetY", offsetY)
            cmds.setAttr(self._joints[i]+".offsetZ", offsetZ)

            if axis == "x" or axis == "-x":
                tUtils.setColorIndex(self._joints[i], 13)
            elif axis == "y" or axis == "-y":
                tUtils.setColorIndex(self._joints[i], 14)
            elif axis == "z" or axis == "-z":
                tUtils.setColorIndex(self._joints[i], 6)

    def getJoints(self):
        return self._joints

    def getStartOffsetGroup(self):
        return self._startOffsetGroup

    def getEndOffsetGroup(self):
        return self._endOffsetGroup

    def getStartLocator(self):
        return self._startLocator

    def getEndLocator(self):
        return self._endLocator

    def getTopNode(self):
        return self._topNode

    def _populateData(self):
        joints = cmds.listConnections(self._node, s=1, d=0)
        self._joints = arrayUtils.sort(
            list(set([j for j in joints if jUitls.isJoint(j)])))

        self._startLocator = cmds.listConnections(
            self._node+".inMatrix", s=1, d=0)[0]
        self._endLocator = cmds.listConnections(
            self._node+".inBlendMatrix", s=1, d=0)[0]

        self._startOffsetGroup = cmds.listRelatives(
            self._startLocator, p=True)[0]
        self._endOffsetGroup = cmds.listRelatives(self._endLocator, p=True)[0]
