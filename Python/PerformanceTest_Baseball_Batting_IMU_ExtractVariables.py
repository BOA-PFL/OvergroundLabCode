'''

Created on Fri Oct  7 12:04:23 2022

@author: Bethany.Kilpatrick with help from Milena Singletary
"""



""" 
This code is used to extract and compile Blast IMU variables from batting


"""
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os



# Read in files
# only read .asc files for this work
fPath = 'C:\\Users\\bethany.kilpatrick\\Boa Technology Inc\\PFL - General\\Testing Segments\\Baseball\BatIMU\\'
fileExt = r".csv"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]




# Initialize Variables
PlaneScore = []
ConnectionScore = []
RotationScore = []
BatSpeed = []
RotAcceleration = []
PlaneEfficiency = []
AttackAng = []
EarlyConnection  = []
ConnectionatImpact = []
VertBatAngle = []
Power = []
TimetoContact = []
PeakHandSpeed = []
ExitVelocity = [] 
LaunchAng = []
EstimatedDist = []


Subject = []
subName =[]
batcount = []

Config = []




for fName in entries:
    try:
        """
        loop through the selected files and obtain values for batting radar metrics
        Start by looping through files and getting meta data 
        Output metrics
        
       
       """

        # fName = entries[1]



        subName = fName.split(sep="_")[0]
        tmpConfig = fName.split(sep="_")[1]
        config= tmpConfig.split(".")[0]
        
        dat = pd.read_csv(fPath + "\\" + fName, sep =',', skiprows = 7, header = 'infer')
         
        
        #Defining new variable names bc the CSV has spaces
        dat.columns = ['Date', 'Equipment','Handedness','SwingDetails', 'PlaneScore', 'ConnectionScore', 'RotationScore', 'BatSpeed', 'RotAcceleration','PlaneEfficiency', 
                        'AttackAng', 'EarlyConnection',
                        'ConnectionatImpact', 'VertBatAngle','Power', 'TimetoContact', 'PeakHandSpeed', 'ExitVelocity', 'LaunchAng', 'EstimatedDist'
                           
                            ]
        
        
        
        #Pulling metrics from the data set
        PlaneScore.extend(np.array(dat.PlaneScore))
                
        ConnectionScore.extend(np.array(dat.ConnectionScore))
            
        RotationScore.extend(np.array(dat.RotationScore)) 
        
        BatSpeed.extend(np.array(dat.BatSpeed))  
         
        RotAcceleration.extend(np.array(dat.RotAcceleration))
        
        PlaneEfficiency.extend(np.array(dat.PlaneEfficiency))
        
        AttackAng.extend(np.array(dat.AttackAng))     
        
        EarlyConnection.extend(np.array(dat.EarlyConnection))  
        
        ConnectionatImpact.extend(np.array(dat.ConnectionatImpact)) 
        
        VertBatAngle.extend(np.array(dat.VertBatAngle))
        
        Power.extend(np.array(dat.Power))
        
        TimetoContact.extend(np.array(dat.TimetoContact))
        
        PeakHandSpeed.extend(np.array(dat.PeakHandSpeed))
        
        ExitVelocity.extend(np.array(dat.ExitVelocity)) 
        
        LaunchAng.extend(np.array(dat.LaunchAng)) 
        
        EstimatedDist.extend(np.array(dat.EstimatedDist))
        
        
        batcount = len(dat.PlaneScore)
        
         #Apply subject name and config        
        for ii in range(batcount): # Using the length of the spin variable, we can then apply names and figs to each array
            
             Subject.append(subName)
             Config.append( config )
                              
            
    except:
        print(fName) 
        
        
        

             
             
outcomes = pd.DataFrame({'Subject':list(Subject), 'Config': list(Config),  'PlaneScore':list(PlaneScore), 'ConnectionScore':list(ConnectionScore), 'RotationScore':list(RotationScore), 
                         'BatSpeed':list(BatSpeed), 'RotAcceleration': list(RotAcceleration),'PlaneEfficiency': list(PlaneEfficiency), 'AttackAng': list(AttackAng),
                         'EarlyConnection':list(EarlyConnection), 'ConnectionatImpact':list(ConnectionatImpact),'VertBatAngle': list(VertBatAngle), 'Power': list(Power), 'TimetoContact':list(TimetoContact),
                         'PeakHandSpeed':list(PeakHandSpeed), 'ExitVelocity':list(ExitVelocity), 'LaunchAng':list(LaunchAng), 'EstimatedDist':list(EstimatedDist),
                           })


outfileName = fPath + 'CompiledRadarBattingIMUData.csv'
outcomes.to_csv(outfileName, index = False)