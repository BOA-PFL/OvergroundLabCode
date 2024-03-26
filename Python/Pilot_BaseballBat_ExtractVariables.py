# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 13:26:47 2022

@author: Kate.Harrison
"""

"""
This script extracts joint kinematic variables and distal foot work

"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks
import copy
import math
from tkinter import messagebox


fPath = 'Z:/Testing Segments/Baseball/Baseball_Pilot/Mocap/Bat/'
rf_fPath = 'Z:/Testing Segments/Baseball/Baseball_Pilot/DistalFootWork/Batting/'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]
rf_entries = [fName for fName in os.listdir(rf_fPath) if fName.endswith(fileExt)]



badFileList = []

for i in range(len(entries)):
    
    #i = 1
    fName = entries[i]
    rf_fName = rf_entries[i]

    plt.close('all')
    sub = fName.split(sep = '_')[0]
    hand = fName.split(sep = '_')[1]
    config = fName.split(sep = '_')[3].split(sep = ' ')[0]
    
    dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
    rf_dat = pd.read_csv(rf_fPath+rf_fName,sep='\t', skiprows = 8, header = 0)
    
    dat2 = pd.read_csv(fPath+fName,sep='\t', skiprows = 2, header = None, usecols= [2], nrows = 1)
    startTime = str(dat2[2].iloc[0][0:8])
    
    dat['PelvisRotationVel'] = np.gradient(dat.PelvisRotation, 0.005)
    
    dat['RightWristVel'] = np.gradient(dat.RightWristPosition_Y, 0.005)
    ### Find start (back foot steps on to plate) and end (front foot lifts off of plate) of each throw
    fig, ax = plt.subplots()
    #ax.plot(dat.FP2_GRF_Z, 'r', label = 'Rear foot')
    ax.plot(dat.FP3_GRF_Z, 'r--',label = 'Front foot')
    ax.set_ylabel("GRF (N)")
    ax2 = ax.twinx()
    ax2.plot(dat.RightWristVel, 'b--', label = 'RightWrist')
    ax2.set_ylim([-15, 15])
    ax2.set_ylabel('Wrist Velocity')
    fig.legend()
    
    ballContact = find_peaks(dat.RightWristVel, height = 4, distance = 50)[0]
    ax2.plot(ballContact, dat.RightWristVel[ballContact], 'kx', label = 'Ball Contact' )
    fig.legend()
    #sep = plt.ginput(n = -1, timeout=-1)
    

    leadfootContact = []
    leadfootLift = []
    
    Subject = []
    Config = []
    t0 = []
    batStartTime = []
    batEndTime = []
    kneeFlexFC = []
    pkKneeFlex = []
    kneeExtROM = []
    kneeFlexBC = []
    kneeExtVelBC = []
    pkKneeExtVel = []
    pelVel = []
    peakNegLeadDistalRFpower = []
    leadDistalRFnegWork = []
    peakNegRearDistalRFpower = []
    peakPosRearDistalRFpower = []
    rearDistalRFnegWork = []
    pBF = []
    pVGRF = []
    pAF = []
    
    
    
    for j in range(len(ballContact)):
        
        try: 
            #j = 0
            if (j == 0 or (ballContact[i] - ballContact[j-1]) > 500) and ballContact[j] >250:
            
          
                for k in range(len(dat.FP3_GRF_Z[ballContact[j]-250:ballContact[j]])):
                    if dat.FP3_GRF_Z[ballContact[j] - k] < 100 and dat.FP3_GRF_Z[ballContact[j] -k - 1] > 100:
                        leadfootLift = ballContact[j] - k
                
                for k in range(len(dat.FP3_GRF_Z[leadfootLift:ballContact[j]])):
                    if dat.FP3_GRF_Z[leadfootLift + k] < 100 and dat.FP3_GRF_Z[leadfootLift + k + 1] > 100:
                        leadfootContact = leadfootLift + k
                
                tmpdat = dat[leadfootLift:ballContact[j]].reset_index(drop = True)
                rf_tmpdat = rf_dat[leadfootLift:ballContact[j]].reset_index(drop = True)
                
                
                fig, ((ax, ax1), (ax2, ax3)) = plt.subplots(2, 2)
                ax.set_title('Vertical Ground Reaction Force')
                ax.plot(tmpdat.FP3_GRF_Z, color = 'b', label = 'Lead foot')
                ax.plot(tmpdat.FP2_GRF_Z, color = 'r', label = 'Rear Foot')
                ax.legend()
                    
       
            
                ax1.set_title('Knee Angle')
                if hand == 'Right':
                    ax1.plot(tmpdat.LKneeAngle_Sagittal, color = 'b', label = 'lead leg')
                    ax1.plot(tmpdat.RKneeAngle_Sagittal, color = 'r', label = 'Rear leg')
            
                else:
                    ax1.plot(tmpdat.RKneeAngle_Sagittal, color = 'b', label = 'lead leg')
                    ax1.plot(tmpdat.LKneeAngle_Sagittal, color = 'r', label = 'Rear leg')
                    
                    
                ax2.set_title('Pelvis Rotation Velocity')
                if hand == 'Right':
                    ax2.plot(tmpdat.PelvisRotationVel)
                    
                else:
                    ax2.plot((tmpdat.PelvisRotationVel)*-1)
                    
                    
                ax3.set_title('Lead Distal Rearfoot Work')
                if hand == 'Right':
                    ax3.plot(rf_tmpdat.RDistalFootPower_FP2, 'r')
                    ax3.plot(rf_tmpdat.LDistalFootPower_FP3, 'b')
                    
                else:
                    ax3.plot(rf_tmpdat.LDistalFootPower_FP2, 'r')
                    ax3.plot(rf_tmpdat.RDistalFootPower_FP3, 'b')
                    
                
                    
                plt.tight_layout()
                
                answer = messagebox.askyesno("Question","Is data clean?")
                
                if answer == False:
                    plt.close('all')
                    print('Adding file to bad file list')
                    badFileList.append(fName)
                
                if answer == True:
                    plt.close('all')
                    print('Estimating point estimates')
               
        
                    if hand == 'Right':
                        kneeFlexFC.append(tmpdat.LKneeAngle_Sagittal[leadfootContact - leadfootLift])
                        minkneeAng = np.min(tmpdat.LKneeAngle_Sagittal)
                        pkKneeFlex.append(minkneeAng)
                        kneeang_bc = tmpdat['LKneeAngle_Sagittal'].iloc[-1]
                        kneeFlexBC.append(kneeang_bc)
                        kneeExtROM.append(kneeang_bc - minkneeAng)
                        kneeExtVelBC.append(tmpdat['LKneeAngVel_Sagittal'].iloc[-1])
                        pkKneeExtVel.append(np.max(tmpdat.LKneeAngVel_Sagittal[leadfootContact - leadfootLift:]))
                        pBF.append(np.min(tmpdat.FP4_GRF_Y)*-1)
                        pVGRF.append(np.max(tmpdat.FP4_GRF_Z))
                        pAF.append(np.min(tmpdat.FP4_GRF_X)*-1)
                        
                    
                        pelVel.append(np.max(tmpdat.PelvisRotationVel))
                        
                        peakNegLeadDistalRFpower.append(np.min(rf_tmpdat.LDistalFootPower_FP3))
                        peakNegRearDistalRFpower.append(np.min(rf_tmpdat.RDistalFootPower_FP2))
                        peakPosRearDistalRFpower.append(np.max(rf_tmpdat.RDistalFootPower_FP2))
                        
                        negLeadFootPower = copy.deepcopy(rf_tmpdat.LDistalFootPower_FP3)
                        negLeadFootPower[negLeadFootPower > 0] = 0
                        leadDistalRFnegWork.append(np.sum(negLeadFootPower[leadfootContact-leadfootLift:]))
                        negRearFootPower = copy.deepcopy(rf_tmpdat.RDistalFootPower_FP2)
                        negRearFootPower[negRearFootPower > 0] = 0
                        rearDistalRFnegWork.append(np.sum(negRearFootPower[leadfootContact-leadfootLift:]))
                    

                    
                    else:
                        kneeFlexFC.append(tmpdat.RKneeAngle_Sagittal[leadfootContact - leadfootLift])
                        minkneeAng = np.min(tmpdat.RKneeAngle_Sagittal)
                        pkKneeFlex.append(minkneeAng)
                        kneeang_bc = tmpdat['RKneeAngle_Sagittal'].iloc[-1]
                        kneeFlexBC.append(kneeang_bc)
                        kneeExtROM.append(kneeang_bc - minkneeAng)
                        kneeExtVelBC.append(tmpdat['RKneeAngVel_Sagittal'].iloc[-1])
                        pkKneeExtVel.append(np.max(tmpdat.RKneeAngVel_Sagittal[leadfootContact - leadfootLift:]))
                        pBF.append(np.min(tmpdat.FP4_GRF_Y)*-1)
                        pVGRF.append(np.max(tmpdat.FP4_GRF_Z))
                        pAF.append(np.min(tmpdat.FP4_GRF_X)*-1)
                        
                        
                        pelVel.append(np.min(tmpdat.PelvisRotationVel)*-1)
                    
                        peakNegLeadDistalRFpower.append(np.min(rf_tmpdat.RDistalFootPower_FP3))
                        peakNegRearDistalRFpower.append(np.min(rf_tmpdat.LDistalFootPower_FP2))
                        peakPosRearDistalRFpower.append(np.max(rf_tmpdat.LDistalFootPower_FP2))
                        
                        negLeadFootPower = copy.deepcopy(rf_tmpdat.RDistalFootPower_FP3)
                        negLeadFootPower[negLeadFootPower > 0] = 0
                        leadDistalRFnegWork.append(np.sum(negLeadFootPower[leadfootContact-leadfootLift:]))
                        
                        negRearFootPower = copy.deepcopy(rf_tmpdat.LDistalFootPower_FP2)
                        negRearFootPower[negRearFootPower > 0] = 0
                        rearDistalRFnegWork.append(np.sum(negRearFootPower[leadfootContact-leadfootLift:]))
        
                    Subject.append(sub)
                    Config.append(config)
                    t0.append(startTime)
                    batStartTime.append(math.floor(tmpdat['Sample #'][0]/200))
                    batEndTime.append(math.ceil(tmpdat['Sample #'].iloc[-1]/200))
                
        except: 
                
                print('Adding file to bad file list')
                badFileList.append(fName)
        
    outcomes = pd.DataFrame({'Subject':list(Subject), 'Config': list(Config), 't0':list(t0), 'batStartTime':list(batStartTime), 'batEndTime':list(batEndTime),
                             'kneeFlexFC':list(kneeFlexFC), 'kneeFlexBC':list(kneeFlexBC),
                         'kneeExtVelBC':list(kneeExtVelBC), 'pkKneeFlex':list(pkKneeFlex), 'kneeExtROM':list(kneeExtROM),
                         'pkKneeExtVel':list(pkKneeExtVel), 'pelVel': list(pelVel),
                         'peakNegLeadDistalRFpower':list(peakNegLeadDistalRFpower),'peakNegRearDistalRFpower':list(peakNegRearDistalRFpower), 'peakPosRearDistalRFpower':list(peakPosRearDistalRFpower),
                         'leadDistalRFnegWork':list(leadDistalRFnegWork),'rearDistalRFnegWork':list(rearDistalRFnegWork),
                         'pBF':list(pBF), 'pVGRF':list(pVGRF), 'pAF':list(pAF)
                         
                         })

    outfileName = fPath + 'CompiledResults3.csv'


    if os.path.exists(outfileName) == False:
        outcomes.to_csv(outfileName, mode='a', header=True, index = False)

    else:
        outcomes.to_csv(outfileName, mode='a', header=False, index = False)

