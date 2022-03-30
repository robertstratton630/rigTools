import maya.cmds as cmds
import rsTools.utils.data.osUtils as osUtils
import os,cPickle,time
import rsTools.utils.data.scene.topNode as topUtils
__dataPath__ = osUtils.get_project_show_asset_path()


def saveControlData(transform, verbose=True):
    if not nurbs.isNurbsCurve(transform):
        return

    folder = os.path.join(__dataPath__, "data", "controls", transform, "")

    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topUtils.getRigBoundTopNodes()
    if topNode:
        topNode = topNode[0]
        element = cmds.getAttr(topNode+".element", asString=True)
        folder = os.path.join(__dataPath__, "data", element,
                              "controlShapes", transform, "")

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

    curveData = nurbs.getNurbsCurveDataClean(transform)

    osUtils.saveJson(filePath, curveData)

    if verbose:
        _logger.warning("Saved to file: {0}".format(filePath))


def loadControlData(transform, topNode=None, version=-1, verbose=True):
    folder = os.path.join(__dataPath__, "data", "controlShapes", transform, "")

    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topNode or topUtils.getRigBoundTopNodes()
    if topNode:
        if isinstance(topNode, list):
            topNode = topNode[0]

        try:
            element = cmds.getAttr(topNode+".element", asString=True)
        except:
            element = topNode.split("_")[-2]

        folder = os.path.join(__dataPath__, "data", element,
                              "controlShapes", transform, "")

    if os.path.exists(folder):
        findVersion = "v"+str(version)
        versions = array.sort(osUtils.getSubdirs(folder))
        if version == -1:
            findVersion = versions[-1]

        data = {}
        filePath = os.path.join(folder, findVersion,
                                transform+".json").replace("\\", "/")
        curve = None
        if os.path.exists(filePath):
            if verbose:
                _logger.info("Transform Data : {0}".format(filePath))

            data = osUtils.loadJson(filePath)

            keys = data.keys
            allCurves = []
            count = 1
            for key, dir in data.iteritems():
                curve = pm.curve(
                    name="tmp"+str(count), d=dir["degree"], p=dir["cvs"], k=dir["knots"], per=dir["periodic"])
                pm.makeIdentity(curve, apply=True, t=0, r=0, s=1)
                curve = str(curve)
                allCurves.append(curve)
                count += 1

            if(len(allCurves) > 1):
                curve = nurbs.combineShapes(allCurves, transform)
            else:
                curve = cmds.rename(curve, transform)

            shapes = catch.getShapes(curve)
            [cmds.rename(s, curve+"Shape#") for s in shapes]

        if data:
            return curve
        else:
            _logger.warning("FILE DOES NOT EXIST: {0}".format(filePath))

    else:
        _logger.error(
            "Transform Data Doesnt Exist for Object: {0}".format(transform))
