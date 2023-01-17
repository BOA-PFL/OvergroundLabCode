

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import copy

# Define constants and options
fThresh = 80  # below this value will be set to 0.

# Read in balance file


fPath = 'C:/Users/adam.luftglass/OneDrive - Boa Technology Inc/General/Testing Segments/Material Testing/Speedland/Overground/'


fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt)]
stepLen = 50
x = np.linspace(0,stepLen,stepLen)

def findLandings(force, fThresh):
    """
    This function finds the landings from force plate data
    it uses a heuristic to determine landings from when the smoothed force is
    0 and then breaches a threshold

    Parameters
    ----------
    force : Pandas Series
        Vertical force from force plate.
    fThresh: integer
        Value force has to be greater than to count as a takeoff/landing
    Returns
    -------
    lic : list
        Indices of landings.
    """
    lic = []

    for step in range(len(force)-1):

            if force[step] == 0 and force[step + 1] >= fThresh:
                lic.append(step)

    return lic


def findTakeoffs(force, fThresh):
    """
    This function calculates the takeoffs using a heuristic
    Parameters
    ----------
    force : Pandas Series
        vertical force from force plate.

    fThresh: integer
        Value force has to be greater than to count as a takeoff/landing
    Returns
    -------
    lto : list
        indices of takeoffs obtained from force data. Takeoffs here mean
        the moment a force signal was > a threshold and then goes to 0
    # """
    lto = []
    for step in range(len(force)-1):
        if force[step] >= fThresh and force[step + 1] == 0:
            lto.append(step + 1)
    return lto

    # lto = []
    # for step in range(len(force)-1):
    #     if force[step] >= fThresh and force[step + 1] == 0 and force[step + 5] == 0 and force[step + 10] == 0:
    #         lto.append(step + 1)
    # return lto


def delimitTrial(inputDF):
    """
      This function uses ginput to delimit the start and end of a trial
    You will need to indicate on the plot when to start/end the trial.
    You must use tkinter or plotting outside the console to use this function
    Parameters
    ----------
    inputDF : Pandas DataFrame
        DF containing all desired output variables.
    zForce : numpy array
        of force data from which we will subset the dataframe
    Returns
    -------
    outputDat: dataframe subset to the beginning and end of jumps.
    """

    # generic function to plot and start/end trial #
    fig, ax = plt.subplots()
    totForce = dat.FP1_GRF_Z + dat.FP2_GRF_Z + dat.FP3_GRF_Z + dat.FP4_GRF_Z
    ax.plot(totForce, label='Total Force')
    fig.legend()
    pts = np.asarray(plt.ginput(2, timeout=-1))
    plt.close()
    outputDat = dat.iloc[int(np.floor(pts[0, 0])): int(np.floor(pts[1, 0])), :]
    outputDat = outputDat.reset_index()
    return(outputDat)


def makeNewFig(avgVal1, sdVal1, avgVal2, sdVal2, avgVal3, sdVal3, Ylabel1, Ylabel2, Ylabel3):
    
        # plot ensemble average values from landings defined in a
        # a different function above. Takes the avg and std of the columns
        # as inputs
        fig, (ax1, ax2, ax3) = plt.subplots(1,3)
        
        ax1.plot(x, avgVal1, 'k', color='#00966C')
        ax1.set_xlabel('Time')
        ax1.set_ylabel(f"{Ylabel1}")
        ax1.fill_between(x, avgVal1-sdVal1, avgVal1+sdVal1,
            alpha=0.5, edgecolor='#00966C', facecolor='#00966C')

        ax2.plot(x, avgVal2, 'k', color='#00966C')
        ax2.set_xlabel('Time')
        ax2.set_ylabel(f"{Ylabel2}")
        ax2.fill_between(x, avgVal2-sdVal2, avgVal2+sdVal2,
            alpha=0.5, edgecolor='#00966C', facecolor='#00966C')

        ax3.plot(x, avgVal3, 'k', color='#00966C')
        ax3.set_xlabel('Time')
        ax3.set_ylabel(f"{Ylabel3}")
        ax3.fill_between(x, avgVal3-sdVal3, avgVal3+sdVal3,
            alpha=0.5, edgecolor='#00966C', facecolor='#00966C')

        plt.tight_layout()


CT = []

impulseZ = []
impulseX = []
peakGRFz = []
peakGRFx = []
peakPFmom = []
peakINVmom = []
peakKneeEXTmom = []
kneeABDrom = []
eccWork = []
peakPower = []
peakpropulse = []

jumpHeight = []
impulse = []
jumpTime = []

posankwork = []
subName = []
config = []
movements = []
combomoment = []

# save configuration names from files
for fName in entries:
    try:

        #fName = entries[61]

        config1 = fName.split('_')[1]
        tmpMove = fName.split('_')[2]

        dat = pd.read_csv(fPath+fName, sep='\t', skiprows=8, header=0)
        dat = dat.fillna(0)

        landings = []  # erase landings and takeoffs from last loop
        takeoffs = []
        if (tmpMove == 'Skater') or (tmpMove == 'skater'):

            dat = delimitTrial(dat)
            # create vector of force from vertical signal from each file and make low values 0
           
            ZForce = dat.FP4_GRF_Z
            XForce = dat.FP4_GRF_X
            YForce = dat.FP4_GRF_Y

            if abs(np.min(XForce)) > abs(np.max(XForce)):
                XForce = XForce * -1

            # dat = delimitTrialSkate(dat)
            ZForce[ZForce < fThresh] = 0

            # find the landings from function above
            landings = findLandings(ZForce, fThresh)
            takeoffs = findTakeoffs(ZForce, fThresh)

            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]]



        elif (tmpMove == 'CMJ') or (tmpMove == 'cmj'):

            dat = delimitTrial(dat)

            ZForce = dat.FP2_GRF_Z
            ZForce[ZForce < fThresh] = 0

            XForce = dat.FP2_GRF_X
            YForce = dat.FP2_GRF_Y

            landings = findLandings(ZForce, fThresh)
            takeoffs = findTakeoffs(ZForce, fThresh)
            

            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]]


        elif (tmpMove == 'Triangle') or (tmpMove == 'triangle'):
     
            #dat = delimitTrial(dat)
     

            ZForce = dat.FP1_GRF_Z + dat.FP2_GRF_Z
            ZForce[ZForce<fThresh] = 0
     
            XForce = dat.FP1_GRF_X + dat.FP2_GRF_X
            YForce = dat.FP1_GRF_Y + dat.FP2_GRF_Y
             
     
            landings = findLandings(ZForce, fThresh)
            takeoffs = findTakeoffs(ZForce, fThresh)
     

    
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]] 
        elif (tmpMove == 'AP') or (tmpMove == 'ap'):
     
           # dat = delimitTrial(dat)
     

            ZForce = dat.FP2_GRF_Z 
            ZForce[ZForce<fThresh] = 0
     
            XForce = dat.FP2_GRF_X
            YForce = dat.FP2_GRF_Y
             
     
            landings = findLandings(ZForce, fThresh )
            takeoffs = findTakeoffs(ZForce, fThresh)
     

    
            landings[:] = [x for x in landings if x < takeoffs[-1]]
            takeoffs[:] = [x for x in takeoffs if x > landings[0]]
           
        else:
            print('this movement is not included in Performance Test Analysis')
        
        
        for i in range(len(landings)):
         

            try:
                
                # i = 0
                CT.append((takeoffs[i] - landings[i])/200)
                impulseZ.append(np.sum(ZForce[landings[i]:takeoffs[i]])/200)
                impulseX.append(np.sum(XForce[landings[i]:takeoffs[i]])/200)
                
                #peakGRFz.append(np.max(ZForce[landings[i]:takeoffs[i]]))
                #peakGRFx.append(np.max(XForce[landings[i]:takeoffs[i]]))
            
                peakPFmom.append(np.min(dat.RAnkleMoment_Sagittal[landings[i]:takeoffs[i]])*-1)
                peakINVmom.append(np.max(dat.RAnkleMoment_Frontal[landings[i]:takeoffs[i]]))
                peakKneeEXTmom.append(np.max(dat.RKneeMoment_Sagittal[landings[i]:takeoffs[i]]))
                kneeABDrom.append(np.max(dat.RKneeAngle_Frontal[landings[i]:takeoffs[i]]) - np.min(dat.RKneeAngle_Frontal[landings[i]:takeoffs[i]]))
                negpower = copy.deepcopy(dat.COM_Power)
                negpower[negpower>0] = 0
                eccWork.append(np.sum(negpower[landings[i]:takeoffs[i]])/200*-1)
                
                peakPower.append(np.max(dat.COM_Power[landings[i]:takeoffs[i]]))
                peakpropulse.append(np.max(ZForce[round(landings[i]+((takeoffs[i]-landings[i])/2)):takeoffs[i]]))
                subName.append(fName.split('_')[0])
                config.append( config1 )
                movements.append( tmpMove )
                
                
                
                try: 
                    jumpHeight.append(np.max(dat.Pelvis_Position_Z[takeoffs[i]:landings[i+1]])-np.min(dat.Pelvis_Position_Z[takeoffs[i]:landings[i+1]]))

                except:
                    jumpHeight.append(0)
            except:

                print(fName + str(i))
                
                
     
               
    

    except:
        print(fName)

           


    
                            
                            


outcomes = pd.DataFrame({'Subject':list(subName), 'Config': list(config), 'Movement':list(movements),


                         'CT':list(CT), 'impulse_Z':list(impulseZ), 'impulse_X':list(impulseX), 'peakPFmom':list(peakPFmom), 'eccWork':list(eccWork),
                         'peakINVmom':list(peakINVmom), 'peakKneeEXTmom':list(peakKneeEXTmom), 'kneeABDrom':list(kneeABDrom),  'peakpropulse':list(peakpropulse), 
                         'jumpheight':list(jumpHeight), 'peakPower':list(peakPower) })

                       

outfileName = fPath + 'CompiledAgilityData.csv'
outcomes.to_csv(outfileName, index = False)