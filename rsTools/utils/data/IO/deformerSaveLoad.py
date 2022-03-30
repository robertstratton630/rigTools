import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import rsTools.utils.openMaya.transform as transform
import rsTools.utils.openMaya.deformer as defUtils
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.data.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.openMaya.passReference as ref
import rsTools.utils.array as array
import rsTools.utils.shaders as shader
import rsTools.utils.array as aUtils
from functools import partial
import rsTools.utils.data.osUtils as osUtils
import rsTools.utils.data.osUtils.osUtils as osUtils
import os,cPickle,time

from rsTools.utils.openMaya.vec2 import Vec2


import rsTools.utils.openMaya.skincluster as skinUtils


import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

__dataPath__ = osUtils.get_project_show_asset_path()

'''
def saveDeformerData(deformer,verbose=True):
    t1 = time.time()
    nodeType = cmds.nodeType(deformer)
    deformerFolder = os.path.join(__dataPath__,"data","deformers",nodeType,deformer,"")
    osUtils.createDirectoryFromPath(deformerFolder)
    
    versions = array.sort(osUtils.getSubdirs(deformerFolder))
    nextVersion = "v1"
    if versions:
        nextVersion = osUtils.getFolderNextVersion(versions)
    newFolder = osUtils.createDirectory(deformerFolder,nextVersion)
    geometry = defUtils.getAffectedGeometry(deformer).keys()[0]
    uvs = meshUtils.getSharedUVs(geometry)
    
    weightList = defUtils.getWeights(deformer)
    attributes = defUtils.getAttributes(deformer)
    
    data = {"weights":weightList}
            
    jsonFile = deformer+"Weights.json"
    jsonFile = os.path.join(newFolder,jsonFile)
    osUtils.saveJson(jsonFile,data,debug=False)
    elapsedA = time.time()-t1
    
    if verbose:
        _logger.info("Time :{0} = Deformer Weights Saved : {1}".format(elapsedA,jsonFile))
  
    
    attributes = defUtils.getAttributes(deformer)
    
    data = {"deformerName":deformer,
            "geometry":geometry,
            "deformerType":nodeType,
            "attributes":attributes}
        
    print "NODE TYPE {0}:".format(nodeType)    
    if nodeType == "skinCluster":
        
        joints = skinUtils.getSkinClusterInfluences(deformer)
        print joints
    
        data["joints"] = joints
            
            
    jsonFile = deformer+"Info.json"
    jsonFile = os.path.join(newFolder,jsonFile)
    osUtils.saveJson(jsonFile,data,debug=False)
    elapsedB = time.time()-t1
    
    
    if verbose:
        _logger.info("Time :{0} = Deformer Weights Saved : {1}".format(elapsedA,jsonFile))
  
  
        
def loadDeformerWeights(deformer,version = -1,verbose=True):
    nodeType = cmds.nodeType(deformer)
    deformerFolder = os.path.join(__dataPath__,"data","deformers",nodeType,deformer,"")

    findVersion = "v"+str(version)
    versions = array.sort(osUtils.getSubdirs(deformerFolder))
    if version == -1:
        findVersion = versions[-1]
     
     
    deformerData = {}
    pickleFile = os.path.join(deformerFolder,findVersion,deformer+"Weights.json")
    if os.path.exists(pickleFile):
        if verbose:
            _logger.info("DeformerData Loaded : {0}".format(pickleFile))
         
        deformerData = osUtils.loadJson(jsonFile)
                
    if deformerData:
        return deformerData
    else:
        _logger.warning("FILE DOES NOT EXIST: {0}".format(pickleFile))
 '''    
        
def loadDeformerInformation(deformer,version = -1,verbose=True,nodeType = None):
    if not nodeType:
        nodeType = cmds.nodeType(deformer)
        
    deformerFolder = os.path.join(__dataPath__,"data","deformers",nodeType,deformer,"")

    findVersion = "v"+str(version)
    versions = array.sort(osUtils.getSubdirs(deformerFolder))
    if version == -1:
        findVersion = versions[-1]
     
     
    deformerData = {}
    jsonFile = os.path.join(deformerFolder,findVersion,deformer+"Info.json")
    if os.path.exists(jsonFile):
        if verbose:
            _logger.info("DeformerInfo Loaded : {0}".format(jsonFile))
         
        deformerData = osUtils.loadJson(jsonFile)
                
    if deformerData:
        return deformerData
    else:
        _logger.warning("FILE DOES NOT EXIST: {0}".format(jsonFile))    
        
     
     
## CPP BINDINGS

def saveDeformerDataCpp(deformer,verbose=True):
    t1 = time.time()
    
    if not defUtils.isDeformer(deformer):
        _logger.warning("Object is not a deformer")
        return
          
    nodeType = cmds.nodeType(deformer)
    deformerFolder = os.path.join(__dataPath__,"data","deformers",nodeType,deformer,"")
    osUtils.createDirectoryFromPath(deformerFolder)
    
    versions = array.sort(osUtils.getSubdirs(deformerFolder))
    nextVersion = "v1"
    if versions:
        nextVersion = osUtils.getFolderNextVersion(versions)
    newFolder = osUtils.createDirectory(deformerFolder,nextVersion)
    geometry = defUtils.getAffectedGeometry(deformer).keys()[0]

    # save deformer weights cpp

    jsonFile = os.path.join(newFolder,deformer+"Weights.json").replace("\\","/")
    mel.eval('rig_saveLoadWeights -task "save" -file "{0}" -deformer "{1}";'.format(jsonFile,str(deformer)))
    elapsedA = time.time()-t1
    if verbose:
        _logger.info("Time :{0} = Deformer Weights Saved : {1}".format(elapsedA,jsonFile))
  
  
    # save deformer info file
    vertCount = cmds.polyEvaluate(geometry,v=True) 
    attributes = defUtils.getAttributes(deformer)
    
    data = {"deformerName":deformer,
            "geometry":geometry,
            "deformerType":nodeType,
            "attributes":attributes,
            "vertCount":vertCount}
            
    if nodeType == "skinCluster":
        joints = skinUtils.getSkinClusterInfluences(deformer)    
        data["joints"] = joints
            
            
    jsonFile = deformer+"Info.json"
    jsonFile = os.path.join(newFolder,jsonFile)
    osUtils.saveJson(jsonFile,data,debug=False)
    elapsedB = time.time()-t1
        

def loadDeformerWeightsCpp(deformer,version = -1,doUV = False,verbose=True):
    t1 = time.time()
    nodeType = cmds.nodeType(deformer)
    deformerFolder = os.path.join(__dataPath__,"data","deformers",nodeType,deformer,"")

    findVersion = "v"+str(version)
    versions = array.sort(osUtils.getSubdirs(deformerFolder))
    if version == -1:
        findVersion = versions[-1]
     
    deformerData = {}
    weightFile = os.path.join(deformerFolder,findVersion,deformer+"Weights.json").replace("\\","/")
    if os.path.exists(weightFile):
        weightFile = weightFile.replace("\\","/")

        # get all the information
        infoFile = os.path.join(deformerFolder,findVersion,deformer+"Info.json")
        _data = loadDeformerInformation(deformer,version)
        _geometry = _data.get("geometry")
        _vertCount = _data.get("vertCount")
        
        
        # do quick check to auto try UV if vertcount doesnt match 
        vertCount = cmds.polyEvaluate(_geometry,v=True)            
        if not doUV and vertCount != _vertCount:
            doUV = True
            _logger.warning("VertCount Doesnt Match Version: {0}, Attempting to load Via UV Space".format(version))
            
        geoFile = None
        if doUV:
            folder = os.path.join(__dataPath__,"data","geometry",_geometry,"")
        
            if os.path.exists(folder):
                findVersion = "v"+str(version)
                versions = array.sort(osUtils.getSubdirs(folder))
                if version == -1:
                    findVersion = versions[-1]
                 
                data = {}
                _geoFile = os.path.join(folder,findVersion,_geometry+".json")
                if os.path.exists(_geoFile):
                    geoFile = _geoFile.replace("\\","/")
                else:
                    doUV = False
                    
            else:
                doUV = False
                
        if doUV:
            mel.eval('rig_saveLoadWeights -task "load" -file "{0}" -uvF "{1}" -deformer "{2}";'.format(weightFile,geoFile,deformer))
        else:
            mel.eval('rig_saveLoadWeights -task "load" -file "{0}" -deformer "{1}";'.format(weightFile,deformer))
         
        if verbose:
            tEnd = time.time() - t1
            
            _logger.info("{0}, DeformerWeights Loaded : {1}".format(tEnd,weightFile))
  
    else:
        _logger.warning("FILE DOES NOT EXIST: {0}".format(weightFile))
        