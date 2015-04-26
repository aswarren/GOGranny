#!/usr/bin/env python

from GOGranny import *
from GOGranny.GONode import GONode as GN
from math import log
from math import ceil
import networkx as nx
import matplotlib.pyplot as plt
import itertools
from operator import xor
import ipdb

def create_tree(r, h=None, num_nodes=None):
    #need to have either height or num_nodes
    assert xor(bool(h),bool(num_nodes))
    to_remove=0
    if num_nodes != None:
        if r==1:
            h=num_nodes
        else:
            h=ceil(log(num_nodes*(r-1)+1, r)-1)
            init_size=(r**(h+1)-1)/(r-1)
            to_remove=int(init_size-num_nodes)
        
    #branching factor of 1 does not seem to work for nx.balanced_tree
    result_graph = semGODiGraph(None, Aspects.BP)
    if r ==1:
        for u in range(0,h):
            v=u+1
            result_graph.add_edge(GN(nodetype=GN.TERM_TYPE,dbid=v),GN(nodetype=GN.TERM_TYPE,dbid=u))
    else:	
        internal_graph=nx.balanced_tree(r=r,h=h,create_using=nx.DiGraph()) #gnp_random_graph(10,0.5,directed=True)
        current=internal_graph.number_of_nodes()
        remove_nodes=range(current-to_remove,current)
        for r in remove_nodes:
            internal_graph.remove_node(r)
        if num_nodes != None:
            assert num_nodes == internal_graph.number_of_nodes()
        for u,v in internal_graph.edges_iter():
            result_graph.add_edge(GN(nodetype=GN.TERM_TYPE,dbid=u),GN(nodetype=GN.TERM_TYPE,dbid=v))
        nx.reverse(result_graph, copy=False) #make the edges point up not down
        root_list=[n for n,d in result_graph.out_degree().items() if d==0]
        result_graph.root=root_list[0]
    result_graph.semMakeGraph()
    return result_graph
    
def plotTreeBehavior():
    marker = itertools.cycle(('+', '.', '*'))
    color = itertools.cycle(('r', 'g', 'b', 'c', 'm', 'y', 'k'))
    lines={}
    for h in range(2,5):#height
        x_values=[]
        y_values=[]
        for r in range(1,10):#branching factor
            cur_graph=create_tree(r,h)
            max_entropy=-2*log(1/float(cur_graph.num_nodes),2)
            min_entropy=-1*log(1/float(cur_graph.num_nodes),2)
            cur_entropy=cur_graph.calc_graph_uncert()
            cur_index=(cur_entropy-min_entropy)/(max_entropy-min_entropy)
            x_values.append(r)
            y_values.append(cur_index)
        lines["height:"+str(h)]=plt.plot(x_values, y_values, color=str(color.next()), marker=str(marker.next()),label="height "+str(h), linestyle="-")
    plt.legend(loc=4)
    plt.axis([0,11,-0.1,1.1])
    plt.title('Branching factor vs. TI for balanced trees')
    plt.ylabel('Term-Independence')
    plt.xlabel('Branching factor')
    plt.savefig("./test_fig.png")

if __name__ == '__main__':
    plotTreeBehavior()

