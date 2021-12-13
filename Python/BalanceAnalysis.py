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
fPath = 'C:/Users/kate.harrison/Boa Technology Inc/PFL - Documents/General/PowerPerformance/Ecco_Nov2021/KineticsKinematics/Balance/'
entries = os.listdir(fPath)

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

def trimLandings(landings, takeoffs):
    trimTakeoffs = landings
    if len(takeoffs) > len(landings) and takeoffs[0] > landings[0]:
        del(trimTakeoffs[0])
    return(trimTakeoffs)

def trimTakeoffs(landings, takeoffs):
    if len(takeoffs) < len(landings):
        del(landings[-1])
    return(landings)

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


#estimated stability after 200 indices
def findBW(force):
    BW = np.mean(avgF[200:300])
    return BW

def findStabilization(avgF, sdF):
    stab = []
    for step in range(len(avgF)-1):
        if avgF[step] >= (subBW - 0.05*subBW) and avgF[step] <= (subBW + 0.05*subBW) and sdF[step] < 20:
            stab.append(step + 1)
    return stab[0]

#Preallocation
#stabilization = []
sdFz = []
#ankleWork = []
#kneeWork = []
#hipWork = []
sName = []
tmpConfig = []
## loop through the selected files
for file in entries:
    try:
        
        #file = entries[0]
        
        dat = pd.read_csv(fPath+file,sep='\t', skiprows = 8, header = 0)
        #Parse file name into subject and configuration 
        subName = file.split(sep = "_")[0]
        config = file.split(sep = "_")[1]
        
        # Filter force
        forceZ = (dat.FP3_Z + dat.FP4_Z + dat.FP2_Z + dat.FP1_Z) * -1
        forceZ[forceZ<fThresh] = 0
        #find the landings and offs of the FP as vectors
        # landings = findLandings(forceZ)
        # takeoffs = findTakeoffs(forceZ)
        # landings[:] = [x for x in landings if x < takeoffs[-1]]
        # takeoffs[:] = [x for x in takeoffs if x > landings[0]]
        #For each landing, calculate rolling averages and time to stabilize
    
        landings = [5, 10, 15, 20]
        takeoffs = [10, 15, 20, 25]
        for landing in range(len(landings)):
            try:
                #landing = 0
                avgF = movAvgForce(forceZ, landings[landing], takeoffs[landing], 10)
                sdF = movSDForce(forceZ, landings[landing], takeoffs[landing], 10)
                subBW = findBW(avgF)
                
                #stabilization.append(findStabilization(avgF, sdF))
                sdFz.append(np.std(forceZ[landings[landing] +100 : landings[landing] +400]))
                #ankleWork.append(sum(abs(dat.LeftAnklePower[landings[landing]:landings[landing] + stabilization[landing]])))
                #kneeWork.append(sum(abs(dat.LeftKneePower[landings[landing]:landings[landing] + stabilization[landing]])))
                #hipWork.append(sum(abs(dat.LeftHipPower[landings[landing]:landings[landing] + stabilization[landing]])))
                
                sName.append(subName)
                tmpConfig.append(config)
                
            except:
                print(file, landing)
        
    except:
            print(file)

outcomes = pd.DataFrame({'Subject':list(sName), 'Config': list(tmpConfig), 'steadiness':list(sdFz)
                         })
    
outFileName = fPath + 'CompiledBalanceData.csv'
outcomes.to_csv(outFileName, index = False)