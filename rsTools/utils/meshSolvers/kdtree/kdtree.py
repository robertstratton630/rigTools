import maya.cmds as mc
import maya.cmds as cmds

import maya.api.OpenMaya as om

import rsTools.utils.openMaya.mesh as mUtils
import rsTools.utils.meshSolvers.solverUtils as eUtils
import time
from math import sqrt
from copy import deepcopy

class Pt( object ):
	def __init__(self, pnt, ind):
		self.pnt = deepcopy(pnt)
		self.ind = ind

class _Node(list):
	'''
	Simple wrapper around tree nodes - mainly to make the code a little more readable (although
	members are generally accessed via indices because its faster)
	'''
	
	@property
	def point( self ): return self[0]
	@property
	def left( self ): return self[1]
	@property
	def right( self ): return self[2]
	
	def is_leaf( self ):
		return self[1] is None and self[2] is None

class ExactMatch(Exception): pass

class KdTree():

    def __init__( self,points,dim=3):
        self.dim = dim
        self.setPoints(points)
	
    def setPoints( self,points):
        t1 = time.time()
        
        meshPtList = []
        if self.dim ==2:
            for i,pnt in enumerate(points):
                meshPtList.append(Pt([pnt[0],pnt[1]],i))
        else:
            for i,pnt in enumerate(points):
                meshPtList.append(Pt([pnt[0],pnt[1],pnt[2]],i))

        def populateTree( points, depth ):
            '''
            '''
            if not points: return None

            axis = depth % self.dim

            # NOTE: this is slower than a DSU sort, but its a bit more readable, and the difference is only a few percent...
            points.sort( key=lambda point: point.pnt[ axis ] )

            # Find the half way point
            half = len( points ) / 2

            node = _Node( [ points[ half ],
                            populateTree( points[ :half ], depth+1 ),
                            populateTree( points[ half+1: ], depth+1 ) ] )

            return node
            
            

        self.root = populateTree(meshPtList,0)
        elapsed = time.time()-t1
        print 'KD Tree Set: ', elapsed, 'seconds.'
	
    def getClosest( self, queryPoint, numResults=5):
        '''
        Returns the closest point in the tree to the given point
        NOTE: see the docs for getWithin for info on the returnDistances arg
        '''
        dimension = self.dim
        
        if dimension == 3:
            distBest = ((self.root[0].pnt[0]-queryPoint[0]) ** 2) + ((self.root[0].pnt[1]-queryPoint[1]) ** 2) + ((self.root[0].pnt[2]-queryPoint[2]) ** 2)
        else:
            distBest = ((self.root[0].pnt[0]-queryPoint[0]) ** 2) + ((self.root[0].pnt[1]-queryPoint[1]) ** 2)
        
        
        bestList = [ (distBest, 0) ]
        def search( node, depth ):
            '''
            '''
            nodePoint = node[0].pnt            
            axis = depth % dimension

            if queryPoint[axis] < nodePoint[axis]:
                nearNode = node[1]
                farNode = node[2]
            else:
                nearNode = node[2]
                farNode = node[1]

            # Start Search
            if nearNode is not None:
                search( nearNode, depth+1 )

            # Get squared distance
            distance = 0
            for v1, v2 in zip( nodePoint, queryPoint ):
                distance += (v1 - v2)**2
             
            curBest = bestList[0][0]
            
            # If the point is closer than the currently stored one, insert it at the head
            if distance < curBest:
                bestList.insert( 0, (distance, node[0].ind) )
                if not distance:
                    raise ExactMatch
            else:
                bestList.append( (distance, node[0].ind) )
                            

            # Check whether there could be any points on the other side of the
            # splitting plane that are closer to the query point than the current best
            if farNode is not None:
                if (nodePoint[ axis ] - queryPoint[ axis ])**2 < curBest:
                    search( farNode, depth+1 )

        try:
            search( self.root, 0 )
        except ExactMatch: pass
        
        bestList.sort(key=lambda x: x[0]) 
        
        return bestList[0:numResults]
