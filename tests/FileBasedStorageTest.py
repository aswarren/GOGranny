import unittest
from GOGranny import *
import random
from utils import *
from xml.sax.handler import ContentHandler
from xml.sax import make_parser


class TestGOOwlHandler(ContentHandler):
    def __init__(self):
        self.current_goid = None
        self.aspects = {}
        
    def startElement(self, name, attributes):
        self.cdata = ""
        if name == "owl:Class" and len(attributes) > 0:
            about = attributes["rdf:about"]
            if about.startswith("http://purl.org/obo/owl/GO#"):
                self.current_goid = about[27:].replace('_', ':')

    def endElement(self, name):
        if name == "oboInOwl:hasOBONamespace":
            if not self.cdata in self.aspects.keys():
                self.aspects[self.cdata] = []
            self.aspects[self.cdata].append(self.current_goid)

    def characters(self, data):
        self.cdata += data


class FileBasedStorageTest(unittest.TestCase):
    def setUp(self):
        self.owlfile = "./tests/data/go_daily-termdb.owl"
        self.oboxmlfile = "./tests/data/go_daily-termdb.obo-xml"
        self.assocs = {'human': "./tests/data/gene_association.goa_human"}
        self.storage = StorageFactory.makeStorage(Storage.Types.FILEBASED, self.assocs, owlfile=self.owlfile)
        self.aspect = Aspects.BP
        self.species = "human"
        if not self.storage:
            print 'self.storage did not initialize'

    def testPickling(self):
        assoclist = self.storage.getTermAssocList(self.aspect).keys()
        self.storage.saveState()
        self.storage.loadState()
        newassoclist = self.storage.getTermAssocList(self.aspect).keys()
        self.failUnless(arraysAreEqual(assoclist, newassoclist))


    def testGetTermAssocs(self):
        # Pretty hard to test this one.....but let's just check that the goids are read
        parser = make_parser()
        handler = TestGOOwlHandler()
        parser.setContentHandler(handler)
        f = open(self.owlfile, 'r')
        parser.parse(f)
        f.close()
        goids = handler.aspects[self.aspect]
        testgoids = self.storage.getTermAssocList(self.aspect).keys()
        self.failUnless(arraysAreEqual(goids, testgoids))
        

    def testNoSuchSpecies(self):
        assoc = self.storage.getTermAssocList(self.aspect)
        # get a random term
        goid = random.choice(assoc.keys())
        while len(assoc[goid]) == 0:
            goid = random.choice(assoc.keys())        
        term = GOTermNode("not a valid goid")
        self.assertEqual(len(self.storage.getTermsProteinIDs(term, self.species)), 0)
    

    def testOboXML(self):
        obostorage = StorageFactory.makeStorage(Storage.Types.FILEBASED, self.assocs, oboxmlfile=self.oboxmlfile)
        self.failUnless(arraysAreEqual(obostorage.relationships.keys(), self.storage.relationships.keys()))
        for parent, child in obostorage.relationships.iteritems():
            self.failUnless(arraysAreEqual(obostorage.relationships[parent], self.storage.relationships[parent]))
        term = self.storage.makeTerm("GO:0000012")
        self.assertEqual(term.name, "single strand break repair")


    def testOWLNames(self):
        term = self.storage.makeTerm("GO:0000012")
        self.assertEqual(term.name, "single strand break repair")
