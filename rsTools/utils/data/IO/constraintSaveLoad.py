import maya.cmds as cmds
import rsTools.utils.data.osUtils as osUtils
import os,cPickle,time
import rsTools.utils.data.scene.topNode as topUtils
__dataPath__ = osUtils.get_project_show_asset_path()

def saveConstraintData(obj=None, verbose=False):
    if not cUtils.isConstraint(obj):
        return

    t1 = time.time()
    folder = os.path.join(__dataPath__, "data", "constraint", obj, "")

    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topUtils.getRigBoundTopNodes()
    if topNode:
        topNode = topNode[0]
        element = cmds.getAttr(topNode+".element", asString=True)
        folder = os.path.join(__dataPath__, "data",
                              element, "constraint", obj, "")

    ''' create folder '''
    t1 = time.time()
    osUtils.createDirectoryFromPath(folder)

    versions = array.sort(osUtils.getSubdirs(folder))
    nextVersion = "v1"
    if versions:
        nextVersion = osUtils.getFolderNextVersion(versions)
    newFolder = osUtils.createDirectory(folder, nextVersion)

    ''' set filePath '''
    filePath = os.path.join(newFolder, obj+".json").replace("\\", "/")

    ''' create tree '''
    data = {}

    data["constrained"] = cUtils.getConstrainedObject(obj)
    data["targets"] = cUtils.getConstraintTargets(obj)
    data["weights"] = cUtils.getConstraintWeights(obj)
    data["type"] = cUtils.getConstraintType(obj)
    data["offsets"] = cUtils.getConstraintOffsets(obj)
    data["rests"] = cUtils.getConstraintRestPosition(obj)
    data["skip"] = cUtils.getSkipChannelsObject(obj)

    ''' save out tree to disk '''
    osUtils.saveJson(filePath, data)

    tEnd = time.time() - t1

    if verbose:
        _logger.info("Data Stored for {0} in : {1}".format(obj, filePath))


def loadConstraintData(node, topNode=None, version=-1, verbose=False):

    folder = os.path.join(__dataPath__, "data", "constraint", node, "")

    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topNode or topUtils.getRigBoundTopNodes()
    if topNode:
        if isinstance(topNode, list):
            topNode = topNode[0]
        try:
            element = cmds.getAttr(topNode+".element", asString=True)
        except:
            element = topNode.split("_")[-2]
        folder = os.path.join(__dataPath__, "data",
                              element, "constraint", node, "")

    if os.path.exists(folder):
        findVersion = "v"+str(version)
        versions = array.sort(osUtils.getSubdirs(folder))
        if version == -1:
            findVersion = versions[-1]

        data = {}
        filePath = os.path.join(folder, findVersion,
                                node+".json").replace("\\", "/")

        if os.path.exists(filePath):
            data = osUtils.loadJson(filePath)

            constrained = data["constrained"]
            targets = data["targets"]
            weights = data["weights"]
            typ = data["type"]
            offsets = data["offsets"]
            rests = data["rests"]
            skip = data.get("skip", [])

            if typ == "parentConstraint":
                ''' create node '''

                if not cmds.objExists(node):

                    skipTranslate = [item for item in skip if "t" in item]
                    skipRotate = [item for item in skip if "r" in item]
                    node = cmds.parentConstraint(
                        targets, constrained, skipTranslate=skipTranslate, skipRotate=skipRotate)[0]

                ''' set weights '''
                alias = list(cUtils.getConstraintWeightAliasList(node))
                for i, a in enumerate(alias):
                    cmds.setAttr(node+"."+a, weights[i])

                ''' set offsets '''
                for i, t in enumerate(targets):
                    cmds.setAttr(
                        node+".target[{0}].targetOffsetTranslateX".format(i), offsets[i][0])
                    cmds.setAttr(
                        node+".target[{0}].targetOffsetTranslateY".format(i), offsets[i][1])
                    cmds.setAttr(
                        node+".target[{0}].targetOffsetTranslateZ".format(i), offsets[i][2])
                    cmds.setAttr(
                        node+".target[{0}].targetOffsetRotateX".format(i), offsets[i][3])
                    cmds.setAttr(
                        node+".target[{0}].targetOffsetRotateY".format(i), offsets[i][4])
                    cmds.setAttr(
                        node+".target[{0}].targetOffsetRotateZ".format(i), offsets[i][5])

                ''' set rests '''
                cmds.setAttr(node+".restTranslateX", rests[0])
                cmds.setAttr(node+".restTranslateY", rests[1])
                cmds.setAttr(node+".restTranslateZ", rests[2])
                cmds.setAttr(node+".restRotateX", rests[3])
                cmds.setAttr(node+".restRotateY", rests[4])
                cmds.setAttr(node+".restRotateZ", rests[5])

            if typ == "pointConstraint":
                ''' create node '''
                if not cmds.objExists(node):
                    node = cmds.pointConstraint(
                        targets, constrained, skip=skip)[0]

                ''' set weights '''
                alias = list(cUtils.getConstraintWeightAliasList(node))
                for i, a in enumerate(alias):
                    cmds.setAttr(node+"."+a, weights[i])

                cmds.setAttr(node+".offsetX", offsets[i][0])
                cmds.setAttr(node+".offsetY", offsets[i][1])
                cmds.setAttr(node+".offsetZ", offsets[i][2])

                ''' set rests '''
                cmds.setAttr(node+".restTranslateX", rests[0])
                cmds.setAttr(node+".restTranslateY", rests[1])
                cmds.setAttr(node+".restTranslateZ", rests[2])

            if typ == "orientConstraint":
                ''' create node '''
                if not cmds.objExists(node):
                    node = cmds.orientConstraint(
                        targets, constrained, skip=skip)[0]

                ''' set weights '''
                alias = list(cUtils.getConstraintWeightAliasList(node))
                for i, a in enumerate(alias):
                    cmds.setAttr(node+"."+a, weights[i])

                cmds.setAttr(node+".offsetX", offsets[i][0])
                cmds.setAttr(node+".offsetY", offsets[i][1])
                cmds.setAttr(node+".offsetZ", offsets[i][2])

                ''' set rests '''
                cmds.setAttr(node+".restRotateX", rests[0])
                cmds.setAttr(node+".restRotateY", rests[1])
                cmds.setAttr(node+".restRotateZ", rests[2])

        if data:
            return data
        else:
            _logger.warning("FILE DOES NOT EXIST: {0}".format(filePath))

    else:
        _logger.error(
            "Transform Data Doesnt Exist for Object: {0}".format(node))
