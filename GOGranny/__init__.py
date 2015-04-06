## \mainpage GOGranny :: A Python library for GO network graph analysis and representation
# \section desc Description
# GOGranny is a python library that uses the Gene Ontology to create a network relating terms
# to each other and proteins to terms. Given a species name or the name of one of the origin
# databases for the GODB (and an aspect), a directed unweighted graph is constructed (a GODiGraph
# using https://networkx.lanl.gov). Then, the following utilities can be used:
# \li given a weighting class (that extends GOWeighter) all edges can be come weighted (creating a GOXDiGraph)
# \li a utility to convert from/to protein symbols to protein ids found in other listings
# \li permanent storage for a GO(X)DiGraph 
# \section Resources
# \li The source, docs, bug reporting, and more info can be found at https://github.com/aswarren//GOGranny
# \section Authors
# \li Andrew Warren <aswarren@gmail.com>
# \li Brian Muller <mullerb@musc.edu>
# \li Adam J Richards <richa@musc.edu>
# \li Bo Jin <jinbo@musc.edu>
# \li Xinghua Lu <lux@musc.edu>

import networkx,re
from GOError import GOError, GOPercentMessage
 
#m = re.search("\.",networkx.__version__)
#if float(networkx.__version__[:m.start()]) < float("1.7"):
if networkx.__version__ < "1.7":
    error = GOError()
    error.handleFatal("You must upgrade networkx to at least version 1.7.")

from StorageFactory import StorageFactory
from GOXDiGraph import GOXDiGraph
from GOXGraph import GOXGraph
from GOProteinGraph import GOProteinGraph
from GOGraph import GOGraph
from GONode import GOTermNode, GOProteinNode
from Aspects import *
from GODiGraph import GODiGraph
from GOGraphBase import GOGraphBase
from SteinerTree import make_steiner_tree, make_prim_mst
from semGODiGraph import semGODiGraph

import XGraphWeighters
import Storage
