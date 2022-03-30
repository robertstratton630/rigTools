import maya.cmds as cmds


def createNamespace(name):
    cmds.namespace(add=name)


def setNameSpace(name):
    cmds.namespace(set=name)
