# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 13:26:47 2022

@author: Kate.Harrison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks
import copy
import math

fPath = 'C:/Users/Kate.Harrison/Boa Technology Inc/PFL Team - General/Testing Segments/Baseball/Mocap/Bat/'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]


for fName in entries:
    fName = entries[0]

    plt.close('all')
    sub = fName.split(sep = '_')[0]
    hand = fName.split(sep = '_')[1]
    config = fName.split(sep = '_')[3].split(sep = ' ')[0]
    
    dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
    
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
    pBF = []
    pPF = []
    brakeBC = []
    brakeImp = []
    pVGRF =[]
    vGRF_bc = []
    minFreeMoment = []
    maxFreeMoment = []
    pelVel = []
    
    
    leadAnklePosWork = []
    leadAnklePeakPosPower = []
    leadAnkleNegWork = []
    leadAnklePeakNegPower = []
    
    leadKneePosWork = []
    leadKneePeakPosPower = []
    leadKneeNegWork = []
    leadKneePeakNegPower = []
    
    leadHipPosWork = []
    leadHipPeakPosPower = []
    leadHipNegWork = []
    leadHipPeakNegPower = []
    
    rearAnklePosWork = []
    rearAnklePeakPosPower = []
    rearAnkleNegWork = []
    rearAnklePeakNegPower = []
    
    rearKneePosWork = []
    rearKneePeakPosPower = []
    rearKneeNegWork = []
    rearKneePeakNegPower = []
    
    rearHipPosWork = []
    rearHipPeakPosPower = []
    rearHipNegWork = []
    rearHipPeakNegPower = []
    
    for i in range(len(ballContact)):
        
        try: 
            i = 0
            if (i == 0 or (ballContact[i] - ballContact[i-1]) > 500) and ballContact[i] >250:
            
          
                for k in range(len(dat.FP3_GRF_Z[ballContact[i]-250:ballContact[i]])):
                    if dat.FP3_GRF_Z[ballContact[i] - k] < 100 and dat.FP3_GRF_Z[ballContact[i] -k - 1] > 100:
                        leadfootLift = ballContact[i] - k
                
                for k in range(len(dat.FP3_GRF_Z[leadfootLift:ballContact[i]])):
                    if dat.FP3_GRF_Z[leadfootLift + k] < 100 and dat.FP3_GRF_Z[leadfootLift + k + 1] > 100:
                        leadfootContact = leadfootLift + k
                
                tmpdat = dat[leadfootLift:ballContact[i]].reset_index(drop = True)
                
                plt.figure('Vertical Ground Reaction Force')
                plt.plot(tmpdat.FP3_GRF_Z, color = 'b', label = 'Lead foot')
                plt.plot(tmpdat.FP2_GRF_Z, color = 'r', label = 'Rear Foot')
                if i == 0:
                    plt.legend()
       
                plt.figure('AP GRF')
                plt.plot(tmpdat.FP3_GRF_Y, color = 'b', label = 'Lead foot')
                plt.plot(tmpdat.FP2_GRF_Y, color = 'r',  label = 'Rear foot')
                if i == 0:
                    plt.legend()
        
                plt.figure('Free Moment')
                plt.plot(tmpdat.FreeMoment_FP3, color = 'b', label = 'lead foot')
                plt.plot(tmpdat.FreeMoment_FP2, color = 'r', label = 'Rear foot')
                if i == 0:
                    plt.legend()
            
                plt.figure('Knee Angle')
                if hand == 'Right':
                    plt.plot(tmpdat.LKneeAngle_Sagittal, color = 'b', label = 'lead leg')
                    plt.plot(tmpdat.RKneeAngle_Sagittal, color = 'r', label = 'Rear leg')
            
                else:
                    plt.plot(tmpdat.RKneeAngle_Sagittal, color = 'b', label = 'lead leg')
                    plt.plot(tmpdat.LKneeAngle_Sagittal, color = 'r', label = 'Rear leg')
            
                if i == 0:
                    plt.legend()
                    
                    
                plt.figure('Pelvis Rotation Velocity')
                if hand == 'Right':
                    plt.plot(tmpdat.PelvisRotationVel)
                    
                else:
                    plt.plot((tmpdat.PelvisRotationVel)*-1)
                if i == 0:
                    plt.legend()
                    
                    
                plt.figure('Ankle Power')
                if hand == 'Right':
                    plt.plot(tmpdat.RightAnklePower, 'r')
                    plt.plot(tmpdat.LeftAnklePower, 'b')
                    
                else:
                    plt.plot(tmpdat.LeftAnklePower, 'r')
                    plt.plot(tmpdat.RightAnklePower, 'b')
                    
                if i == 0:
                    plt.legend()
                    
                    
                plt.figure('Knee Power')
                if hand == 'Right':
                    plt.plot(tmpdat.RightKneePower, 'r')
                    plt.plot(tmpdat.LeftKneePower, 'b')
                    
                else:
                    plt.plot(tmpdat.LeftKneePower, 'r')
                    plt.plot(tmpdat.RightKneePower, 'b')
                    
                if i == 0:
                    plt.legend()
                    
                plt.figure('Hip Power')
                if hand == 'Right':
                    plt.plot(tmpdat.RHipPower, 'r')
                    plt.plot(tmpdat.LHipPower, 'b')
                    
                else:
                    plt.plot(tmpdat.LHipPower, 'r')
                    plt.plot(tmpdat.RHipPower, 'b')
                    
                if i == 0:
                    plt.legend()
        
                if hand == 'Right':
                    kneeFlexFC.append(tmpdat.LKneeAngle_Sagittal[leadfootContact - leadfootLift])
                    minkneeAng = np.min(tmpdat.LKneeAngle_Sagittal)
                    pkKneeFlex.append(minkneeAng)
                    kneeang_bc = tmpdat['LKneeAngle_Sagittal'].iloc[-1]
                    kneeFlexBC.append(kneeang_bc)
                    kneeExtROM.append(kneeang_bc - minkneeAng)
                    kneeExtVelBC.append(tmpdat['LKneeAngVel_Sagittal'].iloc[-1])
                    pkKneeExtVel.append(np.max(tmpdat.LKneeAngVel_Sagittal))
                    minFreeMoment.append(np.min(tmpdat.FreeMoment_FP3))
                    maxFreeMoment.append(np.max(tmpdat.FreeMoment_FP3))
                    pelVel.append(np.max(tmpdat.PelvisRotationVel))
                    
                    
                    leadAnklePosPower = copy.deepcopy(tmpdat.LeftAnklePower)
                    leadAnklePosPower[leadAnklePosPower<0] = 0
                    leadAnklePosWork.append(np.sum(leadAnklePosPower))
                    leadAnklePeakPosPower.append(np.max(tmpdat.LeftAnklePower))
                    
                    leadAnkleNegPower = copy.deepcopy(tmpdat.LeftAnklePower)
                    leadAnkleNegPower[leadAnkleNegPower>0] = 0
                    leadAnkleNegWork.append(np.sum(leadAnkleNegPower))
                    leadAnklePeakNegPower.append(np.min(tmpdat.LeftAnklePower))
                    
                    leadKneePosPower = copy.deepcopy(tmpdat.LeftKneePower)
                    leadKneePosPower[leadKneePosPower<0] = 0
                    leadKneePosWork.append(np.sum(leadKneePosPower))
                    leadKneePeakPosPower.append(np.max(tmpdat.LeftKneePower))
                    
                    leadKneeNegPower = copy.deepcopy(tmpdat.LeftKneePower)
                    leadKneeNegPower[leadKneeNegPower>0] = 0
                    leadKneeNegWork.append(np.sum(leadKneeNegPower))
                    leadKneePeakNegPower.append(np.min(tmpdat.LeftKneePower))
                    
                    leadHipPosPower = copy.deepcopy(tmpdat.LHipPower)
                    leadHipPosPower[leadHipPosPower<0] = 0
                    leadHipPosWork.append(np.sum(leadHipPosPower))
                    leadHipPeakPosPower.append(np.max(tmpdat.LHipPower))
                    
                    leadHipNegPower = copy.deepcopy(tmpdat.LHipPower)
                    leadHipNegPower[leadHipNegPower>0] = 0
                    leadHipNegWork.append(np.sum(leadHipNegPower))
                    leadHipPeakNegPower.append(np.min(tmpdat.LHipPower))
                    
                    
                    rearAnklePosPower = copy.deepcopy(tmpdat.RightAnklePower)
                    rearAnklePosPower[rearAnklePosPower<0] = 0
                    rearAnklePosWork.append(np.sum(rearAnklePosPower))
                    rearAnklePeakPosPower.append(np.max(tmpdat.RightAnklePower))
                    
                    rearAnkleNegPower = copy.deepcopy(tmpdat.RightAnklePower)
                    rearAnkleNegPower[rearAnkleNegPower>0] = 0
                    rearAnkleNegWork.append(np.sum(rearAnkleNegPower))
                    rearAnklePeakNegPower.append(np.min(tmpdat.RightAnklePower))
                    
                    rearKneePosPower = copy.deepcopy(tmpdat.RightKneePower)
                    rearKneePosPower[rearKneePosPower<0] = 0
                    rearKneePosWork.append(np.sum(rearKneePosPower))
                    rearKneePeakPosPower.append(np.max(tmpdat.RightKneePower))
                    
                    rearKneeNegPower = copy.deepcopy(tmpdat.RightKneePower)
                    rearKneeNegPower[rearKneeNegPower>0] = 0
                    rearKneeNegWork.append(np.sum(rearKneeNegPower))
                    rearKneePeakNegPower.append(np.min(tmpdat.RightKneePower))
                    
                    rearHipPosPower = copy.deepcopy(tmpdat.RHipPower)
                    rearHipPosPower[rearHipPosPower<0] = 0
                    rearHipPosWork.append(np.sum(rearHipPosPower))
                    rearHipPeakPosPower.append(np.max(tmpdat.RHipPower))
                    
                    rearHipNegPower = copy.deepcopy(tmpdat.RHipPower)
                    rearHipNegPower[rearHipNegPower>0] = 0
                    rearHipNegWork.append(np.sum(rearHipNegPower))
                    rearHipPeakNegPower.append(np.min(tmpdat.RHipPower))
                    
                else:
                    kneeFlexFC.append(tmpdat.RKneeAngle_Sagittal[leadfootContact - leadfootLift])
                    minkneeAng = np.min(tmpdat.RKneeAngle_Sagittal)
                    pkKneeFlex.append(minkneeAng)
                    kneeang_bc = tmpdat['RKneeAngle_Sagittal'].iloc[-1]
                    kneeFlexBC.append(kneeang_bc)
                    kneeExtROM.append(kneeang_bc - minkneeAng)
                    kneeExtVelBC.append(tmpdat['RKneeAngVel_Sagittal'].iloc[-1])
                    pkKneeExtVel.append(np.max(tmpdat.RKneeAngVel_Sagittal))
                    minFreeMoment.append(np.max(tmpdat.FreeMoment_FP3))
                    maxFreeMoment.append(np.min(tmpdat.FreeMoment_FP3))
                    pelVel.append(np.min(tmpdat.PelvisRotationVel)*-1)
                    
                    leadAnklePosPower = copy.deepcopy(tmpdat.RightAnklePower)
                    leadAnklePosPower[leadAnklePosPower<0] = 0
                    leadAnklePosWork.append(np.sum(leadAnklePosPower))
                    leadAnklePeakPosPower.append(np.max(tmpdat.RightAnklePower))
                    
                    leadAnkleNegPower = copy.deepcopy(tmpdat.RightAnklePower)
                    leadAnkleNegPower[leadAnkleNegPower>0] = 0
                    leadAnkleNegWork.append(np.sum(leadAnkleNegPower))
                    leadAnklePeakNegPower.append(np.min(tmpdat.RightAnklePower))
                    
                    leadKneePosPower = copy.deepcopy(tmpdat.RightKneePower)
                    leadKneePosPower[leadKneePosPower<0] = 0
                    leadKneePosWork.append(np.sum(leadKneePosPower))
                    leadKneePeakPosPower.append(np.max(tmpdat.RightKneePower))
                    
                    leadKneeNegPower = copy.deepcopy(tmpdat.RightKneePower)
                    leadKneeNegPower[leadKneeNegPower>0] = 0
                    leadKneeNegWork.append(np.sum(leadKneeNegPower))
                    leadKneePeakNegPower.append(np.min(tmpdat.RightKneePower))
                    
                    leadHipPosPower = copy.deepcopy(tmpdat.RHipPower)
                    leadHipPosPower[leadHipPosPower<0] = 0
                    leadHipPosWork.append(np.sum(leadHipPosPower))
                    leadHipPeakPosPower.append(np.max(tmpdat.RHipPower))
                    
                    leadHipNegPower = copy.deepcopy(tmpdat.RHipPower)
                    leadHipNegPower[leadHipNegPower>0] = 0
                    leadHipNegWork.append(np.sum(leadHipNegPower))
                    leadHipPeakNegPower.append(np.min(tmpdat.RHipPower))
                    
                    
                    rearAnklePosPower = copy.deepcopy(tmpdat.LeftAnklePower)
                    rearAnklePosPower[rearAnklePosPower<0] = 0
                    rearAnklePosWork.append(np.sum(rearAnklePosPower))
                    rearAnklePeakPosPower.append(np.max(tmpdat.LeftAnklePower))
                    
                    rearAnkleNegPower = copy.deepcopy(tmpdat.LeftAnklePower)
                    rearAnkleNegPower[rearAnkleNegPower>0] = 0
                    rearAnkleNegWork.append(np.sum(rearAnkleNegPower))
                    rearAnklePeakNegPower.append(np.min(tmpdat.LeftAnklePower))
                    
                    rearKneePosPower = copy.deepcopy(tmpdat.LeftKneePower)
                    rearKneePosPower[rearKneePosPower<0] = 0
                    rearKneePosWork.append(np.sum(rearKneePosPower))
                    rearKneePeakPosPower.append(np.max(tmpdat.LeftKneePower))
                    
                    rearKneeNegPower = copy.deepcopy(tmpdat.LeftKneePower)
                    rearKneeNegPower[rearKneeNegPower>0] = 0
                    rearKneeNegWork.append(np.sum(rearKneeNegPower))
                    rearKneePeakNegPower.append(np.min(tmpdat.LeftKneePower))
                    
                    rearHipPosPower = copy.deepcopy(tmpdat.LHipPower)
                    rearHipPosPower[rearHipPosPower<0] = 0
                    rearHipPosWork.append(np.sum(rearHipPosPower))
                    rearHipPeakPosPower.append(np.max(tmpdat.LHipPower))
                    
                    rearHipNegPower = copy.deepcopy(tmpdat.LHipPower)
                    rearHipNegPower[rearHipNegPower>0] = 0
                    rearHipNegWork.append(np.sum(rearHipNegPower))
                    rearHipPeakNegPower.append(np.min(tmpdat.LHipPower))
                    
                    
                pBF.append(np.min(tmpdat.FP3_GRF_Y))
                pPF.append(np.max(tmpdat.FP2_GRF_Y))
                brakeBC.append(tmpdat['FP3_GRF_Y'].iloc[-1])
                tmpdat.FP3_GRF_Y[tmpdat.FP3_GRF_Y>0] = 0
                brakeImp.append(np.sum(tmpdat.FP3_GRF_Y)/200)
                pVGRF.append(np.max(tmpdat.FP3_GRF_Z))
                vGRF_bc.append(tmpdat['FP3_GRF_Z'].iloc[-1])
        
                Subject.append(sub)
                Config.append(config)
                t0.append(startTime)
                batStartTime.append(math.floor(tmpdat['Sample #'][0]/200))
                batEndTime.append(math.ceil(tmpdat['Sample #'].iloc[-1]/200))
                
        except: 
                
                print(fName, i)
        
    outcomes = pd.DataFrame({'Subject':list(Subject), 'Config': list(Config), 't0':list(t0), 'batStartTime':list(batStartTime), 'batEndTime':list(batEndTime),
                             'kneeFlexFC':list(kneeFlexFC), 'kneeFlexBC':list(kneeFlexBC),
                         'kneeExtVelBC':list(kneeExtVelBC), 'pkKneeFlex':list(pkKneeFlex), 'kneeExtROM':list(kneeExtROM),
                         'pkKneeExtVel':list(pkKneeExtVel), 'pelVel': list(pelVel),
                         'pBF':list(pBF), 'pPF':list(pPF), 'brakeBC':list(brakeBC), 'brakeImp':list(brakeImp),
                         'pVGRF':list(pVGRF), 'vGRF_bc':list(vGRF_bc), 
                         'minFreeMoment':list(minFreeMoment),'maxFreeMoment':list(maxFreeMoment),
                         
                         'leadAnklePosWork':list(leadAnklePosWork),
                         'leadAnklePeakPosPower':list(leadAnklePeakPosPower),
                         'leadAnkleNegWork':list(leadAnkleNegWork),
                         'leadAnklePeakNegPower':list(leadAnklePeakNegPower),
                         
                         'leadKneePosWork':list(leadKneePosWork),
                         'leadKneePeakPosPower':list( leadKneePeakPosPower),
                         'leadKneeNegWork':list(leadKneeNegWork),
                         'leadKneePeakNegPower':list(leadKneePeakNegPower),
                         
                         'leadHipPosWork':list(leadHipPosWork),
                         'leadHipPeakPosPower':list(leadHipPeakPosPower),
                         'leadHipNegWork':list(leadHipNegWork),
                         'leadHipPeakNegPower':list( leadHipPeakNegPower),
                         
                         'rearAnklePosWork':list(rearAnklePosWork),
                         'rearAnklePeakPosPower':list(rearAnklePeakPosPower),
                         'rearAnkleNegWork':list(rearAnkleNegWork),
                         'rearAnklePeakNegPower':list(rearAnklePeakNegPower),
                         
                         'rearKneePosWork':list(rearKneePosWork),
                         'rearKneePeakPosPower':list(rearKneePeakPosPower),
                         'rearKneeNegWork':list(rearKneeNegWork),
                         'rearKneePeakNegPower':list(rearKneePeakNegPower),
                         
                         'rearHipPosWork':list(rearHipPosWork),
                         'rearHipPeakPosPower':list( rearHipPeakPosPower),
                         'rearHipNegWork':list( rearHipNegWork),
                         'rearHipPeakNegPower':list(rearHipPeakNegPower)
                         
                         })

    outfileName = fPath + 'CompiledResults2.csv'


    if os.path.exists(outfileName) == False:
        outcomes.to_csv(outfileName, mode='a', header=True, index = False)

    else:
        outcomes.to_csv(outfileName, mode='a', header=False, index = False)

