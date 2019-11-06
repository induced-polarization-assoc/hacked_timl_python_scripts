# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:57 2018

@author: TimL
"""
import os
import scipy as sp
import commonSense as cs
from textwrap import wrap
import pickle
import matplotlib.pyplot as plt


class fileClass:
    pass


def ipPlot():
    ps = cs.emptyClass
    # Whether to save the plot images.
    doSave = False

    folderPath = r'C:\temp\180821_artificial'
    fileStart = cs.lastName(folderPath)

    # Processed result choice.
    ps.loadThis = 'zOddH'
    # Plotting choice.
    ps.plotThis = 'zPhase'

    # Channel plotted.
    ps.ch = 1

    # Number of means to include in each plot. Three indicates target means
    # plotted with one baseline sandwiched on either side.
    # One indicates files plotted individually.
    meanCount = 1
    # Whether to omit 60 Hz data from the plots.
    ps.omit60Hz = False
    # Whether to plot only the first three odd harmonic frequencies.
    ps.h135 = False

    ps.plotGuidePosts = False
    ps.plotCustomPosts = False
    # Colors for plotting targets and sandwich baselines.
    if ps.plotThis == 'zPhase':
        ps.meanCol = ['Blue', 'Green', 'Red']
        ps.stdCol = ['DodgerBlue', 'LimeGreen', 'Fuchsia']
    elif ps.plotThis == 'zMag':
        ps.meanCol = ['Black', 'Blue', 'Green']
        ps.stdCol = ['Gray', 'DodgerBlue', 'LimeGreen']
    elif ps.plotThis == '2MagPhys':
        ps.meanCol = ['Black', 'Blue', 'DarkGoldenRod']
        ps.stdCol = ['Gray', 'DodgerBlue', 'Gold']

    params = {'legend.fontsize': 'x-large',
              'figure.figsize': (9, 6.5),
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'x-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    # Loading the data:
    fileName = fileStart + '_' + ps.loadThis + '.pkl'
    filePath = os.path.join(folderPath, fileName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    tarList = []
    for t in range(len(a)):
        # Identify target files (They aren't baselines).
        if a[t].descript != 'baseline' and a[t].descript != 'test':
            tarList.append(t)

    if meanCount == 3 or meanCount == sp.inf:
        tList = [0]  # Target files.
    elif meanCount == 1:
        tList = [0]  # range(len(a))  # All files.
    for t in tList:
        if meanCount == 3:
            ps.tar = t  # Index of the target file.
            plot3Mean(a, ps)
        elif meanCount == sp.inf:
            ps.tar = t  # Index of the target file.
            plot3All(a, ps)
        elif meanCount == 1:
            plot1Mean(a[t], ps)
        imgFile = ('%s_ch%d_%d_%s'
                   % (a[t].fileDateStr, ps.ch, a[t].fileNum,
                      ps.plotThis))
        imgFolder = ps.plotThis + str(meanCount)
        if ps.h135:
            imgFile += 'H135'
            imgFolder += 'H135'
        if doSave:
            imgPath = os.path.join(folderPath, 'plots', imgFolder,
                                   imgFile + '.png')
            plt.savefig(imgPath)
#        if t != tList[-1]:
#            # Clear the figure before plotting again, unless this is the
#            # last plot to be generated.
#            plt.clf()
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()


def plot3All(a, ps):
    '''
    Plots all file data for a target and baselines falling before and after.

    Parameters
    ----------
    a  : list of fileClass objects loaded from the .pkl file.
      0-indexed list of all file data read and processed.
    ps : class containing plotting choices
      See construction in ipPlot()
    '''
    tArr = ps.tar + sp.array([-1, 1, 0], dtype=int)
    for idx in range(3):
        t = tArr[idx]
        # Marker size.
        mrkSize = 3
        # Legend text.
        legStr = ('%d %s (%d packets)'
                  % (a[t].fileNum, a[t].descript, a[t].pktCount))
        freq = a[t].freq
        mask = sp.ones_like(freq, dtype=bool)
        # Mask out 60 Hz, if requested.
        if ps.omit60Hz:
            mask[freq == 60] = False
        if ps.h135:
            mask[3:] = False
            mrkSize = 6
        freq = freq[mask]
        # Rotate through each packet in the file and plot.
        for pkt in range(a[t].pktCount):
            if ps.plotThis == 'zPhase':
                yVal = a[t].phaseDiff[ps.ch, pkt, :]  # (mrad)
            elif ps.plotThis == 'zMag':
                yVal = a[t].zMag[ps.ch, pkt, :]  # (mOhm)
            yVal = yVal[mask]
            # Plot the results.
            if pkt == 1:
                legStr = '_nolegend_'
            plt.plot(freq, yVal, color=ps.meanCol[idx], markersize=mrkSize,
                     marker='o', label=legStr)

    at = a[ps.tar]
    titleStr = ('%s Ch %d (%s). xmitFund = %.1f Hz. %s %s'
                % (at.fileDateStr, ps.ch, at.measStr[ps.ch], at.xmitFund,
                   at.major, a[t].minor))
    if ps.omit60Hz:
        titleStr += ' 60 Hz omitted.'
    # Wrap text at a set character length.
    titleStr = '\n'.join(wrap(titleStr, 75))
    plt.title(titleStr)
    plt.xlabel('Frequency (Hz)')
    if ps.plotThis == 'zPhase':
        plt.ylabel('Impedance Phase (mrad)')
    elif ps.plotThis == 'zMag':
        plt.ylabel('Impedance Amplitude (m$\Omega$)')


def plot3Mean(a, ps):
    '''
    Plots mean file data for a target and baselines falling before and after.

    Parameters
    ----------
    a  : list of fileClass objects loaded from the .pkl file.
      0-indexed list of all file data read and processed.
    ps : class containing plotting choices
      See construction in ipPlot()
    '''
    tArr = ps.tar + sp.array([-1, 0, 1], dtype=int)
    for idx in range(3):
        t = tArr[idx]
        # Marker size.
        mrkSize = 3
        # Legend text.
        legStr = ('%d %s (Avg. of %d packets)'
                  % (a[t].fileNum, a[t].descript, a[t].pktCount))
#        if t == ps.tar:
#            # Target position during the test.
#            legStr += '. %s' % a[t].minor
        # Compute means and standard deviations over the packets.
        pktAxis = 1
        freq = a[t].freq
        if ps.plotThis == 'zPhase':
            mean = sp.mean(a[t].phaseDiff, axis=pktAxis)  # (mrad)
            std = sp.std(a[t].phaseDiff, axis=pktAxis)  # (mrad)
        elif ps.plotThis == 'zMag':
            mean = sp.mean(a[t].zMag, axis=pktAxis)  # (mOhm)
            std = sp.std(a[t].zMag, axis=pktAxis)  # (mOhm)
        # Pick out data on the requested channel.
        mean = mean[ps.ch, :]
        std = std[ps.ch, :]
        mask = sp.ones_like(freq, dtype=bool)
        # Mask out 60 Hz, if requested.
        if ps.omit60Hz:
            mask[freq == 60] = False
        # Only include three frequencies, if requested.
        if ps.h135:
            mask[3:] = False
            mrkSize = 6
        freq = freq[mask]
        mean = mean[mask]
        std = std[mask]

        # Plot a shaded envelope symbolizing the mean +/- 1 std. dev.
        plt.fill_between(freq, mean - std, mean + std,
                         facecolor=ps.stdCol[idx], alpha=0.5)
        # Plot the mean results.
        plt.plot(freq, mean, color=ps.meanCol[idx], markersize=mrkSize,
                 marker='o', label=legStr)

    at = a[ps.tar]
    titleStr = ('%s Ch %d (%s). xmitFund = %.1f Hz. %s %s '
                'Shaded patches are means +/- 1 STD.'
                % (at.fileDateStr, ps.ch, at.measStr[ps.ch], at.xmitFund,
                   at.major, a[t].minor))
    if ps.omit60Hz:
        titleStr += ' 60 Hz omitted.'
    # Wrap text at a set character length.
    titleStr = '\n'.join(wrap(titleStr, 75))
    plt.title(titleStr)
    plt.xlabel('Frequency (Hz)')
    if ps.plotThis == 'zPhase':
        plt.ylabel('Impedance Phase (mrad)')
    elif ps.plotThis == 'zMag':
        plt.ylabel('Impedance Amplitude (m$\Omega$)')


def plot1Mean(at, ps):
    '''
    Plots mean file data.

    Parameters
    ----------
    at  : fileClass object.
    ps : class containing plotting choices
      See construction in ipPlot()
    '''
    # Marker size.
    mrkSize = 3
    # Colors.
    meanCol = ps.meanCol[2]
    stdCol = ps.stdCol[2]
    if ps.loadThis == 'zCustom':
        if at.fileNum == 4:
            meanCol = 'Green'
            stdCol = 'LimeGreen'
        elif at.fileNum == 5:
            meanCol = 'Red'
            stdCol = 'Fuchsia'
    # Legend text.
    legStr = ('%d %s (Avg. of %d packets)'
              % (at.fileNum, at.descript, at.pktCount))
    # Compute means and standard deviations over the packets.
    pktAxis = 1
    freq = at.freq
    if ps.loadThis == 'zCustom':
        # Convert to estimates of the inductance in the circuit.
        r2 = 8.6  # Ohm
        if at.fileNum == 4:
            r3 = 1  # Ohm
        elif at.fileNum == 5:
            r3 = 2  # Ohm
        # Matrix of inductance values.
        lMat = sp.zeros_like(at.phaseDiff)
        for p in range(at.pktCount):
            for freqIdx in range(len(at.freq)):
                omega = 2*sp.pi*at.freq[freqIdx]  # (rad/s)
                # Solving the quadratic for L.
                tangent = sp.tan(at.phaseDiff[ps.ch, p, freqIdx]/1000)
                a = omega**2*tangent
                b = -omega*r2
                c = r3*(r3 + r2)*tangent
                # (H)
                lMat[ps.ch, p, freqIdx] = (-b - sp.sqrt(b**2 - 4*a*c))/(2*a)
        # Convert to microHenry.
        lMat *= 1e6  # (uH)
        # Take the mean and standard deviation over packets.
        mean = sp.mean(lMat, axis=pktAxis)  # (uH)
        std = sp.std(lMat, axis=pktAxis)  # (uH)
    elif ps.plotThis == 'zPhase':
        mean = sp.mean(at.phaseDiff, axis=pktAxis)  # (mrad)
        std = sp.std(at.phaseDiff, axis=pktAxis)  # (mrad)
    elif ps.plotThis == 'zMag':
        mean = sp.mean(at.zMag, axis=pktAxis)  # (mOhm)
        std = sp.std(at.zMag, axis=pktAxis)  # (mOhm)
    elif ps.plotThis == '2MagPhys':
        mean = sp.mean(2*at.magPhys, axis=pktAxis)  # (A or V)
        std = sp.std(2*at.magPhys, axis=pktAxis)
    # Pick out data on the requested channel.
    mean = mean[ps.ch, :]
    std = std[ps.ch, :]
    mask = sp.ones_like(freq, dtype=bool)
    # Mask out 60 Hz, if requested.
    if ps.omit60Hz:
        mask[freq == 60] = False
    # Only include three frequencies, if requested.
    if (ps.loadThis == 'zOddH') and ps.h135:
        mask[3:] = False
        mrkSize = 6
    freq = freq[mask]
    mean = mean[mask]
    std = std[mask]

    if ps.loadThis == 'zAnyF' and ps.plotGuidePosts:
        # Guide post values to plot where maximum values in complex magnitude
        # are expected as a function of frequency, based on a square wave
        # spectrum.
        gPostX = [0]
        gPostY = [0]
        hCount = 17
        freqIdx = 4-1
        for postIdx in range(hCount):
            for ii in range(3):
                gPostX.append(at.freq[freqIdx])
            # Vertical spike to the maximum of the plotted mean list.
            gPostY.append(0)
            gPostY.append(sp.amax(mean))
            gPostY.append(0)
            # Move to the next odd harmonic.
            freqIdx += 8

        # Plot the guide posts.
        plt.plot(gPostX, gPostY, color='DodgerBlue',
                 marker='None', label='Odd Harmonic Frequencies')
    elif ps.loadThis == 'zAnyF' and ps.plotCustomPosts:
        # Guide posts at custom frequencies.
        customIdx = -1 + sp.array([4, 12, 19, 27, 35, 43, 51, 58, 66, 74, 82,
                                   89, 97, 105, 113, 120, 128, 136])
        gPostX = [0]
        gPostY = [0]
        for cI in customIdx:
            for ii in range(3):
                gPostX.append(at.freq[cI])
            # Vertical spike to the maximum of the plotted mean list.
            gPostY.append(0)
            gPostY.append(sp.amax(mean))
            gPostY.append(0)

        # Plot the custom posts.
        plt.plot(gPostX, gPostY, color='DodgerBlue',
                 marker='None', label='Custom Frequencies Selected')

    # Plot a shaded envelope symbolizing the mean +/- 1 std. dev.
    plt.fill_between(freq, mean - std, mean + std,
                     facecolor=stdCol, alpha=0.5)
    # Plot the mean results.
    plt.plot(freq, mean, color=meanCol, markersize=mrkSize,
             marker='o', label=legStr)

    titleStr = ('%s Ch %d (%s). xmitFund = %.1f Hz. %s %s '
                'Shaded patches are means +/- 1 STD.'
                % (at.fileDateStr, ps.ch, at.measStr[ps.ch], at.xmitFund,
                   at.major, at.minor))
    titleStr = titleStr
    if ps.omit60Hz:
        titleStr += ' 60 Hz omitted.'
    # Wrap text at a set character length.
    titleStr = '\n'.join(wrap(titleStr, 75))
    plt.title(titleStr)
    plt.xlabel('Frequency (Hz)')
    if ps.loadThis == 'zCustom':
        plt.ylabel('Inductance L ($\mu$H)')
    elif ps.plotThis == 'zPhase':
        plt.ylabel('Impedance Phase (mrad)')
    elif ps.plotThis == 'zMag':
        plt.ylabel('Impedance Amplitude (m$\Omega$)')
    elif ps.plotThis == '2MagPhys':
        if at.measStr[ps.ch] == 'currentMeas':
            plt.ylabel('Twice Complex Mag. (A)')
        else:
            plt.ylabel('Twice Complex Mag. (V)')


# Invoke the main function here.
if __name__ == "__main__":
    ipPlot()
