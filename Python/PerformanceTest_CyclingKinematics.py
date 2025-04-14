# -*- coding: utf-8 -*-
"""
Created on Mon May 17 14:48:59 2021

Updating 2/6/24 to turn on/off plot vizualization - MS

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
import scipy.integrate as integrate 



import seaborn as sns
from dataclasses import dataclass

import scipy.signal as sig


pd.options.mode.chained_assignment = None  # default='warn' set to warn for a lot of warnings

# Define constants and options
# fThresh = .255 #below this force value will be set to 0.
save_on = 1 # turn this on for automatic saving of csv!!!! 
debug = 1 #turn off to skip makeVizPlot
ts_plot = 0 # turn this on for timeseries plotting of extracted variables
data_check = 1
fPath = 'C:\\Users\\bethany.kilpatrick\\BOA Technology Inc\\PFL Team - General\\Testing Segments\\Cycling Performance Tests\\2025_Performance_CyclingLacevBOA_Specialized\\Overground\\'

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

def findBDC(force, fThresh):
    """
    This function finds the BDC from force plate data
    it uses a heuristic to determine BDC from when the smoothed force is
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
        Indices of BDC.

    """
    lic = [] 
    
    for step in range(len(force)-1):
    
            
            if force[step] == 0 and force[step + 1] >= fThresh :
                lic.append(step)
    
        
    return lic



def findTDC(force, fThresh):
    """
    This function calculates the TDC using a heuristic 

    Parameters
    ----------
    force : Pandas Series
        vertical force from force plate.
    
    fThresh: integer
        Value force has to be greater than to count as a takeoff/landing
    Returns
    -------
    lto : list
        indices of TDC obtained from force data. TDC here mean
        the moment a force signal was > a threshold and then goes to 0

    # """
    lto = []
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0 :
            lto.append(step + 1)
    return lto 


   

def makeVizPlot(inputDF, inputBDC, inputTDC):
    
    """
    Parameters
    ----------
    inputDF : Pandas DF
        Standard Agility export in dataframe.
    inputBDC : list
        list of BDC from findBDC function.
    inputTDC : list
        list of TDC from findTDC function.
    COMpwrILM: list
        list of COM pwr

    Returns
    -------
    No variables; just a plot to inspect for clean kinematic/kinetic data.

    """
    fig, ((ax, ax1), (ax2, ax3)) = plt.subplots(2, 2)
    ax.plot(inputDF.RAnkleAngle_Sagittal[inputBDC[0]:inputTDC[-1]], 'k')
    # ax.vlines(x = inputBDC[1:], ymin = np.min(inputDF.RAnkleMoment_Sagittal[inputBDC[0]:inputTDC[-1]]), ymax = np.max(inputDF.RAnkleMoment_Sagittal[inputBDC[0]:inputTDC[-1]]),
    #    color = 'coral', label = 'BDC',linewidth=3.0, ls='--')
    # ax.vlines(x = inputTDC[1:], ymin = np.min(inputDF.RAnkleMoment_Sagittal[inputBDC[0]:inputTDC[-1]]), ymax = np.max(inputDF.RAnkleAngle_Sagittal[inputBDC[0]:inputTDC[-1]]),
    #    color = 'cyan', label = 'TDC',linewidth=3.0, ls='--')
    for i in range(len(inputBDC)):

        ax.axvspan(inputBDC[i], inputTDC[i], color = 'lightgray', alpha = 0.5)
    
    ax.set_ylim(-250, 10)
    ax.set_xlabel('Indices')
    ax.set_title('Ankle Sagittal Angle')
    ax.set_ylabel('Angle (deg)')
    ax1.plot(inputDF.RKneeAngle_Sagittal[inputBDC[0]:inputTDC[-1]], 'k')
    for i in range(len(inputBDC)):

        ax1.axvspan(inputBDC[i], inputTDC[i], color = 'lightgray', alpha = 0.5)
    ax1.set_ylim(-25, 250)
    ax1.set_xlabel('Indices') 
    ax1.set_title('Knee Sagittal Angle')
    ax1.set_ylabel('Moment (Nm)')
    plt.tight_layout()
    plt.show()
    

    ax2.plot(inputDF.RKneeAngle_Frontal[inputBDC[0]:inputTDC[-1]], 'k')
    for i in range(len(inputBDC)):

        ax2.axvspan(inputBDC[i], inputTDC[i], color = 'lightgray', alpha = 0.5)
    ax2.set_ylim(-50, 150)
    ax2.set_xlabel('Indices')
    ax2.set_title('Knee Frontal Angle')
    ax2.set_ylabel('Angle (deg)')
    ax3.plot(inputDF.RAnkleAngle_Frontal[inputBDC[0]:inputTDC[-1]], 'k')
    ax3.set_ylim(-100, 100)
    ax3.set_xlabel('Indices')
    ax3.set_title('Ankle Frontal Moment')
    ax3.set_ylabel('Angle (deg)')
    plt.tight_layout()
    for i in range(len(inputBDC)):

        ax3.axvspan(inputBDC[i], inputTDC[i], color = 'lightgray', alpha = 0.5)
    plt.show()

  
    

from scipy.interpolate import interp1d

def interpMet(metric, BDC, TDC):
    fig = plt.figure()
    normMetric = []
    xx = np.array(np.linspace(0, 100, 101)) # Return evenly spaced numbers over a specified interval (0,100) with 101 
    for value1, value2 in zip(BDC, TDC):
        x = np.array(range(value1, value2))
        y = np.array(metric[value1 :value2])
        f = interp1d(x,y, 'linear' ,  fill_value= 'extrapolate')
        xnorm = np.linspace(value1, value2, 101)
        ynorm = np.array([f(x) for x in xnorm])
        normMetric.append(ynorm)
        #plt.figure()
        plt.plot(xx, ynorm)
        
        titleName = [name for name, value in globals().items() if value is metric][0]
        plt.title('Interpolated {0}'.format(titleName))
        # plt.ylabel('Force (N)')
        plt.xlabel ('Percentage of Task')
        
    saveFolder= fPath + '2DPlots'
    
    if os.path.exists(saveFolder) == False:
        os.mkdir(saveFolder)
        
    plt.savefig(saveFolder + '/' + subName + '_'  + config1 + '_' + titleName +'.png')
    return fig  


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
        # sprint_start = round(trial_segment_old[1][1,0])
        trialEnd = trial_segment_old[1][1,0] # Change to [1][2,0] if sprint present
        inputDF = inputDF.iloc[int(np.floor(trialStart)) : int(np.floor(trialEnd)),:]
        outputDat = inputDF.reset_index()
        
    else: 
        fig, ax = plt.subplots()

        RToes = inputDF.RToes
        print('Select 2 point on the plot to represent the beginning & end of trial where Y-value is near 0. If there is a sprint, click 3 for the start of the sprint.')


        ax.plot(RToes, label = 'Total Force')
        fig.legend()
        pts = np.asarray(plt.ginput(2, timeout=-1))
        plt.close()
        # outputDat = inputDF[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
        start = round(pts[0][0])
        # sprint_start = round(pts[1][0]) #Uncomment when there is a sprint present
        end =  round(pts[1][0]) # Change to pts[2][0]) if sprint present
        outputDat = inputDF[start: end]
        outputDat = outputDat.reset_index()
        trial_segment = np.array([FName, pts], dtype = object)
        np.save(fPath+FName+'TrialSeg.npy',trial_segment)

    return outputDat  #, sprint_start

    

################# initiate variables
CT = []


pkINVang = []
pkEVang = []
pkKneeABDang = []
pkKneeADDang = []
pkKneeSagAng = []
kneeABDrom = [] 
AnkTransAngrom = []


AnkFront_mean = []
AnkFront_sd = []

AnkSag_mean = []
AnkSag_sd = []

AnkTrans_mean = []
AnkTrans_sd = []

KneeFront_mean = []
KneeFront_sd = []

KneeSag_mean = []
KneeSag_sd = []

KneeTrans_mean = []
KneeTrans_sd = []



ExtAnkAngTrans = []
IntAnkAngTrans = []
dwn_ExtAnkAng = []
up_ExtAnkAng = []

dwn_pkAnkFlex = []
up_pkAnkFlex = []


up_pkKneeABDang = []
dwn_pkKneeABDang  = []
pkAnkFlex = []

ankFrontROM =[]


subNamelist = []
config = []
movement = []
trial = []
badFileList = [] 
 

pkKneeTransAng = []
IntKneeTransAng = []
ExtTransROM = []


dwn_pkEVang = []
up_pkEVang = []

PkAnkleExt = []
kneeSagROM = [] 
ankleSagROM = [] 
dwn_pkKneeFlex = []
up_pkKneeFlex = []

dwn_pkKneeExtTrans = []
up_pkKneeExtTrans = []




minKneeSagAng =[]

order = [] 

outcomes = []

## save configuration names from files
for fName in entries:
    try:
        
        # fName = entries[0]
        print(fName)
        subName = fName.split('_')[0]
        config1 = fName.split('_')[1]
        trialTmp = fName.split(sep = "_")[2].split(sep = "-")[0] 

        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        dat = dat.fillna(0)
        descr = pd.read_csv(fPath + "\\" + fName , sep = '\t' , nrows = 5, header = None , skiprows = [2])
      
        frequency = float(descr.iloc[2,0])
        
        # dat,sprint_start = delimitTrial(dat,fName) 
      
        dat = delimitTrial(dat,fName) 
        ZForce = dat.RToes 
        # toes = dat[dat['RToes']]
        
        BDC = np.where(np.gradient(np.sign(np.gradient(ZForce))) > 0)[0]
        GC = [] # Good Cycle detections
        for jj in range(len(BDC)-1):
            if BDC[jj+1] - BDC[jj] > 10:
                GC.append(jj)

        BDC = BDC[np.array(GC)]
        
        
        TDC = []
        for jj in range(len(BDC[:-1])):
            TDC.append(np.argmax(ZForce[BDC[jj]:BDC[jj+1]]) + BDC[jj])
        
        
        
        
        
        # plt.figure()
        # plt.plot(dat.RToes, label = 'Right Foot Total Force')
       
        # for i in range(len(BDC)-1):
        #         plt.axvspan(BDC[i], TDC[i], color = 'lightgray', alpha = 0.5)   
        # plt.scatter(BDC, dat.RToes[BDC],color='blue', label='BDC', marker='o')  # Blue circles for BDC
        # plt.scatter(TDC, dat.RToes[TDC],color='red', label='TDC', marker='o')    # Red circles for TDC
        # plt.legend()
        
       
          
        
       
            

            
        for i in range(len(BDC)-1):
           
            try:
                subNamelist.append(subName)
                config.append( config1 )
                order.append(trialTmp)  
                # if BDC[i] < sprint_start:
                #     movement.append('Steady')
                # else:
                #     movement.append('Sprint')
            
               
                #Ank Frontal
                pkINVang.append(np.min(dat.RAnkleAngle_Frontal[BDC[i]:BDC[i+1]]))
                pkEVang.append(np.max(dat.RAnkleAngle_Frontal[BDC[i]:BDC[i+1]]))
                ankFrontROM.append(np.max(dat.RAnkleAngle_Frontal[BDC[i]:BDC[i+1]]) - np.min(dat.RAnkleAngle_Frontal[BDC[i]:BDC[i+1]])) 
                
                dwn_pkEVang.append(np.max(dat.RAnkleAngle_Frontal[TDC[i]:BDC[i+1]]))
                up_pkEVang.append(np.max(dat.RAnkleAngle_Frontal[BDC[i]:TDC[i]]))  
                
                AnkFront_mean.append(np.mean(dat.RAnkleAngle_Frontal[BDC[i]:BDC[i+1]])) 
                AnkFront_sd.append(np.std(dat.RAnkleAngle_Frontal[BDC[i]:BDC[i+1]])) 
                
                
                # Ank Sag
                pkAnkFlex.append(np.min(dat.RAnkleAngle_Sagittal[BDC[i]:BDC[i+1]]))
                PkAnkleExt.append(np.max(dat.RAnkleAngle_Sagittal[BDC[i]:BDC[i+1]]))
                ankleSagROM.append(np.max(dat.RAnkleAngle_Sagittal[BDC[i]:BDC[i+1]]) - np.min(dat.RAnkleAngle_Sagittal[BDC[i]:BDC[i+1]])) 
                
                dwn_pkAnkFlex.append(np.min(dat.RAnkleAngle_Sagittal[TDC[i]:BDC[i+1]]))
                up_pkAnkFlex.append(np.min(dat.RAnkleAngle_Sagittal[BDC[i]:TDC[i]])) 
                
                AnkSag_mean.append(np.mean(dat.RAnkleAngle_Sagittal[BDC[i]:BDC[i+1]]))
                AnkSag_sd.append(np.std(dat.RAnkleAngle_Sagittal[BDC[i]:BDC[i+1]]))
    
    
                #Ank Transv
                ExtAnkAngTrans.append(np.max(dat.RAnkleAngle_Transverse[BDC[i]:BDC[i+1]]))
                IntAnkAngTrans.append(np.min(dat.RAnkleAngle_Transverse[BDC[i]:BDC[i+1]])) 
                AnkTransAngrom.append(np.max(dat.RAnkleAngle_Transverse[BDC[i]:BDC[i+1]]) - np.min(dat.RAnkleAngle_Transverse[BDC[i]:BDC[i+1]]))
                
                dwn_ExtAnkAng.append(np.max(dat.RAnkleAngle_Transverse[TDC[i]:BDC[i+1]]))
                up_ExtAnkAng.append(np.max(dat.RAnkleAngle_Transverse[BDC[i]:TDC[i]])) 
                
                AnkTrans_mean.append(np.mean(dat.RAnkleAngle_Transverse[TDC[i]:BDC[i+1]]))
                AnkTrans_sd.append(np.std(dat.RAnkleAngle_Transverse[TDC[i]:BDC[i+1]])) 
                
                
                #Knee Frontal
                pkKneeABDang.append(np.min(dat.RKneeAngle_Frontal[BDC[i]:BDC[i+1]]))
                pkKneeADDang.append(np.max(dat.RKneeAngle_Frontal[BDC[i]:BDC[i+1]])) 
                kneeABDrom.append(np.max(dat.RKneeAngle_Frontal[BDC[i]:BDC[i+1]]) - np.min(dat.RKneeAngle_Frontal[BDC[i]:BDC[i+1]]))
                
                dwn_pkKneeABDang.append(np.max(dat.RKneeAngle_Frontal[TDC[i]:BDC[i+1]]))
                up_pkKneeABDang.append(np.max(dat.RKneeAngle_Frontal[BDC[i]:TDC[i]])) 

                KneeFront_mean.append(np.mean(dat.RKneeAngle_Frontal[TDC[i]:BDC[i+1]]))
                KneeFront_sd.append(np.std(dat.RKneeAngle_Frontal[TDC[i]:BDC[i+1]]))

                # Knee Sag
                pkKneeSagAng.append(np.max(dat.RKneeAngle_Sagittal[BDC[i]:BDC[i+1]])) 
                minKneeSagAng.append(np.min(dat.RKneeAngle_Sagittal[BDC[i]:BDC[i+1]])) 
                kneeSagROM.append(np.max(dat.RKneeAngle_Sagittal[BDC[i]:BDC[i+1]]) - np.min(dat.RKneeAngle_Sagittal[BDC[i]:BDC[i+1]])) 
    
                dwn_pkKneeFlex.append(np.min(dat.RKneeAngle_Sagittal[TDC[i]:BDC[i+1]]))
                up_pkKneeFlex.append(np.min(dat.RKneeAngle_Sagittal[BDC[i]:TDC[i]])) 
                
                KneeSag_mean.append(np.mean(dat.RKneeAngle_Sagittal[TDC[i]:BDC[i+1]]))
                KneeSag_sd.append(np.std(dat.RKneeAngle_Sagittal[TDC[i]:BDC[i+1]])) 
                
                #Knee Transv 
                pkKneeTransAng.append(np.max(dat.RKneeAngle_Transverse[BDC[i]:BDC[i+1]])) 
                IntKneeTransAng.append(np.min(dat.RKneeAngle_Transverse[BDC[i]:BDC[i+1]])) 
                ExtTransROM.append(np.max(dat.RKneeAngle_Transverse[BDC[i]:BDC[i+1]]) - np.min(dat.RKneeAngle_Transverse[BDC[i]:BDC[i+1]]))  
                
                dwn_pkKneeExtTrans.append(np.max(dat.RKneeAngle_Transverse[TDC[i]:BDC[i+1]]))
                up_pkKneeExtTrans.append(np.max(dat.RKneeAngle_Transverse[BDC[i]:TDC[i]])) 
            

                KneeTrans_mean.append(np.mean(dat.RKneeAngle_Transverse[TDC[i]:BDC[i+1]]))
                KneeTrans_sd.append(np.std(dat.RKneeAngle_Transverse[TDC[i]:BDC[i+1]]))
 
           
            
            except:
                 print(fName + str(i))

    
    except:
        print(fName)


# outcomes = []


outcomes = pd.DataFrame({'Subject':list(subNamelist), 'Config': list(config), 'Order':list(order) , #'Movement':list(movement),
                        
                          'PkAnkINVang':list(pkINVang), ' peakEVang':list(pkEVang),'ankFrontROM':list(ankFrontROM),
                          'dwn_pkEVang':list(dwn_pkEVang), 'up_pkEVang':list(up_pkEVang),

                         
                          'ankleSagROM':list(ankleSagROM) , 'pkAnkFlex':list(pkAnkFlex), 'PkAnkleExt':list(PkAnkleExt),
                          'dwn_pkAnkFlex':list(dwn_pkAnkFlex), 'up_pkAnkFlex':list(up_pkAnkFlex),
                          
                         
                          'AnkTransverseROM':list(AnkTransAngrom),'ExtAnkAngTrans':list(ExtAnkAngTrans), 'IntAnkAngTrans':list(IntAnkAngTrans), 
                          'dwn_ExtAnkAng':list(dwn_ExtAnkAng),'up_ExtAnkAng':list(up_ExtAnkAng),
                          
                        
                          'PkKneeABDang':list(pkKneeABDang),  'kneeABDrom':list(kneeABDrom), 
                          'dwn_pkKneeABDang':list(dwn_pkKneeABDang),'up_pkKneeABDang':list(up_pkKneeABDang),
                          
                        
                          'kneeSagROM':list(kneeSagROM),' pkKneeSagAng':list(pkKneeSagAng),'minKneeSagAng':list(minKneeSagAng),
                          'dwn_pkKneeFlex':list(dwn_pkKneeFlex),'up_pkKneeFlex':list(up_pkKneeFlex),
                        
                          'pkKneeTransAng ':list(pkKneeTransAng),'IntKneeTransAng':list(IntKneeTransAng), 'ExtTransROM':list(ExtTransROM), 
                          'dwn_pkKneeExtTrans':list(dwn_pkKneeExtTrans),'up_pkKneeExtTrans':list(up_pkKneeExtTrans), 
                          
                          'AnkFront_mean':list(AnkFront_mean),'AnkFront_sd':list(AnkFront_sd),
                          'AnkSag_mean':list(AnkSag_mean),'AnkSag_sd':list(AnkSag_sd),
                          'AnkTrans_mean':list(AnkTrans_mean),'AnkTrans_sd':list(AnkTrans_sd),
                          'KneeFront_mean':list(KneeFront_mean),'KneeFront_sd':list(KneeFront_sd),
                          'KneeSag_mean':list(KneeSag_mean),'KneeSag_sd':list(KneeSag_sd),
                          'KneeTrans_mean':list(KneeTrans_mean),'KneeTrans_sd':list(KneeTrans_sd)
                        
                        
                        })


save_on = 1

outfileName = fPath + '0_OvergroundKinematics.csv'
if save_on == 1:
    if os.path.exists(outfileName) == False:
    
        outcomes.to_csv(outfileName, header=True, index = False)

    else:
        outcomes.to_csv(outfileName, mode='a', header=False, index = False) 

