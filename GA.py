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


class GA:
    
    
    
    def __init__(self, system,populationSeed,evolutionSeed):
        
        
        
        self.system = system
        self.cnf = config.CONFIG()
        
        self.populationSize = self.cnf.populationSize
        self.populationPt = pop.POPULATION(self.populationSize)
        self.mutationProbability = self.cnf.mutationProbability

        self.rndPOP = random.Random()
        self.rndEVOL = random.Random()
        
        self.rndPOP.seed(populationSeed)
        self.rndEVOL.seed(evolutionSeed)
        
        self.autoAjustedWeight = True
        self.spreadWeight = 1.0
        self.makespanWeight = 1.0
        self.spreadMax = 0
        self.makespanMin = float('inf')
        self.TMPspreadMax = 0
        self.TMPmakespanMin = float('inf')
        
 #       self.system.FGCSmodel(self.rndPOP)
        
        


#******************************************************************************************
#   Solution adaptation
#******************************************************************************************


    def placeReplicasInCloud(self,chromosome):
        
        for i in iter(chromosome):
            i[self.system.cloudDeviceId]=1


#******************************************************************************************
#   END Solution adaptation
#******************************************************************************************



#******************************************************************************************
#   MUTATIONS
#******************************************************************************************


    def replicaIncreseValue(self,child,myvalue):
        
        for i in iter(child):
            if self.rndEVOL.random() > 0.5:
                startingPoint = self.rndEVOL.randint(0,self.system.fogNumber-1)
                indx = startingPoint
                indx = (indx + 1) % self.system.fogNumber
                while (i[indx]==myvalue) and (indx!=startingPoint):
                    indx = (indx + 1) % self.system.fogNumber
                i[indx]=myvalue
                
        self.placeReplicasInCloud(child)


        
    def replicaGrowth(self,child):
        self.replicaIncreseValue(child,1)
          
    def replicaShrink(self,child):
        self.replicaIncreseValue(child,0)
          
           
        
    def serviceShuffle(self,child):
        for i in range(0,self.system.serviceNumber/2):
            self.serviceReplace(child)
            
        self.placeReplicasInCloud(child)
        
        

    def serviceReplace(self,child):
        
        firstPoint = self.rndEVOL.randint(0,self.system.serviceNumber-1)
        secondPoint = self.rndEVOL.randint(0,self.system.serviceNumber-1)
        child[firstPoint],child[secondPoint] = child[secondPoint],child[firstPoint]
        
        self.placeReplicasInCloud(child)


    def sendToCloud(self,child):
        
        for i in iter(child):
            if self.rndEVOL.random() > 0.05:
                i = [0 for j in xrange(self.system.fogNumber)]
                
        self.placeReplicasInCloud(child)

    def spreadToFog(self,child):
        
        for i in iter(child):
            if self.rndEVOL.random() > 0.01:
                i = [1 for j in xrange(self.system.fogNumber)]

        self.placeReplicasInCloud(child)
        

      
    
    def mutate(self,child):
        
        mutationOperators = [] 
        mutationOperators.append(self.replicaGrowth)
        mutationOperators.append(self.replicaShrink)
        mutationOperators.append(self.serviceShuffle)
        mutationOperators.append(self.serviceReplace)
        mutationOperators.append(self.sendToCloud)
        mutationOperators.append(self.spreadToFog)
        
        mutationOperators[self.rndEVOL.randint(0,len(mutationOperators)-1)](child)

        

        
        
        
        

#******************************************************************************************
#   END MUTATIONS
#******************************************************************************************


#******************************************************************************************
#   CROSSOVER
#******************************************************************************************



    def crossoverMIO(self,f1,f2,offs):

        
        c1 = list()
        c2 = list()
        
        for i in range(0,self.system.serviceNumber):
            cuttingPoint = self.rndEVOL.randint(1,self.system.fogNumber-1)
            c1.append(f1[i][:cuttingPoint] + f2[i][cuttingPoint:])
            c2.append(f2[i][:cuttingPoint] + f1[i][cuttingPoint:])

        self.placeReplicasInCloud(c1)
        self.placeReplicasInCloud(c2)

        offs.append(c1)
        offs.append(c2)

        return c1,c2


        
        
        
    def crossover(self,f1,f2,offs):
        
        self.crossoverMIO(f1,f2,offs)




#******************************************************************************************
#   END CROSSOVER
#******************************************************************************************




#******************************************************************************************
#   Model constraints
#******************************************************************************************

    
    def notEnoughResource(self,chromosome):
        
        fogConsumResource = 0
        
        for fogId in range(0,self.system.fogNumber):
            for servId in range(0,self.system.serviceNumber):
                if chromosome[servId][fogId]==1:
                    fogConsumResource = fogConsumResource + self.system.serviceResources[servId]
            if fogConsumResource > self.system.fogResources[fogId]:
                return True
            #TODO si quiero normalizar las soluciones, es aquí que debería cambiar el placement para que ucmpla la constraint
        return False
                    
            


        
    def checkConstraints(self,chromosome):
             
#        if self.duplicatedReplicaInVM(pop.population[index]['block'],index):
#            print("duplicatedReplica")
#            return False
        if self.notEnoughResource(chromosome):
            print("resourceUsages")
            return False
        return True

#******************************************************************************************
#   END Model constraints
#******************************************************************************************



#******************************************************************************************
#   Service spread calculation
#******************************************************************************************

    def calculateServiceSpreadMIN(self,chromosome):
        
        totalSpread = 0
        for servPlace in iter(chromosome):
            elements = list()
            mymin = float('inf')
            for idx,val in enumerate(servPlace):
                if (val==1):
                    elements.append(idx)
            if len(elements)>1:
                for i in range(0,len(elements)-1):
                    for j in range(i+1,len(elements)):
                        mydist = self.system.devDistanceMatrix[elements[i]][elements[j]]
                        mymin = min(mydist,mymin) 
                servSpread = mymin / len(elements)
            else:
                servSpread = 0 #TODO que valor le pongo en el caso de que solo hay un elemento, es decir solo esta en cloud?
            
            totalSpread = totalSpread + servSpread
            
            
        return totalSpread
    
    
    def calculateServiceSpreadVARMULTN(self,chromosome):
        
        totalSpread = 0
        for servPlace in iter(chromosome):
            elements = list()
            mymin = float('inf')
            for idx,val in enumerate(servPlace):
                if (val==1):
                    elements.append(idx)
            if len(elements)>1:
                allTheValues = list()
                for i in range(0,len(elements)-1):
                    for j in range(i+1,len(elements)):
                        allTheValues.append(self.system.devDistanceMatrix[elements[i]][elements[j]])

                
                servSpread = math.sqrt(np.var(allTheValues) * len(allTheValues))

            else:
                servSpread = 0 #TODO que valor le pongo en el caso de que solo hay un elemento, es decir solo esta en cloud?
            
            totalSpread = totalSpread + servSpread
            
            
        return totalSpread    



    def calculateServiceSpread(self,chromosome):
        

        return self.calculateServiceSpreadMIN(chromosome)

#******************************************************************************************
#   END Service spread calculation
#******************************************************************************************


#******************************************************************************************
#   Service makespan calculation
#******************************************************************************************


    def calculateRecursiveMakespan(self, currentService, currentDevice,chromosome):
        
        servicePlacement = chromosome[currentService] #get the placement list of the current service
        if servicePlacement[currentDevice]==1:
            netTime = 0
            cpuTime = 0 #TODO execution time of the currentService in the current device
            closestDevice = currentDevice
        else:
            deviceDistances = self.system.devDistanceMatrix[currentDevice] # get the distances of the currentDevice with the other devices
            mask = [a*b for a,b in zip(servicePlacement,deviceDistances)] #select the distances of the devices where the service is placed
            #print mask
            netTime = min(i for i in mask if i > 0) # get the min value bigger than 0
            closestDevice = mask.index(netTime)
            #SI peta aquí diciendo que min() arg is an empty sequence es que hay una solucion que no considera emplazamiento en cloud y eso debería de no estar permitido.
                    
        #print "netTime:"+str(netTime)
         # get the device with the min distance value
        
        cpuTime = 0 #TODO execution time of the currentService in the closest device
        delayTime = netTime + cpuTime
        
        consumedServices = self.system.serviceMatrix[currentService] #get the services that need to be requested from the current service
        for idx,cServ in enumerate(consumedServices):  # calculate the makespan of the services to be requested for the case of having the current service placed in the closest device
            if (cServ==1):
                #print "recursive calculating "+str(idx)+" service for "+str(closestDevice)+" ggateway"
                delayTime = delayTime + self.calculateRecursiveMakespan(idx,closestDevice,chromosome)
        
        return delayTime

    def calculateServiceMakespan(self,chromosome):
        
        totMakeSpan = 0
        for servId,mobPlace in enumerate(self.system.mobilePlacementMatrix):
            for gatewayId in iter(mobPlace):
                #print "calculating "+str(servId)+" service for "+str(gatewayId)+" ggateway"
                totMakeSpan = totMakeSpan + self.calculateRecursiveMakespan(servId,gatewayId,chromosome)
        
        return totMakeSpan

#******************************************************************************************
#   END Service makespan calculation
#******************************************************************************************







#******************************************************************************************
#   Objectives and fitness calculation
#******************************************************************************************


    def calculateFitnessObjectives(self, pop, index):
        chr_fitness = {}
        chr_fitness["index"] = index
        
        chromosome=pop.population[index]
        
        if self.checkConstraints(chromosome):
            chr_fitness["makespan"] = self.calculateServiceMakespan(chromosome)
            chr_fitness["spread"] = self.calculateServiceSpread(chromosome)
            self.spreadMax = max(self.spreadMax,chr_fitness["spread"])
            self.makespanMin = min(self.makespanMin,chr_fitness["makespan"])
            chr_fitness["total"] = self.makespanWeight * chr_fitness["makespan"] - self.spreadWeight * chr_fitness["spread"] #minimizamos makespan y maximizamos spread
     
        else:
#            print ("not constraints")
            chr_fitness["makespan"] = float('inf')
            chr_fitness["spread"] = float('inf')
            chr_fitness["total"] = float('inf')
            
        return chr_fitness
    
    def normalizeTotalFitness(self,pop):
        for index,chr_fitness in enumerate(pop.fitness):
            chr_fitness["total"] = chr_fitness["makespan"] - (self.makespanMin/self.spreadMax) * chr_fitness["spread"] #minimizamos makespan y maximizamos spread

    def calculatePopulationFitnessObjectives(self,pop):   
        for index,citizen in enumerate(pop.population):
            cit_fitness = self.calculateFitnessObjectives(pop,index)
            pop.fitness[index] = cit_fitness
        if self.autoAjustedWeight:
            self.normalizeTotalFitness(pop)
            
        
         
    
#******************************************************************************************
#   END Objectives and fitness calculation
#******************************************************************************************

  
            




#******************************************************************************************
#   NSGA-II Algorithm
#******************************************************************************************

#            
#    def dominates(self,a,b):
#        #checks if solution a dominates solution b, i.e. all the objectives are better in A than in B
#        Adominates = True
#        #### OJOOOOOO Hay un atributo en los dictionarios que no hay que tener en cuenta, el index!!!
#        for key in a:
#            if key!="index":  #por ese motivo está este if.
#                if b[key]<=a[key]:
#                    Adominates = False
#                    break
#        return Adominates        
#
#        
#    def crowdingDistancesAssigments(self,popT,front):
#        
#        for i in front:
#            popT.crowdingDistances[i] = float(0)
#            
#        frontFitness = [popT.fitness[i] for i in front]
#        #OJOOOOOO hay un atributo en el listado que es index, que no se tiene que tener en cuenta.
#        for key in popT.fitness[0]:
#            if key!="index":   #por ese motivo está este if.
#                orderedList = sorted(frontFitness, key=lambda k: k[key])
#                
#                popT.crowdingDistances[orderedList[0]["index"]] = float('inf')
#                minObj = orderedList[0][key]
#                popT.crowdingDistances[orderedList[len(orderedList)-1]["index"]] = float('inf')
#                maxObj = orderedList[len(orderedList)-1][key]
#                
#                normalizedDenominator = float(maxObj-minObj)
#                if normalizedDenominator==0.0:
#                    normalizedDenominator = float('inf')
#        
#                for i in range(1, len(orderedList)-1):
#                    popT.crowdingDistances[orderedList[i]["index"]] += (orderedList[i+1][key] - orderedList[i-1][key])/normalizedDenominator
#
#    def calculateCrowdingDistances(self,popT):
#        
#        i=0
#        while len(popT.fronts[i])!=0:
#            self.crowdingDistancesAssigments(popT,popT.fronts[i])
#            i+=1
#
#
#    def calculateDominants(self,popT):
#        
#        for i in range(len(popT.population)):
#            popT.dominatedBy[i] = set()
#            popT.dominatesTo[i] = set()
#            popT.fronts[i] = set()
#
#        for p in range(len(popT.population)):
#            for q in range(p+1,len(popT.population)):
#                if self.dominates(popT.fitness[p],popT.fitness[q]):
#                    popT.dominatesTo[p].add(q)
#                    popT.dominatedBy[q].add(p)
#                if self.dominates(popT.fitness[q],popT.fitness[p]):
#                    popT.dominatedBy[p].add(q)
#                    popT.dominatesTo[q].add(p)        
#
#    def calculateFronts(self,popT):
#
#        addedToFronts = set()
#        
#        i=0
#        while len(addedToFronts)<len(popT.population):
#            popT.fronts[i] = set([index for index,item in enumerate(popT.dominatedBy) if item==set()])
#            addedToFronts = addedToFronts | popT.fronts[i]
#            
#            for index,item in enumerate(popT.dominatedBy):
#                if index in popT.fronts[i]:
#                    popT.dominatedBy[index].add(-1)
#                else:
#                    popT.dominatedBy[index] = popT.dominatedBy[index] - popT.fronts[i]
#            i+=1        
#            
#    def fastNonDominatedSort(self,popT):
#        
#        self.calculateDominants(popT)
#        self.calculateFronts(popT)
             
                
#******************************************************************************************
#   END NSGA-II Algorithm
#******************************************************************************************


#******************************************************************************************
#   Evolution based on NSGA-II 
#******************************************************************************************




    def generatePopulation(self,popT):
        
        for individual in range(self.populationSize):
            chromosome = [[0 for j in xrange(self.system.fogNumber)] for i in xrange(self.system.serviceNumber)]
        
            for iService in iter(chromosome):
                iService[self.rndPOP.randint(0,len(iService)-1)] = 1
                
            self.placeReplicasInCloud(chromosome)
        
            popT.population[individual]=chromosome
            
        self.calculatePopulationFitnessObjectives(popT)
            
#        self.calculateSolutionsWorkload(popT)
#        self.calculatePopulationFitnessObjectives(popT)


    def tournamentSelection(self,k,popSize):
        selected = sys.maxint 
        for i in range(k):
            selected = min(selected,self.rndEVOL.randint(0,popSize-1))
        return selected
           
    def fatherSelection(self, orderedFathers): #TODO
        i = self.tournamentSelection(2,len(orderedFathers))
        return  orderedFathers[i]["index"]
        

    def orderPopulation(self,popT):
        valuesToOrder=[]
        for i,v in enumerate(popT.fitness):
            citizen = {}
            citizen["index"] = i
            citizen["fitness"] = v["total"]
            valuesToOrder.append(citizen)
        
             
        return sorted(valuesToOrder, key=lambda k: (k["fitness"]))

    def evolveToOffspring(self):
        
        offspring = pop.POPULATION(self.populationSize)
        offspring.population = []

        orderedFathers = self.orderPopulation(self.populationPt)
        

        #offspring generation

        while len(offspring.population)<(self.populationSize):
            father1 = self.fatherSelection(orderedFathers)
            father2 = father1
            while father1 == father2:
                father2 = self.fatherSelection(orderedFathers)
            #print "[Father selection]: Father1: %i **********************" % father1
            #print "[Father selection]: Father1: %i **********************" % father2
            
            self.crossover(self.populationPt.population[father1],self.populationPt.population[father2],offspring.population)
        
        #offspring mutation
        
        for index,children in enumerate(offspring.population):
            if self.rndEVOL.uniform(0,1) < self.mutationProbability:
                self.mutate(children)
                #print "[Offsrping generation]: Children %i MUTATED **********************" % index
            
        #print "[Offsrping generation]: Population GENERATED **********************"  
        
        return offspring

        
#    def crowdedComparisonOrder(self,popT):
#        valuesToOrder=[]
#        for i,v in enumerate(popT.crowdingDistances):
#            citizen = {}
#            citizen["index"] = i
#            citizen["distance"] = v
#            citizen["rank"] = 0
#            valuesToOrder.append(citizen)
#        
#        f=0    
#        while len(popT.fronts[f])!=0:
#            for i,v in enumerate(popT.fronts[f]):
#                valuesToOrder[v]["rank"]=f
#            f+=1
#             
#        return sorted(valuesToOrder, key=lambda k: (k["rank"],-k["distance"]))
#


#
#        
#    def evolveAIA(self):
#        
#        offspring = pop.POPULATION(self.populationSize)
#        offspring.population = []
#
#        orderedFathers = self.crowdedComparisonOrder(self.populationPt)
#        
#
#        #offspring generation
#
#        while len(offspring.population)<self.populationSize:
#            father1 = self.fatherSelection(orderedFathers)
#            children = copy.deepcopy(self.populationPt.population[father1])
#            if self.rndEVOL.uniform(0,1) < self.mutationProbability:
#                self.mutate(children)
#            offspring.population.append(children)
#            
#        self.populationPt = offspring
#       
#        self.calculateSolutionsWorkload(self.populationPt)
#        self.calculatePopulationFitnessObjectives(self.populationPt)
#        self.fastNonDominatedSort(self.populationPt)
#        self.calculateCrowdingDistances(self.populationPt)        
#                 
#            
#        
#        return offspring

    def evolveGA(self):
        
        offspring = pop.POPULATION(self.populationSize)
        offspring.population = []

        offspring = self.evolveToOffspring()
        
        if self.autoAjustedWeight:
            populationRt = offspring.populationUnion(self.populationPt,offspring)
            self.calculatePopulationFitnessObjectives(populationRt)
        else:
            self.calculatePopulationFitnessObjectives(offspring)
            populationRt = offspring.populationUnion(self.populationPt,offspring)
        
       
        orderedElements = self.orderPopulation(populationRt)
        
        finalPopulation = pop.POPULATION(self.populationSize)
        
        for i in range(self.populationSize):
            finalPopulation.population[i] = populationRt.population[orderedElements[i]["index"]]
            finalPopulation.fitness[i] = populationRt.fitness[orderedElements[i]["index"]]

        for i,v in enumerate(finalPopulation.fitness):
            finalPopulation.fitness[i]["index"]=i        
        
        self.populationPt = finalPopulation
        
#       
#
#
#        
#       
#    def evolveNSGA2(self):
#        
#        offspring = pop.POPULATION(self.populationSize)
#        offspring.population = []
#
#        offspring = self.evolveToOffspring()
#        
#        self.calculateSolutionsWorkload(offspring)
#        self.calculatePopulationFitnessObjectives(offspring)
#        
#       
#        
#        populationRt = offspring.populationUnion(self.populationPt,offspring)
#        
#        self.fastNonDominatedSort(populationRt)
#        self.calculateCrowdingDistances(populationRt)
#        
#        orderedElements = self.crowdedComparisonOrder(populationRt)
#        
#        finalPopulation = pop.POPULATION(self.populationSize)
#        
#        for i in range(self.populationSize):
#            finalPopulation.population[i] = populationRt.population[orderedElements[i]["index"]]
#            finalPopulation.fitness[i] = populationRt.fitness[orderedElements[i]["index"]]
#            finalPopulation.vmsUsages[i] = populationRt.vmsUsages[orderedElements[i]["index"]]
#
#        for i,v in enumerate(finalPopulation.fitness):
#            finalPopulation.fitness[i]["index"]=i        
#        
#        self.populationPt = finalPopulation
#        
#        
#        self.fastNonDominatedSort(self.populationPt)
#        self.calculateCrowdingDistances(self.populationPt)
#        


        
       
        

#******************************************************************************************
#  END Evolution based on NSGA-II 
#******************************************************************************************



