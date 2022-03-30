import maya.api.OpenMaya as om
import maya.OpenMaya as OpenMaya


def getDagPathFromMObject(m_obj):
    m_dagPath = om.MDagPath()

    if m_obj.hasFn(om.MFn.kDagNode):
        om.MDagPath.getAPathTo(m_obj, m_dagPath)

    return m_dagPath


def getMObject(name):
    selectionList = om.MSelectionList()
    selectionList.add(str(name))
    node = selectionList.getDependNode(0)
    return node


def getDagPath(xform):
    selectionList = om.MSelectionList()
    selectionList.add(str(xform))
    dagPath = selectionList.getDagPath(0)
    return dagPath


def getMObjectOld(name):

    selectionList = OpenMaya.MSelectionList()
    selectionList.add(str(name))
    mObject = OpenMaya.MObject()
    selectionList.getDependNode(0, mObject)
    return mObject
