# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 14:17:19 2022

@author: Bethany.Kilpatrick
"""

### This code only looks at CMJ ###

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.signal as sig
import seaborn as sns 
from scipy.signal import find_peaks_cwt 


# Define constants and options
fThresh = 40 #below this value will be set to 0.

# Read in balance file
fPath = "C:\\Users\\bethany.kilpatrick\\Boa Technology Inc\\PFL - General\\Testing Segments\\agilityPerformanceData\\CPDMech_PanelLength_June2022\\Overground\\"
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


# Setting up variable arrays
ct = []
impulse = []

subName = []
config = []
movements = []

PkRankleABDMom = []
PkRankleADDMom = [] 
RAnkleMomentFrontal_excursion = [] 

PkRankleABDAngle = [] 
PkRankleADDAngle = [] 
RAnkleAngleFrontal_excursion = []

PkRankSagAng =[]
RAnkSagAng_IC = []
RAnkleAngleSagittal_excursion = []

RAnkSagMome_IC = [] 
PkAnkSagMom =[] 
RAnkMomentSagittal_excursion = []

PkRkneeABDAng = [] 
PkRkneeADDAng = [] 


PkRkneeSagAng = []
RKneeSagAng_IC = [] 


RKneeSagMome_IC = []
PkRkneeSagMom =[]
RKneeMomentSagittal_excursion = []


PkRkneeABDMom = []
PkRkneeADDMom = [] 
RKneeMomentFrontal_excursion = []

RKneeFrontMome_IC =[] 
RKneeFrontAng_IC = []

RAnkFrontMome_IC =[] 
RAnkFrontAng_IC = []

PkAnkPwr = []

PosAnkWork = [] 
NegAnkWork = []

# PkRkneeADDMom_Mean = []
# PkRkneeADDMom_SD = [] 

# RAnkleFrontMom_Mean = [] 
# RRAnkleFrontMom_SD = []


# RKneeFrontMom_Mean = [] 
# RKneeFrontMom_SD = []


# PkRAnkADDMom_Mean = [] 
# PkRAnkADDMom_SD = [] 

# x =[]
RKMF =[]
idx =[] 

RKMF_Max = []
PkAnkPwr = []

#Setting up plots 
plt.figure(1) # Initializing plot
cc = 1 # Initiate subject counter
   


## save configuration names from files
for ii, fName in enumerate(entries):
    try:
              
        
        fName = entries [1]
        config1 = fName.split('_')[1]
        tmpMove = fName.split('_')[2].split(' ')[0]
        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)


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
            
            dat = delimitTrialSkate(dat, ZForce)
            #find the landings from function above
            landings = findLandings(ZForce, fThresh)
            takeoffs = findTakeoffs(ZForce, fThresh)
        
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]] 


        # fName = entries[1] # Loading in one file at a time
        
        # config1 = fName.split('_')[1]
        # tmpMove = fName.split('_')[2].split(' ')[0]
        
        # dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        
        if (tmpMove == 'CMJ') or (tmpMove == 'cmj'):
            
            
            # dat = delimitTrialCMJ(dat)
            
            ZForce = dat.FP2_GRF_Z *1 
            ZForce[ZForce<fThresh] = 0
            
            YForce = ZForce  #This is out of convenience to calculate impulse below even though this is not the Y force
            
            XForce = dat.FP2_GRF_X *1 
            
            
            landings = findLandings(ZForce, fThresh )
            takeoffs = findTakeoffs(ZForce, fThresh)
            
            
            
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
                
               #Peak R Ankle Angles at landing
                PkRankleABDAngle.append( min( dat.RAnkleAngle_Frontal[landing:takeoffs[countVar]]))
                PkRankleADDAngle.append( max( dat.RAnkleAngle_Frontal[landing:takeoffs[countVar]])) 
                PkRankSagAng.append( max( dat.RAnkleAngle_Sagittal[landing:takeoffs[countVar]])) 
                
               #Peak R Ankle Mom  at landing
                PkRankleABDMom.append( min( dat.RAnkleMoment_Frontal[landing:takeoffs[countVar]]))
                PkRankleADDMom.append( max( dat.RAnkleMoment_Frontal[landing : takeoffs[countVar]]))
                PkAnkSagMom.append( max( dat.RAnkleMoment_Sagittal[landing: takeoffs[countVar]]))
                
                #Peak R Knee Angles at landing
                PkRkneeABDAng.append( max( dat.RKneeAngle_Frontal[landing : takeoffs[countVar]]))
                PkRkneeADDAng.append( min( dat.RKneeAngle_Frontal[landing  : takeoffs[countVar]]))
                PkRkneeSagAng.append( max( dat.RKneeAngle_Sagittal[landing : takeoffs[countVar]]))
                
                
                #Peak R Knee Moments at landing
                PkRkneeADDMom.append( max( dat.RKneeMoment_Frontal[landing:takeoffs[countVar]]))
                PkRkneeABDMom.append( min( dat.RKneeMoment_Frontal[landing  : takeoffs[countVar]]))
                PkRkneeSagMom.append( max( dat.RKneeMoment_Sagittal[landing  : takeoffs[countVar]]))
               
               
              #Peak Power @ ankle
                PkAnkPwr.append( max( dat.RightAnklePower[landing  : takeoffs[countVar]]))
               
                 
               #Work -  Pos and Neg @ ankle             
                PosAnkWork.append(sum(dat.RightAnklePower[landing  : takeoffs[countVar]] > 0)/200)
                NegAnkWork.append(sum(dat.RightAnklePower[landing  : takeoffs[countVar]] < 0)/200)
              
               # ---  Knee and ankle moments and angles at initial contact (IC) 
               # Knee Frontal mom and angs
                RKneeFrontMome_IC.append(dat.RKneeMoment_Frontal[landings[countVar]])
                RKneeFrontAng_IC.append( dat.RKneeAngle_Frontal[landings[countVar]]) 
             
                # Knee sagittal moment and angs
                RKneeSagAng_IC.append(dat.RKneeAngle_Sagittal[landings[countVar]])
                RKneeSagMome_IC.append(dat.RKneeMoment_Sagittal[landings[countVar]])
                
                #Ankle moments and angles at IC  
                RAnkFrontMome_IC.append(dat.RAnkleMoment_Frontal[landings[countVar]]) 
                RAnkFrontAng_IC.append(dat.RAnkleAngle_Frontal[landings[countVar]])
                # Sagittal
                RAnkSagAng_IC.append(dat.RAnkleAngle_Sagittal[landings[countVar]])
                RAnkSagMome_IC.append(dat.RAnkleMoment_Sagittal[landings[countVar]])


                
                
                # --- Excursion of knee Frontal and sagittal plane Moments and angles  
                   # Defining excursion as Pk knee sag angle minus angle at IC (Perraton et al.,2019 ) 
                   
                RKneeMomentFrontal_excursion = np.array(PkRkneeABDMom) - np.array(RKneeFrontMome_IC)  
                RKneeADDAngleFrontal_excursion = np.array(PkRkneeADDAng) - np.array(RKneeFrontAng_IC)
               
                RKneeAngleSagittal_excursion =  np.array(PkRkneeSagAng) - np.array(RKneeSagAng_IC) 
                RKneeMomentSagittal_excursion = np.array(PkRkneeSagMom) - np.array (RKneeSagMome_IC)
               
                # Excursion of Ankle moments and angles
                RAnkleMomentFrontal_excursion =  np.array(PkRankleADDMom) - np.array(RAnkFrontMome_IC)
                RAnkleAngleFrontal_excursion = np.array(PkRankleADDAngle) - np.array(RAnkFrontAng_IC)
               
                RAnkleAngleSagittal_excursion = np.array(PkRankSagAng) - np.array(RAnkSagAng_IC)
                RAnkMomentSagittal_excursion = np.array(PkAnkSagMom) - np.array(RAnkSagMome_IC)
               
                
               ### Turning an arrays to a lists #---- 
                RKneeMomentFrontal_excursion = RKneeMomentFrontal_excursion.tolist()
                RKneeADDAngleFrontal_excursion = RKneeADDAngleFrontal_excursion.tolist() 
               
                
                RKneeAngleSagittal_excursion = RKneeAngleSagittal_excursion.tolist()
                RKneeMomentSagittal_excursion = RKneeMomentSagittal_excursion.tolist()
                
                
                RAnkleMomentFrontal_excursion = RAnkleMomentFrontal_excursion.tolist()
                RAnkleAngleFrontal_excursion = RAnkleAngleFrontal_excursion.tolist() 
     
                
                RAnkleAngleSagittal_excursion = RAnkleAngleSagittal_excursion.tolist()
                RAnkMomentSagittal_excursion = RAnkMomentSagittal_excursion.tolist()
                
                
                # # Findinding meand and SDs for plots
                # RKneeFrontMom_Mean = np.mean(dat.RKneeMoment_Frontal[landing - 20 :landing + 75]) 
                # RKneeFrontMom_SD = np.std(dat.RKneeMoment_Frontal[landing - 20 :landing + 75]) 
                

                 
                RKMF =  (dat.RKneeMoment_Frontal[landing - 20 :landing + 75])
        
                idx = np.argmax(dat.RKneeMoment_Frontal)
        
        
            except:
                print(fName, landing) 
             
                

  
        if ii > 0 and subName[ii] != subName[ii-1]:
                  cc = cc+1
                  plt.figure(cc)
        
        # R Knee Moment Plot
        plt.plot(range(len(dat.FP2_GRF_Z[landing - 20 :landing + 75])), dat.RKneeMoment_Frontal[landing - 20 :landing + 75]) # marker="o", ms = 3) 
        plt.title('Frontal Plane Knee Moment at Landing ')
        plt.ylabel('Moment (Nm)')
        plt.xlabel('Ground contact time (ms)')
        # plt.ylabel('Moment (Nm)')
        
        
        
        # fig, ax1 = plt.subplots() 
        # ax1.plot( RKMF, color = 'red')
        # ax1.plot(idx,RKMF[idx], 'x') 
        # ax1.set_xlabel('Ground contact time (ms)')
        # ax1.set_ylabel('Moment (Nm)', color = 'Green')  
        
        
        # GRF Plot
        # plt.plot(range(len(dat.FP1_GRF_Z[around_contact-50:around_contact+50])),dat.FP1_GRF_Z[around_contact-50:around_contact+50]) 
        


    except:
        print(fName)


# fig = plt.figure(cc)

# fig, axs = plt.subplots(2, 3) 

# axs[0,0].plot(x, dat.RKneeMoment_Frontal[landing - 20 :landing + 75],'k', color='#CC4F1B')
# axs[0,0].set_title('RKneeFrontMom') 
# axs[0,0].fill_between(x, RKneeFrontMom_Mean-RKneeFrontMom_SD, RKneeFrontMom_Mean+RKneeFrontMom_SD,
#     alpha=0.5, edgecolor='#CC4F1B', facecolor='#FF9848') 

# plt.show() 
# plt.tight_layout() 



# outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Movement':list(movements),
#                           'PK_R_ABD_KneeMome':list(PkRkneeABDMom), 'PkRkneeADDAng':list(PkRkneeADDAng), 'RAnkAngFront_Excursion':list( RAnkleAngleFrontal_excursion), '':list(RKneeAngleFrontal_excursion),
#                           'PosAnkWork':list(PosAnkWork)
#                           })

# outfileName = fPath + 'CompiledAgilityData.csv'
# outcomes.to_csv(outfileName, index = False)



