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



def delimitTrialSkate(inputDF, zForce):
    """
     This function uses ginput to delimit the start and end of a trial
    You will need to indicate on the plot when to start/end the trial. 
    You must use tkinter or plotting outside the console to use this function
    Parameters
    ----------
    inputDF : Pandas DataFrame
        DF containing all desired output variables.
    zForce : numpy array 
        of force data from which we will subset the dataframe

    Returns
    -------
    outputDat: dataframe subset to the beginning and end of jumps.

    """
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
    """
     This function uses ginput to delimit the start and end of a trial
    You will need to indicate on the plot when to start/end the trial. 
    You must use tkinter or plotting outside the console to use this function
    Parameters
    ----------
    inputDF : Pandas DataFrame
        DF containing all desired output variables.
    zForce : numpy array 
        of force data from which we will subset the dataframe

    Returns
    -------
    outputDat: dataframe subset to the beginning and end of jumps.

    """
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
            if np.max(abs(dat.FP3_GRF_Z)) > np.max(abs(dat.FP4_GRF_Z)):
                ZForce = dat.FP3_GRF_Z*1
                YForce = dat.FP3_GRF_Y
                
            else:
                ZForce = dat.FP4_GRF_Z *1
                YForce = dat.FP4_GRF_Y 
                
            if abs(np.min(YForce)) > abs(np.max(YForce)): 
                
                YForce = YForce * 1
            ZForce = dat.FP4_GRF_Z *1  
            ZForce[ZForce<fThresh] = 0
            
            # dat = delimitTrialSkate(dat, ZForce)
            #find the landings from function above
            landings = findLandings(ZForce, fThresh)
            takeoffs = findTakeoffs(ZForce, fThresh)
        
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]] 

        
        elif (tmpMove == 'CMJ') or (tmpMove == 'cmj'):
            
            
            # dat = delimitTrialCMJ(dat)
            
            ZForce = dat.FP2_GRF_Z *1 
            ZForce[ZForce<fThresh] = 0
            
            YForce = ZForce  #This is out of convenience to calculate impulse below even though this is not the Y force
            
            XForce = dat.FP2_GRF_X *1 
            
            
            landings = findLandings(ZForce, fThresh )
            takeoffs = findTakeoffs(ZForce, fThresh)
            
            
            # landings = trimLandings(landings, takeoffs)
            # takeoffs = trimTakeoffs(landings, takeoffs)
            
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





