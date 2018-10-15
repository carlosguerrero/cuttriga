    #!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 08:04:42 2017
@author: carlos
"""


import weightedGA as wga
import SYSTEMMODEL as systemmodel
import pickle
from datetime import datetime
import os
import copy
import time
import CONFIG as config
import NSGA2 as nsga2
import MOEAD as moead

numAppsArray = [1,2,3]
numAppsArray = [25]

networkTopologyArray = ['scenario/lobster100.graphml','scenario/barabasi100.graphml','scenario/euclidean100.graphml']
networkTopologyArray = ['nxgenerated.1000']

#networkTopologyArray = ['scenario/lobster100.graphml']
                        
#el nsga ha petado en el lobster y el barabasi, para los de 3 lo ejecuto en el mac


gatypeArray = ['nsga2','weightedga','moead']
#gatypeArray = ['nsga2']
#gatypeArray = ['weightedga']
#gatypeArray = ['nsga2']


executionId= datetime.now().strftime('%Y%m%d%H%M%S')
file_path = "./"+executionId
    
cnf = config.CONFIG()
if cnf.storeData:    
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    outputCSV = open(file_path+'/execution_data.csv', 'wb')
    strTitle = "topology;algorithm;numapss;total;wspr;wmak;wres;spread;makespan;resources"
    outputCSV.write(strTitle+"\n")
    

for numApps in numAppsArray:
    for networkTopology in networkTopologyArray:
        networkTopologyStr = networkTopology[networkTopology.find("/")+1:networkTopology.find(".")]
        for gatype in gatypeArray:
        
            print "."
        
            cnf = config.CONFIG()
            print "."
            cnf.topologyGraphml = networkTopology
            print "."
            cnf.numberOfReplicatedApps = numApps
            print "."
            system = systemmodel.SYSTEMMODEL(cnf)
            #no permite bucles
            #los servicios y fog devices deben de estar ordenador desde 0 y con ids consecutivos, sin dejar ninguno en blanco     
            print "."
            system.FGCSmodel3(cnf.modelSeed)
            print "."
            
            if gatype == 'weightedga':            
            #g = ga.GA(system,300,28)
                g = wga.weightedGA(system,cnf.populationSeed,cnf.evolutionSeed,cnf)
                
            if gatype == 'nsga2':
                g = nsga2.NSGA2(system,cnf.populationSeed,cnf.evolutionSeed,cnf)
            
            if gatype == 'moead':
                g = moead.MOEAD(system,cnf.populationSeed,cnf.evolutionSeed,cnf)  
            
            print "."
            
            generationSolution = list()
            generationPareto = list()

            print "."
            minV = float('inf')
            minIdx = -1
            for idx,v in enumerate(g.corega.populationPt.fitness):
                if v['total']<minV:
                    minIdx = idx
                    minV = v['total']
            if len(g.corega.populationPt.population)>0:
                print g.corega.populationPt.fitness[minIdx]            

                if cnf.storeData:
                    currentSolution = {}
                    currentSolution['fitness']=g.corega.populationPt.fitness[minIdx]
                    currentSolution['population']=g.corega.populationPt.population[minIdx]
                    currentSolution['executiontime']=0
                    generationSolution.append(currentSolution)
                    generationPareto.append(g.corega.populationPt.paretoExport())
                
            print "."
            for i in range(0,cnf.numberGenerations):
                
                t=cnf.getTime()
                g.evolve()
                print time.strftime("%H:%M:%S")
                print "Population size: "+str(len(g.corega.populationPt.population))
                timestep=cnf.printTime(t,"Evolving time: ")
                print networkTopologyStr+":"+gatype+":"+str(numApps)+":"+"Generation number "+str(i)
                minV = float('inf')
                minIdx = -1
                for idx,v in enumerate(g.corega.populationPt.fitness):
                    if v['total']<minV:
                        minIdx = idx
                        minV = v['total']
                print g.corega.populationPt.fitness[minIdx]
                

                
                if cnf.storeData:
                    currentSolution = {}
                    currentSolution['fitness']=g.corega.populationPt.fitness[minIdx]
                    currentSolution['population']=g.corega.populationPt.population[minIdx]
                    currentSolution['executiontime']=timestep
                    generationSolution.append(currentSolution)
#                    generationPareto.append(g.corega.populationPt.paretoExport())
                
                #print "[Generation number "+str(i)+" of "+"experimentName"+"] "+ str(time-timeold)
                print "[Generation number "+str(i)+" of "+"experimentName"+"] "
                
            if cnf.storeData:
                
                generationPareto = {}
                generationPareto['fitness'] = list()
                generationPareto['population'] = list()  
                if gatype == 'nsga2':
                    for i in g.corega.populationPt.fronts[0]: 
                        generationPareto['fitness'].append(g.corega.populationPt.fitness[i])
                        generationPareto['population'].append(g.corega.populationPt.population[i])
                else:
                    for i in g.corega.populationPt.fitness: 
                        generationPareto['fitness'].append(i)
                    for i in g.corega.populationPt.population: 
                        generationPareto['population'].append(i)            

       
                
                idString =networkTopologyStr+"."+gatype+"."+str(numApps)+"."
                output = open(file_path+'/'+idString+'selectedEvolution.pkl', 'wb')
                pickle.dump(generationSolution, output)
                output.close()

                output = open(file_path+'/'+idString+'paretoEvolution.pkl', 'wb')
                pickle.dump(generationPareto, output)
                output.close()

                strValue = networkTopologyStr+";"+gatype+";"+str(numApps)+";"+str(g.corega.populationPt.fitness[minIdx]['total'])+";"+str(g.corega.populationPt.fitness[minIdx]['wspr'])+";"+str(g.corega.populationPt.fitness[minIdx]['wmak'])+";"+str(g.corega.populationPt.fitness[minIdx]['wres'])+";"+str(g.corega.populationPt.fitness[minIdx]['spread'])+";"+str(g.corega.populationPt.fitness[minIdx]['makespan'])+";"+str(g.corega.populationPt.fitness[minIdx]['resources'])
                outputCSV.write(strValue+"\n")
                outputCSV.flush()
                
if cnf.storeData:
    outputCSV.close()
