# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 16:34:25 2022

@author: Kate.Harrison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks
import copy
import math
from tkinter import messagebox


fPath = 'C:/Users/Kate.Harrison/Boa Technology Inc/PFL Team - General/Testing Segments/Baseball/Baseball_Pilot/Mocap/Throw/'
rf_fPath = 'C:/Users/Kate.Harrison/Boa Technology Inc/PFL Team - General/Testing Segments/Baseball/Baseball_Pilot/DistalFootWork/Throw/'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]
rf_entries = [fName for fName in os.listdir(rf_fPath) if fName.endswith(fileExt)]

badFileList = []


for i in range(len(entries)):
    
    i = 1
    fName = entries[i]
    rf_fName = rf_entries[i]
    #plt.close('all')

    sub = fName.split(sep = '_')[0]
    hand = fName.split(sep = '_')[1]
    config = fName.split(sep = '_')[3].split(sep = ' ')[0]
    
    dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
    rf_dat = pd.read_csv(rf_fPath+rf_fName,sep='\t', skiprows = 8, header = 0)
    
    #dat2 = pd.read_csv(fPath+fName,sep='\t', skiprows = 1, header = 0, names = ['x1', 'x2', 'time', 'x4'], usecols= ['time'], nrows = 1)
    
    dat2 = pd.read_csv(fPath+fName,sep='\t', skiprows = 2, header = None, usecols= [2], nrows = 1)
    startTime = str(dat2[2].iloc[0][0:8])

    dat['PelvisRotationVel'] = np.gradient(dat.PelvisRotation, 0.005)
    
    dat.LeftFootPosition[dat.LeftFootPosition >6] = 'Nan'
    dat.LeftFootVel = np.gradient(dat.LeftFootPosition, 0.005)
    dat.RightFootPosition[dat.RightFootPosition >6] = 'Nan'
    dat.RightFootVel = np.gradient(dat.RightFootPosition, 0.005)
   
    plt.figure()
    
    if hand == 'Right':
        
        plt.plot(dat.LeftFootVel)
        footFwd= find_peaks(dat.LeftFootVel, height = 1)
        pkVels = dat.LeftFootVel[footFwd[0]]
        z = (pkVels - np.mean(pkVels))/np.std(pkVels)
        pkVels = pkVels*(z<2)
        pkVels = pd.DataFrame(pkVels[pkVels != 0])
        pkVels.columns = ['pkVels']
        pkVels = pkVels.sort_values(by = 'pkVels', ascending = False).head(12)
        footVelThresh = np.mean(pkVels)*0.8
        throwStart = find_peaks(dat.LeftFootVel, height = footVelThresh[0], distance = 1000)[0]
        plt.plot(throwStart, dat.LeftFootVel[throwStart], 'kx')
       
        
    if hand == 'Left':
       plt.plot(dat.RightFootVel)
       footFwd= find_peaks(dat.RightFootVel, height = 1)
       pkVels = dat.RightFootVel[footFwd[0]]
       z = (pkVels - np.mean(pkVels))/np.std(pkVels)
       pkVels = pkVels*(z<2)
       pkVels = pd.DataFrame(pkVels[pkVels != 0])
       pkVels.columns = ['pkVels']
       pkVels = pkVels.sort_values(by = 'pkVels', ascending = False).head(12)
       footVelThresh = np.mean(pkVels)*0.8
       throwStart = find_peaks(dat.RightFootVel, height = footVelThresh[0], distance = 1000)[0]
       plt.plot(throwStart, dat.RightFootVel[throwStart], 'kx')
        
   

    
    leadfootContact = []
    ballRelease = []
    followThru = []
    
    Subject = []
    Config = []
    t0 = []
    throwStartTime = []
    throwEndTime = []
    minKneeFlex = []
    kneeFlexBR = []
    kneeExtROM = []
    pkKneeExtVel = []
    pelVel = []
    peakNegLeadDistalRFpower = []
    leadDistalRFnegWork = []
    peakNegRearDistalRFpower = []
    rearDistalRFnegWork = []
    peakPosRearDistalRFpower = []
    pBF = []
    pVGRF = []
    pAF = []
    
    
    

    
   
    
    for j in range(len(throwStart)):
        
        
        try:
           
            j = 9
            
            td = []
            for k in range(len(dat.FP4_GRF_Z[throwStart[j]:throwStart[j]+400])):
                    if dat.FP4_GRF_Z[throwStart[j]+k] < 40 and dat.FP4_GRF_Z[throwStart[j]+k+1] > 40:
                        td.append(throwStart[j]+k)
            leadfootContact = (td[0])
            #plt.plot(dat.RightShoulderRotation)
                
            
          
            # # Find ball release (1 frame ahead of where wrist passes elbow in anterior direction)
            if hand == 'Right':
                br = []
                for f in range(len(dat.RightWristElbowDiff_Y[leadfootContact +25:leadfootContact+150])):
                    if dat.RightWristElbowDiff_Y[leadfootContact + 25+f] <=0 and dat.RightWristElbowDiff_Y[leadfootContact + 25+ f + 1] > 0:
                        br.append(leadfootContact + 25 + f + 1)
                ballRelease = br[0]
                
            else:
                br = []
                for f in range(len(dat.LeftWristElbowDiff_Y[leadfootContact+25:leadfootContact+150])):
                    if dat.LeftWristElbowDiff_Y[leadfootContact + 25 + f] <=0 and dat.LeftWristElbowDiff_Y[leadfootContact + 25 + f + 1] > 0:
                        br.append(leadfootContact + 25 + f + 1)
                ballRelease = br[0]
                
            
            tmpdat = dat[throwStart[j]:ballRelease].reset_index(drop = True)
            rf_tmpdat = rf_dat[throwStart[j]:ballRelease].reset_index(drop = True)
            
            fig, ((ax, ax1), (ax2, ax3)) = plt.subplots(2, 2)
            
            
            # if hand == 'Right':
            #     ax.plot(tmpdat.RightWristElbowDiff_Y, 'r')
            # if hand == 'Left':
            #     ax.plot(tmpdat.LeftWristElbowDiff_Y, 'r')
            # ax.set_title('Wrist vs. Elbow Postition')
            # ax.set_ylabel('distance (m)')
            
            ax.plot(tmpdat.FP4_GRF_Y)
            ax.set_title('Lead Foot Braking Force')
            ax.set_ylabel('Force (N)')
            
            
            if hand =='Right':
                ax1.plot(rf_tmpdat.LDistalFootPower_FP4, 'b', label = 'Lead foot')
                ax1.plot(rf_tmpdat.RDistalFootPower_FP2, 'r', label = 'Rear foot')
            if hand =='Left':
                ax1.plot(rf_tmpdat.RDistalFootPower_FP4, 'b', label = 'Lead foot')
                ax1.plot(rf_tmpdat.LDistalFootPower_FP2, 'r', label = "Rear foot")
            ax1.set_title('Lead Distal Rearfoot Power')
            ax1.set_ylabel('W')
            ax1.legend()
            
        
            
            if hand == 'Right': 
            
                ax2.plot(tmpdat.RKneeAngle_Sagittal, 'r', label = 'Rear foot')
                ax2.plot(tmpdat.LKneeAngle_Sagittal, 'b', label = 'Lead foot')
            
            else:
                ax2.plot(tmpdat.LKneeAngle_Sagittal, 'r', 'Rear foot' )
                ax2.plot(tmpdat.RKneeAngle_Sagittal, 'b', 'Lead foot')
            ax2.set_title('Sagittal Plane knee angle')
            ax2.set_ylabel('degrees')
            ax2.set_xlabel('frames')
            ax2.legend()
                
            
            if hand == 'Right':
                ax3.plot(tmpdat.PelvisRotationVel)
                
            else:
                ax3.plot((tmpdat.PelvisRotationVel)*-1)
            ax3.set_title('Pelvis Rotation Velocity')
            ax3.set_ylabel('deg/s')
            ax3.set_xlabel('frames')
            
            plt.tight_layout()
            
            answer = messagebox.askyesno("Question","Is data clean?")
            
            tmpdat['Time'] = tmpdat['Sample #'] /1000 
            tmpdat['Time'] = tmpdat.Time - tmpdat.Time[0]
            
            plt.figure('fy')
            plt.plot(tmpdat.Time, tmpdat.FP4_GRF_Y, label = 'BOA')
            plt.xlabel('Time (s)')
            plt.ylabel('Force (N)')
            
            plt.figure('fy')
            plt.plot(tmpdat.Time, tmpdat.FP4_GRF_Y, 'r', label = 'Lace')
            plt.legend()
            
            
            plt.xlabel('Time (s)')
            plt.ylabel('Angular velocity (deg/s)')
            
            plt.figure('Check')
            plt.plot(rf_tmpdat.LDistalFootPower_FP4)
            
            if answer == False:
                plt.close('all')
                print('Adding file to bad file list')
                badFileList.append(fName)
            
            if answer == True:
                plt.close('all')
                print('Estimating point estimates')
        
            
                if hand == 'Right':
                    kneeFlexmin = np.min(tmpdat.LKneeAngle_Sagittal[leadfootContact-throwStart[j]:])
                    minKneeFlex.append(kneeFlexmin)
                    kneeangBR = tmpdat['LKneeAngle_Sagittal'].iloc[-1]
                    kneeFlexBR.append( kneeangBR)
                    kneeExtROM.append( kneeangBR - kneeFlexmin)
                    pkKneeExtVel.append(np.max(tmpdat.LKneeAngVel_Sagittal[leadfootContact-throwStart[j]:]))
                    pBF.append(np.min(tmpdat.FP4_GRF_Y)*-1)
                    pVGRF.append(np.max(tmpdat.FP4_GRF_Z))
                    pAF.append(np.min(tmpdat.FP4_GRF_X)*-1)
                    pelVel.append(np.max(tmpdat.PelvisRotationVel))
                    peakNegLeadDistalRFpower.append(np.min(rf_tmpdat.LDistalFootPower_FP4))
                    peakNegRearDistalRFpower.append(np.min(rf_tmpdat.RDistalFootPower_FP2))
                    peakPosRearDistalRFpower.append(np.max(rf_tmpdat.RDistalFootPower_FP2))
                    
                    negLeadFootPower = copy.deepcopy(rf_tmpdat.LDistalFootPower_FP4)
                    negLeadFootPower[negLeadFootPower > 0] = 0
                    leadDistalRFnegWork.append(np.sum(negLeadFootPower[leadfootContact-throwStart[j]:]))
                    
                    negRearFootPower = copy.deepcopy(rf_tmpdat.RDistalFootPower_FP2)
                    negRearFootPower[negRearFootPower > 0] = 0
                    rearDistalRFnegWork.append(np.sum(negRearFootPower[leadfootContact-throwStart[j]:]))
                
        
                if hand == 'Left':
                    kneeFlexmin = np.min(tmpdat.RKneeAngle_Sagittal[leadfootContact-throwStart[j]:])
                    minKneeFlex.append(kneeFlexmin)
                    kneeangBR = tmpdat['LKneeAngle_Sagittal'].iloc[-1]
                    kneeFlexBR.append( kneeangBR)
                    kneeExtROM.append( kneeangBR - kneeFlexmin)
                    pkKneeExtVel.append(np.max(tmpdat.RKneeAngVel_Sagittal[leadfootContact-throwStart[j]:]))
                    pBF.append(np.min(tmpdat.FP4_GRF_Z)*-1)
                    pVGRF.append(np.max(tmpdat.FP4_GRF_Z))
                    pAF.append(np.max(tmpdat.FP4_GRF_X))
                    pelVel.append(np.min(tmpdat.PelvisRotationVel)*-1)
                    peakNegLeadDistalRFpower.append(np.min(rf_tmpdat.RDistalFootPower_FP4))
                    peakNegRearDistalRFpower.append(np.min(rf_tmpdat.LDistalFootPower_FP2))
                    peakPosRearDistalRFpower.append(np.max(rf_tmpdat.LDistalFootPower_FP2))
                    
                    negLeadFootPower = copy.deepcopy(rf_tmpdat.RDistalFootPower_FP4)
                    negLeadFootPower[negLeadFootPower > 0] = 0
                    leadDistalRFnegWork.append(np.sum(negLeadFootPower[leadfootContact-throwStart[j]:]))
                    
                    negRearFootPower = copy.deepcopy(rf_tmpdat.LDistalFootPower_FP2)
                    negRearFootPower[negRearFootPower > 0] = 0
                    rearDistalRFnegWork.append(np.sum(negRearFootPower[leadfootContact-throwStart[j]:]))
                                 
        
        
                Subject.append(sub)
                Config.append(config)
                t0.append(startTime)
                throwStartTime.append(math.floor(tmpdat['Sample #'][0]/200))
                throwEndTime.append(math.ceil(tmpdat['Sample #'].iloc[-1]/200))
              
            
            
        except:
            
            badFileList.append(fName)
         
            
        
    outcomes = pd.DataFrame({'Subject':list(Subject), 'Config': list(Config), 't0':list(t0), 'throwStart':list(throwStartTime), 'throwEnd':list(throwEndTime),                            
                             'kneeFlexBR':list(kneeFlexBR), 
                         'pkKneeExtVel':list(pkKneeExtVel), 'pelVel': list(pelVel), 
                         'pkKneeFlex':list(minKneeFlex), 'kneeExtROM': list(kneeExtROM), 
                         'peakNegLeadDistalRFpower':list(peakNegLeadDistalRFpower),'peakNegRearDistalRFpower':list(peakNegRearDistalRFpower), 'peakPosRearDistalRFpower':list(peakPosRearDistalRFpower),
                         'leadDistalRFnegWork':list(leadDistalRFnegWork),'rearDistalRFnegWork':list(rearDistalRFnegWork),
                         'pBF':list(pBF), 'pVGRF':list(pVGRF), 'pAF':list(pAF)
                        
                         })

    outfileName = fPath + 'CompiledResults7.csv'

    if os.path.exists(outfileName) == False:
        outcomes.to_csv(outfileName, mode='a', header=True, index = False)

    else:
        outcomes.to_csv(outfileName, mode='a', header=False, index = False)
