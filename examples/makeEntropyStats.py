#!/usr/bin/env python
# -*- coding: utf-8 -*-
from GOGranny import *
import networkx as nx
import pandas as pd
from math import log
import os, sys

#Calculate entropy of the ontology and create and image as well
def main(init_args):

	if(len(init_args)<2): 
		print "Usage: makeEntropyStats.py [onto_cat] [owl_go_file]"
		sys.exit()
	
	onto_cat=init_args[0]
	go_files=init_args[1:]
	results = pd.DataFrame(columns=['date','entropy','TI','edges','nodes','in_degree','out_degree','degree'])
	num_file=0
	for go_file in go_files:
                print "creating stats for "+go_file
		num_file+=1
		#expand tilde to be actual home directory
		go_file=os.path.expanduser(go_file)

		storage= StorageFactory.makeStorage(Storage.Types.FILEBASED, obofile=go_file, hardEvidence=False)

		cur_graph=semGODiGraph(storage, getattr(Aspects,onto_cat))
		cur_graph.makeGraph()
		graph_uncert=cur_graph.calc_graph_uncert()
		in_degree=cur_graph.in_degree()
		out_degree=cur_graph.out_degree()
		#eccentricity=nx.eccentricity(cur_graph)
		#diameter=nx.diameter(cur_graph)
		degree_total=[]
		for k in in_degree.keys():
			x=0
			y=0
			if k in in_degree: x=in_degree[k]
			if k in out_degree: y=out_degree[k]
			degree_total.append(x+y)
		date=storage.date.split(' ')[0].replace(':','-')
		min_uncert=-log(float(1)/cur_graph.num_nodes,2)
		max_uncert=min_uncert*2
		ti=(graph_uncert-min_uncert)/(max_uncert-min_uncert)#for clarity. could just be min_uncert.
		cur_row={'date':date,'TI':ti,'entropy':graph_uncert,'edges':cur_graph.number_of_edges(),'nodes':cur_graph.num_nodes,'in_degree':float(sum(out_degree.values()))/len(degree_total),'out_degree':float(sum(in_degree.values()))/len(degree_total),'degree':float(sum(degree_total))/len(degree_total)}
		results.loc[num_file]=pd.Series(cur_row)
	results.to_csv(onto_cat+'_go_stats_table.txt',sep="\t",mode='w')
			
if __name__ == "__main__":
        main(sys.argv[1:])
