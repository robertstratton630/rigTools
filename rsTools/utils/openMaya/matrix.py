import maya.cmds as mc
import maya.api.OpenMaya as OpenMaya

from . import mathUtils, dataUtils
import math

__startIndex__ = {0: 0,
                  1: 4,
                  2: 8,
                  3: 12}


def buildMatrix(xAxis=(1, 0, 0), yAxis=(0, 1, 0), zAxis=(0, 0, 1), translate=(0, 0, 0)):
    # Create transformation matrix from input vectors
    matrix = OpenMaya.MMatrix()

    setMatrixRow(0, xAxis, matrix)
    setMatrixRow(1, yAxis, matrix)
    setMatrixRow(2, zAxis, matrix)
    setMatrixRow(3, translate, matrix)

    return matrix


def setMatrixRow(row=0, vec=None, matrix=None):
    matrix[__startIndex__[row]] = vec[0]
    matrix[__startIndex__[row]+1] = vec[1]
    matrix[__startIndex__[row]+2] = vec[2]


def getMatrixRow(row=0, inMat=None):
    outVec = OpenMaya.MVector(inMat[__startIndex__[row]], inMat[__startIndex__[
                              row]+1], inMat[__startIndex__[row]+2])
    return outVec


def vectorMatrixMultiply(vector, matrix, transformAsPoint=False, invertMatrix=False):
    # Create MPoint/MVector object for transformation
    if transformAsPoint:
        vector = OpenMaya.MPoint(vector[0], vector[1], vector[2], 1.0)
    else:
        vector = OpenMaya.MVector(vector[0], vector[1], vector[2])

    # Check input is of type MMatrix
    if type(matrix) != OpenMaya.MMatrix:
        raise Exception(
            'Matrix input variable is not of expected type! Expecting MMatrix, received '+str(type(matrix))+'!!')

    # Transform vector
    if matrix != OpenMaya.MMatrix.identity:
        if invertMatrix:
            matrix = matrix.inverse()
        vector *= matrix

    # Return new vector
    return [vector.x, vector.y, vector.z]


def getTranslation(matrix):
    x = matrix[__startIndex__[3]]
    y = matrix[__startIndex__[3]+1]
    z = matrix[__startIndex__[3]+2]
    return (x, y, z)


def getRotation(matrix, rotationOrder='xyz'):
    # Calculate radian constant
    radian = 180.0/math.pi

    # Check rotation order
    if type(rotationOrder) == str:
        rotationOrder = rotationOrder.lower()
        rotateOrder = {'xyz': 0, 'yzx': 1,
                       'zxy': 2, 'xzy': 3, 'yxz': 4, 'zyx': 5}
        if not rotateOrder.has_key(rotationOrder):
            raise Exception('Invalid rotation order supplied!')
        rotationOrder = rotateOrder[rotationOrder]
    else:
        rotationOrder = int(rotationOrder)

    # Get transformation matrix
    transformMatrix = OpenMaya.MTransformationMatrix(matrix)

    # Get Euler rotation from matrix
    eulerRot = transformMatrix.rotation()

    # Return XYZ rotation values
    return (eulerRot.x*radian, eulerRot.y*radian, eulerRot.z*radian)


def buildRotation(aimVector, upVector=(0, 1, 0), aimAxis='x', upAxis='y'):
    '''
    Build rotation matrix from the specified inputs
    @param aimVector: Aim vector for construction of rotation matrix (worldSpace)
    @type aimVector: tuple or list
    @param upVector: Up vector for construction of rotation matrix (worldSpace)
    @type upVector: tuple or list
    @param aimAxis: Aim vector for construction of rotation matrix
    @type aimAxis: str
    @param upAxis: Up vector for construction of rotation matrix
    @type upAxis: str
    '''
    # Check negative axis
    negAim = False
    negUp = False
    if aimAxis[0] == '-':
        aimAxis = aimAxis[1]
        negAim = True
    if upAxis[0] == '-':
        upAxis = upAxis[1]
        negUp = True

    # Check valid axis
    axisList = ['x', 'y', 'z']
    if not axisList.count(aimAxis):
        raise Exception('Aim axis is not valid!')
    if not axisList.count(upAxis):
        raise Exception('Up axis is not valid!')
    if aimAxis == upAxis:
        raise Exception('Aim and Up axis must be unique!')

    # Determine cross axis
    axisList.remove(aimAxis)
    axisList.remove(upAxis)
    crossAxis = axisList[0]

    # Normaize aimVector
    aimVector = mathUtils.normalizeVector(aimVector)
    if negAim:
        aimVector = (-aimVector[0], -aimVector[1], -aimVector[2])
    # Normaize upVector
    upVector = mathUtils.normalizeVector(upVector)
    if negUp:
        upVector = (-upVector[0], -upVector[1], -upVector[2])

    # Get cross product vector
    crossVector = (0, 0, 0)
    if (aimAxis == 'x' and upAxis == 'z') or (aimAxis == 'z' and upAxis == 'y'):
        crossVector = mathUtils.crossProduct(upVector, aimVector)
    else:
        crossVector = mathUtils.crossProduct(aimVector, upVector)
    # Recalculate upVector (orthogonalize)
    if (aimAxis == 'x' and upAxis == 'z') or (aimAxis == 'z' and upAxis == 'y'):
        upVector = mathUtils.crossProduct(aimVector, crossVector)
    else:
        upVector = mathUtils.crossProduct(crossVector, aimVector)

    # Build axis dictionary
    axisDict = {aimAxis: aimVector, upAxis: upVector, crossAxis: crossVector}
    # Build rotation matrix
    mat = buildMatrix(xAxis=axisDict['x'],
                      yAxis=axisDict['y'], zAxis=axisDict['z'])

    # Return rotation matrix
    return mat


def inverseTransform(source, destination, translate=True, rotate=True, scale=True):
    '''
    Apply the inverse of a specified transform to another target transform.
    @param source: The source transform that will supply the transformation
    @type source: str
    @param destination: The destination transform that will receive the inverse transformation
    @type destination: str
    @param translate: Apply inverse translate to destination transform
    @type translate: bool
    @param rotate: Apply inverse rotation to destination transform
    @type rotate: bool
    @param scale: Apply inverse scale to destination transform
    @type scale: bool
    '''
    # ==========
    # - Checks -
    # ==========

    if not cmds.objExists(source):
        raise Exception('Transform "'+source+'" does not exist!!')
    if not cmds.objExists(destination):
        raise Exception('Transform "'+destination+'" does not exist!!')

    # Load decomposeMatrix plugin
    if not cmds.pluginInfo('decomposeMatrix', q=True, l=True):
        try:
            cmds.loadPlugin('decomposeMatrix')
        except:
            raise MissingPluginError(
                'Unable to load "decomposeMatrix" plugin!!')

    # =================================
    # - Apply Inverse Transformations -
    # =================================

    # Create and name decomposeMatrix node
    dcm = cmds.createNode('decomposeMatrix', n=source+'_decomposeMatrix')

    # Make connections
    cmds.connectAttr(source+'.inverseMatrix', dcm+'.inputMatrix', f=True)
    if translate:
        cmds.connectAttr(dcm+'.outputTranslate',
                         destination+'.translate', f=True)
    if rotate:
        cmds.connectAttr(dcm+'.outputRotate', destination+'.rotate', f=True)
    if scale:
        cmds.connectAttr(dcm+'.outputScale', destination+'.scale', f=True)

    # =================
    # - Return Result -
    # =================

    return dcm


def fromList(valueList):
    # Check Value List
    if len(valueList) != 16:
        raise Exception(
            'Invalid value list! Expecting 16 element, found '+str(len(valueList)))

    # Create transformation matrix from input vaules
    matrix = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList(valueList, matrix)
    return matrix


matrix = OpenMaya.MMatrix()


def asList(matrix):
    return [	matrix[0], matrix[1], matrix[2], matrix[3],
             matrix[4], matrix[5], matrix[6], matrix[7],
             matrix[8], matrix[9], matrix[10], matrix[11],
             matrix[12], matrix[13], matrix[14], matrix[15]	]


def printMatrix(matrix):
    print('%.3f' % matrix(0, 0))+', '+('%.3f' % matrix(0, 1)) + \
        ', '+('%.3f' % matrix(0, 2))+', '+('%.3f' % matrix(0, 3))
    print('%.3f' % matrix(1, 0))+', '+('%.3f' % matrix(1, 1)) + \
        ', '+('%.3f' % matrix(1, 2))+', '+('%.3f' % matrix(1, 3))
    print('%.3f' % matrix(2, 0))+', '+('%.3f' % matrix(2, 1)) + \
        ', '+('%.3f' % matrix(2, 2))+', '+('%.3f' % matrix(2, 3))
    print('%.3f' % matrix(3, 0))+', '+('%.3f' % matrix(3, 1)) + \
        ', '+('%.3f' % matrix(3, 2))+', '+('%.3f' % matrix(3, 3))


def matchTransformToMatrix(transform, matrix, r=True, t=True):
    if not cmds.objExists(transform):
        raise Exception('Transform "'+transform+'" does not exist!!')

    if t:
        trans = getTranslation(matrix)
        cmds.xform(transform, ws=True, t=(trans[0], trans[1], trans[2]))

    if r:
        rotate = getRotation(matrix)
        cmds.xform(transform, ws=True, ro=(rotate[0], rotate[1], rotate[2]))


def rotateMatrixBy(matrix, r=[0, 0, 0]):
    rot = OpenMaya.MEulerRotation(r[0], r[1], r[2])
    tMat = OpenMaya.MTransformationMatrix(matrix)
    tMat.rotateBy(rot, OpenMaya.MSpace.kObject)
    return tMat.asMatrix()


def rotateMatrixTo(matrix, r=[0, 0, 0]):
    rot = OpenMaya.MEulerRotation(r[0], r[1], r[2])
    tMat = OpenMaya.MTransformationMatrix(matrix)
    tMat.rotateTo(rot)
    return tMat.asMatrix()
