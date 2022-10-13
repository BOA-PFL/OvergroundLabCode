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


fPath = 'C:/Users/Kate.Harrison/Boa Technology Inc/PFL Team - General/Testing Segments/Baseball/Mocap/Throw/'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]


for fName in entries:
    
    
    #fName = entries[0]
    
    plt.close('all')

    sub = fName.split(sep = '_')[0]
    hand = fName.split(sep = '_')[1]
    config = fName.split(sep = '_')[3].split(sep = ' ')[0]
    
    dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
    
    #dat2 = pd.read_csv(fPath+fName,sep='\t', skiprows = 1, header = 0, names = ['x1', 'x2', 'time', 'x4'], usecols= ['time'], nrows = 1)
    
    dat2 = pd.read_csv(fPath+fName,sep='\t', skiprows = 2, header = None, usecols= [2], nrows = 1)
    startTime = str(dat2[2].iloc[0][0:8])

    dat['PelvisRotationVel'] = np.gradient(dat.PelvisRotation, 0.005)
    dat.LeftFootPosition[dat.LeftFootPosition >6] = 'Nan'
    dat.RightFootPosition[dat.RightFootPosition >6] = 'Nan'
    ### Find start (back foot steps on to plate) and end (front foot lifts off of plate) of each throw
    # plt.figure()
    # plt.plot(dat.FP2_GRF_Z, label = 'Rear foot')
    # plt.plot(dat.FP4_GRF_Z, label = 'Front foot')
    # plt.legend()
    plt.figure()
    
    if hand == 'Right':
        plt.plot(dat.LeftFootPosition)
        footFwd= find_peaks(dat.LeftFootPosition, height = 1)
        pkVels = dat.LeftFootPosition[footFwd[0]]
        z = (pkVels - np.mean(pkVels))/np.std(pkVels)
        pkVels = pkVels*(z<2)
        pkVels = pkVels[pkVels != 0]
        pkVels = pkVels.sort_values(ascending = False).head(12)
        footVelThresh = np.mean(pkVels)*0.8
        throwStart = find_peaks(dat.LeftFootPosition, height = footVelThresh, distance = 1000)[0]
        plt.plot(throwStart, dat.LeftFootPosition[throwStart], 'kx')
        plt.axhline(footVelThresh)
        
    if hand == 'Left':
        plt.plot(dat.RightFootPosition)
        footFwd= find_peaks(dat.RightFootPosition, height = 1)
        pkVels = dat.RightFootPosition[footFwd[0]]
        z = (pkVels - np.mean(pkVels))/np.std(pkVels)
        pkVels = pkVels*(z<2)
        pkVels = pkVels[pkVels != 0]
        pkVels = pkVels.sort_values(ascending = False).head(12)
        footVelThresh = np.mean(pkVels)*0.8
        throwStart = find_peaks(dat.RightFootPosition, height = footVelThresh, distance = 1000)[0]
        plt.plot(throwStart, dat.RightFootPosition[throwStart], 'kx')
        plt.axhline(footVelThresh)
        
    # sep = plt.ginput(n = -1, timeout=-1)
    # plt.close()
    # start = []

    #kneeLift = []
    leadfootContact = []
    shoulderExtRot = []
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
    kneeExtVelBR = []
    kneeExtVelMER = []
    pkKneeExtVel = []
    pelVel = []
    pBF = []
    pPF= []
    brakeBR = []
    brakeImp = []
    pVGRF =[]
    vGRF_br = []
    vGRF_mer = []
    minFreeMoment = []
    maxFreeMoment = []
    
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
    
    shoulderER = []
    elbowValgus = []

    # for i in range(len(sep)):
        
        
    #         #i = 0
    
    #         windowStart = round(sep[i][0])

    #         rearfootContact = []
    
    #         for j in range(len(dat.FP2_GRF_Z[windowStart:])):
        
    #             if dat.FP2_GRF_Z[windowStart+j]<40 and dat.FP2_GRF_Z[windowStart+j +1]>40:
    #                 rearfootContact.append(windowStart+j+1)
            
    #         start.append(rearfootContact[0])
            
    
    # if hand == 'Right':
    #     plt.figure()
    #     plt.plot(dat.LeftKneeHeight)
    #     meanKneeHt = np.mean(dat.LeftKneeHeight)
    #     kneeThresh = meanKneeHt + .3  
    #     plt.axhline (meanKneeHt)
    #     plt.axhline(kneeThresh)
    #     kneeLift = find_peaks(dat.LeftKneeHeight, height = kneeThresh, distance = 1000)[0]
    #     plt.plot(kneeLift, dat.LeftKneeHeight[kneeLift], 'kx')
        
    # else:
    #     plt.figure()
    #     plt.plot(dat.RightKneeHeight)
    #     meanKneeHt = np.mean(dat.RightKneeHeight)
    #     kneeThresh = meanKneeHt + .3  
    #     plt.axhline (meanKneeHt)
    #     plt.axhline(kneeThresh)
    #     kneeLift = find_peaks(dat.RightKneeHeight, height = kneeThresh, distance = 1000)[0]
    #     plt.plot(kneeLift, dat.RightKneeHeight[kneeLift], 'kx')
    
    i = 0
    
    for j in range(len(throwStart)):
        
        try:
            #i = 0
        
            # Find point where lead knee is lifted up teh highest (peak knee flexion immediately following rearfoot plant)
            # if hand == 'Right':
            #     kneeLift.append( start[i] + np.argmax(dat.LeftKneeHeight[start[i]:start[i]+1000]))
            # else:
            #     kneeLift.append( start[i] + np.argmax(dat.RightKneeHeight[start[i]:start[i]+1000])  )

            #Find point where lead leg contacts the ground
        
            td = []
            for k in range(len(dat.FP4_GRF_Z[throwStart[i]:throwStart[i]+400])):
                    if dat.FP4_GRF_Z[throwStart[i]+k] < 40 and dat.FP4_GRF_Z[throwStart[i]+k+1] > 40:
                        td.append(throwStart[i]+k)
            leadfootContact = (td[0])
            #plt.plot(dat.RightShoulderRotation)
                
            #Find Maximum shoulder external rotation
            if hand == 'Right':
                shoulderExtRot = leadfootContact + np.argmin(dat.RightShoulderRotation[leadfootContact:leadfootContact+100])
            
            else: 
                shoulderExtRot = leadfootContact + np.argmin(dat.LeftShoulderRotation[leadfootContact:leadfootContact+100])
          
            # # Find ball release (1 frame ahead of where wrist passes elbow in anterior direction)
            if hand == 'Right':
                br = []
                for f in range(len(dat.RightWristElbowDiff_Y[shoulderExtRot:shoulderExtRot+50])):
                    if dat.RightWristElbowDiff_Y[shoulderExtRot + f] <=0 and dat.RightWristElbowDiff_Y[shoulderExtRot + f + 1] > 0:
                        br.append(shoulderExtRot + f + 1)
                ballRelease = br[0]
                
            
            else:
                br = []
                for f in range(len(dat.LeftWristElbowDiff_Y[shoulderExtRot:shoulderExtRot+50])):
                    if dat.LeftWristElbowDiff_Y[shoulderExtRot + f] <=0 and dat.LeftWristElbowDiff_Y[shoulderExtRot + f + 1] > 0:
                        br.append(shoulderExtRot + f + 1)
                ballRelease = br[0]
                
            # Find end of follow through
    
            # if hand == 'Right':
            #     followThru.append(ballRelease[i] + np.argmax(dat.RightWristElbowDiff_Y[start[i]+ballRelease[i]:start[i]+ballRelease[i]+30]))
            # else:
            #     followThru.append(ballRelease[i] + np.argmax(dat.LeftWristElbowDiff_Y[start[i]+ballRelease[i]:start[i]+ballRelease[i]+30]))
        
        
            # if followThru[i] > ballRelease[i]:
            #     tmpdat = dat[start[i]:start[i]+followThru[i]+1].reset_index(drop = True)
            # else:
            #     tmpdat = dat[start[i]:start[i]+ballRelease[i]+1].reset_index(drop = True)
                
            tmpdat = dat[throwStart[i]:ballRelease].reset_index(drop = True)
    
            brakingF = copy.deepcopy(tmpdat.FP4_GRF_Y)
            brakingF[brakingF>0] = 0
            pBF.append(np.min( tmpdat.FP4_GRF_Y))
            pPF.append(np.max(tmpdat.FP2_GRF_Y))
            brakeBR.append(tmpdat['FP4_GRF_Y'].iloc[-1])
            brakeImp.append(np.sum(brakingF/1000))
            pVGRF.append(np.max(tmpdat.FP4_GRF_Z))
            vGRF_br.append(tmpdat['FP4_GRF_Z'].iloc[-1])
            #vGRF_mer.append(tmpdat.FP4_GRF_Z[shoulderExtRot[i]])
        
            
            if hand == 'Right':
                minKneeFlex.append(np.min(tmpdat.LKneeAngle_Sagittal[leadfootContact-throwStart[i]:]))
                kneeFlexBR.append( tmpdat['LKneeAngle_Sagittal'].iloc[-1])
                kneeExtROM.append( kneeFlexBR[i] - minKneeFlex[i])
                kneeExtVelBR.append(tmpdat['LKneeAngVel_Sagittal'].iloc[-1])
                pkKneeExtVel.append(np.max(tmpdat.LKneeAngVel_Sagittal))
                #kneeExtVelMER.append(tmpdat.LKneeAngVel_Sagittal[shoulderExtRot[i]])
                minFreeMoment.append(np.min(tmpdat.FreeMoment_FP4))
                maxFreeMoment.append(np.max(tmpdat.FreeMoment_FP2))
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
                
                shoulderER.append(np.min(tmpdat.RightShoulderRotation))
                elbowValgus.append(np.min(tmpdat.RightElbowVarus))
        
            if hand == 'Left':
                minKneeFlex.append(np.min(tmpdat.RKneeAngle_Sagittal[leadfootContact-throwStart[i]:]))
                kneeFlexBR.append( tmpdat['RKneeAngle_Sagittal'].iloc[-1])
                kneeExtROM.append( kneeFlexBR[i] - minKneeFlex[i])
                kneeExtVelBR.append(tmpdat['RKneeAngVel_Sagittal'].iloc[-1])
                pkKneeExtVel.append(np.max(tmpdat.RKneeAngVel_Sagittal))
                #kneeExtVelMER.append(tmpdat.RKneeAngVel_Sagittal[shoulderExtRot[i]])
                minFreeMoment.append(np.max(tmpdat.FreeMoment_FP4)*-1)
                maxFreeMoment.append(np.min(tmpdat.FreeMoment_FP2)*-1)
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
                
                shoulderER.append(np.min(tmpdat.LeftShoulderRotation))
                elbowValgus.append(np.min(tmpdat.LeftElbowVarus))
        
        
            Subject.append(sub)
            Config.append(config)
            t0.append(startTime)
            throwStartTime.append(math.floor(tmpdat['Sample #'][0]/200))
            throwEndTime.append(math.ceil(tmpdat['Sample #'].iloc[-1]/200))
        
        
            plt.figure('Vertical GRF')
            plt.plot(tmpdat.FP2_GRF_Z, 'r')
            plt.plot(tmpdat.FP4_GRF_Z, 'b')
            
            plt.figure('AP GRF')
            plt.plot(tmpdat.FP2_GRF_Y, 'r')
            plt.plot(tmpdat.FP4_GRF_Y, 'b')
        
            plt.figure('Free Moment')
            plt.plot(tmpdat.FreeMoment_FP2, 'r')
            plt.plot(tmpdat.FreeMoment_FP4, 'b')
            
            plt.figure('Elbow vs. Wrist AP Position')
            if hand == 'Right': 
                plt.plot(tmpdat.RightWristElbowDiff_Y, 'r')
            
            else:
                plt.plot(tmpdat.LeftWristElbowDiff_Y, 'r')
            
        
            plt.figure('Knee Flexion Angle')
            if hand == 'Right': 
            
                plt.plot(tmpdat.RKneeAngle_Sagittal, 'r')
                plt.plot(tmpdat.LKneeAngle_Sagittal, 'b')
            
            else:
                plt.plot(tmpdat.LKneeAngle_Sagittal, 'r')
                plt.plot(tmpdat.RKneeAngle_Sagittal, 'b')
                
            plt.figure('Pelvis Rotation Velocity')
            if hand == 'Right':
                plt.plot(tmpdat.PelvisRotationVel)
                
            else:
                plt.plot((tmpdat.PelvisRotationVel)*-1)
                
            plt.figure('Ankle Power')
            if hand == 'Right':
                plt.plot(tmpdat.RightAnklePower, 'r')
                plt.plot(tmpdat.LeftAnklePower, 'b')
                
            else:
                plt.plot(tmpdat.LeftAnklePower, 'r')
                plt.plot(tmpdat.RightAnklePower, 'b')
                
            plt.figure('Knee Power')
            if hand == 'Right':
                plt.plot(tmpdat.RightKneePower, 'r')
                plt.plot(tmpdat.LeftKneePower, 'b')
                
            else:
                plt.plot(tmpdat.LeftKneePower, 'r')
                plt.plot(tmpdat.RightKneePower, 'b')
                
            plt.figure('Hip Power')
            if hand == 'Right':
                plt.plot(tmpdat.RHipPower, 'r')
                plt.plot(tmpdat.LHipPower, 'b')
                
            else:
                plt.plot(tmpdat.LHipPower, 'r')
                plt.plot(tmpdat.RHipPower, 'b')
                
            plt.figure('Shoulder External Rotation')
            if hand == 'Right':
                plt.plot(tmpdat.RightShoulderRotation)
            if hand == 'Left':
                plt.plot(tmpdat.LeftShoulderRotation)
                
            plt.figure('Elbow Valgus')
            if hand == 'Right':
                plt.plot(tmpdat.RightElbowVarus)
            if hand == 'Left':
                plt.plot(tmpdat.LeftElbowVarus)
            i = i+1
    
        except:
          throwStart = np.delete(throwStart, i, axis = 0)
            # img_start = 
            # img_kneeLift = 
            # img_lead foot plant = 
            # img_shoulder rotation = 
            # img_ball release = 
            # img_followThru = 
    
            # plt.figure('Vertical GRF')
            # y = round(plt.gca().get_ylim()[1]) + 10
            # plt.axvline(np.mean(kneeLift), color ='k')
            # plt.axvline(np.mean(leadfootContact), color = 'k')
            # ##plt.axvline(np.mean(shoulderExtRot), color = 'k')
            # plt.axvline(np.mean(ballRelease), color = 'k')
            # plt.axvline(np.mean(followThru), color = 'k')
    
            # plt.figure('AP GRF')
            # plt.axvline(np.mean(kneeLift), color ='k')
            # plt.axvline(np.mean(leadfootContact), color = 'k')
            # #plt.axvline(np.mean(shoulderExtRot), color = 'k')
            # plt.axvline(np.mean(ballRelease), color = 'k')
            # plt.axvline(np.mean(followThru), color = 'k')

            # plt.figure('Free Moment')
            # plt.axvline(np.mean(kneeLift), color ='k')
            # plt.axvline(np.mean(leadfootContact), color = 'k')
            # #plt.axvline(np.mean(shoulderExtRot), color = 'k')
            # plt.axvline(np.mean(ballRelease), color = 'k')
            # plt.axvline(np.mean(followThru), color = 'k')
    
            # plt.figure('Knee Flexion Angle')
            # plt.axvline(np.mean(kneeLift), color ='k')
            # plt.axvline(np.mean(leadfootContact), color = 'k')
            # #plt.axvline(np.mean(shoulderExtRot), color = 'k')
            # plt.axvline(np.mean(ballRelease), color = 'k')
            # plt.axvline(np.mean(followThru), color = 'k')
            
        
###################################################################################################################### 
############ Check plots. If all looks good, export point estimates to outcomes sheet.


    outcomes = pd.DataFrame({'Subject':list(Subject), 'Config': list(Config), 't0':list(t0), 'throwStart':list(throwStartTime), 'throwEnd':list(throwEndTime),                            
                             'kneeFlexBR':list(kneeFlexBR), 
                         'kneeExtVelBR':list(kneeExtVelBR), 'pkKneeExtVel':list(pkKneeExtVel), 'pelVel': list(pelVel), 
                         'pkKneeFlex':list(minKneeFlex), 'kneeExtROM': list(kneeExtROM),
                         'pBF':list(pBF), 'pPF':list(pPF), 'brakeBR':list(brakeBR), 'brakeImp':list(brakeImp),
                         'pVGRF':list(pVGRF), 'vGRF_br':list(vGRF_br),
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
                         'rearHipPeakNegPower':list(rearHipPeakNegPower),
                         
                         'shoulderER':list(shoulderER),
                         'elbowValugs':list(elbowValgus)
                         
                         
                         })

    outfileName = fPath + 'CompiledResults.csv'

    if os.path.exists(outfileName) == False:
        outcomes.to_csv(outfileName, mode='a', header=True, index = False)

    else:
        outcomes.to_csv(outfileName, mode='a', header=False, index = False)
