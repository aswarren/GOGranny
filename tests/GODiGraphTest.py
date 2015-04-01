import unittest
from GOGranny import *
import random
from utils import *


class GODiGraphTest(unittest.TestCase):
    def setUp(self):
        owlfile = "./tests/data/go_daily-termdb.owl"
        assocs = {'human': "./tests/data/gene_association.goa_human"}
        self.species = "human"
        self.storage = StorageFactory.makeStorage(Storage.Types.FILEBASED, assocs, owlfile=owlfile)
        # Make human biological process
        self.aspect = Aspects.BP
        self.graph = GODiGraph(self.storage, self.species, self.aspect)
        self.nodeids = map(lambda n: n.goid, self.graph.nodes_iter())
        self.pickle_file = "/tmp/testpickle"


    def getConnectedNodes(self, assoc):
        def getDescendents(node, seen):
            a = assoc[node]
            for n in a:
                if not seen.has_key(n):
                    aa, seen = getDescendents(n, seen)
                    a += aa
                    seen[n] = None
            print "finished %i" % len(seen.keys())
            return a, seen
        seen = {}
        a, seen = getDescendents(self.graph.root.goid, seen)
        print "size of a: ", len(a)
        return [self.graph.root.goid] + a
        ###return getDescendents("GO:0008150", seen)


    def testNodes(self):
        assoc = self.storage.getTermAssocList(self.aspect)
        print "getting nodes"
        nodes = self.getConnectedNodes(assoc)
        print nodes[:20]
        print self.nodeids[:20]
        self.failUnless(arraysAreEqual(nodes, self.nodeids))
