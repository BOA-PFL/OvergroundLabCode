# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 09:45:18 2020
Visualize shadded errorbars
@author: Daniel.Feeney
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define constants and options
fThresh = 80 #below this value will be set to 0.
stepLen = 75

# Read in balance file
fPath = 'C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\Hike Work Research\\Work Pilot 2021\\SLL\\'
fPath = 'C:\\Users\\Daniel.Feeney\\Dropbox (Boa)\\AgilityPerformance\\Altra_June2021\\Landings\\'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]

fName = entries[1] #Load one file at a time
fName2 = entries[4]
fName3 = entries[7]
subName = fName.split('_')[0]

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

## save configuration names from files
config1 = fName.split('_')[2].split(' - ')[0]
config2 = fName2.split('_')[2].split(' - ')[0]
config3 = fName3.split('_')[2].split(' - ')[0]

dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
dat2 = pd.read_csv(fPath+fName2,sep='\t', skiprows = 8, header = 0) 
dat3 = pd.read_csv(fPath+fName3,sep='\t', skiprows = 8, header = 0) 

# create vector of force from vertical signal from each file and make low values 0
totalForce = dat.FP3_RForceZ * -1
totalForce[totalForce<fThresh] = 0
XtotalForce = dat.FP3_ForceX
YtotalForce = dat.FP3_RForceY

totalForce2 = dat2.FP3_RForceZ * -1
totalForce2[totalForce2<fThresh] = 0
XtotalForce2 = dat2.FP3_ForceX
YtotalForce2 = dat.FP3_RForceY

totalForce3 = dat3.FP3_RForceZ * -1
totalForce3[totalForce3<fThresh] = 0
XtotalForce3 = dat3.FP3_ForceX
YtotalForce3 = dat.FP3_RForceY

#find the landings from function above
landings = findLandings(totalForce)
landings2 = findLandings(totalForce2)
landings3 = findLandings(totalForce3)

#Create matrix data from function above
XforceOut1 = forceMatrix(XtotalForce, landings, 3, stepLen)
XforceOut2 = forceMatrix(XtotalForce2, landings2, 3, stepLen)
XforceOut3 = forceMatrix(XtotalForce3, landings3, 3, stepLen)

#Create matrix data from function above
YforceOut1 = forceMatrix(YtotalForce, landings, 3, stepLen)
YforceOut2 = forceMatrix(YtotalForce2, landings2, 3, stepLen)
YforceOut3 = forceMatrix(YtotalForce3, landings3, 3, stepLen)

#Create matrix data from function above for X force
forceOut1 = forceMatrix(totalForce, landings, 3, stepLen)
forceOut2 = forceMatrix(totalForce2, landings2, 3, stepLen)
forceOut3 = forceMatrix(totalForce3, landings3, 3, stepLen)


# create matrices with average and SD of force trajectories
x = np.linspace(0,stepLen,stepLen)
avgF1 = np.mean(forceOut1, axis = 0)
sdF1 = np.std(forceOut1, axis = 0)
avgXF1 = np.mean(XforceOut1, axis = 0)
sdXF1 = np.std(XforceOut1, axis = 0)
avgYF1 = np.mean(YforceOut1, axis = 0)
sdYF1 = np.std(YforceOut1, axis = 0)

avgF2 = np.mean(forceOut2,axis=0)
sdF2 = np.std(forceOut2, axis = 0)
avgXF2 = np.mean(XforceOut2, axis = 0)
sdXF2 = np.std(XforceOut2, axis = 0)
avgYF2 = np.mean(YforceOut2, axis = 0)
sdYF2 = np.std(YforceOut2, axis = 0)

avgF3 = np.mean(forceOut3,axis=0)
sdF3 = np.std(forceOut3, axis = 0)
avgXF3 = np.mean(XforceOut3, axis = 0)
sdXF3 = np.std(XforceOut3, axis = 0)
avgYF3 = np.mean(YforceOut3, axis = 0)
sdYF3 = np.std(YforceOut3, axis = 0)

#Plot force
fig, (ax1, ax2, ax3) = plt.subplots(1,3)
ax1.plot(x, avgF1, 'k', color='#ECEB1A', label = '{}'.format(config1))
ax1.plot(x, avgF2, 'k', color='#00966C', label = '{}'.format(config2))
ax1.plot(x, avgF3, 'k', color='#000000', label = '{}'.format(config3))
ax1.set_xlabel('Time')
ax1.set_ylabel('Force (N)')
ax1.set_title('Average Vertical Force')
ax1.fill_between(x, avgF1-sdF1, avgF1+sdF1,
    alpha=0.5, edgecolor='#ECEB1A', facecolor='#ECEB1A')
ax1.fill_between(x, avgF2-sdF2, avgF2+sdF2,
    alpha=0.5, edgecolor='#00966C', facecolor='#00966C')
ax1.fill_between(x, avgF3-sdF3, avgF3+sdF3,
    alpha=0.5, edgecolor='#000000', facecolor='#000000')

ax2.plot(x, avgXF1, 'k', color='#ECEB1A', label = '{}'.format(config1))
ax2.plot(x, avgXF2, 'k', color='#00966C', label = '{}'.format(config2))
ax2.plot(x, avgXF3, 'k', color='#000000', label = '{}'.format(config3))
ax2.set_xlabel('Time')
ax2.set_ylabel('Force (N)')
ax2.set_title('Average A-P Force')
ax2.fill_between(x, avgXF1-sdXF1, avgXF1+sdXF1,
    alpha=0.5, edgecolor='#ECEB1A', facecolor='#ECEB1A')
ax2.fill_between(x, avgXF2-sdXF2, avgXF2+sdXF2,
    alpha=0.5, edgecolor='#00966C', facecolor='#00966C')
ax2.fill_between(x, avgXF3-sdXF3, avgXF3+sdXF3,
    alpha=0.5, edgecolor='#000000', facecolor='#000000')
ax2.legend(loc = 'right')

ax3.plot(x, avgYF1, 'k', color='#ECEB1A', label = '{}'.format(config1))
ax3.plot(x, avgYF2, 'k', color='#00966C', label = '{}'.format(config2))
ax3.plot(x, avgYF3, 'k', color='#000000', label = '{}'.format(config3))
ax3.set_xlabel('Time')
ax3.set_ylabel('Force (N)')
ax3.set_title('Average M-L Force')
ax3.fill_between(x, avgYF1-sdXF1, avgYF1+sdYF1,
    alpha=0.5, edgecolor='#ECEB1A', facecolor='#ECEB1A')
ax3.fill_between(x, avgYF2-sdXF2, avgYF2+sdYF2,
    alpha=0.5, edgecolor='#00966C', facecolor='#00966C')
ax3.fill_between(x, avgYF3-sdYF3, avgYF3+sdYF3,
    alpha=0.5, edgecolor='#000000', facecolor='#000000')
plt.suptitle('{} Single Leg Landing'.format(subName))
plt.tight_layout()




    