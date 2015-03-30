from GOGrapher import *

# We want to print debugging info
error = GOError(3)

# load picked graph
graph = GODiGraph.loadPickle(filename='human.bp.digraph.pickle')

# make it weighted
f = open('human.bp.digraph.xgmml', 'w')
graph.toXGMML(f)
f.close()
