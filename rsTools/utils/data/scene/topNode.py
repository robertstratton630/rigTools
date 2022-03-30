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


def getAllTopNodes():
    ls = cmds.ls(typ="transform")
    topNodes = []

    for l in ls:
        parents = cmds.listRelatives(l, allParents=True)

        if not parents:
            if not catch.isType(l, "camera"):
                topNodes.append(l)
    return topNodes


def getTopNodes(assetType="rigSkeleton", element=None):
    allTopNodes = getAllTopNodes()
    if allTopNodes:
        tops = []
        for t in allTopNodes:
            if assetType in t:
                if element:
                    if element in t:
                        tops.append(t)
                else:
                    tops.append(t)
        return tops
    return None


def getRigSkeletonTopNodes(element=None):
    allTopNodes = getAllTopNodes()
    if allTopNodes:
        tops = []
        for t in allTopNodes:
            if "rigSkeleton" in t:
                if element:
                    if element in t:
                        tops.append(t)
                else:
                    tops.append(t)
        return tops
    return None


def getRigBoundTopNodes(element=None):
    allTopNodes = getAllTopNodes()
    if allTopNodes:
        tops = []
        for t in allTopNodes:
            if "rigBound" in t:
                if element:
                    if element in t:
                        tops.append(t)
                else:
                    tops.append(t)
        return tops
    return None


def getRigPuppetTopNodes(element=None):
    allTopNodes = getAllTopNodes()
    if allTopNodes:
        tops = []
        for t in allTopNodes:
            if "rigPuppet" in t:
                if element:
                    if element in t:
                        tops.append(t)
                else:
                    tops.append(t)
        return tops
    return None
