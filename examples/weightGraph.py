from GOGrapher import *

# We want to print debugging info
error = GOError(3)

# load picked graph
graph = GODiGraph.loadPickle(filename='human.bp.digraph.pickle')

# make it weighted
xgraph = graph.makeWeighted(XGraphWeighters.SimpleWeighter)

xgraph.savePickle('human.bp.xdigraph.pickle')
