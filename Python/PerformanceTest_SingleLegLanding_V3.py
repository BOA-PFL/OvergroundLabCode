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
from tkinter import messagebox


# Define constants and options
fThresh = 40 #below this value will be set to 0.
save_on = 1 #will write to spreadsheet if 1 entered
debug = 0 # turn to 1 for degbugging and displaying plots

# Read in balance file
fPath = 'C:\\Users\\eric.honert\\Boa Technology Inc\\PFL Team - General\\Testing Segments\\WorkWear_Performance\\EH_Workwear_MidCutStabilityI_CPDMech_June23\\Overground\\'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt) and fName.count('SLL')]

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
        if len(lic) == 0: 
            
            if force[step] == 0 and force[step + 1] >= fThresh and force [step + 10 ] > 300:
                lic.append(step)
    
        else:
        
            if force[step] == 0 and force[step + 1] >= fThresh and step > lic[-1] + 300 and force [step + 10] > 300:
                lic.append(step)
    return lic


# def trimLandings(landings, takeoffs):
    """
    This function is used to trim falsely detected landings if the last
    landing occured after the last takeoff
    
    Parameters
    ----------
    landings : Series
        Indices of ground contact obtained from findLandings function
    takeoffs: Series
        Indices of takeoffs from findTakeoffs function

    Returns
    -------
    trimTakeoffs : list
        Indices of takeoffs excluding any potential takeoffs before 1st
        landing
    
    """
#     trimTakeoffs = landings
#     if len(takeoffs) > len(landings) and takeoffs[0] > landings[0]:
#         del(trimTakeoffs[0])
#     return(trimTakeoffs)

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

    """
    lto = []
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0 and force[step + 5] == 0 and force[step + 10] == 0:
            lto.append(step + 1)
    return lto

# def trimTakeoffs(landing, takeoff):
#     if landing[0] > takeoff[0]:
#         takeoff.pop(0)
#         return(takeoff)
#     else:
#         return(takeoff)


#Moving average of length specified in function
def movAvgForce(force, landing, takeoff, length):
    """
    In order to estimate when someone stabilized, we calcualted the moving
    average force and SD of the force signal. This is one of many published 
    methods to calcualte when someone is stationary. 
    
    Parameters
    ----------
    force : Pandas series
        pandas series of force from force plate.
    landing : List
        list of landings calcualted from findLandings.
    takeoff : List
        list of takeoffs from findTakeoffs.
    length : Integer
        length of time in indices to calculate the moving average.

    Returns
    -------
    avgF : list
        smoothed average force .

    """
    newForce = np.array(force)
    win_len = length; #window length for steady standing
    avgF = []
    for i in range(landing, takeoff):
        avgF.append(np.mean(newForce[i : i + win_len]))     
    return avgF

#moving SD as calcualted above
def movSDForce(force, landing, takeoff, length):
    """
    This function calculates a rolling standard deviation over an input
    window length
    
    Parameters
    ----------
    force : Pandas series
        pandas series of force from force plate.
    landing : List
        list of landings calcualted from findLandings.
    takeoff : List
        list of takeoffs from findTakeoffs.
    length : Integer
        length of time in indices to calculate the moving average.

    Returns
    -------
    avgF : list
        smoothed rolling SD of forces

    """
    newForce = np.array(force)
    win_len = length; #window length for steady standing
    avgF = []
    for i in range(landing, takeoff):
        avgF.append(np.std(newForce[i : i + win_len]))     
    return avgF

#estimated stability after 200 indices
def findBW(force):
    """
    If you do not have the subject's body weight or want to find from the 
    steady portion of force, this may be used. This is highly conditional on 
    the data and how it was collected. The below assumes quiet standing from
    100 to 200 indices. 
    
    Parameters
    ----------
    force : Pandas series
        DESCRIPTION.

    Returns
    -------
    BW : floating point number
        estimate of body weight of the subject to find stabilized weight
        in Newtons

    """
    BW = np.mean(avgF[100:200])
    return BW

def findStabilization(avgF, sdF):
    """
    Using the rolling average and SD values, this calcualtes when the 
    actual stabilized force occurs. 
    
    Parameters
    ----------
    avgF : list, calculated using movAvgForce 
        rolling average of force.
    sdF : list, calcualted using movSDForce above
        rolling SD of force.

    Returns
    -------
    floating point number
        Time to stabilize using the heuristic: force is within +/- 5% of subject
        mass and the rolling standrd deviation is below 20

    """
    stab = []
    for step in range(len(avgF)-1):
        if avgF[step] >= (subBW - 0.05*subBW) and avgF[step] <= (subBW + 0.05*subBW) and sdF[step] < 20:
            stab.append(step + 1) 
            
    return stab[0]
   


## Preallocation
stabilization = []
sdFz = []
# ankleWork = []
# kneeWork = []
# hipWork = []
subName = []
movements = []
tmpConfig = []
badFileList = []

RankleEvMom = []
RankleInMom = []

RkneeABDMom = []
RkneeADDMom = []


for fName in entries:
    # try:
        """
        loop through the selected files and obtain values for stabilization time
        Start by looping through files and getting meta data
        Then loop through landings on the force plate for stabilization time
        """
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        print('Processing:',fName)
        
        ##Parse file name into subject and configuration 
        config = fName.split(sep = "_")[1]
        tmpMove = fName.split(sep = "_")[2] 
        # Filter force
        forceZ = np.array(dat.FP4_GRF_Z)
        forceZ[forceZ<fThresh] = 0 
        
        ## find the landings and offs of the FP as vectors
        landings = findLandings(forceZ,fThresh)

        
        ## For each landing, calculate rolling averages and time to stabilize
        answer = True
        if debug == 1:
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
                        stabilization.append(findStabilization(avgF, sdF)/200)
                    except:
                        stabilization.append('NaN')
                    #tmpStab = findStabilization(avgF, sdF)
                    movements.append(tmpMove)
                    subName.append(fName.split(sep = "_")[0])
                    tmpConfig.append(config)
                    ###   ---- Work ---- ##
                    # ankleWork.append(sum(abs(dat.LeftAnklePower[landing : landing + tmpStab])))
                    # kneeWork.append(sum(abs(dat.LeftKneePower[landing : landing + tmpStab])))
                    #hipWork.append(sum(abs(dat.LHipPower[landing : landing + tmpStab])))
                   
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
                    
                   
                   
                    
                    
                except:
                    print(landing, fName)
           

 



outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(tmpConfig),'Movement':list(movements), 'StabTime': list(stabilization), 'sdFz':list(sdFz),
                          'RankleEvMom':list(RankleEvMom), 'RankleInMom':list(RankleInMom),  'RkneeADDMom': list(RkneeADDMom), 
                          'RkneeABDMom':list(RkneeABDMom)})


if save_on == 1:
    outcomes.to_csv(fPath + 'OGStabilization.csv',header=True,index=False) 


