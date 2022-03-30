import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import rsTools.utils.openMaya.transform as tOMUtils
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

import rsTools.utils.scene.topNode as topUtils
from rsTools.utils.openMaya.vec2 import Vec2

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

__dataPath__ = env.get_project_show_asset_path()

def saveMeshData(transform,verbose=False):
    folder = os.path.join(__dataPath__,"data","mesh",transform,"")
    
    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topUtils.getRigBoundTopNodes()
    if topNode:
        topNode = topNode[0]
        element = cmds.getAttr(topNode+".element",asString=True)
        folder = os.path.join(__dataPath__,"data",element,"mesh",transform,"")

    
    ''' create folder '''
    t1 = time.time()
    osUtils.createDirectoryFromPath(folder)
    
    versions = array.sort(osUtils.get_subdirs(folder))
    nextVersion = "v1"
    if versions:
        nextVersion = osUtils.getFolderNextVersion(versions)
    newFolder = osUtils.createDirectory(folder,nextVersion)

    ''' set filePath '''
    filePath = os.path.join(newFolder,transform+".bin").replace("\\","/")

    mel.eval('rig_saveLoadGeometryPointFile -task "save" -file "{0}" -mesh "{1}";'.format(filePath,transform))








def loadMeshData(transform,topNode = None, version = -1,verbose=False):
    folder = os.path.join(__dataPath__,"data","mesh",transform,"")
    
    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topNode or topUtils.getRigBoundTopNodes()
    if topNode:
        if isinstance(topNode,list):
            topNode = topNode[0]
        try:
            element = cmds.getAttr(topNode+".element",asString=True)
        except:
            element = topNode.split("_")[-2]
            
        folder = os.path.join(__dataPath__,"data",element,"mesh",transform,"")

    
    if os.path.exists(folder):
        findVersion = "v"+str(version)
        versions = array.sort(osUtils.get_subdirs(folder))
        if version == -1:
            findVersion = versions[-1]
         
        data = {}
        filePath = os.path.join(folder,findVersion,transform+".bin").replace("\\","/")

        if os.path.exists(filePath):
            mesh = mel.eval('rig_saveLoadGeometryPointFile -task "load" -file "{0}";'.format(filePath))
            mesh = cmds.rename(mesh,transform)
            shader.assignObjectListToShader(mesh,"lambert1")
            return mesh
                 
    else:
        if verbose:
            _logger.error("Transform Data Doesnt Exist for Object: {0}".format(transform))