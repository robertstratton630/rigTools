import maya.cmds as cmds
import maya.OpenMaya as om
import rsTools.utils.openMaya.transform as transform
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.shaders as shader


class PoseReader(object):
    def __init__(self, nodeName="l_armJA_PoseReader", transform=None, targetTransforms=None, mode=0):

        self._node = nodeName
        self._side = sUtils.getSide(nodeName)
        self._base = sUtils.getBase(nodeName)

        self._poseLocator = None
        self._poseBaseLocator = None
        self._poseTargetLocators = []

        # check/create the default topNodes
        self._rigTopNode = tUtils.transformCreate(
            "", "poseReader", parent="rig_GRP")
        self._poseData = tUtils.transformCreate(
            "", "poseReaderInfo", "LOC", parent=self._rigTopNode)

        # create the node
        if cmds.objExists(self._node):
            self._populateData()
        else:
            self._buildNode()
            self.connectTransform(transform)

    def _populateData(self):
        self._poseLocator = str(cmds.listConnections(
            "{0}.poseMatrix".format(self._node), s=1, d=0)[0])
        self._poseBaseLocator = cmds.listConnections(
            "{0}.poseBaseMatrix".format(self._node), s=1, d=0)[0]
        self._poseTargetLocators = [str(i) for i in cmds.listConnections(
            "{0}.poseTargetMatrix".format(self._node), s=1, d=0)]

    def getPoseLocator(self):
        return self._poseLocator

    def getPoseBaseLocator(self):
        return self._poseBaseLocator

    def getPoseTargetLocators(self):
        return self._poseTargetLocators

    ''' PRIVATE '''

    def _buildNode(self):
        self._node = cmds.createNode("rig_poseReader", n=self._node)

    ''' PUBLIC '''

    def connectTransform(self, _transform, poseParent=None):
        if self._node and cmds.objExists(_transform) and transform.isTransform(_transform):
            if not poseParent:
                try:
                    joint = cmds.listRelatives(_transform, p=True)[0]
                    poseParent = cmds.listRelatives(joint, p=True)[0]
                except:
                    poseParent = _transform

            side = sUtils.getSide(_transform)
            base = sUtils.getBase(_transform)
            self._poseLocator = tUtils.transformCreate(
                side, base+"PoseDriver", "LOC", parent=_transform, transformMatch=_transform)
            self._poseBaseLocator = tUtils.transformCreate(
                side, base+"PoseDriverBase", "LOC", parent=poseParent, transformMatch=_transform)
            cmds.setAttr(self._poseLocator+".localScaleX", 0)
            cmds.setAttr(self._poseLocator+".localScaleY", 0.2)
            cmds.setAttr(self._poseLocator+".localScaleZ", 0.2)
            cmds.setAttr(self._poseBaseLocator+".localScaleX", 0)
            cmds.setAttr(self._poseBaseLocator+".localScaleY", 0.2)
            cmds.setAttr(self._poseBaseLocator+".localScaleZ", 0.2)
            cmds.connectAttr(
                self._poseLocator+".worldMatrix[0]", self._node+".poseMatrix", f=True)
            cmds.connectAttr(
                self._poseBaseLocator+".worldMatrix[0]", self._node+".poseBaseMatrix", f=True)

    def addDebugCube(self, posedLocator):
        pCube = cmds.polyCube(h=0.1, w=0.1, d=0.1, ch=0)[0]
        s = shader.applyShader(pCube, posedLocator+"_SDRH", color=[0, 0, 0])

        cmds.connectAttr(posedLocator+".output", s+".colorR")
        cmds.connectAttr(posedLocator+".output", s+".colorG")
        cmds.connectAttr(posedLocator+".output", s+".colorB")

        mat = omUtils.getMatrix(posedLocator)
        mUtils.matchTransformToMatrix(pCube, mat)

        pCube = cmds.parent(pCube, posedLocator)[0]
        cmds.setAttr(pCube+".translateY", -1)

    def getTargetIndex(self, posedLocator):
        index = -1
        try:
            index = self._poseTargetLocators.index(posedLocator)
        except:
            pass
        return index

    def addPose(self, poseName, rx=0, ry=0, rz=0, poseParent=None, twistMode=0, debug=False):
        # make sure you are passing a str
        if isinstance(poseName, unicode):
            poseName = str(poseName)
        if not isinstance(poseName, str):
            return False

        print "debugA"
        print self._poseLocator

        # check if user has input relative rotations
        useCurrentPose = True
        if rx or ry or rz:
            useCurrentPose = False

        # try find to parent
        if not poseParent:
            joint = cmds.listRelatives(self._poseLocator, p=True)[0]
            poseParent = cmds.listRelatives(joint, p=True)[0]

        side = sUtils.getSide(self._poseLocator)
        targetLOC = None
        # create locator
        if useCurrentPose:
            targetLOC = tUtils.transformCreate(
                side, poseName+"Pose", "LOC", parent=poseParent, transformMatch=self._poseLocator)
            self._poseTargetLocators.append(str(targetLOC))
        else:
            targetLOC = tUtils.transformCreate(
                side, poseName+"Pose", "LOC", parent=poseParent, transformMatch=self._poseLocator)

            # set rotations to zero
            j = cmds.listRelatives(self._poseLocator, p=True)[0]
            jMat = omUtils.getMatrix(j)
            cmds.setAttr(j+".rx", 0)
            cmds.setAttr(j+".ry", 0)
            cmds.setAttr(j+".rz", 0)

            mat = omUtils.getMatrix(self._poseLocator)
            mat = mUtils.rotateMatrixBy(mat, [rx, ry, rz])
            mUtils.matchTransformToMatrix(targetLOC, mat)

            # resnap back to current pose
            mUtils.matchTransformToMatrix(j, jMat)
            self._poseTargetLocators.append(str(targetLOC))

        # connect loc up to node
        inputs = cmds.listConnections(self._node+".poseTargetMatrix", s=1, d=0)
        index = 0
        if inputs:
            index = len(inputs)
        cmds.connectAttr(
            targetLOC+".worldMatrix[0]", self._node+".poseTargetMatrix[{0}]".format(index))

        # add twist settings
        tUtils.addSeparator(targetLOC, "AngleMode")
        twistAttr = tUtils.attrAdd(targetLOC, "angleInterpMode", [
                                   "angle", "twist", "angleTwistBlend"], typ="enum")
        cmds.setAttr(twistAttr, twistMode)
        cmds.connectAttr(twistAttr, self._node+".twistMode[{0}]".format(index))

        attrRotate = tUtils.attrAdd(targetLOC, "angleMode", [
                                    "angle", "signedAngle"], typ="enum")
        cmds.connectAttr(attrRotate, self._node +
                         ".angleMode[{0}]".format(index))

        tUtils.addSeparator(targetLOC, "RBFMode")
        rbfAttr = tUtils.attrAdd(targetLOC, "RBFInterpMode", [
                                 "angle", "twist", "angleTwistBlend"], typ="enum")

        # create attribute on main data Loc
        attrA = tUtils.attrAdd(self._poseData, poseName+"output", typ="float")
        cmds.connectAttr(
            self._node+".outValue[{0}]".format(index), attrA, force=True)

        # create attribute on poseLoc
        tUtils.addSeparator(targetLOC, "OutputValue")
        attrB = tUtils.attrAdd(targetLOC, "output", typ="float")
        cmds.connectAttr(
            self._node+".outValue[{0}]".format(index), attrB, force=True)

        # JUST FOR DISPLAY
        cmds.connectAttr(
            self._node+".outValue[{0}]".format(index), self._poseData+".tx", force=True)

        if debug:
            self.addDebugCube(targetLOC)


pdata = PoseReader("l_armJA_PoseReader", "l_legJB_JNT")
pdata.addPose("f", debug=True)


mat = omUtils.getMatrix("l_legJBPoseDriverBase_LOC")
translate = mUtils.getMatrixRow(3, mat)
vec = om.MVector(0, 1, 0)
localOffset = vec * mat
translate = translate + localOffset
print translate.x, translate.y, translate.z

'''
MMatrix relativeMat = readerMat * driverMat.inverse();

print vec.x,vec.y,vec.z



MVector translate = rig::getMatrixRow(3, outMatrix);
                    MVector localOffset = prePushVector * outMatrix;
                    translate = translate + localOffset;
                    '''
