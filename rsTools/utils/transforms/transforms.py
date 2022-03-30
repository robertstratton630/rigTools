import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import pymel.core as pm
import maya.mel as mel
import rsTools.utils.data.string as string
import rsTools.utils.transform.joint as joint

import maya.cmds as cmds

# setting overrides


def enableDrawOverrides(obj):
    cmds.setAttr(obj+".overrideEnabled", 1)


def disableDrawOverrides(obj):
    cmds.setAttr(obj+".overrideEnabled", 0)


# getting color values
def setColorIndex(obj, index=14):
    enableDrawOverrides(obj)
    cmds.setAttr(obj+".overrideColor", index)


def getColorIndex(obj):
    return cmds.getAttr(obj+".overrideColor")


def rbgColorMap():
    colorMapDict = {
        0: None,
        1: (0, 0, 0),
        2: (64, 64, 64),
        3: (128, 128, 128),
        4: (155, 0, 40),
        5: (0, 4, 96),
        6: (0, 0, 255),
        7: (0, 70, 25),
        8: (38, 0, 67),
        9: (200, 0, 200),
        10: (138, 72, 51),
        11: (63, 35, 31),
        12: (153, 38, 0),
        13: (255, 0, 0),
        14: (0, 255, 0),
        15: (0, 65, 153),
        16: (255, 255, 255),
        17: (255, 255, 0),
        18: (100, 220, 255),
        19: (67, 255, 163),
        20: (255, 176, 176),
        21: (228, 172, 121),
        22: (255, 255, 99),
        23: (0, 153, 84),
        24: (165, 108, 49),
        25: (158, 160, 48),
        26: (104, 160, 48),
        27: (48, 161, 94),
        28: (48, 162, 162),
        29: (48, 102, 160),
        30: (112, 48, 162),
        31: (162, 48, 106)
    }
    return colorMapDict


def getRBGColorFromIndex(index):
    # colormapping dictionary
    rbgValues = rbgColorMap()
    return rbgValues[index]


def visOveride(obj, value):
    cmds.setAttr(obj+'.overrideEnabled', 1)
    cmds.setAttr(obj+'.overrideVisibility', value)


def hideAnimChannels(obj, lock=False):
    '''hide anim channels on given obj'''
    for attr in ('s', 'r', 't'):
        for axis in ('x', 'y', 'z'):
            cmds.setAttr(obj+'.%s%s' % (attr, axis),
                         keyable=False, channelBox=False, lock=lock)
    #cmds.setAttr(obj+'.v', keyable=False,channelBox=False)


def matchAttr(src, target, attr):
    '''match the attr on the target to the same attr on src. Will work through locks.'''
    if not cmds.objExists(src+'.'+attr):
        raise RuntimeError('Source object.attr not found: %s.%s' % (src, attr))
    srcType = cmds.getAttr(src+'.'+attr, type=True)

    if not cmds.objExists(target+'.'+attr):
        raise RuntimeError('target object.attr not found: %s.%s' % (src, attr))
    targetType = cmds.getAttr(target+'.'+attr, type=True)

    if not srcType == targetType:
        raise RuntimeError('src and target attrs not the same type')

    locked = False
    if cmds.getAttr(target+'.'+attr, lock=True):
        locked = True
        cmds.setAttr(target+'.'+attr, lock=False)

    if srcType == 'string':
        val = cmds.getAttr(src + '.%s' % attr)
        cmds.setAttr(target+'.%s' % attr, val, type='string')
    else:
        if attr in 'srt':
            for axis in 'xyz ':
                cmds.setAttr(target+'.%s%s' % (attr, axis),
                             cmds.getAttr(src+'%s.%s' % (attr, axis)))
        else:
            cmds.setAttr(target+'.%s' % attr, cmds.getAttr(src+'.%s' % attr))

    if locked:
        cmds.setAttr(target+'.'+attr, lock=True)


def lockAndHide(obj, attrs):
    '''given an object and a list of attrs, lock and hide those attrs'''
    for aa in attrs:
        cmds.setAttr(obj+'.'+aa, k=False, l=True)
        if (aa == 'r'):
            cmds.setAttr(obj+'.rx', k=False, l=True)
            cmds.setAttr(obj+'.ry', k=False, l=True)
            cmds.setAttr(obj+'.rz', k=False, l=True)
        if (aa == 't'):
            cmds.setAttr(obj+'.tx', k=False, l=True)
            cmds.setAttr(obj+'.ty', k=False, l=True)
            cmds.setAttr(obj+'.tz', k=False, l=True)
        if (aa == 's'):
            cmds.setAttr(obj+'.sx', k=False, l=True)
            cmds.setAttr(obj+'.sy', k=False, l=True)
            cmds.setAttr(obj+'.sz', k=False, l=True)


def unlockAndShow(obj, attrs):
    '''given an object and a list of attrs, unlock and show those attrs'''
    for aa in attrs:
        cmds.setAttr(obj+'.'+aa, k=True, l=False)
        if (aa == 'r'):
            cmds.setAttr(obj+'.rx', k=True, l=False)
            cmds.setAttr(obj+'.ry', k=True, l=False)
            cmds.setAttr(obj+'.rz', k=True, l=False)
        if (aa == 't'):
            cmds.setAttr(obj+'.tx', k=True, l=False)
            cmds.setAttr(obj+'.ty', k=True, l=False)
            cmds.setAttr(obj+'.tz', k=True, l=False)
        if (aa == 's'):
            cmds.setAttr(obj+'.sx', k=True, l=False)
            cmds.setAttr(obj+'.sy', k=True, l=False)
            cmds.setAttr(obj+'.sz', k=True, l=False)


def breakConnections(obj, attrs):
    '''given an object and a list of attrs, break all incoming connections'''
    for attr in attrs:
        unlockAndShow(obj, [attr])
        fullName = '%s.%s' % (obj, attr)
        dest = cmds.connectionInfo(fullName, getExactDestination=True)
        if dest:
            src = cmds.connectionInfo(dest, sourceFromDestination=True)
            if src:
                cmds.disconnectAttr(src, dest)
        # if translate, rotate, or scale, do sub attributes as well
        if (attr in 'srt'):
            breakConnections(obj, [attr+'x', attr+'y', attr+'z'])


def connectWithReverse(src, targ, force=False):
    '''Given a source 'obj.attr' and a target 'obj.attr', connect with a reverse between.
    Returns the created reverse node. Input should be between 0 and 1
    '''
    revNode = cmds.createNode('reverse', n=src.replace('.', '_')+'_reverse')
    cmds.connectAttr(src, revNode+'.inputX')
    cmds.connectAttr(revNode+'.outputX', targ, f=force)
    return revNode


def connectWithMult(src, targ, mult=-1, force=False):
    '''Given a source 'obj.attr' and a target 'obj.attr', connect with and multiplier between.
    Returns the created multiplyDivide node. mult defaults to -1
    '''
    mdNode = cmds.createNode(
        'multiplyDivide', n=src.replace('.', '_')+'_multiply')
    cmds.setAttr(mdNode+'.input2X', mult)
    cmds.connectAttr(src, mdNode+'.input1X')
    cmds.connectAttr(mdNode+'.outputX', targ, f=force)
    return mdNode


def connectWithAdd(src, targ, add=1, force=False):
    '''Given a source 'obj.attr' and a target 'obj.attr', connect with an addition between.
    Returns the created addDoubleLinear node. add defaults to 1
    '''
    addNode = cmds.createNode(
        'addDoubleLinear', n=src.replace('.', '_')+'_adder')
    cmds.setAttr(addNode+'.input2', add)
    cmds.connectAttr(src, addNode+'.input1')
    cmds.connectAttr(addNode+'.output', targ, f=force)
    return addNode


def addAttrSwitch(attr, type='long', max=1, min=0, value=0, keyable=True, niceName='', node='', lock=False):
    '''Add a default 0-1 animatable attribute to a node and return the attr name'''
    attr = attr.split('.')
    if len(attr) > 1:
        node = attr[0]
        attr = attr[1]
    else:
        if cmds.objExists(node) != True:
            raise RuntimeError(
                'Error attribute.add(): Invalid node specified.')
        attr = attr[0]
    argDict = {'ln': attr, 'k': keyable, 'at': type}

    if max:
        argDict['max'] = max
    if min:
        argDict['min'] = min
    if niceName:
        argDict['nn'] = niceName
    if type == 'message':
        cmds.addAttr(node, ln=attr, at=type)
    else:
        cmds.addAttr(node, **argDict)
    newattr = '%s.%s' % (node, attr)

    try:
        cmds.setAttr(newattr, value)
    except RuntimeError:
        pass

    cmds.setAttr(newattr, l=lock)
    return newattr


def connect(inputsA, outputs):
    for i, axis in range(inputsA):
        if i < len(inputsA):
            try:
                cmds.connectAttr(inputsA[i], outputs[i])
            except:
                try:
                    cmds.setAttr(outputs[i], inputsA[i])
                except:
                    pass


def multiplyDivideNode(inputs, inputsB, outputs=[], mode=0):

    node = cmds.createNode("multiplyDivide")
    cmds.setAttr(node+".operation", mode)

    xyz = "XYZ"
    # input A
    if isinstance(inputs, list):
        for i in range(len(inputs)):
            try:
                cmds.connectAttr(
                    inputs[i], ("{0}.input1{1}".format(node, xyz[i])))
            except:
                try:
                    cmds.setAttr(("{0}.input1{1}".format(node, xyz[i])), float(
                        cmds.getAttr(inputs[i])))
                except:
                    cmds.setAttr(("{0}.input1{1}".format(
                        node, xyz[i])), float(inputs[i]))

    #string or float
    else:
        try:
            cmds.connectAttr(inputs, ("{0}.input1X".format(node)))
        except:
            try:
                cmds.setAttr("{0}.input1X".format(node),
                             float(cmds.getAttr(inputs)))
            except:
                cmds.setAttr("{0}.input1X".format(node), float(inputs))

    # input B
    if isinstance(inputsB, list):
        for i in range(len(inputsB)):
            try:
                cmds.connectAttr(
                    inputsB[i], ("{0}.input2{1}".format(node, xyz[i])))
            except:
                try:
                    cmds.setAttr(("{0}.input2{1}".format(node, xyz[i])), float(
                        cmds.getAttr(inputsB[i])))
                except:
                    cmds.setAttr(("{0}.input2{1}".format(
                        node, xyz[i])), float(inputsB[i]))

    #string or float
    else:
        try:
            cmds.connectAttr(inputsB, ("{0}.input2X".format(node)))
        except:
            try:
                cmds.setAttr("{0}.input2X".format(node),
                             float(cmds.getAttr(inputsB)))
            except:
                cmds.setAttr("{0}.input2X".format(node), float(inputsB))

    # outputs
    if outputs:
        if isinstance(outputs, list):
            for i in range(len(outputs)):
                try:
                    cmds.connectAttr("{0}.output{1}".format(
                        node, xyz[i]), outputs[i])
                except:
                    cmds.setAttr(outputs[i], float(cmds.getAttr(
                        "{0}.output{1}".format(node, xyz[i]))))
        else:
            try:
                cmds.connectAttr("{0}.outputX".format(node), outputs)
            except:
                cmds.setAttr(outputs, float(
                    cmds.getAttr("{0}.outputX".format(node))))

    return node


def plusMinusNode(inputs, inputsB, outputs=[], mode=1):

    node = cmds.createNode("plusMinusAverage")
    cmds.setAttr(node+".operation", mode)

    dim = 1
    if isinstance(inputs, list):
        dim = len(inputs)

    if dim == 1:

        # inputA
        try:
            cmds.connectAttr(inputs, ("{0}.input1D[0]".format(node)))
        except:
            try:
                cmds.setAttr(("{0}.input1D[0]".format(
                    node)), float(cmds.getAttr(inputs)))
            except:
                cmds.setAttr(("{0}.input1D[0]".format(node)), float(inputs))

        # inputB
        try:
            cmds.connectAttr(inputsB, ("{0}.input1D[1]".format(node)))
        except:
            try:
                cmds.setAttr(("{0}.input1D[1]".format(
                    node)), float(cmds.getAttr(inputsB)))
            except:
                cmds.setAttr(("{0}.input1D[1]".format(node)), float(inputsB))

        # output
        try:
            cmds.connectAttr("{0}.output1D".format(node), outputs)
        except:
            pass

    XY = "xy"
    if dim == 2:
        for i in range(2):

            # inputA
            try:
                cmds.connectAttr(
                    inputs, ("{0}.input2D[0].input2D{1}".format(node, XY[1])))
            except:
                try:
                    cmds.setAttr(("{0}.input2D[0].input2D{1}".format(
                        node, XY[1])), float(cmds.getAttr(inputs)))
                except:
                    cmds.setAttr(
                        ("{0}.input2D[0].input2D{1}".format(node, XY[1])), float(inputs))

            # inputB
            try:
                cmds.connectAttr(
                    inputs, ("{0}.input2D[1].input2D{1}".format(node, XY[1])))
            except:
                try:
                    cmds.setAttr(("{0}.input2D[1].input2D{1}".format(
                        node, XY[1])), float(cmds.getAttr(inputs)))
                except:
                    cmds.setAttr(
                        ("{0}.input2D[1].input2D{1}".format(node, XY[1])), float(inputs))

            # output
            try:
                cmds.connectAttr("{0}.output2D.output2D{1}".format(
                    node, XY[1]), outputs[i])
            except:
                pass

    XY = "xyz"
    if dim == 3:
        for i in range(3):

            # inputA
            try:
                cmds.connectAttr(
                    inputs, ("{0}.input3D[0].input3D{1}".format(node, XY[1])))
            except:
                try:
                    cmds.setAttr(("{0}.input3D[0].input3D{1}".format(
                        node, XY[1])), float(cmds.getAttr(inputs)))
                except:
                    cmds.setAttr(
                        ("{0}.input3D[0].input3D{1}".format(node, XY[1])), float(inputs))

            # inputB
            try:
                cmds.connectAttr(
                    inputs, ("{0}.input3D[1].input3D{1}".format(node, XY[1])))
            except:
                try:
                    cmds.setAttr(("{0}.input3D[1].input3D{1}".format(
                        node, XY[1])), float(cmds.getAttr(inputs)))
                except:
                    cmds.setAttr(
                        ("{0}.input3D[1].input3D{1}".format(node, XY[1])), float(inputs))

            # output
            try:
                cmds.connectAttr("{0}.output3D.output3D{1}".format(
                    node, XY[1]), outputs[i])
            except:
                pass
    return node


def connectReverse(inputs, outputs, force=True):

    node = cmds.createNode("reverse")

    # inputs
    xyz = "XYZ"
    if isinstance(inputs, list):
        for i in range(len(inputs)):
            try:
                cmds.connectAttr(
                    inputs[i], ("{0}.input{1}".format(node, xyz[i])))
            except:
                try:
                    cmds.setAttr(("{0}.input{1}".format(node, xyz[i])), float(
                        cmds.getAttr(inputs[i])))
                except:
                    cmds.setAttr(("{0}.input{1}".format(
                        node, xyz[i])), float(inputs[i]))
    else:
        try:
            cmds.connectAttr(inputs, ("{0}.inputX".format(node)))
        except:
            try:
                cmds.setAttr("{0}.inputX".format(node),
                             float(cmds.getAttr(inputs)))
            except:
                cmds.setAttr("{0}.inputX".format(node), float(inputs))

    # outputs
    if isinstance(outputs, list):
        for i in range(len(inputs)):
            try:
                cmds.connectAttr("{0}.output{1}".format(
                    node, xyz[i]), outputs[i])
            except:
                cmds.setAttr(outputs[i], float(cmds.getAttr(
                    "{0}.output{1}".format(node, xyz[i]))))
    else:
        try:
            cmds.connectAttr("{0}.outputX".format(node), outputs)
        except:
            cmds.setAttr(outputs, float(
                cmds.getAttr("{0}.outputX".format(node))))


def getConstraintNodes(obj):
    parent = cmds.listRelatives(obj, c=True, type="parentConstraint")
    point = cmds.listRelatives(obj, c=True, type="pointConstraint")
    orient = cmds.listRelatives(obj, c=True, type="orientConstraint")
    aim = cmds.listRelatives(obj, c=True, type="aimConstraint")
    output = []
    if parent:
        output.append(parent)
    if point:
        output.append(point)
    if orient:
        output.append(orient)
    if aim:
        output.append(aim)
    return output


def getConstraintAttributes(constraintNode):
    return cmds.listAttr(constraintNode, ud=True)


def getConstraintTargets(constraintNode):
    names = cmds.listAttr(constraintNode, ud=True)
    chop = []
    for n in names:
        chop.append(n[:-2])
    return chop


def getConstraintTargetPlugs(constraintNode):
    names = cmds.listAttr(constraintNode, ud=True)
    chop = []
    for n in names:
        plug = "{0}.{1}".format(constraintNode, n)
        chop.append(plug)
    return chop


def blend(attributeA, attributeB, blender):
    try:
        cmds.connectAttr(blender, attributeB, f=True)
    except:
        print "could not direct connect "

    try:
        connectReverse(blender, attributeA)
    except:
        print "could not connectReverse connect "


def selectConstraintTarget(obj):
    con = getConstraintNodes(obj)[0]
    target = getConstraintTargets(con)[0]
    cmds.select(target, r=True)


'''
selectConstraintTarget (cmds.ls(sl=True)[0])   
     
      
for obj in cmds.ls(sl=True):
    conNode = getConstraintNodes(obj)[0]
    targets =  getConstraintTargetPlugs(conNode[0])
    blend(targets[0],targets[1],"l_arm_GRP.ikfk")
    '''


def calculatePoleVectorLocator(startJoint, midJoint, endJoint):

    sPos = cmds.xform(startJoint, q=True, ws=True, t=True)
    mPos = cmds.xform(midJoint, q=True, ws=True, t=True)
    ePos = cmds.xform(endJoint, q=True, ws=True, t=True)

    sVec = om.MVector(sPos[0], sPos[1], sPos[2])
    mVec = om.MVector(mPos[0], mPos[1], mPos[2])
    eVec = om.MVector(ePos[0], ePos[1], ePos[2])

    # do all calculations at orig
    line = eVec-sVec
    point = mVec - sVec

    # take dot product - projection distance
    scaleValue = (line * point) / (line*line)

    # get the prjection point and add to start
    projectVec = (line * scaleValue) + sVec

    startToMidLen = (mVec - sVec).length()
    midToEndLen = (mVec - eVec).length()
    totalLen = startToMidLen + midToEndLen

    outPos = (mVec - projectVec).normal() * totalLen + mVec

    loc = cmds.spaceLocator()
    cmds.xform(loc, ws=True, t=(outPos[0], outPos[1], outPos[2]))

    return loc


def attrAdd(obj, attrName, defaultVal=0, typ="float", minVal=None, maxVal=None, **kwargs):

    attrExist = cmds.attributeQuery(attrName, node=obj, exists=True)

    if not attrExist:
        hidden = kwargs.get("hidden", 0)
        keyable = kwargs.get("keyable", 1)
        locked = kwargs.get("locked", 0)

        if typ == "float" or typ == "long" or typ == "short" or typ == "double" or typ == "doubleLinear":
            if maxVal and minVal is not None:
                cmds.addAttr(obj, ln=attrName, defaultValue=defaultVal,
                             minValue=minVal, maxValue=maxVal, k=keyable, at=typ)
            elif maxVal:
                cmds.addAttr(obj, ln=attrName, defaultValue=defaultVal,
                             maxValue=maxVal, k=keyable, at=typ)
            elif minVal:
                cmds.addAttr(obj, ln=attrName, defaultValue=defaultVal,
                             minValue=minVal, k=keyable, at=typ)
            else:
                cmds.addAttr(obj, ln=attrName,
                             defaultValue=defaultVal, k=keyable, at=typ)

        elif typ == "string":
            attr = cmds.addAttr(obj, ln=attrName, k=keyable, dt=typ)
            try:
                cmds.setAttr(obj+"."+attrName, defaultVal, typ="string")
            except:
                pass

        elif typ == "enum":
            enumFormatted = ""
            if isinstance(defaultVal, str):
                enumFormatted = defaultVal

            else:
                for e in defaultVal:
                    if e is not defaultVal[-1]:
                        enumFormatted += str(e+":")
                    else:
                        enumFormatted += str(e)

            attr = cmds.addAttr(obj, ln=attrName, k=keyable,
                                at=typ, enumName=enumFormatted)

        elif typ == "float3":
            attr = cmds.addAttr(obj, ln=attrName, k=keyable, dt=typ)

        if locked:
            try:
                cmds.setAttr(obj+"."+attrName, lock=True)
            except:
                pass
        if hidden:
            try:
                cmds.setAttr(obj+"."+attrName, cb=False)
            except:
                pass
    else:
        if typ == "string" or typ == "enum":
            try:
                cmds.setAttr(obj+"."+attrName, defaultVal, typ="string")
            except:
                pass

        else:
            try:
                cmds.setAttr(obj+"."+attrName, defaultVal)
            except:
                pass

    return obj+"."+attrName


def addSeparator(obj, attrName):
    attr = attrAdd(obj, attrName, "____________",
                   typ="enum", **{"locked": True})
    return attr


def getShape(obj):
    shape = cmds.listRelatives(obj, s=1)
    return shape


def getShapes(object):
    shapes = cmds.listRelatives(object, shapes=True)
    if shapes:
        return shapes
    return None


def cleanShapeNodes(object):
    shapes = getShapes(object)

    if shapes:
        for sp in shapes:
            cons = cmds.listConnections(sp, s=False, d=True)
            if not cons:
                cmds.delete(sp)


def cleanAllShapeNodes():
    import rsTools.utils.openMaya.mesh as mesh
    geometry = cmds.ls(geometry=True, s=False)
    for g in geometry:
        if mesh.isMesh(g):
            cleanShapeNodes(g)


def createPivotOffsetConnection(pivotControl, control):
    pass


def transformCreate(side=None, baseName=None, suffix="GRP", parent=None, transformMatch=None, mt=True, mr=True, ms=False, **kwargs):

    name = sUtil.nameBuild(side, baseName, suffix)
    if cmds.objExists(name):
        return name

    transform = ""
    if suffix == "GRP":
        transform = cmds.group(em=True, name=name)
        transform = cmds.group(em=True, name=name)
    elif suffix == "JNT":
        cmds.select(cl=True)
        transform = cmds.joint(name=name)
    elif suffix == "LOC":
        transform = cmds.spaceLocator(name=name)

    if parent and cmds.objExists(parent):
        transform = cmds.parent(transform, parent)

    if transformMatch and cmds.objExists(transformMatch):
        if mt:
            cmds.delete(cmds.pointConstraint(transformMatch, transform))
        if mr:
            cmds.delete(cmds.orientConstraint(transformMatch, transform))

    if isinstance(transform, list):
        return transform[0]
    return transform


def transformCreateFromName(name=None, parent=None, transformMatch=None, mt=True, mr=True, ms=False, **kwargs):
    if cmds.objExists(name):
        return name

    transform = name
    suffix = sUtil.getSuffix(name)
    if suffix == "GRP":
        transform = cmds.group(em=True, name=name)
    elif suffix == "JNT":
        cmds.select(cl=True)
        transform = cmds.joint(name=name)
    elif suffix == "LOC":
        transform = cmds.spaceLocator(name=name)
    else:
        transform = cmds.group(em=True, name=name)

    if parent and cmds.objExists(parent):
        transform = cmds.parent(transform, parent)

    if transformMatch and cmds.objExists(transformMatch):
        if mt:
            cmds.delete(cmds.pointConstraint(transformMatch, transform))
        if mr:
            cmds.delete(cmds.orientConstraint(transformMatch, transform))

    if isinstance(transform, list):
        return transform[0]
    return transform


def distanceBetweenNode(startTransform, endTransform, parent=None, name="DistanceMeasure_DIST"):

    if cmds.objExists(startTransform) and cmds.objExists(endTransform):
        node = cmds.createNode("distanceDimShape")

        sShape = getShape(startTransform)[0]
        eShape = getShape(endTransform)[0]

        nodeTransform = cmds.listRelatives(p=True)[0]
        nodeTransform = cmds.rename(nodeTransform, name)
        node = getShape(nodeTransform)[0]

        cmds.connectAttr(sShape+".worldPosition[0]", node+".startPoint")
        cmds.connectAttr(eShape+".worldPosition[0]", node+".endPoint")

        stretchEnvAttr = attrAdd(nodeTransform, "stretchEnv", 1)
        globalScaleAttr = attrAdd(nodeTransform, "worldScale", 1)
        origLenAttr = attrAdd(nodeTransform, "origLength", 0)
        origLenAttrScaled = attrAdd(nodeTransform, "origLengthWorldScaled", 1)
        currentLenAttr = attrAdd(nodeTransform, "currentLength", 0)
        scaleOffsetAttr = attrAdd(nodeTransform, "scaleOffset", 0)

        scaleResultAttr = attrAdd(nodeTransform, "scaleResult", 1)
        scaleResultFinal = attrAdd(nodeTransform, "scaleResultFinal", 1)
        length = cmds.getAttr(node+".distance")

        # set the orig len
        cmds.setAttr(origLenAttr, length)
        cmds.setAttr(origLenAttr, lock=True)
        mdn_origScaled = multiplyDivideNode(
            origLenAttr, globalScaleAttr, mode=1)
        cmds.connectAttr(mdn_origScaled+".outputX", origLenAttrScaled)

        # set current len
        cmds.connectAttr((node+".distance"), currentLenAttr)

        # get overall stretchValue
        mdn = multiplyDivideNode(currentLenAttr, origLenAttrScaled, mode=2)

        # offset the scale and assign to scale result
        pma = plusMinusNode((mdn+".outputX"), scaleOffsetAttr, scaleResultAttr)

        blender = cmds.createNode("blendTwoAttr")
        cmds.connectAttr(stretchEnvAttr, blender+".attributesBlender")
        cmds.connectAttr(scaleResultAttr, blender+".input[1]")
        cmds.connectAttr(globalScaleAttr, blender+".input[0]")
        cmds.connectAttr(blender+".output", scaleResultFinal)

        if parent:
            nodeTransform = cmds.parent(nodeTransform, parent)

        return nodeTransform
    return None


def remapValueNode(inputVal, inputMin, inputMax, outputMin, outputMax, output=""):
    node = cmds.createNode("remapValue")

    try:
        cmds.connectAttr(inputVal, node+".inputValue")
    except:
        cmds.setAttr(node+".inputValue", inputVal)

    try:
        cmds.connectAttr(inputMin, node+".inputMin")
    except:
        cmds.setAttr(node+".inputMin", inputMin)

    try:
        cmds.connectAttr(inputMax, node+".inputMax")
    except:
        cmds.setAttr(node+".inputMax", inputMax)

    try:
        cmds.connectAttr(outputMin, node+".outputMin")
    except:
        cmds.setAttr(node+".outputMin", outputMin)

    try:
        cmds.connectAttr(outputMax, node+".outputMax")
    except:
        cmds.setAttr(node+".outputMax", outputMax)

    if output:
        cmds.connectAttr(node+".outValue", output)


def connectBlendAttr(sourceAttrs, driverAttr, dest):

    node = cmds.createNode("blendTwoAttr")

    if isinstance(sourceAttrs, list):
        for i, attr in enumerate(sourceAttrs):
            cmds.connectAttr(attr, node+".input[{0}]".format(str(i)))
    else:
        cmds.connectAttr(sourceAttrs, node+".input[0]")

    cmds.connectAttr(driverAttr, node+".attributesBlender")

    if dest:
        try:
            cmds.connectAttr(node+".output", dest)
        except:
            pass
    return node


def distanceBetween(startTransform, endTransform, parent=None, name="DistanceMeasure_DIST"):

    if cmds.objExists(startTransform) and cmds.objExists(endTransform):
        node = cmds.createNode("distanceDimShape")

        sShape = getShape(startTransform)[0]
        eShape = getShape(endTransform)[0]

        nodeTransform = cmds.listRelatives(p=True)[0]
        nodeTransform = cmds.rename(nodeTransform, name)
        node = getShape(nodeTransform)[0]

        cmds.connectAttr(sShape+".worldPosition[0]", node+".startPoint")
        cmds.connectAttr(eShape+".worldPosition[0]", node+".endPoint")

        length = cmds.getAttr(node+".distance")

        origLenAttr = attrAdd(nodeTransform, "origLength", length)
        currentLenAttr = attrAdd(nodeTransform, "currentLength", length)
        outDist = attrAdd(nodeTransform, "outDistance", length)

        inScaleAttr = attrAdd(nodeTransform, "inScale", 1)
        outScaleAttr = attrAdd(nodeTransform, "outScale", 1)

        scaleCon = transformCreate(
            baseName=name, parent=nodeTransform, transformMatch=nodeTransform, mt=True, mr=True)

        cmds.connectAttr(scaleCon+".sx", inScaleAttr)
        cmds.connectAttr(node+".distance", currentLenAttr)

        md1 = multiplyDivideNode(origLenAttr, inScaleAttr, mode=1)
        md2 = multiplyDivideNode(
            currentLenAttr, (md1+".outputX"), outScaleAttr, mode=2)
        md3 = multiplyDivideNode(origLenAttr, outScaleAttr, outDist, mode=1)

        if parent:
            nodeTransform = cmds.parent(nodeTransform, parent)

        return nodeTransform
    return None


def connectTYMult(attr, objects):
    if isinstance(objects, list):
        for o in objects:
            node = cmds.createNode("multiplyDivide")
            origTY = attrAdd(o, "origTy", cmds.getAttr(o+".ty"))
            cmds.connectAttr(attr, node+".input1X")
            cmds.connectAttr(origTY, node+".input2X")
            cmds.connectAttr(node+".outputX", o+".ty")
    else:
        node = cmds.createNode("multiplyDivide")
        origTY = attrAdd(objects, "origTy", cmds.getAttr(objects+".ty"))
        cmds.connectAttr(attr, node+".input1X")
        cmds.connectAttr(origTY, node+".input2X")
        cmds.connectAttr(node+".outputX", objects+".ty")


def connectMult(srcA, srcB, out, force=False):

    mdNode = cmds.createNode('multiplyDivide', n=srcA.replace('.', '_')+'_MDN')
    cmds.connectAttr(srcA, mdNode+'.input1X')
    cmds.connectAttr(srcB, mdNode+'.input2X')
    cmds.connectAttr(mdNode+'.outputX', out, f=force)
    return mdNode


def setDrivenKey(driver, driverVals, driven, drivenVals, tangent="linear"):

    sdkData = []
    if driven:
        cmds.setAttr(driven, k=True, l=False)  # set keyable and unlocked
        animU = cmds.listConnections(driven, s=1, d=0, scn=1)
        if animU:
            for a in animU:
                typ = cmds.nodeType(a)
                if "animCurveU" in typ:
                    cmds.delete(a)

        for i in range(len(driverVals)):
            keyable = cmds.getAttr(driven, k=True)
            sdk = cmds.setDrivenKeyframe(
                driven, cd=driver, itt=tangent, ott=tangent, dv=driverVals[i], v=drivenVals[i])
            sdkData.append(sdk)


def connectClamp(attr, minVal, maxVal, output=None):
    node = cmds.createNode('clamp', n=attr.replace('.', '_')+'_CLAMP')

    try:
        cmds.connectAttr(attr, node+".input.inputR")
    except:
        cmds.setAttr(node+".input.inputR", attr)

    try:
        cmds.connectAttr(attr, node+".minR")
    except:
        cmds.setAttr(node+".minR", attr)

    try:
        cmds.connectAttr(attr, node+".maxR")
    except:
        cmds.setAttr(node+".maxR", attr)

    if output:
        try:
            cmds.connectAttr(node+".outputR", output)
        except:
            pass

    return node


def findObjectsUnderNode(node, nodeType, match="", doShortName=False):
    if isinstance(node, unicode):
        node = str(node)
    if isinstance(node, str):
        try:
            allChildren = []
            if doShortName:
                allChildren = cmds.listRelatives(node, ad=True, typ=nodeType)
            else:
                allChildren = cmds.listRelatives(
                    node, ad=True, f=True, typ=nodeType)
               # and match in a  and not "|{0}|".format(match) in a

            allChildren = [
                a for a in allChildren if match in a and not "|{0}|".format(match) in a]
            return allChildren
        except:
            return None
    else:
        allChildren = []
        for i in node:
            items = findObjectsUnderNode(i, nodeType, match)
            if items:
                allChildren += items
        return allChildren


def setAxisDisplay(display=True, allObj=False):
    if not allObj:
        if len(cmds.ls(sl=1, type="joint")) == 0:
            jointList = cmds.ls(type="joint")
        else:
            jointList = cmds.ls(sl=1, type="joint")
        # set the displayLocalAxis attribute to what the user specifies.
        for jnt in jointList:
            cmds.setAttr(jnt + ".displayLocalAxis", display)
    else:
        if len(cmds.ls(sl=1)) == 0:
            objList = cmds.ls(transforms=1)
        else:
            objList = cmds.ls(sl=1)
        # set the displayLocalAxis attribute to what the user specifies.
        for obj in objList:
            cmds.setAttr(obj + ".displayLocalAxis", display)


def createTransformAxisCone(obj):

    # string
    if isinstance(obj, unicode):
        obj = str(obj)
    if isinstance(obj, str):
        obj = sUtil.getNameShort(obj)

        group = transformCreate(baseName="jointCones")
        attr = attrAdd(group, "coneScale", 1.0)

        # x
        pConeX = cmds.polyCone(r=0.1, h=1, subdivisionsAxis=4, ch=False)[0]
        cmds.setAttr(pConeX+".ty", 0.5)
        cmds.xform(pConeX, ws=True, piv=(0, 0, 0))
        cmds.setAttr(pConeX+".rz", -90)
        shader.applyShader(pConeX, "red_SHDR", color=[1, 0, 0])

        # y
        pConeY = cmds.polyCone(r=0.1, h=1, subdivisionsAxis=4, ch=False)[0]
        cmds.setAttr(pConeY+".ty", 0.5)
        shader.applyShader(pConeY, "green_SHDR", color=[0, 1, 0])

        # z
        pConeZ = cmds.polyCone(r=0.1, h=1, subdivisionsAxis=4, ch=False)[0]
        cmds.setAttr(pConeZ+".ty", 0.5)
        cmds.xform(pConeZ, ws=True, piv=(0, 0, 0))
        cmds.setAttr(pConeZ+".rx", 90)
        shader.applyShader(pConeZ, "blue_SHDR", color=[0, 0, 1])

        side = string.getSide(obj)
        base = string.getBase(obj)
        suffix = string.getSuffix(obj)
        name = string.nameBuild(side, base+"Cone", "GEO")

        newGeo = cmds.polyUnite(pConeX, pConeY, pConeZ, n=name, ch=False)[0]

        cmds.connectAttr(attr, newGeo+".sx")
        cmds.connectAttr(attr, newGeo+".sy")
        cmds.connectAttr(attr, newGeo+".sz")

        if cmds.objExists(obj):
            cmds.parentConstraint(obj, newGeo)

        newGeo = cmds.parent(newGeo, group)

        return newGeo
    else:
        cones = []
        for i in obj:
            cones.append(createTransformAxisCone(i))
        return cones


def messageConnect(source, target, sourceMsg, targetMsg):
    cmds.addAttr(target, at="message", ln=targetMsg)
    cmds.addAttr(source, at="message", ln=sourceMsg)

    cmds.connectAttr(target+"."+targetMsg, source+"."+sourceMsg, f=True)
    cmds.connectAttr(source+"."+sourceMsg, target+"."+targetMsg, f=True)


def isVisibleInChannelBox(attr):
    ret = False
    isKeyable = cmds.getAttr(attr, cb=True)
    isChannelBox = cmds.getAttr(attr, k=True)
    if(isKeyable or isChannelBox):
        ret = True
    return ret


def getAttributesAndConnections(obj):
    __jointExtras__ = ["radius", "rotateAxisX", "rotateAxisY", "rotateAxisZ", "preferredAngleX",
                       "preferredAngleY", "preferredAngleZ", "jointOrientX", "jointOrientY", "jointOrientZ"]
    attrs = cmds.listAttr(obj, k=True)
    udAttrs = cmds.listAttr(obj, ud=True, cb=False) or []
    attrs = attrs + udAttrs

    __displayExtras__ = ["overrideEnabled", "overrideColor"]

    if jUtils.isJoint(obj):
        attrs = attrs + __jointExtras__

    attrs = attrs + __displayExtras__
    output = []

    for a in attrs:
        attr = str(obj+"."+a)
        typ = None
        try:
            typ = cmds.attributeQuery(a, node=obj, attributeType=True)
        except:
            continue

        val = cmds.getAttr(attr)

        keyable = 0
        locked = cmds.getAttr(attr, lock=True)
        hidden = 1
        hiddenState = isVisibleInChannelBox(attr)
        if hiddenState:
            hidden = 0
            keyable = 1

        if (typ == "enum" or typ == "string"):
            val = cmds.getAttr(attr, asString=True)

        minVal = None
        maxVal = None
        connections = None
        try:
            minVal = cmds.attributeQuery(a, node=obj, min=True)[0]
        except:
            pass

        try:
            maxVal = cmds.attributeQuery(a, node=obj, max=True)[0]
        except:
            pass

        try:
            connections = cmds.listConnections(attr, s=True, d=False, p=True)
        except:
            pass

        enum = None
        if (typ == "enum"):
            enum = cmds.attributeQuery(a, node=obj, le=True)
            output.append([typ, attr, val, connections, minVal,
                           maxVal, keyable, locked, enum, hidden])
        else:
            output.append([typ, attr, val, connections, minVal,
                           maxVal, keyable, locked, enum, hidden])

    return output

# messageConnect("l_legJB_JNT","l_armUpPose_LOC","conMsg","conMsg")
