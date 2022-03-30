import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import rsTools.utils.openMaya.transform as transform
import rsTools.utils.openMaya.deformer as defUtils
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.openMaya.passReference as ref
import rsTools.utils.array as array
import rsTools.utils.shaders as shader
import rsTools.utils.array as aUtils
from functools import partial
import rsTools.utils.osUtils.enviroments as env
import rsTools.utils.osUtils.osUtils as osUtils
import os,cPickle,time

from rsTools.utils.openMaya.vec2 import Vec2

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

__dataPath__ = env.get_project_show_asset_path()

        
def loadGeometryData(mesh,version = -1,verbose=True):
    folder = os.path.join(__dataPath__,"data","geometry",mesh,"")
    
    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topUtils.getRigBoundTopNodes()
    if topNode:
        topNode = topNode[0]
        element = cmds.getAttr(topNode+".element",asString=True)
        folder = os.path.join(__dataPath__,"data",element,"geometry",mesh,"")
    
    if os.path.exists(folder):
        findVersion = "v"+str(version)
        versions = array.sort(osUtils.get_subdirs(folder))
        if version == -1:
            findVersion = versions[-1]
         
        data = {}
        pickleFile = os.path.join(folder,findVersion,mesh+".json")
        if os.path.exists(pickleFile):
            if verbose:
                _logger.info("GeometryData Loaded : {0}".format(pickleFile))
             
                     
            data = osUtils.loadJson(pickleFile)
                    
        if data:
            return data
        else:
            _logger.warning("FILE DOES NOT EXIST: {0}".format(pickleFile))
        
    else:
        _logger.error("GeomtryFile Doesnt Exist for Mesh: {0}".format(mesh))  
        
def saveGeometryDataCpp(mesh,verbose=True):
    geoFolder = os.path.join(__dataPath__,"data","geometry",mesh,"")
    
    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topUtils.getRigBoundTopNodes()
    if topNode:
        topNode = topNode[0]
        element = cmds.getAttr(topNode+".element",asString=True)
        geoFolder = os.path.join(__dataPath__,"data",element,"geometry",mesh,"")

        
    t1 = time.time()
    osUtils.createDirectoryFromPath(geoFolder)
    
    versions = array.sort(osUtils.get_subdirs(geoFolder))
    nextVersion = "v1"
    if versions:
        nextVersion = osUtils.getFolderNextVersion(versions)
    newFolder = osUtils.createDirectory(geoFolder,nextVersion)

    filePath = os.path.join(newFolder,mesh+".json").replace("\\","/")

    mel.eval('rig_saveGeometryFile -f "{0}" -mesh "{1}";'.format(filePath,mesh))

    elapsedA = time.time()-t1
    
    if verbose:
        _logger.info("\n\n Time :{0} \n DeformerData Saved : {1}".format(elapsedA,filePath))
          

'''

mel.eval('rig_saveLoadGeometryPointFile -t "save" -file "C:/3D/geoTest.json" -mesh "{0}";'.format("pSphere1"))
mel.eval('rig_saveLoadGeometryPointFile -t "load" -file "C:/3D/geoTest.json";')

meshUtils.duplicateOrigMesh("polySurface1","pSphere1NewOrig")

v = 5 % 3
'''

#saveGeometryDataCpp("pSphere1")           
#saveGeometryData("pSphere1")