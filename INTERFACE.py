#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:56:02 2017

@author: carlos
"""
import copy
import random as random
import CONFIG as config
from topology import Entity, Topology
import json
import networkx as nx

class INTERFACE:
    
    def __init__(self):
        
        
        cnf = config.CONFIG()
#        with open(cnf.topologyJson,'r') as json_data:
#            myjson = json.load(json_data)
#            json_data.close()
#                    
        f = open (cnf.topologyJson,'r')
        txtjson = f.read()
        f.close() 
        txtjson=txtjson.replace("Entity.ENTITY_FOG","\"Entity.ENTITY_FOG\"")
        txtjson=txtjson.replace("Entity.ENTITY_CLUSTER","\"Entity.ENTITY_CLUSTER\"")
        myjson = json.loads(txtjson)



        print myjson

        t = Topology()
        t.load(myjson)

        devDistanceMatrix = [[0 for j in xrange(len(t.G.nodes))] for i in xrange(len(t.G.nodes))]


        
        for i in range(0, len(t.G.nodes)):
            for j in range(i,len(t.G.nodes)):       
        
                
                mylength = nx.shortest_path_length(t.G, source=i, target=j, weight="weight")
                devDistanceMatrix[i][j]=mylength
                devDistanceMatrix[j][i]=mylength

        
        
#        t.write("network_ex1.gexf")
        #t.draw()
#        allshortest = nx.shortest_path(t.G,weight="weight")
#        for i in range(0, len(allshortest)):
#            for j in range(0,len(allshortest[i])):
#                mypath = allshortest[i][j]
#                    
#                distance = len(allshortest[i][j]) #TODO hay que considerar las latencia
#                source = allshortest[i][j][0]
#                dest = allshortest[i][j][-1]
#                print distance
#                print source
#                print dest
#                print ":::::"
                
                
                
                

    
       
