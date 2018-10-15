    #!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 08:04:42 2017
@author: carlos
"""


import pickle
import CONFIG as config
import matplotlib
matplotlib.use('Agg')
import os

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt3d
import itertools as itertools


import matplotlib.pyplot as plt 
import POPULATION as pop
import math as math



def dominates(a,b):
    #checks if solution a dominates solution b, i.e. all the objectives are better in A than in B
    Adominates = True
    #### OJOOOOOO Hay un atributo en los dictionarios que no hay que tener en cuenta, el index!!!
    for key in a:
        
        noObjectivesKeys = ["index","total","wspr","wmak","wres"]
        if not (key in noObjectivesKeys):  #por ese motivo está este if.
            if b[key]<=a[key]:
                Adominates = False
                break
    return Adominates     



def calculateDominants(popT):
    
    for i in range(len(popT.population)):
        popT.dominatedBy[i] = set()
        popT.dominatesTo[i] = set()
        popT.fronts[i] = set()

    for p in range(len(popT.population)):
        for q in range(p+1,len(popT.population)):
            if dominates(popT.fitness[p],popT.fitness[q]):
                popT.dominatesTo[p].add(q)
                popT.dominatedBy[q].add(p)
            if dominates(popT.fitness[q],popT.fitness[p]):
                popT.dominatedBy[p].add(q)
                popT.dominatesTo[q].add(p)        

def calculateFronts(popT):

    addedToFronts = set()
    
    i=0
    while len(addedToFronts)<len(popT.population):
        popT.fronts[i] = set([index for index,item in enumerate(popT.dominatedBy) if item==set()])
        addedToFronts = addedToFronts | popT.fronts[i]
        
        for index,item in enumerate(popT.dominatedBy):
            if index in popT.fronts[i]:
                popT.dominatedBy[index].add(-1)
            else:
                popT.dominatedBy[index] = popT.dominatedBy[index] - popT.fronts[i]
        i+=1        
        
def fastNonDominatedSort(popT):
    
    calculateDominants(popT)
    calculateFronts(popT)

def cmetric(A_,B_):
    
    dominated = 0
    for bSol in B_:
        for aSol in A_:
            if dominates(aSol,bSol):
                dominated = dominated +1
                break
    return 100.00*float(dominated)/float(len(B_))
        
def getEucDistNadirUtopia(fitnessList):

    wspr  = list()
    wmak  = list()    
    wres  = list()      
    
    for i in fitnessList:
        wmak.append(i['wmak'])
        wspr.append(i['wspr'])
        wres.append(i['wres'])
        
    Nspr  = max(wspr)
    Nmak  = max(wmak)
    Nres  = max(wres)    
        
    Uspr  = min(wspr)
    Umak  = min(wmak)
    Ures  = min(wres)    
    
    return math.sqrt( ((Nspr - Uspr) ** 2)  +  ((Nmak - Umak) ** 2)  +  ((Nres - Ures) ** 2)  ) 


        
def getParetoVolume(fitnessList):

    wspr  = list()
    wmak  = list()    
    wres  = list()      
    
    for i in fitnessList:
        wmak.append(i['wmak'])
        wspr.append(i['wspr'])
        wres.append(i['wres'])
        
    Nspr  = max(wspr)
    Nmak  = max(wmak)
    Nres  = max(wres)    
        
    Uspr  = min(wspr)
    Umak  = min(wmak)
    Ures  = min(wres)    
    
    return (Nspr - Uspr) * (Nmak - Umak)  *  (Nres - Ures)  



        
def getParetoSurface(fitnessList):

    wspr  = list()
    wmak  = list()    
    
    
    for i in fitnessList:
        wmak.append(i['wmak'])
        wspr.append(i['wspr'])
        
    Nspr  = max(wspr)
    Nmak  = max(wmak)
        
    Uspr  = min(wspr)
    Umak  = min(wmak)
    
    return (Nspr - Uspr) * (Nmak - Umak)





#*****************************************************************#
#
# LECTURA DE DATOS DE ARCHIVOS
#
#*****************************************************************


printBonito = True

gaName = {}

gaName['nsga2']='NSGA-II'
gaName['weightedga']='Weighted GA'
gaName['moead']='MOEA/D'

netName = {}
netName['nxgenerated.100']='100 devices'
netName['nxgenerated.500']='500 devices'
netName['nxgenerated.1000']='1000 devices'


numAppsArray = [5,10,25]
#numAppsArray = [9]

limit =600

networkTopologyArray = ['barabasi100','euclidean100','lobster100']
#networkTopologyArray = ['lobster100']
networkTopologyArray = ['nxgenerated.100']
                        
gatypeArray = ['nsga2','weightedga','moead']
#gatypeArray = ['weightedga','moead','nsga2']
#gatypeArray = ['moead','weightedga']

seriesList = ['total','spread','resources','makespan']
ylabel={}
ylabel['total']='w. sum'
ylabel['spread']='spread\n(CV)'
ylabel['resources']='free res.\n(ratio)'
ylabel['makespan']='net. latency (t)'

#file_path = "./20180410202755"
file_path = "./20181005114137_100"


if not os.path.exists(file_path+'/plots'):
    os.makedirs(file_path+'/plots')
    
cnf = config.CONFIG()
 
generationSolution={}
paretoSolution={}
for networkTopology in networkTopologyArray:
    generationSolution[networkTopology]={}
    paretoSolution[networkTopology]={}
    for numApps in numAppsArray:
        generationSolution[networkTopology][numApps]={}
        paretoSolution[networkTopology][numApps]={}
#        for series in seriesList:
    
#        generationSolution[networkTopology][numApps][series] = {}
        #generationPareto = {}
        
#        mydataserie={}
        
        for gatype in gatypeArray:
            generationSolution[networkTopology][numApps][gatype] = list()
            paretoSolution[networkTopology][numApps][gatype] = list()
            #generationPareto[gatype] = list()


            idString =networkTopology+"."+gatype+"."+str(numApps)+"."
            
            input_ = open(file_path+'/'+idString+'selectedEvolution.pkl', 'rb')
            generationSolution[networkTopology][numApps][gatype]=pickle.load(input_)
            input_.close()
            
            input_ = open(file_path+'/'+idString+'paretoEvolution.pkl', 'rb')
            paretoSolution[networkTopology][numApps][gatype]=pickle.load(input_)
            input_.close()

#                input_ = open(file_path+'/'+idString+'paretoEvolution.pkl', 'rb')
#                generationPareto[gatype]=pickle.load(input_)
#                input_.close()

            
            #generationSolution['nsga2'][500]['fitness']
                
# {'index': 73,
# 'makespan': 9.22832988267771,
# 'resources': 0.0,
# 'spread': 0.6926771989595647,
# 'total': 0.74357739313528315,
# 'wmak': 1.5380549804462849,
# 'wres': 0.0,
# 'wspr': 0.6926771989595647}
#                    
            
            
#*****************************************************************#
#
# GRAFICOS DE LINEAS DE EVOLUCION DE LOS OBJETIVOS
#
#*****************************************************************
            

#networkTopologyArray = ['lobster100','barabasi100','euclidean100']
#numAppsArray = [1,3,5]
seriesList = ['spread','resources','makespan']


line_cycle = itertools.cycle([":","--","-.",])

for networkTopology in networkTopologyArray:
    
    figtitleStr = networkTopology
    
    
    
    font = {'size'   : 12}
    
    matplotlib.rc('font', **font)
    
      
            
    #ejemplo sacado de http://matplotlib.org/users/text_intro.html    
    fig = plt.figure()
       #    fig.suptitle('bold figure suptitle', fontsize=14, fontweight='bold')
    #fig.suptitle(figtitleStr, fontsize=16)
    fig.set_size_inches(12.0, 7.0)
    
    columfigures=3
    
    isplot=0
        
    for series in seriesList:
        for numApps in numAppsArray:
            
            mydataserie={}

            for gatype in gatypeArray:
                
                mydataserie[gatype]=list()
                for i in range(0,len(generationSolution[networkTopology][numApps][gatype])):
                    mydataserie[gatype].append(generationSolution[networkTopology][numApps][gatype][i]['fitness'][series])
    
    
            
            
            ax = fig.add_subplot(3,columfigures,isplot+1)
            fig.subplots_adjust(bottom=0.15)
            plt.grid()
       #    ax.set_title('axes title')

            if isplot==0:
                plt.title(str(numApps*3)+' apps', fontsize=16)
            if isplot==1:
                plt.title(str(numApps*3)+' apps', fontsize=16)
            if isplot==2:
                plt.title(str(numApps*3)+' apps', fontsize=16)
            if isplot==7:
                ax.set_xlabel('Generations', fontsize=16)
            if isplot%columfigures==0:
                ax.set_ylabel(ylabel[series], fontsize=16)
#            plt.gcf().subplots_adjust(left=0.15)
#            plt.gcf().subplots_adjust(right=0.99)
#            plt.gcf().subplots_adjust(bottom=0.2)            
            
            if isplot < 6:
                plt.setp(ax.get_xticklabels(), visible=False)
#            if 'max' in seriesToPlot:
#                ax.plot(mydataSerie['max'], label='max', linewidth=2.5,color='yellow',marker='*',markersize=10,markevery=30)
#            if 'mean' in seriesToPlot:    
#                ax.plot(mydataSerie['mean'], label='mean', linewidth=2.5,color='green',marker='o',markersize=10,markevery=30)
#            if 'min' in seriesToPlot:
#                ax.plot(mydataSerie['min'], label='min', linewidth=2.5,color='red',marker='^',markersize=10,markevery=30)
#            if 'single' in seriesToPlot:
#                ax.plot(mydataSerie['sfit'], label='weighted', linewidth=2.5,color='blue',marker='s',markersize=10,markevery=30)    
#            plt.legend(loc="upper center", ncol=3, fontsize=14) 



            for gatype in gatypeArray:
                ax.plot(mydataserie[gatype][0:limit], label=gaName[gatype], linewidth=2.0,linestyle=line_cycle.next())
                #ax.plot(mydataserie[gatype], label=gatype, linewidth=2.5)
#    
#                if 'max' in seriesToPlot:
#                    
#                if 'mean' in seriesToPlot:    
#                    ax.plot(mydataSerie['mean'][0:250], label='mean', linewidth=2.5,color='green')
#                if 'min' in seriesToPlot:
#                    ax.plot(mydataSerie['min'][0:250], label='min', linewidth=2.5,color='red',linestyle='--')
#                if 'single' in seriesToPlot:
#                    ax.plot(mydataSerie['sfit'][0:250], label='weighted', linewidth=2.5,color='blue')    

            if isplot==1:
                plt.legend(bbox_to_anchor=(0., 1.5, 1., .102),loc="upper center", ncol=3, fontsize=14) 

            isplot=isplot+1




        #upper, arriba    lower, abajo   center, centro    left, izquierda y    right, derecha
            #plt.legend()
       #    plt.show()
       
   #             plt.ylim(ymax=0.5)
       
       

    fig.savefig(file_path+'/plots/evolObj'+networkTopology+'.pdf')
    plt.close(fig)



#*****************************************************************#
#
# GRAFICO DE LOS PARETOS
#
#*****************************************************************


#networkTopologyArray = ['lobster100','barabasi100']
#numAppsArray = [1,2]
seriesList = ['spread','resources','makespan']



for numApps in numAppsArray:
    for networkTopology in networkTopologyArray:
    
        figtitleStr = str(numApps*3)+" app / "+networkTopology
        
        
        
        
        
        
        isplot=0
        mydataserie={}
        
        for gatype in gatypeArray:
            mydataserie[gatype]={}
            for series in seriesList: 
                mydataserie[gatype][series]=list()
                for i in range(0,len(paretoSolution[networkTopology][numApps][gatype]['fitness'])):
                    mydataserie[gatype][series].append(paretoSolution[networkTopology][numApps][gatype]['fitness'][i][series])
        
                    
            
        
        fig = plt.figure()
        fig.suptitle(figtitleStr, fontsize=18)
        fig.set_size_inches(12.0, 7.0)
        
        ax = fig.add_subplot(224, projection='3d')
        #plt.gcf().subplots_adjust(left=0.00)
        
        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
            #### quitarlo para que no sea solo el frente pareto 
            #### while len(popT.fronts[f])!=0:
        #    thisfront = [paretoResults[generationNum].fitness[i] for i in paretoResults[generationNum].fronts[0]]
        
        #a = [thisfront[i]["mttr"] for i,v in enumerate(thisfront)]
        #b = [thisfront[i]["latency"] for i,v in enumerate(thisfront)]
        #c = [thisfront[i]["cost"] for i,v in enumerate(thisfront)]
        
        
        for gatype in gatypeArray:
        
            ax.scatter(mydataserie[gatype]['spread'], mydataserie[gatype]['resources'], mydataserie[gatype]['makespan'], marker="o",alpha=0.4)
        
        ax.set_xlabel(r'$spread$', fontsize=18)
        ax.set_ylabel(r'$free-resources$', fontsize=18)
        ax.set_zlabel(r'$net-latency$', fontsize=18,rotation=90)
        
        
        
        
        
        
        
        ax = fig.add_subplot(222)
        #plt.gcf().subplots_adjust(left=0.00)
        
        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
            #### quitarlo para que no sea solo el frente pareto 
            #### while len(popT.fronts[f])!=0:
        #    thisfront = [paretoResults[generationNum].fitness[i] for i in paretoResults[generationNum].fronts[0]]
        
        #a = [thisfront[i]["mttr"] for i,v in enumerate(thisfront)]
        #b = [thisfront[i]["latency"] for i,v in enumerate(thisfront)]
        #c = [thisfront[i]["cost"] for i,v in enumerate(thisfront)]
        
        
        for gatype in gatypeArray:
        
            ax.scatter( mydataserie[gatype]['spread'], mydataserie[gatype]['makespan'], marker="o",alpha=0.4)
        
        
        ax.set_xlabel(r'$spread$', fontsize=18)
        ax.set_ylabel(r'$net-latency$', fontsize=18,rotation=90)
        plt.legend(bbox_to_anchor=(0., 1.5, 1., .102),loc="upper center", ncol=3, fontsize=14) 
        
        
        
        
        ax = fig.add_subplot(223)
        ax.grid()
        #plt.gcf().subplots_adjust(left=0.00)
        
        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
            #### quitarlo para que no sea solo el frente pareto 
            #### while len(popT.fronts[f])!=0:
        #    thisfront = [paretoResults[generationNum].fitness[i] for i in paretoResults[generationNum].fronts[0]]
        
        #a = [thisfront[i]["mttr"] for i,v in enumerate(thisfront)]
        #b = [thisfront[i]["latency"] for i,v in enumerate(thisfront)]
        #c = [thisfront[i]["cost"] for i,v in enumerate(thisfront)]
        
        
        for gatype in gatypeArray:
        
            ax.scatter( mydataserie[gatype]['resources'], mydataserie[gatype]['spread'], marker="o",alpha=0.4)
        
        
        ax.set_xlabel(r'$free-resources$', fontsize=18)
        ax.set_ylabel(r'$spread$', fontsize=18,rotation=90)
        ax.legend()
        
        
        ax = fig.add_subplot(221)
        #plt.gcf().subplots_adjust(left=0.00)
        
        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
            #### quitarlo para que no sea solo el frente pareto 
            #### while len(popT.fronts[f])!=0:
        #    thisfront = [paretoResults[generationNum].fitness[i] for i in paretoResults[generationNum].fronts[0]]
        
        #a = [thisfront[i]["mttr"] for i,v in enumerate(thisfront)]
        #b = [thisfront[i]["latency"] for i,v in enumerate(thisfront)]
        #c = [thisfront[i]["cost"] for i,v in enumerate(thisfront)]
        
        
        for gatype in gatypeArray:
        
            ax.scatter( mydataserie[gatype]['resources'], mydataserie[gatype]['makespan'], marker="o",alpha=0.4)
        
        
        ax.set_xlabel(r'$free-resources$', fontsize=18)
        ax.set_ylabel(r'$net-latency$', fontsize=18,rotation=90)
        
        
        scatter1_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", marker = 'o',markeredgewidth=1.0)
        scatter2_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", marker = 'o',markeredgecolor='blue',markeredgewidth=1.0)
        scatter3_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", marker = 'o',markeredgewidth=1.0)
#        plt.legend([scatter2_proxy, scatter1_proxy,scatter4_proxy, scatter3_proxy], ['NSGA-II','Weighted GA', 'MOEA/D'], numpoints = 1, fontsize=12,handletextpad=0.1, ncol=3,bbox_to_anchor=(0., 0.5, 0.5, 0.0))
        plt.legend([scatter2_proxy, scatter1_proxy, scatter3_proxy], ['NSGA-II','Weighted GA', 'MOEA/D'], numpoints = 1, fontsize=12,handletextpad=0.1, ncol=3,bbox_to_anchor=(0., 0.5, 0.5, 0.0))
        #plt.legend(bbox_to_anchor=(0., 1.5, 1., .102),) 
        
          
        
        
        fig.savefig(file_path+'/plots/pareto'+str(numApps)+networkTopology+'.pdf')
        plt.close(fig)
        
                        

#*****************************************************************#
#
# GRAFICO DE LOS PARETOS REMARCANDO PARETO FRONT
#
#*****************************************************************

#networkTopologyArray = ['lobster100','barabasi100']
#numAppsArray = [1,2]
seriesList = ['spread','resources','makespan']



for numApps in numAppsArray:
    for networkTopology in networkTopologyArray:
    
        figtitleStr = str(numApps)+" app / "+networkTopology
        
        
        
        
        myPopulation = pop.POPULATION(0)
        
        isplot=0
        mydataserie={}
        
        for gatype in gatypeArray:
            mydataserie[gatype]={}
            tempMyPopulation=pop.POPULATION(len(paretoSolution[networkTopology][numApps][gatype]['population']))
            tempMyPopulation.population = paretoSolution[networkTopology][numApps][gatype]['population']
            tempMyPopulation.fitness = paretoSolution[networkTopology][numApps][gatype]['fitness']
            myPopulation = myPopulation.populationUnion(myPopulation,tempMyPopulation)
            for series in seriesList: 
                mydataserie[gatype][series]=list()
                for i in range(0,len(paretoSolution[networkTopology][numApps][gatype]['fitness'])):
                    mydataserie[gatype][series].append(paretoSolution[networkTopology][numApps][gatype]['fitness'][i][series])
        
        fastNonDominatedSort(myPopulation) 
        mydataserie['pareto']={}
        for series in seriesList: 
            mydataserie['pareto'][series]=list()
            for i in myPopulation.fronts[0]:
                mydataserie['pareto'][series].append(myPopulation.fitness[i][series])
                
            
        print len(myPopulation.fronts[0])
        
        fig = plt.figure()
        #fig.suptitle(figtitleStr, fontsize=18)
        fig.set_size_inches(12.0, 7.0)
        
        ax = fig.add_subplot(224, projection='3d')
        ax.grid(zorder=1)
        #plt.gcf().subplots_adjust(left=0.00)
        
        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
            #### quitarlo para que no sea solo el frente pareto 
            #### while len(popT.fronts[f])!=0:
        #    thisfront = [paretoResults[generationNum].fitness[i] for i in paretoResults[generationNum].fronts[0]]
        
        #a = [thisfront[i]["mttr"] for i,v in enumerate(thisfront)]
        #b = [thisfront[i]["latency"] for i,v in enumerate(thisfront)]
        #c = [thisfront[i]["cost"] for i,v in enumerate(thisfront)]
        
        
        for gatype in gatypeArray:
        
            ax.scatter(mydataserie[gatype]['spread'], mydataserie[gatype]['resources'], mydataserie[gatype]['makespan'], marker="o",alpha=0.2,zorder=10, edgecolors=None)
        ax.scatter(mydataserie['pareto']['spread'], mydataserie['pareto']['resources'], mydataserie['pareto']['makespan'], marker="o",facecolors='black',s=2.0,zorder=10, edgecolors=None)#,facecolors='none', edgecolors='black',linewidths=0.3, alpha=0.1)
            
        
        ax.set_xlabel(r'$spread$', fontsize=12)
        ax.set_ylabel(r'$free-resources$', fontsize=12)
        ax.set_zlabel(r'$net-latency$', fontsize=12,rotation=90)
        
        
        
        
        
        
        
        ax = fig.add_subplot(222)
        ax.grid(zorder=1)
        #plt.gcf().subplots_adjust(left=0.00)
        
        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
            #### quitarlo para que no sea solo el frente pareto 
            #### while len(popT.fronts[f])!=0:
        #    thisfront = [paretoResults[generationNum].fitness[i] for i in paretoResults[generationNum].fronts[0]]
        
        #a = [thisfront[i]["mttr"] for i,v in enumerate(thisfront)]
        #b = [thisfront[i]["latency"] for i,v in enumerate(thisfront)]
        #c = [thisfront[i]["cost"] for i,v in enumerate(thisfront)]
        
       
        for gatype in gatypeArray:
        
            ax.scatter( mydataserie[gatype]['spread'], mydataserie[gatype]['makespan'], marker="o",alpha=0.2,zorder=10, edgecolors=None)

        ax.scatter(mydataserie['pareto']['spread'], mydataserie['pareto']['makespan'], marker="o",facecolors='black',s=2.0,zorder=10, edgecolors=None)#,facecolors='none', edgecolors='black',linewidths=0.3, alpha=0.1)
        
        
        ax.set_xlabel(r'$spread$', fontsize=12)
        ax.set_ylabel(r'$net-latency$', fontsize=12,rotation=90)
        
        
        
        
        ax = fig.add_subplot(223)
        ax.grid(zorder=1)
        #plt.gcf().subplots_adjust(left=0.00)
        
        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
            #### quitarlo para que no sea solo el frente pareto 
            #### while len(popT.fronts[f])!=0:
        #    thisfront = [paretoResults[generationNum].fitness[i] for i in paretoResults[generationNum].fronts[0]]
        
        #a = [thisfront[i]["mttr"] for i,v in enumerate(thisfront)]
        #b = [thisfront[i]["latency"] for i,v in enumerate(thisfront)]
        #c = [thisfront[i]["cost"] for i,v in enumerate(thisfront)]
        
        
        for gatype in gatypeArray:
        
            ax.scatter( mydataserie[gatype]['resources'], mydataserie[gatype]['spread'], marker="o",alpha=0.2,zorder=10, edgecolors=None)
        
        ax.scatter(mydataserie['pareto']['resources'], mydataserie['pareto']['spread'], marker="o",facecolors='black',s=2.0,zorder=10, edgecolors=None)#,edgecolors='black',linewidths=0.3,facecolors='black',s=2.0)#,facecolors='none', edgecolors='black',linewidths=0.3, alpha=0.1)

        
        ax.set_xlabel(r'$free-resources$', fontsize=12)
        ax.set_ylabel(r'$spread$', fontsize=12,rotation=90)
        ax.legend()
        
        
        ax = fig.add_subplot(221)
        ax.grid(zorder=1)
        #plt.gcf().subplots_adjust(left=0.00)
        
        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
            #### quitarlo para que no sea solo el frente pareto 
            #### while len(popT.fronts[f])!=0:
        #    thisfront = [paretoResults[generationNum].fitness[i] for i in paretoResults[generationNum].fronts[0]]
        
        #a = [thisfront[i]["mttr"] for i,v in enumerate(thisfront)]
        #b = [thisfront[i]["latency"] for i,v in enumerate(thisfront)]
        #c = [thisfront[i]["cost"] for i,v in enumerate(thisfront)]
        
        #,facecolors='none', edgecolors='black',linewidths=0.3, alpha=0.1)
        
        for gatype in gatypeArray:
        
            ax.scatter( mydataserie[gatype]['resources'], mydataserie[gatype]['makespan'], marker="o",alpha=0.2,zorder=10, edgecolors=None)
        
        ax.scatter(mydataserie['pareto']['resources'], mydataserie['pareto']['makespan'], marker="o",facecolors='black',s=2.0,zorder=10, edgecolors=None)

        
        ax.set_xlabel(r'$free-resources$', fontsize=12)
        ax.set_ylabel(r'$net-latency$', fontsize=12,rotation=90)
        
        
        scatter1_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", marker = 'o',color='royalblue',markeredgewidth=1.0)
        scatter2_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", marker = 'o',color='orange',markeredgewidth=1.0)
        scatter3_proxy = matplotlib.lines.Line2D([0],[0], linestyle="none", marker = 'o',color='green',markeredgewidth=1.0)
        plt.legend([scatter1_proxy, scatter2_proxy,scatter3_proxy], ['NSGA-II','Weighted GA', 'MOEA/D'], numpoints = 1, fontsize=12,handletextpad=0.1, ncol=3,bbox_to_anchor=(0., 1.3, 1.6, 0.0))
        #plt.legend(bbox_to_anchor=(0., 1.5, 1., .102),) 
        
        
        fig.savefig(file_path+'/plots/paretoMRK'+str(numApps)+networkTopology+'.pdf')
        plt.close(fig)
        
   
            
#*****************************************************************#
#
# GRAFICOS DE LINEAS DE EVOLUCION DE LOS TOTALES
#
#*****************************************************************
            

#networkTopologyArray = ['lobster100','barabasi100','euclidean100']
#numAppsArray = [1,3,5]
seriesList = ['total']

line_cycle = itertools.cycle([":","--","-.",])



figtitleStr = series+" "+str(numApps)+" "+networkTopology



font = {'size'   : 12}

matplotlib.rc('font', **font)

  
        
#ejemplo sacado de http://matplotlib.org/users/text_intro.html    
fig = plt.figure()
   #    fig.suptitle('bold figure suptitle', fontsize=14, fontweight='bold')
#fig.suptitle(figtitleStr, fontsize=16)
fig.set_size_inches(12.0, 7.0)

columfigures=1

isplot=0

    
        
for series in seriesList:
    for numApps in numAppsArray:
        for networkTopology in ['nxgenerated.100']:
            
            mydataserie={}

            for gatype in gatypeArray:
                
                mydataserie[gatype]=list()
                for i in range(0,len(generationSolution[networkTopology][numApps][gatype])):
                    mydataserie[gatype].append(generationSolution[networkTopology][numApps][gatype][i]['fitness'][series])
    
    
            
            
            ax = fig.add_subplot(3,columfigures,isplot+1)
            fig.subplots_adjust(bottom=0.15)
            plt.grid()
       #    ax.set_title('axes title')

            if isplot==0:
                plt.title(netName[networkTopology], fontsize=16)
            if isplot==1:
                plt.title(netName[networkTopology], fontsize=16)
            if isplot==2:
                plt.title(netName[networkTopology], fontsize=16)
            if isplot==7:
                ax.set_xlabel('Generations', fontsize=16)
            if isplot%columfigures==0:
                ax.set_ylabel(str(numApps*3)+' apps\n'+ylabel[series], fontsize=16)
#            plt.gcf().subplots_adjust(left=0.15)
#            plt.gcf().subplots_adjust(right=0.99)
#            plt.gcf().subplots_adjust(bottom=0.2)    
            
#            if printBonito:
#                plt.ylim(ymax=0.8,ymin=0.0)
            
            if isplot < 6:
                plt.setp(ax.get_xticklabels(), visible=False)
#            if 'max' in seriesToPlot:
#                ax.plot(mydataSerie['max'], label='max', linewidth=2.5,color='yellow',marker='*',markersize=10,markevery=30)
#            if 'mean' in seriesToPlot:    
#                ax.plot(mydataSerie['mean'], label='mean', linewidth=2.5,color='green',marker='o',markersize=10,markevery=30)
#            if 'min' in seriesToPlot:
#                ax.plot(mydataSerie['min'], label='min', linewidth=2.5,color='red',marker='^',markersize=10,markevery=30)
#            if 'single' in seriesToPlot:
#                ax.plot(mydataSerie['sfit'], label='weighted', linewidth=2.5,color='blue',marker='s',markersize=10,markevery=30)    
#            plt.legend(loc="upper center", ncol=3, fontsize=14) 



            for gatype in gatypeArray:
                ax.plot(mydataserie[gatype][0:limit], label=gaName[gatype], linewidth=2.0,linestyle=line_cycle.next())
                #ax.plot(mydataserie[gatype], label=gatype, linewidth=2.5)
#    
#                if 'max' in seriesToPlot:
#                    
#                if 'mean' in seriesToPlot:    
#                    ax.plot(mydataSerie['mean'][0:250], label='mean', linewidth=2.5,color='green')
#                if 'min' in seriesToPlot:
#                    ax.plot(mydataSerie['min'][0:250], label='min', linewidth=2.5,color='red',linestyle='--')
#                if 'single' in seriesToPlot:
#                    ax.plot(mydataSerie['sfit'][0:250], label='weighted', linewidth=2.5,color='blue')    

            if isplot==1:
                plt.legend(bbox_to_anchor=(0., 1.5, 1., .102),loc="upper center", ncol=3, fontsize=14) 

            isplot=isplot+1




        #upper, arriba    lower, abajo   center, centro    left, izquierda y    right, derecha
            #plt.legend()
       #    plt.show()
       
                
       
       

fig.savefig(file_path+'/plots/todosTOTAL.pdf')
plt.close(fig)




           
#*****************************************************************#
#
# GRAFICOS PARA TIEMPOS DE EJECUCION
#
#*****************************************************************
            

networkTopologyArray = ['lobster100','barabasi100','euclidean100']
numAppsArray = [5,10,25]
seriesList = ['spread','resources','makespan']


#limit_={}
#
#limit_[5]={}
#limit_[5]['nxgenerated.100']=   0.8
#limit_[5]['barabasi100']=   0.81
#limit_[5]['euclidean100']=   0.82
#
#limit_[10]={}
#limit_[10]['nxgenerated.100']=   1.27
#limit_[10]['barabasi100']=   1.3
#limit_[10]['euclidean100']=   1.32
#
#limit_[25]={}
#limit_[25]['nxgenerated.100']=   1.72
#limit_[25]['barabasi100']=   1.77
#limit_[25]['euclidean100']=    1.82
#    
    
font = {'size'   : 12}

matplotlib.rc('font', **font)

  
        
#ejemplo sacado de http://matplotlib.org/users/text_intro.html    
fig = plt.figure()
   #    fig.suptitle('bold figure suptitle', fontsize=14, fontweight='bold')
#fig.suptitle(figtitleStr, fontsize=16)
fig.set_size_inches(12.0, 7.0)

columfigures=3

isplot=0

import numpy as np
import matplotlib.pyplot as plt 
from scipy import stats
    
for networkTopology in ['nxgenerated.100']:
    for numApps in numAppsArray:
        
        mydataserie={}

        for gatype in gatypeArray:
            
            mydataserie[gatype]=list()
            for i in range(1,len(generationSolution[networkTopology][numApps][gatype])):
                mydataserie[gatype].append(generationSolution[networkTopology][numApps][gatype][i]['executiontime'].total_seconds())
#                if gatype=='moead':
#                    if mydataserie[gatype][i-1] > limit_[numApps][networkTopology]:
#                        mydataserie[gatype][i-1]=mydataserie[gatype][i-2]

        
        
        ax = fig.add_subplot(1,columfigures,isplot+1)
        fig.subplots_adjust(bottom=0.15)
        plt.grid()
   #    ax.set_title('axes title')

        if isplot==0:
            plt.title(str(numApps*3)+' apps', fontsize=16)
        if isplot==1:
            plt.title(str(numApps*3)+' apps', fontsize=16)
        if isplot==2:
            plt.title(str(numApps*3)+' apps', fontsize=16)
        if isplot==7:
            ax.set_xlabel('Generations', fontsize=16)
        if isplot%columfigures==0:
            ax.set_ylabel(netName[networkTopology]+"\n time (s)", fontsize=12)
#        plt.gcf().subplots_adjust(left=0.15)
#        plt.gcf().subplots_adjust(right=0.99)
#        plt.gcf().subplots_adjust(bottom=0.2)            
        
        if isplot < 6:
            plt.setp(ax.get_xticklabels(), visible=False)
#            if 'max' in seriesToPlot:
#                ax.plot(mydataSerie['max'], label='max', linewidth=2.5,color='yellow',marker='*',markersize=10,markevery=30)
#            if 'mean' in seriesToPlot:    
#                ax.plot(mydataSerie['mean'], label='mean', linewidth=2.5,color='green',marker='o',markersize=10,markevery=30)
#            if 'min' in seriesToPlot:
#                ax.plot(mydataSerie['min'], label='min', linewidth=2.5,color='red',marker='^',markersize=10,markevery=30)
#            if 'single' in seriesToPlot:
#                ax.plot(mydataSerie['sfit'], label='weighted', linewidth=2.5,color='blue',marker='s',markersize=10,markevery=30)    
#            plt.legend(loc="upper center", ncol=3, fontsize=14) 




        for gatype in gatypeArray:
            x = np.array(range(0,len(mydataserie[gatype][0:limit])))
            y = np.array(mydataserie[gatype][0:limit])
            
            gradient, intercept, r_value, p_value, std_err = stats.linregress(x,y)
            mn=np.min(x)
            mx=np.max(x)
            x1=np.linspace(mn,mx,500)
            y1=gradient*x1+intercept
            #ax.plot(mydataserie[gatype][0:limit], label=gaName[gatype], linewidth=2.5)
            ax.plot(x1,y1,label=gaName[gatype], linewidth=2.5)
            
            #ax.plot(mydataserie[gatype], label=gatype, linewidth=2.5)
#    
#                if 'max' in seriesToPlot:
#                    
#                if 'mean' in seriesToPlot:    
#                    ax.plot(mydataSerie['mean'][0:250], label='mean', linewidth=2.5,color='green')
#                if 'min' in seriesToPlot:
#                    ax.plot(mydataSerie['min'][0:250], label='min', linewidth=2.5,color='red',linestyle='--')
#                if 'single' in seriesToPlot:
#                    ax.plot(mydataSerie['sfit'][0:250], label='weighted', linewidth=2.5,color='blue')    

        if isplot==1:
            plt.legend(bbox_to_anchor=(0., 1.5, 1., .102),loc="upper center", ncol=3, fontsize=14) 

        isplot=isplot+1




    #upper, arriba    lower, abajo   center, centro    left, izquierda y    right, derecha
        #plt.legend()
   #    plt.show()
   
   #             plt.ylim(ymax=0.5)
   
   

fig.savefig(file_path+'/plots/executionTimes.pdf')
plt.close(fig)


           
#*****************************************************************#
#
# IMPRIMIR DATOS
#
#*****************************************************************






for networkTopology in networkTopologyArray:
    for numApps in numAppsArray:

        for gatype in gatypeArray:
            
            print str(generationSolution[networkTopology][numApps][gatype][399]['fitness']['wmak'])+";"+str(generationSolution[networkTopology][numApps][gatype][399]['fitness']['wres'])+";"+str(generationSolution[networkTopology][numApps][gatype][399]['fitness']['wspr'])+";"+str(generationSolution[networkTopology][numApps][gatype][399]['fitness']['total'])





#tabla de los datos del cmetric

for networkTopology in networkTopologyArray:
    for numApps in numAppsArray:
        
        print netName[networkTopology]+"&"+str(numApps*3)+" & "+str(cmetric(paretoSolution[networkTopology][numApps]['nsga2']['fitness'],paretoSolution[networkTopology][numApps]['moead']['fitness']))+"&"+str(cmetric(paretoSolution[networkTopology][numApps]['moead']['fitness'],paretoSolution[networkTopology][numApps]['nsga2']['fitness']))+"&"+str(cmetric(paretoSolution[networkTopology][numApps]['nsga2']['fitness'],paretoSolution[networkTopology][numApps]['weightedga']['fitness']))+"&"+str(cmetric(paretoSolution[networkTopology][numApps]['weightedga']['fitness'],paretoSolution[networkTopology][numApps]['nsga2']['fitness']))+"&"+str(cmetric(paretoSolution[networkTopology][numApps]['weightedga']['fitness'],paretoSolution[networkTopology][numApps]['moead']['fitness']))+"&"+str(cmetric(paretoSolution[networkTopology][numApps]['moead']['fitness'],paretoSolution[networkTopology][numApps]['weightedga']['fitness']))+"\\\\"



#tabla de los datos de volumen de espacio de direcciones

for networkTopology in networkTopologyArray:
    resultstrnet = netName[networkTopology]
    for numApps in numAppsArray:
        resultstr = resultstrnet+"&" + str(numApps*3)+ " "
        for gatype in gatypeArray:
            
            #distEuc = getEucDistNadirUtopia(paretoSolution[networkTopology][numApps][gatype]['fitness'])
            resultstr=resultstr+"&"+str(round(getParetoVolume(paretoSolution[networkTopology][numApps][gatype]['fitness']),4))

        print resultstr+"\\\\"



####Tabla de los datos de superficie de spread y makespan

for networkTopology in networkTopologyArray:
    resultstrnet = netName[networkTopology]
    for numApps in numAppsArray:
        resultstr = resultstrnet+"&" + str(numApps*3)+ " "
        for gatype in gatypeArray:
            
            #distEuc = getEucDistNadirUtopia(paretoSolution[networkTopology][numApps][gatype]['fitness'])
            resultstr=resultstr+"&"+str(round(getParetoSurface(paretoSolution[networkTopology][numApps][gatype]['fitness']),4))

        print resultstr+"\\\\"