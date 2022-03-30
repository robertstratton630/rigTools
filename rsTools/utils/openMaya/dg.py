import maya.api.OpenMaya as om
import rsTools.utils.openMaya.dataUtils as dataUtils
import maya.cmds as cmds


from rsTools.utils.deformers.normalPush import NormalPush
__nodes__ = {"rig_normalPush": NormalPush}


def getDeformerDataAndConnections(obj):
    data = {}
    # get deformer inputs
    deformers = cmds.listHistory(obj, pdo=1, gl=1)
    for d in deformers:
        nodeType = cmds.nodeType(d)
        node = None

        if nodeType in __nodes__:
            node = __nodes__[nodeType](nodeName=d)

        if node:
            data[d] = node.getBuildString(
                includePath=False, rawPath=True, printResult=False)

    return data

    # get transform connections


def getTransformDataAndConnections(obj):
    pass


'''
data = getDeformerDataAndConnections("pSphere1")
node = eval(data["rig_normalPush1"])
'''
