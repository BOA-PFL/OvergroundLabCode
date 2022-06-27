# -*- coding: utf-8 -*-
"""
Created on Mon May 17 14:48:59 2021

@author: kate.harrison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import copy

# Define constants and options
fThresh = 80 #below this value will be set to 0.

# Read in balance file
fPath = 'C:/Users/kate.harrison/Boa Technology Inc/PFL - Documents/General/Testing Segments/AgilityPerformanceData/CPDMech_PanelLength_June2022/Overground/'
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

def delimitTrial(inputDF):
    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    totForce = dat.FP1_GRF_Z + dat.FP2_GRF_Z + dat.FP3_GRF_Z + dat.FP4_GRF_Z
    ax.plot(totForce, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)


CT = []
impulseZ = []
impulseX = []
peakGRFz = []
peakGRFx = []
peakPFmom = []
peakINVmom = []
peakKneeEXTmom = []
kneeABDrom = []
eccWork = []
peakPower = []

subName = []
config = []
movements = []


## save configuration names from files
for fName in entries:
    try:
        
        #fName = entries[3]
        
        config1 = fName.split('_')[1]
        tmpMove = fName.split('_')[2]
        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        dat = dat.fillna(0)
        
        
        landings = [] # erase landings and takeoffs from last loop
        takeoffs = []
        if (tmpMove == 'Skater') or (tmpMove == 'skater'):
            
            dat = delimitTrial(dat)
            # create vector of force from vertical signal from each file and make low values 0
            if np.max(abs(dat.FP3_GRF_Z)) > np.max(abs(dat.FP4_GRF_Z)):
                ZForce = dat.FP3_GRF_Z
                XForce = dat.FP3_GRF_Y
                
            else:
                ZForce = dat.FP4_GRF_Z
                XForce = dat.FP4_GRF_Y 
                
            if abs(np.min(XForce)) > abs(np.max(XForce)):
                XForce = XForce * -1
                         
            ZForce[ZForce<fThresh] = 0
            
            
            #find the landings from function above
            landings = findLandings(ZForce)
            takeoffs = findTakeoffs(ZForce)
        
        elif (tmpMove == 'CMJ') or (tmpMove == 'cmj'):
            
            dat = delimitTrial(dat)
            
            ZForce = dat.FP2_GRF_Z
            ZForce[ZForce<fThresh] = 0
            
            XForce = dat.FP2_GRF_X 
            
            landings = findLandings(ZForce)
            takeoffs = findTakeoffs(ZForce)
            
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]]
            
        else:
            print('this movement is not included in Performance Test Analysis')
        
        
        for i in range(len(landings)):
            try:
                
                #i = 0
                CT.append((takeoffs[i] - landings[i])/200)
                impulseZ.append(np.sum(ZForce[landings[i]:takeoffs[i]])/200)
                impulseX.append(np.sum(XForce[landings[i]:takeoffs[i]])/200)
                
                peakGRFz.append(np.max(ZForce[landings[i]:takeoffs[i]]))
                peakGRFx.append(np.max(XForce[landings[i]:takeoffs[i]]))
            
                peakPFmom.append(np.min(dat.RAnkleMoment_Sagittal[landings[i]:takeoffs[i]])*-1)
                peakINVmom.append(np.max(dat.RAnkleMoment_Frontal[landings[i]:takeoffs[i]]))
                peakKneeEXTmom.append(np.max(dat.RKneeMoment_Sagittal[landings[i]:takeoffs[i]]))
                kneeABDrom.append(np.max(dat.RKneeAngle_Frontal[landings[i]:takeoffs[i]]) - np.min(dat.RKneeAngle_Frontal[landings[i]:takeoffs[i]]))
                negpower = copy.deepcopy(dat.COM_Power)
                negpower[negpower>0] = 0
                eccWork.append(np.sum(negpower[landings[i]:takeoffs[i]])/200*-1)
                peakPower.append(np.max(dat.COM_Power[landings[i]:takeoffs[i]]))
                
                
                subName.append(fName.split('_')[0])
                config.append( config1 )
                movements.append( tmpMove )
                
            except:
                print(landings[i])
    except:
        print(fName)


outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Movement':list(movements),
                         'CT':list(CT), 'impulse_Z':list(impulseZ), 'impulse_X':list(impulseX), 'peakGRF_Z':list(peakGRFz), 'peakGRF_X':list(peakGRFx), 'peakPFmom':list(peakPFmom),
                         'peakINVmom':list(peakINVmom), 'peakKneeEXTmom':list(peakKneeEXTmom), 'kneeABDrom':list(kneeABDrom), 'eccWork':list(eccWork), 'peakPower':list(peakPower) })

outfileName = fPath + 'CompiledAgilityData.csv'
outcomes.to_csv(outfileName, index = False)





