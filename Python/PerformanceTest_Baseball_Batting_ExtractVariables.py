# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 12:04:23 2022

@author: Bethany.Kilpatrick with help from Milena Singletary
"""



""" 
This code is used to extract and compile Rapsodo variables from Batting


"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os



# Read in files
# only read .asc files for this work
fPath = 'C:\\Users\\bethany.kilpatrick\\Boa Technology Inc\\PFL - General\\Testing Segments\\Baseball\Radar\\Bat\\'
fileExt = r".csv"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]




# Initialize Variables
exitSpeed =[]
LaunchAng =[]
spin = []
distance = []
launchDirection = []
strikeZoneX = [] 
strikeZoneY = []
spinAxisX =[]


Subject = []
subName =[]
swingcount = []

Config = []




for fName in entries:
    try:
        """
        loop through the selected files and obtain values for batting radar metrics
        Start by looping through files and getting meta data 
        Output metrics
        
       
       """





        subName = fName.split(sep="_")[0]
        tmpConfig = fName.split(sep="_")[2]
        config= tmpConfig.split(".")[0]
        
        dat = pd.read_csv(fPath + "\\" + fName, sep =',', skiprows = 3, header = 0)
        
        #Pulling metrics from the data set
        spin.extend(np.array(dat.spin))
                
        exitSpeed.extend(np.array(dat.exitSpeed))
            
        spinAxisX.extend(np.array(dat.launchAngle)) 
        
        launchDirection.extend(np.array(dat.launchDirection))  
         
        strikeZoneX.extend(np.array(dat.strikeZoneX))
        
        strikeZoneY.extend(np.array(dat.strikeZoneY))
        
            
        distance.extend(np.array(dat.distance))     
        
        spinAxisX.extend(np.array(dat.spinAxisX))
        
        swingcnt = len(dat.spin)
        
         #Apply subject name and config        
        for ii in range(swingcnt): # Using the length of the spin variable, we can then apply names and figs to each array
            
             Subject.append(subName)
             Config.append( config )
                              
            
    except:
        print(fName) 
        
        
        

             
             
outcomes = pd.DataFrame({'Subject':list(Subject), 'Config': list(Config),  'spin':list(spin), 'exitSpeed':list(exitSpeed), 'distance':list(distance), 'LaunchAng':list(LaunchAng), 'launchDirection': list(launchDirection), 'spinAxisX': list(spinAxisX), 
                         'strikeZoneX': list(strikeZoneX), 'strikeZoneY': list(strikeZoneY)
                           })


outfileName = fPath + 'CompiledRadarBattingData.csv'
outcomes.to_csv(outfileName, index = False)