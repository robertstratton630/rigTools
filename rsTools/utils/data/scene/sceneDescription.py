import maya.cmds as cmds
import rsTools.utils.data.osUtils as osUtils
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.data.curveData as curveData
import logging,os
import rsTools.utils.data.osUtils as osUtils


import rsTools.utils.data.scene.topNode as topUtils
import rsTools.utils.string as sUtils
from rsTools.core.skeleton.skeletonAsset import SkeletonAsset
from rsTools.core.model.modelAsset import ModelAsset
from rsTools.core.deformation.rigBoundBase import RigBoundBase
from rsTools.utils import  catch

from rsTools.utils.nodes.interpolationJoint import InterpolationJoint
from rsTools.utils.nodes.twistChain import TwistChain

import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.openMaya.dataUtils as dataUtils
import rsTools.utils.openMaya.deformer as defUtils

import rsTools.utils.data.IO.transformSaveLoad as tOI
import rsTools.utils.data.IO.nurbsControlSaveLoad as cOI
import rsTools.utils.data.IO.constraintSaveLoad as conOI
import rsTools.utils.data.IO.graphDescriptionIO as graphOI
import rsTools.utils.nodes.constraints as conUtils
import rsTools.utils.data.scene.sceneIO.meshIO as meshIO

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)



def getModelReleaseMeshes():
    topNode = topUtils.getRigBoundTopNodes()
    
    if topNode:
        topNode = topNode[0]
        version = cmds.getAttr(topNode+".modelVersion",asString=True)
        element = cmds.getAttr(topNode+".modelElement",asString=True)
        path = os.path.join(osUtils.get_project_show_asset_path(),"release","model",element,version,"metaData.json")
        if os.path.exists(path):
            data = osUtils.loadJson(path)
            geometry = data["geometryCacheItems"]
            keys = geometry.keys()
            keys = [k.split("Shape")[0] for k in keys]
            return keys
    return ""
    
__constraints__ = ["parentConstraint","pointConstriant","orientConstraint"]
__modelRelease__ = getModelReleaseMeshes()

def buildHierarchyTree(topNode, tree = {},startIter=0,saveData=True):
    if startIter == 0:
        tOI.saveTransformAttributeData(str(topNode))
    
    children = cmds.listRelatives(topNode, c=True, type='transform')
    if children:
        childrenData=[]
        for c in children:     
            
            if saveData:
                ''' save transform attributes '''
                childrenData.append(getTransformData(c))
                tOI.saveTransformAttributeData(str(c))
                
                ''' special case to save out control shapes '''
                sufix = sUtils.getSuffix(c)
                if sufix == "CTRL" and objectType(str(c)) == "nurbsCurve":
                    cOI.saveControlData(str(c))
                    
                elif conUtils.isConstraint(c):
                    conOI.saveConstraintData(c)
    
                elif meshUtils.isMesh(c):
                    meshIO.saveMeshData(c)
                    
        # store all the children data
        tree[topNode] = (childrenData, {})
        for child in children:
            buildHierarchyTree(child, tree[topNode][1],startIter+1)
            
def flattenTreeByNodeType(nodeType,tree={},filtered=[]):
    for k, v in tree.iteritems():
        childrenNodes = v[0]
        childrenDicts = v[1]
        for nodeData in childrenNodes:
            transform = nodeData["name"]
            nodeTypeChild = str(nodeData["nodeType"])
                    
            if str(nodeType) == str(nodeTypeChild):
                filtered.append(transform)
            
        flattenTreeByNodeType(nodeType,childrenDicts,filtered)
    




def buildTreeData(actualTopNode,treeData = {},startIter=0,filterByType=None,parentNode=None):   

    if startIter == 0:
        parentNode = str(treeData.keys()[0])
        tUtils.transformCreateFromName(parentNode)
        tOI.loadTransformAttributeData(parentNode,actualTopNode,verbose=False)
    
    for k, v in treeData.iteritems():
        childrenNodes = v[0]
        childrenDicts = v[1]
        
        ''' create clean next level dict based on filters '''
   
        
        # build all children nodes
        for i,nodeData in enumerate(childrenNodes):
            transform = nodeData["name"]
            nodeType = nodeData["nodeType"]
            suffix = sUtils.getSuffix(transform)
            
            if not cmds.objExists(transform):
                ''' skip if constraint node '''
                if nodeType in __constraints__:
                    continue
                
                ''' if filter by type, if bad match then pop off tree '''
                if filterByType is not None:
                    if nodeType not in filterByType:
                        childrenDicts.pop(transform, None)
                        continue
                        
                ''' we good, lets build the transforms '''
                if str(nodeType) == "nurbsCurve" and str(suffix) == "CTRL":
                    control = cOI.loadControlData(str(transform),actualTopNode)
                    control = cmds.parent(control,k)[0]
                  
                elif nodeType == "mesh":
                    mesh = meshIO.loadMeshData(str(transform),actualTopNode)
                    if mesh:
                        cmds.parent(mesh,k)[0]    
                else:
                    tUtils.transformCreateFromName(transform,parent=k)
            
            ''' still try to load data if the item exists tho '''
            tOI.loadTransformAttributeData(transform,actualTopNode)
            
        
        #build sub tree
        buildTreeData(actualTopNode,childrenDicts,startIter+1,parentNode = parentNode)
        
    
def getSubTree(topNode,tree = {}):
    for k, v in tree.iteritems():
        childrenNodes = v[0]
        childrenDict = v[1]
        
        if topNode in childrenNodes:
            return childrenDict
        else:
            getSubTree(topNode,childrenDict)
    return False

def transformExistsInTree(topNode,tree = {}):
    for k, v in tree.iteritems():
        childrenNodes = v[0]
        childrenDict = v[1]
        
        if topNode in childrenNodes:
            return True
        else:
            getSubTree(topNode,childrenDict)
    return False

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
    
def getAllCustomMeshes():
    topNode = topUtils.getRigBoundTopNodes()
    
    if topNode:
        topNode = topNode[0]
        version = cmds.getAttr(topNode+".modelVersion",asString=True)
        element = cmds.getAttr(topNode+".modelElement",asString=True)
        
        allMeshesInScene = [item for item in cmds.ls(typ="transform") if objectType(item) == "mesh"]
    
        path = os.path.join(osUtils.get_project_show_asset_path(),"release","model",element,version,"metaData.json")
        if os.path.exists(path):
            data = osUtils.loadJson(path)
            geometry = data["geometryCacheItems"]
            keys = geometry.keys()
            keys = [k.split("Shape")[0] for k in keys]
            allMeshesInScene = [item for item in allMeshesInScene if item not in keys]
            
            return allMeshesInScene
            
    return None
 
 

def removeModelReleaseMeshes(meshes):
    output = []
    modelRelease = getModelReleaseMeshes()
    output = [item for item in meshes if item not in modelRelease]
    return output
            
'''
            
myprint(hierarchy_tree)                  

top_node = 'library_rigBound_bearALODa_GRP'  
hierarchy_tree = {}
hierarchyTree(top_node, hierarchy_tree)   


hierarchy_tree.items


'''

#tree = {}
#buildOutputsConnectionTree("l_legUpperTwistJC_JNT",tree)

def buildOutputsConnectionTree(topNode, tree = {},allNodes=[],startIter=0):
    
    ___ignores___ = ["dagPose","shadingEngine","lambert","blinn","nodeGraphEditorInfo"]
    childrenData=[]
    childrenNodes=[]
     
    outputConnections = cmds.listConnections(topNode,s=0,d=1,p=1) 
    if outputConnections:
        for s in outputConnections:   
            # skip unit conversions
            if objectType(s) == "unitConversion":
                try:
                    s = cmds.listConnections(s.split(".")[0],s=0,d=1,p=1)[0]
                except:
                    continue
                    
            if defUtils.isDeformer(s):
                continue
                
            if cmds.objectType(s) in ___ignores___:
                continue
                
                
            '''split into node and attr '''
            split = s.split(".")
            outputTransform = split[0]
            outputTransformAttr = split[1]
            theSourceAttr = cmds.listConnections(s,s=1,d=0,p=1)[0]
            
            ''' make sure to skip source conversions'''
            if objectType(theSourceAttr) == "unitConversion":
                theSourceAttr = cmds.listConnections(theSourceAttr.split(".")[0],s=1,d=0,p=1)[0]

            ''' check to make sure we dont get into infinite loop if cycle '''
            if outputTransform in allNodes:
                count = allNodes.count(outputTransform)
                if count >= 2:
                    continue
            
            data = {}
            data["name"] = str(outputTransform)
            data["nodeType"] = objectType(outputTransform)
            data["targetAttribute"] = s
            data["sourceAttribute"] = theSourceAttr
            childrenData.append(data)
            childrenNodes.append(outputTransform)

    # store all the children data
    tree[topNode] = (childrenData, {})
    for child in childrenNodes:
        buildOutputsConnectionTree(child, tree[topNode][1],allNodes = allNodes+[topNode], startIter = startIter+1)
   


#buildOutputsConnectionFromTree("l_legUpperTwistJC_JNT",tree)
def buildOutputsConnectionFromTree(actualTopNode, tree = {},startIter=0):    
    for k, v in tree.iteritems():
        childrenNodes = v[0]
        childrenDicts = v[1]
        ''' create clean next level dict based on filters '''
   
        
        # build all children nodes
        for i,data in enumerate(childrenNodes):
            node = data["name"]
            nodeType = data["nodeType"]
            attr = data["targetAttribute"]
            sourceAttr = data["sourceAttribute"]
            
            if not cmds.objExists:
                node = cmds.createNode(node,typ=nodeType)
                
            conTest = cmds.listConnections(node+"."+attr,s=1,d=0)
            
            try:
                cmds.connectAttr(sourceAttr,node+"."+attr)
            except:
                pass
  
        #build sub tree
        buildOutputsConnectionFromTree(actualTopNode,childrenDicts,startIter+1)

