# -*- coding: utf-8 -*-
"""
Created on Mon May 17 14:48:59 2021

@author: Daniel.Feeney
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define constants and options
fThresh = 80 #below this value will be set to 0.
stepLen = 50

# Read in balance file
fPath = 'C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\AgilityPerformance\\BOA_Basketball_Mar2021\\ForceData\\'
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

# preallocate matrix for force and fill in with force data
def forceMatrix(inputForce, landings, noSteps, stepLength):
    #input a force signal, return matrix with n rows (for each landing) by m col
    #for each point in stepLen
    preForce = np.zeros((noSteps,stepLength))
    
    for iterVar, landing in enumerate(landings):
        try:
            preForce[iterVar,] = inputForce[landing:landing+stepLength]
        except:
            print(landing)
            
    return preForce

def delimitTrialSkate(inputDF):
    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    ax.plot(inputDF.FP3_RForceZ, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)

def delimitTrialCMJ(inputDF):
    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    ax.plot(inputDF.FP2_ForceZ2, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)

CT = []
impulse = []
RFDcon = []
COPexcursion = []
COPtraj = []
timingDiff = []
subName = []
config = []
movements = []
## save configuration names from files
for file in entries:
    try:
        fName = file #Load one file at a time
        config1 = fName.split('_')[2].split(' - ')[0]
        tmpMove = fName.split('_')[3].split(' - ')[0]
        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        #dat = dat.fillna(0)
        
        if (tmpMove == 'Skater') or (tmpMove == 'skater'):
            dat = delimitTrialSkate(dat)
            # create vector of force from vertical signal from each file and make low values 0
            totalForce = dat.FP3_RForceZ * -1
            totalForce[totalForce<fThresh] = 0
            XtotalForce = dat.FP3_ForceX
            YtotalForce = dat.FP3_RForceY
            COPy = dat.FP3_COPy
            
            #find the landings from function above
            landings = findLandings(totalForce)
            takeoffs = findTakeoffs(totalForce)
        
        elif tmpMove == 'CMJ':
            
            dat = delimitTrialCMJ(dat)
            
            totalForce = dat.FP2_ForceZ2 * -1
            totalForce[totalForce<fThresh] = 0
            COPy = dat.FP2_COPy2
            YtotalForce = totalForce #This is out of convenience to calculate impulse below even though this is not the Y force
            
            landings = findLandings(totalForce)
            landings= [x + 1 for x in landings] #add 1 and subtract 1 to trim takeoffs and landings so they do not encounter NaN
            
            takeoffs = findTakeoffs(totalForce)
            takeoffs = [x - 1 for x in takeoffs]
            
        else:
            print('movement is not identified')
        
        
        for countVar, landing in enumerate(landings):
            try:
                CT.append( takeoffs[countVar] - landing)
                impulse.append( np.sum(YtotalForce[landing:takeoffs[countVar]]) )
                RFDcon.append( np.min(np.diff(YtotalForce[landing:takeoffs[countVar]])) )
                
                COPexcursion.append( np.max(COPy[landing:takeoffs[countVar]]) - COPy[landing] ) 
                COPtraj.append( np.sum( abs(np.diff((COPy[landing:takeoffs[countVar]]))) ) )
                
                indMaxCOP = np.argmax( COPy[landing:takeoffs[countVar]] ) 
                indMaxFY = np.argmax( YtotalForce[landing:takeoffs[countVar]] )
                timingDiff.append(indMaxCOP - indMaxFY)
                
                subName.append(fName.split('_')[0])
                config.append( fName.split('_')[2] )
                movements.append( tmpMove )
                
            except:
                print(landing)
    except:
        print(file)


outcomes = pd.DataFrame({'Sub':list(subName), 'Config': list(config),'Movement':list(movements),
                         'copExc': list(COPexcursion), 'timingDiff':list(timingDiff), 'CT':list(CT),
                         'impulse':list(impulse), 'RFD':list(RFDcon), 'COPtraj':list(COPtraj) })

outcomes.to_csv("C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\AgilityPerformance/COPanalysis.csv")




