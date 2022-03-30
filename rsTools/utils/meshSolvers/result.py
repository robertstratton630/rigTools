import maya.api.OpenMaya as om
from rsTools.utils.openMaya.vec2 import Vec2


class ClosestPointResult(object):
    def __init__(self, faceID=0, faceTriangleID=0, triPolyVertexIDs=[0, 0, 0], point=om.MVector(0, 0, 0), normal=om.MVector(0, 0, 0), baryWeights=(0, 0, 0)):
        self._faceID = faceID
        self._faceTriangleID = faceTriangleID
        self._triPolyVertexIDs = triPolyVertexIDs
        self._point = point
        self._normal = normal
        self._baryWeights = baryWeights

    def getFaceID(self):
        return self._faceID

    def getFaceTriangleID(self):
        return self._faceTriangleID

    def getPoint(self):
        return self._point

    def getNormal(self):
        return self._normal

    def getBaryWeights(self):
        return self._baryWeights

    def getTriPolyVertexIDs(self):
        return self._triPolyVertexIDs


class ClosestUVResult(object):

    def __init__(self, uvA=Vec2(), uvB=Vec2(), uvC=Vec2(), uvAIndex=0, uvBIndex=0, uvCIndex=0, baryWeights=(0, 0, 0)):

        self._uvA = uvA
        self._uvB = uvB
        self._uvC = uvC

        self._uvAIndex = uvAIndex
        self._uvBIndex = uvBIndex
        self._uvCIndex = uvCIndex

        self._bary = baryWeights

    def getUVA(self):
        return self._uvA

    def getUVB(self):
        return self._uvB

    def getUVC(self):
        return self._uvC

    def getUVAIndex(self):
        return self._uvAIndex

    def getUVBIndex(self):
        return self._uvBIndex

    def getUVCIndex(self):
        return self._uvCIndex

    def getBaryWeights(self):
        return self._bary
