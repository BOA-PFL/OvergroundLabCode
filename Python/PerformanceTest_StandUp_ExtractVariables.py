# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 14:38:22 2023

@author: Eric.Honert
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.signal as sig
from tkinter import messagebox

# Define constants and options
save_on = 1 #will write to spreadsheet if 1 entered
debug = 0
fThresh = 50

# Read in balance file
fPath = 'Z:\\Testing Segments\\WorkWear_Performance\\EH_Workwear_MidCutStabilityII_CPDMech_Sept23\\Overground\\'

fileExt = r".txt"

# Only extract entries with "SU": Stand Ups
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt) and fName.count('SU')]

### set plot font size ###
SMALL_SIZE = 14
MEDIUM_SIZE = 16
BIGGER_SIZE = 18

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

# List of functions
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
            if force[step] == 0 and force[step + 1] >= fThresh :
                lic.append(step)
    return lic

cycle_time = []
RkneeABDMom = []
RkneeADDMom = []
RankleEvMom = []
RankleInMom = []
RFD = []
PeakPosCOMPower = []
PeakNegCOMPower = []
COPEx = []
sdCOP_AP = []
sdCOP_ML = []
forcemaxCV = []




badFileList = []

subName = []
config = []
movements = []

# loop through all of the files
for ii in range(0,len(entries)):
    # Pull the data for examination
    fName = entries[ii]
    print(fName)
    dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
    
    tmpSub = fName.split(sep = "_")[0]
    tmpConfig = fName.split(sep = "_")[1]
    tmpMove = fName.split(sep = "_")[2] 
    
    # Segment the trial: sometimes people did not go right into the trial
    shortFName = fName.split('.')[0]
    # Load in the trial segmentation variable if it is in the directory
    if os.path.exists(fPath+shortFName+'TrialSeg.npy') == True:
        trial_segment_old = np.load(fPath+shortFName+'TrialSeg.npy',allow_pickle=True)
        trialStart = trial_segment_old[0][0]
        trialEnd = trial_segment_old[1][0]
        dat = dat.iloc[int(np.floor(trialStart)) : int(np.floor(trialEnd)),:]
        dat = dat.reset_index()
    else:
            
        ### Subset the trial to a portion that does not include standing ###
        fig, ax = plt.subplots()
        ax.plot(dat.FP2_GRF_Z, label = 'FP2: Right Foot')
        ax.plot(dat.FP3_GRF_Z, label = 'FP3: Left Foot')
        fig.legend()
        print('Select start and end of analysis trial')
        pts = np.asarray(plt.ginput(2, timeout=-1))
        plt.close()
        # downselect the region of the dataframe you selected from above 
        dat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
        dat = dat.reset_index()
        # Save the trial segmentation
        trial_segment = np.array([shortFName,pts])
        np.save(fPath+shortFName+'TrialSeg.npy',trial_segment)
    
     
    # Detect foot contact onto FP3
    FC_sig = np.array(dat.FP3_GRF_Z)
    freq = 200
    w = 1 / (freq / 2) # Normalize the frequency
    b, a = sig.butter(2, w, 'low')
    FC_sig = sig.filtfilt(b, a, FC_sig)
    FC_sig[FC_sig<fThresh] = 0
    left_on = []
    left_on = findLandings(FC_sig, fThresh)
        
    # Some subjects put the weight on the forceplate, remove false detections
    if len(left_on) > 10:
        left_on = left_on[::2]
    
    if len(left_on) > 2:
        # Evaluate if there is enough stand ups that have good knee tracking
        knee_count = 0
        dum = []
        for jj, landing in enumerate(left_on[:-1]):
            if np.isnan(sum(dat.RKneeMoment_Frontal[landing : left_on[jj+1]])) == False:
                knee_count = knee_count + 1
                dum.extend(dat.RKneeMoment_Frontal[landing : left_on[jj+1]])
        
        answer = True # Defaulting to true: In case "debug" is not used
        if debug == 1:
           plt.figure(ii)
           plt.subplot(2,2,1)
           # plt.plot(dum)
           plt.plot(dat.RKneeMoment_Frontal)
           plt.ylabel('Good Knee ADD/ABD Moment')
           plt.subplot(2,2,2)
           plt.plot(dat.FP2_GRF_Z)
           plt.ylabel('Vertical GRF')
           plt.subplot(2,2,3)
           plt.plot(dat.COM_Power)
           plt.ylabel('COM Power')
           plt.subplot(2,2,4)
           plt.plot(dat.FP2_COP_X,dat.FP2_COP_Y)
           plt.xlabel('AP')
           plt.ylabel('ML')
           answer = messagebox.askyesno("Question","Is data clean?")
           plt.close('all')
       
        if answer == False:
           print('Adding file to bad file list')
           badFileList.append(fName)
        
        if answer == True:
            # Compute a moving CV of the force magnitude
            Fmag = np.linalg.norm(np.array([dat.FP2_GRF_X,dat.FP2_GRF_Y,dat.FP2_GRF_Z]),axis=0)
            FmoveCV = np.zeros(len(Fmag))
            for ii in range(5,len(Fmag)-4):
                FmoveCV[ii] = np.std(Fmag[ii-5:ii+5])/np.mean(Fmag[ii-5:ii+5])
                
            
            for jj, landing in enumerate(left_on[:-1]):
                # COM Power
                PeakPosCOMPower.append(np.max(dat.COM_Power[landing : left_on[jj+1]]))
                PeakNegCOMPower.append(np.min(dat.COM_Power[landing : left_on[jj+1]]))
                # Rate of Force Development
                RFD.append(np.max(np.gradient(dat.FP2_GRF_Z[landing : left_on[jj+1]],1/200)))
                # Time to go from standing to the next standing position
                cycle_time.append((left_on[jj+1]-landing)/200)
                # Center-of-Pressure Metrics
                COP_ML_demean = np.array(dat.FP2_COP_Y[landing : left_on[jj+1]] - np.mean(dat.FP2_COP_Y[landing : left_on[jj+1]]))
                COP_AP_demean = np.array(dat.FP2_COP_X[landing : left_on[jj+1]] - np.mean(dat.FP2_COP_X[landing : left_on[jj+1]]))
                COP_mag_demean = np.linalg.norm(np.array([dat.FP2_COP_X[landing : left_on[jj+1]],dat.FP2_COP_Y[landing : left_on[jj+1]]]),axis=0)
                COP_mag_demean = COP_mag_demean-np.mean(COP_mag_demean)
                
                COPEx.append(max(COP_mag_demean)-min(COP_mag_demean))
                sdCOP_AP.append(np.std(COP_AP_demean))
                sdCOP_ML.append(np.std(COP_ML_demean))
                
                # Maximum force variability
                forcemaxCV.append(max(FmoveCV[landing : left_on[jj+1]]))
                
                # Ankle Eversion/Inversion Moment
                if np.isnan(sum(dat.RAnkleMoment_Frontal[landing : left_on[jj+1]])) == False and knee_count > 2:
                    RankleEvMom.append(min(dat.RKneeMoment_Frontal[landing : left_on[jj+1]]))
                    RankleInMom.append(max(dat.RKneeMoment_Frontal[landing : left_on[jj+1]]))
                else:
                    RankleEvMom.append(np.nan)
                
                # Knee ABD Moment
                if np.isnan(sum(dat.RKneeMoment_Frontal[landing : left_on[jj+1]])) == False and knee_count > 2:
                    RkneeABDMom.append(min(dat.RKneeMoment_Frontal[landing : left_on[jj+1]]))
                    RkneeADDMom.append(max(dat.RKneeMoment_Frontal[landing : left_on[jj+1]]))
                else:
                    RkneeABDMom.append(np.nan)
                    RkneeADDMom.append(np.nan)
                
                # Append trial information
                subName.append(tmpSub)
                config.append(tmpConfig)
                movements.append(tmpMove)
                


outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config),'Movement':list(movements),
                         'cycle_time':list(cycle_time),'PeakPosCOMPower':list(PeakPosCOMPower),
                         'PeakNegCOMPower':list(PeakNegCOMPower),'RFD':list(RFD),'COPEx':list(COPEx),
                         'sdCOP_AP':list(sdCOP_AP),'sdCOP_ML':list(sdCOP_ML),'forcemaxCV':list(forcemaxCV),
                         'RkneeABDMom':list(RkneeABDMom),'RkneeADDMom':list(RkneeADDMom),'RankleEvMom':list(RankleEvMom),
                         'RankleInMom':list(RankleInMom)})

if save_on == 1:
    outcomes.to_csv(fPath + '0_StandUp.csv',header=True,index=False)                    
    
    