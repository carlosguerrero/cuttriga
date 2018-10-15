#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:56:02 2017

@author: carlos
"""


import networkx as nx




G = nx.read_graphml('euclidean100unordered.graphml')
G = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)
mapping=dict(zip(G.nodes(),range(0,len(G.nodes))))
H=nx.relabel_nodes(G,mapping) # nodes a..z
nx.write_graphml(H, "euclidean100.graphml")        


    
       
