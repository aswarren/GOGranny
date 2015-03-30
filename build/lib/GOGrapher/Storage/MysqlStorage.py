## \package Storage.DBStorage
# Common storage classes/functions
# \author mullerb@musc.edu

import StorageInterface
from GOGrapher.GONode import GOProteinNode, GOTermNode
    

# Store that can use a variety of DB types
class MysqlStorage(StorageInterface.StorageInterface):
    
    ## Constructor
    # @param dbconfig Database configuration string
    # \see http://www.sqlobject.org/SQLObject.html#dbconnection-database-connections
    def __init__(self, dbconfig):
        # don't import the following unless we're actually being used
        import MySQLdb
        StorageInterface.StorageInterface.__init__(self)
        # We now need to create hash for a uri like: mysql://gosteiner:hackme@localhost/gosteiner
        dbhash = {}
        if dbconfig.startswith('mysql://'): # which it should
            dbconfig = dbconfig[8:]
        else:
            self.error.handleFatal("Cannot use mysql storage if the uri \"%s\" is not for mysql (must begin with mysql://)" % dbconfig)

        # if passwd given
        if dbconfig.count(':') > 0:
            dbhash['user'] = dbconfig[:dbconfig.index(':')]
            dbhash['passwd'] = dbconfig[dbconfig.index(':')+1:dbconfig.index('@')]
        else:
            dbhash['user'] = dbconfig[:dbconfig.index('@')]
        dbhash['host'] = dbconfig[dbconfig.index('@')+1:dbconfig.index('/')]
        dbhash['db'] = dbconfig.split('/')[-1]                
        
        # initialize DB
        try:
            self.connection = MySQLdb.connect(**dbhash)
        except Exception, e:
            self.error.handleFatal("Error initializing MysqlStorage:\n%s" % str(e))

        self.speciescache = {}
        self.config = dbhash


    # get ready to be pickled
    def saveState(self):
        self.connection = None
        # self.config was saved initially


    def loadState(self):
        import MySQLdb
        # initialize DB
        try:
            self.connection = MySQLdb.connect(**self.config)
        except Exception, e:
            self.error.handleFatal("Error initializing MysqlStorage:\n%s" % str(e))


    def getTermAssocList(self, aspect):
        # The assoclist var is a hash of lists - the hash key is the parent term id, and the hash value is the list of children ids
        assoclist = {}
        cursor = self.connection.cursor()
        query = "SELECT count(*) FROM term WHERE term_type = \"%s\"" % aspect
        cursor.execute(query)
        count = cursor.fetchone()[0]

        if count == 0:
            self.error.handleFatal("There are no terms for the aspect \"%s\"" % aspect)            
        
        offset = 0
        limit = 100
        self.error.debug("Fetching all %i terms for %s" % (count, aspect))
        while True:
            query = "SELECT id FROM term WHERE term_type = \"%s\" LIMIT %i OFFSET %i" % (aspect, limit, offset)
            cursor.execute(query)
            offset += limit
            results = cursor.fetchall()
            if not results:
                break
            for result in results:
                assoclist[str(result[0])] = []
        self.error.debug("Fetching all those term's kids")

        query = 'select id from term where name = "is_a"'
        cursor.execute(query)
        is_a_id = cursor.fetchall()[0][0]

        for key in assoclist.iterkeys():
            query = "SELECT term2_id FROM term2term WHERE term1_id = %i AND relationship_type_id = %i" % (int(key), int(is_a_id))
            cursor.execute(query)
            results = cursor.fetchall()
            if results != None:
                assoclist[key] = map(lambda x: x[0], results)
        return assoclist
        

    def makeTerm(self, term_id):
        term_id = int(term_id)
        cursor = self.connection.cursor()
        query = "SELECT acc FROM term WHERE id = %i" % term_id
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return GOTermNode(result[0], dbid=term_id, storage=self)
        else:
            self.error.handleWarning("No term with id of %i" % term_id)


    def makeTerms(self, term_ids):
        if len(term_ids) == 0:
            return []
        if len(term_ids) > 200:
            return self.makeTerms(term_ids[:200]) + self.makeTerms(term_ids[200:])
        term_ids = map(lambda x: str(x), term_ids)
        cursor = self.connection.cursor()
        query = "SELECT acc, id FROM term WHERE id IN (%s)" % ",".join(term_ids)
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            return map(lambda result: GOTermNode(result[0], dbid=result[1], storage=self), results)
        else:
            self.error.handleWarning("No term with ids in %s" % ",".join(term_ids))


    def makeProtein(self, protein_id):
        protein_id = int(protein_id)
        cursor = self.connection.cursor()
        query = "SELECT symbol FROM gene_product WHERE id = %i" % protein_id
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return GOProteinNode(result[0], dbid=protein_id, storage=self)
        else:
            self.error.handleWarning("No gene product with id of %i" % term_id)        


    def makeProteins(self, protein_ids):
        if len(protein_ids) == 0:
            return []
        if len(protein_ids) > 100:
            return self.makeProteins(protein_ids[:100]) + self.makeProteins(protein_ids[100:])
        protein_ids = map(lambda x: str(x), protein_ids)
        cursor = self.connection.cursor()
        query = "SELECT symbol, id FROM gene_product WHERE id IN (%s)" % ",".join(protein_ids)
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            return map(lambda result: GOProteinNode(result[0], dbid=result[1], storage=self), results)
        else:
            self.error.handleWarning("No gene products with ids in %s" % ",".join(protein_ids))


    # Get the db id for the given species
    # @param species Species common name
    def getSpeciesID(self, species):
        cursor = self.connection.cursor()
        if not species in self.speciescache.keys():
            query = "select id from species where common_name = \"%s\"" % species
            cursor.execute(query)
            results = cursor.fetchall()
            if(len(results) == 0):
                self.error.handleWarning("There are no species with a common_name of \"%s\"" % species)
                return []
            self.speciescache[species] = results[0][0]
        return self.speciescache[species]


    def getTermsProteinIDs(self, termnode, species):
        cursor = self.connection.cursor()
        speciesid = self.getSpeciesID(species)
        
        query = "SELECT association.gene_product_id FROM association left join gene_product on (association.gene_product_id = gene_product.id) WHERE association.term_id = %i and gene_product.species_id = %i and association.is_not = 0" % (int(termnode.dbid), int(speciesid))
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            return map(lambda x: x[0], results)
        return []


    def getProteinsTermIDs(self, proteinnode, species):
        cursor = self.connection.cursor()
        speciesid = self.getSpeciesID(species)        
        
        query = "SELECT association.term_id FROM association left join gene_product on (association.gene_product_id = gene_product.id) WHERE association.gene_product_id = %i and gene_product.species_id = %i and association.is_not = 0" % (int(proteinnode.dbid), int(speciesid))
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            return map(lambda x: x[0], results)
        return []


    # Normally, terms have a lazy lookup method for determining what proteins are associated with them,
    # i.e., the term doesn't find out unless you call node.getProteins.  We're going to ask storage to go ahead
    # and look them up explicitly now.
    def setTermsProteins(self, termlist, species):
        count = 0
        nlist = []
        while termlist > 0:
            nlist.append(termlist.pop())
            if len(nlist) == 100:
                self._setTermsProteins(nlist, species)
                count += 100
                self.error.debug("finished handling %s terms" % str(count), True)                
                nlist = []
        if len(nlist) > 0:
            self._setTermsProteins(nlist, species)


    def _setTermsProteins(self, termlist, species):
        def getTerm(dbid, termlist):
            for term in termlist:
                if term.dbid == dbid:
                    return term
                
        speciesid = self.getSpeciesID(species)                
        cursor = self.connection.cursor()
        ids = map(lambda term: str(term.dbid), termlist)
        query = "SELECT association.term_id, association.gene_product_id FROM association left join gene_product on (association.gene_product_id = gene_product.id) WHERE association.term_id in (%s) and gene_product.species_id = %i and association.is_not = 0" % (",".join(ids), int(speciesid))
        cursor.execute(query)
        rows = cursor.fetchall()
        prots = self.makeProteins(map(lambda row: row[1], rows))
        assocs = {}
        for row in rows:
            term = getTerm(row[0], termlist)
            if not assocs.has_key(term):
                assocs[term] = []
            for prot in prots:
                if prot.dbid == row[1]:
                    assocs[term].append(prot)
        for term, prots in assocs.items():
            term.setProteins(prots, species)


    def getProteinsID(self, symbol):
        cursor = self.connection.cursor()
        query = "SELECT id FROM gene_product WHERE symbol = \"%s\"" % symbol
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return int(result[0])
        else:
            self.error.handleWarning("No gene product with symbol of %s" % symbol)


    def getTermsID(self, goid):
        cursor = self.connection.cursor()
        query = "SELECT id FROM term WHERE acc = \"%s\"" % goid
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            return int(result[0])
        else:
            self.error.handleWarning("No term with gene ontology id of %s" % goid)

            

            
