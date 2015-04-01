## \package XGraphWeighters.WeightingInterface
# An interface that all graph weighters must implement
# \author Brian Muller <mullerb@musc.edu>


from GOGrapher import GOError
from GOGrapher import GOXDiGraph
from GOGrapher import GODiGraph

class WeightingInterface: 
    def __init__(self, storage, species, aspect, directed):
        self.error = GOError()
        if directed:
            self.graph = GOXDiGraph(storage, species, aspect)
        else:
            self.graph = GOXGraph(storage, species, aspect)
            

    # should take edges from original unweighted originalGraph and add them
    # to self.graph but now with weights.
    # \returns a weighted graph (either GOXDiGraph or GOXGraph)
    def makeWeighted(self, originalGraph):
        raise NotImplementedError
    
