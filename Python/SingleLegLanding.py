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
fPath = 'C:/Users/Daniel.Feeney/Dropbox (Boa)/EnduranceProtocolWork/BalanceData/'
entries = os.listdir(fPath)

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
stabilization = []
ankleWork = []
kneeWork = []
hipWork = []
sName = []
tmpConfig = []
## loop through the selected files
for file in entries:
    try:
        
        fName = file #Load one file at a time
        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        #Parse file name into subject and configuration 
        subName = fName.split(sep = "_")[0]
        config = fName.split(sep = "_")[2]
        
        # Filter force
        forceZ = dat.FP3Z * -1
        forceZ[forceZ<fThresh] = 0
        #find the landings and offs of the FP as vectors
        landings = findLandings(forceZ)
            
        #For each landing, calculate rolling averages and time to stabilize
    
        for landing in range(len(landings)):
            try:
                sName.append(subName)
                tmpConfig.append(config)
                avgF = movAvgForce(forceZ, landings[landing], landings[landing]+200, 10)
                sdF = movSDForce(forceZ, landings[landing], landings[landing]+200, 10)
                subBW = findBW(avgF)
                stabilization.append(findStabilization(avgF, sdF))
                ankleWork.append(sum(abs(dat.RAnklePower[landings[landing]:landings[landing] + stabilization[landing]])))
                kneeWork.append(sum(abs(dat.RKneePower[landings[landing]:landings[landing] + stabilization[landing]])))
                hipWork.append(sum(abs(dat.RHipPower[landings[landing]:landings[landing] + stabilization[landing]])))
            except:
                print(landing)
        
    except:
            print(file)

outcomes = pd.DataFrame({'Sub':list(sName), 'Config': list(tmpConfig), 'StabTime': list(stabilization),
                         'ankleWork': list(ankleWork), 'kneeWork': list(kneeWork),'hipWork': list(hipWork)})
    
    
