from GOGrapher import *

# We want to print debugging info
error = GOError(3)

# load picked graph
graph = GOGraph.loadPickle(filename='human.bp.digraph.pickle')

graph.makeImage("human.bp.digraph.png", prog="neato")
