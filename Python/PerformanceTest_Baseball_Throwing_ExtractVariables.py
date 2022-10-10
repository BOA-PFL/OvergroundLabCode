
"""
Created on Fri Oct  7 12:04:23 2022

@author: Bethany.Kilpatrick with help from Milena Singletary
"""



""" 
This code is used to extract and compile Rapsodo variables from Throwing


"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os



# Read in files
# only read .asc files for this work
fPath = 'C:\\Users\\bethany.kilpatrick\\Boa Technology Inc\\PFL - General\\Testing Segments\\Baseball\Radar\\Throw\\'
fileExt = r".csv"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]




# Initialize Variables
StrikeZoneSide = []
StrikeZoneHt = []
Velocity = []
TotalSpin = []
TrueSpin = []
SpinEfficiency = []
SpinDirection = []
VB_Spin  = []
HB_Spin = []
HorizontalAng = []
ReleaseAng = []
ReleaseHt = []
ReleaseSide = []
GyroDegree = []

Subject = []
subName =[]
throwcount = []

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
        tmpConfig = fName.split(sep="_")[2]
        config= tmpConfig.split(".")[0]
        
        dat = pd.read_csv(fPath + "\\" + fName, sep =',', skiprows = 3, header = 0)
         
        dat.columns = ['No', 'Date', 'PitchID','PitchType','isStrike', 'StrikeZoneSide', 'StrikeZoneHt', 'Velocity', 'TotalSpin', 'TrueSpin','SpinEfficiency', 'SpinDirection', 'SpinConfidence',
                       'VB_Spin', 'HB_Spin','HorizontalAng', 'ReleaseAng', 'ReleaseHt', 'ReleaseSide', 'GyroDegree', 'UniqueID', 'DeviceSerialNumber'
                           
                            ]
        
        
        
        #Pulling metrics from the data set
        StrikeZoneSide.extend(np.array(dat.StrikeZoneSide))
                
        StrikeZoneHt.extend(np.array(dat.StrikeZoneHt))
            
        Velocity.extend(np.array(dat.Velocity)) 
        
        TotalSpin.extend(np.array(dat.TotalSpin))  
         
        TrueSpin.extend(np.array(dat.TrueSpin))
        
        SpinEfficiency.extend(np.array(dat.SpinEfficiency))
        
        SpinDirection.extend(np.array(dat.SpinDirection))     
        
        VB_Spin.extend(np.array(dat.VB_Spin))  
        
        HB_Spin.extend(np.array(dat.HB_Spin)) 
        
        HorizontalAng.extend(np.array(dat.HorizontalAng))
        
        ReleaseAng.extend(np.array(dat.ReleaseAng))
        
        ReleaseHt.extend(np.array(dat.ReleaseHt))
        
        ReleaseSide.extend(np.array(dat.ReleaseSide))
        
        GyroDegree.extend(np.array(dat.GyroDegree))
        
        
        throwcount = len(dat.StrikeZoneSide)
        
         #Apply subject name and config        
        for ii in range(throwcount): # Using the length of the spin variable, we can then apply names and figs to each array
            
             Subject.append(subName)
             Config.append( config )
                              
            
    except:
        print(fName) 
        
        
        

             
             
outcomes = pd.DataFrame({'Subject':list(Subject), 'Config': list(Config),  'StrikeZoneSide':list(StrikeZoneSide), 'StrikeZoneHt':list(StrikeZoneHt), 'Velocity':list(Velocity), 
                         'TotalSpin':list(TotalSpin), 'TrueSpin': list(TrueSpin), 'SpinEfficiency': list(SpinEfficiency),'SpinDirection': list(SpinDirection), 'VB_Spin': list(VB_Spin),
                         'HB_Spin':list(HB_Spin), 'HorizontalAng':list(HorizontalAng),'ReleaseAng': list(ReleaseAng), 'ReleaseHt': list(ReleaseHt), 'ReleaseSide':list(ReleaseSide),
                         'GyroDegree':list(GyroDegree)
                           })


outfileName = fPath + 'CompiledRadarThrowingData.csv'
outcomes.to_csv(outfileName, index = False)