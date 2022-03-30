
import maya.api.OpenMaya as om


import rsTools.utils.data.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.openMaya.dataUtils as dUtils
from rsTools.utils.kdtree.kdtree import KdTree

from rsTools.utils.meshSolvers.evaluatorUtils import computeBarycentricCoords
from rsTools.utils.meshSolvers.evaluatorUtils import closestPointOnTriangle
from rsTools.utils.meshSolvers.result import ClosestPointResult
import sys


class ClosestPointKDSolver(object):

    def __init__(self, mesh=None):

        self._results = []
        self._intersector = None
        self._mesh = None
        self._initalized = False
        self._kdTree = None

        self._targetPoints = None

        # polygonCount
        self._triangleVertIDs = None

        # num triID's
        self._triangleCenters = None
        self._triIDtoPolyID = None
        self._triIDInsidePolyID = None

        if mesh and cmds.objExists(mesh):
            self.setMesh(mesh)

    def getResults(self, idx=None):
        if idx:
            return self._results[idx]
        else:
            return self._results

    def initalized(self):
        return self._initalized

    def setMesh(self, mesh):
        # get points and triangle data
        points = meshUtils.getPoints(mesh, True)
        self._targetPoints = points
        trianglesPerPoly, triangleIndices = meshUtils.getTrianglesData(mesh)

        # create hash table of indices
        numTriangles = 0
        numPolygons = len(trianglesPerPoly)
        triStartIDs = []

        for poly in range(numPolygons):
            triStartIDs.append(numTriangles)
            numTriangles += trianglesPerPoly[poly]

        self._triangleCenters = [None]*numTriangles
        self._triIDtoPolyID = [None]*numTriangles
        self._triIDInsidePolyID = [None]*numTriangles
        self._triangleVertIDs = [None]*numPolygons

        if numTriangles > 0.0:
            # loop polys
            for poly in range(numPolygons):
                self._triangleVertIDs[poly] = [
                    None]*(trianglesPerPoly[poly] * 3)

                # loop triangles
                for tri in range(trianglesPerPoly[poly]):
                    # get the triangle index
                    indexTri = triStartIDs[poly] + tri
                    center = om.MPoint()
                    vtx = om.MPoint()

                    for v in range(3):
                        vtx = om.MPoint(
                            points[triangleIndices[indexTri * 3 + v]])
                        center += vtx
                        self._triangleVertIDs[poly][tri * 3 +
                                                    v] = triangleIndices[indexTri * 3 + v]

                    center *= 1.0 / 3.0

                    self._triangleCenters[indexTri] = center
                    self._triIDtoPolyID[indexTri] = poly
                    self._triIDInsidePolyID[indexTri] = tri

            self._kdTree = KdTree(self._triangleCenters)
            self._initalized = True

    def run(self, sourcePoints):
        if self.initalized():
            for point in sourcePoints:
                data = self._kdTree.getClosest(point, 6)

                print "DATA LEN {0}".format(len(data0))

                # GET THE CLOSEST IDS AND DISTANCES

                bestTriID = -1
                bestDistance = sys.float_info.max
                bestPoint = om.MVector()

                for d in data:
                    # get the polyID and triID of the best tri index
                    polyID = self._triIDtoPolyID[d[1]]
                    triID = self._triIDInsidePolyID[d[1]]

                    triVtxID0 = self._triangleVertIDs[polyID][triID * 3 + 0]
                    triVtxID1 = self._triangleVertIDs[polyID][triID * 3 + 1]
                    triVtxID2 = self._triangleVertIDs[polyID][triID * 3 + 2]

                    queryPoint = om.MVector(point)
                    pointVtxID0 = om.MVector(self._targetPoints[triVtxID0])
                    pointVtxID1 = om.MVector(self._targetPoints[triVtxID1])
                    pointVtxID2 = om.MVector(self._targetPoints[triVtxID2])

                    point = closestPointOnTriangle(
                        queryPoint, pointVtxID0, pointVtxID1, pointVtxID2)
                    PQ = queryPoint - point
                    distance = PQ.length()
                    if (distance < bestDistance):
                        bestTriID = d[1]
                        bestPoint = point
                        bestDistance = distance

                polyID = self._triIDtoPolyID[bestTriID]
                triID = self._triIDInsidePolyID[bestTriID]

                triVtxID0 = self._triangleVertIDs[polyID][triID * 3 + 0]
                triVtxID1 = self._triangleVertIDs[polyID][triID * 3 + 1]
                triVtxID2 = self._triangleVertIDs[polyID][triID * 3 + 2]

                triPolyVertexIDs = [triVtxID0, triVtxID1, triVtxID2]

                pointVtxID0 = om.MVector(self._targetPoints[triVtxID0])
                pointVtxID1 = om.MVector(self._targetPoints[triVtxID1])
                pointVtxID2 = om.MVector(self._targetPoints[triVtxID2])

                normal = (pointVtxID1 -
                          pointVtxID0) ^ (pointVtxID2 - pointVtxID0)
                uvw = computeBarycentricCoords(
                    bestPoint, pointVtxID0, pointVtxID1, pointVtxID2)
                output = ClosestPointResult(faceID=polyID, faceTriangleID=triID,
                                            triPolyVertexIDs=triPolyVertexIDs, point=bestPoint, normal=normal, baryWeights=uvw)

                if output:
                    self._results.append(output)


'''        
import maya.cmds as cmds        
evalu = ClosestPointKDSolver("pSphere1")
xform = cmds.xform("locator1",q=True,ws=True,t=True)
pt = evalu.run([xform])
'''
