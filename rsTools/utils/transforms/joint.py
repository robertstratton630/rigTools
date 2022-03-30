import maya.cmds as cmds
import maya.OpenMaya as om

import rsTools.utils.string as sUtil
import maya.cmds as cmds
import rsTools.utils.openMaya.dataUtils as dataUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mathUtils as mathUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.openMaya.vector as vUtils



import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

def isJoint(joint):

	# Check object exists
	if not cmds.objExists(joint): return False
	
	# Check joint
	if not cmds.ls(type='joint').count(joint): return False
	
	# Return result
	return True

def isEndJoint(joint):
    # Check Joint
    if not isJoint(joint):
        raise Exception('Object "'+joint+'" is not a valid joint!')

    # Check Child Joints
    jointDescendants = cmds.ls(cmds.listRelatives(joint,ad=True) or [],type='joint')
    if not jointDescendants:
        return True
    else:
        return False

def getEndJoint(startJoint,includeTransforms=False):
    '''
    Find the end joint of a chain from the specified start joint.
    @param joint: Joint to find end joint from
    @type joint: str
    @param includeTransforms: Include non-joint transforms in the chain.
    @type includeTransforms: bool
    '''
    # Check Start Joint
    if not cmds.objExists(startJoint):
        raise Exception('Start Joint "'+startJoint+'" does not exist!')

    # Find End Joint
    endJoint = None
    nextJoint = startJoint
    while(nextJoint):
        
        # Get Child Joints
        childList = cmds.listRelatives(nextJoint,c=True) or []
        childJoints = cmds.ls(childList,type='joint') or []
        if includeTransforms:
            childJoints = list(set(childJoints + cmds.ls(childList,transforms=True) or []))
        
        # Check End Joint
        if childJoints:
            nextJoint = childJoints[0]
        else:
            endJoint = nextJoint
            nextJoint = None

    # Return Result	
    return endJoint
    
def getJointList(startJoint,endJoint):
    '''return a list representing the chain between a given start and end joint'''
    allParents = cmds.listRelatives(endJoint,p=True,f=True)
    if not allParents:
        raise RuntimeError("'%s' has no parents, not part of chain." % endJoint)
        
    parList = allParents[0].split('|')
    if not startJoint in parList:
        raise RuntimeError("'%s' not a parent of '%s'" % (startJoint,endJoint))
    startIndex = parList.index(startJoint)
    jointList = parList[startIndex:]
    jointList.append(endJoint)
    return jointList
 
    
def getChainLength(startJoint,endJoint):
    '''given a start and end joint return the length of the chain.'''
    joints=getJointList(startJoint,endJoint)
    distance=0.0
    for idx,joint in enumerate(joints):
        if idx==0:
            continue
        par=Vector(joints[idx-1])
        cur=Vector(joint)
        distance+=(par-cur).length()
    return distance
    
    
def getJointChain(startJoint,debug=False):
    al = list()

    al = cmds.listRelatives(startJoint,ad=True,type="joint",f=True)
    al.append(startJoint)
    al.reverse()
    return al
      
def rotToOrient(jnt):
    '''copy rotation to orient, zeroes the joint basically'''
    #first get everything into rot
    orientToRot(jnt)
    
    oldOrder = cmds.getAttr(jnt + ".rotateOrder")
    rotOrders = ['xyz','yzx','zxy','xzy','yxz','zyx']
    cmds.xform(jnt,p=True,roo='xyz')
    oldRot = cmds.getAttr(jnt + ".rotate")[0]
    
    cmds.setAttr(jnt + ".jointOrient",oldRot[0],oldRot[1],oldRot[2])
    cmds.setAttr(jnt + ".rotate",0,0,0)
    
    cmds.xform(jnt,p=True,roo=rotOrders[oldOrder])
    
def orientToRot(jnt):
    '''copy orient to rotation'''
    mat = omUtils.getMatrix(jnt)
    rot = mUtils.getRotation(mat,rotationOrder='xyz')
    print rot

    cmds.setAttr(jnt + '.jointOrient',0,0,0)
    cmds.xform(jnt,ws = True,ro=(rot))

def crossProduct(objA, objB, objC):
	
    cross=[0, 0, 0]
    if objA == "" or objB == "" or objC == "" or cmds.objExists(objA) != True or cmds.objExists(objB) != True or cmds.objExists(objC) != True:
        return cross
        
    posA=cmds.xform(objA, q=1, rp=1, ws=1)
    posB=cmds.xform(objB, q=1, rp=1, ws=1)
    posC=cmds.xform(objC, q=1, rp=1, ws=1)
    v1=Vector(posA[0] - posB[0], posA[1] - posB[1], posA[2] - posB[2])
    v2=Vector(posC[0] - posB[0], posC[1] - posB[1], posC[2] - posB[2])

    vC= v1.cross(v2)
    vC.normalize()

    # normalize
    cross[0]=vC.x
    cross[1]=vC.y
    cross[2]=vC.z

    return cross

def orientJoint(joint,aimAxis='y',upAxis='x',upVec=(0,1,0)):

    # Check joint
    if not cmds.objExists(joint):
        raise Exception('Joint "'+joint+'" does not exist!')
	
    # Get joint child list
    childList = cmds.listRelatives(joint,c=1)
    childJointList = cmds.listRelatives(joint,c=1,type='joint',pa=True)
	
    # Unparent children
    if childList: childList = cmds.parent(childList,w=True)
	
    # Orient joint
    if not childJointList:
        cmds.setAttr(joint+'.jo',0,0,0)
		
    else:
        
        # Get parent joint matrix
        pMat = om.MMatrix()
        pJoint = cmds.listRelatives(joint,p=True,pa=True)
        print pJoint
        if pJoint: pMat = omUtils.getMatrix(pJoint[0])
        
        print pMat
        
        # Calculate aim vector
        p1 = mathUtils.getPosition(joint)
        p2 = mathUtils.getPosition(childJointList[0])
        aimVec = mathUtils.offsetVector(p1,p2)
        
        # Build target matrix
        tMat = mUtils.buildRotation(aimVec,upVec,aimAxis,upAxis)
        
        # Calculate orient matrix
        oriMat = tMat * pMat.inverse()
        
        # Extract joint orient values
        rotOrder = cmds.getAttr(joint+'.ro')
        oriRot = mUtils.getRotation(oriMat,rotOrder)
        
        # Reset joint rotation and orientation
        cmds.setAttr(joint+'.r',0,0,0)
        cmds.setAttr(joint+'.jo',oriRot[0],oriRot[1],oriRot[2])
        print "DONE"
		
	# Reparent children
    if childList: cmds.parent(childList,joint)

def orientChain(jointRoot,upAxis="-z",aimAxis = "y",upDir=(0,1,0)):
    side = sUtil.getSide(jointRoot)
    if side:
        if side=="l":
            aimAxis = "-y"
        else:
            aimAxis = "y"
        
    chain = getJointChain(jointRoot)
    print chain,aimAxis,upAxis
    
    for j in chain:
        print j
        orientJoint(str(j), aimAxis, upAxis, upDir)

def orientMatch(joint,target):

    # Check joint
    if not cmds.objExists(joint):
        raise Exception('Joint "'+joint+'" does not exist!')
    # Check target
    if not cmds.objExists(target):
        raise Exception('Target transform "'+target+'" does not exist!')

    # Unparent children
    childList = cmds.listRelatives(joint,c=1,type=['joint','transform'])
    if childList: childList = cmds.parent(childList,w=True)

    # Get parent joint matrix
    pMat = om.MMatrix()
    pJoint = cmds.listRelatives(joint,p=True,pa=True)
    if pJoint: pMat = omUtils.getMatrix(pJoint[0])

    # Get target matrix
    tMat = omUtils.getMatrix(target)

    # Calculate orient matrix
    oriMat = tMat * pMat.inverse()

    # Extract joint orient values
    rotOrder = cmds.getAttr(joint+'.ro')
    oriRot = mUtils.getRotation(oriMat,rotOrder)

    # Reset joint rotation and orientation
    cmds.setAttr(joint+'.r',0,0,0)
    cmds.setAttr(joint+'.jo',oriRot[0],oriRot[1],oriRot[2])
	
    # Reparent children
    if childList:
        cmds.parent(childList,joint)
    
    cmds.select(joint,r=True)

def flipOrient(joint,rollAxis):
    
    if isinstance(joint,unicode):
        joint = str(joint)
    if isinstance(joint,str):
        # Check Joint
        if not cmds.objExists(joint):
            raise Exception('Joint "'+joint+'" does not exist!')

        # Check Roll Axis
        if not ['x','y','z'].count(rollAxis):
            raise Exception('Invalid roll axis "'+rollAxis+'"!')

        # UnParent Children
        childList = cmds.listRelatives(joint,c=True)
        if childList: cmds.parent(childList,w=True)

        # ReOrient Joint
        rt = [0,0,0]
        axisDict = {'x':0,'y':1,'z':2}
        rt[axisDict[rollAxis]] = 180
        cmds.setAttr(joint+'.r',*rt)
        cmds.makeIdentity(joint,apply=True,t=True,r=True,s=True)

        # Reparent children
        if childList: cmds.parent(childList,joint)
        cmds.select(joint,r=True)
    else:
        for j in joint:
            flipOrient(j,rollAxis)
            
def mirrorOrient(obj,rollAxis="x"):
    mirror = sUtil.getNameMirror(obj)
    flipOrient(mirror,rollAxis)
        
def createJointAtObject(obj,r=False):
    if obj:
        if isinstance(obj,str or unicode):
            cmds.select(cl=True)
            j = cmds.joint()        
            mat = omUtils.getMatrix(obj)
            mUtils.matchTransformToMatrix(j,mat,r=r)
            return j
        
        else:
            print "LIST"
            cmds.select(cl=True)
            joints= []
            print obj
            
            for item in obj:
                print item
                j = createJointAtObject(str(item),r)
                joints.append(j)
                
            return joints
            
    return None
    
def createJointBetweenTwoObjects(objA,objB,numJoints):
    if cmds.objExists(objA) and cmds.objExists(objB):
            
        xformA = cmds.xform(objA,q=True,ws=True,t=True)
        xformB = cmds.xform(objB,q=True,ws=True,t=True)
        
        vecA = om.MVector(xformA[0],xformA[1],xformA[2])
        vecB = om.MVector(xformB[0],xformB[1],xformB[2])
        
        vecC = vUtils.blend(vecA,vecB,0.5)
        
        cmds.select(cl=True)
        param  = 1.0/(numJoints-1)
        step = 0
        joints=[]
        for i in range (numJoints):
            vec = vUtils.blend(vecA,vecB,step)
            j = cmds.joint(p=(vec.x,vec.y,vec.z))
            joints.append(j)
            step += param
            
            
        orientChain(joints[0])
        






def createJointAlongCurve(curve,numJoints):
    curveShape = cmds.listRelatives(curve,s=1)
    dagPath = dataUtils.getDagPath(curve)
    crvFn = om.MFnNurbsCurve(dagPath)

    cmds.select(cl=True)
    param  = (1.0/(numJoints-1))
    step = 0
    joints=[]
    for i in range(numJoints):
        parameter = crvFn.findParamFromLength(crvFn.length() * (i*param))
        point = om.MPoint()
        crvFn.getPointAtParam(parameter, point)
        jnt = cmds.joint()
        cmds.xform(jnt,ws=True,t=[point.x,point.y,point.z])
        joints.append(jnt)
        step += param
        
    orientChain(joints[0])
    return joints

def duplicateJoint(joint,name=None):
	# Check Joint
	if not cmds.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	if not name: name = joint+'_dup'
	if cmds.objExists(str(name)):
		raise Exception('Joint "'+name+'" already exist!')
	
	# Duplicate Joint
	dupJoint = cmds.duplicate(joint,po=True)[0]
	if name: dupJoint = cmds.rename(dupJoint,name)
	
	# Unlock Transforms
	for at in ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radius']:
		cmds.setAttr(dupJoint+'.'+at,l=False,cb=True)
	
	# Return Result
	return dupJoint
    
def duplicateChain(	startJoint,
					endJoint	= None,
					parent		= None,
					prefix		= None,
                    baseAppendName = None	):
	# Check Joints
    if not cmds.objExists(startJoint):
        raise Exception('Start Joint "'+startJoint+'" does not exist!')
    if endJoint and not cmds.objExists(str(endJoint)):
        raise Exception('End Joint "'+endJoint+'" does not exist!')

    # Check Parent
    if parent:
        if not cmds.objExists(parent):
            raise Exception('Specified parent transform "'+parent+'" does not exist!')
	
    # Get Full Joint List
    if not endJoint: 
        endJoint = getEndJoint(startJoint)
    joints = getJointList(startJoint,endJoint)
		
    dupChain = []
    for i in range(len(joints)):
        
        side = prefix or sUtil.getSide(joints[0])
        base = sUtil.getBase(joints[0])
        suffix = sUtil.getSuffix(joints[0])
        
        if baseAppendName:
            base += baseAppendName
            
        name = sUtil.nameBuild(side,base,suffix)
        
        # Duplicate Joint
        jnt = duplicateJoint(joints[i],name)

        # Parent Joint
        if not i:
            if not parent:
                if cmds.listRelatives(jnt,p=True):
                    try: cmds.parent(jnt,w=True)
                    except: pass
            else:
                try: cmds.parent(jnt,parent)
                except: pass
        else:
            try:
                cmds.parent(jnt,dupChain[-1])
                if not cmds.isConnected(dupChain[-1]+'.scale',jnt+'.inverseScale'):
                    cmds.connectAttr(dupChain[-1]+'.scale',jnt+'.inverseScale',f=True)
            except Exception, e:
                raise Exception('Error duplicating joint chain! Exception Msg: '+str(e))
            
        # Append to list
        dupChain.append(jnt)
        
        return dupChain

def renameChain(rootJoint,prefix=None,coreName=None,suffix="JNT"):
    chain = getJointChain(rootJoint)
    
    joints=[]
    if coreName:

        for i in range(len(chain)):
            alpha = sUtil.alpha(i).capitalize()
            name = sUtil.nameBuild(prefix,coreName+"J"+alpha,suffix)
            nameEnd = sUtil.nameBuild(prefix,coreName+"JEnd",suffix)
            # just append renamed rootChain
            if i == 0:
                joints.append(cmds.rename(rootJoint,name))
                
            # get updated long names
            renamedChain = getJointChain(joints[0])
            
            #middle
            if i != 0 and i != len(chain)-1:
                joints.append(cmds.rename(renamedChain[i],name))
                
            if i == len(chain)-1:
                joints.append(cmds.rename(renamedChain[i],nameEnd))


    return joints
        
def mirrorJointChain(rootJoint):
    
     #string
    if isinstance(rootJoint,unicode):
        rootJoint = str(rootJoint)
    if isinstance(rootJoint,str):
        rootJoint = sUtil.getNameShort(rootJoint)

        if isJoint(rootJoint):
            side = sUtil.getSide(rootJoint)
            base = sUtil.getBase(rootJoint)
            suffix = sUtil.getSuffix(rootJoint)
            
            chainName = getJointChain(rootJoint)
            print chainName

            mirrorSide = "r"
            if side == "r":
                mirrorSide = "l"
                
            mirrorJoint = sUtil.nameBuild(mirrorSide,base,"JNT")
            if cmds.objExists(mirrorJoint):
                mirrorChain = cmds.mirrorJoint(rootJoint,mirrorYZ=True,mirrorBehavior=True,searchReplace=(side+"_", "TMP_"))

                cons=[]
                for i in range (len(mirrorChain)):

                    baseChain = sUtil.getBase(sUtil.getNameShort(mirrorChain[i]))
                    name = sUtil.nameBuild(mirrorSide,baseChain,suffix)
                    if cmds.objExists(name):
                        cmds.delete(cmds.parentConstraint(mirrorChain[i],name))
                cmds.delete(mirrorChain)
            else:
                 mirrorChain = cmds.mirrorJoint(rootJoint,mirrorYZ=True,mirrorBehavior=True,searchReplace=(side+"_", mirrorSide+"_"))
                 
            _logger.info("Mirrored Chain {0}".format(rootJoint))
    else:
        for item in rootJoint:
            mirrorJointChain(item)
            
    