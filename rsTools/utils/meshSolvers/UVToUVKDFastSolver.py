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
from rsTools.utils.meshSolvers.result import ClosestUVResult
import sys
import maya.cmds as cmds

from rsTools.utils.openMaya.vec2 import Vec2


class UVToUVKDFastSolver(object):
    def __init__(self, mesh=None, targetUVs=None):

        self._results = []
        self._intersector = None
        self._mesh = None
        self._initalized = False
        self._kdTree = None

        self._vertUVs = None

        if mesh and cmds.objExists(mesh):
            self.setMesh(mesh)
        elif targetUVs:
            self.setTargetUVs(targetUVs)

    def setMesh(self, mesh):
        sharedUVs = meshUtils.getSharedUVs(mesh)
        self._vertUVs = sharedUVs
        self._kdTree = KdTree(sharedUVs, dim=2)
        self._initalized = True

    def setTargetUVs(self, targetUVs):
        self._vertUVs = targetUVs
        self._kdTree = KdTree(self._vertUVs, dim=2)
        self._initalized = True

    def run(self, sourceUVs):
        if self.initalized():
            for queryUV in sourceUVs:
                data = self._kdTree.getClosest(queryUV, 10)

                print "DATA LEN {0}".format(len(data))

                # try to find the best matching triangle
                bestUV0 = self._vertUVs[data[0][1]]
                bestUV1 = self._vertUVs[data[1][1]]
                bestUV2 = self._vertUVs[data[2][1]]

                bestID = 2
                bestQuery = queryUV
                bestDistance = sys.float_info.max
                for i in range(2, len(data)):
                    print i
                    nextClosest = self._vertUVs[data[i][1]]
                    newQueryUV = closestPointOnTriangle(
                        queryUV, bestUV0, bestUV1, bestUV2)
                    PQ = queryUV - newQueryUV
                    distance = PQ.length()
                    if (distance < bestDistance):
                        bestUV2 = nextClosest
                        bestID = i
                        bestQuery = newQueryUV

                print "got best match"
                # snap onto triangle to make sure
                closestUV = closestPointOnTriangle(
                    bestQuery, bestUV0, bestUV1, bestUV2)
                print closestUV

                uvw = computeBarycentricCoords(
                    closestUV, bestUV0, bestUV1, bestUV2, attempts=5)
                print "got new bary"
                if uvw:
                    result = ClosestUVResult(uvA=bestUV0,
                                             uvB=bestUV1,
                                             uvC=bestUV2,
                                             uvAIndex=data[0][1],
                                             uvBIndex=data[1][1],
                                             uvCIndex=bestID,
                                             baryWeights=uvw,
                                             )

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
