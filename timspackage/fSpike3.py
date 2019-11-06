# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:57 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import scipy as sp
from textwrap import wrap
import pickle
import matplotlib.pyplot as plt


class fileClass:
    pass


def fSpike3():
    # Whether to save the plot images.
    doSave = True

    folderPath = r'C:\temp\180806_Creosote'
    fileStart = '180806_Creosote'

    # Processed result choice.
    loadThis = 'freq'

    # Channel plotted.
    ch = 5

    params = {'legend.fontsize': 'x-large',
              'figure.figsize': (9, 6.5),
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'x-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    # Loading the data:
    fileName = fileStart + '_' + loadThis + '.pkl'
    filePath = os.path.join(folderPath, fileName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    # Which file numbers to plot.
    fileNums = 5 + sp.array([-1, 0, 1])

    # Index of the file numbers within the structure.
    tList = [0, 0, 0]
    for take in range(3):
        for t in range(len(a)):
            if a[t].fileNum == fileNums[take]:
                tList[take] = t

    # The frequency at which we search for a spike in phase difference.
    spikeFreq = 100  # (Hz)

    # The harmonic number corresponding to the spike frequency.
    spikeH = int(spikeFreq//a[tList[1]].xmitFund)

    # Index of the requested harmonic number.
    spikeIdx = int((spikeH + 1)//2 - 1)

    # Calculate the relative spike in phase difference at each packet in each
    # file.
    spikeList = 3*[0]
    for take in range(3):
        t = tList[take]
        spikeList[take] = sp.zeros(a[t].pktCount)
        for p in range(a[t].pktCount):
            spikeList[take][p] = relSpike(a[t].phaseDiff[ch, p, :], spikeIdx)

    # Plot each file's results as a box plot.
    fig, ax = plt.subplots()
    ax.boxplot(spikeList, showfliers=False)

    t = tList[1]
    at = a[t]
    titleStr = ('%s Ch %d (%s). xmitFund = %.0f Hz. %s %s'
                % (at.fileDateStr, ch, at.measStr[ch], at.xmitFund,
                   at.major, a[t].minor))
    # Wrap text at a set character length.
    titleStr = '\n'.join(wrap(titleStr, 75))
    plt.title(titleStr)
    locs, xLabels = plt.xticks()  # Get locations and labels
    for take in range(3):
        t = tList[take]
        xLabels[take] = '%d %s' % (a[t].fileNum, a[t].descript)
    plt.xticks(locs, xLabels)  # Set locations and labels
    plt.ylabel('Relative spike in phase difference at %d Hz. (mrad)'
               % spikeFreq)
    plt.grid()
    plt.tight_layout()
    plt.show()

    imgFile = ('%s_ch%d_%d_%dHz' % (a[t].fileDateStr, ch, at.fileNum,
                                    spikeFreq))
    imgFolder = 'fSpike3'
    if doSave:
        imgPath = os.path.join(folderPath, 'plots', imgFolder,
                               imgFile + '.png')
        plt.savefig(imgPath)


def relSpike(arra, spikeIdx):
    # Calculate how much the value at the spike index is different from the
    # average of values at adjacent frequencies on either side.
    expected = (arra[spikeIdx + 1] + arra[spikeIdx - 1])/2
    spike = arra[spikeIdx] - expected
    return spike


# Invoke the main function here.
if __name__ == "__main__":
    fSpike3()
