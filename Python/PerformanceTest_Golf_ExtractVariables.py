# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 13:59:13 2023

@author: Milena.Singletary
"""

 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.signal as sig
from tkinter import messagebox
import math
from  datetime import datetime, timedelta


import scipy
from scipy.interpolate import interp1d

fPath = 'C:\\Users\\milena.singletary\\OneDrive - BOA Technology Inc\\General - PFL Team\\Testing Segments\\Athletic\\Golf\\2026_Performance_AysmPFS_Adidas\\Overground\\'
fileExt = r".txt"
entries = [fName for fName in os.listdir(fPath) if fName.endswith(fileExt) and 'rive' in fName]
massdf =  pd.read_excel('C:\\Users\\milena.singletary\\OneDrive - BOA Technology Inc\\General - PFL Team\\Testing Segments\\Athletic\\Golf\\2026_Performance_AysmPFS_Adidas\\CompiledQualData_AdiAysm28.xlsx', sheet_name= 'Anthro')
tmPath = 'C:\\Users\\milena.singletary\\OneDrive - BOA Technology Inc\\General - PFL Team\\Testing Segments\\Athletic\\Golf\\2026_Performance_AysmPFS_Adidas\\Trackman\\'

# one Trackman file per subject: store by subject name
trackman = {}
for tmName in os.listdir(tmPath):
    if tmName.endswith('.csv'):
        tmDat = pd.read_csv(tmPath + tmName, header = 1)
        tmDat = tmDat.iloc[1:].reset_index(drop = True) # drop units row
        tmDat['ShotTime'] = pd.to_datetime(tmDat['Date'], format = '%m/%d/%Y %I:%M:%S %p')
        trackman[tmName.split(sep = '_')[0]] = tmDat



def checkPhases(FName):
    if os.path.exists(fPath+FName+'SwingSeg.npy'):
        swing_segment_stored = np.load(fPath+FName+'SwingSeg.npy', allow_pickle =True)
        swgStart = swing_segment_stored[1]
        transition = swing_segment_stored[2]
        bc = swing_segment_stored[3]
        swgEnd = swing_segment_stored[4]


    return swgStart, transition, bc, swgEnd


def segManual(leadGRF_z, trailGRF_z):
    s = [] # start
    t = [] # transition
    bc = []
    e = [] # end
    plt.plot(leadGRF_z)
    plt.plot(trailGRF_z)
    collectPts = np.asarray(plt.ginput(-1, timeout=-1, mouse_add=None, mouse_pop=None, mouse_stop=None))

    
    # append corrected transitions to array for replotting/saving
    for ii in range(0,len(collectPts),3):
        s.append(int(collectPts[ii,0]))
    for ii in range(1, len(collectPts),3):
        t.append(int(collectPts[ii,0]))
    for ii in range(2, len(collectPts),3):
        b = int(collectPts[ii,0]) + 30
        bc.append(b)
    for ii in range(3,len(collectPts),3):
        e.append(int(collectPts[ii,0]))
    
    return s, t, bc, e


def getStartTime(FName):
    """ Pull the recording start time and sampling rate from the overground file header """
    with open(fPath + FName) as fh:
        header = [next(fh) for _ in range(4)]
    tsLine = header[2].split('\t')  # name, date, time
    startTime = datetime.strptime(tsLine[1] + ' ' + tsLine[2], '%d-%m-%Y %H:%M:%S:%f')
    freq = float(header[3].split('\t')[0])
    return startTime, freq


def findShotPeaks(GRF_z, startTime, freq, tmDat, winBefore = 100, winAfter = 200):
    """
    Convert Trackman shot times to frames and find the max GRF from winBefore frames before
    to winAfter frames after each shot. Window is skewed later because Trackman truncates
    shot times to the second, so impact occurs 0-1 s after the listed time.
    Returns peak indices, Trackman shot frames, and the Trackman rows that fall in this trial.
    """
    shotFr = ((tmDat['ShotTime'] - startTime).dt.total_seconds() * freq).round().astype(int)
    inTrial = (shotFr >= 0) & (shotFr < len(GRF_z))
    shots = tmDat[inTrial].reset_index(drop = True)
    shotFr = shotFr[inTrial].values

    pkIdx = []
    for fr in shotFr:
        st = max(fr - winBefore, 0)
        en = min(fr + winAfter, len(GRF_z))
        pkIdx.append(st + np.argmax(GRF_z[st:en]))
    return np.array(pkIdx), shotFr, shots


def findSwingPeaksGRF(leadGRF_z, trailGRF_z, BW, freq):
    """
    Find swing peaks from the force plates alone (no Trackman). Candidate lead GRF peaks are kept
    only if they show the swing weight-shift pattern (thresholds in BW, from Trackman-confirmed swings):
        - 1 s before peak: lead median 0.30-0.55 BW (weight split at address)
        - 1 s before peak: trail max 0.75-0.95 BW (backswing load onto trail)
        - 0.2 s after peak: trail > 0.15 BW (trail foot still on plate, not stepping off)
    """
    pks, _ = sig.find_peaks(leadGRF_z, height = 0.85*BW, prominence = 0.15*BW, distance = int(freq))
    pre = int(freq)
    post = int(0.2*freq)

    swgIdx = []
    for pk in pks:
        if pk - pre < 0 or pk + post >= len(leadGRF_z):
            continue
        leadPre = np.median(leadGRF_z[pk-pre:pk]) / BW
        trailPreMax = np.max(trailGRF_z[pk-pre:pk]) / BW
        trailPost = trailGRF_z[pk+post] / BW
        if (0.30 <= leadPre <= 0.55) and (0.75 <= trailPreMax <= 0.95) and (trailPost > 0.15):
            swgIdx.append(pk)
    return np.array(swgIdx, dtype = int)


def findSwingEvents(leadGRF_z, trailGRF_z, swgpks, BW, freq, thrStart = (0.01, 0.02, 0.03), endFrac = 0.9, leadGRF_x = None, splitRange = (0.3, 0.7)):
    """
    Find swing start, approximate ball contact, and swing end around each swing peak.
        - Swing start: end of the last quiet period (address) within 1.6 s before the peak.
          Quiet = rolling SD (0.2 s window) of BOTH plates' vertical GRF below a threshold (in BW),
          held 0.1 s. Thresholds in thrStart are tried in order, so golfers who fidget at address
          still get a start. The weight must also be split between the feet (each plate's vertical
          GRF within splitRange, in BW) so a pause at the top of the backswing, with the weight on
          the trail foot, is not taken as address.
          If no quiet period is found:
            * swing within 1.6 s of the start of the trial (address happened before data was
              collected): swing start = first frame of the trial
            * otherwise (e.g. golfer settles only briefly at address): swing start = the quietest
              frame (lowest rolling SD) with the weight split, within 1.6 s before the peak
          so every swing has a start.
        - Ball contact: most negative lead AP GRF (leadGRF_x) between the lead vertical GRF
          minimum and the lead (swing) peak. The lead vertical minimum is the min lead GRF between
          the trail vertical GRF peak and the swing peak. The trail peak is the max trail GRF from
          swing start (or 0.6 s before the peak if no start was found) to 0.15 s before the swing
          peak. The last 0.15 s is skipped so the trail peak is the backswing load, not the impact
          transient that shows on both plates at the swing peak for some golfers.
          If leadGRF_x is not given, ball contact is the lead vertical GRF minimum.
        - Swing end: first frame after the swing peak where lead vertical GRF falls below
          endFrac of the peak value (the peak beginning to fall)
    Returns arrays of start, contact, end indices (-1 where an event is not found).
    """
    win = int(0.2*freq)
    minQuiet = int(0.1*freq)
    sdLead = pd.Series(leadGRF_z/BW).rolling(win, center = True).std().values
    sdTrail = pd.Series(trailGRF_z/BW).rolling(win, center = True).std().values
    sdMax = np.fmax(sdLead, sdTrail)
    # weight split between the feet, as at address
    split = ((leadGRF_z/BW >= splitRange[0]) & (leadGRF_z/BW <= splitRange[1]) &
             (trailGRF_z/BW >= splitRange[0]) & (trailGRF_z/BW <= splitRange[1]))

    swgStart = []
    ballContact = []
    swgEnd = []
    for pk in swgpks:
        # swing start: walk back from the peak to the last sustained quiet period with the weight split
        st = -1
        srchSt = max(pk - int(1.6*freq), 0)
        for thr in thrStart:
            quiet = (sdMax[srchSt:pk] < thr) & split[srchSt:pk]
            runLen = 0
            for jj in range(len(quiet)-1, -1, -1):
                runLen = runLen + 1 if quiet[jj] else 0
                if runLen >= minQuiet:
                    st = srchSt + jj + minQuiet - 1  # last quiet frame
                    break
            if st >= 0:
                break

        # no quiet period found
        if st < 0:
            if pk - int(1.6*freq) <= 0:
                # swing at the start of the trial: address was before data collection
                st = 0
            else:
                # quietest frame with the weight split before the peak
                cand = np.where(split[srchSt:pk] & ~np.isnan(sdMax[srchSt:pk]))[0]
                if len(cand) > 0:
                    st = srchSt + cand[np.argmin(sdMax[srchSt:pk][cand])]

        # ball contact: lead vertical GRF minimum between the trail GRF peak and the lead GRF peak,
        # then the most negative lead AP GRF between that minimum and the lead GRF peak
        bc = -1
        srchSt = st if st >= 0 else max(pk - int(0.6*freq), 0)
        srchEn = pk - int(0.15*freq)
        if srchEn > srchSt:
            trailPk = srchSt + np.argmax(trailGRF_z[srchSt:srchEn])
            if pk > trailPk:
                bc = trailPk + np.argmin(leadGRF_z[trailPk:pk])
                if leadGRF_x is not None and pk > bc:
                    bc = bc + np.argmin(leadGRF_x[bc:pk+1])

        # swing end: lead GRF peak begins to fall
        en = -1
        falling = np.where(leadGRF_z[pk:min(pk + int(1*freq), len(leadGRF_z))] < endFrac*leadGRF_z[pk])[0]
        if len(falling) > 0:
            en = pk + falling[0]

        swgStart.append(st)
        ballContact.append(bc)
        swgEnd.append(en)
    return np.array(swgStart), np.array(ballContact), np.array(swgEnd)


def plotGlobalCOP(dat, swgstart, ballCon, swgend, swgpks, FilePath, titleStr, minFz = 20):
    """
    Plot the global (net) center of pressure of one representative swing per file, from swing start
    to swing end. The plate COPs in the export are already in lab coordinates (m), so the global COP
    is the vertical-force-weighted average of the trail (FP2) and lead (FP3) COPs:
        COP_global = (COP_FP2 * Fz_FP2 + COP_FP3 * Fz_FP3) / (Fz_FP2 + Fz_FP3)
    The representative swing is the middle swing (in time) with a valid start < ball contact < end.
    Lab Y (the line between the feet) is on the horizontal axis, reversed so the lead/left foot is on
    the left and the trail/right foot on the right, and lab X is on the vertical axis, both in cm. Each foot's own plate COP is drawn faintly for reference.
    Saved to FilePath/GlobalCOP/<titleStr> GlobalCOP.png

    Parameters
    ----------
    dat : DataFrame
        Overground data with FP2/FP3 GRF_Z, COP_X, COP_Y
    swgstart, ballCon, swgend, swgpks : numpy array
        Swing events and swing peaks (-1 = not found)
    FilePath : str
        file path string; the plot is saved in FilePath/GlobalCOP
    titleStr : str
        plot title, also used as the file name
    minFz : float
        frames with total vertical force below this (N) are not drawn

    Returns
    -------
    fig : matplotlib figure (None if there is no complete swing)

    """
    valid = [ii for ii in range(len(swgstart)) if 0 <= swgstart[ii] < ballCon[ii] < swgend[ii]]
    if len(valid) == 0:
        print('No complete swing to plot global COP for: ' + titleStr)
        return None
    sw = valid[len(valid) // 2]
    st, bc, en, pk = swgstart[sw], ballCon[sw], swgend[sw], swgpks[sw]

    Fz2 = dat.FP2_GRF_Z.values[st:en+1]; Fz3 = dat.FP3_GRF_Z.values[st:en+1]
    Fz2 = np.clip(Fz2, 0, None); Fz3 = np.clip(Fz3, 0, None) # no negative weights from plate noise
    FzTot = Fz2 + Fz3
    with np.errstate(invalid = 'ignore', divide = 'ignore'):
        gX = (dat.FP2_COP_X.values[st:en+1] * Fz2 + dat.FP3_COP_X.values[st:en+1] * Fz3) / FzTot * 100
        gY = (dat.FP2_COP_Y.values[st:en+1] * Fz2 + dat.FP3_COP_Y.values[st:en+1] * Fz3) / FzTot * 100
    gX[FzTot < minFz] = np.nan; gY[FzTot < minFz] = np.nan

    # each foot's plate COP (cm), only while that foot is loaded
    footCOP = {}
    for fp, Fz in (('FP2', Fz2), ('FP3', Fz3)):
        fx = dat[fp + '_COP_X'].values[st:en+1] * 100; fy = dat[fp + '_COP_Y'].values[st:en+1] * 100
        fx = np.where(Fz > minFz, fx, np.nan); fy = np.where(Fz > minFz, fy, np.nan)
        footCOP[fp] = (fx, fy)

    fig, ax = plt.subplots(figsize = (9, 6), layout = 'constrained')
    ax.plot(footCOP['FP2'][1], footCOP['FP2'][0], color = 'C1', alpha = 0.35, linewidth = 1, label = 'Trail foot COP (FP2)')
    ax.plot(footCOP['FP3'][1], footCOP['FP3'][0], color = 'C0', alpha = 0.35, linewidth = 1, label = 'Lead foot COP (FP3)')

    # global COP: start -> ball contact and ball contact -> end in different colors
    b, p = bc - st, pk - st
    ax.plot(gY[:b+1], gX[:b+1], color = 'k', linewidth = 2, label = 'Global COP: start to ball contact')
    ax.plot(gY[b:], gX[b:], color = 'red', linewidth = 2, label = 'Global COP: ball contact to end')
    ax.scatter(gY[0], gX[0], color = 'lime', edgecolor = 'k', s = 60, zorder = 3, label = 'Swing start')
    ax.scatter(gY[b], gX[b], color = 'w', edgecolor = 'k', marker = 'X', s = 90, zorder = 3, label = 'Ball contact')
    if 0 <= p < len(gY):
        ax.scatter(gY[p], gX[p], color = 'gold', edgecolor = 'k', marker = '*', s = 140, zorder = 3, label = 'Swing peak (lead GRF)')
    ax.scatter(gY[-1], gX[-1], color = 'red', edgecolor = 'k', marker = 's', s = 50, zorder = 3, label = 'Swing end')

    ax.set_aspect('equal', adjustable = 'datalim')
    # lab Y increases from the trail (FP2) to the lead (FP3) plate: reverse the axis so the lead/left
    # foot is on the left side of the figure and the trail/right foot on the right
    ax.invert_xaxis()
    ax.set_xlabel('Lab Y (cm): lead/left foot <- -> trail/right foot')
    ax.set_ylabel('Lab X (cm)')
    ax.set_title(titleStr + '\nGlobal COP: representative swing (swing ' + str(sw + 1) + ' of ' + str(len(swgstart)) + ')')
    fig.legend(loc = 'outside right center', fontsize = 8)

    if FilePath is not None:
        saveFolder = FilePath + 'GlobalCOP'
        if os.path.exists(saveFolder) == False:
            os.mkdir(saveFolder)
        plt.savefig(saveFolder + '/' + titleStr + ' GlobalCOP.png')
    return fig


def normSwingGlobalCOP(dat, swgstart, ballCon, swgend, nPre = 101, nPost = 51, minFz = 20):
    """
    Time-normalize the global COP (cm, same calculation as plotGlobalCOP) of every complete swing in
    a file so swings can be averaged. Each swing is normalized in two parts so ball contact lines up
    across swings: swing start -> ball contact (nPre points) and ball contact -> swing end (nPost
    points, the first point repeats ball contact and is dropped). The trail (FP2) and lead (FP3) foot
    COPs are normalized the same way. Frames where the plate(s) carry less than minFz are filled by
    interpolation; swings with no valid global COP are skipped, and a foot that is never loaded in a
    swing is left as NaN.

    Returns
    -------
    traces : list of (6, nPre + nPost - 1) arrays, rows = global X, global Y, trail (FP2) X, trail Y,
             lead (FP3) X, lead Y (cm, lab coordinates)
    """
    Fz2 = np.clip(dat.FP2_GRF_Z.values, 0, None); Fz3 = np.clip(dat.FP3_GRF_Z.values, 0, None)
    FzTot = Fz2 + Fz3
    with np.errstate(invalid = 'ignore', divide = 'ignore'):
        gX = (dat.FP2_COP_X.values * Fz2 + dat.FP3_COP_X.values * Fz3) / FzTot * 100
        gY = (dat.FP2_COP_Y.values * Fz2 + dat.FP3_COP_Y.values * Fz3) / FzTot * 100
    gX[FzTot < minFz] = np.nan; gY[FzTot < minFz] = np.nan
    # each foot's own COP (cm), only while that foot is loaded
    sigs = [gX, gY]
    for fp, Fz in (('FP2', Fz2), ('FP3', Fz3)):
        sigs.append(np.where(Fz >= minFz, dat[fp + '_COP_X'].values * 100, np.nan))
        sigs.append(np.where(Fz >= minFz, dat[fp + '_COP_Y'].values * 100, np.nan))

    traces = []
    for st, bc, en in zip(swgstart, ballCon, swgend):
        if not (0 <= st < bc < en):
            continue
        fr = np.arange(st, en + 1)
        if (~np.isnan(gX[st:en+1])).sum() < 2:
            continue
        tPre = np.linspace(st, bc, nPre); tPost = np.linspace(bc, en, nPost)[1:]
        tNorm = np.concatenate([tPre, tPost])
        rows = []
        for s in sigs:
            seg = s[st:en+1]; ok = ~np.isnan(seg)
            if ok.sum() < 2:
                rows.append(np.full(len(tNorm), np.nan)) # foot not loaded in this swing
                continue
            # fill unloaded frames, then resample start->bc and bc->end
            rows.append(np.interp(tNorm, fr, np.interp(fr, fr[ok], seg[ok])))
        traces.append(np.vstack(rows))
    return traces


def footOutline(cY, cX, footW, footL, medSign, toeDir, nPts = 200):
    """
    Foot-shaped outline (plantar view) centred on (cY, cX) in lab coordinates, footW wide (at the
    ball of the foot) and footL long, with the long axis along lab X.

    Parameters
    ----------
    cY, cX : float
        outline centre (lab Y, lab X)
    footW, footL : float
        width and length (same units as cY, cX)
    medSign : +1 or -1
        lab Y direction of the medial side (big toe and arch)
    toeDir : +1 or -1
        lab X direction the toes point

    Returns
    -------
    y, x : numpy arrays of the closed outline
    """
    from scipy.interpolate import splprep, splev
    # template: w = side-to-side (+ = medial), l = heel (0) to toe (1); traced around the foot
    w = np.array([ 0.00, -0.22, -0.34, -0.38, -0.37, -0.40, -0.46, -0.49, -0.47, -0.40, -0.28,
                  -0.12,  0.06,  0.24,  0.40,  0.48,  0.51,  0.44,  0.28,  0.24,  0.30,  0.33,
                   0.27,  0.14])
    l = np.array([ 0.00,  0.02,  0.08,  0.18,  0.35,  0.52,  0.66,  0.75,  0.83,  0.89,  0.93,
                   0.96,  0.99,  1.00,  0.97,  0.88,  0.76,  0.66,  0.53,  0.42,  0.28,  0.15,
                   0.06,  0.01])
    # smooth closed curve through the template points
    tck, _ = splprep([w, l], s = 0, per = True)
    ws, ls = splev(np.linspace(0, 1, nPts), tck)
    y = cY + ws * footW * medSign
    x = cX + (ls - 0.5) * footL * toeDir
    return y, x


def plotSubjectConfigCOP(subTraces, FilePath, nPre = 101, footW = 10, footL = 29):
    """
    One plot per subject: the average time-normalized global COP trace of each config, across all
    swings of that subject in that config (from normSwingGlobalCOP). Each swing is aligned to its own
    start position (start COP subtracted) before averaging, so the traces show COP displacement from
    swing start and differences in where the subject stood on the plates are removed. Same layout as
    plotGlobalCOP: lab Y horizontal and reversed (toward the lead/left foot on the left, toward the
    trail/right foot on the right), lab X vertical, both in cm. The mean trace runs from swing start
    (circle, at 0,0) to swing end (square). An outline of each foot (footW wide x footL long, cm) is
    drawn on its force plate for scale: the lead/left foot on the left (FP3) and the trail/right foot
    on the right (FP2). Each outline is centred on that foot's average COP over the swing (all swings
    and configs of the subject, shifted by the same start position as the global COP), centred
    front-to-back on the middle of that foot's COP range, with the long axis along lab X.
    Saved to FilePath/AverageCOP/<Subject> AvgGlobalCOP_byConfig.png

    Parameters
    ----------
    subTraces : dict
        subTraces[subject][config] = list of normalized swing traces from normSwingGlobalCOP
    FilePath : str
        file path string; the plots are saved in FilePath/AverageCOP
    nPre : int
        number of points from swing start to ball contact (not marked; kept for reference)
    footW, footL : float
        foot outline width and length (cm)
    """
    cfgColors = {'CFS': 'grey', 'PFS': 'C0', 'ASYM': 'C3'}
    saveFolder = FilePath + 'AverageCOP'
    if os.path.exists(saveFolder) == False:
        os.mkdir(saveFolder)

    for sub in sorted(subTraces):
        fig, ax = plt.subplots(figsize = (10, 4.6), layout = 'constrained') # sized for the fixed -20 to 25 cm y range
        allAligned = [] # aligned swings of every config, used to place the foot outlines
        for ii, cfg in enumerate(sorted(subTraces[sub])):
            tr = np.array(subTraces[sub][cfg]) # swings x 6 x points (global X/Y, trail X/Y, lead X/Y)
            if len(tr) == 0:
                continue
            # align each swing to its global COP start position (start = 0, 0); the same shift is
            # applied to both feet so they stay in the same frame as the global COP
            start = tr[:, 0:2, :1]
            tr = tr - np.concatenate([start, start, start], axis = 1)
            allAligned.append(tr)
            with np.errstate(invalid = 'ignore'):
                avg = np.nanmean(tr, axis = 0)
            col = cfgColors.get(cfg, 'C' + str(ii + 4))
            ax.plot(avg[1], avg[0], color = col, linewidth = 2.5, label = cfg + ' (n = ' + str(len(tr)) + ' swings)', zorder = 2)
            ax.scatter(avg[1][-1], avg[0][-1], color = col, edgecolor = 'k', marker = 's', s = 45, zorder = 3)

        # foot outlines on each force plate (lead/left = FP3 rows 4-5, trail/right = FP2 rows 2-3)
        if allAligned:
            pooled = np.concatenate(allAligned, axis = 0)
            with np.errstate(invalid = 'ignore'):
                pAvg = np.nanmean(pooled, axis = 0)
            centres = {}
            for rx, ry, key in ((4, 5, 'lead'), (2, 3, 'trail')):
                if not np.all(np.isnan(pAvg[rx])):
                    centres[key] = (np.nanmean(pAvg[ry]), # medial/lateral centre on the plate
                                    (np.nanmin(pAvg[rx]) + np.nanmax(pAvg[rx])) / 2) # middle of the COP range front-to-back
            # foot drawing orientation: toes (wide forefoot / ball of the foot) at the top of the plot
            # (+ lab X) and the narrower heel at the bottom
            toeDir = 1.0
            for key, name in (('lead', 'Lead/left foot (FP3)'), ('trail', 'Trail/right foot (FP2)')):
                if key not in centres:
                    continue
                cY, cX = centres[key]
                # medial side faces the other foot
                other = centres.get('trail' if key == 'lead' else 'lead')
                medSign = np.sign(other[0] - cY) if other is not None else (-1.0 if key == 'lead' else 1.0)
                fy, fx = footOutline(cY, cX, footW, footL, medSign, toeDir)
                ax.plot(fy, fx, color = 'k', linewidth = 1.2, linestyle = '--', zorder = 1)
                ax.text(cY, cX + footL/2 + 1.5, name, ha = 'center', va = 'bottom', fontsize = 8) # label above the toes

        # all global traces start at the origin after alignment
        ax.scatter(0, 0, color = 'w', edgecolor = 'k', marker = 'o', s = 60, zorder = 4, label = 'Swing start')
        ax.scatter([], [], color = 'w', edgecolor = 'k', marker = 's', label = 'Swing end')
        ax.plot([], [], color = 'k', linewidth = 1.2, linestyle = '--',
                label = 'Foot outline (' + str(footW) + ' x ' + str(footL) + ' cm)')

        ax.set_ylim(-20, 25) # same vertical (lab X) range for every subject
        ax.set_aspect('equal', adjustable = 'box') # 'box' keeps the fixed y limits (datalim would change them)
        ax.invert_xaxis() # toward the lead/left foot on the left, toward the trail/right foot on the right
        ax.set_xlabel('COP displacement in lab Y (cm): toward lead/left foot <- -> toward trail/right foot')
        ax.set_ylabel('COP displacement in lab X (cm)')
        ax.set_title(sub + '\nAverage global COP by config (aligned to swing start, time-normalized, all swings)')
        fig.legend(loc = 'outside right center', fontsize = 8)
        plt.savefig(saveFolder + '/' + sub + ' AvgGlobalCOP_byConfig.png')
        plt.close(fig)


def plotConfigLegend(FilePath, cfgColors = {'CFS': 'grey', 'PFS': 'C0', 'ASYM': 'C3'}):
    """
    Stand-alone legend (no axes) for the config colours used in the average COP and GRF plots:
    CFS = grey line, PFS = blue line, ASYM = red line. Useful for figures/slides where the per-subject
    plots are shown without their own legends.
    Saved to FilePath/AverageGRF/ConfigLegend.png (transparent background)

    Parameters
    ----------
    FilePath : str
        file path string; the legend is saved in FilePath/AverageGRF
    cfgColors : dict
        config name -> line colour, in legend order
    """
    saveFolder = FilePath + 'AverageGRF'
    if os.path.exists(saveFolder) == False:
        os.mkdir(saveFolder)
    handles = [plt.Line2D([], [], color = col, linewidth = 3, label = cfg) for cfg, col in cfgColors.items()]
    fig = plt.figure(figsize = (4, 0.6))
    fig.legend(handles = handles, loc = 'center', ncol = len(handles), frameon = False, fontsize = 12)
    plt.savefig(saveFolder + '/ConfigLegend.png', dpi = 300, bbox_inches = 'tight', transparent = True)
    plt.close(fig)
    return


def swingGRFPeakAligned(dat, swgstart, swgend, BW, freq, postWin = 0.5):
    """
    Lead (FP3) and trail (FP2) vertical GRF of every complete swing in a file, in real time (no time
    normalization), aligned on the frame of peak lead vertical GRF within the swing (swing start to
    swing end). Each swing runs from swing start to a fixed window of postWin seconds after the peak
    (instead of stopping at swing end, which falls just after the peak), so the unloading after the
    peak is included; the window is cut short only if the trial ends first. Forces are divided by
    body weight.

    Parameters
    ----------
    freq : float
        force plate sampling rate (Hz)
    postWin : float
        time kept after the peak lead vertical GRF (s)

    Returns
    -------
    swings : list of (pkOffset, lead, trail) tuples; lead/trail are the GRF from swing start to
             postWin s after the peak (x BW) and pkOffset is the index of the peak within them
    """
    leadFz = dat.FP3_GRF_Z.values / BW
    trailFz = dat.FP2_GRF_Z.values / BW
    nPost = int(round(postWin * freq))
    swings = []
    for st, en in zip(swgstart, swgend):
        if not (0 <= st < en):
            continue
        pk = st + int(np.argmax(leadFz[st:en+1])) # peak lead vertical GRF within the swing
        stop = min(pk + nPost, len(leadFz) - 1) # fixed window after the peak
        swings.append((pk - st, leadFz[st:stop+1], trailFz[st:stop+1]))
    return swings


def plotSubjectConfigGRF(subGRF, FilePath, freq, minFrac = 0.5):
    """
    One plot per subject: the average vertical GRF curve of each config, across all swings of that
    subject in that config (from swingGRFPeakAligned). Time is not normalized: each swing is kept in
    real time and aligned so its peak lead vertical GRF is at t = 0, from swing start to
    a fixed window after the peak (postWin in swingGRFPeakAligned). Because the time from swing start to
    the peak differs between swings, each swing only covers part of the time axis before the peak; the mean and SD at each time point use the
    swings that cover it, and points covered by fewer than minFrac of the swings are not drawn. Two
    panels: lead/left foot (FP3) on the left and trail/right foot (FP2) on the right. Each config is
    drawn as its mean curve with a shaded band of +/- 1 SD. Forces are in body weights.
    Saved to FilePath/AverageGRF/<Subject> AvgVerticalGRF_byConfig.png

    Parameters
    ----------
    subGRF : dict
        subGRF[subject][config] = list of (pkOffset, lead, trail) from swingGRFPeakAligned
    FilePath : str
        file path string; the plots are saved in FilePath/AverageGRF
    freq : float
        force plate sampling rate (Hz)
    minFrac : float
        minimum fraction of a config's swings that must cover a time point for it to be plotted
    """
    cfgColors = {'CFS': 'grey', 'PFS': 'C0', 'ASYM': 'C3'}
    saveFolder = FilePath + 'AverageGRF'
    if os.path.exists(saveFolder) == False:
        os.mkdir(saveFolder)

    for sub in sorted(subGRF):
        fig, axs = plt.subplots(1, 2, figsize = (12, 4.8), sharey = True, layout = 'constrained')
        cfgs = [c for c in cfgColors if c in subGRF[sub]] + sorted(c for c in subGRF[sub] if c not in cfgColors) # CFS, PFS, ASYM first
        for ii, cfg in enumerate(cfgs):
            swings = subGRF[sub][cfg]
            if len(swings) == 0:
                continue
            # common frame axis relative to the peak: from the earliest start to the latest end
            nBefore = max(pk for pk, ld, tr in swings)
            nAfter = max(len(ld) - pk for pk, ld, tr in swings)
            grid = np.full((len(swings), 2, nBefore + nAfter), np.nan) # NaN where a swing has no data
            for kk, (pk, ld, tr) in enumerate(swings):
                i0 = nBefore - pk
                grid[kk, 0, i0:i0 + len(ld)] = ld
                grid[kk, 1, i0:i0 + len(tr)] = tr
            nCover = np.sum(~np.isnan(grid[:, 0, :]), axis = 0)
            with np.errstate(invalid = 'ignore'):
                avg = np.nanmean(grid, axis = 0); sd = np.nanstd(grid, axis = 0)
            keep = nCover >= minFrac * len(swings)
            avg[:, ~keep] = np.nan; sd[:, ~keep] = np.nan
            tt = (np.arange(nBefore + nAfter) - nBefore) / freq # s, 0 = peak lead vertical GRF
            col = cfgColors.get(cfg, 'C' + str(ii + 4))
            for jj in range(2):
                axs[jj].fill_between(tt, avg[jj] - sd[jj], avg[jj] + sd[jj], color = col, alpha = 0.15, linewidth = 0)
                axs[jj].plot(tt, avg[jj], color = col, linewidth = 2,
                             label = cfg + ' (n = ' + str(len(swings)) + ' swings)' if jj == 0 else '_nolegend_')

        for jj, name in enumerate(('Lead/left foot (FP3)', 'Trail/right foot (FP2)')):
            axs[jj].set_title(name)
            axs[jj].set_xlabel('Time relative to peak lead vertical GRF (s)')
        axs[0].set_ylabel('Vertical GRF (x body weight)')
        fig.suptitle(sub + '\nAverage vertical GRF by config (aligned on peak lead vertical GRF, mean +/- 1 SD, all swings)')
        fig.legend(loc = 'outside right center', fontsize = 8)
        plt.savefig(saveFolder + '/' + sub + ' AvgVerticalGRF_byConfig.png')
        plt.close(fig)




#########################            
save_plts = 1
show_plts = 0
noTrackmanSubs = ['SeanODell'] # Trackman missed many shots: find swings from GRF only
subTraces = {} # subTraces[subject][config] = time-normalized global COP of each swing
subGRF = {} # subGRF[subject][config] = lead/trail vertical GRF of each swing, aligned on peak lead GRF
COPY_ex = []
COPex_L = []
COPex_T = []
config = []
Subject = []

pkhorizFr_lead_BS = []
pkhorizFr_trail_BS = []
pkhorizFr_lead_DS = []
pkhorizFr_trail_DS = []

pkZFr_lead = []
pkZFr_trail = []
pkML_lead = []


for fName in entries:

    dat = pd.read_csv(fPath + fName,sep='\t', skiprows = 8, header = 0)
    dat = dat.fillna(0)

    
    subName = fName.split(sep = "_")[0]
    ConfigTmp = fName.split(sep="_")[1]
    ClubTmp = fName.split(sep="_")[2]
    fileNo = fName.split(sep = '_')[3].split(sep = '-')[0]
    subBW = massdf.loc[massdf['Subject']==subName, 'Mass'].iloc[0] * 9.81 # pull mass from subAnthro 
    
    
    # check to see if phases are stored
    if os.path.exists(fPath+fName+'SwingSeg.npy'):
        swgstart, Transition, apxImpact, swgend = checkPhases(fName)
    
    # find swing events and save if not found
    thresh = subBW * 1.05
    # swgpks = sig.find_peaks(dat.FP3_GRF_Z, thresh, distance = 1200, prominence= 400 )
    # print(len(swgpks[0]))
    # plt.figure() 
    # plt.plot(dat.FP3_GRF_Z)
    # plt.plot(dat.FP2_GRF_Z)
    
    def findCommonPeaks(signals, heights, tol, distance):
        """
        Find peaks that occur in all signals within tol samples of each other.
    
        signals  : list of 1D arrays (same length / sampling rate)
        heights  : list of minimum peak heights, one per signal
        tol      : max sample offset allowed between matching peaks
        distance : optional min samples between peaks (applied to every signal)
    
        Returns indices of common events (taken from the first signal).
        """
        pkList = [sig.find_peaks(s, height=h, distance=distance)[0]
                  for s, h in zip(signals, heights)]
    
        common = []
        for pk in pkList[0]:
            # keep the peak only if every other signal has a peak within tol samples
            if all(np.any(np.abs(otherPks - pk) <= tol) for otherPks in pkList[1:]):
                common.append(pk)
        return np.array(common), pkList
    
    
    # signals = [dat.FP3_GRF_Z, -1*dat.FP3_GRF_Y, -1*dat.FP3_GRF_X]
    # heights = [subBW*1.05, 0.15*subBW, 0.1*subBW]   # one threshold per signal, in that signal's units
    # swgpks, allPks = findCommonPeaks(signals, heights, tol=25, distance=50)

    # localize swings with Trackman shot times, then find the lead vertical GRF peak from -100 to +200 frames
    # (+200 keeps the first peak of Benjamin's bimodal lead GRF curve)
    startTime, freq = getStartTime(fName)
    swgpks, shotFr, shots = findShotPeaks(dat.FP3_GRF_Z.values, startTime, freq, trackman[subName], winBefore = 100, winAfter = 200)

    # subjects with missing Trackman shots: detect swings from the force plates instead
    # (shotFr still marks the Trackman shots that did record; shots no longer lines up with swgpks)
    if subName in noTrackmanSubs:
        swgpks = findSwingPeaksGRF(dat.FP3_GRF_Z.values, dat.FP2_GRF_Z.values, subBW, freq)

    swgstart, apxImpact, swgend = findSwingEvents(dat.FP3_GRF_Z.values, dat.FP2_GRF_Z.values, swgpks, subBW, freq, leadGRF_x = dat.FP3_GRF_X.values)
        
    
    
    
    
    
    
    
    
    
    # Original global COP (kept for reference, overwritten by the corrected line below):
    dat['COP'] =((dat.FP2_COP_Y * dat.FP2_GRF_Z)+ (dat.FP3_GRF_Z * (dat.FP3_COP_Y + 60))) / (dat.FP3_GRF_Z +dat.FP2_GRF_Z) # from Ball & Best pt 1 ; 60 cm from center of FP2 to center of FP3
    # Corrected global COP: the original line assumes each plate's COP is in its own local frame (cm)
    # and adds a 60 cm offset to FP3. In this export the plate COPs are already in the global lab frame
    # and in METERS (trail FP2_COP_Y ~0.36 m, lead FP3_COP_Y ~0.84 m, so the feet are ~48 cm apart,
    # not 60). Adding 60 to a value in meters adds 60 m, so the original COP mostly tracks the fraction
    # of weight on the lead foot x 60 rather than the COP position, which also distorts COPY_excursion.
    # No offset is needed: weight the two global COPs by vertical force and convert m -> cm.
    dat['COP'] = (dat.FP2_COP_Y * dat.FP2_GRF_Z + dat.FP3_COP_Y * dat.FP3_GRF_Z) / (dat.FP3_GRF_Z + dat.FP2_GRF_Z) * 100 # cm, plates already in lab coords
    leadCOP = dat.FP3_COP_Y
    trailCOP = dat.FP2_COP_Y
    
    plt.figure()
    plt.plot(dat['FP3_GRF_Z'], color ='C0', label = 'Lead Vertical')
    plt.plot(dat['FP2_GRF_Z'], color ='C1', label = 'Trail Vertical')
    plt.plot(dat['FP3_GRF_Y'], color ='C0', linestyle= '-.', label = 'Lead ML')
    plt.plot(dat['FP2_GRF_Y'], color ='C1', linestyle= '-.', label = 'Trail ML')
    plt.plot(dat['FP3_GRF_X'], color ='C0', linestyle= ':', label = 'Lead AP')
    plt.plot(dat['FP2_GRF_X'], color ='C1', linestyle= ':', label = 'Trail AP')
    plt.scatter(swgpks, dat.FP3_GRF_Z[swgpks], color = 'k', zorder = 3, label = 'Swing peak')
    # label only the first line of each event so it shows once in the legend
    labeled = set()
    def evtLabel(name):
        if name in labeled:
            return '_nolegend_'
        labeled.add(name)
        return name

    for fr in shotFr:
        plt.axvline(fr, color = 'grey', linestyle = '--', label = evtLabel('Trackman shot'))
    for st, bc, en in zip(swgstart, apxImpact, swgend):
        if st >= 0:
            plt.axvline(st, color = 'g', label = evtLabel('Swing start'))
        if bc >= 0:
            plt.axvline(bc, color = 'k', linestyle = ':', label = evtLabel('Ball contact'))
        if en >= 0:
            plt.axvline(en, color = 'r', label = evtLabel('Swing end'))
    plt.title(subName + ' ' + ConfigTmp + ' (trial ' + fileNo.strip() + ')\n'
              + 'Trackman shots: ' + str(len(shotFr)) + ' | Swing peaks: ' + str(len(swgpks)))
    plt.legend()

    # global COP of one representative swing (saved to Overground/GlobalCOP)
    copFig = plotGlobalCOP(dat, swgstart, apxImpact, swgend, swgpks, fPath,
                           subName + ' ' + ConfigTmp + ' ' + ClubTmp + ' ' + fileNo.strip())
    if copFig is not None:
        plt.close(copFig)

    # store the time-normalized global COP of every swing for the per-subject config averages
    subTraces.setdefault(subName, {}).setdefault(ConfigTmp, []).extend(
        normSwingGlobalCOP(dat, swgstart, apxImpact, swgend))
    # and the vertical GRF of every swing in real time, aligned on peak lead vertical GRF (x body weight)
    subGRF.setdefault(subName, {}).setdefault(ConfigTmp, []).extend(
        swingGRFPeakAligned(dat, swgstart, swgend, subBW, freq, postWin = 0.5)) # 0.5 s kept after the peak


    ## extract COP excursion
    
    for ii in range(len(swgstart)):
        COPY_ex.append(np.max(dat.COP[swgstart[ii]:swgend[ii]]) - np.min(dat.COP[swgstart[ii]:swgend[ii]]))
        COPex_L.append(np.max(leadCOP[swgstart[ii]:swgend[ii]]) - np.min(leadCOP[swgstart[ii]:swgend[ii]]))
        COPex_T.append(np.max(trailCOP[swgstart[ii]:swgend[ii]]) - np.min(trailCOP[swgstart[ii]:swgend[ii]]))
        Subject.append(subName)
        config.append(ConfigTmp)
        pkZFr_lead.append(np.max(dat.FP3_GRF_Z[swgstart[ii]:swgend[ii]]))
        pkZFr_trail.append(np.max(dat.FP2_GRF_Z[swgstart[ii]:swgend[ii]]))
        pkML_lead.append(np.max(dat.FP3_GRF_Y[swgstart[ii]:swgend[ii]]))
#     


# average global COP trace of each config, one plot per subject (saved to Overground/AverageCOP)
plotSubjectConfigCOP(subTraces, fPath)
# average vertical GRF curve of each config aligned on peak lead GRF, one plot per subject (saved to Overground/AverageGRF)
plotSubjectConfigGRF(subGRF, fPath, freq)
# stand-alone config legend (CFS grey, PFS blue, ASYM red), saved to Overground/AverageGRF
plotConfigLegend(fPath)

Outcomes = pd.DataFrame({'Subject':list(Subject), 'Config':list(config), 
                          'PeakLeadGRF':list(pkZFr_lead), 'PeakTrailGRF':list(pkZFr_trail) , 'PeakLeadML':list( pkML_lead) ,
                         'COPY_excursion':list(COPY_ex), 'COPY_lead_excursion':list(COPex_L), 'COPY_trail_excursion':list(COPex_T)})    

save_on = 1
if save_on == 1:
    outfileName = fPath + '0_CompiledOG_COP.csv'
    Outcomes.to_csv(outfileName, index = False)