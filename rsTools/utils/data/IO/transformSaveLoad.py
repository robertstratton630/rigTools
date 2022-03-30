import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import rsTools.utils.openMaya.transform as tOMUtils
import rsTools.utils.openMaya.deformer as defUtils
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.data.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.omWrappers as omUtils
from functools import partial
import rsTools.utils.data.osUtils as osUtils

import os
import cPickle
import time

import rsTools.utils.data.scene.topNode as topUtils
from rsTools.utils.openMaya.vec2 import Vec2

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

__dataPath__ = osUtils.get_project_show_asset_path()


def saveTransformAttributeData(transform, verbose=False):
    folder = os.path.join(__dataPath__, "data", "transform", transform, "")

    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topUtils.getRigBoundTopNodes()
    if topNode:
        topNode = topNode[0]
        element = cmds.getAttr(topNode+".element", asString=True)
        folder = os.path.join(__dataPath__, "data",
                              element, "transform", transform, "")

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


# saveTransformAttributeData("library_rigBound_bearALODa_GRP")
#d = loadTransformAttributeData("library_rigBound_bearALODa_GRP")

# cmds.getAttr("l_legUpperTwistRig_GRP.reverse",cb=True)


#cmds.setAttr("l_legUpperTwistRig_GRP.reverse",k=True, cb= True)


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


# tUtils.attrAdd("library_rigBound_bearALODa_GRP","qweewqeqweqweqwe","defaultVal",typ="enum",**{"keyable":1,"hidden":0,"locked":1})
