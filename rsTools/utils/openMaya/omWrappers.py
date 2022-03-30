import maya.api.OpenMaya as om
import maya.cmds as cmds
from rsTools.utils.openMaya import mesh, matrix, dataUtils, transform
from rsTools.utils.openMaya import mesh


def getMatrix(inObj):

    # single input
    if isinstance(inObj, unicode):
        inObj = str(inObj)

    if isinstance(inObj, str):
        if transform.isTransform(inObj):
            mat = transform.getTransformMatrix(inObj)
            return mat

        if mesh.isMesh(inObj):
            if mesh.isMeshVertex(inObj):
                _id = mesh.getMeshID(inObj)
                mat = mesh.getVertexMatrix(inObj, _id)
                return mat
            if mesh.isMeshEdge(inObj):
                _id = mesh.getMeshID(inObj)
                mat = mesh.getEdgeMatrix(inObj, _id)
                return mat

            if mesh.isMeshFace(inObj):
                _id = mesh.getMeshID(inObj)
                mat = mesh.getFaceMatrix(inObj, _id)
                return mat

    else:
        mats = []
        for obj in inObj:
            mats.append(getMatrix(str(obj)))
        return mats
