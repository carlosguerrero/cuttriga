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
import sys
import json


####The call is
#subprocess.check_call(['python', 'CLcallMainGA.py' , str(numApps), networkTopology, gatype, executionId])

#numApps=int(sys.argv[1])
#networkTopology=sys.argv[2]
#gatype=sys.argv[3]
#executionId=sys.argv[4]


#gatype = 'nsga2'
numApps = 10
networkTopology = 'scenario/barabasi100.graphml'
networkTopology = 'nxgenerated.500'
executionId = 'moead500-10'
gatype = 'moead'

#executionId= datetime.now().strftime('%Y%m%d%H%M%S')
file_path = "./"+executionId
    
cnf = config.CONFIG()
if cnf.storeData:    
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    outputCSV = open(file_path+'/execution_data.csv', 'wb')
    strTitle = "topology;algorithm;numapss;total;wspr;wmak;wres;spread;makespan;resources"
    outputCSV.write(strTitle+"\n")
f_stdout = open('./log.txt', 'wb')
    

#networkTopologyStr = networkTopology[networkTopology.find("/")+1:networkTopology.find(".")]
networkTopologyStr = networkTopology    
        
cnf = config.CONFIG()
cnf.topologyGraphml = networkTopology
cnf.numberOfReplicatedApps = numApps
system = systemmodel.SYSTEMMODEL(cnf)
#no permite bucles
#los servicios y fog devices deben de estar ordenador desde 0 y con ids consecutivos, sin dejar ninguno en blanco     
system.FGCSmodel3(cnf.modelSeed)


if gatype == 'weightedga':            
#g = ga.GA(system,300,28)
    g = wga.weightedGA(system,cnf.populationSeed,cnf.evolutionSeed,cnf)
    
if gatype == 'nsga2':
    g = nsga2.NSGA2(system,cnf.populationSeed,cnf.evolutionSeed,cnf)

if gatype == 'moead':
    g = moead.MOEAD(system,cnf.populationSeed,cnf.evolutionSeed,cnf)  



generationSolution = list()
generationPareto = list()


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
#        fitnessSol = list()
#        for i in g.corega.populationPt.fronts[0]: 
#            fitnessSol.append(g.corega.populationPt.fitness[i])
#        generationPareto.append(fitnessSol)
    

for i in range(0,cnf.numberGenerations):
    
    t=cnf.getTime()
    g.evolve()
    f_stdout.write(time.strftime("%H:%M:%S")+'\n')
    f_stdout.write("Population size: "+str(len(g.corega.populationPt.population))+'\n')
    timestep=cnf.printTime(t,"Evolving time: ")
    f_stdout.write(networkTopologyStr+":"+gatype+":"+str(numApps)+":"+"Generation number "+str(i)+'\n')
    minV = float('inf')
    minIdx = -1
    for idx,v in enumerate(g.corega.populationPt.fitness):
        if v['total']<minV:
            minIdx = idx
            minV = v['total']
    f_stdout.write(json.dumps(g.corega.populationPt.fitness[minIdx])+'\n')
    f_stdout.flush()

    
    if cnf.storeData:
        currentSolution = {}
        currentSolution['fitness']=g.corega.populationPt.fitness[minIdx]
        #currentSolution['population']=g.corega.populationPt.population[minIdx]
        currentSolution['executiontime']=timestep
        generationSolution.append(currentSolution)
        
#        for i in g.corega.populationPt.fronts[0]: 
#            fitnessSol.append(g.corega.populationPt.fitness[i])
#        generationPareto.append(fitnessSol)
    
    #print "[Generation number "+str(i)+" of "+"experimentName"+"] "+ str(time-timeold)
    
if cnf.storeData:
    
 ## ['nsga2','weightedga','moead'] 
    generationPareto = {}
    generationPareto['fitness'] = list()
    generationPareto['population'] = list()  
    if gatype == 'nsga2':
        for i in g.corega.populationPt.fronts[0]: 
            generationPareto['fitness'].append(g.corega.populationPt.fitness[i])
            #generationPareto['population'].append(g.corega.populationPt.population[i])
    else:
        for i in g.corega.populationPt.fitness: 
            generationPareto['fitness'].append(i)
#        for i in g.corega.populationPt.population: 
#            generationPareto['population'].append(i)            

    
    
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
f_stdout.close()
