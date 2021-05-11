# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 13:55:28 2020

@author: Daniel.Feeney
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define constants and options
fThresh = 100; #below this value will be set to 0.
writeData = 0; #will write to spreadsheet if 1 entered

# Read in balance file
fPath = 'C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\Hike Work Research\\Work Pilot 2021\\SLL\\'
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

def trimLandings(landings, takeoffs):
    trimTakeoffs = landings
    if len(takeoffs) > len(landings) and takeoffs[0] > landings[0]:
        del(trimTakeoffs[0])
    return(trimTakeoffs)

#Moving average of length specified in function
def movAvgForce(force, landing, takeoff, length):
    newForce = np.array(force)
    win_len = length; #window length for steady standing
    avgF = []
    for i in range(landing, takeoff):
        avgF.append(np.mean(newForce[i : i + win_len]))     
    return avgF

#moving SD as calcualted above
def movSDForce(force, landing, takeoff, length):
    newForce = np.array(force)
    win_len = length; #window length for steady standing
    avgF = []
    for i in range(landing, takeoff):
        avgF.append(np.std(newForce[i : i + win_len]))     
    return avgF

def findStabilization(avgF, sdF):
    stab = []
    for step in range(len(avgF)-1):
        if avgF[step] >= (subBW - 0.05*subBW) and avgF[step] <= (subBW + 0.05*subBW) and sdF[step] < 20:
            stab.append(step + 1)
    return stab[0]

     
#Preallocation
stabilization = []
pkForce = []
sName = []
movements = []
tmpConfig = []

## loop through the selected files
for file in entries:
    try:
        
        fName = file #Load one file at a time
        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        #Parse file name into subject and configuration 
        subName = fName.split(sep = "_")[0]
        config = fName.split(sep = "_")[2]
        config = config.split(" " )[0]
        movement = fName.split("_")[1]
        
        # Filter force
        forceZ = dat.FP4_ForceZ * -1
        forceZ[forceZ<fThresh] = 0
        
        fig, ax = plt.subplots()
        ax.plot(forceZ, label = 'Vertical Force')
        fig.legend()
        print('Select steady portion of force where subject is mostly still')
        pts = np.asarray(plt.ginput(2, timeout=-1))
        plt.close()

        subBW = np.mean(forceZ[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0]))])

        
        #find the landings and offs of the FP as vectors
        landings = findLandings(forceZ)
        
        #For each landing, calculate rolling averages and time to stabilize
        
        for landing in landings:
            try:
                sName.append(subName)
                tmpConfig.append(config)
                movements.append(movement)
                avgF = movAvgForce(forceZ, landing, landing+200, 10)
                sdF = movSDForce(forceZ, landing, landing+200, 10)
                subBW = subBW
                stabilization.append(findStabilization(avgF, sdF))
                tmpStab = findStabilization(avgF, sdF)
                pkForce.append(np.max(forceZ[landing:landing+200]))
            except:
                print(landing)
            
    except:
            print(file)

outcomes = pd.DataFrame({'Sub':list(sName), 'Config': list(tmpConfig),'Movement':list(movements),
                         'StabTime': list(stabilization), 'pkForce':list(pkForce)})

outcomes.to_csv("C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\Hike Work Research\\Work Pilot 2021/SLLForces.csv",mode='a',header=False)

# List comprehension is written below & probably faster but not necessary for this code #
#        avgF2 = [movAvgForce(forceZ, landing, landing+100, 10) for landing in landings]
#        sdF2 = [movSDForce(forceZ, landing, landing+100, 10) for landing in landings]
#        subBW2 = [findBW(avgF2) for forceTrace in avgF2]
#        ankleSagMom2 = [np.max(dat.RightAnkleMomentSagittal[landing : landing + 50]) for landing in landings] 