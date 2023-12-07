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
fPath = 'Z:\\Testing Segments\\PowerPerformance\\2021\\Ecco_Nov2021\\KineticsKinematics\\Balance\\'
entries = os.listdir(fPath)

# list of functions 
def findLandings(force, fThresh):
    """
    This function finds the landings from force plate data
    it uses a heuristic to determine landings from when the smoothed force is
    0 and then breaches a threshold
    
    Parameters
    ----------
    force : Pandas Series
        Vertical force from force plate.
    fThresh: integer
        Value force has to be greater than to count as a takeoff/landing

    Returns
    -------
    lic : list
        Indices of landings.

    """
    lic = [] 
    
    for step in range(len(force)-1):
        if len(lic) == 0: 
            
            if force[step] == 0 and force[step + 1] >= fThresh and force [step + 10 ] > 300:
                lic.append(step)
    
        else:
        
            if force[step] == 0 and force[step + 1] >= fThresh and step > lic[-1] + 300 and force [step + 10] > 300:
                lic.append(step)
    return lic



def findTakeoffs(force, fThresh):
    """
    This function calculates the takeoffs using a heuristic 

    Parameters
    ----------
    force : Pandas Series
        vertical force from force plate.
    
    fThresh: integer
        Value force has to be greater than to count as a takeoff/landing
    Returns
    -------
    lto : list
        indices of takeoffs obtained from force data. Takeoffs here mean
        the moment a force signal was > a threshold and then goes to 0

    """
    lto = []
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0 and force[step + 5] == 0 and force[step + 10] == 0:
            lto.append(step + 1)
    return lto

# def trimTakeoffs(landing, takeoff):
#     if landing[0] > takeoff[0]:
#         takeoff.pop(0)
#         return(takeoff)
#     else:
#         return(takeoff)


#Moving average of length specified in function
def movAvgForce(force, landing, takeoff, length):
    """
    In order to estimate when someone stabilized, we calcualted the moving
    average force and SD of the force signal. This is one of many published 
    methods to calcualte when someone is stationary. 
    
    Parameters
    ----------
    force : Pandas series
        pandas series of force from force plate.
    landing : List
        list of landings calcualted from findLandings.
    takeoff : List
        list of takeoffs from findTakeoffs.
    length : Integer
        length of time in indices to calculate the moving average.

    Returns
    -------
    avgF : list
        smoothed average force .

    """
    newForce = np.array(force)
    win_len = length; #window length for steady standing
    avgF = []
    for i in range(landing, takeoff):
        avgF.append(np.mean(newForce[i : i + win_len]))     
    return avgF

#moving SD as calcualted above
def movSDForce(force, landing, takeoff, length):
    """
    This function calculates a rolling standard deviation over an input
    window length
    
    Parameters
    ----------
    force : Pandas series
        pandas series of force from force plate.
    landing : List
        list of landings calcualted from findLandings.
    takeoff : List
        list of takeoffs from findTakeoffs.
    length : Integer
        length of time in indices to calculate the moving average.

    Returns
    -------
    avgF : list
        smoothed rolling SD of forces

    """
    newForce = np.array(force)
    win_len = length; #window length for steady standing
    avgF = []
    for i in range(landing, takeoff):
        avgF.append(np.std(newForce[i : i + win_len]))     
    return avgF

#estimated stability after 200 indices
def findBW(force):
    """
    If you do not have the subject's body weight or want to find from the 
    steady portion of force, this may be used. This is highly conditional on 
    the data and how it was collected. The below assumes quiet standing from
    100 to 200 indices. 
    
    Parameters
    ----------
    force : Pandas series
        DESCRIPTION.

    Returns
    -------
    BW : floating point number
        estimate of body weight of the subject to find stabilized weight
        in Newtons

    """
    BW = np.mean(avgF[100:200])
    return BW

def findStabilization(avgF, sdF):
    """
    Using the rolling average and SD values, this calcualtes when the 
    actual stabilized force occurs. 
    
    Parameters
    ----------
    avgF : list, calculated using movAvgForce 
        rolling average of force.
    sdF : list, calcualted using movSDForce above
        rolling SD of force.

    Returns
    -------
    floating point number
        Time to stabilize using the heuristic: force is within +/- 5% of subject
        mass and the rolling standrd deviation is below 20

    """
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
