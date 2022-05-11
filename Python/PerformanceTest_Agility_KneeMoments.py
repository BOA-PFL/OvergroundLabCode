# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 14:17:19 2022

@author: Bethany.Kilpatrick
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.signal as sig
import seaborn as sns 

# Define constants and options
fThresh = 40 #below this value will be set to 0.

# Read in balance file
fPath = 'C:/Users/bethany.kilpatrick/Boa Technology Inc/PFL - General/Testing Segments/AgilityPerformanceData/DialLocation_CPDMech_April2022 (NOBULL)/Overground/'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]


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
            
            if force[step] == 0 and force[step + 1] >= fThresh and force [step + 10 ] > 100:
                lic.append(step)
    
        else:
        
            if force[step] == 0 and force[step + 1] >= fThresh and step > lic[-1] + 100 and force [step + 10] > 100:
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

    """
    lto = []
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0 and force[step + 5] == 0 and force[step + 10] == 0:
            lto.append(step + 1)
    return lto 



def trimLandings(landings, takeoffs):
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
    trimTakeoffs = landings
    if len(takeoffs) > len(landings) and takeoffs[0] > landings[0]:
        del(trimTakeoffs[0])
    return(trimTakeoffs)

def trimTakeoffs(landing, takeoff):
    if landing[0] > takeoff[0]:
        takeoff.pop(0)
        return(takeoff)
    else:
        return(takeoff)



def delimitTrialSkate(inputDF, ZForce):
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
    ax.plot(ZForce, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)

# def delimitTrialCMJ(inputDF):
#     """
#      This function uses ginput to delimit the start and end of a trial
#     You will need to indicate on the plot when to start/end the trial. 
#     You must use tkinter or plotting outside the console to use this function
#     Parameters
#     ----------
#     inputDF : Pandas DataFrame
#         DF containing all desired output variables.
#     zForce : numpy array 
#         of force data from which we will subset the dataframe

#     Returns
#     -------
#     outputDat: dataframe subset to the beginning and end of jumps.

#     """
#     # generic function to plot and start/end trial #
#     fig, ax = plt.subplots()
#     ax.plot(ZForce, label = 'Total Force')
#     fig.legend()
#     pts = np.asarray(plt.ginput(2, timeout=-1))
#     plt.close()
#     outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
#     outputDat = outputDat.reset_index()
#     return(outputDat)


# Setting up variable arrays
ct = []
impulse = []

subName = []
config = []
movements = []

PkLankleABDMom = []
PkLankleADDMom = [] 
LAnkleMomentFrontal_variation = [] 

PkLankleABDAngle = [] 
PkLankleADDAngle = [] 
LAnkleAngleFrontal_variation = []


PkLkneeABDAng = [] 
PkLkneeADDAng = [] 
LkneeAngleFrontal_variation = []


PkLkneeABDMom = []
PkLkneeADDMom = [] 
LKneeMomentFrontal_variation = []

PkLHipABDAng = [] 
PkLHipADDAng = [] 
LHipAngleFrontal_variation = [] 





#Setting up plots 
plt.figure(1) # Initializing plot
cc = 1 # Initiate subject counter
   


## save configuration names from files
for ii, fName in enumerate(entries):
    try:
        
        #fName = entries[2] # Loading in one file at a time
        
        config1 = fName.split('_')[1]
        tmpMove = fName.split('_')[2].split(' ')[0]
        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        #dat = dat.fillna(0)
        around_contact = np.argmax(dat.FP1_GRF_Z)

        if (tmpMove == 'Skater') or (tmpMove == 'skater'):
            
            # create vector of force from vertical signal from each file and make low values 0
            if np.max(abs(dat.FP3_GRF_Z)) > np.max(abs(dat.FP4_GRF_Z)):
                ZForce = dat.FP3_GRF_Z*1
                YForce = dat.FP3_GRF_Y
                
            else:
                ZForce = dat.FP4_GRF_Z *1
                YForce = dat.FP4_GRF_Y 
                
            if abs(np.min(YForce)) > abs(np.max(YForce)): 
                
                YForce = YForce * 1
            ZForce = dat.FP4_GRF_Z *1  
            ZForce[ZForce<fThresh] = 0
            
            # dat = delimitTrialSkate(dat, ZForce)
            #find the landings from function above
            landings = findLandings(ZForce, fThresh)
            takeoffs = findTakeoffs(ZForce, fThresh)
        
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]] 

        
        elif (tmpMove == 'CMJ') or (tmpMove == 'cmj'):
            
            
            # dat = delimitTrialCMJ(dat)
            
            ZForce = dat.FP2_GRF_Z *1 
            ZForce[ZForce<fThresh] = 0
            
            YForce = ZForce  #This is out of convenience to calculate impulse below even though this is not the Y force
            
            XForce = dat.FP2_GRF_X *1 
            
            
            landings = findLandings(ZForce, fThresh )
            takeoffs = findTakeoffs(ZForce, fThresh)
            
            
            # landings = trimLandings(landings, takeoffs)
            # takeoffs = trimTakeoffs(landings, takeoffs)
            
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]] 
             
            

           
        else:
            print('this movement is not included in Performance Test Analysis')
        
        
        for countVar, landing in enumerate(landings):
            try:
                
                
                ct.append(takeoffs[countVar] - landing)
                impulse.append(np.sum(YForce[landing:takeoffs[countVar]]) )

                subName.append(fName.split('_')[0])
                config.append( config1 )
                movements.append( tmpMove )
                
               #Peak L Ankle Angles 
                PkLankleABDAngle.append( min(dat.LAnkleAngle_Frontal[landing  : landing + 300]))
                PkLankleADDAngle.append( max(dat.LAnkleAngle_Frontal[landing : landing + 300]))
                
               #Peak L Ankle Moments
                PkLankleABDMom.append( min(dat.LAnkleMoment_Frontal[landing  : landing + 300]))
                PkLankleADDMom.append( max(dat.LAnkleMoment_Frontal[landing : landing + 300]))
               
                
                #Peak L Knee Angles
                PkLkneeABDAng.append(max(dat.LKneeAngle_Frontal[landing : landing + 300]))
                PkLkneeADDAng.append(min(dat.LKneeAngle_Frontal[landing : landing + 300]))
                
                #Peak L Knee Moments
                PkLkneeADDMom.append(max(dat.LKneeMoment_Frontal[landing : landing + 300]))
                PkLkneeABDMom.append(min(dat.LKneeMoment_Frontal[landing : landing + 300]))
                
                
                #Variation of knee Frontal Moments and angles 
                LKneeMomentFrontal_variation =  (np.array(PkLkneeADDMom) - np.array(PkLankleABDMom))
                LKneeAngleFrontal_variation = (np.array(PkLkneeABDAng) - np.array(PkLkneeADDAng))  
                 
                
                # Variation of L Ankle moments and angles
                LAnkleMomentFrontal_variation =  (np.array(PkLankleADDMom) - np.array(PkLankleABDMom))
                LAnkleAngleFrontal_variation = (np.array(PkLankleABDAngle) - np.array(PkLankleADDAngle))
                 
                
                
                
            except:
                print(fName, landing) 
             
                

  
        if ii > 0 and subName[ii] != subName[ii-1]:
                  cc = cc+1
                  plt.figure(cc)
        
        # L Knee Moment Plot
        plt.plot(range(len(dat.FP1_GRF_Z[landing - 50 :landing + 50])), dat.LKneeAngle_Frontal[landing - 50 :landing + 50]) 
        plt.title('Frontal Plane Knee Moment at Landing ')
        plt.xlabel('Ground contact time (ms)')
        plt.ylabel('Moment (Nm)')
        
        # GRF Plot
        # plt.plot(range(len(dat.FP1_GRF_Z[around_contact-50:around_contact+50])),dat.FP1_GRF_Z[around_contact-50:around_contact+50]) 
        


    except:
        print(fName)


outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Movement':list(movements),
                         'CT':list(ct), 'impulse':list(impulse) })

outfileName = fPath + 'CompiledAgilityData.csv'
outcomes.to_csv(outfileName, index = False)


outcomes.to_csv("C:/Users/bethany.kilpatrick/Boa Technology Inc/PFL - General/WorkWear_Performance/Elten_Jan2022/Overground/CompiledOvergroundData.csv"
                      ,mode='a',header=True) 


