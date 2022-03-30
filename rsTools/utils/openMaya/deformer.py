import maya.cmds as cmds
import re

import rsTools.utils.openMaya.dataUtils as dUtils

import maya.OpenMayaAnim as OpenMayaAnimOld
import maya.OpenMaya as OpenMayaOld
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma


def isDeformer(deformer):
    if not cmds.objExists(deformer):
        return False
    nodeType = cmds.nodeType(deformer, i=1)
    if not nodeType.count('geometryFilter'):
        return False
    return True


'''
isDeformer("rig_normalPushq")
getDeformerList("pSphere1",nodeType='geometryFilter')
getDeformerFn("rig_normalPushq")
getDeformerSet("rig_normalPushq")
getDeformerSetFn("rig_normalPushq")
q = getDeformerSetMembers("rig_normalPushq")
p = getDeformerSetMemberStrList("rig_normalPushq")
  
s = getAffectedGeometry("rig_normalPushq")

weights = getWeights("rig_normalPushq")
'''


def getAttributes(deformer):
    attrs = cmds.listAttr(deformer, k=True)
    if "weightList.weights" in attrs:
        attrs.remove("weightList.weights")

    output = []
    for a in attrs:
        attr = str(deformer+"."+a)
        val = cmds.getAttr(attr)
        output.append([attr, val])

    return output


def getAttributesAndConnections(deformer):
    attrs = cmds.listAttr(deformer, k=True)
    if "weightList.weights" in attrs:
        attrs.remove("weightList.weights")

    output = []
    for a in attrs:
        attr = str(deformer+"."+a)
        val = cmds.getAttr(attr)

        connections = cmds.listConnections(attr, s=True, d=False, p=True)
        if connections:
            output.append([attr, val, connections[0]])
        else:
            output.append([attr, val, None])

    return output


def getDeformerList(affectedGeometry=[], nodeType='geometryFilter', regexFilter=''):
    # Get Deformer List
    deformerNodes = cmds.ls(type=nodeType)
    if affectedGeometry:
        if type(affectedGeometry) == str:
            affectedGeometry = [affectedGeometry]
        historyNodes = cmds.listHistory(
            affectedGeometry, groupLevels=True, pruneDagObjects=True)
        deformerNodes = cmds.ls(historyNodes, type=nodeType)

    # Remove Duplicates
    deformerNodes = aUtils.removeDuplicates(deformerNodes)

    # Remove Tweak Nodes
    tweakNodes = cmds.ls(deformerNodes, type='tweak')
    if tweakNodes:
        deformerNodes = [x for x in deformerNodes if not x in tweakNodes]

    # Remove TransferAttributes Nodes
    transferAttrNodes = cmds.ls(deformerNodes, type='transferAttributes')
    if transferAttrNodes:
        deformerNodes = [
            x for x in deformerNodes if not x in transferAttrNodes]

    if regexFilter:
        reFilter = re.compile(regexFilter)
        deformerNodes = filter(reFilter.search, deformerNodes)

    return deformerNodes


def listMeshDeformers(mesh):
    historyNodes = cmds.listHistory(
        mesh, groupLevels=True, pruneDagObjects=True)
    deformerNodes = cmds.ls(historyNodes, type="geometryFilter")

    # remove tweak
    deformerNodes = aUtils.removeDuplicates(deformerNodes)
    tweakNodes = cmds.ls(deformerNodes, type='tweak')
    if tweakNodes:
        deformerNodes = [x for x in deformerNodes if not x in tweakNodes]

    # remove transfer nodes
    transferAttrNodes = cmds.ls(deformerNodes, type='transferAttributes')
    if transferAttrNodes:
        deformerNodes = [
            x for x in deformerNodes if not x in transferAttrNodes]

    return deformerNodes


def getDeformerFn(deformer):
    # Checks
    if not cmds.objExists(deformer):
        raise Exception('Deformer '+deformer+' does not exist!')

    # Get MFnWeightGeometryFilter
    deformerObj = dUtils.getMObject(deformer)
    try:
        deformerFn = oma.MFnGeometryFilter(deformerObj)
    except:
        raise Exception(
            'Could not get a geometry filter for deformer "'+deformer+'"!')

    return deformerFn


def getDeformerSet(deformer):
    # Checks
    if not cmds.objExists(deformer):
        raise Exception('Deformer '+deformer+' does not exist!')
    if not isDeformer(deformer):
        raise Exception('Object '+deformer+' is not a valid deformer!')

    # Get Deformer Set
    deformerObj = dUtils.getMObject(deformer)
    deformerFn = oma.MFnGeometryFilter(deformerObj)
    deformerSetObj = deformerFn.deformerSet
    if deformerSetObj.isNull():
        raise Exception('Unable to determine deformer set for "'+deformer+'"!')

    # Return Result
    return om.MFnDependencyNode(deformerSetObj).name()


def getDeformerSetFn(deformer):
    # Checks
    if not cmds.objExists(deformer):
        raise Exception('Deformer '+deformer+' does not exist!')

    # Get deformer set
    deformerSet = getDeformerSet(deformer)

    # Get MFnWeightGeometryFilter
    deformerSetObj = dUtils.getMObject(deformerSet)
    deformerSetFn = om.MFnSet(deformerSetObj)

    # Return result
    return deformerSetFn


def getDeformerSetMembers(deformer, geometry=''):
    '''
    Return the deformer set members of the specified deformer.
    You can specify a shape name to query deformer membership for.
    Otherwise, membership for the first affected geometry will be returned.
    Results are returned as a list containing an MDagPath to the affected shape and an MObject for the affected components.
    @param deformer: Deformer to query set membership for
    @type deformer: str
    @param geometry: Geometry to query deformer set membership for. Optional.
    @type geometry: str
    '''
    # Get deformer function sets
    deformerSetFn = getDeformerSetFn(deformer)

    # Get deformer set members
    deformerSetSel = deformerSetFn.getMembers(True)

    # Get geometry index
    if geometry:
        geomIndex = getGeomIndex(geometry, deformer)
    else:
        geomIndex = 0

    # Get number of selection components
    deformerSetLen = deformerSetSel.length()
    if geomIndex >= deformerSetLen:
        raise Exception('Geometry index out of range! (Deformer: "'+deformer+'", Geometry: "' +
                        geometry+'", GeoIndex: '+str(geomIndex)+', MaxIndex: '+str(deformerSetLen)+')')

    # Get deformer set members
    data = deformerSetSel.getDagPath(geomIndex)

    # Return result
    return data


def getDeformerSetMemberStrList(deformer, geometry=''):
    '''
    Return the deformer set members of the specified deformer as a list of strings.
    You can specify a shape name to query deformer membership for.
    Otherwise, membership for the first affected geometry will be returned.
    @param deformer: Deformer to query set membership for
    @type deformer: str
    @param geometry: Geometry to query deformer set membership for. Optional.
    @type geometry: str
    '''
    # Get deformer function sets
    deformerSetFn = getDeformerSetFn(deformer)

    # Get deformer set members
    deformerSetSel = om.MSelectionList()
    deformerSetFn.getMembers(deformerSetSel, True)

    # Convert to list of strings
    setMemberStr = []
    deformerSetSel.getSelectionStrings(setMemberStr)
    setMemberStr = cmds.ls(setMemberStr, fl=True)

    # Return Result
    return setMemberStr


def getDeformerSetMemberIndices(deformer, geometry=''):

    # Check geometry
    geo = geometry
    if cmds.objectType(geometry) == 'transform':
        try:
            geometry = cmds.listRelatives(
                geometry, s=True, ni=True, pa=True)[0]
        except:
            raise Exception('Object "'+geo+'" is not a valid geometry!')
    # Get geometry type
    geometryType = cmds.objectType(geometry)

    # Get deformer set members
    deformerSetMem = getDeformerSetMembers(deformer, geometry)

    # ==========================
    # - Get Set Member Indices -
    # ==========================
    memberIdList = []

    # Single Index
    if geometryType == 'mesh' or geometryType == 'nurbsCurve' or geometryType == 'particle':
        memberIndices = om.MIntArray()
        singleIndexCompFn = om.MFnSingleIndexedComponent(deformerSetMem[1])
        singleIndexCompFn.getElements(memberIndices)
        memberIdList = list(memberIndices)

    # Double Index
    if geometryType == 'nurbsSurface':
        memberIndicesU = om.MIntArray()
        memberIndicesV = om.MIntArray()
        doubleIndexCompFn = om.MFnDoubleIndexedComponent(deformerSetMem[1])
        doubleIndexCompFn.getElements(memberIndicesU, memberIndicesV)
        for i in range(memberIndicesU.length()):
            memberIdList.append([memberIndicesU[i], memberIndicesV[i]])

    # Triple Index
    if geometryType == 'lattice':
        memberIndicesS = om.MIntArray()
        memberIndicesT = om.MIntArray()
        memberIndicesU = om.MIntArray()
        tripleIndexCompFn = om.MFnTripleIndexedComponent(deformerSetMem[1])
        tripleIndexCompFn.getElements(
            memberIndicesS, memberIndicesT, memberIndicesU)
        for i in range(memberIndicesS.length()):
            memberIdList.append(
                [memberIndicesS[i], memberIndicesT[i], memberIndicesU[i]])

    # Return result
    return memberIdList


def getAffectedGeometry(deformer, returnShapes=False, fullPathNames=False):
    # Verify Input
    if not isDeformer(deformer):
        raise Exception('Object "'+deformer+'" is not a valid deformer!')

    # Initialize Return Array (dict)
    affectedObjects = {}

    # Get MFnGeometryFilter
    deformerObj = dUtils.getMObject(deformer)
    geoFilterFn = oma.MFnGeometryFilter(deformerObj)

    # Get Output Geometry
    outputObjectArray = geoFilterFn.getOutputGeometry()
    dir(outputObjectArray)

    # Iterate Over Affected Geometry
    for i in range(len(outputObjectArray)):

        # Get Output Connection at Index
        outputIndex = geoFilterFn.indexForOutputShape(outputObjectArray[i])
        outputNode = om.MFnDagNode(om.MObject(outputObjectArray[i]))

        # Check Return Shapes
        if not returnShapes:
            outputNode = om.MFnDagNode(outputNode.parent(0))

        # Check Full Path
        if fullPathNames:
            affectedObjects[outputNode.fullPathName()] = int(outputIndex)
        else:
            affectedObjects[outputNode.partialPathName()] = int(outputIndex)

    # Return Result
    return affectedObjects


def getGeomIndex(geometry, deformer):
    '''
    Returns the geometry index of a shape to a specified deformer.
    @param geometry: Name of shape or parent transform to query
    @type geometry: str
    @param deformer: Name of deformer to query
    @type deformer: str
    '''
    # Verify input
    if not isDeformer(deformer):
        raise Exception('Object "'+deformer+'" is not a valid deformer!')

    # Check geometry
    geo = geometry
    if cmds.objectType(geometry) == 'transform':
        try:
            geometry = cmds.listRelatives(
                geometry, s=True, ni=True, pa=True)[0]
        except:
            raise Exception('Object "'+geo+'" is not a valid geometry!')
    geomObj = dUtils.getMObject(geometry)

    # Get geometry index
    deformerObj = dUtils.getMObject(deformer)
    deformerFn = oma.MFnGeometryFilter(deformerObj)
    try:
        geomIndex = deformerFn.indexForOutputShape(geomObj)
    except:
        raise Exception('Object "'+geometry +
                        '" is not affected by deformer "'+deformer+'"!')

    # Retrun result
    return geomIndex


def findInputShape(shape):
    '''
    Return the input shape ('...ShapeOrig') for the specified shape node.
    This function assumes that the specified shape is affected by at least one valid deformer.
    @param shape: The shape node to find the corresponding input shape for.
    @type shape: str
    '''
    # Checks
    if not cmds.objExists(shape):
        raise Exception('Shape node "'+shape+'" does not exist!')

    # Get inMesh connection
    inMeshConn = cmds.listConnections(
        shape+'.inMesh', source=True, destination=False, shapes=True)
    if not inMeshConn:
        return shape

    # Check direct mesh (outMesh -> inMesh) connection
    if str(cmds.objectType(inMeshConn[0])) == 'mesh':
        return inMeshConn[0]

    # Find connected deformer
    deformerObj = dUtils.getMObject(inMeshConn[0])
    if not deformerObj.hasFn(om.MFn.kGeometryFilt):
        deformerHist = cmds.ls(cmds.listHistory(shape), type='geometryFilter')
        if not deformerHist:
            print('findInputShape.py: Shape node "'+shape +
                  '" has incoming inMesh connections but is not affected by any valid deformers! Returning "'+shape+'"!')
            return shape
            #raise Exception('Shape node "'+shape+'" is not affected by any valid deformers!')
        else:
            deformerObj = dUtils.getMObject(deformerHist[0])

    # Get deformer function set
    deformerFn = oma.MFnGeometryFilter(deformerObj)

    # Get input shape for deformer
    shapeObj = dUtils.getMObject(shape)
    geomIndex = deformerFn.indexForOutputShape(shapeObj)
    inputShapeObj = deformerFn.inputShapeAtIndex(geomIndex)

    # Return result
    return om.MFnDependencyNode(inputShapeObj).name()


def renameDeformerSet(deformer, deformerSetName=''):
    '''
    Rename the deformer set connected to the specified deformer
    @param deformer: Name of the deformer whose deformer set you want to rename
    @type deformer: str
    @param deformerSetName: New name for the deformer set. If left as default, new name will be (deformer+"Set")
    @type deformerSetName: str
    '''
    # Verify input
    if not isDeformer(deformer):
        raise Exception('Object "'+deformer+'" is not a valid deformer!')

    # Check deformer set name
    if not deformerSetName:
        deformerSetName = deformer+'Set'

    # Rename deformer set
    deformerSet = cmds.listConnections(
        deformer+'.message', type='objectSet')[0]
    if deformerSet != deformerSetName:
        deformerSetName = cmds.rename(deformerSet, deformerSetName)

    # Retrun result
    return deformerSetName


def getWeights(deformer, geometry=None):
    # Check Deformer
    if not isDeformer(deformer):
        raise Exception('Object "'+deformer+'" is not a valid deformer!')

    # Check Geometry
    if not geometry:
        geometry = getAffectedGeometry(deformer).keys()[0]

    # Get Geometry Shape
    geoShape = geometry
    if geometry and cmds.objectType(geoShape) == 'transform':
        geoShape = cmds.listRelatives(geometry, s=True, ni=True)[0]

    '''
    weightList = []
    vCount = cmds.polyEvaluate(geometry,v=True)
    for i in range(vCount):
        w = cmds.getAttr("{0}.weightList[0].weights[{1}]".format(deformer,i))
        weightList.append(w)
     '''

    # get deformer set
    defomerObjOLD = dUtils.getMObjectOld(deformer)
    deformerFn = OpenMayaAnimOld.MFnGeometryFilter(defomerObjOLD)
    deformerSetObj = deformerFn.deformerSet()
    deformerSetName = OpenMayaOld.MFnDependencyNode(deformerSetObj).name()

    deformerSetObj = dUtils.getMObjectOld(deformerSetName)
    deformerSetFn = OpenMayaOld.MFnSet(deformerSetObj)

    deformerSetSel = OpenMayaOld.MSelectionList()
    deformerSetFn.getMembers(deformerSetSel, True)
    deformerSetPath = OpenMayaOld.MDagPath()
    deformerSetComp = OpenMayaOld.MObject()
    deformerSetSel.getDagPath(0, deformerSetPath, deformerSetComp)

    # Get weights
    deformerFn = OpenMayaAnimOld.MFnWeightGeometryFilter(defomerObjOLD)
    weightList = OpenMayaOld.MFloatArray()
    deformerFn.getWeights(deformerSetPath, deformerSetComp, weightList)

    # Return result
    return list(weightList)


def setWeights(deformer, weights, geometry=None):
    # Check Deformer
    if not isDeformer(deformer):
        raise Exception('Object "'+deformer+'" is not a valid deformer!')

    # Check Geometry
    if not geometry:
        geometry = getAffectedGeometry(deformer).keys()[0]

    # Get Geometry Shape
    geoShape = geometry
    if geometry:
        geoShape = cmds.listRelatives(geometry, s=True, ni=True)[0]

    # Build weight array
    weightList = OpenMayaOld.MFloatArray()
    [weightList.append(i) for i in weights]

    defomerObjOLD = dUtils.getMObjectOld(deformer)

    # get deformer set
    deformerFn = OpenMayaAnimOld.MFnGeometryFilter(defomerObjOLD)
    deformerSetObj = deformerFn.deformerSet()
    deformerSetName = OpenMayaOld.MFnDependencyNode(deformerSetObj).name()

    deformerSetObj = dUtils.getMObjectOld(deformerSetName)
    deformerSetFn = OpenMayaOld.MFnSet(deformerSetObj)

    deformerSetSel = OpenMayaOld.MSelectionList()
    deformerSetFn.getMembers(deformerSetSel, True)
    deformerSetPath = OpenMayaOld.MDagPath()
    deformerSetComp = OpenMayaOld.MObject()
    deformerSetSel.getDagPath(0, deformerSetPath, deformerSetComp)

    deformerFn = OpenMayaAnimOld.MFnWeightGeometryFilter(defomerObjOLD)
    deformerFn.setWeight(deformerSetPath, deformerSetComp, weightList)


def bindPreMatrix(deformer, bindPreMatrix='', parent=True):
    '''
    Create a bindPreMatrix transform for the specified deformer.
    @param deformer: Deformer to create bind pre matrix transform for
    @type deformer: str
    @param bindPreMatrix: Specify existing transform for bind pre matrix connection. If empty, create a new transform
    @type bindPreMatrix: str
    @param parent: Parent the deformer handle to the bind pre matrix transform
    @type deformer: bool
    '''
    # Check deformer
    if not isDeformer(deformer):
        raise Exception('Object "'+deformer+'" is not a valid deformer!')
    if not cmds.objExists(deformer+'.bindPreMatrix'):
        raise Exception('Deformer "'+deformer +
                        '" does not accept bindPreMatrix connections!')

    # Get deformer handle
    deformerHandle = cmds.listConnections(deformer+'.matrix', s=True, d=False)
    if deformerHandle:
        deformerHandle = deformerHandle[0]
    else:
        raise Exception('Unable to find deformer handle!')

    # Check bindPreMatrix
    if bindPreMatrix:
        if not cmds.objExists(bindPreMatrix):
            bindPreMatrix = cmds.createNode('transform', n=bindPreMatrix)
    else:
        # Build bindPreMatrix transform
        prefix = deformerHandle.replace(deformerHandle.split('_')[-1], '')
        bindPreMatrix = cmds.createNode('transform', n=prefix+'bindPreMatrix')

    # Match transform and pivot
    cmds.xform(bindPreMatrix, ws=True, matrix=cmds.xform(
        deformerHandle, q=True, ws=True, matrix=True))
    cmds.xform(bindPreMatrix, ws=True, piv=cmds.xform(
        deformerHandle, q=True, ws=True, rp=True))

    # Connect inverse matrix to localize cluster
    cmds.connectAttr(
        bindPreMatrix+'.worldInverseMatrix[0]', deformer+'.bindPreMatrix', f=True)

    # Parent
    if parent:
        cmds.parent(deformerHandle, bindPreMatrix)

    # Return result
    return bindPreMatrix


def pruneWeights(deformer, geoList=[], threshold=0.001):
    '''
    Set deformer component weights to 0.0 if the original weight value is below the set threshold
    @param deformer: Deformer to removed components from
    @type deformer: str
    @param geoList: The geometry objects whose components are checked for weight pruning
    @type geoList: list
    @param threshold: The weight threshold for removal
    @type threshold: str
    '''
    # Check deformer
    if not cmds.objExists(deformer):
        raise Exception('Deformer "'+deformer+'" does not exist!')

    # Check geometry
    if type(geoList) == str:
        geoList = [geoList]
    if not geoList:
        geoList = cmds.deformer(deformer, q=True, g=True)
    if not geoList:
        raise Exception('No geometry to prune weight for!')
    for geo in geoList:
        if not cmds.objExists(geo):
            raise Exception('Geometry "'+geo+'" does not exist!')

    # For each geometry
    for geo in geoList:

        # Get deformer member indices
        memberIndexList = getDeformerSetMemberIndices(deformer, geo)

        # Get weight list
        weightList = getWeights(deformer, geo)

        # Prune weights
        pWeightList = [wt if wt > threshold else 0.0 for wt in weightList]

        # Apply pruned weight list
        setWeights(deformer, pWeightList, geo)


def pruneMembershipByWeights(deformer, geoList=[], threshold=0.001):
    '''
    Remove components from a specified deformer set if there weight value is below the set threshold
    @param deformer: Deformer to removed components from
    @type deformer: str
    @param geoList: The geometry objects whose components are checked for removal
    @type geoList: list
    @param threshold: The weight threshold for removal
    @type threshold: str
    '''
    # Check deformer
    if not cmds.objExists(deformer):
        raise Exception('Deformer "'+deformer+'" does not exist!')

    # Check geometry
    if type(geoList) == str:
        geoList = [geoList]
    if not geoList:
        geoList = cmds.deformer(deformer, q=True, g=True)
    if not geoList:
        raise Exception('No geometry to prune weight for!')
    for geo in geoList:
        if not cmds.objExists(geo):
            raise Exception('Geometry "'+geo+'" does not exist!')

    # Get deformer set
    deformerSet = getDeformerSet(deformer)

    # For each geometry
    allPruneList = []
    for geo in geoList:

        # Get Component Type
        geoType = glTools.utils.geometry.componentType(geo)

        # Get Deformer Member Indices
        memberIndexList = getDeformerSetMemberIndices(deformer, geo)

        # Get Weights
        weightList = getWeights(deformer, geo)

        # Get Prune List
        pruneList = [memberIndexList[i] for i in range(
            len(memberIndexList)) if weightList[i] <= threshold]
        for i in range(len(pruneList)):
            if type(pruneList[i]) == str or type(pruneList[i]) == unicode or type(pruneList[i]) == int:
                pruneList[i] = '['+str(pruneList[i])+']'
            elif type(pruneList[i]) == list:
                pruneList[i] = [str(p) for p in pruneList[i]]
                pruneList[i] = '['+']['.join(pruneList[i])+']'
            pruneList[i] = geo+'.'+geoType+str(pruneList[i])
        allPruneList.extend(pruneList)

        # Prune deformer set membership
        if pruneList:
            cmds.sets(pruneList, rm=deformerSet)

    # Return prune list
    return allPruneList


def clean(deformer, threshold=0.001):
    '''
    Clean specified deformer.
    Prune weights under the given tolerance and prune membership.
    @param deformer: The deformer to clean. 
    @type deformer: str
    @param threshold: Weight value tolerance for prune operations.
    @type threshold: float
    '''
    # Print Message
    print('Cleaning deformer: '+deformer+'!')

    # Check Deformer
    if not isDeformer(deformer):
        raise Exception('Object "'+deformer+'" is not a valid deformer!')

    # Prune Weights
    glTools.utils.deformer.pruneWeights(deformer, threshold=threshold)
    # Prune Membership
    glTools.utils.deformer.pruneMembershipByWeights(
        deformer, threshold=threshold)


def checkMultipleOutputs(deformer, printResult=True):
    '''
    Check the specified deformer for multiple ouput connections from a single plug.
    @param deformer: Deformer to check for multiple output connections
    @type deformer: str
    @param printResult: Print results to the script editor
    @type printResult: bool
    '''
    # Check deformer
    if not isDeformer(deformer):
        raise Exception('Deformer "'+deformer+'" is not a valid deformer!')

    # Get outputGeometry plug
    outGeomPlug = glTools.utils.attribute.getAttrMPlug(
        deformer+'.outputGeometry')
    if not outGeomPlug.isArray():
        raise Exception('Attribute "'+deformer +
                        '.outputGeometry" is not an array attribute!')

    # Get existing indices
    indexList = om.MIntArray()
    numIndex = outGeomPlug.getExistingArrayAttributeIndices(indexList)

    # Check output plugs
    returnDict = {}
    for i in range(numIndex):
        plugConn = cmds.listConnections(
            deformer+'.outputGeometry['+str(indexList[i])+']', s=False, d=True, p=True)

        # Check multiple outputs
        if len(plugConn) > 1:
            # Append to return value
            returnDict[deformer+'.outputGeometry[' +
                       str(indexList[i])+']'] = plugConn
            # Print connection info
            if printResult:
                print('Deformer output "'+deformer+'.outputGeometry['+str(
                    indexList[i])+']" has '+str(len(plugConn))+' outgoing connections:')
                for conn in plugConn:
                    print('\t- '+conn)

    # Return result
    return returnDict
