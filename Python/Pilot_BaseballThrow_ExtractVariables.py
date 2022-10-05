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

fPath = 'C:/Users/Kate.Harrison/Boa Technology Inc/PFL Team - General/Testing Segments/Baseball/Mocap/Throw/'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]


for fName in entries:
    fName = entries[15]

    sub = fName.split(sep = '_')[0]
    hand = fName.split(sep = '_')[1]
    config = fName.split(sep = '_')[3].split(sep = ' ')[0]
    
    dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
    dat['PelvisRotationVel'] = np.gradient(dat.PelvisRotation, 0.005)

    ### Find start (back foot steps on to plate) and end (front foot lifts off of plate) of each throw
    # plt.figure()
    # plt.plot(dat.FP2_GRF_Z, label = 'Rear foot')
    # plt.plot(dat.FP4_GRF_Z, label = 'Front foot')
    # plt.legend()
    
    
    # sep = plt.ginput(n = -1, timeout=-1)
    # plt.close()
    # start = []

    kneeLift = []
    leadfootContact = []
    shoulderExtRot = []
    ballRelease = []
    followThru = []
    
    Subject = []
    Config = []
    minKneeFlex = []
    kneeFlexBR = []
    kneeExtROM = []
    kneeExtVelBR = []
    kneeExtVelMER = []
    pkKneeExtVel = []
    pelVel = []
    pBF = []
    brakeBR = []
    brakeImp = []
    pVGRF =[]
    vGRF_br = []
    vGRF_mer = []
    minFreeMoment = []
    maxFreeMoment = []

    # for i in range(len(sep)):
        
        
    #         #i = 0
    
    #         windowStart = round(sep[i][0])

    #         rearfootContact = []
    
    #         for j in range(len(dat.FP2_GRF_Z[windowStart:])):
        
    #             if dat.FP2_GRF_Z[windowStart+j]<40 and dat.FP2_GRF_Z[windowStart+j +1]>40:
    #                 rearfootContact.append(windowStart+j+1)
            
    #         start.append(rearfootContact[0])
            
    
    if hand == 'Right':
        plt.figure()
        plt.plot(dat.LeftKneeHeight)
        meanKneeHt = np.mean(dat.LeftKneeHeight)
        kneeThresh = meanKneeHt + .3  
        plt.axhline (meanKneeHt)
        plt.axhline(kneeThresh)
        kneeLift = find_peaks(dat.LeftKneeHeight, height = kneeThresh, distance = 1000)[0]
        plt.plot(kneeLift, dat.LeftKneeHeight[kneeLift], 'kx')
        
    else:
        plt.figure()
        plt.plot(dat.RightKneeHeight)
        meanKneeHt = np.mean(dat.RightKneeHeight)
        kneeThresh = meanKneeHt + .3  
        plt.axhline (meanKneeHt)
        plt.axhline(kneeThresh)
        kneeLift = find_peaks(dat.RightKneeHeight, height = kneeThresh, distance = 1000)[0]
        plt.plot(kneeLift, dat.RightKneeHeight[kneeLift], 'kx')
    
    for i in range(len(kneeLift)):
        
        
            #i = 0
        
            # Find point where lead knee is lifted up teh highest (peak knee flexion immediately following rearfoot plant)
            # if hand == 'Right':
            #     kneeLift.append( start[i] + np.argmax(dat.LeftKneeHeight[start[i]:start[i]+1000]))
            # else:
            #     kneeLift.append( start[i] + np.argmax(dat.RightKneeHeight[start[i]:start[i]+1000])  )

            #Find point where lead leg contacts the ground
        
            td = []
            for k in range(len(dat.FP4_GRF_Z[kneeLift[i]:kneeLift[i]+400])):
                    if dat.FP4_GRF_Z[kneeLift[i]+k] < 40 and dat.FP4_GRF_Z[kneeLift[i]+k+1] > 40:
                        td.append(kneeLift[i]+k)
            leadfootContact.append(td[0])
            #plt.plot(dat.RightShoulderRotation)
                
            #Find Maximum shoulder external rotation
            if hand == 'Right':
                shoulderExtRot.append(leadfootContact[i] + np.argmin(dat.RightShoulderRotation[leadfootContact[i]:leadfootContact[i]+100]))
            
            else: 
                shoulderExtRot.append(leadfootContact[i] + np.argmax(dat.LeftShoulderRotation[leadfootContact[i]:leadfootContact[i]+100]))
          
            # # Find ball release (1 frame ahead of where wrist passes elbow in anterior direction)
            if hand == 'Right':
                ballRelease.append(shoulderExtRot[i] + 1 + np.argmax(dat.RightWristElbowDiff_Z[shoulderExtRot[i]:shoulderExtRot[i] + 30]))
            
            else:
                ballRelease.append(shoulderExtRot[i] + 1 + np.argmax(dat.LeftWristElbowDiff_Z[shoulderExtRot[i]:shoulderExtRot[i] + 30]))
        
            # Find end of follow through
    
            # if hand == 'Right':
            #     followThru.append(ballRelease[i] + np.argmax(dat.RightWristElbowDiff_Y[start[i]+ballRelease[i]:start[i]+ballRelease[i]+30]))
            # else:
            #     followThru.append(ballRelease[i] + np.argmax(dat.LeftWristElbowDiff_Y[start[i]+ballRelease[i]:start[i]+ballRelease[i]+30]))
        
        
            # if followThru[i] > ballRelease[i]:
            #     tmpdat = dat[start[i]:start[i]+followThru[i]+1].reset_index(drop = True)
            # else:
            #     tmpdat = dat[start[i]:start[i]+ballRelease[i]+1].reset_index(drop = True)
                
            tmpdat = dat[kneeLift[i]:ballRelease[i]].reset_index(drop = True)
    
            brakingF = tmpdat.FP4_GRF_Y
            brakingF[brakingF>0] = 0
            pBF.append(np.min( tmpdat.FP4_GRF_Y))
            brakeBR.append(tmpdat['FP4_GRF_Y'].iloc[-1])
            brakeImp.append(np.sum(brakingF/1000))
            pVGRF.append(np.max(tmpdat.FP4_GRF_Z))
            vGRF_br.append(tmpdat['FP4_GRF_Z'].iloc[-1])
            #vGRF_mer.append(tmpdat.FP4_GRF_Z[shoulderExtRot[i]])
        
            
            if hand == 'Right':
                minKneeFlex.append(np.min(tmpdat.LKneeAngle_Sagittal[leadfootContact[i]-kneeLift[i]:]))
                kneeFlexBR.append( tmpdat['LKneeAngle_Sagittal'].iloc[-1])
                kneeExtROM.append( kneeFlexBR[i] - minKneeFlex[i])
                kneeExtVelBR.append(tmpdat['LKneeAngVel_Sagittal'].iloc[-1])
                pkKneeExtVel.append(np.max(tmpdat.LKneeAngVel_Sagittal))
                #kneeExtVelMER.append(tmpdat.LKneeAngVel_Sagittal[shoulderExtRot[i]])
                minFreeMoment.append(np.min(tmpdat.FreeMoment_FP4))
                maxFreeMoment.append(np.max(tmpdat.FreeMoment_FP4))
                pelVel.append(np.max(tmpdat.PelvisRotationVel))
        
            if hand == 'Left':
                minKneeFlex.append(np.min(tmpdat.RKneeAngle_Sagittal[leadfootContact[i]-kneeLift[i]:]))
                kneeFlexBR.append( tmpdat['RKneeAngle_Sagittal'].iloc[-1])
                kneeExtROM.append( kneeFlexBR[i] - minKneeFlex[i])
                kneeExtVelBR.append(tmpdat['RKneeAngVel_Sagittal'].iloc[-1])
                pkKneeExtVel.append(np.max(tmpdat.RKneeAngVel_Sagittal))
                #kneeExtVelMER.append(tmpdat.RKneeAngVel_Sagittal[shoulderExtRot[i]])
                minFreeMoment.append(np.max(tmpdat.FreeMoment_FP4))
                maxFreeMoment.append(np.min(tmpdat.FreeMoment_FP4))
                pelVel.append(np.min(tmpdat.PelvisRotationVel))
        
            Subject.append(sub)
            Config.append(config)
        
        
            plt.figure('Vertical GRF')
            plt.plot(tmpdat.FP2_GRF_Z, 'r')
            plt.plot(tmpdat.FP4_GRF_Z, 'b')
            
            plt.figure('AP GRF')
            plt.plot(tmpdat.FP2_GRF_Y, 'r')
            plt.plot(tmpdat.FP4_GRF_Y, 'b')
        
            plt.figure('Free Moment')
            plt.plot(tmpdat.FreeMoment_FP2, 'r')
            plt.plot(tmpdat.FreeMoment_FP4, 'b')
        
            plt.figure('Elbow vs. Wrist Vertical Position')
            if hand == 'Right': 
                plt.plot(tmpdat.RightWristElbowDiff_Z, 'r')
             
            else:
                plt.plot(tmpdat.LeftWristElbowDiff_Z, 'r')
            
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


outcomes = pd.DataFrame({'Subject':list(Subject), 'Config': list(Config), 'kneeFlexBR':list(kneeFlexBR), 
                         'kneeExtVelBR':list(kneeExtVelBR), 'pkKneeExtVel':list(pkKneeExtVel), 'pelVel': list(pelVel), 
                         'pkKneeFlex':list(minKneeFlex), 'kneeExtROM': list(kneeExtROM),
                         'pBF':list(pBF), 'brakeBR':list(brakeBR), 'brakeImp':list(brakeImp),
                         'pVGRF':list(pVGRF), 'vGRF_br':list(vGRF_br),
                         'minFreeMoment':list(minFreeMoment),'maxFreeMoment':list(maxFreeMoment)
                         
                         })

outfileName = fPath + 'CompiledResults.csv'

if os.path.exists(outfileName) == False:
    
    outcomes.to_csv(outfileName, mode='a', header=True, index = False)

else:
    outcomes.to_csv(outfileName, mode='a', header=False, index = False)
