# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 14:28:23 2023

@author: Kate.Harrison
"""

import sys
sys.tracebacklimit = 0

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.signal as sig
from scipy.signal import argrelextrema

pd.options.mode.chained_assignment = None  # default='warn' set to warn for a lot of warnings

# Define constants and options
fThresh = 80 #below this force value will be set to 0.
save_on = 0 # turn this on for automatic saving of csv!!!! 
#fPath = 'C:\\Users\\daniel.feeney\\Boa Technology Inc\\PFL Team - General\\Testing Segments\AgilityPerformanceData\\CPD_TongueLocatedDial_Oct2022\\Overground\\'

fPath = 'C:/Users/Kate.Harrison/Boa Technology Inc/PFL Team - General/Testing Segments/Helmets/HelmetPressureTest_Aug2023/TMM/'


fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]

### set plot font size ###
SMALL_SIZE = 14
MEDIUM_SIZE = 16
BIGGER_SIZE = 18

def delimitTrial(inputDF,FName):
    """
     This function uses ginput to delimit the start and end of a trial
    You will need to indicate on the plot when to start/end the trial. 
    You must use tkinter or plotting outside the console to use this function
    Parameters
    ----------
    inputDF : Pandas DataFrame
        DF containing all desired time series data.
    
    Returns
    -------
    outputDat: dataframe subset to the beginning and end of jumps.

    """
    #FName = entries[0]
    # generic function to plot and start/end trial #
    if os.path.exists(fPath+FName+'TrialSeg.npy'):
        trial_segment_old = np.load(fPath+FName+'TrialSeg.npy', allow_pickle =True)
        trialStart = trial_segment_old[1][0,0]
        trialEnd = trial_segment_old[1][1,0]
        inputDF = inputDF.iloc[int(np.floor(trialStart)) : int(np.floor(trialEnd)),:]
        outputDat = inputDF.reset_index()
        
    else: 
        fig, ax = plt.subplots()

        
        print('Select two points on the plot to represent the beginning & end of trial')


        ax.plot(inputDF.iloc[:,4], label = 'Helmet angle X')
        ax.plot(inputDF.iloc[:,5], label = 'Helmet angle Y')
        ax.plot(inputDF.iloc[:,6], label = 'Helmet angle Z')
        fig.legend()
        pts = np.asarray(plt.ginput(2, timeout=-1))
        plt.close()
        outputDat = inputDF.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
        outputDat = outputDat.reset_index()
        trial_segment = np.array([FName, pts], dtype = object)
        np.save(fPath+FName+'TrialSeg.npy',trial_segment)

    return(outputDat)

helmetAngle_X = []
helmetAngle_Y = []
helmetAngle_Z = []

subName = []
config = []
trial = []

for fName in entries:
    try:
        
       
        if 'tatic' in fName:
            
            #fName = entries[1]
            subTmp = fName.split('_')[0]
            configTmp = fName.split('_')[1]
            tmpMove = fName.split('_')[2]
            trialTmp = fName.split('_')[3].split(' ')[0]

            
            dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
            
            dat = delimitTrial(dat,fName) # use to eliminate any portion of the trial where the subject wasn't still or tracking was poor. 
            
            
            
            
             
            helmetAngle_X.append(np.nanmean(dat.iloc[:,4]))
            helmetAngle_Y.append(np.nanmean(dat.iloc[:,5]))
            helmetAngle_Z.append(np.nanmean(dat.iloc[:,6]))
        
            subName.append(subTmp)
            config.append(configTmp)
            trial.append(trialTmp)
        
        elif 'cmj' in fName or 'CMJ' in fName or 'skate' in fName or 'Skate' in fName:
            
            
            fName = entries[1]
            subTmp = fName.split('_')[0]
            configTmp = fName.split('_')[1]
            tmpMove = fName.split('_')[2]
            trialTmp = fName.split('_')[3].split(' ')[0]

            
            dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
            
            dat = delimitTrial(dat,fName) # use to select the portion of teh trial where teh head was shaking
            freq = 200
            cut = 10
            w = cut / (freq / 2) # Normalize the frequency
            b, a = sig.butter(2, w, 'low')
            # Filter the force signal
            x_filt = sig.filtfilt(b, a, dat.iloc[:,4])
            y_filt = sig.filtfilt(b, a, dat.iloc[:,5])
            z_filt = sig.filtfilt(b, a, dat.iloc[:,6])
            
            fig, ax = plt.subplots()


            ax.plot(x_filt, label = 'Helmet angle X')
            ax.plot(y_filt, label = 'Helmet angle Y')
            ax.plot(z_filt, label = 'Helmet angle Z')
            fig.legend()
            
            x_maxidx = argrelextrema(x_filt, np.greater)
            x_maxes = x_filt[x_maxidx]
            x_maxes = sorted(x_maxes, reverse = True)
            x_maxes = x_maxes[:8]
            
            y_maxidx = argrelextrema(y_filt, np.greater)
            y_maxes = y_filt[y_maxidx]
            y_maxes = sorted(y_maxes, reverse = True)
            y_maxes = y_maxes[:8]
            
            z_maxidx = argrelextrema(z_filt, np.greater)
            z_maxes = z_filt[z_maxidx]
            z_maxes = sorted(z_maxes, reverse = True)
            z_maxes = z_maxes[:8]
                
            x_minidx = argrelextrema(x_filt, np.less)
            x_mins = x_filt[x_minidx]
            x_mins = sorted(x_mins, reverse = True)
            x_mins = x_mins[:8]
                
            y_minidx = argrelextrema(y_filt, np.less)
            y_mins = y_filt[y_minidx]
            y_mins = sorted(y_mins, reverse = True)
            y_mins = y_mins[:8]
            
            z_minidx = argrelextrema(z_filt, np.less)
            z_mins = z_filt[z_minidx]
            z_mins = sorted(z_mins, reverse = True)
            z_mins = z_mins[:8]
                
            subName.extend([subTmp]* 8)
            
            
    except:
        print(fName)
        
        
        
outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Trial':list(trial),
                         'HelmetAngle_X':list(helmetAngle_X),
                         'HelmetAngle_Y': list(helmetAngle_Y),
                         'HelmetAngle_Z':list(helmetAngle_Z)})



                       



save_on = 1
if save_on == 1:
    outfileName = fPath + '0_CompiledHelmetStaticData.csv'
    outcomes.to_csv(outfileName, index = False)
