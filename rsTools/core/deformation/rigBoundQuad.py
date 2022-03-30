import maya.cmds as cmds
import logging
import os

import rsTools.utils.data.osUtils as osUtils
import rsTools.utils.data.string as sUtils

from rsTools.core.model.modelAsset import ModelAsset
from rsTools.core.deformation.rigBoundBase import RigBoundBase
from rsTools.core.skeleton.skeletonAsset import SkeletonAsset

from rsTools.utils.nodes.interpolationJoint import InterpolationJoint
from rsTools.utils.nodes.interpolatePushJoint import InterpolatePush
from rsTools.utils.nodes.twistChain import TwistChain


class RigBoundQuad(RigBoundBase):
    def __init__(self, topNode=None,
                 project=None,
                 asset=None,
                 rigBoundElement=None,
                 **kwargs):

        # set the default parameters
        self._project = project or osUtils.get_project_show()
        self._asset = asset or osUtils.get_project_show_asset()
        self._rigBoundElement = rigBoundElement or self._asset[4:].lower(
        )+"ALODa"
        self._topNode = topNode or self._project + \
            "_rigBound_"+self._rigBoundElement+"_GRP"

        # build the baseClass init items
        super(RigBoundQuad, self).__init__(
            topNode, project, asset, rigBoundElement)

        self._interpNodes = []
        self._twistNodes = []
        self._stretchyAimNodes = []
        self._volumeJointNodes = []

        self._buildHelperJoints()

    ''' helper joint functions '''

    def _buildHelperJoints(self):
        self._buildDefaultInterpolationJoints()
        self._buildDefaultTwistJoints()
        self._buildDefaultStretchyJoints()
        self._buildDefaultVolumeJoints()

    def _buildDefaultInterpolationJoints(self):
        _defaultInterpJoints = ["legJA", "legJB", "legJC", "toesJA",
                                "toesJB", "armJA", "armJB", "armJC", "handJA", "handJB"]

        for baseName in _defaultInterpJoints:
            for side in ["l", "r"]:
                name = sUtils.nameBuild(side, baseName, "JNT")
                if cmds.objExists(name):
                    parent = cmds.listRelatives(name, p=True)
                    if parent:
                        self._interpNodes.append(InterpolationJoint(
                            sourceTransform=name, parentTransform=parent[0]))

    def _buildDefaultTwistJoints(self):
        __map__ = {"legJA": "legUpper", "legJB": "legLower", "legJC": "legAnkle",
                   "armJA": "armUpper", "armJB": "armLower", "armJC": "armWrist"}
        for k, v in __map__.items():
            for side in ["l", "r"]:
                joint = sUtils.nameBuild(side, k, "JNT")
                eJoint = cmds.listRelatives(joint, c=True)
                if eJoint and cmds.objExists(joint):
                    nodeName = sUtils.nameBuild(side, v, "TwistNode")
                    twistA = TwistChain(nodeName, joint, eJoint[0])

    def _buildDefaultStretchyJoints(self):
        pass

    def _buildDefaultVolumeJoints(self):
        axis = ["x", "-x", "z", "-z"]

        Interp = InterpolatePush(None, "l_legJA_JNT", "pelvisJA_JNT", axis)
        Interp = InterpolatePush(None, "l_legJB_JNT", "l_legJA_JNT", axis)
        Interp = InterpolatePush(None, "l_legJC_JNT", "l_legJB_JNT", axis)

        Interp = InterpolatePush(None, "r_legJA_JNT", "pelvisJA_JNT", axis)
        Interp = InterpolatePush(None, "r_legJB_JNT", "r_legJA_JNT", axis)
        Interp = InterpolatePush(None, "r_legJC_JNT", "r_legJB_JNT", axis)

        Interp = InterpolatePush(None, "pelvisJA_JNT", "spineJB_JNT", axis)
        Interp = InterpolatePush(None, "headJA_JNT", "neckJC_JNT", axis)

        Interp = InterpolatePush(None, "l_armJA_JNT", "l_scapulaJA_JNT", axis)
        Interp = InterpolatePush(None, "l_armJB_JNT", "l_armJA_JNT", axis)
        Interp = InterpolatePush(None, "l_armJC_JNT", "l_armJB_JNT", axis)

        Interp = InterpolatePush(None, "r_armJA_JNT", "r_scapulaJA_JNT", axis)
        Interp = InterpolatePush(None, "r_armJB_JNT", "r_armJA_JNT", axis)
        Interp = InterpolatePush(None, "r_armJC_JNT", "r_armJB_JNT", axis)


''' 
RigBoundQuad()

import maya.api.OpenMaya as om
up = om.MVector(0,1,0)
loc = "locator1"
connected = cmds.ls(sl=True)

sort = connected[0]
for i in range (1,len(connected)):
	vecA = om.MVector(cmds.xform(connected[0],q=True,t=True,ws=True))
	vecB = om.MVector(cmds.xform(connected[i],q=True,t=True,ws=True))
	
	double angle = acos(a.normal()* b.normal());
	MVector cross = a^b;
	if (n*cross < 0)
	{ 
		angle = -angle;
	}

	return angle;
	
import math
findNextSortedVertClockwise(loc,"locator7",up,connected)
def findNextSortedVertClockwise(point,nextConnectedPoint,upVector,allConnected=[]):
	
	# vector from point to next connected point
	vecA = om.MVector(cmds.xform(nextConnectedPoint,q=True,t=True,ws=True)) - om.MVector(cmds.xform(point,q=True,t=True,ws=True))


	bestAngle = 500
	bestPoint = None
	for a in allConnected:
		#vector from point to all connectedPoints
		
		if a not in nextConnectedPoint:
			
			vecB = om.MVector(cmds.xform(a,q=True,t=True,ws=True)) - om.MVector(cmds.xform(point,q=True,t=True,ws=True))
			angle = math.acos(vecA.normal()*vecB.normal())
			cross = vecA^vecB
			if (upVector*cross < 0.0):
				angle = -angle
				continue
				
			if angle > 0.0 and angle<bestAngle:
				bestAngle = angle
				bestPoint = a

	print bestPoint

	
'''
'''

# transformIO.saveSceneTransformDescriptionData()
# connectionIO.saveTransformDependacyDescriptionData()

# transformIO.buildSceneFromDescription()
# connectionIO.loadAllConnectionData()

connectionIO.saveConnectionData("l_legJBLegJA_InterpNode")
wer
connectionIO.loadConnectionData("l_legJBLegJA_InterpNode")

cmds.deformer("pTorus1", typ="rigMultiSolver")
cmds.connectAttr("pTorusShape2.outMesh", "rigMultiSolver1.baseMesh")


cmds.deformer("pCube1", typ="rigMultiSolver")
cmds.connectAttr("pCubeShape2.outMesh", "rigMultiSolver1.baseMesh")


cmds.deformer("pPlane1", typ="rigMultiSolver")
cmds.connectAttr("pPlaneShape2.outMesh", "rigMultiSolver1.baseMesh")


cmds.deformer("pSphere1", typ="rigMultiSolver")
cmds.connectAttr("pSphereShape2.outMesh", "rigMultiSolver1.baseMesh")

cmds.deformer("pCylinder1", typ="rigMultiSolver")
cmds.connectAttr("pCylinderShape2.outMesh", "rigMultiSolver1.baseMesh")


debugLocatorShape = cmds.createNode("rigDebugLocator")
debugLocator = cmds.listRelatives(debugLocatorShape, p=True)[0]
cmds.connectAttr("rigMultiSolver1.debugData",
                 debugLocatorShape+".debugConnect", force=True)
'''