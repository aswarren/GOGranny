## \package Storage.FilebasedStorage
# Storage is all in memory - The GO info is loaded from an owl file, and
# association files are specified for the associations that will be used
# \authors aswarren@gmail.com, mullerb@musc.edu

from GOGranny.GONode import GOProteinNode, GOTermNode
import StorageInterface
from GOGranny.GOError import *

from xml.sax.handler import ContentHandler
from xml.sax import make_parser

import cPickle, commands
from collections import defaultdict

## A parser for the OBO v1.2
class GOOboHandler():
    def __init__(self, truepath_only=True):
        self.aspects={}
        self.relationships={}
        self.names={}
        self.truepath_relations=set(["part_of","is_a"])
        self.other_relations=set()
        self.truepath_only=truepath_only

    def processVal(self, val):
        result=val.split("!")[0]
        return result.strip()

    def obo_iterator(self, in_handle):
        currentTerm=None
        for line in in_handle:
            line=line.strip()
            if not line:
                continue
            if line == "[Term]":
                if currentTerm: yield dict(currentTerm)
                currentTerm = defaultdict(list)
            elif line == "[Typedef]":
                currentTerm=None
            else:
                if currentTerm == None: continue
                key, sep, val = line.partition(":")
                currentTerm[key].append(self.processVal(val))
        if currentTerm is not None:
            yield dict(currentTerm)

    def processTerm(self, term):
        tid=term["id"][0]
        for k in term.keys():
            if (k in self.truepath_relations) or (k in self.other_relations and not truepath_only):
                #for some reason the parsing interface has relationships stored from ancestors to descendants. going with it for now
                for ancestor in term[k]:
		    if ancestor not in self.relationships:
                        self.relationships[ancestor]=[]
                    self.relationships[ancestor].append(tid)
            elif k == 'namespace':
                for n in term[k]:
                    if n not in self.aspects:
                        self.aspects[n]=[]
                    self.aspects[n].append(tid)
            elif k == "name":
                for n in term[k]:
                    self.names[tid]=n
                    
            
        
    def parse(self, in_handle):
        for term in self.obo_iterator(in_handle):
            self.processTerm(term)

            

## A SAX parser for GO OBO XML files.
class GOOboXmlHandler(ContentHandler):
    def __init__(self):
        self.aspects = {}
        self.relationships = {}
        self.inTypedef = False
        self.names = {}
        self.obsolete = False
        
    def startElement(self, name, attributes):
        self.cdata = ""
        if name == "term":
            self.goid = None
            self.aspect = None
            self.parents = []
            self.obsolete = False
        elif name == "typedef":
            self.inTypedef = True
                
    def endElement(self, name):
        if name == "id":
            self.goid = self.cdata.strip()
        elif name == "namespace":
            self.aspect = self.cdata.strip()
        elif name == "is_a" and not self.inTypedef:
            self.parents.append(self.cdata.strip())
        elif name == "is_obsolete" and self.cdata.strip() == "1":
            self.obsolete = True
        elif name == "typedef":
            self.inTypedef = False
        elif name == "term" and not self.obsolete:
            self.relationships[self.goid] = self.parents
            if not self.aspect in self.aspects.keys():
                self.aspects[self.aspect] = []
            self.aspects[self.aspect].append(self.goid)
        elif name == "name" and not self.obsolete and not self.goid == None and not self.names.has_key(self.goid):
            self.names[self.goid] = self.cdata.strip()

    def characters(self, data):
        self.cdata += data


## A SAX parser for OWL files.
class GOOwlHandler(ContentHandler):
    def __init__(self):
        self.current_goid = None
        self.aspects = {}
        self.relationships = {}
        self.names = {}
        self.current_relation= None
        self.allowed_relations=set(["part_of","is_a"])
        
    def startElement(self, name, attributes):
        self.cdata = ""
        if name == "owl:Class" and len(attributes) > 0:
            about = attributes["rdf:about"]
            if about.startswith("http://purl.org/obo/owl/GO#"):
                self.current_goid = about[27:].replace('_', ':')
                self.relationships[self.current_goid] = []

        elif name == "owl:ObjectProperty" and len(attributes) >0:
            about = attributes["rdf:about"]
            if about.startswith("http://purl.org/obo/owl/OBO_REL#"):
                self.current_relation=about[32:]
            elif about.startswith("http://purl.org/obo/owl/obo#"):
                self.current_relation=about[28:]
            else:
                self.current_relation=None
        elif name == "owl:someValuesFrom" and len(attributes) > 0:
             if(self.current_relation in self.allowed_relations):
                parent = attributes["rdf:resource"]
                self.relationships[self.current_goid].append(parent[27:].replace('_', ':'))
        elif name == "rdfs:subClassOf" and len(attributes) > 0:
            parent = attributes["rdf:resource"]
            if parent != "http://www.geneontology.org/formats/oboInOwl#ObsoleteClass":
                self.relationships[self.current_goid].append(parent[27:].replace('_', ':'))
                
    def endElement(self, name):
        if name == "oboInOwl:hasOBONamespace":
            if not self.cdata in self.aspects.keys():
                self.aspects[self.cdata] = []
            self.aspects[self.cdata].append(self.current_goid)
        elif name == "oboInOwl:hasDate":
		self.date=self.cdata.strip()
        elif name == "rdfs:label" and self.current_goid != None and not self.names.has_key(self.current_goid):
            self.names[self.current_goid] = self.cdata.strip()            

    def characters(self, data):
        self.cdata += data
    

## Abstract class / Interface for all storage implementations.
class FilebasedStorage(StorageInterface.StorageInterface):

    ## Constructor
    # Takes two required parameters.  Parses all files, stores info in memory.  One of
    # oboxmlfile or owlfile must be specified.
    # @param associations An dictionary whose keys are species names and whose values
    # are assocation file locations.  This arg is optional.
    # @param owfile Location of GO term relationship OWL file - or -
    # @param oboxmlfile Location of GO term relationship OBO XML file
    # @param hardEvidence If true, ignore soft evidence for associations (IEA, IEP, ND)
    def __init__(self, associations=None, owlfile=None, oboxmlfile=None, obofile=None, hardEvidence=True):
        StorageInterface.StorageInterface.__init__(self)
        # dictionary of goid to long names
        self.names = {}

        if owlfile != None and oboxmlfile !=None and obofile != None:
            self.error.handleFatal("You must specify either an owlfile, oboxmlfile, or obofile as a keyword parameter to FilebasedStorage constructor")            
        
        if obofile != None:
            self.parseObo(obofile)
        elif owlfile != None:
            self.parseOwl(owlfile)
        elif oboxmlfile != None:
            self.parseOboXml(oboxmlfile)
        else:
            self.error.handleFatal("You must specify an ontology file as a keyword parameter to FilebasedStorage.__init__")
        self.associations_term = {}
        self.associations_prot = {}
        self.pmids = {}
        associations = associations or {}
        for species, f in associations.items():
            self.error.debug("About to parse associations file %s for species %s" % (f, species))
            self.associations_term[species], self.associations_prot[species], self.pmids[species] = self.parseAssociation(f, hardEvidence)


    ## saveState is meaningless in this context - this class is entirely pickleable
    def saveState(self):
        pass


    ## loadState is meaningless in this context - this class is entirely unpickleable    
    def loadState(self):
        pass

    def parseAssociation(self, location, hardEvidence):
        f = open(location)
        associations_term = {}
        associations_prot = {}
        pmids = {}

        result, output = commands.getstatusoutput("wc -l %s" % location)
        progress = None
        if result == 0:
            try:
                numlines = int(output.split(' ')[0])
                self.error.debug("There are %i lines to process in %s" % (numlines, location))
                progress = GOPercentMessage(numlines)
            except Exception, e:
                pass
                
        for line in f:
            if progress is not None:
                progress.update()            
            if not line.startswith("!"):
                parts = map(lambda x: x.strip(), line.split('\t'))
                if parts[6] in ['IEA', 'IEP', 'ND'] and hardEvidence:
                    continue
                if parts[3] == "NOT":
                    continue
                symbol = parts[2]
                goid = parts[4]
                if not associations_term.has_key(goid):
                    associations_term[goid] = []
                associations_term[goid].append(symbol)
                if not associations_prot.has_key(symbol):
                    associations_prot[symbol] = []
                associations_prot[symbol].append(goid)

                # references
                if not pmids.has_key(goid):
                    pmids[goid] = []
                references = filter(lambda x: x.startswith("PMID:"), parts[5].split('|'))
                for reference in [ref[5:] for ref in references]:
                    if not reference in pmids[goid]:
                        pmids[goid].append(reference)
        if progress is not None:
            progress.finished()
        f.close()
        return associations_term, associations_prot, pmids
        
    def parseObo(self, location):
        self.error.debug("About to parse OBO file %s" % location)
        try:
            f = open(location, 'r')
            obo_handler=GOOboHandler()
            obo_handler.parse(f)
            f.close()
        except Exception, e:
            self.error.handleFatal("Could not parse OBO file %s: %s" % (location, str(e)))
        self.aspects = obo_handler.aspects
        self.names = obo_handler.names
        self.relationships= obo_handler.relationships
        	

    def parseOwl(self, location):
        self.error.debug("About to parse OWL file %s" % location)
        parser = make_parser()
        parser.setFeature("http://xml.org/sax/features/external-general-entities", False)
        parser.setFeature("http://xml.org/sax/features/external-parameter-entities", False)                
        handler = GOOwlHandler()
        parser.setContentHandler(handler)
        try:
            f = open(location, 'r')
            parser.parse(f)
            f.close()
        except Exception, e:
            self.error.handleFatal("Could not parse OWL file %s: %s" % (location, str(e)))
        self.error.debug("Finished parsing OWL file")
        # at this point, handler.relationships has the form
        # relationships[child] = [list of parents] - and we want the opposite,
        # as in relationships[parent] = [list of children]
        self.relationships = {}
        for child, parents in handler.relationships.iteritems():
            for parent in parents:
                if not self.relationships.has_key(parent):
                    self.relationships[parent] = []
                self.relationships[parent].append(child)
        self.aspects = handler.aspects
        self.names = handler.names
        self.date = getattr(handler,'date',"")


    def parseOboXml(self, location):
        self.error.debug("About to parse OBO XML file %s" % location)
        parser = make_parser()
        parser.setFeature("http://xml.org/sax/features/external-general-entities", False)
        parser.setFeature("http://xml.org/sax/features/external-parameter-entities", False)                        
        handler = GOOboXmlHandler()
        parser.setContentHandler(handler)
        try:
            f = open(location, 'r')
            parser.parse(f)
            f.close()
        except Exception, e:
            self.error.handleFatal("Could not parse OBO XML file %s: %s" % (location, str(e)))
        self.error.debug("Finished parsing OBO XML file")
        # at this point, handler.relationships has the form
        # relationships[child] = [list of parents] - and we want the opposite,
        # as in relationships[parent] = [list of children]
        self.relationships = {}
        for child, parents in handler.relationships.iteritems():
            for parent in parents:
                if not self.relationships.has_key(parent):
                    self.relationships[parent] = []
                self.relationships[parent].append(child)
        self.aspects = handler.aspects
        self.names = handler.names


    def getTermAssocList(self, aspect):
        # The result var is a hash of lists - the hash key is the parent term id, and the hash value is the list of children ids
        result = {}
        for term in self.aspects[aspect]:
            # if a term has kids
            if self.relationships.has_key(term):
                result[term] = self.relationships[term]
            # otherwise, no kids
            else:
                result[term] = []
        return result


    def getPMIDReferences(self, term, species):
        if not self.pmids.has_key(species):
            self.error.handleFatal("An annotation file was not loaded for %s" % species)
            return []
        elif not self.associations_term[species].has_key(termnode.goid):
            return []
        return self.pmids[species][termnode.goid]        
        

    def makeTerm(self, term_id):
        # first make sure we've seen the term_id before
        found = False
        for aspect, golist in self.aspects.items():
            if term_id in golist:
                found = True
        if not found:
            self.error.handleWarning("No term with id of %i" % term_id)
        name = self.names.get(term_id, None)            
        return GOTermNode(term_id, storage=self, name=name)


    def makeTerms(self, term_ids):
        return map(lambda id: self.makeTerm(id), term_ids)


    def makeProtein(self, protein_id):
        return GOProteinNode(protein_id, storage=self)


    def makeProteins(self, protein_ids):
        return map(lambda id: self.makeProtein(id), protein_ids)

            
    def getTermsProteinIDs(self, termnode, species):
        if not self.associations_term.has_key(species):
            self.error.handleFatal("An annotation file was not loaded for %s" % species)
            return []
        elif not self.associations_term[species].has_key(termnode.goid):
            return []
        return self.associations_term[species][termnode.goid]


    def getProteinsTermIDs(self, proteinnode, species):
        if not self.associations_prot.has_key(species):
            self.error.handleWarning("An annotation file was not loaded for %s" % species)
            return []
        elif not self.associations_prot[species].has_key(proteinnode.symbol):
            return []
        return self.associations_prot[species][proteinnode.symbol]        


    # Normally, terms have a lazy lookup method for determining what proteins are associated with them,
    # i.e., the term doesn't find out unless you call node.getProteins.  We're going to ask storage to go ahead
    # and look them up explicitly now.
    # BUT - since we're caching everything in memory anyway in this form of storage, lazy lookups aren't expensive
    # at all.  This is mainly for DB type storage methods.
    def setTermsProteins(self, termlist, species):
        pass

    
    def getProteinsID(self, symbol):
        return symbol


    def getTermsID(self, goid):
        return goid
            
