import maya.api.OpenMaya as om
import rsTools.utils.openMaya.transform as transform
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.data.string as sUtils
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.openMaya.dataUtils as dUtils

from rsTools.utils.kdtree.kdtree import KdTree

from rsTools.utils.meshSolvers.solverUtils import computeBarycentricCoords
from rsTools.utils.meshSolvers.solverUtils import closestPointOnTriangle
from rsTools.utils.meshSolvers.result import ClosestPointResult

import sys

from rsTools.utils.openMaya.vec2 import Vec2


class UVToPointKDSolver(object):

    def __init__(self, mesh=None):

        self._results = []
        self._intersector = None
        self._mesh = None
        self._initalized = False
        self._kdTree = None

        self._targetPoints = None

        # polygonCount
        self._triangleVertIDs = None
        self._triangleVertUVs = None

        # num triID's
        self._triangleCentersUV = None
        self._triIDtoPolyID = None
        self._triIDInsidePolyID = None

        if mesh and cmds.objExists(mesh):
            self.setMesh(mesh)

    def setMesh(self, mesh):
        # get points and triangle data
        points = meshUtils.getPoints(mesh, True)
        self._targetPoints = points
        trianglesPerPoly, triangleIndices = meshUtils.getTrianglesData(mesh)

        fnMesh = meshUtils.getMeshFn(mesh)

        # create hash table of indices
        numTriangles = 0
        numPolygons = len(trianglesPerPoly)
        triStartIDs = []

        for poly in range(numPolygons):
            triStartIDs.append(numTriangles)
            numTriangles += trianglesPerPoly[poly]

        if numTriangles > 0:

            self._triangleCentersUV = [None]*numTriangles
            self._triIDtoPolyID = [None]*numTriangles
            self._triIDInsidePolyID = [None]*numTriangles

            self._triangleVertIDs = [None]*(numTriangles * 3)
            self._triangleVertUVs = [Vec2()]*(numTriangles * 3)

            # loop polys
            for poly in range(numPolygons):
                # get the poly vertex
                polyVtxs = fnMesh.getPolygonVertices(poly)

                # loop triangles
                for tri in range(trianglesPerPoly[poly]):
                    # get the triangle index
                    indexTri = triStartIDs[poly] + tri

                    center = Vec2()
                    idx = -1

                    # loop over the triangle vertex and if it matches the poly vertex break
                    for v in range(3):
                        for i, polyVert in enumerate(polyVtxs):
                            if polyVert == triangleIndices[indexTri * 3 + v]:
                                idx = i
                                break

                        # get the UV at that point
                        uv = fnMesh.getPolygonUV(poly, idx)
                        uvVec = Vec2(uv[0], uv[1])
                        self._triangleVertUVs[indexTri * 3 + v] = uvVec
                        self._triangleVertIDs[indexTri * 3 +
                                              v] = triangleIndices[indexTri * 3 + v]
                        center += uvVec

                    # average center
                    center = center / 3.0

                    self._triangleCentersUV[indexTri] = center
                    self._triIDtoPolyID[indexTri] = poly
                    self._triIDInsidePolyID[indexTri] = tri

            self._kdTree = KdTree(self._triangleCentersUV, dim=2)
            self._initalized = True

    def run(self, sourceUVs):
        if self.initalized():
            for queryUV in sourceUVs:
                data = self._kdTree.getClosest(queryUV, 5)

                # for storing best results
                bestTriID = -1
                bestDistance = sys.float_info.max
                bestUV = Vec2()

                # loop on the best results from kdTree
                for d in data:
                    indexTri = d[1] * 3
                    triVtxUVID0 = self._triangleVertUVs[indexTri + 0]
                    triVtxUVID1 = self._triangleVertUVs[indexTri + 1]
                    triVtxUVID2 = self._triangleVertUVs[indexTri + 2]

                    closestUV = closestPointOnTriangle(
                        queryUV, triVtxUVID0, triVtxUVID1, triVtxUVID2)

                    vec = queryUV - closestUV
                    distance = vec.length()
                    if (distance < bestDistance):
                        bestResult = d[1]
                        bestDistance = distance
                        bestUV = closestUV

                indexTri = bestResult * 3
                polyID = self._triIDtoPolyID[bestResult]
                triID = self._triIDInsidePolyID[bestResult]

                bestUV0 = self._triangleVertUVs[indexTri + 0]
                bestUV1 = self._triangleVertUVs[indexTri + 1]
                bestUV2 = self._triangleVertUVs[indexTri + 2]

                triVtxID0 = self._triangleVertIDs[indexTri + 0]
                triVtxID1 = self._triangleVertIDs[indexTri + 1]
                triVtxID2 = self._triangleVertIDs[indexTri + 2]

                triPolyVertexIDs = [triVtxID0, triVtxID1, triVtxID2]

                pointVtxID0 = om.MVector(self._targetPoints[triVtxID0])
                pointVtxID1 = om.MVector(self._targetPoints[triVtxID1])
                pointVtxID2 = om.MVector(self._targetPoints[triVtxID2])

                uvw = computeBarycentricCoords(
                    bestUV, bestUV0, bestUV1, bestUV2)
                if uvw:
                    oPoint = pointVtxID0 * \
                        uvw[0] + pointVtxID1 * uvw[1] + pointVtxID2 * uvw[2]
                    oNormal = (pointVtxID1 -
                               pointVtxID0) ^ (pointVtxID2 - pointVtxID0)

                    result = ClosestPointResult(faceID=polyID,
                                                faceTriangleID=triID,
                                                triPolyVertexIDs=triPolyVertexIDs,
                                                point=oPoint,
                                                normal=oNormal,
                                                baryWeights=uvw)

                    self._results.append(result)

                else:
                    self._results.append(None)

    def getResults(self, idx=None):
        if idx:
            return self._results[idx]
        else:
            return self._results

    def initalized(self):
        return self._initalized
