## \package GODiGraph  A directed graph representation of the Gene Ontology.
# \author Brian Muller <mullerb@musc.edu>
# \edited by Andrew Warren <aswarren@gmail.com> The makeGraph function returns the dictionary of nodes

#import networkx
from networkx import DiGraph, dfs_postorder_nodes, is_directed_acyclic_graph
from networkx import topological_sort, topological_sort_recursive

# imports local modules
from GOError import GOError, GOPercentMessage
from GOGraphBase import GOGraphBase
from GOGraph import GOGraph
import Aspects 
import DOMLight


## This class represents a directed graph based on the Gene Ontology information for a
# given species and aspect.  It is generally the first object created when using this
# library.
class GODiGraph(DiGraph, GOGraphBase):

    ## Constructor
    # @param storage An instance of an object extending Storage.StorageInterface
    # @param species The common name for the species being investigated
    # @param aspect Indicates which namespace this graph represents - one of the Aspects
    # have a descendant that is annotated.
    # /see Storage.StorageInterface
    # /see Aspects
    def __init__(self, storage, species, aspect=Aspects.BP):
        DiGraph.__init__(self, weighted=False)
        GOGraphBase.__init__(self, storage, species, aspect)
        self.root = None


    ## Create a GO directed graph.
    # @param annotatedTermsOnly Only keep nodes on the graph that are either annotated or that
    def makeGraph(self, annotatedTermsOnly=True):
        assoclist = self.storage.getTermAssocList(self.aspect)
        terms=self._makeGraph(assoclist, annotatedTermsOnly)
        self.checkGraph()
	return terms


    ## An internal function that should not be publicly called.  It creates the edges
    # in the graph given an association list.
    # @param assoclist A hash of lists - the hash key is the parent term id, and the hash value is the list of children ids            
    def _makeGraph(self, assoclist, annotatedTermsOnly):
        self.error.debug("Making a graph with %i initial nodes.  This might take a minute." % len(assoclist))
        # at this point we need to add edges between nodes - as we create the edge, networkx will add the nodes.  We'll go ahead and
        # make a hash of actual nodes as we go along so we only have to make each one once
        terms = {}
        self.root = None

        progress = GOPercentMessage(len(assoclist))
        for term_id, children_ids in assoclist.iteritems():
            progress.update()
            if not terms.has_key(term_id):
                terms[term_id] = self.storage.makeTerm(term_id)
            term = terms[term_id]
            # if this is the root node keep track of it            
            if self.root == None and term.goid == Aspects.ROOTS[self.aspect]:
                self.root = term
            
            for child_id in children_ids:
                if not terms.has_key(child_id):
                    terms[child_id] = self.storage.makeTerm(child_id)
                child = terms[child_id]
                # if this is the root node keep track of it
                if self.root == None and child.goid == Aspects.ROOTS[self.aspect]:
                    self.root = child
                self.add_edge(child, term)
        progress.finished()
        
        if self.root == None:
            self.error.handleFatal("Did not find root node of %s when generating graph.  Something is wrong..." % Aspects.ROOTS[self.aspect])

        if annotatedTermsOnly:
            self.removeUnannotatedTerms()

        if not is_directed_acyclic_graph(self):
            self.error.handleWarning("Resulting graph is not a DAG: This generally means something is wrong!")
            
        self.error.debug("Graph completed with %i nodes." % self.number_of_nodes())
	return terms #return the term lookup      


    # Only keep nodes on the graph that are either annotated or that have a descendant that is annotated.
    def removeUnannotatedTerms(self):
        self.error.debug("Removing unannotated terms from graph of size %i..." % len(self))
        self.error.debug("First, will sort graph...")
        rSortedV = topological_sort(self)
        self.error.debug("finished")
        if not rSortedV:
            self.error.handleWarning('Topological sort of GODiGraph failed: could not remove unannotated terms')


        # Normally, terms have a lazy lookup method for determining what proteins are associated with them,
        # i.e., the term doesn't find out unless you call node.getProteins.  We're going to ask storage to go ahead
        # and look them up explicitly now.
        self.storage.setTermsProteins(self.nodes(), self.species)

        count = 0
        for v in self.nodes_iter():
            if len(v.getProteins(self.species)) > 0:
                count += 1
        self.error.debug("There are %i nodes with proteins" %count)

        propProtCount = {}
        for node in self.nodes_iter():
            propProtCount[node.goid] = 0
        rSortedV.reverse()
        for v in rSortedV:
            numprots = len(v.getProteins(self.species)) + propProtCount[v.goid]
            for pred in self.predecessors_iter(v):
                propProtCount[pred.goid] += numprots

        unannotated = []
        for v in rSortedV:
            if propProtCount[v.goid] + len(v.getProteins(self.species)) == 0:
                unannotated.append(v)


        self.error.debug("Found %i unannotated terms, deleting them" % len(unannotated))
        for v in unannotated:
            self.remove_node(v)
                                


    ## Make this graph weighted using the weighting class.
    # @param weightingClass This is weighting class (not an instance, but the class itself)
    # /see XGraphWeighters.WeightingInterface
    def makeWeighted(self, weightingClass):
        wc = weightingClass(self.storage, self.species, self.aspect, directed=True)
        return wc.makeWeighted(self)



    ## Created an undirected version of this graph.
    # /returns A GOGraph
    def toUndirected(self):
        g = GOGraph(self.storage, self.species, self.aspect)
        for source, sink in self.edges_iter():
            g.add_edge(source, sink)
        return g



    ## A private function used to find orphan nodes.  It traverses all predecessors
    # starting from the given node  using depth first search 
    # @param currentNode The node to start from (usually called with the root)
    # \return A set of all ancestor nodes.
    def traversePredecessors(self, currentNode):
        seen = set()
        for c in self.predecessors(currentNode):
            seen.add(c)
            seen = seen.union(self.traversePredecessors(c))
        return seen


    ## Private function to check if the graph is fully connected to the root GO.
    # If not, trim the vertices that are not connected to the root
    def checkGraph(self):
        self.error.debug("Checking graph for orphans...")
        seen = set()
        seen = self.traversePredecessors(self.root)
        seen.add(self.root)

        if len(seen) != self.order():
            self.error.debug("There are %i nodes not connected to the root - removing them." % (self.order() - len(seen)))
            orphans = set(self.nodes()) - seen
            self.remove_nodes_from(orphans)


    ## A private function to create a pygraphviz AGraph.  This is an overwritten function used
    # within GOGraphBase.makeImage to make a png file of this graph.
    # /returns an AGraph
    def makeImageObject(self):
        try:
            from pygraphviz import AGraph
        except Exception, e:
            self.error.handleFatal("Could not import pygraphviz package.  If you're on windows, pygraphviz may not be installable.\n%s" % str(e))
        image = AGraph(directed=True)
        for edge in self.edges_iter():
            image.add_edge(*edge)
        return image
                                   

    ## Write an XGMML version of this graph to a file handle.  It can then be read by programs like
    # cytoscape.
    # @param fhandle An open file handle.
    # /see http://www.cs.rpi.edu/~puninj/XGMML/ for more information on XGMML.
    def toXGMML(self, fhandle):
        xml = DOMLight.XMLMaker()
        fhandle.write("""<?xml version="1.0" encoding="UTF-8"?>
        <graph xmlns="http://www.cs.rpi.edu/XGMML" directed="1" label="GOGranny Network">
        """)
        cid = 0
        goids = {}
        for node in self.nodes_iter():
            goids[node.goid] = cid
            fhandle.write(str(xml.node({'id': cid, 'label': node.goid})) + "\n")
            cid += 1
        count = 0
        for edge in self.edges_iter():
            fhandle.write(str(xml.edge({'source': goids[edge[0].goid], 'target': goids[edge[1].goid], 'label': ""})) + "\n")
            if count == 1000:
                break
            count += 1
        fhandle.write("</graph>")


    ## This method simplifies the process for directed graph traversal.  A given function will be called
    # for each source and sink of a directed edge with the source and sink as arguments.  The function is called
    # for source/sink at bottom of graph first (as in a depth first traversal).
    # @param func A function that accepts two arguments (the source and sink of a directed edge)
    def traverseWithDirection(self, func):
        sorted = list(dfs_postorder_nodes(self))
        for source in sorted:
            for sink in self.neighbors(source):
                func(source, sink)
