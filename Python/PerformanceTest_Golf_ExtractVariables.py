# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 15:53:52 2021

@author: Eric Honert
"""
  

""" 
This script identifies the trial order of the golf swing as well as computes and plots
 the club head speed and max GRF.

"""
###### Force Analysis

# packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Obtain file with condition ordering
ConOrd = pd.read_excel('Z:\\Testing Segments\\PowerPerformance\\AsicsJapan_Golf_March2022\\AsicsConditionOrder.xlsx')

fPath = 'Z:\\Testing Segments\\PowerPerformance\\AsicsJapan_Golf_March2022\\Overground\\'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]

# Pre-allocate arrays
Subject = []
Config = []
Sesh = []
Order = []
MaxForce = []
tc_front_force = np.array([])

# Initiate figure for the first subject
plt.figure(1)
cc = 1 # Initiate subject counter

for ii,fName in enumerate(entries):

    try:
        
        subName = fName.split(sep = "_")[0]
        ConfigTmp = fName.split(sep="_")[1]
        SeshTmp = fName.split(sep="_")[2]
        
        # Get Session Order
        idx = (ConOrd.Subject == subName)*(ConOrd.Config == ConfigTmp)
        # Make sure that the labels in the excel file are correct
        if sum(idx)!=1:
            print(subName)
        
        tmp = np.array(ConOrd.Order[idx])
        
        if int(SeshTmp) == 1:
            OrdTmp = tmp[0]
        else:
            if tmp == 1:
                OrdTmp = 4
            elif tmp == 2:
                OrdTmp = 3
        
        
        

        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        dat = dat.fillna(0)
        
        # Compute the golf head speed
        GHS = np.gradient(np.sqrt(dat.GolfHead_POS_X**2+dat.GolfHead_POS_Y**2+dat.GolfHead_POS_Z**2),1/200)
        
        # Find contact-ish with finding the maximum force on the front foot
        around_contact = np.argmax(dat.FP3_GRF_Z)
        
        # Want to obtain the maximum force around the fastest club head speed
        maxZ_front = np.max(dat.FP3_GRF_Z[around_contact-100:around_contact+100])
               
        MaxForce.append(maxZ_front)
        Subject.append(subName)
        Config.append(ConfigTmp)
        Sesh.append(SeshTmp)
        Order.append(OrdTmp)
        
        # Create a time-continuous vector for forces to check the reliability
        # of the defined contact
        if ii > 0 and Subject[ii] != Subject[ii-1]:
            cc = cc+1
            plt.figure(cc)
        
        plt.subplot(211)    
        plt.plot(range(len(dat.FP3_GRF_Z[around_contact-100:around_contact+100])),dat.FP2_GRF_Z[around_contact-100:around_contact+100])
        
        plt.subplot(212)
        plt.plot(range(len(dat.FP3_GRF_Z[around_contact-100:around_contact+100])),dat.FP3_GRF_Z[around_contact-100:around_contact+100])
        
    except:
        print(fName)

    
    
outcomes = pd.DataFrame({'Subject':list(Subject),'Config':list(Config),'Sesh':list(Sesh),'Order':list(Order), 'MaxForce':list(MaxForce)
                                          })

outcomes.to_csv('Z:\\Testing Segments\\PowerPerformance\\AsicsJapan_Golf_March2022\\CompiledForce.csv', index = False)
