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
import tkinter as tk
from tkinter import messagebox
from OvergroundFunctions import (delimitTrial, findLandings, findTakeoffs,
                                 loadProcessingDecisions, saveProcessingDecision)
import scipy.integrate as integrate

pd.options.mode.chained_assignment = None  # default='warn' set to warn for a lot of warnings

# Define constants and options
fThresh = 80 #below this force value will be set to 0.
save_on = 1 # turn this on for automatic saving of csv!!!! 
# 0 = no data check, nothing is asked or recorded
# 1 = ask only about trials with no recorded decision (the normal setting)
# 2 = re-review EVERY trial, including ones previously rejected. Use after
#     changing processing, when earlier decisions may no longer hold. This
#     mode is good for reruning files with a different threshold or examining
#     files after a different filter has been applied.
data_check = 1
ts_plot = 0 # turn this on for timeseries plotting of extracted variables

fPath = 'Z:/Testing Segments/Athletic/Court/2026_Performance_Court_FullShoeStability_Asics/Overground/'

fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt) and not fName.startswith('0_')]

# Names this script's decision file, 0_ProcessingDecisions_<scriptName>.csv.
# One data folder is often read by several scripts, and a trial that is no
# good for one analysis can be fine for another, so each keeps its own
# record rather than one script's rejection governing the rest.
scriptName = 'Agility'

# Data-quality decisions recorded by previous runs of this script. Loading
# these is what stops a trial being judged twice. Rejected files are left
# where they are so they can still be opened and looked at - it is this
# record, not the folder, that decides what gets processed.
decisions = loadProcessingDecisions(fPath, scriptName)

# Results from an out-of-date copy of this script will not match anyone
# else's. Asked only when nothing has been decided here yet: a decision file
# means the question was answered on an earlier run of this dataset.
if len(decisions) == 0:
    # Give this dialog its own window and put it in front. It is the first
    # thing the script does, so unlike the data check further down there is no
    # figure on screen to pull focus, and a borrowed default root can open the
    # box behind Spyder - which just looks like the script has hung.
    dialogRoot = tk.Tk()
    dialogRoot.withdraw()
    dialogRoot.attributes('-topmost', True)
    upToDate = messagebox.askyesno("Question", "Is this script up to date with main?",
                                   parent = dialogRoot)
    dialogRoot.destroy()
    # A plain error rather than SystemExit: these scripts get run a cell at a
    # time, and SystemExit can take the console with it. This stops just as
    # firmly, prints the reason, and leaves the console alone.
    if upToDate == False:
        raise RuntimeError('Pull this script from main before processing')

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




def powILM (Fz, Vz_COM, Fy, Vy_COM, Fx, Vx_COM):
    """
    This function finds power using the individual limb methods
    Parameters
    ----------
    Fz : as a series, list, or array
        vertical force from forceplate
   
    Fy : as a series, list, or array
        a/p force from forceplate
        
    Fx : as a series, list, or array
        medial/lateral force from forceplate
    
    Vz_COM : list
        vertical COM velocity
   
    Vy_COM : list
        a/p COM velocity
        
    Vx_COM : list
        medial/lateral COM velocity 
        
    Returns
    ----------
    pw : list 
        COM power
    """
    pw = ((Fz * Vz_COM) + (Fy * (Vy_COM)) + (Fx * Vx_COM))
    return pw

def findWork(start, stop, signal, frequency):
    """
    Parameters
    ----------
    start / stop : integer
        index of foot contact and toe off of task
   
    signal : array 
        power 
        
    frequency : float
        frequency data was collected

        
    Returns
    ----------
    Work : list 
        work
    """
    Work = integrate.trapezoid(signal[start:stop], dx = 1/frequency)
    return Work

def COMwk(totF_Z, totF_Y, totF_X, mass, landings):
    '''
    Finds COM work using ILM

    Parameters
    ----------
    totF_Z : series
        total force in Z for task
    totF_Y : series
        total force in Y for task
    totF_X : series
        total force in X for task
    mass : integer
        mass of subject
    landings : list
        landings detected for task

    '''
    acc_z = (totForce_z/mass) - 9.81
    acc_y = totForce_y/mass
    acc_x = totForce_x/mass
    
    velo_z = []
    velo_y = []
    velo_x = []
   # for ii, val in enumerate(landings[:(len(landings)-1)]):
    for ii, val in enumerate(zip(landings, takeoffs)):
        veloz = integrate.cumulative_trapezoid(acc_z[val[0]:val[1]], dx = 1/frequency)
        veloz = veloz - np.mean(veloz)
        velo_z.append(veloz)
        veloy = integrate.cumulative_trapezoid(acc_y[val[0]:val[1]], dx = 1/frequency)
        veloy = veloy - np.mean(veloy)
        velo_y.append(veloy)
        velox = integrate.cumulative_trapezoid(acc_x[val[0]:val[1]], dx = 1/frequency)
        velox = velox - np.mean(velox)
        velo_x.append(velox)
   
    
    pwr = []
    for ii, val in enumerate(zip(landings, takeoffs)):
        pwr.append(powILM(totForce_z[val[0]:val[1]-1], velo_z[ii], totForce_y[val[0]:val[1]-1], velo_y[ii], totForce_x[val[0]:val[1]-1], velo_x[ii]))
        
    #plot
    # plt.figure()
    # plt.title("COM Power")  
    # for ii in pwr:
    #     plt.plot(ii)
    
    PosPwr = []
    NegPwr = []
    pkPwr  =  []
   
    for series in (pwr):
        holdpos = []
        holdneg = []
        pkPwr.append(np.max(series))
        for val in series:
            if val < 0:
                holdpos.append(0)
                holdneg.append(val)
            else: 
                holdpos.append(val)
                holdneg.append(0)
        PosPwr.append(holdpos)
        NegPwr.append(holdneg) 
 
   
    
    PosWk = []
    NegWk = []
    for ii in range(len(pwr)):
        PosWk.append(findWork(0, int(len(PosPwr[ii])), PosPwr[ii], frequency)) 
        NegWk.append(findWork(0, int(len(NegPwr[ii])), NegPwr[ii], frequency)) 
    
    return PosPwr , NegPwr, PosWk, NegWk , pwr, pkPwr

def makeVizPlot(inputDF, inputLandings, inputTakeoffs, COMpwrILM):
    
    """
    Parameters
    ----------
    inputDF : Pandas DF
        Standard Agility export in dataframe.
    inputLandings : list
        list of landings from findLandings function.
    inputTakeoffs : list
        list of takeoffs from findTakeoffs function.
    COMpwrILM: list
        list of COM pwr

    Returns
    -------
    No variables; just a plot to inspect for clean kinematic/kinetic data.

    """
    fig, ((ax, ax1), (ax2, ax3), (ax4, ax5)) = plt.subplots(3, 2)
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

    for i in range(len(COMpwrILM)):
        ax4.plot(COMpwrILM[i],'k')
    ax4.set_title("Center of Mass Power") 
    ax4.set_xlabel('Indicies')
    ax4.set_ylabel('Power (W)')
    for i in range(len(inputLandings)):

        ax4.axvspan(inputLandings[i], inputTakeoffs[i], color = 'lightgray', alpha = 0.5)
    plt.show()
    

from scipy.interpolate import interp1d

def interpMet(metric, landings, takeoffs):
    fig = plt.figure()
    normMetric = []
    xx = np.array(np.linspace(0, 100, 101)) # Return evenly spaced numbers over a specified interval (0,100) with 101 
    for value1, value2 in zip(landings, takeoffs):
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
        
    plt.savefig(saveFolder + '/' + subName + '_'  + tmpMove + '_' + config1 + '_' + titleName +'.png')
    return fig  

    
    
################# initiate variables
CT = []

impulseZ = []
impulseX = []
peakGRFz = []
peakGRFx = []
peakPFmom = []
peakINVmom = []
peakEVmom = []
peakEVvel = []
peakKneeEXTmom = []
peakKneeADDmom = [] # Internal
kneeABDrom = []
eccWork = []
conWork = []
peakPower = []

impulse = []
jumpTime = []


subNamelist = []
config = []
movements = []
oSesh = []

badFileList = []

## save configuration names from files
for fName in entries:
    try:
        print(fName)
        # A trial rejected in a previous run is skipped. The file is still
        # there to open and look at: the recorded decision governs, not the
        # folder
        priorDecision = decisions.get(fName, '')
        if priorDecision == 'bad' and data_check != 2:
            print('Previously excluded, skipping: ' + fName)
            continue
        subName = fName.split('_')[0]
        config1 = fName.split('_')[1]
        tmpMove = fName.split('_')[2]
        tmpSesh = fName.split('_')[3][0]

        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        dat = dat.fillna(0)
        descr = pd.read_csv(fPath + "\\" + fName , sep = '\t' , nrows = 5, header = None , skiprows = [2])
        mass = float(descr.iloc[4,0])
        frequency = float(descr.iloc[2,0])
        
        landings = [] # erase landings and takeoffs from last loop
        takeoffs = []
        if (tmpMove == 'Skater') or (tmpMove == 'skater'):
            
            # Agility trials cross the whole runway, so the plot to click
            # on sums all four plates. delimitTrial used to sum them
            # itself, which is right here and wrong for every other
            # script in this folder.
            totForce = dat.FP1_GRF_Z + dat.FP2_GRF_Z + dat.FP3_GRF_Z + dat.FP4_GRF_Z
            dat = delimitTrial(dat, fName, fPath, totForce)
            # create vector of force from vertical signal from each file and make low values 0
            if np.max(abs(dat.FP3_GRF_Z)) > np.max(abs(dat.FP4_GRF_Z)):

                ZForce = dat.FP3_GRF_Z

                XForce = dat.FP3_GRF_X
                totForce_z = dat.FP3_GRF_Z 
                totForce_y = dat.FP3_GRF_Y         
                totForce_x = dat.FP3_GRF_X 
                
            else:
                ZForce = dat.FP4_GRF_Z
                XForce = dat.FP4_GRF_X 
                totForce_z = dat.FP4_GRF_Z 
                totForce_y = dat.FP4_GRF_Y         
                totForce_x = dat.FP4_GRF_X 
            
        
                
            if abs(np.min(XForce)) > abs(np.max(XForce)):
                XForce = XForce * -1
            
            #dat = delimitTrialSkate(dat)
            ZForce[ZForce<fThresh] = 0
            
         
            
            #find the landings from function above
            landings = findLandings(ZForce, fThresh)
            takeoffs = findTakeoffs(ZForce, fThresh)
            
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]]
            
            PosPwr, NegPwr, PosWk, NegWk, pwr, pkPwr = COMwk(totForce_z, totForce_y, totForce_x, mass, landings)
            
            ankPFmom = dat.RAnkleMoment_Sagittal
            ankIEmom = dat.RAnkleMoment_Frontal
            kFEmom = dat.RKneeMoment_Sagittal
            kAbAdmom = dat.RKneeMoment_Frontal
         
        elif (tmpMove == 'CMJ') or (tmpMove == 'cmj'):
            
            # Agility trials cross the whole runway, so the plot to click
            # on sums all four plates. delimitTrial used to sum them
            # itself, which is right here and wrong for every other
            # script in this folder.
            totForce = dat.FP1_GRF_Z + dat.FP2_GRF_Z + dat.FP3_GRF_Z + dat.FP4_GRF_Z
            dat = delimitTrial(dat, fName, fPath, totForce)
            

            ZForce = dat.FP2_GRF_Z
            ZForce[ZForce<fThresh] = 0
            
            XForce = dat.FP2_GRF_X 
            
            totForce_z = dat.FP2_GRF_Z + dat.FP1_GRF_Z
            totForce_y = dat.FP2_GRF_Y + dat.FP1_GRF_Y         
            totForce_x = dat.FP2_GRF_X + dat.FP1_GRF_X
            
            
            landings = findLandings(ZForce, fThresh)
            takeoffs = findTakeoffs(ZForce, fThresh)
            
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]] 
            
            PosPwr, NegPwr, PosWk, NegWk, pwr, pkPwr   =  COMwk(totForce_z, totForce_y, totForce_x, mass, landings)
            
            ankPFmom = dat.RAnkleMoment_Sagittal
            ankIEmom = dat.RAnkleMoment_Frontal
            kFEmom = dat.RKneeMoment_Sagittal
            kAbAdmom = dat.RKneeMoment_Frontal
           
           
        else:
            print('this movement is not included in Performance Test Analysis')
        
        if (tmpMove == 'CMJ') or (tmpMove == 'cmj') or (tmpMove == 'Skater') or (tmpMove == 'skater'):
            
            answer = True # if data check is off.
            if priorDecision == 'good' and data_check == 1:
                print('Previously accepted, not asking again: ' + fName)
            elif data_check >= 1:
                makeVizPlot(dat, landings, takeoffs, pwr)
                if ts_plot == 1: # plot all relavent metrics 
                    interpMet(totForce_z, landings, takeoffs)
                    interpMet(totForce_y, landings, takeoffs)
                    interpMet(totForce_x, landings, takeoffs)
                    interpMet(ankPFmom, landings, takeoffs)
                    interpMet(ankIEmom, landings, takeoffs)
                    interpMet(kFEmom, landings, takeoffs)
                    interpMet(kAbAdmom, landings, takeoffs)
                
                answer = messagebox.askyesno("Question","Is data clean?")

            # Record the decision straight away, inside the loop, so a run
            # that fails later keeps every decision made so far
            if priorDecision == '' or data_check == 2:
                if answer == False:
                    saveProcessingDecision(fPath, scriptName, fName, 'bad',
                                           Subject=subName, Config=config1,
                                           reason='rejected at the data check')
                else:
                    saveProcessingDecision(fPath, scriptName, fName, 'good',
                                           Subject=subName, Config=config1)

            if answer == False:
                plt.close('all')
                print('Adding file to bad file list')
                badFileList.append(fName)
            
            if answer == True:
                plt.close('all')
                print('Estimating point estimates')
                
                for i in range(len(landings)):
        
                    try:
                        tmpCT = round((takeoffs[i] - landings[i])/2) #to use as approximate for propulsive start
                        # frequency is read from the file header above and
                        # already used for the work and power terms. These
                        # three divided by a literal 200 instead.
                        CT.append((takeoffs[i] - landings[i])/frequency)
                        impulseZ.append(np.sum(ZForce[landings[i]:takeoffs[i]])/frequency)
                        impulseX.append(np.sum(XForce[landings[i]:takeoffs[i]])/frequency)
                        
                        peakGRFz.append(np.max(ZForce[landings[i]+tmpCT:takeoffs[i]])) #peak propulsive force approximated from 2nd half of contact time
                        peakGRFx.append(np.max(XForce[landings[i]+tmpCT:takeoffs[i]])) #peak propulsive force approximated from 2nd half of contact time
                    
                        peakPFmom.append(np.min(dat.RAnkleMoment_Sagittal[landings[i]:takeoffs[i]])*-1)
                        peakINVmom.append(np.max(dat.RAnkleMoment_Frontal[landings[i]:takeoffs[i]]))
                        peakEVmom.append(np.min(dat.RAnkleMoment_Frontal[landings[i]:takeoffs[i]]))
                        peakEVvel.append(np.min(dat.RAnkleAngVel_Frontal[landings[i]:takeoffs[i]])*-1)
                        peakKneeADDmom.append(np.max(dat.RKneeMoment_Frontal[landings[i]:takeoffs[i]])) # looking at an INTERNAL moment, so this is the peak external ABD moment
                        peakKneeEXTmom.append(np.max(dat.RKneeMoment_Sagittal[landings[i]:takeoffs[i]]))
                        kneeABDrom.append(np.max(dat.RKneeAngle_Frontal[landings[i]:takeoffs[i]]) - np.min(dat.RKneeAngle_Frontal[landings[i]:takeoffs[i]]))
                        
                        
                        eccWork.append(abs(NegWk[i]))
                        conWork.append(PosWk[i])
                        peakPower.append(pkPwr[i])
                        

                        subNamelist.append(subName)
                        config.append( config1 )
                        movements.append( tmpMove )
                        oSesh.append(tmpSesh)
        
                    except:
        
                        print(fName + str(i))

    except:
        print(fName)





outcomes = pd.DataFrame({'Subject':list(subNamelist), 'Config': list(config), 'Movement':list(movements), 'Order':list(oSesh),

                         'CT':list(CT), 'impulse_Z':list(impulseZ), 'impulse_X':list(impulseX), 
                         'peakGRF_Z':list(peakGRFz), 'peakGRF_X':list(peakGRFx), 'peakPFmom':list(peakPFmom),
                         'peakINVmom':list(peakINVmom), 'peakEVmom':list(peakEVmom), 'peakEVvel':list(peakEVvel),
                         'peakKneeEXTmom':list(peakKneeEXTmom), 
                         'kneeABDrom':list(kneeABDrom), 'PeakKneeAbMoment': list(peakKneeADDmom),
                         'eccWork':list(eccWork),'conWork':list(conWork), 'peakPower':list(peakPower) })



                       



outfileName = fPath + '0_CompiledAgilityData.csv'
if save_on == 1 and data_check < 2:
    np.save(fPath+'0_badFile.npy', badFileList)
    # Written fresh each run, never appended. Appending duplicates every
    # row when a study is re-processed after more data is collected, and a
    # trial rejected on a later pass keeps its old row beside the rejection.
    outcomes.to_csv(outfileName, header=True, index = False)
    
    






