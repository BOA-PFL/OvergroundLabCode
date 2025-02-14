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
fPath = 'C:\\Users\\milena.singletary\\OneDrive - BOA Technology Inc\\General - PFL Team\\Testing Segments\\Hike\\2025_Mechanistic_LiteHikeInternalPanels_Adidas\\Overground\\'
fileExt = r".txt"
#entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt) and fName.count('SLL')]
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
ct = []
# ankleWork = []
# kneeWork = []
# hipWork = []
subName = []
movements = []
tmpConfig = []
order = []
plate = []
badFileList = []

RankleEvMom = []
RankleInMom = []

RkneeABDMom = []
RkneeADDMom = []
RkneeAbAdROM = []

LankleEvMom = []
LankleInMom = []

LkneeABDMom = []
LkneeADDMom = []
LkneeAbAdROM = []



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
        forder = fName.split(sep = "_")[3][0]
        tmpName = fName.split(sep = "_")[0]
        
        # Filter force
        # forceZ = np.array(dat.FP4_GRF_Z)
        forceZ = np.array(dat.FP2_GRF_Z)
        #fThresh = max(forceZ) *.2
        forceZ[forceZ<fThresh] = 0 
        forceZ4 = np.array(dat.FP4_GRF_Z)
        forceZ4[forceZ4<fThresh] = 0
        
        ## find the landings and takeoffs of the FP as vectors
        landings = findLandings(forceZ, fThresh)
        takeoffs = findTakeoffs(forceZ, fThresh)
        landings2 = findLandings(forceZ4, fThresh)
        takeoffs2 = findTakeoffs(forceZ4, fThresh)
        
        
        if len(landings) > len(takeoffs):
            takeoffs.append((landings[len(landings)-1] + 500))
        # landings.extend(findLandings(forceZ4, fThresh))
        # takeoffs.extend(findTakeoffs(forceZ4, fThresh))
        # landings.sort() 
        # takeoffs.sort()
        
        for to in range((len(takeoffs2)-1)):
            if takeoffs2[to+1]-takeoffs2[to] < 500:
                takeoffs2.pop(to) # remove this takeoff
        
        # if (tmpName == 'SarahMegiligan') and(config == 'IM') and (forder == '6'):
        #     takeoffs.pop(1)
            
        # side to side task
        # plt.figure()
        # plt.plot(forceZ4)
        # plt.plot(forceZ)
        # plt.figure()
        # plt.plot(dat.LAnkleMoment_Frontal)
        # plt.plot(dat.LAnkleAngle_Frontal)
        # plt.plot(dat.LKneeMoment_Frontal)
        # plt.plot(dat.LKneeAngle_Frontal)
        
        ## For each landing, calculate rolling averages and time to stabilize
        answer = True
        if debug == 1:
            plt.figure(0)
            plt.subplot(6,2,1)
            plt.plot(forceZ)
            plt.ylabel('Force (N)')
            plt.title('Vertical Force')
            plt.subplot(6,2,3)
            # plt.plot(dat.RAnkleMoment_Frontal)
            plt.plot(dat.LAnkleMoment_Frontal)
            plt.ylabel('Moment (Nm)')
            plt.title('Left Ankle In/Ev Moment')
            plt.ylim([-50,100])
            plt.subplot(6,2,5)
            # plt.plot(dat.RKneeMoment_Sagittal)
            plt.plot(dat.LKneeMoment_Sagittal)
            plt.ylabel('Moment (Nm)')
            plt.title('Left Knee Flex/Ex Moment')
            plt.ylim([-50,200])
            plt.subplot(6,2,7)
            # plt.plot(dat.RKneeMoment_Frontal)
            plt.plot(dat.LKneeMoment_Frontal)
            plt.ylim([-50,100])
            plt.ylabel('Moment (Nm)')
            plt.title('Left Knee AB/AD Moment')
            
            plt.subplot(6,2,2)
            plt.plot(forceZ4)
            plt.ylabel('Force (N)')
            plt.title('Vertical Force')
            plt.subplot(6,2,4)
            # plt.plot(dat.RAnkleMoment_Frontal)
            plt.plot(dat.RAnkleMoment_Frontal)
            plt.ylabel('Moment (Nm)')
            plt.title('Right Ankle In/Ev Moment')
            plt.ylim([-50,100])
            plt.subplot(6,2,6)
            # plt.plot(dat.RKneeMoment_Sagittal)
            plt.plot(dat.RKneeMoment_Sagittal)
            plt.ylabel('Moment (Nm)')
            plt.title('Right Knee Flex/Ex Moment')
            plt.ylim([-50,200])
            plt.subplot(6,2,8)
            # plt.plot(dat.RKneeMoment_Frontal)
            plt.plot(dat.RKneeMoment_Frontal)
            plt.ylim([-50,100])
            plt.ylabel('Moment (Nm)')
            plt.title('Right Knee AB/AD Moment')
            
            plt.autoscale()
            answer = messagebox.askyesno("Question","Is data clean?")
            plt.close('all')
        
        if answer == False:
            print('Adding file to bad file list')
            badFileList.append(fName)
        
        if answer == True:
            plt.close('all')
            print('Estimating point estimates')
        
            for ind, landing in enumerate(landings):                    
                    movements.append(tmpMove)
                    subName.append(tmpName)
                    tmpConfig.append(config)
                    order.append(forder)
                    plate.append('2')
                    
                    if tmpMove == 'LHS':
                        sdFz.append(np.std(forceZ[landing + 100 : landing + 400]))
                        avgF = movAvgForce(forceZ, landing, landing + 200, 10)
                        sdF = movSDForce(forceZ, landing, landing + 200, 10)
                        subBW = findBW(avgF)
                        
                        try:
                            stabilization.append(findStabilization(avgF, sdF)/200)
                        except:
                            stabilization.append('NaN')
                            
                    if tmpMove == 'SDS':
                        stabilization.append('NaN')
                        sdFz.append('NaN')
                    #tmpStab = findStabilization(avgF, sdF)

                    ###   ---- Work ---- ##
                    # ankleWork.append(sum(abs(dat.LeftAnklePower[landing : landing + tmpStab])))
                    # kneeWork.append(sum(abs(dat.LeftKneePower[landing : landing + tmpStab])))
                    #hipWork.append(sum(abs(dat.LHipPower[landing : landing + tmpStab])))
                    
                    ###   ---- Contact Time ---- ##
                    ct.append((takeoffs[ind] - landings[ind])/200)
                    
                    
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

                    # LEFT SIDE
                    if np.isnan(sum(dat.LKneeMoment_Frontal[landing : landing + 200])):
                        LankleInMom.append(np.nan)
                        LankleEvMom.append(np.nan)
                    else:
                        LankleInMom.append(max(dat.LAnkleMoment_Frontal[landing : landing + 200]))
                        LankleEvMom.append(min(dat.LAnkleMoment_Frontal[landing : landing + 200]))
                   
                    if np.isnan(sum(dat.LKneeMoment_Frontal[landing : landing + 200])):
                        LkneeABDMom.append(np.nan)
                        LkneeADDMom.append(np.nan)
                    else:
                        LkneeABDMom.append(min(dat.LKneeMoment_Frontal[landing : landing + 200]))
                        LkneeADDMom.append(max(dat.LKneeMoment_Frontal[landing : landing + 200]))
                        
                    if np.isnan(sum(dat.LKneeAngle_Frontal[landing : landing + 200])):
                        LkneeAbAdROM.append(np.nan)
                    else:
                        LkneeAbAdROM.append(max(dat.LKneeAngle_Frontal[landing : landing + 200]) - min(dat.LKneeAngle_Frontal[landing : landing + 200]))
                   
            for ind, landing in enumerate(landings2):                    
                    movements.append(tmpMove)
                    subName.append(tmpName)
                    tmpConfig.append(config)
                    order.append(forder)
                    plate.append('4')
                    
                    stabilization.append('NaN') # stabilizing only happened on plate2
                    sdFz.append('NaN')
                    
                    ###   ---- Work ---- ##
                    # ankleWork.append(sum(abs(dat.LeftAnklePower[landing : landing + tmpStab])))
                    # kneeWork.append(sum(abs(dat.LeftKneePower[landing : landing + tmpStab])))
                    #hipWork.append(sum(abs(dat.LHipPower[landing : landing + tmpStab])))
                    
                    ###   ---- Contact Time ---- ##
                    ct.append((takeoffs2[ind] - landings2[ind])/200)
                    
                    
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

                    # LEFT SIDE
                    if np.isnan(sum(dat.LKneeMoment_Frontal[landing : landing + 200])):
                        LankleInMom.append(np.nan)
                        LankleEvMom.append(np.nan)
                    else:
                        LankleInMom.append(max(dat.LAnkleMoment_Frontal[landing : landing + 200]))
                        LankleEvMom.append(min(dat.LAnkleMoment_Frontal[landing : landing + 200]))
                   
                    if np.isnan(sum(dat.LKneeMoment_Frontal[landing : landing + 200])):
                        LkneeABDMom.append(np.nan)
                        LkneeADDMom.append(np.nan)
                    else:
                        LkneeABDMom.append(min(dat.LKneeMoment_Frontal[landing : landing + 200]))
                        LkneeADDMom.append(max(dat.LKneeMoment_Frontal[landing : landing + 200]))
                        
                    if np.isnan(sum(dat.LKneeAngle_Frontal[landing : landing + 200])):
                        LkneeAbAdROM.append(np.nan)
                    else:
                        LkneeAbAdROM.append(max(dat.LKneeAngle_Frontal[landing : landing + 200]) - min(dat.LKneeAngle_Frontal[landing : landing + 200]))
           

 



outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(tmpConfig), 'Order': list(order), 'Movement':list(movements), 'FP':list(plate),
                         'StabTime': list(stabilization), 'sdFz':list(sdFz), 'ContactTime': list(ct),
                          'RankleEvMom':list(RankleEvMom), 'RankleInMom':list(RankleInMom),  'RkneeADDMom': list(RkneeADDMom), 
                          'RkneeABDMom':list(RkneeABDMom), 'RkneeAbAdROM':list(RkneeAbAdROM),
                          'LankleEvMom':list(LankleEvMom), 'LankleInMom':list(LankleInMom),  'LkneeADDMom': list(LkneeADDMom), 
                          'LkneeABDMom':list(LkneeABDMom), 'LkneeAbAdROM':list(LkneeAbAdROM)})


if save_on == 1:
    outcomes.to_csv(fPath + '0_OGHike.csv',header=True,index=False) 


