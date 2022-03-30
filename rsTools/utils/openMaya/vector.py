import maya.mel as mm
import maya.cmds as cmds
import maya.api.OpenMaya as om
import math
import rsTools.utils.openMaya.matrix as mUtils


def blend(vectorA, vectorB, param):

    outX = vectorA.x + (vectorB.x - vectorA.x) * param
    outY = vectorA.y + (vectorB.y - vectorA.y) * param
    outZ = vectorA.z + (vectorB.z - vectorA.z) * param

    return om.MVector(outX, outY, outZ)


def vectorMatrixMult(inMat, inVec):

    out = om.MVector()
    xAxis = mUtils.getMatrixRow(0, inMat)
    yAxis = mUtils.getMatrixRow(1, inMat)
    zAxis = mUtils.getMatrixRow(2, inMat)
    t = mUtils.getMatrixRow(3, inMat)

    out.x = inVec.x * xAxis.x + inVec.y * yAxis.x + inVec.z * zAxis.x + t.x
    out.y = inVec.x * xAxis.y + inVec.y * yAxis.y + inVec.z * zAxis.y + t.y
    out.z = inVec.x * xAxis.z + inVec.y * yAxis.z + inVec.z * zAxis.z + t.z

    return out
