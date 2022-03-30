import maya.api.OpenMaya as om
import sys
import math
from rsTools.utils.openMaya.vec2 import Vec2


def computeBarycentricCoords(p, vtx0, vtx1, vtx2, attempts=2, it=0):
    u = 0.0
    v = 0.0
    w = 0.0

    v0 = vtx1 - vtx0
    v1 = vtx2 - vtx0
    v2 = p - vtx0

    d00 = v0 * v0
    d01 = v0 * v1
    d11 = v1 * v1
    d20 = v2 * v0
    d21 = v2 * v1

    denom = d00 * d11 - d01 * d01

    if (math.fabs(denom) > sys.float_info.epsilon):
        v = (d11 * d20 - d01 * d21) / denom
        w = (d00 * d21 - d01 * d20) / denom
        u = 1.0 - v - w
        return [u, v, w]

    d22 = v2 * v1
    denom = d11 * d22 - d21 * d21

    if (math.fabs(denom) > sys.float_info.epsilon):
        v = (d22 * d01 - d21 * d20) / denom
        w = (d11 * d20 - d21 * d01) / denom
        u = 1 - v - w

    if (it < attempts):
        vtx0New = vtx0 + (vtx0 - p) * 10.0
        vtx1New = vtx1 + (vtx1 - p) * 10.0
        vtx2New = vtx2 + (vtx2 - p) * 10.0

        it = it+1
        return computeBarycentricCoords(p, vtx0New, vtx1New, vtx2New, attempts, it)

    return False


def closestPointOnTriangle(p, a, b, c):
    ab = b - a
    ac = c - a
    ap = p - a

    d1 = ab * ap
    d2 = ac * ap
    if (d1 <= sys.float_info.epsilon and d2 <= sys.float_info.epsilon):
        return a

    bp = p - b
    d3 = ab * bp
    d4 = ac * bp
    if (d3 >= sys.float_info.epsilon and d4 <= d3):
        return b

    vc = d1*d4 - d3*d2
    if (vc <= sys.float_info.epsilon and d1 >= sys.float_info.epsilon and d3 <= sys.float_info.epsilon):
        v = d1 / (d1 - d3)
        return a + v * ab

    cp = p - c
    d5 = ab * cp
    d6 = ac * cp

    if (d6 >= sys.float_info.epsilon and d5 <= d6):
        return c

    vb = d5 * d2 - d1 * d6
    if (vb <= sys.float_info.epsilon and d2 >= sys.float_info.epsilon and d6 <= sys.float_info.epsilon):
        w = d2 / (d2 - d6)
        return a + w * ac

    va = d3 * d6 - d5 * d4
    if (va <= sys.float_info.epsilon and (d4 - d3) >= sys.float_info.epsilon and (d5 - d6) >= sys.float_info.epsilon):
        w = (d4 - d3) / ((d4 - d3) + (d5 - d6))
        return b + w * (c - b)

    denom = 1.0 / (va + vb + vc)
    v = vb * denom
    w = vc * denom
    return a + ab * v + ac * w
