

# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 13:55:28 2020

@author: Daniel.Feeney
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.signal as sig
import seaborn as sns 


# Define constants and options
fThresh = 40; #below this value will be set to 0.
writeData = 0; #will write to spreadsheet if 1 entered

# Read in balance file
fPath = 'C:\\Users\\daniel.feeney\\Boa Technology Inc\\PFL Team - General\\Testing Segments\\WorkWear_Performance\\Elten_Jan2022\\Overground\\Export_V1_ Used for report\\'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]


#entries = os.listdir(fPath)

# list of functions 
# finding landings on the force plate once the filtered force exceeds the force threshold
def findLandings(force):
    """
    
    
    Parameters
    ----------
    force : Pandas Series
        Vertical force from force plate.

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


# def trimLandings(landings, takeoffs):
    """
    
    Parameters
    ----------
    landings : Series
        Indices of ground contact obtained from findLandings function
    takeoffs: Series
        Indices of takeoffs from findTakeoffs function

    Returns
    -------
    trimTakeoffs : list
        Indices of takeoffs excluding any potential takeoffs before 1st
        landing
    
    """
#     trimTakeoffs = landings
#     if len(takeoffs) > len(landings) and takeoffs[0] > landings[0]:
#         del(trimTakeoffs[0])
#     return(trimTakeoffs)

def findTakeoffs(force):
    """
    

    Parameters
    ----------
    force : Pandas Series
        vertical force from force plate.

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

## Preallocation
stabilization = []
sdFz = []
# ankleWork = []
# kneeWork = []
# hipWork = []
subName = []
movements = []
tmpConfig = []

LankleABDMom = []
LankleADDMom = []

LkneeABDMom = []
LkneeADDMom = []


for fName in entries:
    try:
        """
        loop through the selected files and obtain values for stabilization time
        Start by looping through files and getting meta data
        Then loop through landings on the force plate for stabilization time
        """
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        
        ##Parse file name into subject and configuration 
        config = fName.split(sep = "_")[2]
        tmpMove = fName.split(sep = "_")[1] 
        movement = tmpMove.split(sep= ' _ ')[0]
        # Filter force
        forceZ = dat.FP1_Z 
        forceZ[forceZ<fThresh] = 0 
        
        ## find the landings and offs of the FP as vectors
        landings = findLandings(forceZ)
        #takeoffs = findTakeoffs(forceZ) 
        
        # landings = trimLandings(landings, takeoffs)
        # takeoffs = trimTakeoffs(landings, takeoffs)
        
        ## For each landing, calculate rolling averages and time to stabilize
        
        for landing in landings:
            try:
                
                sdFz.append(np.std(forceZ[landing + 100 : landing + 400]))
                avgF = movAvgForce(forceZ, landing, landing + 200, 10)
                sdF = movSDForce(forceZ, landing, landing + 200, 10)
                subBW = findBW(avgF)
                
                try:
                    stabilization.append(findStabilization(avgF, sdF))
                    
                except:
                    stabilization.append('NaN')
                #tmpStab = findStabilization(avgF, sdF)
                movements.append(movement)
                subName.append(fName.split(sep = "_")[0])
                tmpConfig.append(config)
                ###   ---- Work ---- ##
                # ankleWork.append(sum(abs(dat.LeftAnklePower[landing : landing + tmpStab])))
                # kneeWork.append(sum(abs(dat.LeftKneePower[landing : landing + tmpStab])))
                #hipWork.append(sum(abs(dat.LHipPower[landing : landing + tmpStab])))
               
                ###   ---- Pk Moments ---- ##
                
                LankleADDMom.append(max(dat.LAnkleMoment_Frontal[landing : landing + 200]))
                LankleABDMom.append(min(dat.LAnkleMoment_Frontal[landing : landing + 200]))
               
                LkneeABDMom.append(min(dat.LKneeMoment_Frontal[landing : landing + 200]))
                LkneeADDMom.append(max(dat.LKneeMoment_Frontal[landing : landing + 200]))
                
               
               
                
                
            except:
                print(landing, fName)
           

    except:
            print(fName)

# x = np.linspace(landing,landing)
# avgLKneeAddMom = np.mean(LkneeADDMom, axis = 0)
# sdLKneeAddMom = np.std(LkneeADDMom, axis = 0)
# #Plot force
# plt.plot(x, avgLKneeAddMom, 'k', color='#CC4F1B')
# plt.xlabel('Time')
# plt.ylabel('AvgLKneeAddMom Nm')
# plt.title('Avg Knee ADD Mome')
# plt.fill_between(x, avgF-sdF, avgF+sdF,
#      alpha=0.5, edgecolor='#CC4F1B', facecolor='#FF9848')
    
#Average Tibial force
# avgTib = np.mean(preTib,axis=0)
# sdTib = np.std(preTib, axis = 0)
# #Plot average Tibial force 
# plt.plot(x, avgTib, 'k', color='#CC4F1B')
# plt.title('Ensemble average tibial force')
# plt.fill_between(x, avgTib-sdTib, avgTib+sdTib,
#     alpha=0.5, edgecolor='#CC4F1B', facecolor='#FF9848')
    



outcomes = pd.DataFrame({'Sub':list(subName), 'Config': list(tmpConfig),'Movement':list(movements), 'StabTime': list(stabilization), 'sdFz':list(sdFz),
                          'LankleABDMom':list(LankleABDMom), 'LankleADDMom':list(LankleADDMom),  'LkneeADDMom': list(LkneeADDMom), 
                          'LkneeABDMom':list(LkneeABDMom)})


outcomes.to_csv("C:/Users/bethany.kilpatrick/Boa Technology Inc/PFL - General/WorkWear_Performance/Elten_Jan2022/Overground/CompiledOvergroundData.csv"
                      ,mode='a',header=True) 
