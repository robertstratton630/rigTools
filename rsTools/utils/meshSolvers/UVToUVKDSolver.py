import maya.api.OpenMaya as om
import rsTools.utils.openMaya.transform as transform
import rsTools.utils.transforms.transforms as tUtils
import rsTools.utils.data.string as string
import rsTools.utils.openMaya.matrix as mUtils
import rsTools.utils.openMaya.mesh as meshUtils
import rsTools.utils.openMaya.omWrappers as omUtils
import rsTools.utils.openMaya.dataUtils as dUtils

from rsTools.utils.kdtree.kdtree import KdTree

from rsTools.utils.meshSolvers.solverUtils import computeBarycentricCoords
from rsTools.utils.meshSolvers.solverUtils import closestPointOnTriangle
from rsTools.utils.meshSolvers.result import ClosestPointResult
from rsTools.utils.meshSolvers.result import ClosestUVResult
import sys
import time

from rsTools.utils.openMaya.vec2 import Vec2

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class UVToUVKDSolver(object):
    def __init__(self, mesh=None, fileData=None):

        self._results = []
        self._intersector = None
        self._mesh = None
        self._initalized = False
        self._kdTree = None

        # polygonCount
        self._triangleVertIDs = None
        self._triangleVertUVs = None

        # num triID's
        self._triangleCentersUV = None
        self._triIDtoPolyID = None
        self._triIDInsidePolyID = None

        if mesh and cmds.objExists(mesh):
            self.setMesh(mesh)
        elif fileData:
            self.setFileData(fileData)

    def setMesh(self, mesh):
        data = meshUtils.getGeometryUVData(mesh)
        self._triangleVertIDs = data.get("triangleVertIDs")
        self._triangleVertUVs = data.get("triangleVertUVs")
        self._triangleCentersUV = data.get("triangleCentersUV")
        self._triIDtoPolyID = data.get("triIDtoPolyID")
        self._triIDInsidePolyID = data.get("triIDInsidePolyID")

        self._kdTree = KdTree(self._triangleCentersUV, dim=2)
        self._initalized = True

    def setFileData(self, fileData):
        self._triangleVertIDs = fileData.get("triangleVertIDs")
        self._triangleVertUVs = fileData.get("triangleVertUVs")
        self._triangleCentersUV = fileData.get("triangleCentersUV")
        self._triIDtoPolyID = fileData.get("triIDtoPolyID")
        self._triIDInsidePolyID = fileData.get("triIDInsidePolyID")

        self._kdTree = KdTree(self._triangleCentersUV, dim=2)
        self._initalized = True

    def run(self, sourceUVs, verbose=False):
        if self.initalized():
            t1 = time.time()
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

                uvw = computeBarycentricCoords(
                    bestUV, bestUV0, bestUV1, bestUV2)
                if uvw:

                    result = ClosestUVResult(uvA=bestUV0,
                                             uvB=bestUV1,
                                             uvC=bestUV2,
                                             uvAIndex=triVtxID0,
                                             uvBIndex=triVtxID1,
                                             uvCIndex=triVtxID2,
                                             baryWeights=uvw,
                                             )

                    self._results.append(result)

                else:
                    self._results.append(None)
            evalTime = time.time() - t1
            _logger.info("Finished Calculating KD In : {0}".format(evalTime))

    def getResults(self, idx=None):
        if idx:
            return self._results[idx]
        else:
            return self._results

    def initalized(self):
        return self._initalized


'''   
import maya.cmds as cmds        
solver = UVToUVKDSolver("pSphere1")
solver.run([Vec2(0.5,0.5)])

results = solver.getResults()[0]

bary = results.getBaryWeights()
point = results.getPoint()
faceID = results.getFaceID()
faceTriID = results.getFaceTriangleID()
normal = results.getNormal()
triPolyVertexIDs = results.getTriPolyVertexIDs()

loc = cmds.spaceLocator()
cmds.xform(loc,ws=True,t = point)
'''
