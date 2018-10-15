#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:56:02 2017

@author: carlos
"""
import copy
import random as random
from datetime import datetime

class CONFIG:
    
    def __init__(self):
        
        
        self.topologyFile = 'topologyMatrices.dat' #nombre donde se guardan los datos de la topologia
        self.topologyGraphml = 'scenario/lobster100.graphml' #nombre donde se guarda el json de la topologia
        self.topologyJson = 'scenario/topology.former.json' #nombre donde se guarda el json de la topologia
        self.applicationJson = 'scenario/threeapps.json' #nombre donde se guarda el json de la topologia
        self.userJson = 'scenario/user.json' #nombre donde se guarda el json de la topologia
        self.populationSize = 400#100
        self.mutationProbability = 0.25
        self.numberGenerations = 20
        self.T=20 # parameter of MOAE/D
        self.numberOfSubproblems = 13 #parameter to obtain a number of sulutions of N=103 for MOAE/D
        self.numberOfReplicatedApps = 1
        self.numberOfIoTGateways = 20
        self.numberofIoTDevicesPerGw = 1
        self.timeVerbose = True
        self.storeData = False
        self.retailEPmoead = True
        self.EPlimit = self.populationSize
        
#        self.modelSeed = 3
#        self.populationSeed = 300
#        self.evolutionSeed = 28


        self.modelSeed = 50
        self.populationSeed = 100
        self.evolutionSeed = 888
    
       
    def getTime(self):
        return datetime.now()
        
    def printTime(self,timeold,message_str):
        time=datetime.now()
        if self.timeVerbose:
            print message_str+str(time-timeold)
        return time-timeold