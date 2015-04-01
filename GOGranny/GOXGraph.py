## \package GOXGraph A weighted undirected graph representation of the Gene Ontology.
# \author Brian Muller <mullerb@musc.edu>      

from networkx import Graph
from GOGraphBase import GOGraphBase
import Aspects
import DOMLight

class GOXGraph(Graph, GOGraphBase):
    def __init__(self, storage, species, aspect=Aspects.BP):
        GOGraphBase.__init__(self, storage, species, aspect)
        Graph.__init__(self)

                        
    def toXGMML(self, fhandle):
        xml = DOMLight.XMLMaker()
        fhandle.write("""<?xml version="1.0" encoding="UTF-8"?>
        <graph xmlns="http://www.cs.rpi.edu/XGMML" label="GOGranny Network">
        """)
        cid = 0
        goids = {}
        for node in self.nodes_iter():
            goids[node.goid] = cid
            fhandle.write(str(xml.node({'id': cid, 'label': node.goid})) + "\n")
            cid += 1
        count = 0
        for edge in self.edges_iter(data=True):
            fhandle.write(str(xml.edge({'source': goids[edge[0].goid], 'target': goids[edge[1].goid], 'weight': edge[2], 'label': ""})) + "\n")
            if count == 1000:
                break
            count += 1
        fhandle.write("</graph>")
                                                                                                                    

    ## Get weighted edges from this graph.
    def edges(self):
        # this is the code from graph.py in networkx
        return list(self.edges_iter())


    def edges_iter(self, nbunch=None):
        for edge in Graph.edges_iter(self, nbunch, data=True):
            yield edge
