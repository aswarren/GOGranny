## \package XGraphWeighters.SimpleWeighter
# A simple example of a weighting class - gives all edges a weight of 1
# \author Brian Muller <mullerb@musc.edu>

from WeightingInterface import WeightingInterface

class SimpleWeighter(WeightingInterface):
    # should take edges from original unweighted originalGraph and add them
    # to self.graph but now with weights.
    # \returns a weighted graph (either GOXDiGraph or GOXGraph)
    def makeWeighted(self, originalGraph):
        self.error.debug("Making a weighted graph simply (every weight is 1)")

        for source, sink in originalGraph.edges_iter():
            self.graph.add_edge(source, sink, 1)

        return self.graph


