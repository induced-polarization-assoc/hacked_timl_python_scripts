# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:57 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import scipy as sp
from ipdataproc import common_sense as cs
import plotWrap as pw
import pickle
import matplotlib.pyplot as plt


class fileClass:
    pass


def ipArgand(instruct):
    # Whether to save the plot images.
    doSave = False

    plotThis = 'zPhase'

    pklFolder = instruct.pklFolder
    fileStart = cs.lastName(pklFolder)

    # Processed file choice.
    loadThis = 'zAnyF'

    # Channels plotted.
    ch = 2

    # Whether to identify and plot target files.
    targetBool = True

    # Whether to manually select which file numbers to plot.
    manualTargetBool = True
    manualTargetArra = instruct.fileNums

    # Whether to plot all the files together without erasing at all.
    fileTogether = True

    # Whether to omit 60 Hz data from the plots.
    omit60Hz = True

    # Frequencies plotted.
    maskChoice = 'oddHUp2'

    isYAxStartedFromZero = False
    
    # Whether to subtract baseline phase results from separate files.
    subtract1 = False
    if subtract1:
        # Pick a standard packet range to use.
        pktRang = range(17)

    # Whether to include the minor note in the legend entries rather than the
    # title.
    minorLegBool = False

    # Whether to include the minor note anywhere at all.
    minorBool = True

    # Whether to swap the description and minor note text for display purposes.
    swapDescriptMinor = False

    legOutside = False
    loc = 'center right'

    stdBool = False
    
    # Whether to plot only one packet's results instead of an average over all
    # the packets in the file.
    onePkt = False

    # File number from which the plot title is taken. inf if it doesn't matter.
    titleFileNum = sp.inf

    # Let colors be selected automatically if files are plotted together.
    if fileTogether:
        color = None
        stdColor = None

    # Loading the data:
    fileName = fileStart + '_' + loadThis + '.pkl'
    filePath = os.path.join(pklFolder, fileName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    # List of file numbers.
    fileNumArra = sp.zeros(len(a))
    for t in range(len(a)):
        fileNumArra[t] = a[t].fileNum
        if swapDescriptMinor:
            descript = a[t].descript
            a[t].descript = a[t].minor
            a[t].minor = descript

    if targetBool:
        tarList = []
        lowFilesA = sp.zeros(len(a), dtype=int)
        colorsA = len(a)*['']
        linestylesA = len(a)*['']
        legFilterA = sp.zeros(len(a), dtype=bool)
        for t in range(len(a)):
            if manualTargetBool:
                if any(a[t].fileNum == manualTargetArra):
                    tarList.append(t)
                    # Set up the low frequency normalization files for each file.
                    manualIdx = cs.find(manualTargetArra, a[t].fileNum)
                    lowFileNum = instruct.lowFiles[manualIdx]
                    lowFilesA[t] = cs.find(fileNumArra, lowFileNum)
                    colorsA[t] = instruct.colors[manualIdx]
                    linestylesA[t] = instruct.linestyles[manualIdx]
                    legFilterA[t] = instruct.legFilter[manualIdx]
            else:
                # Identify target files (They aren't baselines or tests).
                if a[t].descript != 'baseline' and a[t].descript != 'test':
                    if t < (len(a) - 1):
                        tarList.append(t)

    # Discover the maximum file number.
    maxFile = -sp.inf
    for t in range(len(a)):
        if a[t].fileNum > maxFile:
            maxFile = a[t].fileNum

    # Pick out the desired result data to be plotted as x and y values.
    res = []

    for t in range(len(a)):
        # Result class for each possible file to be read.
        res.append(cs.emptyClass())

    for t in tarList:
        if not subtract1 or not any(t == sp.array(tarList)):
            # (radian)
            phaseDiff = a[t].phaseDiff[ch, ...]/1000
            zMag = a[t].zMag[ch, ...]
        else:
            # Subtract the baseline phase differences. (radian)
            fileOff = 3
            phaseDiff = (a[t].phaseDiff[ch, pktRang, :] -
                         a[t-fileOff].phaseDiff[ch, pktRang, :])/1000
            # Magnitudes.
            zMag = a[t].zMag[ch, pktRang, :]
            
        res[t].xVal = zMag*sp.cos(phaseDiff)
        res[t].yVal = zMag*sp.sin(phaseDiff)
        
        # Average over packets.
        if not onePkt:
            res[t].xVal = sp.mean(res[t].xVal, axis=0)
            res[t].yVal = sp.mean(res[t].yVal, axis=0)
        else:
            meanRang = instruct.pkt + sp.array([-1, 0, 1])
            res[t].xVal = res[t].xVal[meanRang, :]
            res[t].yVal = res[t].yVal[meanRang, :]
            # Average over the chosen packet and those on either side.
            res[t].xVal = sp.mean(res[t].xVal, axis=0)
            res[t].yVal = sp.mean(res[t].yVal, axis=0)


        # Mask out unwanted frequencies.
        mask = sp.zeros_like(a[t].freq, dtype=bool)
        if maskChoice == 'oddHUp2':
            mask[4:len(mask):8] = True
            # Number of frequencies included in the plot.
            freqCount = 17
            mask[(1+4+8*(freqCount-1)):] = False
        # Mask out 60 Hz, if requested.
        if omit60Hz:
            mask[a[t].freq == 60] = False
        res[t].xVal = res[t].xVal[mask]
        res[t].yVal = res[t].yVal[mask]

        # Result X and Y data normalized by the low freq. fundamental real
        # component of impedance.
        if t == lowFilesA[t]:
            maxReal1 = res[lowFilesA[t]].xVal[0]
        res[t].xVal /= maxReal1
        res[t].yVal /= maxReal1
        
        # If the phase difference baselines were subtracted, divide the
        # magnitudes.
        if subtract1 and any(t == sp.array(tarList)):
            baseMags = sp.sqrt(res[t-fileOff].xVal**2 + res[t-fileOff].yVal**2)
            res[t].xVal /= baseMags
            res[t].yVal /= baseMags
            # Renormalize.
            if t == lowFilesA[t]:
                maxReal2 = res[lowFilesA[t]].xVal[0]
            res[t].xVal /= maxReal2
            res[t].yVal /= maxReal2

    # Initialize plot settings.
    ps = cs.emptyClass()
    # Figure with axes.
    ps.color = color
    ps.stdColor = stdColor
    ps.markerSize = 5
    ps.marker = 'o'
    ps.linestyle = '-'
    ps.markerSize = 4
    ps.titleWrap = 83
    ps.legOutside = legOutside
    ps.omit60Hz = omit60Hz
    ps.isYAxStartedFromZero = isYAxStartedFromZero
    ps.xLabel = 'REAL'
    ps.yLabel = 'IMAG'
    ps.stdBool = stdBool
    ps.normMag = False
    ps.loc = loc

    # List of file indices plotted.
    if targetBool:
        tList = tarList
    else:
        tList = range(0, len(a))

    # List adjacent files with each target file, if there are three per plot.
    tarList = tList

    # Plot, and save if needed.
    for idx in range(len(tList)):
        t = tList[idx]
        tar = tarList[idx]
        ps.ch = ch
        ps.color = colorsA[t]
        ps.linestyle = linestylesA[t]
#        ps.titleStr = ('%s Ch %d (%s). xmitFund = %.0f Hz. %s'
#                       % (a[t].fileDateStr, ch, a[t].measStr[ch],
#                          a[t].xmitFund, a[t].major))
        ps.titleStr = ('%s Ch %d (%s). xmitFund = %.0f Hz.'
               % (a[t].fileDateStr, ch, a[t].measStr[ch],
                  a[t].xmitFund))
#        ps.titleStr = ('Phase differences for artificial signals.')
        if onePkt:
            ps.titleStr += (' Results averaged over three packets centered '
                            'on each packet listed in the legend.')
 
        if subtract1:
            ps.titleStr += (' Baseline sand phase angles have been subtracted, ' +
                        'and normalized magnitudes have been divided by ' +
                        'baseline normalized magnitudes before normalizing ' +
                        'to a low frequency real value of 1 again.')
        # Legend text.
        if legFilterA[t]:
            # With legend.
            ps.legStr = 'File %d. Ch %d. %s.' % (a[t].fileNum, ch,
                                                 a[t].descript)
            if onePkt:
                ps.legStr = '(pkt %d) ' % (a[t].pkt[instruct.pkt]) + ps.legStr
        else:
            # Without legend.
            ps.legStr = '_nolegend_'
        if minorBool and (ps.legStr != '_nolegend_'):
            if not minorLegBool:
                if a[t].minor != 'None.':
                    ps.titleStr += ' %s.' % (a[t].minor)
            else:
                ps.legStr += ' %s.' % (a[t].minor)
        # The plot title is taken from the target file.
        ps.titleBool = False
        if t == tar:
            if (titleFileNum == sp.inf) or (titleFileNum == a[t].fileNum):
                ps.titleBool = True

        if plotThis == 'argand':
            ps.titleStr += ' Normalized Apparent Impedance Argand.'
            ps.xVal = res[t].xVal
            ps.yVal = res[t].yVal
        elif plotThis == 'zMag':
            ps.xVal = a[t].freq[mask]
            ps.yVal = sp.sqrt(res[t].xVal**2 + res[t].yVal**2)
            if subtract1:
                ps.titleStr += (' Normalized magnitudes have been divided by ' +
                        'baseline normalized magnitudes before normalizing ' +
                        'to a low frequency real value of 1 again.')
            ps.xLabel = 'Frequency (Hz)'
            ps.yLabel = 'Impedance Magnitude (Normalized)'
        elif plotThis == 'zPhase':
            ps.xVal = a[t].freq[mask]
            # Milliradian
            ps.yVal = 1000*sp.arctan2(res[t].yVal, res[t].xVal)
            ps.xLabel = 'Frequency (Hz)'
            ps.yLabel = 'Impedance Phase (mrad)'
        pw.basePlot(ps)

        if (t == tar):
            if ((not fileTogether) or
                    (fileTogether and idx == len(tList) - 1)):
                if doSave:
                    pass
                if not (t == tList[-1]):
                    plt.clf()

    ax = plt.gca()
    if plotThis == 'argand':
        ax.set_aspect('equal', 'box')
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    if ps.isYAxStartedFromZero:
        if ymax > 0:
            ax.axis([xmin, xmax, 0, ymax])
        else:
            ax.axis([0, xmax, ymin, 0])


# Invoke the main function here.
if __name__ == "__main__":
    ipArgand()
