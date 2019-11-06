# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:57 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import scipy as sp
import commonSense as cs
import plotWrap as pw
import pickle
import matplotlib.pyplot as plt


class fileClass:
    pass


def ipPlot(inFolder, inFileNums, inPlotThis):
    # Whether to save the plot images.
    doSave = False

    pklFolder = inFolder
    fileStart = cs.lastName(pklFolder)

    # Processed file choice.
    loadThis = 'zAnyF'
    # Plotting choice (y-axis).
    plotThis = inPlotThis
    # Plotting choice (x-axis).
    # 'freq': frequency (Hz).
    # 'phase': absolute phase (rad).
    xChoice = 'freq'

    # Frequency index to plot, if not plotting vs frequency.
    hChoice = 1
    freqIdx1 = 4*hChoice

    # Channels plotted.
    chList = [6]

    # Whether to include the listed channels together in the same plots.
    chTogether = False

    # Whether to identify and plot target files.
    targetBool = True

    # Whether to manually select which file numbers to plot.
    manualTargetBool = True
    manualTargetArra = inFileNums

    # Number of files included in each plot.
    # 1: just one file.
    # 3: 3 files are included, one primary, and each of the two adjacent files.
    fileCount = 1

    # Whether to subtract an average of results from the adjacent two files.
    subtractAdj = False

    # Whether to subtract one file's results from the target.
    subtract1 = False

    # Whether to plot all the files together without erasing at all.
    fileTogether = True

    # Whether to average over packets.
    meanBool = True

    if meanBool:
        # Whether to plot standard deviation envelopes.
        stdBool = True
    else:
        stdBool = False
        # Whether to plot all packets individually on the same plots.
        allPktBool = True
        if not allPktBool:
            # Which packet index to plot alone.
            pIso = 0

    # Whether to omit 60 Hz data from the plots.
    omit60Hz = True

    # Frequencies plotted.
    maskChoice = 'oddHUp2'

    isYAxStartedFromZero = False


    # Whether to include the minor note anywhere at all.
    minorBool = False

    # Whether to include the minor note in the legend entries rather than the
    # title.
    minorLegBool = False

    # Whether to swap the description and minor note text for display purposes.
    swapDescriptMinor = False

    legOutside = False
    loc = 'best'

    if plotThis == 'zMag':
        # Whether to normalize the impedance magnitudes by the fundamental.
        normMag = False
    else:
        normMag = False

    # File number from which the plot title is taken. inf if it doesn't matter.
    titleFileNum = sp.inf

    # Colors for plotting main results.
    if plotThis == 'zPhase':
        color = 'Red'
        stdColor = 'Fuchsia'
    elif plotThis == 'zMag':
        color = 'Green'
        stdColor = 'LimeGreen'
    elif plotThis == '2MagPhys':
        color = 'DarkGoldenRod'
        stdColor = 'Gold'
    elif plotThis == 'inductance':
        color = None
        stdColor = None

    # Let colors be selected automatically if files are plotted together.
    if fileTogether:
        color = None
        stdColor = None

    if fileCount == 3:
        # Colors for plotting main results.
        color3 = ['Black', 'Blue', color]
        stdColor3 = ['Gray', 'DodgerBlue', stdColor]

    # Colors for plotting results on different channels.
    chColor = ['Black', 'SteelBlue', 'LimeGreen', 'Crimson', 'Green',
               'DeepPink', 'BlueViolet', 'Orange']
    chStdColor = ['Gray', 'SkyBlue', 'YellowGreen', 'Brown', 'ForestGreen',
                  'HotPink', 'DarkMagenta', 'Coral']

    # Loading the data:
    fileName = fileStart + '_' + loadThis + '.pkl'
    filePath = os.path.join(pklFolder, fileName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    # Pick out the desired result data to be plotted as x and y values.
    res = []
    for t in range(len(a)):
        res.append(cs.emptyClass())
        if xChoice == 'freq':
            # Frequencies along the x-axis.
            res[t].xVal = a[t].freq
        elif xChoice == 'phase':
            res[t].xVal = abs(abs(a[t].phase) - sp.pi/2)

        if plotThis == 'zPhase':
            res[t].yVal = a[t].phaseDiff
        elif plotThis == 'zMag':
            res[t].yVal = a[t].zMag
        elif plotThis == '2MagPhys':
            res[t].yVal = 2*a[t].magPhys
        elif plotThis == 'zTime':
            res[t].yVal = sp.zeros_like(a[t].phaseDiff)
            # Convert phase differences to time differences.
            for idx in range(len(a[t].freq)):
                freq = a[t].freq[idx]
                if freq != 0:
                    # (microsecond)
                    res[t].yVal[:, :, idx] = (10**3 * a[t].phaseDiff[:, :, idx]
                        / (2 * sp.pi * freq))
        elif plotThis == 'inductance':
            # Convert to estimates of the inductance in the circuit.
            r2 = 8.1  # Ohm
            r3 = sp.inf  # initialization
            if sp.any(a[t].fileNum == sp.array([2, 5, 9, 10])):
                r3 = 1.0  # Ohm
            elif sp.any(a[t].fileNum == sp.array([3, 6, 11, 12])):
                r3 = 2.0  # Ohm
            # Matrix of inductance values.
            lMat = sp.zeros_like(a[t].phaseDiff)
            for p in range(a[t].pktCount):
                for freqIdx in range(len(a[t].freq)):
                    omega = 2*sp.pi*a[t].freq[freqIdx]  # (rad/s)
                    # Solving the quadratic for L.
                    # (rad)
                    phaseDiff = a[t].phaseDiff[chList[0], p, freqIdx]/1000
                    tangent = sp.tan(phaseDiff)
                    aQ = omega**2*tangent
                    b = -omega*r2
                    c = r3*(r3 + r2)*tangent
                    # (H)
                    lMat[chList[0], p, freqIdx] = (-b - sp.sqrt(b**2 - 4*aQ*c)
                                                   )/(2*aQ)
            # Convert to microHenry.
            lMat *= 1e6  # (uH)
            res[t].yVal = lMat
        if xChoice == 'freq':
            # Mask out unwanted frequencies.
            mask = sp.zeros_like(a[t].freq, dtype=bool)
            if maskChoice == 'oddH':
                # Save odd harmonics of the transmit fundamental.
                mask[4:len(mask):8] = True
            elif maskChoice == 'fund':
                mask[4] = True
            elif maskChoice == 'blockSine':
                mask[4:len(mask):8] = True
                mask[12:len(mask):24] = False
            elif maskChoice == 'oddHUp2':
                mask[4:len(mask):8] = True
                # Number of frequencies included in the plot.
                freqCount = 17
                mask[(1+4+8*(freqCount-1)):] = False
            elif maskChoice == 'oddUp2':
                mask[1:len(mask):2] = True
                mask[10:] = False
            elif maskChoice == 'nonzero':
                mask[1:150] = True
            elif maskChoice == 'custom':
                mask[sp.array([4, 12, 20, 27, 35, 43, 51, 59, 66, 74, 82, 90, 98, 106,
                     113, 121, 129, 137, 145])] = True
            # Mask out 60 Hz, if requested.
            if omit60Hz:
                mask[a[t].freq == 60] = False
            res[t].xVal = res[t].xVal[mask]
            res[t].yVal = res[t].yVal[..., mask]

    if targetBool:
        tarList = []
        for t in range(len(a)):
            if manualTargetBool:
                if any(a[t].fileNum == manualTargetArra):
                    tarList.append(t)
            else:
                # Identify target files (They aren't baselines or tests).
                if a[t].descript != 'baseline' and a[t].descript != 'test':
                    if t < (len(a) - 1):
                        tarList.append(t)

    # List of file numbers.
    fileNumList = []
    for t in range(len(a)):
        fileNumList.append(a[t].fileNum)
        if swapDescriptMinor:
            descript = a[t].descript
            a[t].descript = a[t].minor
            a[t].minor = descript

    # Initialize plot settings.
    ps = cs.emptyClass()
    # Figure with axes.
    ps.color = color
    ps.stdColor = stdColor
    ps.stdBool = stdBool
    ps.markerSize = 3
    ps.marker = 'o'
    if xChoice == 'freq':
        ps.linestyle = 'solid'
    else:
        ps.linestyle = 'none'
        ps.markerSize = 4
    ps.titleWrap = 75
    ps.legOutside = legOutside
    ps.omit60Hz = omit60Hz
    ps.isYAxStartedFromZero = isYAxStartedFromZero
    ps.normMag = normMag
    ps.loc = loc
    if xChoice == 'freq':
        ps.xLabel = 'Frequency (Hz)'
    elif xChoice == 'phase':
        ps.xLabel = 'abs(abs(Phase) - pi/2) (rad)'

    if plotThis == 'zPhase':
        ps.yLabel = 'Impedance Phase (mrad)'
        if subtractAdj or subtract1:
            ps.yLabel = 'Phase Displacement from Baseline (mrad)'
    elif plotThis == 'zMag':
        if not normMag:
            ps.yLabel = 'Impedance Magnitude (m$\Omega$)'
        else:
            ps.yLabel = 'Impedance Magnitude (Normalized)'
    elif plotThis == '2MagPhys':
        if chList[0] == 0:
            ps.yLabel = 'Twice Complex Mag. (A)'
        else:
            ps.yLabel = 'Twice Complex Mag. (V)'
    elif plotThis == 'zTime':
        ps.yLabel = 'Voltage Lead Time ($\mu$s)'
    elif plotThis == 'inductance':
        ps.yLabel = 'Inductance L ($\mu$H)'

    # List of file indices plotted.
    if targetBool:
        tList = tarList
    else:
        tList = range(0, len(a))

    # List adjacent files with each target file, if there are three per plot.
    if fileCount == 3:
        newTList = []
        tarList = []
        for t in tList:
            newTList.extend(t + sp.array([-1, 1, 0]))
            tarList.extend(3*[t])
        tList = newTList
        del newTList
    else:
        tarList = tList

    # Plot, and save if needed.
    for idx in range(len(tList)):
        imgFolder = plotThis + str(fileCount)
        t = tList[idx]
        tar = tarList[idx]
        if False:
            if a[t].fileNum <= 10 + 2:
                ps.color = 'C0'
            elif a[t].fileNum <= 22 + 2:
                ps.color = 'C1'
            elif a[t].fileNum <= 34 + 2:
                ps.color = 'C2'

        for ch in chList:
            ps.ch = ch
            if chTogether:
                ps.color = chColor[ch]
                ps.stdColor = chStdColor[ch]
            ps.xVal = res[t].xVal
            if fileCount == 3:
                colorIdx = cs.find((t - tar) == [-1, 1, 0], True)
                ps.color = color3[colorIdx]
                ps.stdColor = stdColor3[colorIdx]
#            ps.titleStr = ('%s Ch %d (%s). xmitFund = %.2f Hz. %s'
#                           % (a[t].fileDateStr, ch, a[t].measStr[ch],
#                              a[t].xmitFund, a[t].major))
            ps.titleStr = ('%s Ch %d (%s). %s'
                           % (a[t].fileDateStr, ch, a[t].measStr[ch],
                              a[t].major))
            if xChoice == 'phase':
                ps.titleStr = ('Plotted freq. = %d Hz. '
                               % (a[t].freq[freqIdx1]) + ps.titleStr)
            # Linestyle choice.
            if a[t].minor == 'Sand.':
                ps.linestyle = '--'
            else:
                ps.linestyle = 'solid'
            # Legend text.
            if a[t].xmitFund == 1 and sp.mod(a[t].fileNum, 12) != 0:
                # With legend.
                ps.legStr = '%s' % (a[t].descript[:-6])
            else:
                # Without legend.
                ps.legStr = '_nolegend_'
#            ps.legStr = ('%d. %s' % (a[t].fileNum, a[t].descript))
            if chTogether:
                ps.titleStr = ('%s_%d %s. xmitFund = %.1f Hz. %s'
                               % (a[t].fileDateStr, a[t].fileNum,
                                  a[t].descript, a[t].xmitFund,
                                  a[t].major))
                ps.legStr = 'Ch %d (%s)' % (ch, a[t].measStr[ch])
            if minorBool and (ps.legStr != '_nolegend_'):
                if not minorLegBool:
                    ps.titleStr = '%s ' % (a[t].minor) + ps.titleStr
                else:
                    ps.legStr = '%s ' % (a[t].minor) + ps.legStr
#            if not sp.any(a[t].fileNum ==
#                          (32 + sp.array([1, 3, 5, 7, 9, 11, 13, 15]))):
#                ps.legStr = '_nolegend_'
            # The plot title is taken from the target file.
            ps.titleBool = False
            if t == tar:
                if (titleFileNum == sp.inf) or (titleFileNum == a[t].fileNum):
                    ps.titleBool = True
            imgFile = ('%s_ch%d_%d_%s'
                       % (a[t].fileDateStr, ch, a[t].fileNum, plotThis))
            if meanBool:
                # Result Y data.
                ps.yVal = res[t].yVal[ch, ...]
#                ps.legStr += ' (Avg. of %d packets)' % (a[t].pktCount)
                if stdBool:
                    ps.titleStr += ' Shaded patches are means +/- 1 STD.'
                if not subtractAdj and not subtract1:
                    pw.plot1Mean(ps)
                elif subtract1:
                    ps.yValA = res[t-3].yVal[ch, ...]
                    pw.plot1MeanSubtract1(ps)
                elif subtractAdj:
                    ps.yValA = res[t-1].yVal[ch, ...]
                    ps.yValB = res[t+1].yVal[ch, ...]
                    pw.plot1MeanSubtractAdj(ps)
            else:
                if allPktBool:
                    pList = sp.array(range(a[t].pktCount))
                else:
                    pList = sp.array([pIso])
                if xChoice != 'freq':
                    pList = sp.array([0])
                for idx in range(len(pList)):
                    p = pList[idx]
                    if idx != 0:
                        # Only the first packet in the list appears in the
                        # legend.
                        ps.legStr = '_nolegend_'
                    else:
                        if allPktBool:
                            ps.legStr += '\n (%d packets)' % (a[t].pktCount)
                        else:
                            ps.legStr += ' (pkt %d)' % (a[t].pkt[p])
                    if xChoice != 'freq':
                        # When x is not frequency.
                        ps.xVal = res[t].xVal[ch, :, freqIdx1]
                        ps.yVal = res[t].yVal[ch, :, freqIdx1]
                    else:
                        ps.yVal = res[t].yVal[ch, p, :]
                    pw.basePlot(ps)

            if (t == tar):
                if (not chTogether) or (chTogether and ch == chList[-1]):
                    if ((not fileTogether) or
                            (fileTogether and idx == len(tList) - 1)):
                        if doSave:
                            cs.saveImg(pklFolder, imgFolder, imgFile)
                        if not ((t == tList[-1]) and (ch == chList[-1])):
                            plt.clf()

    ax = plt.gca()
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
#    plt.xscale('log')
    if ps.isYAxStartedFromZero:
        if ymax > 0:
            ax.axis([xmin, xmax, 0, ymax])
        else:
            ax.axis([xmin, xmax, ymin, 0])


# Invoke the main function here.
if __name__ == "__main__":
    ipPlot()
