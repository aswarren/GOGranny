from GOGranny import *
from networkx import *
import unittest

class TestSteinerTree(unittest.TestCase):
    def stree(self, edges, voi):
        g = Graph()
	for edge in edges:
	    g.add_edge(edge[0],edge[1],weight=edge[2])
	return make_steiner_tree(g, voi)

    def testSteinerTrees(self):
	edges = [("a", "b", 1), ("a", "c", 5), ("a", "e", 2), ("a", "d", 2), ("b", "c", 2), ("c", "d", 3), ("e", "d", 6)]
	st = self.stree(edges, ['c', 'e', 'a'])

	self.failUnless(st.edges(data=True) == [('a', 'b',{'weight':1}), ('a', 'e', {'weight':2}), ('c', 'b', {'weight':2})])
	
	edges = [('a', 'b', 3), ('b', 'c', 4), ('c', 'd', 5), ('a', 'e', 1), ('e', 'd', 1)]
	st = self.stree(edges, ['b', 'd'])
        
	self.failUnless(st.edges(data=True) == [('a', 'b', {'weight':3}), ('a', 'e',{'weight':1}), ('e', 'd', {'weight':1})])
	
	edges = [('a', 'b', 4), ('a', 'c', 4), ('b', 'c', 4)]
	st = self.stree(edges, ['a', 'b', 'c'])
	self.failUnless(st.edges(data=True) == [('a', 'c', {'weight':4}), ('a', 'b', {'weight':4})])
	
	# from the markowsky paper
	edges = [('v1', 'v9', 1), ('v1', 'v2', 10), ('v8', 'v9', .5), ('v9', 'v5', 1), ('v8', 'v7', .5), ('v7', 'v6', 1), ('v6', 'v5', 1), ('v2', 'v6', 1),
		 ('v2', 'v3', 8), ('v3', 'v5', 2), ('v5', 'v4', 2), ('v3', 'v4', 9)]
	st = self.stree(edges, ['v1', 'v2', 'v3', 'v4'])
	self.failUnless(st.edges(data=True) == [('v1', 'v9', {'weight':1}), ('v2', 'v6', {'weight':1}), ('v3', 'v5', {'weight':2}), ('v4', 'v5', {'weight':2}), ('v5', 'v9', {'weight':1}), ('v5', 'v6', {'weight':1})])
	
	edges = [('a', 'b', 0), ('b', 'c', 0), ('a', 'd', 3), ('b', 'd', 3), ('c', 'd', 3)]
	st = self.stree(edges, ['a', 'b', 'c', 'd'])
	self.failUnless(st.edges(data=True) == [('a', 'b', {'weight':0}), ('a', 'd', {'weight':3}), ('c', 'b', {'weight':0})])
	
	edges = [('a', 'b', 0), ('b', 'c', 0), ('a', 'd', 3), ('b', 'd', 3), ('c', 'd', 3), ('d', 'e', 1)]
	st = self.stree(edges, ['a', 'b', 'c', 'e'])
	self.failUnless(st.edges(data=True) == [('a', 'b', {'weight':0}), ('a', 'd', {'weight':3}), ('c', 'b', {'weight':0}), ('e', 'd', {'weight':1})])
