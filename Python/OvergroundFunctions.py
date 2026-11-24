# -*- coding: utf-8 -*-
"""
Shared functions for the overground lab analyses.

Everything here is called by at least two of the scripts in this folder.
Anything used by only one script stays in that script.

Where two scripts had drifted apart, the function takes an argument for the
difference rather than picking a winner, and the docstring says which script
passes what. The call site then shows the detection settings instead of them
being buried in two silently different copies.

Note: the two processing-decision helpers at the end are kept byte-identical
to the copies in XSENSOR/XSENSORFunctions.py, TreadmillCodeBOA/Python/
TreadmillFunctions.py and IMU_BOA/IMUFunctions.py. There is no shared package
across the BOA-PFL repos, so if you change one, change the others in the same
commit. The detection functions above are NOT shared across repos - the
treadmill versions of findLandings and findTakeoffs are separate code for
separate data and are deliberately left alone.

@author: Eric.Honert
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime


def delimitTrial(inputDF, FName, FilePath, forceSig):
    """
    Crop a trial to a start and an end chosen by clicking on a force trace.

    The two clicks are saved to <FName>TrialSeg.npy beside the data, so the
    trial is only delimited once - later runs load the saved points and do not
    ask again. Delete that file to re-select.

    Plotting has to be outside the console for the clicks to register: in
    Spyder use %matplotlib qt, or set Tools > Preferences > IPython console >
    Graphics > Backend to Automatic.

    Usage
    -----
    PerformanceTest_Agility:
        delimitTrial(dat, fName, fPath, totForce)
        where totForce sums all four plates, because the agility trials cross
        the whole runway.

    Other scripts in this folder read a single plate - Hike FP2 and FP4,
    SingleLegLanding FP4, StandUp FP3 - and pass that plate's vertical force.
    The signal is an argument rather than being summed here for exactly that
    reason: the four-plate sum this started as was only correct for Agility.

    Parameters
    ----------
    inputDF : Pandas DataFrame
        The whole trial, which is what gets cropped
    FName : str
        File name, used to name the saved click file
    FilePath : str
        Folder holding the data, where the saved click file goes. This used to
        be read from module scope, which meant the function only worked when
        called from a script that happened to define fPath.
    forceSig : Pandas Series or numpy array
        The force to plot for the clicking. Whatever signal makes the start and
        end of the trial easy to see - usually vertical force from the plate or
        plates the trial crosses.

    Returns
    -------
    outputDat : Pandas DataFrame
        inputDF cropped to the two clicked points

    """
    # The saved clicks, if this trial has been delimited before
    segPath = FilePath + FName + 'TrialSeg.npy'

    if os.path.exists(segPath):
        trial_segment_old = np.load(segPath, allow_pickle = True)
        trialStart = trial_segment_old[1][0, 0]
        trialEnd = trial_segment_old[1][1, 0]
        inputDF = inputDF.iloc[int(np.floor(trialStart)) : int(np.floor(trialEnd)), :]
        # Note: reset_index(), not reset_index(drop = True) - this keeps the
        # original index as a column, which is what the existing callers get
        outputDat = inputDF.reset_index()

    else:
        fig, ax = plt.subplots()

        print('Select a point on the plot to represent the beginning & end of trial where Y-value is near 0')

        ax.plot(forceSig, label = 'Force')
        fig.legend()
        pts = np.asarray(plt.ginput(2, timeout = -1))
        plt.close()

        outputDat = inputDF.iloc[int(np.floor(pts[0, 0])) : int(np.floor(pts[1, 0])), :]
        outputDat = outputDat.reset_index()

        trial_segment = np.array([FName, pts], dtype = object)
        np.save(segPath, trial_segment)

    return(outputDat)


def findLandings(force, fThresh, confirmForce = 0, confirmDelay = 10, minGap = 0):
    """
    Find the landings (foot contacts) in a force signal.

    A landing is a sample where the force is zero and the next sample breaches
    fThresh. The optional arguments add two further requirements, both off by
    default.

    Usage
    -----
    PerformanceTest_Agility, PerformanceTest_StandUp_ExtractVariables:
        findLandings(force, fThresh)
        The bare threshold crossing. Agility is rapid cutting, where a
        refractory gap would throw away real contacts that genuinely occur
        close together.

    PerformanceTest_Hike, PerformanceTest_SingleLegLanding_V3:
        findLandings(force, fThresh, confirmForce = 300, minGap = 300)
        Landings in these protocols are discrete and well separated, so the
        detection can afford to be strict: the force has to still be above
        300 N ten samples later, which rejects a single-sample blip across the
        threshold, and no second landing is accepted within 300 samples of the
        last one.

    Parameters
    ----------
    force : Pandas Series or numpy array
        Vertical force from the force plate
    fThresh : float
        Force the signal has to breach to count as a landing
    confirmForce : float
        Force that must still be present confirmDelay samples after the
        crossing. 0, the default, skips the check.
    confirmDelay : int
        How many samples after the crossing confirmForce is tested. Ignored
        when confirmForce is 0.
    minGap : int
        Fewest samples allowed between one landing and the next. 0, the
        default, accepts them however close together they fall. The first
        landing of a trial is never subject to this.

    Returns
    -------
    lic : list
        Indices of the landings

    """
    lic = []

    for step in range(len(force)-1):
        if force[step] != 0:
            continue
        if force[step + 1] < fThresh:
            continue

        # Still loaded a moment later? A crossing that is gone again by the
        # next sample is noise, not a foot landing.
        if confirmForce > 0:
            # Guarded, unlike the copies this came from: a crossing within
            # confirmDelay of the end of the signal used to index past it
            if step + confirmDelay >= len(force):
                continue
            if force[step + confirmDelay] <= confirmForce:
                continue

        # Far enough from the previous landing to be a separate one
        if minGap > 0 and len(lic) > 0:
            if step <= lic[-1] + minGap:
                continue

        lic.append(step)

    return lic


def findTakeoffs(force, fThresh, holdOffsets = ()):
    """
    Find the takeoffs in a force signal.

    A takeoff is the sample after the force drops from above fThresh to zero.
    holdOffsets adds a requirement that the signal is still at zero some
    samples later, which separates a real takeoff from the force momentarily
    passing through zero.

    Usage
    -----
    PerformanceTest_Agility:
        findTakeoffs(force, fThresh)
        Takes the drop to zero at face value.

    PerformanceTest_Hike, PerformanceTest_SingleLegLanding_V3:
        findTakeoffs(force, fThresh, holdOffsets = (5, 10))
        The foot is off the plate for a while in these protocols, so the
        signal is required to still read zero 5 and 10 samples later. Without
        it, a dip through zero inside a contact registers as a takeoff.

    Parameters
    ----------
    force : Pandas Series or numpy array
        Vertical force from the force plate
    fThresh : float
        Force the signal has to be above before the drop to zero
    holdOffsets : tuple of int
        Sample offsets after the crossing that must also read zero. The
        default, an empty tuple, requires nothing beyond the drop itself.

    Returns
    -------
    lto : list
        Indices of the takeoffs

    """
    lto = []

    for step in range(len(force)-1):
        if force[step] < fThresh:
            continue
        if force[step + 1] != 0:
            continue

        # Confirm the signal stays at zero rather than passing through it
        stillZero = True
        for offset in holdOffsets:
            # Guarded, unlike the copies this came from: a takeoff near the
            # end of the signal used to index past it
            if step + offset >= len(force):
                stillZero = False
                break
            if force[step + offset] != 0:
                stillZero = False
                break

        if stillZero == False:
            continue

        lto.append(step + 1)

    return lto


def movAvgForce(force, landing, takeoff, length):
    """
    Rolling mean of the force signal between a landing and a takeoff.

    Used with movSDForce to judge when someone has stabilised: the average
    says where the force has settled, the standard deviation says how still it
    is. One of several published ways of deciding when a subject is stationary.

    Usage
    -----
    PerformanceTest_Hike, PerformanceTest_SingleLegLanding_V3:
        movAvgForce(forceZ, landing, landing + 200, 10)
        A 10-sample rolling mean over the 200 samples following the landing,
        which at 200 Hz is the first second after touchdown.

    Parameters
    ----------
    force : Pandas Series
        Force from the force plate
    landing : int
        Index to start at, from findLandings
    takeoff : int
        Index to stop at, from findTakeoffs - or simply the landing plus a
        fixed number of samples, which is what both current callers pass
    length : int
        Window length, in samples, of the rolling mean

    Returns
    -------
    avgF : list
        Rolling mean of the force

    """
    newForce = np.array(force)
    win_len = length # window length for steady standing
    avgF = []
    for ii in range(landing, takeoff):
        avgF.append(np.mean(newForce[ii : ii + win_len]))
    return avgF


def movSDForce(force, landing, takeoff, length):
    """
    Rolling standard deviation of the force signal between a landing and a
    takeoff.

    The companion to movAvgForce - see that function for how the pair is used.

    Usage
    -----
    PerformanceTest_Hike, PerformanceTest_SingleLegLanding_V3:
        movSDForce(forceZ, landing, landing + 200, 10)
        Same window as the matching movAvgForce call, which it has to be for
        findStabilization to compare them sample for sample.

    Parameters
    ----------
    force : Pandas Series
        Force from the force plate
    landing : int
        Index to start at, from findLandings
    takeoff : int
        Index to stop at
    length : int
        Window length, in samples, of the rolling standard deviation

    Returns
    -------
    sdF : list
        Rolling standard deviation of the force

    """
    newForce = np.array(force)
    win_len = length # window length for steady standing
    sdF = []
    for ii in range(landing, takeoff):
        sdF.append(np.std(newForce[ii : ii + win_len]))
    return sdF


def findBW(avgF, startIdx = 100, endIdx = 200):
    """
    Estimate body weight from a quiet portion of the rolling average force.

    For use when the subject's body weight was not recorded, or when the
    weight as the plate sees it is wanted. Highly conditional on how the trial
    was collected: the default indices assume quiet standing between samples
    100 and 200 of the rolling average.

    Note: this used to take an argument named "force" and then ignore it,
    reading a module-level avgF instead. It worked because the one thing every
    caller passed was the variable that global pointed at. The argument is now
    the thing that gets averaged, which is what the callers already intended.

    Usage
    -----
    PerformanceTest_Hike, PerformanceTest_SingleLegLanding_V3:
        findBW(avgF)
        Called on the rolling average from movAvgForce, immediately after it,
        and the result is passed straight to findStabilization.

    Parameters
    ----------
    avgF : list or numpy array
        Rolling average force, from movAvgForce
    startIdx : int
        First index of the quiet portion to average over
    endIdx : int
        One past the last index of the quiet portion

    Returns
    -------
    BW : float
        Estimated body weight of the subject, in Newtons

    """
    BW = np.mean(avgF[startIdx:endIdx])
    return BW


def findStabilization(avgF, sdF, subBW, bwTol = 0.05, sdThresh = 20):
    """
    Find when the force signal settles, from the rolling average and standard
    deviation.

    Stabilisation is the first sample where the rolling average sits within
    bwTol of the subject's body weight AND the rolling standard deviation is
    below sdThresh. Both conditions are needed: the average alone is satisfied
    while passing through body weight on the way somewhere else.

    Note: subBW used to be read from module scope rather than passed in, which
    meant the function could only be called from a script that happened to
    have defined it on the line above. It is now an argument.

    Usage
    -----
    PerformanceTest_Hike, PerformanceTest_SingleLegLanding_V3:
        findStabilization(avgF, sdF, subBW)
        The result is divided by the collection frequency at the call site to
        give a time in seconds.

    Parameters
    ----------
    avgF : list
        Rolling average of force, from movAvgForce
    sdF : list
        Rolling standard deviation of force, from movSDForce, over the same
        window as avgF
    subBW : float
        Subject body weight in Newtons, from findBW or from the subject log
    bwTol : float
        Fraction of body weight the average may sit either side of it. The
        default of 0.05 is +/- 5%.
    sdThresh : float
        Standard deviation the signal must fall below, in Newtons

    Returns
    -------
    int or float
        Index of the first stabilised sample. NaN when the signal never
        settles, which used to raise IndexError on stab[0] and take the whole
        run with it.

    """
    stab = []
    for step in range(len(avgF)-1):
        aboveLow = avgF[step] >= (subBW - bwTol*subBW)
        belowHigh = avgF[step] <= (subBW + bwTol*subBW)
        isStill = sdF[step] < sdThresh

        if aboveLow and belowHigh and isStill:
            stab.append(step + 1)

    if len(stab) == 0:
        return np.nan

    return stab[0]

#______________________________________________________________________________
# Processing-decision helpers.
# Note: these two functions are kept byte-identical to the copies in
# XSENSOR/XSENSORFunctions.py, TreadmillCodeBOA/Python/TreadmillFunctions.py
# and IMU_BOA/IMUFunctions.py. There is no shared package across the BOA-PFL
# repos, so if you change one, change the others in the same commit.


def loadProcessingDecisions(fPath, scriptName):
    """
    Load the data-quality decisions recorded by previous runs of this script.

    Decisions live in 0_ProcessingDecisions_<scriptName>.csv beside the data.
    The name carries the script because one data folder is often read by
    several scripts, and they do not judge the same thing - a trial that is
    unusable for one analysis can be perfectly good for another. A shared file
    would let one script's rejection silently govern the rest.

    The file is append-only: correcting a decision means adding a later row for
    the same file rather than editing the original, so the record of what was
    judged and when is preserved. The most recent row for a file is the one
    that counts.

    Reading these back is what stops a trial being judged a second time. A file
    already marked good is processed without the dialog box appearing again.

    Rejected files are left where they are. Nothing is moved out of the folder,
    so a rejected trial can still be opened and looked at; it is this record,
    not the folder, that decides what gets processed.

    Parameters
    ----------
    fPath : str
        Path to the folder holding the data and the decision file
    scriptName : str
        Short name of the calling script, set as a constant at the top of it

    Returns
    -------
    decisions : dict
        File name -> 'good' or 'bad'. Empty if nothing has been decided yet.

    """
    decisionFile = fPath + '0_ProcessingDecisions_' + scriptName + '.csv'
    if os.path.exists(decisionFile) == False:
        return {}

    dat = pd.read_csv(decisionFile)

    # The latest row for a file wins. Sort on the parsed timestamp, not on the
    # raw text: opening this file in Excel to correct a decision rewrites every
    # timestamp into the local format, and sorting those as text puts 9:52
    # after 10:15 because the hour has no leading zero. A row whose timestamp
    # will not parse at all is taken as the newest, since that is almost always
    # someone having typed a correction in by hand.
    stamps = pd.to_datetime(dat['Timestamp'], errors='coerce', format='mixed')
    dat['SortStamp'] = stamps
    dat_sorted = dat.sort_values('SortStamp', kind='stable', na_position='last')
    latest = dat_sorted.drop_duplicates(subset='FileName', keep='last')

    # Preallocate
    decisions = {}
    for ii in range(len(latest)):
        fName = latest['FileName'].iloc[ii]
        decisions[fName] = latest['Decision'].iloc[ii]

    return decisions

def saveProcessingDecision(fPath, scriptName, fName, decision, Subject='', Config='', reason=''):
    """
    Append one data-quality decision to this script's decision file.

    Call this inside the processing loop, immediately after the decision is
    made, so that a run which fails part way through still keeps every decision
    taken up to that point.

    Note: this appends on purpose, and is the one place in these scripts where
    appending is correct. The file is a decision history that must never be
    overwritten. Data outputs are a different matter - those are written fresh
    each run, because appending to them produces duplicate rows.

    Parameters
    ----------
    fPath : str
        Path to the folder holding the data
    scriptName : str
        Short name of the calling script, matching loadProcessingDecisions
    fName : str
        Name of the file the decision applies to. For IMU trials this is the
        low-g file, since that is what the processing loops index through.
    decision : str
        'good' or 'bad'
    Subject : str
        Subject name, for reading the file by eye
    Config : str
        Configuration, for reading the file by eye
    reason : str
        Free text. Worth filling in when a trial is rejected.

    Returns
    -------
    None

    """
    decisionFile = fPath + '0_ProcessingDecisions_' + scriptName + '.csv'
    stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    row = pd.DataFrame({'Timestamp':[stamp], 'FileName':[fName],
                        'Subject':[Subject], 'Config':[Config],
                        'Decision':[decision], 'Reason':[reason]})

    # Only write the header when the file is being created
    writeHeader = os.path.exists(decisionFile) == False
    row.to_csv(decisionFile, mode='a', header=writeHeader, index=False)
