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

def delimitTrial(inputDF):
    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    ax.plot(inputDF.FP3_RForceZ, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)


COPexcursion = []
subName = []
config = []
movements = []
timingDiff = []
## save configuration names from files
for file in entries:
    try:
        fName = file #Load one file at a time
        config1 = fName.split('_')[2].split(' - ')[0]
        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        
        dat = delimitTrial(dat)
        
        # create vector of force from vertical signal from each file and make low values 0
        totalForce = dat.FP3_RForceZ * -1
        totalForce[totalForce<fThresh] = 0
        XtotalForce = dat.FP3_ForceX
        YtotalForce = dat.FP3_RForceY
        
        #find the landings from function above
        landings = findLandings(totalForce)
        
        
        for landing in landings:
            try:
                COPexcursion.append( np.max(dat.FP3_COPy[landing:landing+50]) - dat.FP3_COPy[landing] ) 
                indMaxCOP = np.argmax( dat.FP3_COPy[landing:landing+50]) 
                indMaxFY = np.argmax( dat.FP3_RForceY[landing:landing+50])
                timingDiff.append(indMaxCOP - indMaxFY)
                subName.append(fName.split('_')[0])
                config.append( fName.split('_')[2] )
                movements.append( fName.split('_')[3] )
            except:
                print(landing)
    except:
        print(file)


outcomes = pd.DataFrame({'Sub':list(subName), 'Config': list(config),'Movement':list(movements),
                         'copExc': list(COPexcursion), 'timingDiff':list(timingDiff)})

outcomes.to_csv("C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\AgilityPerformance/COPanalysis.csv")




