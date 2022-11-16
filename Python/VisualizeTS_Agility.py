# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 13:36:58 2022

Visualizing time series plots of common varibales for agility data

@author: Dan.Feeney
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import messagebox
from dataclasses import dataclass

### main inputs ###

# select files

fPath = 'C:\\Users\\adam.luftglass\\OneDrive - Boa Technology Inc\\General\\Testing Segments\\AgilityPerformanceData\\CPD_TongueLocatedDial_Oct2022\\Overground\\'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]
entries = os.listdir(fPath)

# Choose two files to compare averaged for data 
fName1 = entries[1]
fName2 = entries[8]
fThresh = 40

stepLen = 150 #this is how far forward you will look to average data
x = np.linspace(0,stepLen,stepLen)

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

pd.options.mode.chained_assignment = None  # default='warn' set to warn for a lot of warnings

#############################################################################
# Functions and classes #
# instantiate a dataclass to be used below

@dataclass
class JumpStarts:
    movement: str
    config: str
    landings: list
    takeoffs: list
    df: pd.DataFrame

@dataclass
class EnsembleData:
    meanData: np.ndarray
    sdData: np.ndarray
    
    
# preallocate matrix for force and fill in with force data
def forceMatrix(inputForce, landings, noSteps, stepLength):
    """
    input a force signal, return matrix with n rows (for each landing) by m col
    #for each point in stepLen
    """
    preForce = np.zeros((noSteps,stepLength))
    
    for iterVar, landing in enumerate(landings):
        try:
            preForce[iterVar,] = inputForce[landing:landing+stepLength]
        except:
            print(landing)
            
    return preForce


def calcEnsembleData(Force, TurnStarts, stepLength):
    """ 
    Calculates ensemble averaged force and SD data from a time series
    """
    rightForceMat = forceMatrix(Force, TurnStarts, len(TurnStarts), stepLength)
    meanRightForce = np.mean(rightForceMat, axis = 0)
    sdRightForce = np.std(rightForceMat, axis = 0)
    
    result = EnsembleData(meanRightForce, sdRightForce)
    
    return(result)

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


def findTakeoffs(force, fThresh):
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

    # """
    lto = []
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0 :
            lto.append(step + 1)
    return lto 

def delimitTrial(inputDF):
    """
     This function uses ginput to delimit the start and end of a trial
    You will need to indicate on the plot when to start/end the trial. 
    You must use tkinter or plotting outside the console to use this function
    Parameters
    ----------
    inputDF : Pandas DataFrame
        DF containing all desired output variables.
    zForce : numpy array 
        of force data from which we will subset the dataframe

    Returns
    -------
    outputDat: dataframe subset to the beginning and end of jumps.

    """

    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    totForce = inputDF.FP1_GRF_Z + inputDF.FP2_GRF_Z + inputDF.FP3_GRF_Z + inputDF.FP4_GRF_Z
    print('Select a point on the plot to represent the beginning & end of trial where Y-value is near 0')
    ax.plot(totForce, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = inputDF.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)


def makeVizPlot(inputDF, inputLandings, inputTakeoffs):
    
    """
    Parameters
    ----------
    inputDF : Pandas DF
        Standard Agility export in dataframe.
    inputLandings : list
        list of landings from findLandings function.
    inputTakeoffs : list
        list of takeoffs from findTakeoffs function.

    Returns
    -------
    No variables; just a plot to inspect for clean kinematic/kinetic data.

    """
    fig, (ax, ax1) = plt.subplots(1,2)
    ax.plot(inputDF.RAnkleAngle_Sagittal[inputLandings[1]:inputTakeoffs[5]], label = 'Right Sagittal')
    ax.plot(inputDF.LAnkleAngle_Sagittal[inputLandings[1]:inputTakeoffs[5]], label = 'Left Sagittal')
    ax.plot(inputDF.RAnkleAngle_Frontal[inputLandings[1]:inputTakeoffs[5]], label = 'Right Frontal')
    ax.plot(inputDF.LAnkleAngle_Frontal[inputLandings[1]:inputTakeoffs[5]], label = 'Left Frontal')
    ax.vlines(x = inputLandings[1:5], ymin = 0, ymax = np.max(inputDF.RAnkleAngle_Sagittal[inputLandings[0]:inputTakeoffs[3]]),
       color = 'coral', label = 'Landings',linewidth=3.0, ls='--')
    ax.vlines(x = inputTakeoffs[1:5], ymin = 0, ymax = np.max(inputDF.RAnkleAngle_Sagittal[inputLandings[0]:inputTakeoffs[3]]),
       color = 'cyan', label = 'Takeoffs',linewidth=3.0, ls='--')
    ax.set_xlabel('Indices')
    ax.set_title('Ankle')
    ax.set_ylabel('Angle (Deg)')
    ax.legend(bbox_to_anchor =(0.5,-0.27), loc='lower center')
    ax1.plot(inputDF.RKneeAngle_Frontal[inputLandings[1]:inputTakeoffs[5]], label = 'Right Frontal')
    ax1.plot(inputDF.LKneeAngle_Frontal[inputLandings[1]:inputTakeoffs[5]], label = 'Left Frontal')
    ax1.vlines(x = inputLandings[1:5], ymin = 0, ymax = np.max(inputDF.RKneeAngle_Frontal[inputLandings[0]:inputTakeoffs[3]]),
       color = 'coral', label = 'Landings',linewidth=3.0, ls='--')
    ax1.vlines(x = inputTakeoffs[1:5], ymin = 0, ymax = np.max(inputDF.RKneeAngle_Frontal[inputLandings[0]:inputTakeoffs[3]]),
       color = 'cyan', label = 'Takeoffs',linewidth=3.0, ls='--')
    ax1.set_xlabel('Indices') 
    ax1.set_title('Knee')
    ax1.set_ylabel('Angle (Deg)')
    plt.tight_layout()
    ax1.legend(bbox_to_anchor =(0.5,-0.27), loc='lower center')
    plt.show()
    
    fig2, (ax3, ax4) = plt.subplots(1,2)
    ax3.plot(inputDF.RAnkleMoment_Sagittal[inputLandings[1]:inputTakeoffs[5]], label = 'Right Sagittal')
    ax3.plot(inputDF.LAnkleMoment_Sagittal[inputLandings[1]:inputTakeoffs[5]], label = 'Left Sagittal')
    ax3.plot(inputDF.RAnkleMoment_Frontal[inputLandings[1]:inputTakeoffs[5]], label = 'Right Frontal ')
    ax3.plot(inputDF.LAnkleMoment_Frontal[inputLandings[1]:inputTakeoffs[5]], label = 'Left Frontal ')
    ax3.vlines(x = inputLandings[1:5], ymin = 0, ymax = np.nanmax(inputDF.RAnkleMoment_Frontal[inputLandings[0]:inputTakeoffs[3]]),
       color = 'coral', label = 'Landings',linewidth=3.0, ls='--')
    ax3.vlines(x = inputTakeoffs[1:5], ymin = 0, ymax = np.nanmax(inputDF.RAnkleMoment_Frontal[inputLandings[0]:inputTakeoffs[3]]),
       color = 'cyan', label = 'Takeoffs',linewidth=3.0, ls='--')
    ax3.set_xlabel('Indices')
    ax3.set_title('Ankle')
    ax3.set_ylabel('Moment (Nm)')
    ax3.legend(bbox_to_anchor =(0.5,-0.27), loc='lower center')
    ax4.plot(inputDF.RKneeMoment_Sagittal[inputLandings[1]:inputTakeoffs[5]], label = 'Right Sagittal')
    ax4.plot(inputDF.LKneeMoment_Sagittal[inputLandings[1]:inputTakeoffs[5]], label = 'Left Sagittal')
    ax4.set_xlabel('Indices')
    ax4.set_title('Knee')
    ax4.set_ylabel('Moment (Nm)')
    plt.tight_layout()
    ax4.legend(bbox_to_anchor =(0.5,-0.27), loc='lower center')
    ax4.vlines(x = inputLandings[1:5], ymin = 0, ymax = np.max(inputDF.RKneeMoment_Sagittal[inputLandings[0]:inputTakeoffs[3]]),
       color = 'coral', label = 'Landings',linewidth=3.0, ls='--')
    ax4.vlines(x = inputTakeoffs[1:5], ymin = 0, ymax = np.max(inputDF.RKneeMoment_Sagittal[inputLandings[0]:inputTakeoffs[3]]),
       color = 'cyan', label = 'Takeoffs',linewidth=3.0, ls='--')
    plt.show()

def calcFullTrialStarts(fileName, filePath):
    
    fName = fileName
    fPath = filePath
    
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
    
            XForce = dat.FP3_GRF_X
            
        else:
            ZForce = dat.FP4_GRF_Z
            XForce = dat.FP4_GRF_X 
    
        if abs(np.min(XForce)) > abs(np.max(XForce)):
            XForce = XForce * -1
        
        #dat = delimitTrialSkate(dat)
        ZForce[ZForce<fThresh] = 0
        
        
        #find the landings from function above
        landings = findLandings(ZForce, fThresh)
        takeoffs = findTakeoffs(ZForce, fThresh)
        
        landings[:] = [x for x in landings if x < takeoffs[-1]]
        takeoffs[:] = [x for x in takeoffs if x > landings[0]]
        
     
    elif (tmpMove == 'CMJ') or (tmpMove == 'cmj'):
        
        dat = delimitTrial(dat)
        
        ZForce = dat.FP2_GRF_Z
        ZForce[ZForce<fThresh] = 0
        
        XForce = dat.FP2_GRF_X 
      
        landings = findLandings(ZForce, fThresh)
        takeoffs = findTakeoffs(ZForce, fThresh)
      
        landings[:] = [x for x in landings if x < takeoffs[-1]]
        takeoffs[:] = [x for x in takeoffs if x > landings[0]] 
         
    else:
        print('this movement is not included in Performance Test Analysis')
    
    if (tmpMove == 'CMJ') or (tmpMove == 'cmj') or (tmpMove == 'Skater') or (tmpMove == 'skater'):
        makeVizPlot(dat, landings, takeoffs)
        answer = messagebox.askyesno("Question","Is data clean?")
        
        if answer == False:
            plt.close('all')
            print('Adding file to bad file list')
        
        if answer == True:
            plt.close('all')
            print('Moving onto plotting')


    result = JumpStarts(tmpMove, config1, landings, takeoffs, dat)
               
    return(result)

trial1 = calcFullTrialStarts(fName1, fPath)
trial2 = calcFullTrialStarts(fName2, fPath)

### calculating ensemble mean and SD ###

## Calculating averaged data ## 
## need to fix function to calculate right value for the given movement ##
forcesTrial1 = calcEnsembleData(trial1.df.FP2_GRF_Z, trial1.landings, stepLen)
forcesTrial2 = calcEnsembleData(trial2.df.FP2_GRF_Z, trial2.landings, stepLen)

momTrial1 = calcEnsembleData(trial1.df.RAnkleMoment_Frontal, trial1.landings, stepLen)
momTrial2 = calcEnsembleData(trial2.df.RAnkleMoment_Frontal, trial2.landings, stepLen)
#COMPowerTrial1 = calcEnsembleData(trial1.df.COMPower, trial1.landings, stepLen)
sagmomTrial1 = calcEnsembleData(trial1.df.RAnkleMoment_Sagittal, trial1.landings, stepLen)
sagmomTrial2 = calcEnsembleData(trial2.df.RAnkleMoment_Sagittal, trial1.landings, stepLen)

### plotting ###
fig, (ax1, ax2) = plt.subplots(2)
ax1.plot(x, forcesTrial1.meanData, 'k', color='#DC582A')
ax1.fill_between(x,forcesTrial1.meanData-forcesTrial1.sdData, forcesTrial1.meanData+forcesTrial1.sdData,
    alpha=0.5, edgecolor='#DC582A', facecolor='#DC582A', label = trial1.config)
ax1.plot(x, forcesTrial2.meanData, 'k', color='#00966C')
ax1.fill_between(x,forcesTrial2.meanData-forcesTrial2.sdData, forcesTrial2.meanData+forcesTrial2.sdData,
    alpha=0.5, edgecolor='#00966C', facecolor='#00966C', label = trial2.config)
ax1.set_title('Vertical Forces')
ax1.set_ylabel('Force (N)')
ax1.legend()
ax2.plot(x, momTrial1.meanData, 'k', color='#DC582A')
ax2.fill_between(x,momTrial1.meanData-momTrial1.sdData, momTrial1.meanData+momTrial1.sdData,
    alpha=0.5, edgecolor='#DC582A', facecolor='#DC582A', label = trial1.config)
ax2.plot(x, momTrial2.meanData, 'k', color='#00966C')
ax2.fill_between(x,momTrial2.meanData-momTrial2.sdData, momTrial2.meanData+momTrial2.sdData,
    alpha=0.5, edgecolor='#00966C', facecolor='#00966C', label = trial2.config)
ax2.legend()
ax2.set_title('Frontal Moments')
ax2.set_ylabel('Moment (Nm)')
ax2.set_xlabel('Index')
plt.tight_layout()

fig, (ax3, ax4) = plt.subplots(2)
ax3.plot(x, forcesTrial1.meanData, 'k', color='#DC582A')
ax3.fill_between(x,forcesTrial1.meanData-forcesTrial1.sdData, forcesTrial1.meanData+forcesTrial1.sdData,
    alpha=0.5, edgecolor='#DC582A', facecolor='#DC582A', label = trial1.config)
ax3.plot(x, forcesTrial2.meanData, 'k', color='#00966C')
ax3.fill_between(x,forcesTrial2.meanData-forcesTrial2.sdData, forcesTrial2.meanData+forcesTrial2.sdData,
    alpha=0.5, edgecolor='#00966C', facecolor='#00966C', label = trial2.config)
ax3.set_title('Vertical Forces')
ax3.set_ylabel('Force (N)')
ax3.legend()
ax4.plot(x, sagmomTrial1.meanData, 'k', color='#DC582A')
ax4.fill_between(x,sagmomTrial1.meanData-sagmomTrial1.sdData, sagmomTrial1.meanData+sagmomTrial1.sdData,
    alpha=0.5, edgecolor='#DC582A', facecolor='#DC582A', label = trial1.config)
ax4.plot(x, sagmomTrial2.meanData, 'k', color='#00966C')
ax4.fill_between(x,sagmomTrial2.meanData-sagmomTrial2.sdData, sagmomTrial2.meanData+sagmomTrial2.sdData,
    alpha=0.5, edgecolor='#00966C', facecolor='#00966C', label = trial2.config)
ax4.legend()
ax4.set_title('Sagittal Moments')
ax4.set_ylabel('Moment (Nm)')
ax4.set_xlabel('Index')
plt.tight_layout()


def makecoolsagittalplots(forcedatas1, sagmomentdatas1, forcedatas2, sagmomentdatas2, trials1, trials2):
    fig, (ax5, ax6) = plt.subplots(2)
    ax5.plot(x, forcedatas1.meanData, 'k', color='#DC582A')
    ax5.fill_between(x,forcedatas1.meanData-forcedatas1.sdData, forcedatas1.meanData+forcedatas1.sdData,
        alpha=0.5, edgecolor='#DC582A', facecolor='#DC582A', label = trials1.config)
    ax5.plot(x, forcedatas2.meanData, 'k', color='#00966C')
    ax5.fill_between(x,forcedatas2.meanData-forcedatas2.sdData, forcesTrial2.meanData+forcedatas2.sdData,
        alpha=0.5, edgecolor='#00966C', facecolor='#00966C', label = trials2.config)
    ax5.set_title('Vertical Forces')
    ax5.set_ylabel('Force (N)')
    ax5.legend()
    ax6.plot(x, sagmomentdatas1.meanData, 'k', color='#DC582A')
    ax6.fill_between(x,sagmomentdatas1.meanData-sagmomentdatas1.sdData, sagmomentdatas1.meanData+sagmomentdatas1.sdData,
        alpha=0.5, edgecolor='#DC582A', facecolor='#DC582A', label = trials1.config)
    ax6.plot(x, sagmomentdatas2.meanData, 'k', color='#00966C')
    ax6.fill_between(x,sagmomentdatas2.meanData-sagmomentdatas2.sdData, sagmomentdatas2.meanData+sagmomentdatas2.sdData,
        alpha=0.5, edgecolor='#00966C', facecolor='#00966C', label = trials2.config)
    ax6.legend()
    ax6.set_title('Sagittal Moments')
    ax6.set_ylabel('Moment (Nm)')
    ax6.set_xlabel('Index')
    plt.tight_layout()
  
    
makecoolsagittalplots(forcesTrial1, sagmomTrial1, forcesTrial2, sagmomTrial2, trial1, trial2)
## TODO: extend plots to include:
### Make a new plot for Sagittal moments & COM power 
### Making plot a function that uses the same format
### Extend to skater jump for force plate swap
### Extend to a third model (afer the above 3 are done)