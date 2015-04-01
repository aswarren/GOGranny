## \package GOGraph  An unddirected unweighted graph representation of the Gene Ontology.
# \author Brian Muller <mullerb@musc.edu>

from networkx import Graph
from GOGraphBase import GOGraphBase
import Aspects
import DOMLight

# undirected unweighted
class GOGraph(Graph, GOGraphBase):
    def __init__(self, storage, species, aspect=Aspects.BP):
        GOGraphBase.__init__(self, storage, species, aspect)
        Graph.__init__(self)
                        

    def makeWeighted(self, weightingClass):
        wc = weightingClass(self.storage, species, aspect, directed=False)
        return wc.makeWeighted(self)
                    

    def toXGMML(self, fhandle):
        if fhandle.__class__.__name__ == 'str':
            f = open(fhandle, 'w')
            self.toXGMML(f)
            f.close()
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
        for edge in self.edges_iter():
            fhandle.write(str(xml.edge({'source': goids[edge[0].goid], 'target': goids[edge[1].goid], 'label': ""})) + "\n")
            if count == 1000:
                break
            count += 1
        fhandle.write("</graph>")
                                                                                                                    
