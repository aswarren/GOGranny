import unittest
import networkx as nx
from GOGranny import *
import random
from utils import *
from math import log
from GOGranny.GONode import GONode as GN

class semGODiGraphTest(unittest.TestCase):
    def setUp(self):
        self.aspect = Aspects.BP
        self.graph = semGODiGraph(None, self.aspect)

    def testMax(self, n=7):
	#create star graph for maximum case
	internal_graph=nx.star_graph(n-1) #n+1 nodes created for star so 16  #gnp_random_graph(10,0.5,directed=True)
	for u,v in internal_graph.edges_iter():
		self.graph.add_edge(GN(nodetype=GN.TERM_TYPE,dbid=u),GN(nodetype=GN.TERM_TYPE,dbid=v))
	nx.reverse(self.graph, copy=False)
	root_list=[n for n,d in self.graph.out_degree().items() if d==0]
	self.failUnless(len(root_list)==1)
	self.graph.root=root_list[0]
	self.graph.semMakeGraph()
	graph_entropy=self.graph.calc_graph_uncert()
	nn=float(self.graph.num_nodes)
	self.failUnless(graph_entropy < -2*log(1/nn,2))
	self.failUnless(graph_entropy == -1*log(1/nn,2)-((nn-1)/nn)*(log(1/(nn-2),2)))

    def testMin(self, n=16):
	#create line graph for minimum case
	for u in range(0,n-2):
		v=u+1
		self.graph.add_edge(GN(nodetype=GN.TERM_TYPE,dbid=v),GN(nodetype=GN.TERM_TYPE,dbid=u))
	#nx.reverse(self.graph, copy=False)
	root_list=[n for n,d in self.graph.out_degree().items() if d==0]
	self.failUnless(len(root_list)==1)
	self.graph.root=root_list[0]
	self.graph.semMakeGraph()
	graph_entropy=self.graph.calc_graph_uncert()
	self.failUnless(graph_entropy == -1*log(1/float(self.graph.num_nodes),2))

    def testTree(self, r=2, h=2):
	internal_graph=nx.balanced_tree(r=r,h=h,create_using=nx.DiGraph()) #gnp_random_graph(10,0.5,directed=True)
	for u,v in internal_graph.edges_iter():
		self.graph.add_edge(GN(nodetype=GN.TERM_TYPE,dbid=u),GN(nodetype=GN.TERM_TYPE,dbid=v))
	nx.reverse(self.graph, copy=False) #make the edges point up not down
	root_list=[n for n,d in self.graph.out_degree().items() if d==0]
	self.failUnless(len(root_list)==1)
	self.graph.root=root_list[0]
	self.graph.semMakeGraph()
	graph_entropy=self.graph.calc_graph_uncert()
	graph_max=-2*log(1/float(self.graph.num_nodes),2)
	graph_min=-1*log(1/float(self.graph.num_nodes),2)
	print "num nodes:"+str(self.graph.num_nodes)+" entropy:"+str(graph_entropy)
	nn=float(self.graph.num_nodes)
	component1=-1*log(1/nn,2)
        component2=-((r**h)/nn)*log(1/float(nn-h-1),2)
        component3=-sum([((r**i)/nn)*log(1/float(nn-i-r**(h-i)-1),2) for i in range(1,h)])
	test_entropy=component1+component2+component3
	self.failUnless(graph_min < graph_entropy < graph_max)
	self.failUnless(graph_entropy == test_entropy )

if __name__ == '__main__':
    unittest.main()
	
	


