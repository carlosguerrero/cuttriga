# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal
"""

import numpy as np
import random as random
import sys
import POPULATION as pop
import matplotlib.pyplot as plt3d
import SYSTEMMODEL as systemmodel
import copy
import CONFIG as config
import math as math
import GAcore as gacore



class weightedGA:
    
    
    
    def __init__(self, system,populationSeed,evolutionSeed,conf_):
        

        self.corega = gacore.GAcore(system,populationSeed,evolutionSeed,conf_)
        
        self.corega.generatePopulation(self.corega.populationPt)
        

    def evolveToOffspring(self):
        
        offspring = pop.POPULATION(self.corega.populationSize)
        offspring.population = []

        orderedFathers = self.corega.orderPopulation(self.corega.populationPt)
        

        #offspring generation

        while len(offspring.population)<(self.corega.populationSize):
            father1 = self.corega.fatherSelection(orderedFathers)
            father2 = father1
            while father1 == father2:
                father2 = self.corega.fatherSelection(orderedFathers)
            #print "[Father selection]: Father1: %i **********************" % father1
            #print "[Father selection]: Father1: %i **********************" % father2
            
            self.corega.crossover(self.corega.populationPt.population[father1],self.corega.populationPt.population[father2],offspring.population)
        
        #offspring mutation
        
        for index,children in enumerate(offspring.population):
            if self.corega.rndEVOL.uniform(0,1) < self.corega.mutationProbability:
                self.corega.mutate(children)
                #print "[Offsrping generation]: Children %i MUTATED **********************" % index
            
        #print "[Offsrping generation]: Population GENERATED **********************"  
        
        return offspring

 
    def evolve(self):
        
        offspring = pop.POPULATION(self.corega.populationSize)
        offspring.population = []

        offspring = self.evolveToOffspring()
        
#        if self.autoAjustedWeight:
#            populationRt = offspring.populationUnion(self.populationPt,offspring)
#            self.calculatePopulationFitnessObjectives(populationRt)
#        else:
        self.corega.calculatePopulationFitnessObjectives(offspring)
        populationRt = offspring.populationUnion(self.corega.populationPt,offspring)
        
        del self.corega.populationPt
        del offspring
        
       
        orderedElements = self.corega.orderPopulation(populationRt)
        
        finalPopulation = pop.POPULATION(self.corega.populationSize)
        
        for i in range(self.corega.populationSize):
            finalPopulation.population[i] = copy.deepcopy(populationRt.population[orderedElements[i]["index"]])
            finalPopulation.fitness[i] = copy.deepcopy(populationRt.fitness[orderedElements[i]["index"]])
        
        del populationRt

        for i,v in enumerate(finalPopulation.fitness):
            finalPopulation.fitness[i]["index"]=i        
        
        self.corega.populationPt = finalPopulation
        

