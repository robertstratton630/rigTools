import maya.api.OpenMaya as om
import maya.cmds as cmds

from . import dataUtils, matrix


def isTransform(obj):
    if not cmds.objExists(obj):
        return False
    mObject = dataUtils.getMObject(obj)
    if not mObject.hasFn(om.MFn.kTransform):
        return False
    return True


def getTransformMatrix(transform, local=False, time=None):

    # Check transform
    if not isTransform(transform):
        raise Exception('Object "'+transform+'" does not exist!!')

    # Define Matrix attribute
    matAttr = 'worldMatrix[0]'
    if local:
        matAttr = 'matrix'

    # Get time
    mat = om.MMatrix()
    if time != None:
        mat = cmds.getAttr(transform+'.'+matAttr, t=frame)
    else:
        mat = cmds.getAttr(transform+'.'+matAttr)

    # Build Matrix
    m = matrix.buildMatrix(translate=(mat[12], mat[13], mat[14]), xAxis=(
        mat[0], mat[1], mat[2]), yAxis=(mat[4], mat[5], mat[6]), zAxis=(mat[8], mat[9], mat[10]))

    # Return result
    return m


def matchTransformToMatrix(transform, inMat, r=True, t=True):
    if not cmds.objExists(transform):
        raise Exception('Transform "'+transform+'" does not exist!!')

    if t:
        trans = matrix.getTranslation(inMat)
        cmds.xform(transform, ws=True, t=(trans[0], trans[1], trans[2]))

    if r:
        rotate = matrix.getRotation(inMat)
        cmds.xform(transform, ws=True, r=True, ro=(
            rotate[0], rotate[1], rotate[2]))
