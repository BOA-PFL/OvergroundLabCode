# -*- coding: utf-8 -*-
"""
Created on Mon May 17 14:48:59 2021

@author: kate.harrison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define constants and options
fThresh = 80 #below this value will be set to 0.

# Read in balance file
fPath = 'C:/Users/kate.harrison/Boa Technology Inc/PFL - Documents/General/AgilityPerformanceData/BOA_DualPanel_Sept2021/Overground/'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]


# list of functions 
# finding landings on the force plate once the filtered force exceeds the force threshold
def findLandings(force):
    lic = []
    for step in range(len(force)-1):
        if force[step] == 0 and force[step + 1] >= fThresh:
            lic.append(step)
    return lic

#Find takeoff from FP when force goes from above thresh to 0
def findTakeoffs(force):
    lto = []
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0:
            lto.append(step + 1)
    return lto



def delimitTrialSkate(inputDF):
    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    ax.plot(ZForce, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)

def delimitTrialCMJ(inputDF):
    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    ax.plot(ZForce, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)

CT = []
impulse = []

subName = []
config = []
movements = []


## save configuration names from files
for fName in entries:
    try:
        
        #fName = entries[0]
        
        config1 = fName.split('_')[2]
        tmpMove = fName.split('_')[3].split(' ')[0]
        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        #dat = dat.fillna(0)
        
        if (tmpMove == 'Skater') or (tmpMove == 'skater'):
            
            # create vector of force from vertical signal from each file and make low values 0
            if np.max(abs(dat.FP3_Z)) > np.max(abs(dat.FP4_Z)):
                ZForce = dat.FP3_Z *-1
                XForce = dat.FP3_Y
                
            else:
                ZForce = dat.FP4_Z * -1
                XForce = dat.FP4_Y 
                
            if abs(np.min(XForce)) > abs(np.max(XForce)):
                XForce = XForce * -1
                         
            ZForce[ZForce<fThresh] = 0
            
            dat = delimitTrialSkate(dat)
            #find the landings from function above
            landings = findLandings(ZForce)
            takeoffs = findTakeoffs(ZForce)
        
        elif (tmpMove == 'CMJ') or (tmpMove == 'cmj'):
            
            
            
            ZForce = dat.FP2_Z * -1
            ZForce[ZForce<fThresh] = 0
            
            XForce = ZForce #This is out of convenience to calculate impulse below even though this is not the Y force
            
            dat = delimitTrialCMJ(dat)
            
            landings = findLandings(ZForce)
            takeoffs = findTakeoffs(ZForce)
            
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]]
            
        else:
            print('this movement is not included in Performance Test Analysis')
        
        
        for countVar, landing in enumerate(landings):
            try:
                
                
                CT.append(takeoffs[countVar] - landing)
                impulse.append(np.sum(XForce[landing:takeoffs[countVar]]) )

                subName.append(fName.split('_')[0])
                config.append( config1 )
                movements.append( tmpMove )
                
                
            except:
                print(landing)
    except:
        print(fName)


outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Movement':list(movements),
                         'CT':list(CT), 'impulse':list(impulse) })

outfileName = fPath + 'CompiledAgilityData.csv'
outcomes.to_csv(outfileName, index = False)





