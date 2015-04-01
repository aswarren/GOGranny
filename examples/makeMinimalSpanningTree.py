from GOGranny import *
import random

# We want to print debugging info
error = GOError(3)

# load picked graph
graph = GODiGraph.loadPickle(filename='human.bp.digraph.pickle')

# randomly choose some nodes to be interested in
goi = [random.choice(graph.nodes()) for x in range(10)]

mst = graph.makeMST(goi)
f = open('mst.xgmml', 'w')
mst.toXGMML(f)
f.close()
