# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 15:53:52 2021

@author: Kate.Harrison
"""

######COP analysis

# packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


fPath = 'C:/Users/kate.harrison/Dropbox (Boa)/GolfPerformance/AdiHammer_Feb2020/adiHammer_Performance_Feb2020/Data/'
fileExt = r"COP_COM.txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]


Subject = []
Config = []
targetMax = []
backMax = []
targetBack_range = []
toeMax = []
heelMax = []
toeHeel_range = []

for fName in entries:

    try:

        subName = fName.split(sep = "_")[0]
        ConfigTmp = fName.split(sep="_")[1]

        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 9, header = 0)


        # Name vectors

        dat.columns = ['Sample','COM_X', 'COM_Y', 'COP_X_3', 'COP_X_4', 'COP_Y_3', 'COP_Y_4', 'GRF_BackFoot', 'GRF_FrontFoot', 'blank'
               ]



        # 2. Find midpoint of COPx (anterior-posterioe) by weighting resultant forces. 

        GRF_Tot = (dat.GRF_FrontFoot + dat.GRF_BackFoot)*-1

        bc = np.argmax(GRF_Tot)

        start = bc - 100

        finish = bc
        # Find GRF peak and 2ms before and after to ID period of interest

        GRF_prop = dat.GRF_FrontFoot/GRF_Tot
        # 3. Find midpoint of COPy

        copY = dat.COP_Y_4 + (dat.COP_Y_3 - dat.COP_Y_4)*GRF_prop

        copX = dat.COP_X_4 - (dat.COP_X_4 - dat.COP_X_3)*GRF_prop


        # center COP on start location

        copY_cent = copY - copY[start]
        copX_cent = copX - copX[start]
        # 4. Plot COPx vs COPy for all repetitions (shows consistecy of path as well as differences in shape between shoes)
        
        if ConfigTmp == 'Lace':
            plt.plot(copX_cent[start:finish+1], copY_cent[start:finish+1], 'k')
            plt.plot(copX_cent[finish], copY_cent[finish], 'ko')
        elif ConfigTmp == 'Hammer':
            plt.plot(copX_cent[start:finish+1], copY_cent[start:finish+1], 'g')
            plt.plot(copX_cent[finish], copY_cent[finish], 'go')
        

        #5. Calculate variables
        Subject.append(subName)
        Config.append(ConfigTmp)
        toeMax.append(max(copY_cent[start:finish+1]))
        heelMax.append(min(copY_cent[start:finish+1]))
        toeHeel_range.append(toeMax[-1] - heelMax[-1])
        targetMax.append(max(copX_cent[start:finish+1]))
        backMax.append(min(copX_cent[start:finish+1]))
        targetBack_range.append(targetMax[-1] - backMax[-1])
        
    except:
        print(fName)
    
    
outcomes = pd.DataFrame({'SubjectName':list(Subject),'Shoe':list(Config), 'toeMax':list(toeMax), 'heelMax':list(heelMax), 'toeHeel_range':list(toeHeel_range),
                         'targetMax':list(targetMax), 'backMax':list(backMax), 'targetBack_range':list(targetBack_range)
                                         })

outcomes.to_csv("C:/Users/kate.harrison/Dropbox (Boa)/GolfPerformance/AdiHammer_Feb2020/adiHammer_Performance_Feb2020/Data/CompiledCOP100msData.csv", index = False)
