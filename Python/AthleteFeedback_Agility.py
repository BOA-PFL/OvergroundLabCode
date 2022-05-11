# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 09:07:04 2021

@author: Kate.Harrison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename



# Define constants and options
fThresh = 40 #below this value will be set to 0.
#stepLen = 45 #Set value to look forward 
# list of functions 
# finding landings on the force plate once the filtered force exceeds the force threshold
# def findLandings(force, fThresh):
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
def findLandings(force, fThresh):    
    lic = [] 
    fThresh = 40
    for step in range(len(force)-1):
        if len(lic) == 0: 
            
            if force[step] == 0 and force[step + 1] >= fThresh and force [step + 10 ] > 300:
                lic.append(step)
    
        else:
        
            if force[step] == 0 and force[step + 1] >= fThresh and step > lic[-1] + 300 and force [step + 10] > 300:
                lic.append(step)
    return lic



# def findTakeoffs(force, fThresh):
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
def findTakeoffs(force, fThresh):    
    lto = [] 
    fThresh = 40
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0 and force[step + 5] == 0 and force[step + 10] == 0:
            lto.append(step + 1)
    return lto

# Initiate arrays for time series

RanklePower = []
LanklePower = []
RkneePower = []
LkneePower = []
RhipPower = []
LhipPower = []
RkneeAngleFrontal = []
LkneeAngleFrontal = []
RankleAngleFrontal = []
LankleAngleFrontal = []

filename = askopenfilename() # Open CMJ file

dat = pd.read_csv(filename, sep='\t', skiprows = 7, header = 0)


## Might add some filtering in here to smooth out curves.


forceTot = (dat.FP1_GRF_Z + dat.FP2_GRF_Z)*1

#  Once the plot pops up, click a starting point and click an ending point
plt.plot(forceTot)
print('Click a zero point/starting time point on the plot')
minClick = plt.ginput(1)
endClick = plt.ginput(1)
plt.close()
minExtract = minClick[0]
(begin, y) = minExtract
begin = round(begin)
endExtract = endClick[0]
(finish, y) = endExtract
finish = round(finish)
        
        
        
forceTot[forceTot<fThresh] = 0
        
    
#find the landings and offs of the FP as vector
landings = findLandings(forceTot, fThresh)
landings[:] = [x for x in landings if x > begin] # remove landings before the start point specified on graph
takeoffs = findTakeoffs(forceTot, fThresh)
takeoffs[:] = [x for x in takeoffs if x > landings[0]] # remove takeoffs before first landing
landings[:] = [x for x in landings if x < finish]

ct = []

for i in range(len(landings)):
    ct.append(takeoffs[i] - landings[i])
    
stepLen = max(ct)

for i in range(len(landings)):
    RanklePower.append(dat.RightAnklePower[landings[i]: landings[i] + stepLen])
    LanklePower.append(dat.LeftAnklePower[landings[i]: landings[i] + stepLen])
    RkneePower.append(dat.RightKneePower[landings[i]: landings[i] + stepLen])
    LkneePower.append(dat.LeftKneePower[landings[i]: landings[i] + stepLen])
    RhipPower.append(dat.RHipPower[landings[i]: landings[i] + stepLen])
    LhipPower.append(dat.LHipPower[landings[i]: landings[i] + stepLen])
    RkneeAngleFrontal.append(dat.RKneeAngle_Frontal[landings[i]: landings[i] + stepLen])
    LkneeAngleFrontal.append(dat.LKneeAngle_Frontal[landings[i]: landings[i] + stepLen])
    RankleAngleFrontal.append(dat.RAnkleAngle_Frontal[landings[i]: landings[i] + stepLen])
    LankleAngleFrontal.append(dat.LAnkleAngle_Frontal[landings[i]: landings[i] + stepLen])
    
RanklePower = np.stack(RanklePower, axis = 0)  
LanklePower = np.stack(LanklePower, axis = 0)
RkneePower = np.stack(RkneePower, axis = 0)
LkneePower = np.stack(LkneePower, axis = 0)
RhipPower = np.stack(RhipPower, axis = 0)
LhipPower = np.stack(LhipPower, axis = 0)
RkneeAngleFrontal = np.stack(RkneeAngleFrontal, axis = 0)
LkneeAngleFrontal = np.stack(LkneeAngleFrontal, axis = 0)
RankleAngleFrontal = np.stack(RankleAngleFrontal, axis = 0)
LankleAngleFrontal = np.stack(LankleAngleFrontal, axis = 0)

RanklePowerMean = np.mean(RanklePower, axis = 0)
LanklePowerMean = np.mean(LanklePower, axis = 0)
RkneePowerMean = np.mean(RkneePower, axis = 0)
LkneePowerMean = np.mean(LkneePower, axis = 0)
RhipPowerMean = np.mean(RhipPower, axis = 0)
LhipPowerMean = np.mean(LhipPower, axis = 0)
RkneeAngleFrontalMean = np.mean(RkneeAngleFrontal, axis = 0)
LkneeAngleFrontalMean = np.mean(LkneeAngleFrontal, axis = 0)
RankleAngleFrontalMean = np.mean(RankleAngleFrontal, axis = 0)
LankleAngleFrontalMean = np.mean(LankleAngleFrontal, axis = 0)

    
## Plot Ankle Power
for i in range(len(landings)):
    plt.plot(RanklePower[i,:], 'b', linewidth = 0.1)
    
plt.plot(RanklePowerMean, 'b', linewidth = 3)

       
for i in range(len(landings)):
    plt.plot(LanklePower[i,:], 'r', linewidth = 0.1)
    
plt.plot(LanklePowerMean, 'r', linewidth = 3)
    
plt.title('Ankle power (Blue = right, Red = left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Power (Nm/s)')


## Plot Knee Power
plt.figure()

for i in range(len(landings)):
    plt.plot(RkneePower[i,:], 'b', linewidth = 0.1)
    
plt.plot(RkneePowerMean, 'b', linewidth = 3)

       
for i in range(len(landings)):
    plt.plot(LkneePower[i,:], 'r', linewidth = 0.1)
    
plt.plot(LkneePowerMean, 'r', linewidth = 3)
    
plt.title('Knee power (Blue = right, Red = left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Power (Nm/s)')

## Plot Hip Power
plt.figure()

for i in range(len(landings)):
    plt.plot(RhipPower[i,:], 'b', linewidth = 0.1)
    
plt.plot(RhipPowerMean, 'b', linewidth = 3)

       
for i in range(len(landings)):
    plt.plot(LhipPower[i,:], 'r', linewidth = 0.1)
    
plt.plot(LhipPowerMean, 'r', linewidth = 3)
    
plt.title('Hip power (Blue = right, Red = Left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Power (Nm/s)')

## Plot Ankle Angle
plt.figure()

for i in range(len(landings)):
    plt.plot(RankleAngleFrontal[i,:], 'b', linewidth = 0.1)
    
plt.plot(RankleAngleFrontalMean, 'b', linewidth = 3)

       
for i in range(len(landings)):
    plt.plot(LankleAngleFrontal[i,:], 'r', linewidth = 0.1)
    
plt.plot(LankleAngleFrontalMean, 'r', linewidth = 3)
    
plt.title('Frontal Plane Ankle Angle (Blue = right, Red = Left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Angle (degrees)')

## Plot Knee angle
plt.figure()

for i in range(len(landings)):
    plt.plot(RkneeAngleFrontal[i,:], 'b', linewidth = 0.1)
    
plt.plot(RkneeAngleFrontalMean, 'b', linewidth = 3)

       
for i in range(len(landings)):
    plt.plot(LkneeAngleFrontal[i,:], 'r', linewidth = 0.1)
    
plt.plot(LkneeAngleFrontalMean, 'r', linewidth = 3)
    
plt.title('Frontal Plane Knee Angle (Blue = right, Red = Left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Angle (degrees)')

########################### Calculate point estimates #############################################


peakRanklePower = np.mean(np.nanmax(RanklePower, axis = 0))
peakLanklePower = np.mean(np.nanmax(LanklePower, axis = 0))
anklePowerSym = 1 - abs(peakRanklePower - peakLanklePower)/((peakRanklePower + peakLanklePower)/2)

peakRkneePower = np.mean(np.nanmax(RkneePower, axis = 0))
peakLkneePower = np.mean(np.nanmax(LkneePower, axis = 0))
kneePowerSym = 1 - abs(peakRkneePower - peakLkneePower)/((peakRkneePower + peakLkneePower)/2)

peakRhipPower = np.mean(np.nanmax(RhipPower, axis = 0))
peakLhipPower = np.mean(np.nanmax(LhipPower, axis = 0))
hipPowerSym = 1 - abs(peakRhipPower - peakLhipPower)/((peakRhipPower + peakLhipPower)/2)

peakRAnkleinv = np.mean(np.nanmax(RankleAngleFrontal, axis = 0))
peakLAnkleinv = np.mean(np.nanmax(LankleAngleFrontal, axis = 0))
AnkleinvSym = 1 - abs(peakRAnkleinv - peakLAnkleinv)/((peakRAnkleinv + peakLAnkleinv)/2)

peakRKneeAbd = np.mean(np.nanmax(RkneeAngleFrontal, axis = 0))
peakLKneeAbd = np.mean(np.nanmax(LkneeAngleFrontal, axis = 0)) 
abdSym =  1 - abs(peakRKneeAbd - peakLKneeAbd)/((peakRKneeAbd + peakLKneeAbd)/2)

output = pd.DataFrame([[peakLanklePower, peakRanklePower, anklePowerSym], [peakLkneePower, peakRkneePower, kneePowerSym],[peakLhipPower, peakRhipPower, hipPowerSym],[peakRAnkleinv,peakLAnkleinv, AnkleinvSym ],[peakRKneeAbd, peakLKneeAbd,abdSym ]], columns = ['Left', 'Right','Symmetry'], index = ['Ankle Power', 'Knee Power', 'Hip Power','Ankle Abd Angle','Knee Abd Angle'])
