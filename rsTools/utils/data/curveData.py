import os
import json

import cPickle as pickle
import maya.cmds as mc
import maya.OpenMayaUI as omui
import pymel.core as pm

from rsTools import utils
import rsTools.utils.osUtils.enviroments as env
from rsTools.utils import nurbs, catch, image, path, string
import rsTools.utils.transforms.transforms as transforms
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


# make sure that controlFolder exists
controlFolder = env.get_rsTools_data_path_controlData()
imageFolder = env.get_rsTools_img_path_controls()

""" save controlData to folder """


def saveControlData(nurbsObject=None, controlName=None, saveThumbnail=False, debug=False):

    if mc.objExists(nurbsObject) & catch.isType(nurbsObject, "nurbsCurve"):

        xfile = os.path.join(controlFolder, (controlName+".pkl"))
        curveData = nurbs.getNurbsCurveDataClean(nurbsObject)

        dump = pickle.dump(curveData, open(xfile, "wb"))
        print("Saving Data To File Path {0}".format(xfile))

        if debug:
            jsonFile = os.path.join(controlFolder, (controlName+".json"))
            with open(jsonFile, "w") as outFile:
                json.dump(curveData, outFile, indent=4)

    else:
        print("Please select valid curveNode")


""" load controlData from folder"""


def buildControlShape(controlName=None, libraryName=None, debug=False, scale=1.0, color=0):

    if not controlName or not libraryName:
        _logger.error("No Controller Name Provivded")

    xfile = os.path.join(controlFolder, (libraryName+".pkl"))
    if debug:
        xfile = os.path.join(controlFolder, (libraryName+".json"))

    curve = ""
    recalledData = {}
    if os.path.exists(xfile):
        if debug:
            with open(xfile) as json_file:
                recalledData = json.load(json_file)
        else:
            recalledData = pickle.load(open(xfile, "rb"))

        keys = recalledData.keys
        allCurves = []
        count = 1
        for key, dir in recalledData.iteritems():
            curve = pm.curve(
                name="tmp"+str(count), d=dir["degree"], p=dir["cvs"], k=dir["knots"], per=dir["periodic"])
            curve.scale.set(scale, scale, scale)
            pm.makeIdentity(curve, apply=True, t=0, r=0, s=1)
            curve = str(curve)
            allCurves.append(curve)
            count += 1

        if(len(allCurves) > 1):
            curve = nurbs.combineShapes(allCurves, controlName)
        else:
            curve = mc.rename(curve, controlName)

        curve = str(curve)
        transforms.enableDrawOverrides(curve)
        transforms.setColorIndex(curve, index=color)

        shapes = catch.getShapes(curve)
        [mc.rename(s, curve+"Shape#") for s in shapes]

    else:
        _logger.error("ControlName Does not Exist in DataBase")

    return curve

# list all of the existing controls in the lib


def listControlsInLibrary():
    onlyfiles = [f.split(".")[0] for f in os.listdir(
        controlFolder) if os.path.isfile(os.path.join(controlFolder, f))]
    onlyfiles = sorted(list(set(onlyfiles)))
    return onlyfiles
