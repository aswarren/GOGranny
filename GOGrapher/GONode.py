## \package GONode  Both node and term type vertice classes
# \author Brian Muller <mullerb@musc.edu>

from GOError import GOError


class GONode:
    TERM_TYPE = "term_type"
    PROTEIN_TYPE = "protein_type"
    
    ## Constructor
    def __init__ (self, nodetype, dbid, storage=None, name=None, description=None):
        self.goError = GOError()
        self.storage = storage
        self.dbid = dbid
        self.type = nodetype
        self.name = name
        self.description = description


    def __ne__(self, other):
        return not self == other
                      

    def __repr__(self):
        props = ['dbid','storage', 'name','description']
        return "<GONode {%s}>" % ", ".join(["%s: %s" % (n, self.__dict__[n]) for n in props])            


    def __hash__(self):
        return hash(str(self))


    def __eq__(self, other):
        return hash(self) == hash(other)


    def __cmp__(self, other):
        # hash(self) - hash(other) was sometimes a long, but the following seems to always
        # be an int - must be int, because of heapq restrictions
        return hash(hash(self) - hash(other))


    def requireStorage(self, fname):
        if self.storage is None:
            self.goError.handleFatal("The method %s cannot be called because no storage was specified" % fname)
        

    def isTermNode(self):
        return not self.isProteinNode()
        

class GOTermNode(GONode):

    ## Constructor
    def __init__ (self, goid, dbid=None, name=None, description=None, storage=None):
        GONode.__init__(self, nodetype=GONode.TERM_TYPE, storage=storage, dbid=dbid, name=name, description=description)
        self.goid = goid
        self._proteins = {}
        self._pmids = {}
        if self.storage != None and self.dbid == None:
            self.dbid = self.storage.getTermsID(self.goid)
        

    def __str__(self):
        if hasattr(self, "str"):
            return self.str
        props = ['name', 'description', 'goid']
        self.str = "<GOTermNode {%s}>" % ", ".join(["%s: %s" % (n, self.__dict__[n]) for n in props])
        return self.str


    # Get all of the proteins associated with this term node.  Results are cached.
    # @param species The gene products will be given per specified species
    def getProteins(self, species):
        self.requireStorage("getProteins")
        if not self._proteins.has_key(species):
            protein_ids = self.storage.getTermsProteinIDs(self, species)
            self._proteins[species] = self.storage.makeProteins(protein_ids)
        return self._proteins[species]


    ## Get a list of the PMID's used as evidence for this term.
    # @param species The species to restrict the search to.
    # \return A list of PMIDs
    def getPMIDReferences(self, species):
        self.requireStorage("getPMIDReferences")
        if not self._pmids.has_key(species):
            self._pmids[species] = self.storage.getPMIDReferences(self, species)
        return self._pmids[species]
    

    def isProteinNode(self):
        return False


    def setProteins(self, prots, species):
        self._proteins[species] = prots
    

class GOProteinNode(GONode):

    ## Constructor
    def __init__ (self, symbol, dbid=None, name=None, description=None, storage=None):
        GONode.__init__(self, nodetype=GONode.PROTEIN_TYPE, storage=storage, dbid=dbid, name=name, description=description)
        self.symbol = symbol
        self._terms = {}
        if self.storage != None and self.dbid == None:
            self.dbid = self.storage.getProteinsID(self.symbol)        

    def __str__(self):
        props = ['name', 'description', 'symbol']
        return "<GOProteinNode {%s}>" % ", ".join(["%s: %s" % (n, self.__dict__[n]) for n in props])            


    # Get all of the terms associated with this protein node.  Results are cached.
    # @param species The terms will be given per specified species
    def getTerms(self, species):
        self.requireStorage("getTermNodes")
        if not self._terms.has_key(species):
            term_ids = self.storage.getProteinsTermIDs(self, species)
            self._terms[species] = self.storage.makeTerms(term_ids)
        return self._terms[species]


    def isProteinNode(self):
        return True
