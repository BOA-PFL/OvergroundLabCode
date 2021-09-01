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
fThresh = 80 #below this value will be set to 0.
#stepLen = 45 #Set value to look forward 
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


# Initiate arrays for time series
ct = []
jmpHt = []
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

filename = askopenfilename()

dat = pd.read_csv(filename, sep='\t', skiprows = 7, header = 0)


## Might add some filtering in here to smooth out curves.


forceTot = (dat.FP1_Z + dat.FP2_Z)*-1

plt.plot(forceTot)
print('Click a zero point/starting time point on the plot')
minClick = plt.ginput(1)
endClick = plt.ginput(1) # click AFTER last landing (i.e not while the force is 0) 
plt.close()
minExtract = minClick[0]
(begin, y) = minExtract
begin = round(begin)
endExtract = endClick[0] 
(finish, y) = endExtract
finish = round(finish)
        
        
        
forceTot[forceTot<fThresh] = 0
        
    
#find the landings and offs of the FP as vector
landings = findLandings(forceTot)
landings[:] = [x for x in landings if x > begin] # remove landings before the start point specified on graph
takeoffs = findTakeoffs(forceTot)
takeoffs[:] = [x for x in takeoffs if x > landings[0]] # remove takeoffs before first landing
takeoffs[:] = [x for x in takeoffs if x < finish]



for i in range(len(takeoffs)):
    ct.append(takeoffs[i] - landings[i])
    
stepLen = max(ct)

for i in range(len(takeoffs)):
    RanklePower.append(dat.RightAnklePower[landings[i]: landings[i] + stepLen])
    LanklePower.append(dat.LeftAnklePower[landings[i]: landings[i] + stepLen])
    RkneePower.append(dat.RightKneePower[landings[i]: landings[i] + stepLen])
    LkneePower.append(dat.LeftKneePower[landings[i]: landings[i] + stepLen])
    RhipPower.append(dat.RightHipPower[landings[i]: landings[i] + stepLen])
    LhipPower.append(dat.LeftHipPower[landings[i]: landings[i] + stepLen])
    RkneeAngleFrontal.append(dat.RightKneeAngleY[landings[i]: landings[i] + stepLen])
    LkneeAngleFrontal.append(dat.LeftKneeAngleY[landings[i]: landings[i] + stepLen])
    RankleAngleFrontal.append(dat.RightAnkleAngle_Y[landings[i]: landings[i] + stepLen])
    LankleAngleFrontal.append(dat.LeftAnkleAngle_Y[landings[i]: landings[i] + stepLen])
    t = ((landings[i+1] - takeoffs[i])/100)/2  #find time to peak jump height
    jmpHt.append(0.5*9.81*t**2)
    
    
    
    
    
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
for i in range(len(takeoffs)):
    plt.plot(RanklePower[i,:], 'b', linewidth = 0.1)
    
plt.plot(RanklePowerMean, 'b', linewidth = 3)

       
for i in range(len(takeoffs)):
    plt.plot(LanklePower[i,:], 'r', linewidth = 0.1)
    
plt.plot(LanklePowerMean, 'r', linewidth = 3)
    
plt.title('Ankle power (Blue = right, Red = left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Power (Nm/s)')


## Plot Knee Power
plt.figure()

for i in range(len(takeoffs)):
    plt.plot(RkneePower[i,:], 'b', linewidth = 0.1)
    
plt.plot(RkneePowerMean, 'b', linewidth = 3)

       
for i in range(len(takeoffs)):
    plt.plot(LkneePower[i,:], 'r', linewidth = 0.1)
    
plt.plot(LkneePowerMean, 'r', linewidth = 3)
    
plt.title('Knee power (Blue = right, Red = left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Power (Nm/s)')

## Plot Hip Power
plt.figure()

for i in range(len(takeoffs)):
    plt.plot(RhipPower[i,:], 'b', linewidth = 0.1)
    
plt.plot(RhipPowerMean, 'b', linewidth = 3)

       
for i in range(len(takeoffs)):
    plt.plot(LhipPower[i,:], 'r', linewidth = 0.1)
    
plt.plot(LhipPowerMean, 'r', linewidth = 3)
    
plt.title('Hip power (Blue = right, Red = Left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Power (Nm/s)')

## Plot Ankle Angle
plt.figure()

for i in range(len(takeoffs)):
    plt.plot(RankleAngleFrontal[i,:], 'b', linewidth = 0.1)
    
plt.plot(RankleAngleFrontalMean, 'b', linewidth = 3)

       
for i in range(len(takeoffs)):
    plt.plot(LankleAngleFrontal[i,:], 'r', linewidth = 0.1)
    
plt.plot(LankleAngleFrontalMean, 'r', linewidth = 3)
    
plt.title('Frontal Plane Ankle Angle (Blue = right, Red = Left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Angle (degrees)')

## Plot Knee angle
plt.figure()

for i in range(len(takeoffs)):
    plt.plot(RkneeAngleFrontal[i,:], 'b', linewidth = 0.1)
    
plt.plot(RkneeAngleFrontalMean, 'b', linewidth = 3)

       
for i in range(len(takeoffs)):
    plt.plot(LkneeAngleFrontal[i,:], 'r', linewidth = 0.1)
    
plt.plot(LkneeAngleFrontalMean, 'r', linewidth = 3)
    
plt.title('Frontal Plane Knee Angle (Blue = right, Red = Left)')
plt.xlabel('Ground contact time (ms)')
plt.ylabel('Angle (degrees)')

########################### Calculate point estimates #############################################
contactTime = np.mean(ct)
jumpHeight = np.mean(jmpHt)
peakRanklePower = np.mean(np.nanmax(RanklePower, axis = 0))
peakLanklePower = np.mean(np.nanmax(LanklePower, axis = 0))
anklePowerSym = 1 - abs(peakRanklePower - peakLanklePower)/((peakRanklePower + peakLanklePower)/2)

peakRkneePower = np.mean(np.nanmax(RkneePower, axis = 0))
peakLkneePower = np.mean(np.nanmax(LkneePower, axis = 0))
kneePowerSym = 1 - abs(peakRkneePower - peakLkneePower)/((peakRkneePower + peakLkneePower)/2)

peakRhipPower = np.mean(np.nanmax(RhipPower, axis = 0))
peakLhipPower = np.mean(np.nanmax(LhipPower, axis = 0))
hipPowerSym = 1 - abs(peakRhipPower - peakLhipPower)/((peakRhipPower + peakLhipPower)/2)

peakRinv = np.mean(np.nanmax(RankleAngleFrontal, axis = 0))
peakLinv = np.mean(np.nanmax(LankleAngleFrontal, axis = 0))
invSym = 1 - abs(peakRinv - peakLinv)/((peakRinv + peakLinv)/2)

peakRkneeAbd = np.mean(np.nanmax(RkneeAngleFrontal, axis = 0)) ## Is this actually a max or min??
peakLkneeAbd = np.mean(np.nanmax(LkneeAngleFrontal, axis = 0)) ## Is this actually a max or min??
abdSym = 1 - abs(peakRkneeAbd - peakLkneeAbd)/((peakRkneeAbd + peakLkneeAbd)/2)

#output = pd.DataFrame([[peakLanklePower, peakRanklePower, anklePowerSym], [peakLkneePower, peakRkneePower, kneePowerSym],[peakLhipPower, peakRhipPower, hipPowerSym]], columns = ['Left', 'Right','Symmetry'], index = ['Ankle Power', 'Knee Power', 'Hip Power'])

### Run Data ###

L_vlr = []
R_vlr = []

filename = askopenfilename()

rundat = pd.read_csv(filename, sep='\t', skiprows = 7, header = 0)

runfz = rundat.LForceZ *-1
runfz[runfz<fThresh] = 0



landings = findLandings(runfz)
takeoffs = findTakeoffs(runfz)
takeoffs[:] = [x for x in takeoffs if x > landings[0]] # remove takeoffs before first landing
landings[:] = [x for x in landings if x < takeoffs[-1]] # remove landings after last takeoff

copX1 = rundat.LCOPx[landings[0]]
copX2 = rundat.LCOPx[landings[1]]

if copX1<copX2:
    L_landings = landings[0:-1:2]
    L_takeoffs = takeoffs[0:-1:2]
    R_landings = landings[1:-1:2]
    R_takeoffs = takeoffs[1:-1:2]
else:
    L_landings = landings[1:-1:2]
    L_takeoffs = takeoffs[1:-1:2]
    R_landings = landings[0:-1:2]
    R_takeoffs = takeoffs[0:-1:2]

for i in range(len(L_landings)):
    runct = L_takeoffs[i] - L_landings[i]
    t4 = L_landings[i] + round(runct*0.04)
    t14 = L_landings[i] + round(runct*0.14)
    f4 = runfz[t4]
    f14 = runfz[t14]
    L_vlr.append((f14-f4)/(t14-t4))
    
for i in range(len(R_landings)):
    
    runct = R_takeoffs[i] - R_landings[i]
    t4 = R_landings[i] + round(runct*0.04)
    t14 = R_landings[i] + round(runct*0.14)
    f4 = runfz[t4]
    f14 = runfz[t14]
    R_vlr.append((f14-f4)/(t14-t4))
    
LeftVLR = np.mean(L_vlr)
RightVLR = np.mean(R_vlr)   
VLRsym = 1 - abs(RightVLR - LeftVLR)/((RightVLR + LeftVLR)/2)

output_PageOne = pd.DataFrame([[peakLanklePower, peakRanklePower, anklePowerSym], [peakLkneePower, peakRkneePower, kneePowerSym],[peakLhipPower, peakRhipPower, hipPowerSym]], columns = ['Left', 'Right','Symmetry'], index = ['Ankle Power', 'Knee Power', 'Hip Power'])

output_PageTwo = pd.DataFrame([[peakLkneeAbd, peakRkneeAbd, abdSym], [peakLinv, peakRinv, invSym], [LeftVLR, RightVLR, VLRsym]], columns = ['Left', 'Right', 'Symmetery'], index = ['Knee Alignment', 'Ankle inversion', 'Impact'])

print('Copy contactTime, jumpHeight and data from output_PageOne and output_PageTwo into feedback sheet')

print(contactTime)
print(jumpHeight)
print(output_PageOne)
print(output_PageTwo)