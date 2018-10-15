#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:56:02 2017

@author: carlos
"""
import copy

class POPULATION:
    
    def populationUnion(self,a,b):
        
        r=POPULATION(1)
        
        r.population = copy.deepcopy(a.population) + copy.deepcopy(b.population)
        r.vmsUsages = copy.deepcopy(a.vmsUsages) + copy.deepcopy(b.vmsUsages)
        r.pmsUsages = copy.deepcopy(a.pmsUsages) + copy.deepcopy(b.pmsUsages)
        r.fitness = copy.deepcopy(a.fitness) + copy.deepcopy(b.fitness)
        r.fitnessNormalized = copy.deepcopy(a.fitnessNormalized) + copy.deepcopy(b.fitnessNormalized)
        for i,v in enumerate(r.fitness):
            r.fitness[i]["index"]=i
        r.dominatesTo = copy.deepcopy(a.dominatesTo) + copy.deepcopy(b.dominatesTo)
        r.dominatedBy = copy.deepcopy(a.dominatedBy) + copy.deepcopy(b.dominatedBy)
        r.fronts = copy.deepcopy(a.fronts) + copy.deepcopy(b.fronts)
        r.crowdingDistances = copy.deepcopy(a.crowdingDistances) + copy.deepcopy(b.crowdingDistances)
        
        
        return r
        
    def paretoExport(self):
        
        paretoPop = self.__class__(len(self.population))
              
        
        for i in self.fronts[0]:
            paretoPop.population[i] = self.population[i]
            paretoPop.fitness[i] = self.fitness[i]

            
        return paretoPop
    
    def replaceSolution(self,newPop,newId,oldPop,oldId):
        oldPop.population[oldId] = newPop.population[newId]
        oldPop.fitness[oldId] = newPop.fitness[newId]
        oldPop.fitnessNormalized[oldId] = newPop.fitnessNormalized[newId]
        oldPop.dominatesTo[oldId] = newPop.dominatesTo[newId]
        oldPop.dominatedBy[oldId] = newPop.dominatedBy[newId]
        oldPop.fronts[oldId] = newPop.fronts[newId]
        oldPop.crowdingDistances[oldId] = newPop.crowdingDistances[newId]
        oldPop.vmsUsages[oldId] = newPop.vmsUsages[newId]
        oldPop.pmsUsages[oldId] = newPop.pmsUsages[newId]

    def remove(self,idx):

        del self.population[idx]
        del self.fitness[idx]
        del self.fitnessNormalized[idx]
        del self.dominatesTo[idx]
        del self.dominatedBy[idx]
        del self.fronts[idx]
        del self.crowdingDistances[idx]
        del self.vmsUsages[idx]
        del self.pmsUsages[idx]
        
    def appendAndIncrease(self,solution):
        
        size = 1
        self.population.append(solution)
        #self.population = self.population + [list()]*size
        self.fitness = self.fitness + [{}]*size
        self.fitnessNormalized = self.fitnessNormalized + [{}]*size
        self.dominatesTo = self.dominatesTo + [set()]*size
        self.dominatedBy = self.dominatedBy + [set()]*size
        self.fronts = self.fronts + [set()]*size
        self.crowdingDistances = self.crowdingDistances + [float(0)]*size
        self.vmsUsages = self.vmsUsages + [list()]*size
        self.pmsUsages = self.pmsUsages + [list()]*size

    def __init__(self,size):
        
        self.population = [list()]*size
        self.fitness = [{}]*size
        self.fitnessNormalized = [{}]*size
        self.dominatesTo = [set()]*size
        self.dominatedBy = [set()]*size
        self.fronts = [set()]*size
        self.crowdingDistances = [float(0)]*size
        self.vmsUsages = [list()]*size
        self.pmsUsages = [list()]*size
    
   
