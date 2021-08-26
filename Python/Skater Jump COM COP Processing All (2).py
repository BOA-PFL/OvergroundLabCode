# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 10:01:51 2021

@author: Adam.Luftglass
"""

# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Define constants and options
fThresh = 80 #below this value will be set to 0.
stepLen = 50

# Read in balance file
fPath = 'C:/Users/Adam.Luftglass/OneDrive - Boa Technology Inc/Documents/AdamLookingAtCOMDataTennis/New All Performance/'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]

## need to be modified for each test!

# list of functions 
# finding landings on the force plate once the filtered force exceeds the force threshold
def findLandings(force):
    lic = []
    for step in range(len(force)-1):
        if force[step] == 0 and force[step + 1] >= fThresh:
            lic.append(step)
    return lic

#Find takeoff from FP when force goes from above thresh to 0
def findTakeoffs(force):
    lto = []
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0:
            lto.append(step + 1)
    return lto

# preallocate matrix for force and fill in with force data
def forceMatrix(inputForce, landings, noSteps, stepLength):
    #input a force signal, return matrix with n rows (for each landing) by m col
    #for each point in stepLen
    preForce = np.zeros((noSteps,stepLength))
    
    for iterVar, landing in enumerate(landings):
        try:
            preForce[iterVar,] = inputForce[landing:landing+stepLength]
        except:
            print(landing)
            
    return preForce

def delimitTrialSkate(inputDF):
    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    ax.plot(inputDF.FP4_Z, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)

def delimitTrialCMJ(inputDF):
    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    ax.plot(inputDF.FP2_Z, label = 'Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0,0])) : int(np.floor(pts[1,0])),:]
    outputDat = outputDat.reset_index()
    return(outputDat)

CT = []
impulse = []
RFDcon = []
COPexcursion = []
COPtraj = []
timingDiff = []
subName = []
config = []
movements = []
COMY = []
diffCOMCOP = []
avgdiffCOMCOP = []
sumdiffCOMCOP = []
maxdiffCOMCOP = []
mindiffCOMCOP = []
impulseCT = []
CTimpulse = []
MaxVertPropulsion = []
MaxHorizPropulsion = []
CTMaxVertProp = []
CTMaxHorizProp = []
ankleWork = []
kneeWork = []
hipWork = []
ankleSagMom = []
ankleFrontMom = []
kneeSagMom = []
kneeFrontMom = []
ankleXAng = []
ankleYAng = []
kneeYAng = []
kneeZAng = []
kneeXAng = []
## save configuration names from files
for file in entries:
    try:
        fName = file #Load one file at a time
       
        config1 = fName.split('_')[2].split(' - ')[0]
        tmpMove = fName.split('_')[3].split(' - ')[0]
        
        dat = pd.read_csv(fPath+fName,sep='\t', skiprows = 8, header = 0)
        #dat = dat.fillna(0)
        
        if (tmpMove == 'Skater') or (tmpMove == 'skater'):
            dat = delimitTrialSkate(dat)
            # create vector of force from vertical signal from each file and make low values 0
            if np.max(dat.FP4_Z) > 100:
                totalForce = dat.FP4_Z
            else:
                totalForce = dat.FP4_Z * -1
            
            totalForce[totalForce<fThresh] = 0
            XtotalForce = dat.FP4_Y
            YtotalForce = dat.FP4_Z
            COPy = dat.FP4_COP_Y
            COMY = dat.LeftFootCOMY
            diffCOMCOP = COPy-COMY
            #find the landings from function above
            landings = findLandings(totalForce)
            landings= [x + 1 for x in landings] #add 1 and subtract 1 to trim takeoffs and landings so they do not encounter NaN
            takeoffs = findTakeoffs(totalForce)
            takeoffs = [x - 1 for x in takeoffs] 

        elif (tmpMove == 'CMJ') or (tmpMove == 'cmj'):
            
            dat = delimitTrialCMJ(dat)
            
            if np.max(dat.FP2_Z) > 100:
                totalForce = dat.FP2_Z
            else:
                totalForce = dat.FP2_Z * -1
         
            totalForce[totalForce<fThresh] = 0
            COPy = dat.FP2_COP_Y
            YtotalForce = totalForce #This is out of convenience to calculate impulse below even though this is not the Y force
            
            landings = findLandings(totalForce)
            landings= [x + 1 for x in landings] #add 1 and subtract 1 to trim takeoffs and landings so they do not encounter NaN
            
            takeoffs = findTakeoffs(totalForce)
            takeoffs = [x - 1 for x in takeoffs]  
            COMY = dat.LeftFootCOMY
            diffCOMCOP = COPy-COMY
        
            
        else:
            
            print('movement is not identified in file name correctly')
        
        
        for countVar, landing in enumerate(landings):
            try:
                ankleWork.append(sum(abs(dat.LeftAnklePower[landing : takeoffs[countVar]])))
                kneeWork.append(sum(abs(dat.LeftKneePower[landing : takeoffs[countVar]])))
                RFDcon.append( np.min(np.diff(YtotalForce[landing:takeoffs[countVar]])) )
                COPexcursion.append( np.max(COPy[landing:takeoffs[countVar]]) - COPy[landing] ) 
                COPtraj.append( np.sum( abs(np.diff((COPy[landing:takeoffs[countVar]]))) ) )
                CT.append( takeoffs[countVar] - landing)
                impulse.append( np.sum(YtotalForce[landing:takeoffs[countVar]]) )
                impulseCT.append(np.sum(YtotalForce[landing:takeoffs[countVar]]) /( takeoffs[countVar] - landing))
                CTimpulse.append(( takeoffs[countVar] - landing)/abs(np.sum(YtotalForce[landing:takeoffs[countVar]]) ))
                indMaxCOP = np.max( COPy[landing:takeoffs[countVar]] ) 
                indMaxFY = np.max( YtotalForce[landing:takeoffs[countVar]] )
                timingDiff.append(indMaxCOP - indMaxFY)
                MaxVertPropulsion.append(abs(np.min(YtotalForce[landing+20:takeoffs[countVar]])))
                CTMaxVertProp.append(( takeoffs[countVar] - landing)/abs(np.min(YtotalForce[landing+20:takeoffs[countVar]])))
                MaxHorizPropulsion.append(abs(np.min(XtotalForce[landing+20:takeoffs[countVar]])))
                CTMaxHorizProp.append(( takeoffs[countVar] - landing)/abs(np.min(XtotalForce[landing+20:takeoffs[countVar]])))
           
                avgdiffCOMCOP.append(np.mean(diffCOMCOP[landing:takeoffs[countVar]])) # The higher the value, the more average difference is present between COM and COP
                sumdiffCOMCOP.append(np.sum(diffCOMCOP[landing:takeoffs[countVar]])) # The higher the value, the more difference present between COM and COP
                maxdiffCOMCOP.append(np.max(diffCOMCOP[landing:takeoffs[countVar]])) #The more positive means COM is less in the positive Y in comparison to COP meaning foot is moving more laterally
                mindiffCOMCOP.append(np.min(diffCOMCOP[landing:takeoffs[countVar]])) #negative indicating that COM is more in positive Y than COP meaning the foot is moving more medially
                subName.append(fName.split('_')[0])
                config.append( config1 )
                movements.append( tmpMove )
    
                ## Pk Moments ##
                # ankleSagMom.append(np.max(dat.LAnkleMomentx[landing : takeoffs[countVar]]))
                # ankleFrontMom.append(np.max(dat.LAnkleMomenty[landing : takeoffs[countVar]]))
                # kneeSagMom.append(np.min(dat.LKneeMomentX[landing : takeoffs[countVar]]))
                # kneeFrontMom.append(np.min(dat.LKneeMomentY[landing : takeoffs[countVar]]))
                #hipSagMom.append(np.max(dat.LeftHipMomentSagittal[landing : landing + tmpStab]))
                #hipFrontMom.append(np.max(dat.LeftHipMomentFrontal[landing : landing + tmpStab]))
                ## Angles ## 
                # ankleXAng.append(np.max(dat.LAnkleAngleX[landing : takeoffs[countVar]]))
                # ankleYAng.append(np.min(dat.LAnkleAngleY[landing : takeoffs[countVar]]))
                # kneeYAng.append(np.max(dat.LKneeYAngle[landing : takeoffs[countVar]]))
                # kneeZAng.append(np.max(dat.LKneeZAngle[landing : takeoffs[countVar]]))
                # kneeXAng.append(np.max(dat.LKneeXAngle[landing : takeoffs[countVar]]))
                
                
            
            except:
                print(landing)
    except:
        print(file)
# landingToPlot = 2
# fig, (ax7, ax9) = plt.subplots(2)
# ax7.plot(COPy[landings[landingToPlot]:takeoffs[landingToPlot]])
# ax7.plot(COMY[landings[landingToPlot]:takeoffs[landingToPlot]])
# ax7.set_xlabel('Time')
# ax7.set_ylabel('COP and COM')
# ax7.set_title('One Landing COP and COM')
# ax9.plot(diffCOMCOP[landings[landingToPlot]:takeoffs[landingToPlot]])
# ax9.set_xlabel('Time')
# ax9.set_ylabel('DiffCOPCOM')
# ax9.set_title('DiffCOPCOM')
# fig.tight_layout() 
outcomes = pd.DataFrame({'Sub':list(subName), 'Config': list(config), 'Movement':list(movements),
                         'copExc': list(COPexcursion), 'timingDiff':list(timingDiff), 'CT':list(CT),
                         'impulse':list(impulse), 'RFD':list(RFDcon), 'COPtraj':list(COPtraj), 'AvergaeCOPCOM Diff':list(avgdiffCOMCOP), 
                         'SumDiffCOPCOM':list(sumdiffCOMCOP),'MaxdiffCOMCOP':list(maxdiffCOMCOP), 'MindiffCOMCOP':list(mindiffCOMCOP),
                         'ImpulseCT':list(impulseCT),'CTImpulse':list(CTimpulse), 'MaxVertPropulsion':list(MaxVertPropulsion), 'CTMaxVertProp':list(CTMaxVertProp),
                         'MaxHorizPropulsion':list(MaxHorizPropulsion), 'CTMaxHorizProp':list(CTMaxHorizProp),'ankleWork': list(ankleWork),
                         'kneeWork': list(kneeWork)})

outcomes.to_csv("C:/Users/Adam.Luftglass/OneDrive - Boa Technology Inc/Documents/AdamLookingAtCOMDataTennis/New All Performance/All Data.csv", mode ='a', header = True)


