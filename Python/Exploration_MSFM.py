# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 11:00:16 2022

@author: Kate.Harrison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import signal
from scipy import interpolate
from tkinter.filedialog import askopenfilenames
import tkinter as tk


ROOT = tk.Tk()
ROOT.withdraw()

# plt.figure(3)
# plt.title('Ankle Sagittal')
# plt.xlabel('Percent Stance')
# plt.ylabel('Joint position (deg)')
# plt.figure(4)
# plt.title('Ankle Frontal')
# plt.xlabel('Percent Stance')
# plt.ylabel('Joint position (deg)')
# plt.figure(5)
# plt.title('Ankle Transverse')
# plt.xlabel('Percent Stance')
# plt.ylabel('Joint position (deg)')

plt.figure(6)
plt.title('Midfoot Sagittal')
plt.xlabel('Percent Stance')
plt.ylabel('Joint position (deg)')
plt.figure(7)
plt.title('Midfoot Frontal')
plt.xlabel('Percent Stance')
plt.ylabel('Joint position (deg)')
plt.figure(8)
plt.title('Midfoot Transverse')
plt.xlabel('Percent Stance')
plt.ylabel('Joint position (deg)')

# plt.figure(9)
# plt.title('Toe Sagittal')
# plt.xlabel('Percent Stance')
# plt.ylabel('Joint position (deg)')
# plt.figure(10)
# plt.title('Toe Valgus')
# plt.xlabel('Percent Stance')
# plt.ylabel('Joint position (deg)')

# plt.figure(10)
# plt.title('Foot sliding M/L')
# plt.xlabel('Percent Stance')
# plt.ylabel('Foot Position M/L relative to landing position')
# plt.figure(11)
# plt.title('Foot sliding A/P')
# plt.xlabel('Percent Stance')
# plt.ylabel('Foot Position A/P relative to landing position')

# initiate output arrays
Subject = []
Condition = []
Movement = []
# Velocity = []
Markers = []


# time series data
# ankle_Sagittal = []
# ankle_Frontal = []
# ankle_Transverse = []

midfoot_Sagittal = []
midfoot_Frontal = []
midfoot_Transverse = []

# toe_Sagittal = []
# toe_Valgus = []

# foot_COM_X = []
# foot_COM_Y = []
    
# Read files
fPath = 'C:/Users/kate.harrison/Boa Technology Inc/PFL Team - Documents/General/Testing Segments/MSFM_April2022/Data/'
entries = askopenfilenames(initialdir = fPath)


for fName in entries:
    # loop through files for individual subjects to extract data.
    #fName = entries[0]

    # extract info from filename
    info = fName.split(sep = "/")[-1]
    sub = info.split(sep = "_")[0]
    config = info.split(sep = "_")[2]
    move = info.split(sep = "_")[3]
    markers = info.split(sep = "_")[4]
    trial = info.split(sep = "_")[5].split(sep = " ")[0]
    dat = pd.read_csv(fName, sep = '	',skiprows = 8, header = 0, index_col = False)
    
    plt.plot(dat.Midfoot_Sagittal)
    print('Select start and end of good data')
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    # downselect the region of the dataframe you selected from above 
    dat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    dat = dat.reset_index()
    
    
    # trim file to remove bad data at start/end of trial
    if move == 'Walking' or move == 'Walk' or move == 'Running' or move == 'Run':
        # initial contact is identified as the minimum heel acceleration within +/- 10 frames of the maximum of the heel jerk squared.
        dat["heel_jerk"] = np.gradient(np.gradient(np.gradient(dat.Heel_Position, 0.1), 0.1), 0.1)
        dat["heel_jerk_sq"] = dat.heel_jerk**2
        dat["heel_accel"] = np.gradient(np.gradient(dat.Heel_Position, 0.1), 0.1)
        
        
        if move == 'Walking' or move == 'Walk':
            maxjerk = np.max(dat.heel_jerk_sq)
            jerkPeak, _ = signal.find_peaks(dat.heel_jerk_sq, distance = 180, threshold = maxjerk*0.5    )
        else:
            maxjerk = np.max(dat.heel_jerk_sq)
            jerkPeak, _ = signal.find_peaks(dat.heel_jerk_sq, distance = 60, threshold = maxjerk*0.5  )

        hs = []

        for i in range(len(jerkPeak)):
            #i = 0
            tmpAccel = np.array(dat.heel_accel[jerkPeak[i] -10:jerkPeak[i] ])
            minAccIdx = np.argmin(tmpAccel)
            hs.append(jerkPeak[i] -10 + minAccIdx)
       
        to = []
        for i in range(len(dat.Heel_Position)-1):
            #i = 0
            if dat.Heel_Position[i] < 0.15 and dat.Heel_Position[i+1] >= 0.15:
                to.append(i)
        
        # plt.figure()
        # plt.plot(dat.heel_jerk_sq)
        # plt.plot(dat.index[hs], dat.heel_jerk_sq[hs], "x", color = 'green' ) # plot initial contacts to verify 
        # plt.plot(dat.index[jerkPeak], dat.heel_jerk_sq[jerkPeak], "x", color = 'red')
            
        # plt.figure()
        # plt.plot(dat.heel_accel)
        # plt.plot(dat.index[hs], dat.heel_accel[hs], "x", color = 'green' ) # plot initial contacts to verify 
        # plt.plot(dat.index[jerkPeak], dat.heel_accel[jerkPeak], "x", color = 'red')
            
    else:
        dat['force'] = (dat.Fz_FP2 + dat.Fz_FP4)*-1
        fig, ax = plt.subplots()
        ax.plot(dat.force, color = 'red')
        ax.set_xlabel("Time (msec)", color = 'red')
        ax.set_ylabel("Force (N)")
        plt.show()

        print('Select start and end of good data')
        pts = np.asarray(plt.ginput(2, timeout=-1))
        plt.close()
        # downselect the region of the dataframe you selected from above 
        dat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
        dat = dat.reset_index()
        hs = []
        
        for step in range(len(dat.force)-1):
            if dat.force[step] <40 and dat.force[step + 1] >= 40:
                hs.append(step)
                
        to = []
        for step in range(len(dat.index)-1):
            if dat.force[step] >=40 and dat.force[step + 1] < 40:
                to.append(step)
    
    try: 
        hs[:] = [x for x in hs if x < to[-1]]
        to[:] = [x for x in to if x > hs[0]]
    except:
        print('Missing gait events')
        
        
        
        fig, ax = plt.subplots(2)
        # ax[0].plot(dat.Pelvis_Velocity, color = 'blue', label = 'Pelvis Velocity')
        # ax[0].set_xlabel("Time (msec)")
        # ax[0].set_ylabel("Pelvis Velocity (m/s)", color = 'blue')
        # plt.ylim([0,10])
        # plt.legend()
        # ax[1].plot(dat.MSFM_Ankle_Sagittal, color = 'red', label = 'Ankle Angle')
        ax[0].plot(dat.Midfoot_Angle_Sagittal, color = 'orange', label = 'Midfoot Angle')
        # ax[1].plot(dat.Toe_Angle_Sagittal, color = 'yellow', label = 'Toe Angle')
        ax[0].set_ylabel('Joint Angle')
        plt.ylim([-50,50])
        plt.legend()
        ax[1].plot(dat.Heel_Position)
        ax[1].plot(dat.index[hs], dat.Heel_Position[hs], "x", color = 'green' )            
        ax[1].plot(dat.index[to], dat.Heel_Position[to], "x", color = 'red')
        plt.ylim([0, 0.5])
        plt.legend()
        plt.show()

        print('Select start and end of good data')
        pts = np.asarray(plt.ginput(2, timeout=-1))
        plt.close()
        # downselect the region of the dataframe you selected from above 
        dat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
        dat = dat.reset_index()
    
    
        # calculate running/walking velocity. Only use trials within the prescribed range
    

        ##Use if we need to manually ID threshold for heel_jerk_sq for initial contact
        # plt.plot(dat.heel_jerk_sq)
        # thresh = np.asarray( plt.ginput(1))
        # hs, _ = signal.find_peaks(dat.heel_jerk_sq, height = thresh[0,1], distance = 75 )

                
        #Calculate toe off as the peak knee extention after heel strike (with minimum width 15 to exclude fales peaks during midstance)
       
    
    
    #vel = np.mean(dat.Pelvis_Velocity)
    
    plt.close()
    if dat.shape[0] > 50:
        for i in range(len(hs)):
            # loop through all steps in a trial to extract time series. Interpolate all stance phases to 101 points
            #i = 0
            x = np.linspace(hs[i], to[i], 101)
                
            # interp = interpolate.interp1d(np.arange(hs[i],to[i]+1, 1), dat.MSFM_Ankle_Sagittal[hs[i]:to[i]+1], kind = "cubic")
            # ankle_Sagittal.append(interp(x))
            # plt.figure(3)
            # if config == 'Loose':
            #     plt.plot(interp(x), color = 'red', label = "Loose")
            # else:
            #     plt.plot(interp(x), color = 'blue', label = "Tight")
            
            
            # plt.figure(4)
            # interp = interpolate.interp1d(np.arange(hs[i],to[i]+1, 1), dat.MSFM_Ankle_Frontal[hs[i]:to[i]+1], kind = "cubic")
            # ankle_Frontal.append(interp(x))
            # if config == 'Loose':
            #     plt.plot(interp(x), color = 'red', label = "Loose")
            # else:
            #     plt.plot(interp(x), color = 'blue', label = "Tight")
            
            
            # plt.figure(5)
            # interp = interpolate.interp1d(np.arange(hs[i],to[i]+1, 1), dat.MSFM_Ankle_Transverse[hs[i]:to[i]+1], kind = "cubic")
            # ankle_Transverse.append(interp(x))
            # if config == 'Loose':
            #     plt.plot(interp(x), color = 'red', label = "Loose")
            # else:
            #     plt.plot(interp(x), color = 'blue', label = "Tight")
            
            
            interp = interpolate.interp1d(np.arange(hs[i],to[i]+1, 1), dat.Midfoot_Angle_Sagittal[hs[i]:to[i]+1], kind = "cubic")
            midfoot_Sagittal.append(interp(x))
            plt.figure(6)
            if config == 'Loose':
                plt.plot(interp(x), color = 'red', label = "Loose")
            else:
                plt.plot(interp(x), color = 'blue', label = "Tight")
            
            
            interp = interpolate.interp1d(np.arange(hs[i],to[i]+1, 1), dat.Midfoot_Angle_Frontal[hs[i]:to[i]+1], kind = "cubic")
            midfoot_Frontal.append(interp(x))
            plt.figure(7)
            if config == 'Loose':
                plt.plot(interp(x), color = 'red', label = "Loose")
            else:
                plt.plot(interp(x), color = 'blue', label = "Tight")
            
            
            interp = interpolate.interp1d(np.arange(hs[i],to[i]+1, 1), dat.Midfoot_Angle_Transverse[hs[i]:to[i]+1], kind = "cubic")
            midfoot_Transverse.append(interp(x))
            plt.figure(8)
            if config == 'Loose':
                plt.plot(interp(x), color = 'red', label = "Loose")
            else:
                plt.plot(interp(x), color = 'blue', label = "Tight")
            
            
            # interp = interpolate.interp1d(np.arange(hs[i],to[i]+1, 1), dat.Toe_Angle_Sagittal[hs[i]:to[i]+1], kind = "cubic")
            # toe_Sagittal.append(interp(x))
            # plt.figure(9)
            # if config == 'Loose':
            #     plt.plot(interp(x), color = 'red', label = "Loose")
            # else:
            #     plt.plot(interp(x), color = 'blue', label = "Tight")
            
                
            # interp = interpolate.interp1d(np.arange(hs[i],to[i]+1, 1), dat.Toe_Angle_Valgus[hs[i]:to[i]+1], kind = "cubic")
            # toe_Valgus.append(interp(x))
            # plt.figure(10)
            # if config == 'Loose':
            #     plt.plot(interp(x), color = 'red', label = "Loose")
            # else:
            #     plt.plot(interp(x), color = 'blue', label = "Tight")
            
            # foot_x = np.array(dat.Foot_COM_X[hs[i]:to[i]+1])- dat.Foot_COM_X[hs[i]] # Center COM location on landing position 
            # interp = interpolate.interp1d(np.arange(hs[i],to[i]+1, 1), foot_x, kind = "cubic")
            # foot_COM_X.append(interp(x))
            # plt.figure(11)
            # if config == 'Loose':
            #     plt.plot(interp(x), color = 'red', label = "Loose")
            # else:
            #     plt.plot(interp(x), color = 'blue', label = "Tight")
                
                
            # plt.figure()
            # plt.plot(foot_x)
            Subject.append(sub)
            Condition.append(config)
            Movement.append(move)
            # Velocity.append(vel)
            Markers.append(markers)
                
    else:
        print(fName + ' poor data')

for i in range(1,10,1):
    plt.figure(i)
    plt.legend()

### Export compiled time series data

infoDat = pd.DataFrame({'Subject':list(Subject),'Config':list(Condition),'Movement': list(Movement)
                                 
                                 })

# timeSeriesDat = pd.DataFrame(np.stack(ankle_Sagittal))
# outputDat = pd.concat([infoDat, timeSeriesDat], axis = 1)
# outfileName = fPath + 'ankle_Sagittal.csv'

# if os.path.exists(outfileName) == False:
    
#     outputDat.to_csv(outfileName, mode='a', header=True, index = False)

# else:
#     outputDat.to_csv(outfileName, mode='a', header=False, index = False) 
    
    

# timeSeriesDat = pd.DataFrame(np.stack(ankle_Frontal))
# outputDat = pd.concat([infoDat, timeSeriesDat], axis = 1)
# outfileName = fPath + 'ankle_Frontal.csv'

# if os.path.exists(outfileName) == False:
    
#     outputDat.to_csv(outfileName, mode='a', header=True, index = False)

# else:
#     outputDat.to_csv(outfileName, mode='a', header=False, index = False)
    
    
# timeSeriesDat = pd.DataFrame(np.stack(ankle_Transverse))
# outputDat = pd.concat([infoDat, timeSeriesDat], axis = 1)
# outfileName = fPath + 'ankle_Transverse.csv'

# if os.path.exists(outfileName) == False:
    
#     outputDat.to_csv(outfileName, mode='a', header=True, index = False)

# else:
#     outputDat.to_csv(outfileName, mode='a', header=False, index = False) 
    
    
timeSeriesDat = pd.DataFrame(np.stack(midfoot_Sagittal))
outputDat = pd.concat([infoDat, timeSeriesDat], axis = 1)
outfileName = fPath + 'midfoot_Sagittal.csv'

if os.path.exists(outfileName) == False:
    
    outputDat.to_csv(outfileName, mode='a', header=True, index = False)

else:
    outputDat.to_csv(outfileName, mode='a', header=False, index = False) 
    
    
timeSeriesDat = pd.DataFrame(np.stack(midfoot_Frontal))
outputDat = pd.concat([infoDat, timeSeriesDat], axis = 1)
outfileName = fPath + 'midfoot_Frontal.csv'

if os.path.exists(outfileName) == False:
    
    outputDat.to_csv(outfileName, mode='a', header=True, index = False)

else:
    outputDat.to_csv(outfileName, mode='a', header=False, index = False) 
    
    
timeSeriesDat = pd.DataFrame(np.stack(midfoot_Transverse))
outputDat = pd.concat([infoDat, timeSeriesDat], axis = 1)
outfileName = fPath + 'midfoot_Transverse.csv'

if os.path.exists(outfileName) == False:
    
    outputDat.to_csv(outfileName, mode='a', header=True, index = False)

else:
    outputDat.to_csv(outfileName, mode='a', header=False, index = False) 
    

# timeSeriesDat = pd.DataFrame(np.stack(toe_Sagittal))
# outputDat = pd.concat([infoDat, timeSeriesDat], axis = 1)
# outfileName = fPath + 'toe_Sagittal.csv'

# if os.path.exists(outfileName) == False:
    
#     outputDat.to_csv(outfileName, mode='a', header=True, index = False)

# else:
#     outputDat.to_csv(outfileName, mode='a', header=False, index = False) 
    
    
# timeSeriesDat = pd.DataFrame(np.stack(toe_Valgus))
# outputDat = pd.concat([infoDat, timeSeriesDat], axis = 1)
# outfileName = fPath + 'toe_Valgus.csv'

# if os.path.exists(outfileName) == False:
    
#     outputDat.to_csv(outfileName, mode='a', header=True, index = False)

# else:
#     outputDat.to_csv(outfileName, mode='a', header=False, index = False) 