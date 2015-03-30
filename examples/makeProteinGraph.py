# This will add all of the gene products to the graph as vertices

from GOGrapher import *

# We want to print debugging info
error = GOError(3)

# load picked graph
graph = GODiGraph.loadPickle(filename='human.bp.digraph.pickle')

# make it weighted
pgraph = GOProteinGraph(graph.toUndirected())

pgraph.savePickle('human.bp.proteingraph.pickle')
