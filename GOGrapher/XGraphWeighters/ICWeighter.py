## \package XGraphWeighters.InformationContent
# A graph weighter that uses Information Content to assign
# weights to edges.
# \author Brian Muller <mullerb@musc.edu>      

from WeightingInterface import WeightingInterface
from networkx import topological_sort
from math import log

class ICWeighter(WeightingInterface):
    # should take edges from original unweighted originalGraph and add them
    # to self.graph but now with weights.
    # \returns a weighted graph (either GOXDiGraph or GOXGraph)
    def makeWeighted(self, originalGraph):
        self.error.debug("Making a weighted graph using information content")
        self.originalGraph = originalGraph
        
        self.propProtCount = {}
        self.propagateProteinCount()
        
        self.updateIC()
        # this will update self.graph
        self.updateEdgeDistances()
        self.error.debug("Finished weighting graph.")
        return self.graph


    def propagateProteinCount(self):
        self.error.debug("Propagating protein counts")
        rSortedV = topological_sort(self.originalGraph)
        if not rSortedV:
            self.error.handleFatal('Topological sort of GOXDiGraph failed')      


        for node in self.originalGraph.nodes_iter():
            self.propProtCount[node.goid] = 0
        rSortedV.reverse()
        for v in rSortedV:
            numprots = len(v.getProteins(self.originalGraph.species)) + self.propProtCount[v.goid]
            for pred in self.originalGraph.predecessors_iter(v):
                self.propProtCount[pred.goid] += numprots


    ## Instantiate the weight/distance of each edge of the new graph.
    # Currently, only word net kind semantic distance is used.
    # In future, more methods may be implemented for selection
    def updateEdgeDistances(self):
        self.error.debug("Updating edge distances...")

        # at this point IC has been updated,  using IC of the nodes to determine the semantic distance
        for node in self.originalGraph.nodes_iter():
            for predecessor in self.originalGraph.predecessor_iter(node):
                self.graph.add_edge(node, predecessor, weight = abs(node.infoContent - predecessor.infoContent))


    # Calculate the information content of each GONode in the graph
    def updateIC(self):
        self.error.debug("Updating each nodes information content value")      
        totalAnnotCount = len(self.originalGraph.root.getProteins(self.originalGraph.species)) + self.propProtCount[self.originalGraph.root.goid]
        self.originalGraph.root.totalAnnotCount=totalAnnotCount

        # Go through all the nodes and call their updateInfoContent the IC
        for node in self.originalGraph.nodes_iter():
            protCount = len(node.getProteins(self.originalGraph.species)) + self.propProtCount[node.goid]
            node.infoContent = (log(totalAnnotCount) - log(protCount))/log(2)
                                                         
                

