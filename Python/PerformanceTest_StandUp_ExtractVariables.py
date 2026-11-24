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
import tkinter as tk
from tkinter import messagebox
from OvergroundFunctions import (findLandings, loadProcessingDecisions,
                                 saveProcessingDecision)

# Define constants and options
save_on = 1 #will write to spreadsheet if 1 entered
# 0 = no data check, nothing is asked or recorded
# 1 = ask only about trials with no recorded decision (the normal setting)
# 2 = re-review EVERY trial, including ones previously rejected. Use after
#     changing processing, when earlier decisions may no longer hold. This
#     mode is good for reruning files with a different threshold or examining
#     files after a different filter has been applied.
data_check = 1
fThresh = 50

# Read in balance file
fPath = 'C:\\Users\\milena.singletary\\OneDrive - BOA Technology Inc\\General - PFL Team\\Testing Segments\\WorkWear_Performance\\2025_Performance_HighCutPFSWorwearII_TimberlandPro\\overground\\'

fileExt = r".txt"

# Only extract entries with "SU": Stand Ups
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt) and fName.count('SU') and not fName.startswith('0_')]

# Names this script's decision file, 0_ProcessingDecisions_<scriptName>.csv.
# One data folder is often read by several scripts, and a trial that is no
# good for one analysis can be fine for another, so each keeps its own
# record rather than one script's rejection governing the rest.
scriptName = 'StandUp'

# Data-quality decisions recorded by previous runs of this script. Loading
# these is what stops a trial being judged twice. Rejected files are left
# where they are so they can still be opened and looked at - it is this
# record, not the folder, that decides what gets processed.
decisions = loadProcessingDecisions(fPath, scriptName)

# Results from an out-of-date copy of this script will not match anyone
# else's. Asked only when nothing has been decided here yet: a decision file
# means the question was answered on an earlier run of this dataset.
if len(decisions) == 0:
    # Give this dialog its own window and put it in front. It is the first
    # thing the script does, so unlike the data check further down there is no
    # figure on screen to pull focus, and a borrowed default root can open the
    # box behind Spyder - which just looks like the script has hung.
    dialogRoot = tk.Tk()
    dialogRoot.withdraw()
    dialogRoot.attributes('-topmost', True)
    upToDate = messagebox.askyesno("Question", "Is this script up to date with main?",
                                   parent = dialogRoot)
    dialogRoot.destroy()
    # A plain error rather than SystemExit: these scripts get run a cell at a
    # time, and SystemExit can take the console with it. This stops just as
    # firmly, prints the reason, and leaves the console alone.
    if upToDate == False:
        raise RuntimeError('Pull this script from main before processing')

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
order = []

# loop through all of the files
for ii in range(0,len(entries)):
    # Pull the data for examination
    fName = entries[ii]
    print(fName)
    # A trial rejected in a previous run is skipped. The file is still
    # there to open and look at: the recorded decision governs, not the
    # folder
    priorDecision = decisions.get(fName, '')
    if priorDecision == 'bad' and data_check != 2:
        print('Previously excluded, skipping: ' + fName)
        continue
    dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)

    # The collection frequency comes from the file header rather than
    # being assumed. Line 4 of the export reads "200.000 // Sampling
    # rate"; skiprows=[2] drops the source-file line, which carries four
    # fields rather than two, and the blank line is skipped by pandas.
    descr = pd.read_csv(fPath + fName, sep = '\t', nrows = 5, header = None,
                        skiprows = [2])
    frequency = float(descr.iloc[2, 0])
    
    tmpSub = fName.split(sep = "_")[0]
    tmpConfig = fName.split(sep = "_")[1]
    tmpMove = fName.split(sep = "_")[2] 
    tmpOrd = fName.split(sep = "_")[3][0] 
    
    # Segment the trial: sometimes people did not go right into the trial
    shortFName = fName.split('.')[0]
    # Load in the trial segmentation variable if it is in the directory
    if os.path.exists(fPath+shortFName+'TrialSeg.npy') == True:
        trial_segment_old = np.load(fPath+shortFName+'TrialSeg.npy',allow_pickle=True)
        trialStart = trial_segment_old[1]
        trialEnd = trial_segment_old[2]
        dat = dat.iloc[int(trialStart) : int(trialEnd),:]
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
        # trial_segment = np.array([shortFName,pts])
        trial_segment = np.array([shortFName,round(pts[0,1]),round(pts[1,0])])
        np.save(fPath+shortFName+'TrialSeg.npy',trial_segment)
    
     
    # Detect foot contact onto FP3
    FC_sig = np.array(dat.FP3_GRF_Z)
    w = 1 / (frequency / 2) # Normalize the frequency
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
        
        answer = True # if data check is off.
        if priorDecision == 'good' and data_check == 1:
            print('Previously accepted, not asking again: ' + fName)
        elif data_check >= 1:
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

        # Record the decision straight away, inside the loop, so a run that
        # fails later keeps every decision made so far
        if priorDecision == '' or data_check == 2:
            if answer == False:
                saveProcessingDecision(fPath, scriptName, fName, 'bad',
                                       Subject=tmpSub, Config=tmpConfig,
                                       reason='rejected at the data check')
            else:
                saveProcessingDecision(fPath, scriptName, fName, 'good',
                                       Subject=tmpSub, Config=tmpConfig)

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
                RFD.append(np.max(np.gradient(dat.FP2_GRF_Z[landing : left_on[jj+1]],1/frequency)))
                # Time to go from standing to the next standing position
                cycle_time.append((left_on[jj+1]-landing)/frequency)
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
                    RankleEvMom.append(min(dat.RAnkleMoment_Frontal[landing : left_on[jj+1]]))
                    RankleInMom.append(max(dat.RAnkleMoment_Frontal[landing : left_on[jj+1]]))
                else:
                    RankleEvMom.append(np.nan)
                    RankleInMom.append(np.nan)
                
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
                order.append(tmpOrd)


outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Order':list(order),'Movement':list(movements),
                         'cycle_time':list(cycle_time),'PeakPosCOMPower':list(PeakPosCOMPower),
                         'PeakNegCOMPower':list(PeakNegCOMPower),'RFD':list(RFD),'COPEx':list(COPEx),
                         'sdCOP_AP':list(sdCOP_AP),'sdCOP_ML':list(sdCOP_ML),'forcemaxCV':list(forcemaxCV),
                         'RkneeABDMom':list(RkneeABDMom),'RkneeADDMom':list(RkneeADDMom),'RankleEvMom':list(RankleEvMom),
                         'RankleInMom':list(RankleInMom)})

if save_on == 1 and data_check < 2:
    # Note: written fresh each run, never appended. Appending duplicates
    # every row when a study is re-processed after more data is collected.
    outcomes.to_csv(fPath + '0_StandUp.csv',header=True,index=False)                    
    
    