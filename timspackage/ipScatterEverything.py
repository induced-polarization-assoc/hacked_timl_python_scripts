# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:57 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import scipy as sp
from ipdataproc import common_sense as cs
import pickle
import matplotlib.pyplot as plt
from textwrap import wrap


class fileClass:
    pass


def ipScatterEverything():

    folderPath = r'C:\temp\180827_smallSQUR'
    fileStart = cs.lastName(folderPath)

    # Processed file choice.
    loadThis = 'zOddH'
    # Plotting choice.
    plotThis = 'zPhase'

    # Channel plotted.
    ch = 2

    # Index of the frequency plotted.
    freqIdx = 0

    # Colors for plotting main results.
    if plotThis == 'zPhase':
        color = 'Red'
    elif plotThis == 'zMag':
        color = 'Green'
    elif plotThis == '2MagPhys':
        color = 'DarkGoldenRod'

    # Loading the data:
    fileName = fileStart + '_' + loadThis + '.pkl'
    filePath = os.path.join(folderPath, fileName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    # Pick out the desired result data to be plotted as x and y values.
    res = cs.emptyClass()
    res.yVal = sp.array([])
    for t in range(len(a)):
        if plotThis == 'zPhase':
            res.yVal = sp.hstack((res.yVal, a[t].phaseDiff[ch, :, freqIdx]))
        elif plotThis == 'zMag':
            res.yVal = sp.hstack((res.yVal, a[t].zMag[ch, :, freqIdx]))
        elif plotThis == '2MagPhys':
            res.yVal = sp.hstack((res.yVal, 2*a[t].magPhys[ch, :, freqIdx]))
    res.xVal = sp.array(range(len(res.yVal)))

    # Initialize plot settings.
    ps = cs.emptyClass()
    ps.color = color
    ps.markerSize = 3
    ps.marker = 'o'
    ps.titleWrap = 75
    ps.xLabel = 'Packets'
    if plotThis == 'zPhase':
        ps.yLabel = 'Impedance Phase (mrad)'
    elif plotThis == 'zMag':
        ps.yLabel = 'Impedance Amplitude (m$\Omega$)'
    elif plotThis == '2MagPhys':
        if ch == 0:
            ps.yLabel = 'Twice Complex Mag. (A)'
        else:
            ps.yLabel = 'Twice Complex Mag. (V)'

    # Plot.
    # Function plots one thing at file_obj_array time and can update formatting and labels.
    params = {'legend.fontsize': 'x-large',
              'figure.figsize': (9, 6.5),
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'x-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    # Plot the main result.
    # Use the string '_nolegend_' to hide the label from the legend display.
    plt.scatter(res.xVal, res.yVal, color=ps.color, marker=ps.marker)

    titleStr = '%s All Packets' % (fileStart)
    if ps.titleWrap < sp.inf:
        # Wrap text at file_obj_array set character length.
        titleStr = '\n'.join(wrap(titleStr, ps.titleWrap))
    plt.title(titleStr)
    plt.xlabel(ps.xLabel)
    plt.ylabel(ps.yLabel)
    plt.legend()
    plt.grid(b=True)
    plt.tight_layout()
    plt.show()


# Invoke the main function here.
if __name__ == "__main__":
    ipScatterEverything()
