# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 13:15:08 2023

@author: Adam.Luftglass
"""

"""
This script compiles power and work data at the foot and ankle

Updating 11/7/22 to include data visualization plots to 'pass' or fail
and append the failing file names to a list while the passing ones write
results to a csv - DF

""" 

import sys
sys.tracebacklimit = 0

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import copy
from tkinter import messagebox
import scipy.signal as sig
from scipy.fft import fft, fftfreq
import scipy

pd.options.mode.chained_assignment = None  # default='warn' set to warn for a lot of warnings

# Define constants and options
fThresh = 80 #below this force value will be set to 0.
save_on = 0 # turn this on for automatic saving of csv!!!! #fPath = 'C:\\Users\\daniel.feeney\\Boa Technology Inc\\PFL Team - General\\Testing Segments\AgilityPerformanceData\\CPD_TongueLocatedDial_Oct2022\\Overground\\'

fPath = 'Z:\\Testing Segments\\Material Testing\\UpperStiffnessA&S_Performance_Jan2023\\Overground\\DistalFootWork\\'

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

def intp_strides(var,landing,TOs,GS):
    """
    Function to interpolate the variable of interest across a stride
    (from foot contact to subsiquent foot contact) in order to plot the
    variable of interest over top each other



   Parameters
    ----------
    var : list or numpy array
        Variable of interest. Can be taken from a dataframe or from a numpy array
    landings : list
        Foot contact indicies



   Returns
    -------
    intp_var : numpy array
        Interpolated variable to 101 points with the number of columns dictated
        by the number of strides.



   """
    # Preallocate
    intp_var = np.zeros((101,len(GS[:-1])))
    # Index through the strides
    for cc,ii in enumerate(GS[:-1]):
        dum = var[landing[ii]:TOs[ii]]
        f = scipy.interpolate.interp1d(np.arange(0,len(dum)),dum)
        intp_var[:,cc] = f(np.linspace(0,len(dum)-1,101))
        
    return intp_var

def delimitTrial(inputDF,FName):
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
    if os.path.exists(fPath+FName+'TrialSeg.npy'):
        trial_segment_old = np.load(fPath+FName+'TrialSeg.npy', allow_pickle =True)
        trialStart = trial_segment_old[1][0,0]
        trialEnd = trial_segment_old[1][1,0]
        inputDF = inputDF.iloc[int(np.floor(trialStart)) : int(np.floor(trialEnd)),:]
        outputDat = inputDF.reset_index()
        
    else: 
        fig, ax = plt.subplots()

        totForce = inputDF.FP1_GRF_Z + inputDF.FP2_GRF_Z + inputDF.FP3_GRF_Z + inputDF.FP4_GRF_Z
        print('Select a point on the plot to represent the beginning & end of trial where Y-value is near 0')


        ax.plot(totForce, label = 'Total Force')
        fig.legend()
        pts = np.asarray(plt.ginput(2, timeout=-1))
        plt.close()
        outputDat = inputDF.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
        outputDat = outputDat.reset_index()
        trial_segment = np.array([FName, pts])
        np.save(fPath+FName+'TrialSeg.npy',trial_segment)

    return(outputDat)


CT = []
GS = []

peakposRAnkPwr = []
RAnkposWork = []
RAnknegWork = []
peakposLAnkPwr = []
LAnkposWork = []
LAnknegWork = []

peaknegLAnkPwr = []
peaknegRAnkPwr = []

subName = []
config = []
movements = []

badFileList = []

peakNegRightFootPower = []
peakNegLeftFootPower = []
peakPosRightFootPower = []
peakPosLeftFootPower = []

LeftDistalRFnegWork = []
RightDistalRFnegWork = []
RightDistalRFposWork = []
LeftDistalRFposWork = []

## save configuration names from files
for fName in entries:
    try:
        
        #fName = entries[3]
        shortFName = fName.split('.')[0]
        config1 = fName.split('_')[1]
        tmpMove = fName.split('_')[2]

        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        dat = dat.fillna(0)
        
        
        landings = [] # erase landings and takeoffs from last loop
        takeoffs = []
        if (tmpMove == 'Skater') or (tmpMove == 'skater'):
            
            dat = delimitTrial(dat, shortFName)
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
            
            dat = delimitTrial(dat, shortFName)
            

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
            
                            
                for i in range(len(landings)):
        
                    try:

                  
                        if tmpMove == 'CMJ':
                            negLeftFootPower = copy.deepcopy(dat.LDistalFootPower_FP1)
                            negLeftFootPower[negLeftFootPower > 0] = 0
                            negRightFootPower = copy.deepcopy(dat.RDistalFootPower_FP2)
                            negRightFootPower[negRightFootPower > 0] = 0
                            posLeftFootPower = copy.deepcopy(dat.LDistalFootPower_FP1)
                            posLeftFootPower[posLeftFootPower < 0] = 0
                            posRightFootPower = copy.deepcopy(dat.RDistalFootPower_FP2)
                            posRightFootPower[posRightFootPower < 0] = 0
                            negLeftAnkPower = copy.deepcopy(dat.LeftAnklePower)
                            negLeftAnkPower[negLeftAnkPower > 0] = 0
                            negRightAnkPower = copy.deepcopy(dat.RightAnklePower)
                            negRightAnkPower[negRightAnkPower > 0] = 0
                            posLeftAnkPower = copy.deepcopy(dat.LeftAnklePower)
                            posLeftAnkPower[posLeftAnkPower < 0] = 0
                            posRightAnkPower = copy.deepcopy(dat.RightAnklePower)
                            posRightAnkPower[posRightAnkPower < 0] = 0
                            peakposLAnkPwr.append(np.max(dat.LeftAnklePower[landings[i]:takeoffs[i]]))
                            peakposRAnkPwr.append(np.max(dat.RightAnklePower[landings[i]:takeoffs[i]]))
                            peaknegLAnkPwr.append(np.min(dat.LeftAnklePower[landings[i]:takeoffs[i]]))
                            peaknegRAnkPwr.append(np.min(dat.RightAnklePower[landings[i]:takeoffs[i]]))
                            RAnkposWork.append(np.sum(posRightAnkPower[landings[i]:takeoffs[i]]))
                            LAnkposWork.append(np.sum(posLeftAnkPower[landings[i]:takeoffs[i]]))
                            RAnknegWork.append(np.sum(negRightAnkPower[landings[i]:takeoffs[i]]))
                            LAnknegWork.append(np.sum(negLeftAnkPower[landings[i]:takeoffs[i]]))
                            peakPosRightFootPower.append(np.max(dat.RDistalFootPower_FP2[landings[i]:takeoffs[i]]))
                            peakPosLeftFootPower.append(np.max(dat.LDistalFootPower_FP1[landings[i]:takeoffs[i]]))
                            peakNegRightFootPower.append(np.min(dat.RDistalFootPower_FP2[landings[i]:takeoffs[i]]))
                            peakNegLeftFootPower.append(np.min(dat.LDistalFootPower_FP1[landings[i]:takeoffs[i]]))
                            LeftDistalRFnegWork.append(np.sum(negLeftFootPower[landings[i]:takeoffs[i]]))
                            RightDistalRFnegWork.append(np.sum(negRightFootPower[landings[i]:takeoffs[i]]))
                            RightDistalRFposWork.append(np.sum(posRightFootPower[landings[i]:takeoffs[i]]))
                            LeftDistalRFposWork.append(np.sum(posLeftFootPower[landings[i]:takeoffs[i]]))
                            subName.append(fName.split('_')[0])
                            config.append( config1 )
                            movements.append( tmpMove )
                            
                            fig, ax = plt.subplots()
                            plt.plot(dat.RDistalFootPower_FP2[landings[i]:takeoffs[i]])
                            plt.plot(dat.RightAnklePower[landings[i]:takeoffs[i]])
                            ax.set_title("Foot and Ankle Power CMJ")
                            ax.set_ylabel("Power (W)")
                            ax.legend(['Foot Power', 'Ankle Power'])
                            # for counterVar, landing in enumerate(landings):
                            #     GS.append (counterVar)
                                
                            #     plt.figure(i)
                            #     plt.plot()
                            # plt.figure(i)
                            # plt.plot(intp_strides(dat.RDistalFootPower_FP4,landings[i],takeoffs[i],takeoffs[i]-landings[i])) 
                        else:
         
           
                             negLeftFootPower = 0
                             negRightFootPower = copy.deepcopy(dat.RDistalFootPower_FP4)
                             negRightFootPower[negRightFootPower > 0] = 0
                             posRightFootPower = copy.deepcopy(dat.RDistalFootPower_FP4)
                             posRightFootPower[posRightFootPower < 0] = 0
                             negLeftAnkPower = copy.deepcopy(dat.LeftAnklePower)
                             negLeftAnkPower[negLeftAnkPower > 0] = 0
                             negRightAnkPower = copy.deepcopy(dat.RightAnklePower)
                             negRightAnkPower[negRightAnkPower > 0] = 0
                             posLeftAnkPower = copy.deepcopy(dat.LeftAnklePower)
                             posLeftAnkPower[posLeftAnkPower < 0] = 0
                             posRightAnkPower = copy.deepcopy(dat.RightAnklePower)
                             posRightAnkPower[posRightAnkPower < 0] = 0
                             peakposLAnkPwr.append(np.max(dat.LeftAnklePower[landings[i]:takeoffs[i]]))
                             peakposRAnkPwr.append(np.max(dat.RightAnklePower[landings[i]:takeoffs[i]]))
                             peaknegLAnkPwr.append(np.min(dat.LeftAnklePower[landings[i]:takeoffs[i]]))
                             peaknegRAnkPwr.append(np.min(dat.RightAnklePower[landings[i]:takeoffs[i]]))
                             
                             RAnkposWork.append(np.sum(posRightAnkPower[landings[i]:takeoffs[i]]))
                             LAnkposWork.append(0)
                             RAnknegWork.append(np.sum(negRightAnkPower[landings[i]:takeoffs[i]]))
                             LAnknegWork.append(0)
                             peakPosRightFootPower.append(np.max(dat.RDistalFootPower_FP4[landings[i]:takeoffs[i]]))
                             peakPosLeftFootPower.append(0)
                             peakNegRightFootPower.append(np.min(dat.RDistalFootPower_FP4[landings[i]:takeoffs[i]]))
                             peakNegLeftFootPower.append(0)
                             LeftDistalRFnegWork.append(0)
                             RightDistalRFnegWork.append(np.sum(negRightFootPower[landings[i]:takeoffs[i]]))
                             RightDistalRFposWork.append(np.sum(posRightFootPower[landings[i]:takeoffs[i]]))
                             LeftDistalRFposWork.append(0)
                             subName.append(fName.split('_')[0])
                             config.append( config1 )
                             movements.append( tmpMove )
                             
                             fig, ax = plt.subplots()
                             plt.plot(dat.RDistalFootPower_FP4[landings[i]:takeoffs[i]])
                             plt.plot(dat.RightAnklePower[landings[i]:takeoffs[i]])
                             ax.set_title("Foot and Ankle Power Skater")
                             ax.set_ylabel("Power (W)")
                             ax.legend(['Foot Power', 'Ankle Power'])
                    except:
        
                        print(fName + str(i))
                        

    except:
        print(fName)


#plt.plot(dat.RDistalFootPower_FP4[landings[2]:takeoffs[2]])


outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Movement':list(movements),
                         'peakPosRightFootPower': list(peakPosRightFootPower), 'peakPosLeftFootPower': list(peakPosLeftFootPower),
                         'peakNegRightFootPower': list(peakNegRightFootPower), 'peakNegLeftFootPower': list(peakNegLeftFootPower),
                         'NegRightFootWork': list(RightDistalRFnegWork), 'NegLeftFootWork': list(LeftDistalRFnegWork), 
                         'PosRightFootWork': list(RightDistalRFposWork), 'PosLeftFootWork': list(LeftDistalRFposWork),
                         'PeakposRightAnklePower': list(peakposRAnkPwr), 'PeakposLeftAnklePower': list(peakposLAnkPwr),
                         'PeaknegRightAnklePower': list(peaknegRAnkPwr), 'PeaknegLeftAnklePower': list(peaknegLAnkPwr),
                         'PosRightAnkleWork': list(RAnkposWork),'PosLeftAnkleWork': list(LAnkposWork) ,
                         'NegRightAnkleWork': list(RAnknegWork),'NegLeftAnkleWork': list(LAnknegWork) })



                       

save_on = 0
if save_on == 1:
    outfileName = fPath + '0_CompiledPowerWorkData.csv'
    outcomes.to_csv(outfileName, index = False)






