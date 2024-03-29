# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 13:44:38 2023

@author: Bethany.Kilpatrick
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May 17 14:48:59 2021

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

pd.options.mode.chained_assignment = None  # default='warn' set to warn for a lot of warnings

# Define constants and options
fThresh = 100 #below this force value will be set to 0.
save_on = 1 # turn this on for automatic saving of csv!!!! 


#fPath = 'C:\\Users\\bethany.kilpatrick\\Boa Technology Inc\\PFL - General\\Testing Segments\\AgilityPerformanceData\\AS_Trail_DorsalPressureVariation_PFLMech_May2023\\Overground\\Triangle&AP\\'
#fPath = 'C:/Users/milena.singletary/Boa Technology Inc/PFL Team - Documents/General/Testing Segments/AgilityPerformanceData/AS_Trail_HeelLockAgility_Perf_Apr23/Overground/TriangleAP/'
#fPath = 'C:\\Users\\milena.singletary\\Boa Technology Inc\\PFL Team - Documents\\General\\ExploratoryMetrics\\TriangleAP\\Agility_2023\\Exports\\'
fPath = 'C:\\Users\\milena.singletary\\Boa Technology Inc\\PFL Team - Documents\\General\\Testing Segments\\AgilityPerformanceData\\AS_Trail_MinimalStructure_CPDMech_June23\\Overground\\'

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

        totForce = inputDF.FP1_GRF_Z + inputDF.FP2_GRF_Z 
        print('Select a point on the plot to represent the beginning & end of trial where Y-value is near 0')


        ax.plot(totForce, label = 'Total Force')
        fig.legend()
        pts = np.asarray(plt.ginput(2, timeout=-1))
        plt.close()
        outputDat = inputDF.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
        outputDat = outputDat.reset_index()
        trial_segment = np.array([FName, pts], dtype = object)
        np.save(fPath+FName+'TrialSeg.npy',trial_segment)

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
    fig, ((ax, ax1), (ax2, ax3)) = plt.subplots(2, 2)
    ax.plot(inputDF.RAnkleMoment_Sagittal[inputLandings[0]:inputTakeoffs[-1]], 'k')
    # ax.vlines(x = inputLandings[1:], ymin = np.min(inputDF.RAnkleMoment_Sagittal[inputLandings[0]:inputTakeoffs[-1]]), ymax = np.max(inputDF.RAnkleMoment_Sagittal[inputLandings[0]:inputTakeoffs[-1]]),
    #    color = 'coral', label = 'Landings',linewidth=3.0, ls='--')
    # ax.vlines(x = inputTakeoffs[1:], ymin = np.min(inputDF.RAnkleMoment_Sagittal[inputLandings[0]:inputTakeoffs[-1]]), ymax = np.max(inputDF.RAnkleAngle_Sagittal[inputLandings[0]:inputTakeoffs[-1]]),
    #    color = 'cyan', label = 'Takeoffs',linewidth=3.0, ls='--')
    for i in range(len(inputLandings)):

        ax.axvspan(inputLandings[i], inputTakeoffs[i], color = 'lightgray', alpha = 0.5)
    
    ax.set_ylim(-250, 10)
    ax.set_xlabel('Indices')
    ax.set_title('Ankle Sagittal Moment')
    ax.set_ylabel('Moment (Nm)')
    ax1.plot(inputDF.RKneeMoment_Sagittal[inputLandings[0]:inputTakeoffs[-1]], 'k')
    for i in range(len(inputLandings)):

        ax1.axvspan(inputLandings[i], inputTakeoffs[i], color = 'lightgray', alpha = 0.5)
    ax1.set_ylim(-25, 250)
    ax1.set_xlabel('Indices') 
    ax1.set_title('Knee Sagittal Moment')
    ax1.set_ylabel('Moment (Nm)')
    plt.tight_layout()
    plt.show()
    

    ax2.plot(inputDF.RAnkleMoment_Frontal[inputLandings[0]:inputTakeoffs[-1]], 'k')
    for i in range(len(inputLandings)):

        ax2.axvspan(inputLandings[i], inputTakeoffs[i], color = 'lightgray', alpha = 0.5)
    ax2.set_ylim(-50, 150)
    ax2.set_xlabel('Indices')
    ax2.set_title('Ankle Frontal Moment')
    ax2.set_ylabel('Moment (Nm)')
    ax3.plot(inputDF.RKneeMoment_Frontal[inputLandings[0]:inputTakeoffs[-1]], 'k')
    ax3.set_ylim(-100, 100)
    ax3.set_xlabel('Indices')
    ax3.set_title('Knee Frontal Moment')
    ax3.set_ylabel('Moment (Nm)')
    plt.tight_layout()
    for i in range(len(inputLandings)):

        ax3.axvspan(inputLandings[i], inputTakeoffs[i], color = 'lightgray', alpha = 0.5)
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
peakGRFy = []
peakResForce = []
peakGRFxy = []
RFDecc_Z = []
RFDecc_y = []
pkPFmom = []
pkKneeABDmom = []


ZForce = []  

subName = []
config = []
movements = []

badFileList = []
side = []

## save configuration names from files
for fName in entries:
    try:
        
        #fName = entries[1]
        config1 = fName.split('_')[1]
        tmpMove = fName.split('_')[2]

        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        dat = dat.fillna(0)
        
        
        landings = [] # erase landings and takeoffs from last loop
        takeoffs = []  
        
        
            
            
        if (tmpMove == 'Triangle') or (tmpMove == 'triangle'):
            dat = delimitTrial(dat,fName)
            ZForce = dat.FP1_GRF_Z + dat.FP2_GRF_Z 
            XForce = dat.FP1_GRF_X + (dat.FP2_GRF_X*-1)
            YForce = dat.FP1_GRF_Y + dat.FP2_GRF_Y
            resForce = []
            XYForce = []
            
            if abs(np.min(XForce)) > abs(np.max(XForce)):
                XForce = XForce * -1
            
            
            ZForce[ZForce<fThresh] = 0
            
            # compute resultant GRF of X & Y
            for ii in range(len(ZForce)):
                XYForce.append(np.sqrt(YForce[ii]**2 + XForce[ii]**2))
                resForce.append(np.sqrt(ZForce[ii]**2 + YForce[ii]**2 + XForce[ii]**2))
                
            #find the landings from function above
            landings = findLandings(ZForce, fThresh)
            takeoffs = findTakeoffs(ZForce, fThresh)
            
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]]
            
            for ii in landings:
                if dat.FP2_GRF_Z[ii + 10] > fThresh:                
                    xx = str(fName.split('_')[0]) + "- Right" + fName
                    side.append(xx)
                    # side.append('Right',fName.split('_')[0])  
                    # side.append(fName.split('_')[0])
                    
                if dat.FP1_GRF_Z[ii+ 10] > fThresh:
                    xx = str(fName.split('_')[0]) + "- Left" + fName 
                    side.append(xx)
                    # side.append('Left',fName.split('_')[0] )   
                    # side.append(fName.split('_')[0])
                    # XForce = XForce * -1
            
            
            
        elif (tmpMove == 'AP') or (tmpMove == 'ap'):
   
            # for ii in landings: 
            #     side.append('NA')
           dat = delimitTrial(dat,fName)
           ZForce = dat.FP1_GRF_Z + dat.FP2_GRF_Z 
           XForce = dat.FP1_GRF_X + (dat.FP2_GRF_X * -1) # to account for direction (L v R)
           YForce = dat.FP1_GRF_Y + dat.FP2_GRF_Y
           resForce = []
           XYForce = []
               
           if abs(np.min(XForce)) > abs(np.max(XForce)):
                XForce = XForce * -1

           ZForce[ZForce<fThresh] = 0
           
           # compute resultant force    
           for ii in range(len(ZForce)):
               XYForce.append(np.sqrt(YForce[ii]**2 + XForce[ii]**2))
               resForce.append(np.sqrt(ZForce[ii]**2 + YForce[ii]**2 + XForce[ii]**2))
               
           # find the landings from function above
           landings = findLandings(ZForce, fThresh)
           takeoffs = findTakeoffs(ZForce, fThresh)
           
           landings[:] = [x for x in landings if x < takeoffs[-1]]
           takeoffs[:] = [x for x in takeoffs if x > landings[0]]
           
           for ii in landings:
               if dat.FP2_GRF_Z[ii + 10] > fThresh:                
                   xx = str(fName.split('_')[0]) + "- Right" + fName
                   side.append(xx)
                   # side.append('Right') 
                   # side.append(fName.split('_')[0])
               if dat.FP1_GRF_Z[ii+ 10] > fThresh:
                   xx = str(fName.split('_')[0]) + "- Left" + fName
                   side.append(xx)
                   # side.append('Left', fName.split('_')[0]) 
                   # side.append(fName.split('_')[0])
 
            

        else:
            print('this movement is not included in Performance Test Analysis')
        
        if (tmpMove == 'Triangle') or (tmpMove == 'triangle') or (tmpMove == 'AP') or (tmpMove == 'ap'):
            makeVizPlot(dat, landings, takeoffs)
            # answer = messagebox.askyesno("Question","Is data clean?")
            
            # if answer == False:
            #     plt.close('all')
            #     print('Adding file to bad file list')
            #     badFileList.append(fName)
            
            # if answer == True:
            #     plt.close('all')
            #     print('Estimating point estimates')
                
               
            for i in range(len(landings)):
                
                
                try: 
                    subName.append(fName.split('_')[0])
                    config.append( config1 )
                    movements.append( tmpMove )
                    
                    tmpCT = round((takeoffs[i] - landings[i])/2) #to use as approximate for propulsive start
                    
                    CT.append((takeoffs[i] - landings[i])/200)
                    impulseZ.append(np.sum(ZForce[landings[i]:takeoffs[i]])/200)
                    impulseX.append(np.sum(XForce[landings[i]:takeoffs[i]])/200)
                    
                    peakGRFz.append(np.max(ZForce[landings[i]+tmpCT:takeoffs[i]])) #peak propulsive force approximated from 2nd half of contact time
                    peakGRFx.append(np.max(XForce[landings[i]+tmpCT:takeoffs[i]])) #peak propulsive force approximated from 2nd half of contact time
                    peakGRFy.append(np.max(YForce[landings[i]+tmpCT:takeoffs[i]]))
                    peakResForce.append(np.max(resForce[landings[i]+tmpCT:takeoffs[i]]))
                    peakGRFxy.append(np.max(XYForce[landings[i]+tmpCT:takeoffs[i]]))
                    
                    RFDecc_Z.append(np.max(np.diff(ZForce[landings[i]:landings[i]+tmpCT]))/200) # braking RFD, from intitial contact upto 1/2 CT ~ propulsive start
                    RFDecc_y.append(np.max(np.diff(YForce[landings[i]:landings[i]+tmpCT]))/200)
                    
                    # if (side[i] == 'Left'):
                    #     ShankYMin = np.argmin(dat.L_ShankPos_Y[landings[i]: takeoffs[i]])
                    #     # LPkAnkPlantMom.append( np.max( dat.LAnkleMoment_Sagittal[landings[i]+tmpCT: takeoffs[i]]))  
                    #     # LPkKneeABDMom.append( np.min( dat.LKneeMoment_Frontal[landings[i]+tmpCT: takeoffs[i]]))   
                    #     # pkPFmom.append(np.min( dat.LAnkleMoment_Sagittal[landings[i]: takeoffs[i]])*-1)
                    #     # pkKneeABDmom.append(np.min( dat.LKneeMoment_Frontal[landings[i]: takeoffs[i]]))
                        
                    # if (side[i] == 'Right'):
                    #     ShankYMin = np.argmin(dat.R_ShankPos_Y[landings[i]: takeoffs[i]])
                    #     # RPkAnkPlantMom.append( np.max( dat.RAnkleMoment_Sagittal[landings[i]+tmpCT: takeoffs[i]]))  
                    #     # RPkKneeABDMom.append( np.min( dat.RKneeMoment_Frontal[landings[i]+tmpCT: takeoffs[i]]))                                                           
                    #     # pkPFmom.append(np.min( dat.RAnkleMoment_Sagittal[landings[i]: takeoffs[i]])*-1)  
                    #     # pkKneeABDmom.append(np.min( dat.RKneeMoment_Frontal[landings[i]: takeoffs[i]]))
                        
    
                    
                    
                    # # for RFD_y to be computed ShankPosY needs to be exported as TMM variable 
                    # if ShankYMin == 0:
                    #         RFDecc_y.append(np.max(np.diff(YForce[landings[i]:landings[i]+tmpCT]))/200)
                    # else:
                    #         RFDecc_y.append(np.max(np.diff(YForce[landings[i]: landings[i] + ShankYMin]))/200)
               
                    
                except:
    
                    print(fName + str(i))



    except:
        print(fName)





outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Movement':list(movements), 
                         'CT':list(CT), 'impulse_Z':list(impulseZ), 'impulse_X':list(impulseX), 
                          'peakGRF_Z':list(peakGRFz), 'peakGRF_X':list(peakGRFx),'peakGRF_Y':list(peakGRFy), 'peakGRF_R':list(peakResForce), 'peakGRF_XY':list(peakGRFxy),
                          'brakingRFDvertical': list(RFDecc_Z),   'breakingRFDy':list(RFDecc_y) }) 
                          # 'pkPFmom' :list(pkPFmom), 'pkKneeABDmom':list(pkKneeABDmom) ,'Side':list(side),  }) 
                          
                     


# save_on = 1
if save_on == 1:
    #outfileName = 'C:\\Users\\bethany.kilpatrick\\Boa Technology Inc\\PFL - General\\Testing Segments\\AgilityPerformanceData\\AS_Trail_DorsalPressureVariation_PFLMech_May2023\\Overground\\Triangle&AP\\CompiledAgilityDataTest_TriangleAP_Kinetics_2.csv'
    outfileName = 'C:\\Users\\milena.singletary\\Boa Technology Inc\\PFL Team - Documents\\General\\ExploratoryMetrics\\TriangleAP\\Agility_2023\\Data\\MinimalStructure_TriangleAP_Kinetics.csv'
    outcomes.to_csv(outfileName, index = False)




