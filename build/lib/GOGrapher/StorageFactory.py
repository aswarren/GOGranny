## \package StorageFactory
# Singleton - makes storage mechanism
# \author mullerb@musc.edu

import GOError
import Storage


## Simple singleton factory for making storage mechanisms
# \see Storage.BasicStorage
class StorageFactory:
    __state = {}
    ## Constructor.  All instances share state.
    def __init__(self):
        self.__dict__ = self.__state


    ## Return an instance the class requested
    # @param stype The storage type to make
    # @param args Additional arguments for the storage type (if any)
    # @param kwargs Additional keyword arguments for the storage type (if any)    
    # \return The class requested if it exists, Storage.BasicStorage otherwise.
    # \see Storage.__init__.Types
    @classmethod
    def makeStorage(klass, stype, *args, **kwargs):
        error = GOError.GOError()
        if stype == Storage.Types.MYSQL:
            msg = "Not all methods for PMID reference retrieval are implemented in the MySQL storage type."
            error.handleWarning(msg)
            return Storage.MysqlStorage(*args, **kwargs)
        elif stype == Storage.Types.FILEBASED:
            return Storage.FilebasedStorage(*args, **kwargs)
        else:
            error.handleFatal("Attept to create non existant storage in the factory: %s" % stype)
