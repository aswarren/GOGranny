#!/usr/bin/env python

from GOGranny import *
from GOGranny.GONode import GONode as GN
from math import log
import networkx as nx
import matplotlib.pyplot as plt
import itertools


def create_tree(r, h):
	result_graph = semGODiGraph(None, Aspects.BP)
        internal_graph=nx.balanced_tree(r=r,h=h,create_using=nx.DiGraph()) #gnp_random_graph(10,0.5,directed=True)
        for u,v in internal_graph.edges_iter():
                result_graph.add_edge(GN(nodetype=GN.TERM_TYPE,dbid=u),GN(nodetype=GN.TERM_TYPE,dbid=v))
        nx.reverse(result_graph, copy=False) #make the edges point up not down
        root_list=[n for n,d in result_graph.out_degree().items() if d==0]
        result_graph.root=root_list[0]
	result_graph.semMakeGraph()
        return result_graph

def plotTreeBehavior():
    marker = itertools.cycle(('+', '.', 'o', '*', ','))
    color = itertools.cycle(('r', 'g', 'b', 'c', 'm', 'y', 'k'))
    lines={}
    for h in range(2,5):#height
        x_values=[]
        y_values=[]
        for r in range(2,10):#branching factor
            cur_graph=create_tree(r,h)
            max_entropy=-2*log(1/float(cur_graph.num_nodes),2)
            min_entropy=-1*log(1/float(cur_graph.num_nodes),2)
            cur_entropy=cur_graph.calc_graph_uncert()
            cur_index=(cur_entropy-min_entropy)/(max_entropy-min_entropy)
            x_values.append(r)
            y_values.append(cur_index)
        lines["height:"+str(h)]=plt.plot(x_values, y_values, str(color.next())+str(marker.next()),label="height "+str(h))
    plt.legend(loc=4)
    plt.axis([1,11,.4,1.1])
    plt.title('Branching factor vs. TI for balanced trees')
    plt.ylabel('Term-Independence')
    plt.xlabel('Branching factor')
    plt.savefig("./test_fig.png")

if __name__ == '__main__':
    plotTreeBehavior()
	
