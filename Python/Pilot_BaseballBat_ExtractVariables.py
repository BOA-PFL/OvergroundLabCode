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
fPath = 'C:/Users/Kate.Harrison/Boa Technology Inc/PFL Team - General/Testing Segments/Baseball/Mocap/Bat/'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]


for fName in entries:
    #fName = entries[0]

    sub = fName.split(sep = '_')[0]
    hand = fName.split(sep = '_')[1]
    config = fName.split(sep = '_')[3].split(sep = ' ')[0]
    
    dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
    
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
    kneeFlexFC = []
    pkKneeFlex = []
    kneeExtROM = []
    kneeFlexBC = []
    kneeExtVelBC = []
    pkKneeExtVel = []
    pBF = []
    brakeBC = []
    brakeImp = []
    pVGRF =[]
    vGRF_bc = []
    minFreeMoment = []
    maxFreeMoment = []
    
    for i in range(len(ballContact)):
        
        try: 
            #i = 12
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
            
                pBF.append(np.min(tmpdat.FP3_GRF_Y))
                brakeBC.append(tmpdat['FP3_GRF_Y'].iloc[-1])
                tmpdat.FP3_GRF_Y[tmpdat.FP3_GRF_Y>0] = 0
                brakeImp.append(np.sum(tmpdat.FP3_GRF_Y)/200)
                pVGRF.append(np.max(tmpdat.FP3_GRF_Z))
                vGRF_bc.append(tmpdat['FP3_GRF_Z'].iloc[-1])
        
                Subject.append(sub)
                Config.append(config)
                
        except: 
                
                print(fName, i)
        
    outcomes = pd.DataFrame({'Subject':list(Subject), 'Config': list(Config), 'kneeFlexFC':list(kneeFlexFC), 'kneeFlexBC':list(kneeFlexBC),
                         'kneeExtVelBC':list(kneeExtVelBC), 'pkKneeFlex':list(pkKneeFlex), 'kneeExtROM':list(kneeExtROM),
                         'pkKneeExtVel':list(pkKneeExtVel),
                         'pBF':list(pBF), 'brakeBC':list(brakeBC), 'brakeImp':list(brakeImp),
                         'pVGRF':list(pVGRF), 'vGRF_bc':list(vGRF_bc), 
                         'minFreeMoment':list(minFreeMoment),'maxFreeMoment':list(maxFreeMoment)
                         
                         })

    outfileName = fPath + 'CompiledResults2.csv'


    if os.path.exists(outfileName) == False:
        outcomes.to_csv(outfileName, mode='a', header=True, index = False)

    else:
        outcomes.to_csv(outfileName, mode='a', header=False, index = False)

