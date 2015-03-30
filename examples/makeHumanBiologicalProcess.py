from GOGrapher import *

# We want to print debugging info
error = GOError(3)

# You must have a mysql GO database set up
storage = StorageFactory.makeStorage(Storage.Types.FILEBASED, {'human': "../data/gene_association.goa_human"}, owlfile="../data/go_daily-termdb.owl")

# Make human biological process
graph = GODiGraph(storage, "human", Aspects.BP)

# create and trim the graph
graph.makeGraph()

# store picked graph for later
graph.savePickle('human.bp.digraph.pickle')

graph = graph.toUndirected()

graph.savePickle('human.bp.graph.pickle')


