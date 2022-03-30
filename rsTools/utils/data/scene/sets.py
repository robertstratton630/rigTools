import os
import rsTools.utils.osUtils.enviroments as env
import rsTools.utils.osUtils.osUtils as osUtils
import rsTools.utils.catch as catch
import maya.cmds as cmds
import pymel.core as pm
import re
import time
from datetime import datetime
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.string as string


import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def createSet(assetType, assetName, items=[]):
    if items is None:
        items = cmds.ls(sl=True)
    oSet = cmds.sets(items, name="rigHubSet_"+assetType+"_"+assetName)
    return oSet


def addSetItem(item, setName):
    oSet = cmds.sets(item, e=True, add=setName)
    return oSet


def removeSetItem(item, setName):
    oSet = cmds.sets(item, e=True, rm=setName)
    return oSet


def getSetItems(setName):
    items = cmds.sets(setName, q=True)
    return items


def getSetAssetType(setName):
    typ = setName.split("_")[1]
    return typ


def getSetAssetName(setName):
    typ = setName.split("_")[2]
    return typ


def createModelSet(assetType, assetName, topNode):
    mainSet = createSet(assetType, assetName, topNode)
    meshes = tUtils.findObjectsUnderNode(topNode, "mesh")
    geoCache = cmds.sets(meshes, name="rigHubSet_geometryCache")
    addSetItem(geoCache, mainSet)
