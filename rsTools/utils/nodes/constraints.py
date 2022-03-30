import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

''' check node types '''


def isParentConstraint(obj):
    if getConstraintType(obj) == "parentConstraint":
        return True
    return False


def isPointConstraint(obj):
    if getConstraintType(obj) == "pointConstraint":
        return True
    return False


def isOrientConstraint(obj):
    if getConstraintType(obj) == "orientConstraint":
        return True
    return False


def isConstraint(obj):
    __list__ = ["parentConstraint", "pointConstraint", "orientConstraint"]
    if getConstraintType(obj) in __list__:
        return True
    return False


''' get constraint nodes on transform '''


def getConstraintNodes(obj):
    cons = []
    point = cmds.pointConstraint(obj, q=True)
    orient = cmds.orientConstraint(obj, q=True)
    parent = cmds.parentConstraint(obj, q=True)

    if point:
        if isinstance(point, list):
            for p in point:
                cons.append(p)
        else:
            cons.append(point)

    if orient:
        if isinstance(orient, list):
            for p in orient:
                cons.append(p)
        else:
            cons.append(point)

    if parent:
        if isinstance(parent, list):
            for p in parent:
                cons.append(p)
        else:
            cons.append(parent)

    return cons


''' get type of the constraint, point/orient/parent '''


def getConstraintType(constraintNode):
    if isinstance(constraintNode, unicode):
        constraintNode = str(constraintNode)

    if isinstance(constraintNode, str):
        return cmds.nodeType(constraintNode)

    if isinstance(constraintNode, list):
        items = []
        for a in constraintNode:
            items.append(getConstraintType(a))
        return items


''' get maya weight alias'''


def getConstraintWeightAliasList(obj):

    if isParentConstraint(obj):
        weightTargets = cmds.parentConstraint(obj, q=True, wal=True)
        return weightTargets

    if isPointConstraint(obj):
        weightTargets = cmds.pointConstraint(obj, q=True, wal=True)
        return weightTargets

    if isOrientConstraint(obj):
        weightTargets = cmds.orientConstraint(obj, q=True, wal=True)
        return weightTargets

    return None


''' get constraint targets '''


def getConstraintTargets(obj):

    if isParentConstraint(obj):
        weightTargets = cmds.parentConstraint(obj, q=True, tl=True)
        return weightTargets

    if isPointConstraint(obj):
        weightTargets = cmds.pointConstraint(obj, q=True, tl=True)
        return weightTargets

    if isOrientConstraint(obj):
        weightTargets = cmds.orientConstraint(obj, q=True, tl=True)
        return weightTargets

    return None


''' human readable array for weights '''


def getConstraintWeights(obj):
    if isConstraint(obj):
        wlist = getConstraintWeightAliasList(obj)
        weightTargets = [cmds.getAttr(obj+"."+w) for w in wlist]
        return weightTargets
    else:
        return None


''' offset data '''


def getConstraintOffsets(obj):
    numTargets = getConstraintWeights(obj)
    offsets = []

    if isParentConstraint(obj):
        for i in range(len(numTargets)):
            tx = cmds.getAttr(
                obj+".target[{0}].targetOffsetTranslateX".format(i))
            ty = cmds.getAttr(
                obj+".target[{0}].targetOffsetTranslateY".format(i))
            tz = cmds.getAttr(
                obj+".target[{0}].targetOffsetTranslateZ".format(i))
            rx = cmds.getAttr(obj+".target[{0}].targetOffsetRotateX".format(i))
            ry = cmds.getAttr(obj+".target[{0}].targetOffsetRotateY".format(i))
            rz = cmds.getAttr(obj+".target[{0}].targetOffsetRotateZ".format(i))

            offsets.append([tx, ty, tz, rx, ry, rz])
        return offsets

    if isPointConstraint(obj):
        tx = cmds.getAttr(obj+".offsetX")
        ty = cmds.getAttr(obj+".offsetY")
        tz = cmds.getAttr(obj+".offsetZ")

        offsets = [tx, ty, tz]
        return offsets

    if isOrientConstraint(obj):

        tx = cmds.getAttr(obj+".offsetX")
        ty = cmds.getAttr(obj+".offsetY")
        tz = cmds.getAttr(obj+".offsetZ")

        offsets = [tx, ty, tz]
        return offsets


def getConstraintRestPosition(obj):
    numTargets = getConstraintWeights(obj)
    offsets = []

    if isParentConstraint(obj):
        tx = cmds.getAttr(obj+".restTranslateX")
        ty = cmds.getAttr(obj+".restTranslateY")
        tz = cmds.getAttr(obj+".restTranslateZ")
        rx = cmds.getAttr(obj+".restRotateX")
        ry = cmds.getAttr(obj+".restRotateY")
        rz = cmds.getAttr(obj+".restRotateZ")

        offsets = [tx, ty, tz, rx, ry, rz]
        return offsets

    if isPointConstraint(obj):
        tx = cmds.getAttr(obj+".restTranslateX")
        ty = cmds.getAttr(obj+".restTranslateY")
        tz = cmds.getAttr(obj+".restTranslateZ")

        offsets = [tx, ty, tz]
        return offsets

    if isOrientConstraint(obj):
        rx = cmds.getAttr(obj+".restRotateX")
        ry = cmds.getAttr(obj+".restRotateY")
        rz = cmds.getAttr(obj+".restRotateZ")

        offsets = [rx, ry, rz]
        return offsets


def getConstrainedObject(obj):
    parent = cmds.listRelatives(obj, p=True)[0]
    return parent


def getSkipChannelsObject(obj):

    output = []
    if isParentConstraint(obj):
        tx = cmds.listConnections(obj+".constraintTranslateX", s=False, d=True)
        ty = cmds.listConnections(obj+".constraintTranslateY", s=False, d=True)
        tz = cmds.listConnections(obj+".constraintTranslateZ", s=False, d=True)
        rx = cmds.listConnections(obj+".constraintRotateX", s=False, d=True)
        ry = cmds.listConnections(obj+".constraintRotateY", s=False, d=True)
        rz = cmds.listConnections(obj+".constraintRotateZ", s=False, d=True)

        if not tx:
            output.append("tx")
        if not ty:
            output.append("ty")
        if not tz:
            output.append("tz")
        if not rx:
            output.append("rx")
        if not ry:
            output.append("ry")
        if not rz:
            output.append("rz")

    if isPointConstraint(obj):
        tx = cmds.listConnections(obj+".constraintTranslateX", s=False, d=True)
        ty = cmds.listConnections(obj+".constraintTranslateY", s=False, d=True)
        tz = cmds.listConnections(obj+".constraintTranslateZ", s=False, d=True)

        if not tx:
            output.append("x")
        if not ty:
            output.append("y")
        if not tz:
            output.append("z")

    if isOrientConstraint(obj):
        rx = cmds.listConnections(obj+".constraintRotateX", s=False, d=True)
        ry = cmds.listConnections(obj+".constraintRotateY", s=False, d=True)
        rz = cmds.listConnections(obj+".constraintRotateZ", s=False, d=True)

        if not rx:
            output.append("x")
        if not ry:
            output.append("y")
        if not rz:
            output.append("z")

    return output
