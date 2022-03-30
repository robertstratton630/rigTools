import os
import json
import re


def createDirectory(parentDir, name):
    if not os.path.isdir(parentDir):
        return
    newDir = os.path.join(parentDir, name)
    try:
        os.makedirs(newDir)
    except:
        newDir
    return newDir


def get_subdirs(dir):

    folders = []
    try:
        folders = next(os.walk(dir))[1]
    except:
        return folders

    return folders


def get_subfiles(dir):

    files = []
    try:
        files = next(os.walk(dir))[2]
    except:
        return files
    return


def get_projects(projectRootPath):
    projects = get_subdirs(projectRootPath)
    return projects


def createDirectoryFromPath(path):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def saveJson(filePath, data, debug=False):
    with open(filePath, "w") as outFile:
        json.dump(data, outFile, indent=4)


def loadJson(filePath, debug=False):
    if not os.path.exists(filePath):
        return
    with open(filePath) as json_file:
        recalledData = json.load(json_file)
    return recalledData


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles


def getFolderNextVersion(versionList):
    vLast = None
    if isinstance(versionList, str):
        vLast = versionList[0]
    else:
        vLast = versionList[-1]

    v = vLast.split("v")[1]
    nextV = "v"+str(int(v)+1)
    return nextV

#########################################################################################################
# PROJECT ENVIROMENTS
#########################################################################################################
# getters

# get_project_rootpath()
# get_project_show()
# get_project_show_asset()


def get_project_rootpath():
    rootPath = os.getenv('PROJECT_ROOT_PATH')
    if not rootPath:
        return None
    return rootPath


def get_project_show():
    root = get_project_rootpath()
    if not root:
        return None
    project = os.getenv('PROJECT')
    return project


def get_project_show_path():
    root = get_project_rootpath()
    if not root:
        return None
    path = os.path.join(get_project_rootpath(), get_project_show())
    return path


def get_project_show_asset():
    root = get_project_rootpath()
    project = get_project_show()
    if not root and project:
        return None
    project = os.getenv('ASSET')
    return project


def get_project_show_asset_path():
    root = get_project_rootpath()
    if not root:
        return None
    path = os.path.join(get_project_rootpath(),
                        get_project_show(), get_project_show_asset())
    return path

# setters


def set_project_rootpath(name):
    if os.path.exists:
        os.environ['PROJECT_ROOT_PATH'] = name
    os.environ['PROJECT'] = "None"
    os.environ['ASSET'] = "None"


def set_project_show(name):
    rootPath = get_project_rootpath()
    os.environ['PROJECT'] = name
    if rootPath:
        newProject = osUtils.createDirectory(rootPath, name)

    # IF YOU CHANGE SHOW CLEAR ASSET
    set_project_show_asset(None)


def set_project_show_asset(name):
    if name is None:
        os.environ['ASSET'] = "None"
        return

    rootPath = get_project_rootpath()
    project = get_project_show()
    if not rootPath and project:
        return
    os.environ['ASSET'] = name
    if name:
        newProject = osUtils.createDirectory(
            os.path.join(rootPath, project), name)
    return newProject


#########################################################################################################
# RIGGING TOOLS ENVIROMENTS
#########################################################################################################

def get_rsTools_rootPath():
    path = os.path.dirname(__file__)
    path = path.replace("/", "\\")
    path = path.split("rsTools")[0]
    path = os.path.join(os.path.dirname(path), "rsTools")
    return path


def get_rsTools_img_path_controls():
    path = get_rsTools_rootPath()
    path = os.path.join(path, "_img")
    path = os.path.join(path, "_control")
    return path


def get_rsTools_img_path_shelf():
    path = get_rsTools_rootPath()
    path = os.path.join(path, "_img")
    path = os.path.join(path, "_shelf")
    return path


def get_rsTools_img_path_ui():
    path = get_rsTools_rootPath()
    path = os.path.join(path, "_img")
    path = os.path.join(path, "_ui")
    return path


def get_rsTools_data_path_cacheData():
    path = get_rsTools_rootPath()
    path = os.path.join(path, "_data", "_cacheData")
    return path


def get_rsTools_data_path_controlData():
    path = get_rsTools_rootPath()
    path = os.path.join(path, "_data", "_controlData")
    return path


def cache_enviroment():
    rootDir = get_project_rootpath()
    projectName = get_project_show()
    assetName = get_project_show_asset()

    info = {"projectRoot": rootDir,
            "projectName": projectName,
            "asset": assetName}

    dataPath = get_rsTools_data_path_cacheData()
    if dataPath:
        cacheFile = os.path.join(dataPath, "envCache.json")
        osUtils.saveJson(cacheFile, info)


def loadCacheEnviroments():
    cacheJson = os.path.join(
        get_rsTools_data_path_cacheData(), "envCache.json")
    data = osUtils.loadJson(cacheJson)
    if data:
        set_project_rootpath(data.get("projectRoot", None))
        set_project_show(data.get("projectName", None))
        set_project_show_asset(data.get("asset", None))


def listAllProjects():
    projectFolder = get_project_rootpath()
    projects = osUtils.get_subdirs(projectFolder)
    return projects


def listAllAssets():
    projectFolder = get_project_show_path()
    assets = osUtils.get_subdirs(projectFolder)
    return assets



def buildAssetProjectRoot(projectName):

    rootPath = env.get_project_rootpath()
    project = env.get_project_show()
    assetEnv = env.get_project_show_asset()

    if assetEnv:
        assetPath = os.path.join(rootPath, project, assetEnv)

        projectStructure = {"release":
                            {"rigSkeleton": [],
                             "rigBound": [],
                             "rigPuppet": [],
                             "model": [],
                             "rigModel": [],
                             "mayaScene": [],
                             "animCurves": [],
                             },
                            "wip":
                            {"model": [],
                             "rig": [],
                             "anim": [],
                             "lookdev": [],
                             "fx": [],
                             "techAnim": [],
                             "light": [],
                             "comp": [],
                             "mayaScene": [],
                             "animCurves": [],
                             }
                            }

        for mode in projectStructure:
            baseP = osUtils.createDirectory(assetPath, mode)
            for assetType in projectStructure[mode]:
                assetP = osUtils.createDirectory(baseP, assetType)
                for subFolder in projectStructure[mode][assetType]:
                    sub = osUtils.createDirectory(assetP, subFolder)


def buildProjectRoot(projectName):
    rootPath = env.get_project_rootpath()
    baseP = osUtils.createDirectory(rootPath, projectName)


def getAssetSetList():
    b = ["rigSkeleton", "rigBound", "rigPuppet",
         "model", "rigModel", "mayaScene", "animCurves"]
    return b


def findAssets(project, asset, assetType):
    rootPath = env.get_project_rootpath()
    assetPath = os.path.join(rootPath, project, asset, "release", assetType)
    children = osUtils.get_subdirs(assetPath)
    return children


# sets operations
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


def sort(l):
    if l:
        def convert(text): return float(text) if text.isdigit() else text
        def alphanum(key): return [convert(c)
                                   for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key)]
        l.sort(key=alphanum)
    return l


def getAssetVersions(project, asset, assetType, assetName):
    rootPath = env.get_project_rootpath()
    assetPath = os.path.join(rootPath, project, asset,
                             "release", assetType, assetName)

    if not os.path.exists(assetPath):
        osUtils.createDirectoryFromPath(assetPath)

    children = []
    try:
        children = sort(osUtils.get_subdirs(assetPath))
    except:
        pass
    return children


def openScene(file_path):
    force = self.force_cb.isChecked()
    if not force and cmds.file(q=True, modified=True):
        result = QtWidgets.QMessageBox.question(
            self, "Modified", "Current scene has unsaved changes. Continue?")
        if result == QtWidgets.QMessageBox.StandardButton.Yes:
            force = True
        else:
            return
    cmds.file(file_path, open=True, ignoreVersion=True, force=force)


def importScene(file_path):
    cmds.file(file_path, i=True, ignoreVersion=True)


def referenceScene(file_path, nameSpace):
    cmds.file(file_path, reference=True, ignoreVersion=True, ns=nameSpace)

# exportScene(r"\\WDMYCLOUD\Public\mayaDemo\batmanVsSuperMan\charBatman\release\model\bigdaveLODa\v1\tmp.ma",True)


def exportScene(pathName, selected=False):

    if os.path.isdir(pathName):
        _logger.warning("ExportType Must be a file")
        return

    if not pathName.endswith('.ma'):
        _logger.warning("FilePath extension must be .ma or .mb")
        return

    if selected:
        pm.exportSelected(pathName,
                          constructionHistory=True,
                          constraints=True,
                          expressions=True,
                          shader=True)
    else:
        pm.exportAll(pathName,
                     constructionHistory=True,
                     constraints=True,
                     expressions=True,
                     shader=True)


def getAllTopNodes():
    ls = cmds.ls(typ="transform")
    topNodes = []

    for l in ls:
        parents = cmds.listRelatives(l, allParents=True)

        if not parents:
            if not catch.isType(l, "camera"):
                topNodes.append(l)
    return topNodes


def _createModelMetaData(node):
    meshes = tUtils.findObjectsUnderNode(node, "mesh")
    curves = tUtils.findObjectsUnderNode(node, "nurbsCurve")
    if curves:
        meshes = meshes + curves

    geometry = {}
    for geo in meshes:
        short = str(string.getNameShort(geo))
        vertCount = cmds.polyEvaluate(geo, v=True)
        faceCount = cmds.polyEvaluate(geo, f=True)
        edgeCount = cmds.polyEvaluate(geo, e=True)
        geometry[short] = {"vertCount": vertCount,
                           "faceCount": faceCount,
                           "edgeCount": edgeCount
                           }
    return geometry


def _createJointMetaData(node):
    joints = tUtils.findObjectsUnderNode(node, "joint")

    dic = {}
    for j in joints:
        short = str(string.getNameShort(j))
        tx = cmds.getAttr(j+".tx")
        ty = cmds.getAttr(j+".ty")
        tz = cmds.getAttr(j+".tz")
        rx = cmds.getAttr(j+".rx")
        ry = cmds.getAttr(j+".ry")
        rz = cmds.getAttr(j+".rz")
        sx = cmds.getAttr(j+".sx")
        sy = cmds.getAttr(j+".sy")
        sz = cmds.getAttr(j+".sy")

        dic[short] = {"tx": tx,
                      "ty": ty,
                      "tz": tz,
                      "rx": rx,
                      "ry": ry,
                      "rz": rz,
                      "sx": sx,
                      "sy": sy,
                      "sz": sz
                      }
    return dic


def saveMetaData(pathName, topNode=None, assetType="rigSkeleton", **data):
    q = datetime.now()
    timestampStr = q.strftime("%d-%b-%Y (%H:%M:%S.%f)")

    time = data.get("time", timestampStr)
    comment = data.get("comment", "default Comment")
    output = {"time": time,
              "comment": comment,
              }
    allItems = {}

    sceneTopNodes = getAllTopNodes()

    if topNode:
        if cmds.objExists(topNode):
            output["topNodes"] = topNode
            element = topNode.split("_")[-2]
            topNodeSet = "rigHubSet_"+assetType+"_"+element

            # store
            output["mainSet"] = topNodeSet

            skeletonCacheSet = "rigHubSet_"+assetType+"_skeletonCache"
            geometryCacheSet = "rigHubSet_"+assetType+"_geometryCache"
            animControlsCacheSet = "rigHubSet_"+assetType+"_animControls"

            # RIG SKELETON
            if assetType == "rigSkeleton":
                if cmds.objExists(skeletonCacheSet):
                    output["skeletonCacheSet"] = skeletonCacheSet
                    output["skeletonCacheItems"] = _createJointMetaData(
                        skeletonCacheSet)

            # RIG PUPPET
            if assetType == "rigPuppet":
                # SKELETON
                if cmds.objExists(skeletonCacheSet):
                    output["skeletonCacheSet"] = skeletonCacheSet
                    output["skeletonCacheItems"] = _createJointMetaData(
                        skeletonCacheSet)
                # GEOMETRY
                if cmds.objExists(geometryCacheSet):
                    output["geometryCacheSet"] = geometryCacheSet
                    output["geometryCacheItems"] = _createModelMetaData(
                        geometryCacheSet)
                # CONTROLS
                if cmds.objExists(animControlsCacheSet):
                    output["animControlCacheSet"] = animControlsCacheSet
                    setItems = getSetItems(animControlsCacheSet)
                    output["animControlCacheSet"] = setItems

            # RIG PUPPET
            if assetType == "rigBound":
                # SKELETON
                if cmds.objExists(skeletonCacheSet):
                    output["skeletonCacheSet"] = skeletonCacheSet
                    output["skeletonCacheItems"] = _createJointMetaData(
                        skeletonCacheSet)
                # GEOMETRY
                if cmds.objExists(geometryCacheSet):
                    output["geometryCacheSet"] = geometryCacheSet
                    output["geometryCacheItems"] = _createModelMetaData(
                        geometryCacheSet)

            if assetType == "model":
                # GEOMETRY
                if cmds.objExists(geometryCacheSet):
                    output["geometryCacheSet"] = geometryCacheSet
                    output["geometryCacheItems"] = _createModelMetaData(
                        geometryCacheSet)

    else:
        sceneTopNodes = getAllTopNodes()
        output["topNodes"].append(sceneTopNodes)

    osUtils.saveJson(pathName, output)


def loadMetaData(pathName, dataReturn="geo"):
    data = osUtils.loadJson(pathName)
    comment = data.get("comment", "")
    setItems = data.get("items", "")
    geometryCache = data.get("geometry", "")

    data = {"comment": comment,
            "setItems": setItems,
            "geo": geometryCache}

    return data[dataReturn]


def getAllProjects():
    projectPath = env.get_project_rootpath()
    assets = osUtils.get_subdirs(projectPath)
    return assets


def getProjectAssets(project):
    root = env.get_project_rootpath()
    project = os.path.join(root, project)
    assets = osUtils.get_subdirs(project)
    return assets


def getProjectAssetsByType(project, asset, assetType):
    root = env.get_project_rootpath()
    path = os.path.join(root, project, asset, "release", assetType)
    assets = osUtils.get_subdirs(path)
    return assets

# getAssetByType("library","chardigidouble","model")
# getAssetVersions(rootPath,project,asset,assetType,assetName):


def getCurrentProjectAssets():
    root = env.get_project_rootpath()
    project = os.path.join(root, env.get_project_show())
    assets = osUtils.get_subdirs(show)
    return assets


def compareModelSetMetaData(pathA=None, pathB=None):

    useScene = False
    exist = cmds.objExists("rigHubSet_geometryCache")
    if pathA is None or pathB is None and exist:
        useScene = True

    if not useScene:
        aExists = os.path.exists(pathA)
        bExists = os.path.exists(pathB)

        if not aExists or not bExists:
            return "Paths are not valid"

        geoDataA = loadMetaData(pathA, "geo")
        geoDataB = loadMetaData(pathB, "geo")

        geoA = geoDataA.keys()
        geoB = geoDataB.keys()

        diff = string.diff(geoA, geoB)
        return diff

    else:

        geoA = getSetItems("rigHubSet_geometryCache")
        geoDataB = loadMetaData(pathB, "geo")

        geoB = geoDataB.keys()

        diff = string.diff(geoA, geoB)
        return diff

    return None


def compareModelTopologyMetaData(pathA=None, pathB=None):

    useScene = False
    exist = cmds.objExists("rigHubSet_geometryCache")
    if pathA is None or pathB is None and exist:
        useScene = True

    if not useScene:
        aExists = os.path.exists(pathA)
        bExists = os.path.exists(pathB)

        if not aExists or not bExists:
            return "Paths are not valid"

        geoDataA = loadMetaData(pathA, "geo")
        geoDataB = loadMetaData(pathB, "geo")

        geoA = geoDataA.keys()
        geoB = geoDataB.keys()

        common = string.common(geoA, geoB)

        badMatch = []
        for c in common:
            vCountA = geoDataA[c].get("vertCount", -1)
            vCountB = geoDataB[c].get("vertCount", -1)
            if vCountA != vCountB:
                badMatch.append(c)

        return badMatch

    else:

        geoA = getSetItems("rigHubSet_geometryCache")
        geoDataB = loadMetaData(pathB, "geo")

        geoB = geoDataB.keys()
        common = string.common(geoA, geoB)

        badMatch = []
        for c in common:
            vCountA = cmds.polyEvaluate(c, v=True)
            vCountB = geoDataB[c].get("vertCount", -1)
            if vCountA != vCountB:
                badMatch.append(c)

        return badMatch

    return None


def getAssetVersions(project, asset, assetType, assetName):
    rootPath = env.get_project_rootpath()
    assetPath = os.path.join(rootPath, project, asset,
                             "release", assetType, assetName)

    if not os.path.exists(assetPath):
        osUtils.createDirectoryFromPath(assetPath)

    children = []
    try:
        children = sort(osUtils.get_subdirs(assetPath))
    except:
        pass
    return children
