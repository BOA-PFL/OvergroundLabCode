# -*- coding: utf-8 -*-
"""
Created on Mon May 17 14:48:59 2021

Updating 11/7/22 to include data visualization plots to 'pass' or fail
and append the failing file names to a list while the passing ones write
results to a csv - DF

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import copy
from tkinter import messagebox

pd.options.mode.chained_assignment = None  # default='warn' set to warn for a lot of warnings

# Define constants and options
fThresh = 80 #below this force value will be set to 0.
save_on = 0 # turn this on for automatic saving of csv!!!! 
#fPath = 'C:\\Users\\daniel.feeney\\Boa Technology Inc\\PFL Team - General\\Testing Segments\AgilityPerformanceData\\CPD_TongueLocatedDial_Oct2022\\Overground\\'

fPath = 'C:/Users/Kate.Harrison/Boa Technology Inc/PFL Team - General/Testing Segments/AgilityPerformanceData/CPD_TongueLocatedDial_Oct2022/Overground/'

fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]

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
    
    # fig3, ax = plt.subplots(1,1)
    # ax.plot(dat.COM_Power)
    # ax.set_ylabel('Power (W)')
    # ax.set_title('COM Power')
    # plt.show()
    
#makeVizPlot(dat, landings, takeoffs)

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

impulse = []
jumpTime = []


subName = []
config = []
movements = []

badFileList = []

## save configuration names from files
for fName in entries:
    try:

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
                badFileList.append(fName)
            
            if answer == True:
                plt.close('all')
                print('Estimating point estimates')
                
                for i in range(len(landings)):
        
                    try:

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
        
                        print(fName + str(i))

    except:
        print(fName)





outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Movement':list(movements),
                         'CT':list(CT), 'impulse_Z':list(impulseZ), 'impulse_X':list(impulseX), 
                         'peakGRF_Z':list(peakGRFz), 'peakGRF_X':list(peakGRFx), 'peakPFmom':list(peakPFmom),
                         'peakINVmom':list(peakINVmom), 'peakKneeEXTmom':list(peakKneeEXTmom), 
                         'kneeABDrom':list(kneeABDrom), 'eccWork':list(eccWork), 'peakPower':list(peakPower) })

                       




if save_on == 1:
    outfileName = fPath + 'CompiledAgilityDataTest.csv'
    outcomes.to_csv(outfileName, index = False)





