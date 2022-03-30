import maya.mel as mm
import maya.cmds as cmds
import maya.api.OpenMaya as om
import math


def isCurve(mesh):

    # Check Object Exists
    if not cmds.objExists(mesh):
        return False

    # Check Shape
    if 'transform' in cmds.nodeType(mesh, i=True):
        meshShape = cmds.ls(cmds.listRelatives(
            mesh, s=True, ni=True, pa=True) or [], type='nurbsCurve')
        print meshShape
        if not meshShape:
            return False
        mesh = meshShape[0]

        # Check Mesh
    if cmds.objectType(mesh) != 'nurbsCurve':
        return False

    # Return Result
    return True
