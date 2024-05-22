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

pd.options.mode.chained_assignment = None  # default='warn' set to warn for a lot of warnings

# Define constants and options
fThresh = 80 #below this force value will be set to 0.
save_on = 0 # turn this on for automatic saving of csv!!!! 
debug = 1 #turn off to skip makeVizPlot
ts_plot = 0 # turn this on for timeseries plotting of extracted variables

fPath = 'Z:\\Testing Segments\\AgilityPerformanceData\\AS_Train_ExternalvsInternalPanels_Mech_Jan24\\Overground\\'

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
        veloz = integrate.cumtrapz(acc_z[val[0]:val[1]], dx = 1/frequency)
        veloz = veloz - np.mean(veloz)
        velo_z.append(veloz)
        veloy = integrate.cumtrapz(acc_y[val[0]:val[1]], dx = 1/frequency)
        veloy = veloy - np.mean(veloy)
        velo_y.append(veloy)
        velox = integrate.cumtrapz(acc_x[val[0]:val[1]], dx = 1/frequency)
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

    for pwr in range(len(COMpwrILM)):
        ax4.axvspan(COMpwrILM[pwr],'k')
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
peakKneeEXTmom = []
peakKneeADDmom = [] # Internal
kneeABDrom = []
eccWork = []
conWork = []
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
        
        #fName = entries[1]
        config1 = fName.split('_')[1]
        tmpMove = fName.split('_')[2]

        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        dat = dat.fillna(0)
        descr = pd.read_csv(fPath + "\\" + fName , sep = '\t' , nrows = 5, header = None , skiprows = [2])
        mass = float(descr.iloc[4,0])
        frequency = float(descr.iloc[2,0])
        
        landings = [] # erase landings and takeoffs from last loop
        takeoffs = []
        if (tmpMove == 'Skater') or (tmpMove == 'skater'):
            
            dat = delimitTrial(dat,fName)
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
            
            dat = delimitTrial(dat,fName)
            

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
            
            if debug == 1:
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
            else: answer = True
            
            
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
                        CT.append((takeoffs[i] - landings[i])/200)
                        impulseZ.append(np.sum(ZForce[landings[i]:takeoffs[i]])/200)
                        impulseX.append(np.sum(XForce[landings[i]:takeoffs[i]])/200)
                        
                        peakGRFz.append(np.max(ZForce[landings[i]+tmpCT:takeoffs[i]])) #peak propulsive force approximated from 2nd half of contact time
                        peakGRFx.append(np.max(XForce[landings[i]+tmpCT:takeoffs[i]])) #peak propulsive force approximated from 2nd half of contact time
                    
                        peakPFmom.append(np.min(dat.RAnkleMoment_Sagittal[landings[i]:takeoffs[i]])*-1)
                        peakINVmom.append(np.max(dat.RAnkleMoment_Frontal[landings[i]:takeoffs[i]]))
                        peakEVmom.append(np.min(dat.RAnkleMoment_Frontal[landings[i]:takeoffs[i]]))
                        peakKneeADDmom.append(np.max(dat.RKneeMoment_Frontal[landings[i]:takeoffs[i]])) # looking at an INTERNAL moment, so this is the peak external ABD moment
                        peakKneeEXTmom.append(np.max(dat.RKneeMoment_Sagittal[landings[i]:takeoffs[i]]))
                        kneeABDrom.append(np.max(dat.RKneeAngle_Frontal[landings[i]:takeoffs[i]]) - np.min(dat.RKneeAngle_Frontal[landings[i]:takeoffs[i]]))
                        
                        
                        eccWork.append(abs(NegWk[i]))
                        conWork.append(PosWk[i])
                        peakPower.append(pkPwr[i])
                        

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
                         'kneeABDrom':list(kneeABDrom), 'PeakKneeAbMoment': list(peakKneeADDmom),'eccWork':list(eccWork),'conWork':list(conWork), 'peakPower':list(peakPower) })



                       



save_on = 1
if save_on == 1:
    np.save(fPath+'0_badFile.npy', badFileList)
    outfileName = fPath + 'CompiledAgilityDataTest.csv'
    outcomes.to_csv(outfileName, index = False)





