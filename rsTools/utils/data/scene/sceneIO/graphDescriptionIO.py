import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import rsTools.utils.openMaya.transform as tOMUtils
import rsTools.utils.openMaya.deformer as defUtils
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.openMaya.passReference as ref
import rsTools.utils.openMaya.dataUtils as dataUtils
import rsTools.utils.array as array
import rsTools.utils.shaders as shader
import rsTools.utils.array as aUtils
from functools import partial
import rsTools.utils.osUtils.enviroments as env
import rsTools.utils.osUtils.osUtils as osUtils
import os,cPickle,time
import rsTools.utils.scene.topNode as topUtils

import rsTools.utils.scene.sceneIO.attrConnectionIO as attrIO


import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

__dataPath__ = env.get_project_show_asset_path()


########################################
# SAVE LOAD DEPENDACY DATA
########################################

#saveTransformDependacyDescriptionData("library_rigBound_bearALODa_GRP",verbose=True)
#saveConnectionData("l_legJBLegJA_InterpPushNode")
#loadConnectionData("l_legJBLegJA_InterpPushNode")
#loadAllConnectionData("library_rigBound_bearALODa_GRP") 


def saveTransformDependacyDescriptionData(topNode=None,verbose=True):
    t1 = time.time()
    folder = os.path.join(__dataPath__,"data","dGraph","")
        
    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topNode or topUtils.getRigBoundTopNodes()
    if topNode:
        if isinstance(topNode,list):
            topNode = topNode[0]
        try:
            element = cmds.getAttr(topNode+".element",asString=True)
        except:
            element = topNode.split("_")[-2]    
        folder = os.path.join(__dataPath__,"data",element,"dGraph","")
        
    ''' create folder '''
    t1 = time.time()
    osUtils.createDirectoryFromPath(folder)
    
    versions = array.sort(osUtils.get_subdirs(folder))
    nextVersion = "v1"
    if versions:
        nextVersion = osUtils.getFolderNextVersion(versions)
    newFolder = osUtils.createDirectory(folder,nextVersion)

    ''' set filePath '''
    filePath = os.path.join(newFolder,"sceneTransformDependencyDescription.json").replace("\\","/")

    ''' create tree and all data'''
    tree = buildAllTransformConnectionTree(topNode)
    ''' save out tree to disk '''
    osUtils.saveJson(filePath,tree)
    
    ''' save out all connection data '''
    flattenItems = []
    flattenDictByKeys(tree,flattenItems)
    flattenItems = list(set(flattenItems))
    
    if flattenItems:
        for f in flattenItems:
            saveConnectionData(f,verbose=False)
    

    tEnd = time.time() - t1
    
    _logger.info("dependency Data for {0} in : {1}".format(topNode,tEnd))
 
def loadSceneTransformDependacyData(topNode=None,version = -1,verbose=True):
    t1 = time.time()
    folder = os.path.join(__dataPath__,"data","dGraph","")
    
    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topNode or topUtils.getRigBoundTopNodes()
    if topNode:
        if isinstance(topNode,list):
            topNode = topNode[0]
        try:
            element = cmds.getAttr(topNode+".element",asString=True)
        except:
            element = topNode.split("_")[-2]    
        folder = os.path.join(__dataPath__,"data",element,"dGraph","")
  
    ''' make sure folder exists '''
    if not os.path.exists(folder):
        return
        
    ''' find correct version '''
    findVersion = "v"+str(version)
    versions = array.sort(osUtils.get_subdirs(folder))
    if version == -1:
        findVersion = versions[-1]
         
    data = {}
    filePath = os.path.join(folder,findVersion,"sceneTransformDependencyDescription.json").replace("\\","/")

    ''' make sure file exists '''
    if not os.path.exists(filePath):
        _logger.warning("FILE DOES NOT EXIST: {0}".format(filePath))
        return
        
    ''' verbose '''
    if verbose:
        _logger.info("sceneFile Loaded : {0}".format(filePath))
             
    ''' return data '''
    data = osUtils.loadJson(filePath)
    return data    

########################################
# SAVE LOAD CONNECTION DATA
########################################
     
     
#saveConnectionData("l_legJBLegJA_InterpPushNode")  
def saveConnectionData(node,topNode=None,verbose=True):
    t1 = time.time()
    folder = os.path.join(__dataPath__,"data","connections",node,"")
        
    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topNode or topUtils.getRigBoundTopNodes()
    if topNode:
        if isinstance(topNode,list):
            topNode = topNode[0]
        try:
            element = cmds.getAttr(topNode+".element",asString=True)
        except:
            element = topNode.split("_")[-2]    
        folder = os.path.join(__dataPath__,"data",element,"connections",node,"")
        
    ''' create folder '''
    t1 = time.time()
    osUtils.createDirectoryFromPath(folder)
    
    versions = array.sort(osUtils.get_subdirs(folder))
    nextVersion = "v1"
    if versions:
        nextVersion = osUtils.getFolderNextVersion(versions)
    newFolder = osUtils.createDirectory(folder,nextVersion)

    ''' set filePath '''
    filePath = os.path.join(newFolder,node+".json").replace("\\","/")

    ''' create tree and all data'''
    items = attrIO.getAllConnections(node)

    ''' save out tree to disk '''
    osUtils.saveJson(filePath,items)
    tEnd = time.time() - t1
    
    if verbose:
        _logger.info("Saved Connections to : {0}".format(filePath))
        
        
        

#t = loadConnectionData("l_legJBLegJA_InterpPushNode")
def loadConnectionData(node,topNode=None,version = -1,verbose=True):
    t1 = time.time()
    folder = os.path.join(__dataPath__,"data","connections",node,"")
    
    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topNode or topUtils.getRigBoundTopNodes()
    if topNode:
        if isinstance(topNode,list):
            topNode = topNode[0]
        try:
            element = cmds.getAttr(topNode+".element",asString=True)
        except:
            element = topNode.split("_")[-2]    
        folder = os.path.join(__dataPath__,"data",element,"connections",node,"")
  
    ''' make sure folder exists '''
    if not os.path.exists(folder):
        return
        
    ''' find correct version '''
    findVersion = "v"+str(version)
    versions = array.sort(osUtils.get_subdirs(folder))
    if version == -1:
        findVersion = versions[-1]
         
    data = {}
    filePath = os.path.join(folder,findVersion,node+".json").replace("\\","/")

    ''' make sure file exists '''
    if not os.path.exists(filePath):
        _logger.warning("FILE DOES NOT EXIST: {0}".format(filePath))
        return
        
    ''' verbose '''
    if verbose:
        _logger.info("sceneFile Loaded : {0}".format(filePath))
             
    ''' return data '''
    data = osUtils.loadJson(filePath)
    
    inputs = data.get("inputs",None)
    outputs = data.get("outputs",None)
    defaultVals = data.get("defaultValues",None)
    
    
    if inputs:
        for k,v in inputs.iteritems():
            sourceAttr = v["sourceAttribute"]
            sourceNode = v["sourceName"]
            sourceNodeType = v["sourceNodeType"]
            sourceNodeTypeBase = v["sourceBaseNodeType"]
             
            targetAttr = v["targetAttribute"]
            targetNode = v["targetName"]
            targetNodeType = v["targetNodeType"]
            targetNodeTypeBase = v["targetBaseNodeType"]
            
            ''' make sure source Node exists '''
            if not cmds.objExists(sourceNode):
                if not sourceNodeTypeBase == "transform":
                    if sourceNodeTypeBase == "node":
                        sourceNode = cmds.createNode(sourceNodeType,name=sourceNode)
                    if sourceNodeTypeBase == "deformer":
                        pass
                        
            ''' made sure targetNode exists '''
            if not cmds.objExists(targetNode):
                if not targetNodeTypeBase == "transform":
                    if targetNodeTypeBase == "node":
                        targetNode = cmds.createNode(targetNodeType,name=targetNode)
                    if targetNodeTypeBase == "deformer":
                        pass
                
            ''' we gucci lets connect stuff '''
            mel.eval('''catchQuiet(`connectAttr "{0}" "{1}"`)'''.format(sourceAttr,targetAttr))
            
    if outputs:
        for k,v in outputs.iteritems():
            sourceAttr = v["sourceAttribute"]
            sourceNode = v["sourceName"]
            sourceNodeType = v["sourceNodeType"]
            sourceNodeTypeBase = v["sourceBaseNodeType"]
             
            targetAttr = v["targetAttribute"]
            targetNode = v["targetName"]
            targetNodeType = v["targetNodeType"]
            targetNodeTypeBase = v["targetBaseNodeType"]
            
            ''' make sure source Node exists '''
            if not cmds.objExists(sourceNode):
                if not sourceNodeTypeBase == "transform":
                    if sourceNodeTypeBase == "node":
                        sourceNode = cmds.createNode(sourceNodeType,name=sourceNode)
                    if sourceNodeTypeBase == "deformer":
                        pass
                        
            ''' made sure targetNode exists '''
            if not cmds.objExists(targetNode):
                if not targetNodeTypeBase == "transform":
                    if targetNodeTypeBase == "node":
                        targetNode = cmds.createNode(targetNodeType,name=targetNode)
                    if targetNodeTypeBase == "deformer":
                        pass
                
            ''' we gucci lets connect stuff '''
            mel.eval('''catchQuiet(`connectAttr "{0}" "{1}"`)'''.format(sourceAttr,targetAttr))

    if defaultVals:
        for v in defaultVals:
            mel.eval('''catchQuiet(`setAttr "{0}" "{1}"`)'''.format(v[0],v[1]))
            
            
        
    return data    
        

def loadAllConnectionData(topNode=None,version = -1,verbose=True):
    topNode = topNode or topUtils.getRigBoundTopNodes()
    
    t1 = time.time()
    treeData = loadSceneTransformDependacyData(topNode,verbose=True)

    flattenItems = []
    flattenDictByKeys(treeData,flattenItems)
    flattenItems = list(set(flattenItems))

    if flattenItems:
        for f in flattenItems:
            loadConnectionData(f,verbose=False)
            
    tEnd = time.time() - t1
    if verbose:
        _logger.info("loaded all connections in : {0}".format(tEnd))




#tree = {} 
#g_dupCounter = []
#buildConnectionTreeNew(cmds.listRelatives("library_rigBound_bearALODa_GRP",c=1,ad=1,typ="transform"),tree)
#buildConnectionTreeNew("global_CTRL",tree)

#osUtils.saveJson("C:/3D/testData.json",tree)

#tree.keys()


def buildTransformConnectionTree(topNode, tree = {},startIter=0):
    
    if isinstance(topNode,list):
        return
        
    global g_dupCounter
    if startIter == 0:
        global g_dupCounter
        g_dupCounter = []
        
    g_dupCounter.append(topNode)

    childrenNodes=[]
    items = attrIO.getAllConnections(topNode)

    inputData = items["inputs"]
    outputData = items["outputs"]
    
    inputTransforms = []
    if inputData:
        inputTransforms = [val.split(".")[0] for val in inputData.keys()]
    
    outputTransforms = []
    if outputData:
        outputTransforms = [val.split(".")[0] for val in outputData.keys()]
    
    childrenNodes = childrenNodes + inputTransforms + outputTransforms
    
    childrenNodes = list(set(childrenNodes))
    childrenNodes = [a for a in childrenNodes if a not in g_dupCounter]
        
    if childrenNodes:
        childrenNodeData = {}
        for i,c in enumerate(childrenNodes):
            childrenNodeData[childrenNodes[i]] = getTransformData(a)

        tree[topNode] = (childrenNodeData, {})
        for child in childrenNodes:
            buildTransformConnectionTree(child, tree[topNode][1], startIter = startIter+1)
 
 
def getTransformData(transform):
    data = {}
    data["name"] = str(transform)
    data["nodeType"] = objectType(transform)
    return data
    
def objectType(obj):
    if cmds.objExists(obj):
        tempType = cmds.objectType(obj)
        shp = cmds.listRelatives(obj, s=True)
        if shp:
            tempType = cmds.objectType(shp[0])
    return tempType
    
#tree = connectionTreeForLoop("library_rigBound_bearALODa_GRP")
def buildAllTransformConnectionTree(topNode):
    
    transforms = cmds.listRelatives(topNode,c=1,ad=1,typ="transform")
    
    fullTree= {}
    for t in transforms:
        tree = {}
        global  g_dupCounter
        g_dupCounter = []
        buildTransformConnectionTree(t, tree)
        fullTree.update(tree)
        
    return fullTree
            
def flattenDictByKeys(tree={},filtered=[]):
    for k, v in tree.iteritems():
        filtered.append(k)
        if isinstance(v[1],dict):
            flattenDictByKeys(v[1],filtered)
   
   

    