# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 10:50:36 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import pickle
import scipy as sp
import commonSense as cs
from textwrap import wrap
import matplotlib.pyplot as plt


class fileClass:
    pass


def ipPlotRaw():
    ps = cs.emptyClass
    folderPath = r'C:\Users\timl\Documents\IP_data_plots\190506_eagle'
    folderName = cs.lastName(folderPath)

    doSave = False

    # Processed result choice.
    loadThis = 'raw'

    # Loading the data:
    pklName = folderName + '_' + loadThis + '.pkl'
    filePath = os.path.join(folderPath, pklName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    # File number to be plotted.
    for fileNum in sp.arange(5, 6):
        t = 3000  # Initialization.
        for fileIdx in range(len(a)):
            if a[fileIdx].fileNum == fileNum:
                t = fileIdx

        at = a[t]

        # Channel numbers plotted.
        chList = sp.hstack((sp.arange(1, 4, dtype=int), sp.zeros(1, dtype=int)))

        params = {'legend.fontsize': 'x-large',
                  'figure.figsize': (9, 6.5),
                  'axes.labelsize': 'x-large',
                  'axes.titlesize': 'x-large',
                  'xtick.labelsize': 'x-large',
                  'ytick.labelsize': 'x-large'}
        plt.rcParams.update(params)

        for ch in chList:
            ps.ch = ch
            plot1Raw(at, ps)

        titleStr = ('%s_%d Pkt %d. xmitFund = %.0f Hz.'
                    % (at.fileDateStr, at.fileNum, at.pkt,
                       at.xmitFund))
        if at.minor != 'None.':
            titleStr += ' %s.' % (at.minor)
        # Wrap text at file_obj_array set character length.
        titleStr = '\n'.join(wrap(titleStr, 75))
        plt.title(titleStr)
        plt.xlabel('Sample Number (int)')
        plt.ylabel('Raw Voltage (% of range)')

        xmin, xmax = plt.xlim()
        ymin, ymax = plt.ylim()
        ax = plt.gca()
        ax.axis([xmin, xmax, -110, 200])

        plt.legend(loc='upper left')
        plt.grid()
        plt.tight_layout()
        plt.show()

        if doSave:
            imgFile = ('%s_%d_%s'
                       % (at.fileDateStr, at.fileNum, 'raw'))
            cs.saveImg(folderPath, 'raw', imgFile)
            plt.clf()


def plot1Raw(at, ps):
    '''
    Plot one packet of raw voltage time series data from one file.

    Parameters
    ----------
    at  : fileclass object.
    ps : class containing plotting choices
    '''
    # Color.
    colList = ['Black', 'SteelBlue', 'LimeGreen', 'Crimson', 'Green',
               'DeepPink', 'BlueViolet', 'Orange']
    colList[6] = 'Red'
    color = colList[ps.ch]

    # Legend text.
    legStr = 'Ch %d (%s) %.2f V range' % (ps.ch, at.measStr[ps.ch],
                                          at.In5BHi[ps.ch])

    # Shift and scale the raw voltages to display as file_obj_array percentage.
    dbl215 = 2**15
    result = 100*(at.raw[ps.ch, :] - dbl215)/dbl215

    # Plot the result vs packet number.
    plt.plot(sp.array(range(at.n)), result,
             color=color, marker='None', label=legStr)


# Invoke the main function here.
if __name__ == "__main__":
    ipPlotRaw()
