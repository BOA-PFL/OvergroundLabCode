# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 13:55:28 2020

@author: Daniel.Feeney
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.signal as sig
import tkinter as tk
from tkinter import messagebox
from OvergroundFunctions import (findLandings, movAvgForce, movSDForce,
                                 findBW, findStabilization,
                                 loadProcessingDecisions, saveProcessingDecision)


# Define constants and options
fThresh = 40 #below this value will be set to 0.
save_on = 1 #will write to spreadsheet if 1 entered
# 0 = no data check, nothing is asked or recorded
# 1 = ask only about trials with no recorded decision (the normal setting)
# 2 = re-review EVERY trial, including ones previously rejected. Use after
#     changing processing, when earlier decisions may no longer hold. This
#     mode is good for reruning files with a different threshold or examining
#     files after a different filter has been applied.
data_check = 1

# Read in balance file
fPath = 'Z:\\Testing Segments\\WorkWear_Performance\\EH_Workwear_MidCutStabilityI_CPDMech_June23\\Overground\\'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt) and fName.count('SLL') and not fName.startswith('0_')]

# Names this script's decision file, 0_ProcessingDecisions_<scriptName>.csv.
# One data folder is often read by several scripts, and a trial that is no
# good for one analysis can be fine for another, so each keeps its own
# record rather than one script's rejection governing the rest.
scriptName = 'SingleLegLanding_V3'

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


# list of functions 


#Moving average of length specified in function

#moving SD as calcualted above

#estimated stability after 200 indices

   


## Preallocation
stabilization = []
sdFz = []
subName = []
movements = []
tmpConfig = []
order = []
badFileList = []

RankleEvMom = []
RankleInMom = []

RkneeABDMom = []
RkneeADDMom = []
RkneeAbAdROM = []

for fName in entries:
    # try:
        """
        loop through the selected files and obtain values for stabilization time
        Start by looping through files and getting meta data
        Then loop through landings on the force plate for stabilization time
        """
        # Clear the previous trial's cyclic detections. They are assigned
        # inside conditionals, so a trial that skips a detection would keep
        # the last trial's events and be processed against them silently.
        landings = []

        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        print('Processing:',fName)

        # The collection frequency comes from the file header rather than
        # being assumed. Line 4 of the export reads "200.000 // Sampling
        # rate"; skiprows=[2] drops the source-file line, which carries four
        # fields rather than two, and the blank line is skipped by pandas.
        descr = pd.read_csv(fPath + fName, sep = '\t', nrows = 5, header = None,
                            skiprows = [2])
        frequency = float(descr.iloc[2, 0])

        
        ##Parse file name into subject and configuration 
        config = fName.split(sep = "_")[1]
        tmpMove = fName.split(sep = "_")[2] 
        forder = fName.split(sep = "_")[3][0]
        # Filter force
        forceZ = np.array(dat.FP4_GRF_Z)
        forceZ[forceZ<fThresh] = 0 
        
        ## find the landings and offs of the FP as vectors
        # Single-leg landings are discrete, so the strict detection
        # applies: 300 N still present ten samples on, and no second
        # landing inside 300 samples
        landings = findLandings(forceZ, fThresh, confirmForce = 300, minGap = 300)

        
        # A trial rejected in a previous run is skipped. The file is still
        # there to open and look at: the recorded decision governs, not the
        # folder
        priorDecision = decisions.get(fName, '')
        if priorDecision == 'bad' and data_check != 2:
            print('Previously excluded, skipping: ' + fName)
            continue

        ## For each landing, calculate rolling averages and time to stabilize
        answer = True # if data check is off.
        if priorDecision == 'good' and data_check == 1:
            print('Previously accepted, not asking again: ' + fName)
        elif data_check >= 1:
            plt.figure(1010)
            plt.subplot(2,2,1)
            plt.plot(forceZ)
            plt.ylabel('Force (N)')
            plt.title('Vertical Force')
            plt.subplot(2,2,2)
            plt.plot(dat.RAnkleMoment_Frontal)
            plt.ylabel('Moment (Nm)')
            plt.title('Ankle In/Ev Moment')
            plt.ylim([-200,200])
            plt.subplot(2,2,3)
            plt.plot(dat.RKneeMoment_Sagittal)
            plt.ylabel('Moment (Nm)')
            plt.title('Knee Flex/Ex Moment')
            plt.ylim([-200,200])
            plt.subplot(2,2,4)
            plt.plot(dat.RKneeMoment_Frontal)
            plt.ylim([-200,200])
            plt.ylabel('Moment (Nm)')
            plt.title('Knee AB/AD Moment')
            
            answer = messagebox.askyesno("Question","Is data clean?")
            plt.close('all')

        # Record the decision straight away, inside the loop, so a run that
        # fails later keeps every decision made so far
        if priorDecision == '' or data_check == 2:
            tmpName = fName.split(sep = "_")[0]
            if answer == False:
                saveProcessingDecision(fPath, scriptName, fName, 'bad',
                                       Subject=tmpName, Config=config,
                                       reason='rejected at the data check')
            else:
                saveProcessingDecision(fPath, scriptName, fName, 'good',
                                       Subject=tmpName, Config=config)

        if answer == False:
            print('Adding file to bad file list')
            badFileList.append(fName)
        
        if answer == True:
            plt.close('all')
            print('Estimating point estimates')
        
            for landing in landings:
                try:
                    
                    sdFz.append(np.std(forceZ[landing + 100 : landing + 400]))
                    avgF = movAvgForce(forceZ, landing, landing + 200, 10)
                    sdF = movSDForce(forceZ, landing, landing + 200, 10)
                    subBW = findBW(avgF)
                    
                    try:
                        stabilization.append(findStabilization(avgF, sdF, subBW)/frequency)
                    except:
                        stabilization.append('NaN')
                    #tmpStab = findStabilization(avgF, sdF)
                    movements.append(tmpMove)
                    subName.append(fName.split(sep = "_")[0])
                    tmpConfig.append(config)
                    order.append(forder)
                   
                    ###   ---- Pk Moments ---- ##
                    if np.isnan(sum(dat.RKneeMoment_Frontal[landing : landing + 200])):
                        RankleInMom.append(np.nan)
                        RankleEvMom.append(np.nan)
                    else:
                        RankleInMom.append(max(dat.RAnkleMoment_Frontal[landing : landing + 200]))
                        RankleEvMom.append(min(dat.RAnkleMoment_Frontal[landing : landing + 200]))
                   
                    if np.isnan(sum(dat.RKneeMoment_Frontal[landing : landing + 200])):
                        RkneeABDMom.append(np.nan)
                        RkneeADDMom.append(np.nan)
                    else:
                        RkneeABDMom.append(min(dat.RKneeMoment_Frontal[landing : landing + 200]))
                        RkneeADDMom.append(max(dat.RKneeMoment_Frontal[landing : landing + 200]))
                        
                    if np.isnan(sum(dat.RKneeAngle_Frontal[landing : landing + 200])):
                        RkneeAbAdROM.append(np.nan)
                    else:
                        RkneeAbAdROM.append(max(dat.RKneeAngle_Frontal[landing : landing + 200]) - min(dat.RKneeAngle_Frontal[landing : landing + 200]))

               
                   
                    
                    
                except:
                    print(landing, fName)
           

 



outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(tmpConfig), 'Order': list(order), 'Movement':list(movements), 'StabTime': list(stabilization), 'sdFz':list(sdFz),
                          'RankleEvMom':list(RankleEvMom), 'RankleInMom':list(RankleInMom),  'RkneeADDMom': list(RkneeADDMom), 
                          'RkneeABDMom':list(RkneeABDMom), 'RkneeAbAdROM':list(RkneeAbAdROM)})


if save_on == 1 and data_check < 2:
    # Note: written fresh each run, never appended. Appending duplicates
    # every row when a study is re-processed after more data is collected.
    outcomes.to_csv(fPath + '0_OGStabilization.csv',header=True,index=False) 


