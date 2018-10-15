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

import subprocess



#numAppsArray = [1,2,3]
#numAppsArray = [3]
numAppsArray = [5,10,25]


#networkTopologyArray = ['scenario/lobster100.graphml','scenario/barabasi100.graphml','scenario/euclidean100.graphml']
networkTopologyArray = ['nxgenerated.100','nxgenerated.500','nxgenerated.1000']
#networkTopologyArray = ['scenario/euclidean100.graphml']
                        
gatypeArray = ['nsga2','weightedga','moead']
#gatypeArray = ['nsga2']
#gatypeArray = ['weightedga']
#gatypeArray = ['moead']


executionId= datetime.now().strftime('%Y%m%d%H%M%S')
file_path = "./"+executionId
    
    
for networkTopology in networkTopologyArray:
    for numApps in numAppsArray:
    
        networkTopologyStr = networkTopology[networkTopology.find("/")+1:networkTopology.find(".")]
        for gatype in gatypeArray:
        
            subprocess.call(['python', 'CLcallMainGA.py' , str(numApps), networkTopology, gatype, executionId])
            #print subprocess.check_output(['ls'])
            
