import maya.cmds as cmds
import rsTools.utils.data.osUtils as osUtils
import os,cPickle,time
import rsTools.utils.data.scene.topNode as topUtils
__dataPath__ = osUtils.get_project_show_asset_path()



___ignores___ = ["dagPose", "shadingEngine", "lambert", "blinn",
                 "nodeGraphEditorInfo", "mesh", "pointConstraint",
                 "parentConstraint", "orientConstraint", "aimConstraint", "objectSet", "groupId"]


def saveNodeAttrAndConnectionsData(node, verbose=False):
    folder = os.path.join(__dataPath__, "data", "connections", node, "")

    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topUtils.getRigBoundTopNodes()
    if topNode:
        topNode = topNode[0]
        element = cmds.getAttr(topNode+".element", asString=True)
        folder = os.path.join(__dataPath__, "data",
                              element, "connections", node, "")

    ''' create folder '''
    t1 = time.time()
    osUtils.createDirectoryFromPath(folder)

    versions = array.sort(osUtils.getSubdirs(folder))
    nextVersion = "v1"
    if versions:
        nextVersion = osUtils.getFolderNextVersion(versions)
    newFolder = osUtils.createDirectory(folder, nextVersion)

    ''' set filePath '''
    filePath = os.path.join(newFolder, transform+".json").replace("\\", "/")

    data = {"attributes": tUtils.getAttributesAndConnections(transform)}

    osUtils.saveJson(filePath, data)


def loadTransformAttributeData(transform, topNode=None, version=-1, verbose=False):
    if not cmds.objExists(transform):
        return None

    folder = os.path.join(__dataPath__, "data", "transform", transform, "")

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
                              element, "transform", transform, "")

    if os.path.exists(folder):
        findVersion = "v"+str(version)
        versions = array.sort(osUtils.getSubdirs(folder))
        if version == -1:
            findVersion = versions[-1]

        data = {}
        filePath = os.path.join(folder, findVersion,
                                transform+".json").replace("\\", "/")

        if os.path.exists(filePath):
            if verbose:
                _logger.info("Transform Data : {0}".format(filePath))

            data = osUtils.loadJson(filePath)

            for item in data["attributes"]:
                attrType = item[0]
                attr = item[1]
                val = item[2]
                connection = item[3]
                minVal = item[4]
                maxVal = item[5]
                keyable = item[6]
                locked = item[7]
                enum = item[8]
                hidden = item[9]

                objAndAttr = attr.split(".")

                if str(attrType) == "enum":
                    tUtils.attrAdd(objAndAttr[0], objAndAttr[1], str(
                        enum[0]), typ=attrType, **{"keyable": keyable, "hidden": hidden, "locked": locked})

                else:
                    tUtils.attrAdd(objAndAttr[0], objAndAttr[1], val, typ=attrType, minVal=minVal,
                                   maxVal=maxVal, **{"keyable": keyable, "hidden": hidden, "locked": locked})

        if data:
            return data
        else:
            _logger.warning("FILE DOES NOT EXIST: {0}".format(filePath))

    else:
        _logger.error(
            "Transform Data Doesnt Exist for Object: {0}".format(transform))


def objectType(obj):
    if cmds.objExists(obj):
        tempType = cmds.objectType(obj)
        shp = cmds.listRelatives(obj, s=True)
        if shp:
            tempType = cmds.objectType(shp[0])
    return tempType


def getAllConnections(transform):
    data = {}
    data["inputs"] = getAllInputConnections(transform)
    data["outputs"] = getAllOutputConnections(transform)
    data["defaultValues"] = getAllDefaultAttributeValues(transform)
    return data


def getAllInputConnections(transform):
    inputConnections = cmds.listConnections(transform, s=1, d=0, p=1)
    if inputConnections:
        data = {}
        for s in inputConnections:
            # skip unit conversions
            sOrig = s
            if objectType(s) == "unitConversion":
                try:
                    s = cmds.listConnections(s.split(".")[0], s=1, d=0, p=1)[0]
                except:
                    continue

            if cmds.objectType(s) in ___ignores___:
                continue

            if defUtils.isDeformer(s):
                continue

            '''split into node and attr '''
            split = s.split(".")
            outputTransform = split[0]
            outputTransformAttr = split[1]
            theTargetAttr = cmds.listConnections(s, s=0, d=1, p=1)[0]

            ''' make sure to skip source conversions'''
            if objectType(theTargetAttr) == "unitConversion":
                theTargetAttr = cmds.listConnections(
                    theTargetAttr.split(".")[0], s=0, d=1, p=1)[0]

            ''' check to make sure we dont get into infinite loop if cycle '''

            if ".inverseScale" in s or ".inverseScale" in theTargetAttr:
                continue

            attr = s.split(".")[1]
            node = s.split(".")[0]
            data[s] = {}
            data[s]["sourceAttribute"] = s
            data[s]["sourceName"] = node
            data[s]["sourceNodeType"] = objectType(node)

            if cmds.nodeType(node) == "transform":
                data[s]["sourceBaseNodeType"] = "transform"
            elif defUtils.isDeformer(node):
                data[s]["sourceBaseNodeType"] = "deformer"
            else:
                data[s]["sourceBaseNodeType"] = "node"

            node = theTargetAttr.split(".")[0]
            data[s]["targetAttribute"] = theTargetAttr
            data[s]["targetName"] = node
            data[s]["targetNodeType"] = objectType(node)

            if cmds.nodeType(node) == "transform":
                data[s]["targetBaseNodeType"] = "transform"
            elif defUtils.isDeformer(node):
                data[s]["targetBaseNodeType"] = "deformer"
            else:
                data[s]["targetBaseNodeType"] = "node"

        return data


def getAllOutputConnections(transform):
    outputConnections = cmds.listConnections(transform, s=0, d=1, p=1)

    if outputConnections:
        data = {}
        for s in outputConnections:
            # skip unit conversions
            sOrig = s
            if objectType(s) == "unitConversion":
                try:
                    s = cmds.listConnections(s.split(".")[0], s=0, d=1, p=1)[0]
                except:
                    continue

            if cmds.objectType(s) in ___ignores___:
                continue

            if defUtils.isDeformer(s):
                continue

            '''split into node and attr '''
            split = s.split(".")
            outputTransform = split[0]
            outputTransformAttr = split[1]
            theSourceAttr = cmds.listConnections(s, s=1, d=0, p=1)[0]

            ''' make sure to skip source conversions'''
            if objectType(theSourceAttr) == "unitConversion":
                theSourceAttr = cmds.listConnections(
                    theSourceAttr.split(".")[0], s=1, d=0, p=1)[0]

            if ".inverseScale" in s or ".inverseScale" in theSourceAttr:
                continue

            attr = s.split(".")[1]
            node = theSourceAttr.split(".")[0]
            data[s] = {}
            data[s]["sourceAttribute"] = theSourceAttr
            data[s]["sourceName"] = node
            data[s]["sourceNodeType"] = objectType(node)

            if cmds.nodeType(node) == "transform":
                data[s]["sourceBaseNodeType"] = "transform"
            elif defUtils.isDeformer(node):
                data[s]["sourceBaseNodeType"] = "deformer"
            else:
                data[s]["sourceBaseNodeType"] = "node"

            node = s.split(".")[0]
            data[s]["targetAttribute"] = s
            data[s]["targetName"] = node
            data[s]["targetNodeType"] = objectType(node)

            if cmds.nodeType(node) == "transform":
                data[s]["targetBaseNodeType"] = "transform"
            elif defUtils.isDeformer(node):
                data[s]["targetBaseNodeType"] = "deformer"
            else:
                data[s]["targetBaseNodeType"] = "node"

        return data


def getAllDefaultAttributeValues(transform):
    keyableAttrs = cmds.listAttr(transform, k=True)
    if keyableAttrs:
        output = []
        for a in keyableAttrs:
            try:
                val = cmds.getAttr(transform+"."+a)
                output.append([transform+"."+a, val])
            except:
                pass
        return output
