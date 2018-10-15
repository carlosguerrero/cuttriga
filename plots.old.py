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

import matplotlib.pyplot as plt 

numAppsArray = [1,3,5]
#numAppsArray = [9]

limit =400

networkTopologyArray = ['lobster100','barabasi100','euclidean100']
#networkTopologyArray = ['lobster100']
                        
gatypeArray = ['nsga2','weightedga','moead']
#gatypeArray = ['nsga2','weightedga']

seriesList = ['total','spread','resources','makespan']
ylabel={}
ylabel['total']='weighted sum'
ylabel['spread']='CV'
ylabel['resources']='ratio'
ylabel['makespan']='t'

file_path = "./20180410202755"


if not os.path.exists(file_path+'/plots'):
    os.makedirs(file_path+'/plots')
    
cnf = config.CONFIG()

 

for networkTopology in networkTopologyArray:
        for numApps in numAppsArray:
            for series in seriesList:
        
                generationSolution = {}
                generationPareto = {}
                
                mydataserie={}
                
                for gatype in gatypeArray:
                    generationSolution[gatype] = list()
                    generationPareto[gatype] = list()
    
    
                    idString =networkTopology+"."+gatype+"."+str(numApps)+"."
                    input_ = open(file_path+'/'+idString+'selectedEvolution.pkl', 'rb')
                    generationSolution[gatype]=pickle.load(input_)
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
                    
                    mydataserie[gatype]=list()
                    for i in range(0,len(generationSolution[gatype])):
                        mydataserie[gatype].append(generationSolution[gatype][i]['fitness'][series])
    
    
                figtitleStr = series+" "+str(numApps)+" "+networkTopology

                
    
                font = {'size'   : 16}
        
                matplotlib.rc('font', **font)
                
              
                        
                #ejemplo sacado de http://matplotlib.org/users/text_intro.html    
                fig = plt.figure()
           #    fig.suptitle('bold figure suptitle', fontsize=14, fontweight='bold')
                fig.suptitle(figtitleStr, fontsize=16)
                
                fig.set_size_inches(9.0, 3.0)
                
                ax = fig.add_subplot(111)
                fig.subplots_adjust(bottom=0.15)
           #    ax.set_title('axes title')
                ax.set_xlabel('Generations', fontsize=16)
                ax.set_ylabel(ylabel[series], fontsize=16)
                plt.gcf().subplots_adjust(left=0.15)
                plt.gcf().subplots_adjust(right=0.99)
                plt.gcf().subplots_adjust(bottom=0.2)            
                
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
                    ax.plot(mydataserie[gatype][0:limit], label=gatype, linewidth=2.5)
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
                plt.legend(loc="upper center", ncol=3, fontsize=14) 
    
    
    
    
            #upper, arriba    lower, abajo   center, centro    left, izquierda y    right, derecha
                #plt.legend()
           #    plt.show()
           
   #             plt.ylim(ymax=0.5)
           
           
                plt.grid()
                fig.savefig(file_path+'/plots/'+series+"-"+str(numApps)+"-"+networkTopology+'.pdf')
                plt.close(fig)
    
    



                
                
