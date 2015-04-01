## \package GOGraphBase A base class that all GO graph types inherit from.
# \author Brian Muller <mullerb@musc.edu>

import cPickle
import Aspects
from GOError import GOError
from SteinerTree import make_steiner_tree
from networkx import Graph
from GONode import GOTermNode

class GOGraphBase:
    def __init__(self, storage, species, aspect=Aspects.BP):
        self.error = GOError()
        self.storage = storage
        self.species = species
        self.aspect = aspect
        
        if aspect not in Aspects.ALLSPACENAMES:
            self.error.handleFatal("Unknown aspect: %s" % self.aspect)
        

    ## Save self using pickle protocol.  Note that this method will call saveState
    # on your storage as well.
    # @param filename The filename of the pickle to use.
    def savePickle(self, filename="gograph.pickle"):
        self.error.debug("Saving pickled graph to %s..." % filename)
        try:
            f = open(filename, 'wb')
            self.storage.saveState()
            cPickle.dump(self, f, protocol = cPickle.HIGHEST_PROTOCOL)
            self.storage.loadState()
            f.close()
        except Exception, e:
            self.error.handleWarning("Cannot save the instance of gograph: %s" % str(e))
        

    # Load a pickle from the filesystem.  You do not need to have a storage object initialized - the object's state was stored.
    # @param storage A Storage.StorageInterface object
    # @param filename The location of the pickle file to load
    @classmethod                                                                          
    def loadPickle(klass, storage=None, filename="gograph.pickle"):
        error = GOError()
        error.debug("Loading pickled graph from %s..." % filename)        
        try:
            f = open(filename, 'rb')
            g = cPickle.load(f)
            if storage == None:
                g.storage.loadState()
            else:
                g.storage = storage
            f.close()
            return g
        except Exception, e:
            error.handleWarning("Could not load pickle instance: %s" % str(e))
            return


    # this method should be reimplemented in each child class -
    # for instance, a directed graph should make a directed AGraph
    # and a weighted graph should have weights displayed on edges
    def makeImageObject(self):
        try:
            from pygraphviz import AGraph
        except Exception, e:
            self.error.handleFatal("Could not import pygraphviz package.  If you're on windows, pygraphviz may not be installable.\n%s" % str(e))
        image = AGraph()
        for edge in self.edges_iter():
            image.add_edge(*edge)
        return image
    
            
    def makeImage(self, filename="graphimage.png", prog = "dot"):
        image = self.makeImageObject()
        image.draw(filename, prog=prog)


    def isWeighted(self):
        return self.__class__.__name__ in ['GOXGraph', 'GOXDiGraph']


    # Create a minimal spanning tree containing only some number of terms of interest and the pairwise shortest
    # paths between them.
    # @param goi The gene ontology terms of interest
    # /returns a new one of self's type of graph.  Nodes in this graph are strings (goids).
    def makeMST(self, goi):
        graph = XGraph()
        if self.isWeighted():
            for v1, v2, w in self.edges_iter(data=True):
                graph.add_edge(v1.goid, v2.goid, w)
        else:
            for v1, v2 in self.edges_iter():
                graph.add_edge(v1.goid, v2.goid, 1)
        goi = map(lambda x: x.goid, goi)
        
        mst = make_steiner_tree(graph, goi)
        
        graph = self.__class__(self.storage, self.species, self.aspect)
        for v1, v2, w in mst.edges_iter(data=True):
            if graph.isWeighted():
                graph.add_edge(GOTermNode(v1), GOTermNode(v2), w)
            else:
                graph.add_edge(GOTermNode(v1), GOTermNode(v2))
        return graph
