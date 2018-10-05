#class with two way transitive closure (ancestors and descendants) computed for nodes for the purpose of calculating the Graph Entropy
#author: Andrew Warren aswarren@gmail.com

#NOTE: There are obsolete terms. Not in the graph itself and not in the nodes or node iterator but in the term lookup table (node_lookup)

from GOGranny import GODiGraph
from GOGranny import Aspects
from GOGranny import GONode
from math import log
import shelve, cPickle
import sys

#this class computes the transitive closure on all nodes
#and is used for computing the IC and term similarity for all nodes
class semGODiGraph(GODiGraph):

	def __init__(self, storage, aspect=Aspects.BP, storage_path="none"):
		GODiGraph.__init__(self, storage, species="none", aspect=aspect)#no species
		#for retreiving the node by GOID
		self.storage_path=storage_path
		self.leaves=set()
		self.tranState=False #transitive closure has not been calc.
		#adds prob, suprisal, and gIC to each node
		self.totalSuprisal=0
		self.avgSuprisal=0
		self.maxGraphIC=0
		self.num_nodes=0
	def semMakeGraph(self):
		self.check_closure()
		self.num_nodes=self.number_of_nodes()
	def makeGraph(self, annotatedTermsOnly=False):
		self.node_lookup=GODiGraph.makeGraph(self, annotatedTermsOnly)
		self.semMakeGraph()

	##Compute the transitive closure of the graph so that the graph based information content can be calculated
	#also determines which nodes are leaves
	#Stores a set of ancestors and descendants at each node: each set is made up of node pointers
	#DFS traversal
	def trans_closure(self, currentNode, seenabove):
		if hasattr(currentNode, 'ancestors'):
			currentNode.ancestors=currentNode.ancestors.union(seenabove)
		else:
			currentNode.ancestors=seenabove.copy()
		seenabove.add(currentNode)
		seenbelow=set()
		for c in self.predecessors(currentNode):
			seenbelow.add(c)
			seenbelow=seenbelow.union(self.trans_closure(c,seenabove.copy()))
		currentNode.descendants=seenbelow.copy()
		if len(currentNode.descendants)==0:
			self.leaves.add(currentNode)
			currentNode.leaf = True
		return seenbelow.copy()

	##Check if the trans_closure has been computed and if not do it
	def check_closure(self):
		if(not self.tranState):
			root_ancestor=set()
			self.trans_closure(self.root, root_ancestor)
			self.tranState=True

	##converts the aspect type of the ontology into a string
	def getAspect(self):
		if(self.aspect==Aspects.BP):
			return "BP"
		elif(self.aspect==Aspects.CC):
			return "CC"
		elif(self.aspect==Aspects.MF):
			return "MF"

	##Determine the uncertainty of the graph when a term is asserted as true for a gene
	##If no ID is given then the uncertainty of the entire graph is determined
	##Parameters: the node for GO term asserted to be true
	##whether to exclude the descendants of the node
	##WARNING: this function can also be affected by the obsolete term issue
	##setting annot_node excludes ancestors
	##setting annot_node and exclude_dec=True excludes ancestors and descendants
	##setting reroot calculates the entropy of the graph rooted at that node
	def calc_graph_uncert(self, annot_node=None, exclude_dec=False, reroot=None, invroot=None):
		num_induced=0
		excluded=set()
		to_subtract=0
		num_desc=0
		result=0
		contribution=0
		dep_uncert=0#the dependent uncertainty
		
		#be careful getting references to sets Ancenstors and Descendants!
		
		if reroot:
			sub_graph=self.getDecCopy(reroot)
			sub_graph.add(reroot)
			anc_ignore=self.getAnc(reroot)
			cur_num_nodes=len(sub_graph)
			init_prob=1/float(cur_num_nodes)
			init_uncert=-(log(init_prob)/log(2))
			for j in sub_graph:
				induced_nodes=self.getAnc(j).intersection(sub_graph)
				j_num_induce=len(induced_nodes)
				j_num_desc=len(self.getDec(j))
				if len(sub_graph)==(j_num_induce+j_num_desc):
					j_probability=1
				else: j_probability=1/float(len(sub_graph)-j_num_induce-j_num_desc)
				contribution+= -log(j_probability)/log(2)
			dep_uncert=contribution*init_prob #probability that a block is active * the conditional entropy when it is active
			result=dep_uncert+init_uncert
		elif invroot:
			sub_graph=self.getAncCopy(invroot)
			sub_graph.add(invroot)
			cur_num_nodes=len(sub_graph)
			init_prob=1/float(cur_num_nodes)
			init_uncert=-(log(init_prob)/log(2))
			for k in sub_graph:
				induced_nodes=self.getAnc(k)#.intersection(sub_graph) no intersect needed since truepath
				k_num_induce=len(induced_nodes)
				k_num_desc=len(self.getDec(k).intersection(sub_graph))
				if len(sub_graph)==(k_num_induce+k_num_desc):
					k_probability=1
				else: k_probability=1/float(len(sub_graph)-k_num_induce-k_num_desc)
				contribution+= -log(k_probability)/log(2)
			dep_uncert=contribution*init_prob #probability that a block is active * the conditional entropy when it is active
			result=dep_uncert+init_uncert
		else:
			if(annot_node != None):
				excluded=self.getAnc(annot_node)#get the ancestors of the node
				if exclude_dec: excluded=excluded.union(self.getDec(annot_node))
				num_induced=len(excluded)#not +1 because though +1 for itself -1 for the root node which should always be present
				#num_desc+=len(self.getDec(annot_node)) #do not need to get the number of descendants for the previous annotation

			cur_num_nodes=self.num_nodes-num_induced#the number of nodes currently in the graph given a previous annotation
			init_prob=1/float(cur_num_nodes)#initial probability is 1/number of nodes left in ontology
			init_uncert=-(log(init_prob)/log(2))# since all the nodes have equal probability the average ends up being -log P		
			#for every node in the ontology get its contribution to the annotation uncertainty
			#this part skips the inner loop because the summation will just be the -log(j_prob)
			num_root=0
			for j in self.nodes_iter():
				if (not j in excluded) and (not j == annot_node):#if this term is in the ancestors induced by a node it has a probability of 1 and uncertainty of 0
					induced_nodes=self.getAnc(j).union(excluded).union(set([j]))#get the number of nodes that cannot follow this one in an annotation
					if annot_node != None: induced_nodes.add(annot_node)
					j_num_induce=len(induced_nodes)
					j_num_desc=len(self.getDec(j))
					if (j_num_induce == 0):
						num_root+=1
						assert num_root <= 1
					if(self.num_nodes==j_num_induce+j_num_desc):
						j_probability=1
					else: j_probability=1/float(self.num_nodes-j_num_induce-j_num_desc)
					contribution+= -log(j_probability)/log(2)
			#		result+=(1/j_num_induce)
			dep_uncert=contribution*init_prob #probability that a block is active * the conditional entropy when it is active
			result=dep_uncert+init_uncert
		return result
		


	

	##For a set of nodes get all their ancestors
	#include the actual nodes themselves
	def nodeGetAllAnc(self, nodeset):
		result=set()
		for t in nodeset:
			result.add(t)
			result=result.union(t.ancestors)
		return result


	##For a set of nodes get all their descendants
	#include the actual nodes themselves
	def nodeGetAllDes(self, nodeset):
		result=set()
		for t in nodeset:
			result.add(t)
			result=result.union(t.descendants)
		return result



	##For a node retreive ancestors
	##WARNING: returns a reference to the ancestors set
	def getAnc(self, tnode):
		if tnode!= None and hasattr(tnode, 'ancestors'):
			return tnode.ancestors #this is a reference!
		else: return set()


	##For a node retreive descendants
	##WARNING: returns a reference to the descendants set
	def getDec(self, tnode):
		if tnode!= None and hasattr(tnode, 'descendants'):
			return tnode.descendants #this is a reference!
		else: return set()
		
	##For a node retreive ancestors
	def getAncCopy(self, tnode):
		return self.getAnc().copy()


	##For a node retreive descendants
	def getDecCopy(self, tnode):
		return self.getDec().copy()
		

	##For a set of terms get all their ancestors
	#include the actual terms themselves
	#WARNING: The code here should be changed to account for obsolete terms being called here
	#apparently nodes are still created for obsolete nodes
	#if the TERM IS OBSOLETE THEN AN EMPTY SET WILL BE RETURNED
	def getAllAnc(self, terms, include_self=True):
		result=set()
		for t in terms:
			if type(t) == GONode.GOTermNode:
				n = t
			else:
				n=self.idGetNode(t)
			if n!= None:
				if not hasattr(n, 'ancestors'):
					sys.stderr.write(str(n.dbid)+" does not have ancestors\n")
					return result
				if include_self:
					result.add(n)
				result=result.union(n.ancestors)
		return result
				

	##Get Node according to term id
	#storage structure tracks obsolete terms and auto_converts to suggested alternatives
	def idGetNode(self, term_id):
		if term_id == None:
			return None
		result=self.node_lookup.get(term_id, None)
		if term_id in self.aliases:
			sys.stderr.write("WARNING: Old GOID autoconverted from "+term_id+" to "+result.dbid+"\n")
		return result
				
