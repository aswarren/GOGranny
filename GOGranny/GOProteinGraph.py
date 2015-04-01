## \package GOProteinGraph
# A graph that extends a GOGraph that will contain all of the gene products
# as vertices in a graph.  Since "distance" and "weight" are basically
# meaningless for the edges between terms and proteins, this graph will
# only a accept an unweighted, undirected GOGraph.
# \author Brian Muller <mullerb@musc.edu>

from GOGraph import GOGraph
from GOError import GOError

class GOProteinGraph(GOGraph):
    # Create a protein graph from a GOGraph
    # @param gograph A GOGraph to base this graph off of.
    def __init__(self, gograph):
        if not gograph.__class__.__name__ is 'GOGraph':
            msg = "You did not give an instance of GOGraph to GOProteinGraph (it's a %s):" % gograph.__class__.__name__ \
                  + " any weights or directions will be ignored." 
            GOError().handleWarning(msg)
        GOGraph.__init__(self, gograph.storage, gograph.species, gograph.aspect)
        self.add_edges_from(gograph.edges_iter())
        self.annotate()


    def annotate(self):
        self.error.debug("Annotating a graph with %i terms.  This might take a few minutes." % self.number_of_nodes())
        # alrighty - here's how we do this - since we're iterating over a nodelist we can't add nodes as we go - we've got
        # to put them in a hash and add them after we iterate through all the initial term nodes
        annotations = {}   # cache of hash[goid] -> [list of protein_ids]
        originalnodes = {} # cache of goid -> term node 
        proteins = {}      # cache of protein_id -> protein node

        total = self.number_of_nodes()
        current = -1

        # Make proteins in bunches
        def makeProteins(prot_ids):
            dont_have = []
            for prot_id in prot_ids:
                if not proteins.has_key(prot_id):
                    dont_have.append(prot_id)
            for prot in  self.storage.makeProteins(dont_have):
                proteins[prot.dbid] = prot
                     
        for node in self.nodes_iter():
            current += 1
            self.error.debug("Finished %i of %i..." % (current, total), True)
            annotations[node.goid] = []
            originalnodes[node.goid] = node
            prot_ids = self.storage.getTermsProteinIDs(node, self.species)

            makeProteins(prot_ids)
            for prot_id in prot_ids:
                annotations[node.goid].append(proteins[prot_id])
                
        self.error.debug("Finished finding annotations, adding protein nodes...")
        for node_id, node in originalnodes.iteritems():
            for prot in annotations[node_id]:
                self.add_edge(node, prot)


    def getNeighborTerms(self, node):
        a = []
        for n in self.neighbors(node):
            if n.isTermNode():
                a.append(n)
        return a


    def getNeighborProteins(self, node):
        a = []
        for n in self.neighbors(node):
            if n.isProteinNode():
                a.append(n)
        return a        


    def proteinNodesIter(self):
        for node in self.nodes_iter():
            if node.isProteinNode():
                yield node


    def termNodesIter(self):
        for node in self.nodes_iter():
            if not node.isProteinNode():
                yield node    
