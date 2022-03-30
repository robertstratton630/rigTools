import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pm

from rsTools.utils.data import string


def isNurbsCurve(obj):
    tempType = cmds.objectType(obj)
    shp = cmds.listRelatives(obj, s=True)
    if shp:
        tempType = cmds.objectType(shp[0])

    if tempType == "nurbsCurve":
        return True

    return False


def getNurbsCurveDataRaw(curve):

    curveShapes = curve.getShapes()

    outDict = {}
    for i, curveShape in enumerate(curveShapes):
        knots = curveShape.getKnots()
        cvs = curveShape.getCVs(space="world")
        spans = curveShape.spans.get()
        degree = curveShape.degree()
        form = curveShape.form()
        periodic = True if form.key == "periodic" else False

        mDict = dict(cvs=cvs,
                     knots=knots,
                     spans=spans,
                     degree=degree,
                     periodic=periodic)

        outDict["shapeNode"+str(i)] = mDict

    return outDict


def getNurbsCurveDataClean(curve):

    name = curve.name()
    curveShapes = curve.getShapes()

    outDict = {}
    for i, curveShape in enumerate(curveShapes):
        knots = curveShape.getKnots()
        cvs = curveShape.getCVs(space="world")
        spans = curveShape.spans.get()
        degree = curveShape.degree()
        form = curveShape.form()
        periodic = True if form.key == "periodic" else False
        # clean up CV so json works
        cleanCVs = [tuple(cv) for cv in cvs]

        mDict = dict(cvs=cleanCVs,
                     knots=knots,
                     spans=spans,
                     degree=degree,
                     periodic=periodic)

        outDict["shapeNode"+str(i)] = mDict

    return outDict


def combineShapes(curves, name):
    cmds.makeIdentity(curves, apply=True, t=1, r=1, s=1)
    if isinstance(curves, list):
        shapes = string.getShapes(curves)
        group = cmds.group(em=True, name=name)
        shapes.append(group)
        p = cmds.parent(*shapes, s=1, r=1)
        cmds.delete(curves)
    else:
        return str(curves)
    return group


def curveFromTransforms(nodeList):
    '''given a list of nodes make and return a 1-degree curve passing through those transforms'''
    positions = []
    for node in nodeList:
        positions.append(cmds.xform(node, q=True, t=True, ws=True))
    return cmds.curve(d=1, p=positions)
