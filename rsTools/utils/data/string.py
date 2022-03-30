import maya.cmds as cmds
import re

from itertools import chain


def getShape(obj):
    shape = cmds.listRelatives(obj, s=1)
    return shape


def getShapes(objs):
    shapes = []
    for o in objs:
        shapes.append(getShape(o))
    return shapes


def getSide(obj):
    split = obj.split("_")
    if len(split) > 1:
        if split[0] == "l" or split[0] == "r":
            return split[0]
    else:
        return ""


def getSuffix(obj):
    split = obj.split("_")
    if split:
        return split[-1]


def getBase(obj):
    split = obj.split("_")
    if len(split) > 2:
        return split[1]
    elif len(split) > 1:
        return split[0]
    else:
        return obj


def nameBuild(side, base, suffix):
    name = ""
    if side:
        name = side+"_"
    if base:
        name = name+base
    if suffix:
        name = name+"_"+suffix

    return name


def getNameShort(obj):
    split = obj.split("|")
    if len(split) > 1:
        return split[-1]
    return obj


def alpha(inInt):
    inInt += 1
    alpha = chr(ord('`')+inInt)
    return alpha


def diff(list1, list2):
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    return list(c - d)


def common(list1, list2):
    return [element for element in list1 if element in list2]


def getNameMirror(name):

    if isinstance(name, unicode):
        name = str(name)

    if isinstance(name, str):
        name = getNameShort(name)
        side = getSide(name)
        base = getBase(name)
        suffix = getSuffix(name)
        mirrorSide = "r"

        if side:
            if side == "r":
                mirrorSide = "l"

            mirrorName = nameBuild(mirrorSide, base, suffix)
            return mirrorName
        return name
    else:
        mirrors = []
        for i in name:
            mirrors.append(getMirror(i))
        return mirrors


def capitalize(s):
    return ''.join((c.upper() if prev == ' ' else c) for c, prev in zip(s, chain(' ', s)))


def printSel():

    sel = cmds.ls(sl=True)
    st = "["
    for s in sel:
        if s is not sel[-1]:
            st += "'{0}',".format(str(s))
        else:
            st += "'{0}']".format(str(s))

    print st


def removeDuplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def sort(l):
    if l:
        def convert(text): return float(text) if text.isdigit() else text
        def alphanum(key): return [convert(c)
                                   for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key)]
        l.sort(key=alphanum)
    return l


def diff(list1, list2):
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    return list(c - d)


def diffB(list1, list2):
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    return list(c - d)


def findMatches(pattern, text):
    for match in re.finditer(pattern, text):
        s = match.start()
        e = match.end()
        print("[{0}:{1}]".format(s, e))

#aX = [1,2,3,4,5]
#bX = [5,6,7]
