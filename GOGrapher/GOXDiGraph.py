## \package GOXDiGraph  A weighted directed graph representation of the Gene Ontology.
# \author Brian Muller <mullerb@musc.edu>

from networkx import DiGraph, dfs_postorder_nodes
import Aspects
from GOGraphBase import GOGraphBase
from GOXGraph import GOXGraph
import DOMLight

class GOXDiGraph(DiGraph, GOGraphBase):
    def __init__(self, storage, species, aspect=Aspects.BP):
        DiGraph.__init__(self, weighted=True)
        GOGraphBase.__init__(self, storage, species, aspect)


    def toUndirected(self):
        g = GOXGraph(self.storage, self.species, self.aspect);
        for source, sink, weight in self.edges_iter():
            g.add_edge(source, sink, weight=weight['weight'])
        return g
                                    

    def makeImageObject(self):
        try:
            from pygraphviz import AGraph
        except Exception, e:
            self.error.handleFatal("Could not import pygraphviz package.  If you're on windows, pygraphviz may not be installable.\n%s" % str(e))
        image = AGraph(directed=True)
        for edge in self.edges_iter():
            image.add_edge(edge[0], edge[1])
            agraph_edge = image.get_edge(edge[0], edge[1])
            agraph_edge.attr['label'] = edge[2]['weight']
        return image
                                    

    def toXGMML(self, fhandle):
        xml = DOMLight.XMLMaker()
        fhandle.write("""<?xml version="1.0" encoding="UTF-8"?>
        <graph xmlns="http://www.cs.rpi.edu/XGMML" directed="1" label="GOGrapher Network">
        """)
        cid = 0
        goids = {}
        for node in self.nodes_iter():
            goids[node.goid] = cid
            fhandle.write(str(xml.node({'id': cid, 'label': node.goid})) + "\n")
            cid += 1
        count = 0
        for edge in self.edges_iter():
            fhandle.write(str(xml.edge({'source': goids[edge[0].goid], 'target': goids[edge[1].goid], 'weight': edge[2]['weight'], 'label': ""})) + "\n")
            if count == 1000:
                break
            count += 1
        fhandle.write("</graph>")
                                                                                                                    

    ## Get weighted edgesD from this graph.
    def edges(self):
        # This is just the code from networkx.graph - except call our
        return list(self.edges_iter())
                

    ## Overwrite Graph edges_iter method so we get weight information too
    def edges_iter(self, nbunch=None):
        for edge in DiGraph.edges_iter(self, nbunch, data=True):
            yield edge
                        

    ## This method simplifies the process for directed graph traversal.  A given function will be called
    # for each source and sink of a directed edge with the source and sink as arguments.  The function is called
    # for source/sink at bottom of graph first (as in a depth first traversal).
    # @param func A function that accepts two arguments (the source and sink of a directed edge)
    def traverseWithDirection(self, func):
        sorted = dfs_postorder_nodes(self)
        for source in sorted:
            for sink in self.neighbors(source):
                func(source, sink)
                                                            
