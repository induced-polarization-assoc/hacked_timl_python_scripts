# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 10:50:36 2018

@author: TimL
"""
import os
import pickle
import ipQuickVsPkt as qvp
import commonSense as cs


class fileClass:
    pass


def ipQuickShow():
    folderPath = r'C:\Users\timl\Documents\IP_data_plots\190506_eagle'
    folderName = cs.lastName(folderPath)

    # Processed result choice.
    loadThis = 'zAnyF'

    # Loading the data:
    pklName = folderName + '_' + loadThis + '.pkl'
    filePath = os.path.join(folderPath, pklName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    # File number to be plotted, and its associated index in the class.
    fileNum = 14
    fileDateStr = '190506'
    # Plotting choice.
    plotThis = 'zPhase'
    # Channel number plotted.
    ch = 1
    # Harmonic number of the xmitFund plotted.
    h = 1

    t = 3000  # Initialization.
    for fileIdx in range(len(a)):
        if (a[fileIdx].fileNum == fileNum and
                a[fileIdx].fileDateStr == fileDateStr):
            t = fileIdx

    qvp.ipQuickVsPkt(a[t], ch, h, plotThis)


# Invoke the main function here.
if __name__ == "__main__":
    ipQuickShow()
