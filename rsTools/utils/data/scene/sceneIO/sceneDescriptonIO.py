import maya.cmds as cmds
import rsTools.utils.data.osUtils as osUtils
import os,cPickle,time
import rsTools.utils.data.scene.topNode as topUtils
__dataPath__ = osUtils.get_project_show_asset_path()


def saveSceneTransformDescriptionData(topNode=None,verbose=True):
    t1 = time.time()
    folder = os.path.join(__dataPath__,"data","scene","")
    
    ''' do a topNode check to make sure we are saving per asset LOD'''
    topNode = topNode or topUtils.getRigBoundTopNodes()
    if topNode:
        topNode = topNode[0]
        element = cmds.getAttr(topNode+".element",asString=True)
        folder = os.path.join(__dataPath__,"data",element,"scene","")

    ''' create folder '''
    t1 = time.time()
    osUtils.createDirectoryFromPath(folder)
    
    versions = array.sort(osUtils.getSubdirs(folder))
    nextVersion = "v1"
    if versions:
        nextVersion = osUtils.getFolderNextVersion(versions)
    newFolder = osUtils.createDirectory(folder,nextVersion)

    ''' set filePath '''
    filePath = os.path.join(newFolder,"sceneTransformDescription.json").replace("\\","/")

    ''' create tree and all data'''
    tree = {}
    sceneUtils.buildHierarchyTree(topNode, tree)   
    
    ''' save out tree to disk '''
    osUtils.saveJson(filePath,tree)
    
    tEnd = time.time() - t1
    
    _logger.info("TreeData for {0} in : {1}".format(topNode,tEnd))
 
 
 
def loadSceneTransformDescriptionData(topNode=None,version = -1,verbose=True):
    t1 = time.time()
    folder = os.path.join(__dataPath__,"data","scene","")
    
    ''' do a topNode check to make sure we are saving per asset LOD'''
    if topNode is None:
        topNode =  topUtils.getRigBoundTopNodes();
        topNode = topNode[0]
        element = cmds.getAttr(topNode+".element",asString=True)
        folder = os.path.join(__dataPath__,"data",element,"scene","")
    else:
        element = topNode.split("_")[-2]
        folder = os.path.join(__dataPath__,"data",element,"scene","")
  
    ''' make sure folder exists '''
    if not os.path.exists(folder):
        return
        
    ''' find correct version '''
    findVersion = "v"+str(version)
    versions = array.sort(osUtils.getSubdirs(folder))
    if version == -1:
        findVersion = versions[-1]
         
    data = {}
    filePath = os.path.join(folder,findVersion,"sceneTransformDescription.json").replace("\\","/")

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

def buildSceneFromDescription(topNode=None,
                project=None,
                asset=None,
                rigBoundElement=None,
                version = -1,verbose=True):
    
    project = project or osUtils.get_project_show()
    asset = asset or osUtils.get_project_show_asset()
    rigBoundElement = rigBoundElement or str(asset[4:].lower()+"ALODa")
    topNode = topNode or project+"_rigBound_"+rigBoundElement+"_GRP"   
        
    print topNode
    ''' build all transform items '''
    data = loadSceneTransformDescriptionData(topNode)
    print data
    sceneUtils.buildTreeData(topNode,data)
    
    ''' load constraints POST TREE '''
    print "BUILDING CONSTRAINTS"
    __constraints__ = ["parentConstraint","pointConstraint","orientConstraint"]
    
    for con in __constraints__:
        result = []
        sceneUtils.flattenTreeByNodeType(con,data,result)
        
        print result
        
        if result:
            for r in result:
                conOI.loadConstraintData(r,topNode)

def objectType(obj):
    if cmds.objExists(obj):
        tempType = cmds.objectType(obj)
        shp = cmds.listRelatives(obj, s=True)
        if shp:
            tempType = cmds.objectType(shp[0])
    return tempType    
 
#buildSceneFromDescription()
 
    
#saveSceneTransformDescriptionData()


'''
things to add:]

CTRL data saver / drawOverride + color





'''





