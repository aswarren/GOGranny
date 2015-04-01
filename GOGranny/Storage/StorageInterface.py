## \package Storage.StorageInterface
# Common storage classes/functions
# \author mullerb@musc.edu

from GOGranny import GOError    

## Abstract class / Interface for all storage implementations.
class StorageInterface:
    ## Constructor
    def __init__(self):
        self.error = GOError()

    ## Get all PMID's that were used as refernces
    # for a specific GO term
    # @param termnode The term node to get references for
    # @param species The species to restrict the search for
    # \return A list of PMID's
    def getPMIDReferences(self, termnode, species):
        raise NotImplementedError

    def getTermAssocList(self, aspect):
        raise NotImplementedError

    def makeTerm(self, term_id):
        raise NotImplementedError

    def makeProtein(self, protein_id):
        raise NotImplementedError

    def makeProteins(self, protein_ids):
        raise NotImplementedError

    ## @param species is the common_name
    def getTermsProteinIDs(self, termnode, species):
        raise NotImplementedError

    ## @param species is the common_name
    def getProteinsTermIDs(self, proteinnode, species):
        raise NotImplementedError    

    def saveState(self):
        raise NotImplementedError

    def loadState(self):
        raise NotImplementedError

    ## Normally, terms have a lazy lookup method for determining what proteins are associated with them,
    # i.e., the term doesn't find out unless you call node.getProteins.  We're going to ask storage to go ahead
    # and look them up explicitly now. 
    def setTermsProteins(self, termlist, species):
        raise NotImplementedError

    def getProteinsID(self, symbol):
        raise NotImplementedError

    def getTermsID(self, goid):
        raise NotImplementedError
