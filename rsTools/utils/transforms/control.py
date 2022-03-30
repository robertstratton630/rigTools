import maya.cmds as mc
import rsTools.utils.controls.curveData as csIO
import rsTools.utils.string as str

__controls__ = csIO.listControlsInLibrary()


# main function to create controls
def createControl(objects=[], controlName=None, libraryName="sphere", color="auto",
                  t=False, tx=True, ty=True, tz=True,
                  r=False, rx=True, ry=True, tz=True,
                  s=False, sx=True, sy=True, sz=True,
                  offsetGrp=1, conGrp=1, modifyGrp=1,

                  ):

    # building from list
    if isinstance(objects, list):
        for obj in objects:
            if controlName is None:
                side = str.getSide(obj)
                base = str.getBase(obj)
                controlName = str.nameBuild(side, base, "JNT")

            # build control
            ctrl = csIO.buildControlShape(
                controlName=controlName, libraryName=libraryName, debug=False, scale=1.0)
            setColor(ctrl, color)

    # add offset
    ctrlOffset = mc.group(n=prefix + '_cto', em=True)
    mc.parent(ctrl, ctrlOffset)

    # limit control channels
    for channel in ['sx', 'sy', 'sz', 'v']:

        mc.setAttr(ctrl + '.' + channel, l=True, k=False)

    # move control to reference
    if matchObject:

        mc.delete(mc.parentConstraint(matchObject, ctrlOffset))

    # translate control to reference
    if matchObjectTr:

        mc.delete(mc.pointConstraint(matchObjectTr, ctrlOffset))

    # parent control
    if parentObj:

        mc.parent(ctrlOffset, parentObj)

    return {
        'c': ctrl,
        'off': ctrlOffset
    }


# enables draw overrides
def enableDrawOverrides(obj):
    shapeNode = catch.getShapes(obj)

    if isinstance(shapeNode, list):
        for s in shapeNode:
            cmds.setAttr(s+".overrideEnabled", 1)
    else:
        cmds.setAttr(shapeNode+".overrideEnabled", 1)

# set color


def setColorIndex(object, index=14):
    shapeNode = catch.getShapes(object)
    if isinstance(shapeNode, list):
        for s in shapeNode:
            cmds.setAttr(s+".overrideColor", index)
    else:
        cmds.setAttr(shapeNode+".overrideColor", index)


def setColor(obj, index=14):

    color = None
    if isinstance(index, str):
        if index == "auto":
            color = 17
            if prefix.startswith('l_'):
                color = 6
            if prefix.startswith('r_'):
                color = 13

    index = color or index
    enableDrawOverrides(obj)
    setColorIndex(obj, index)
