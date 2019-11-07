# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 11:19:02 2019

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
from ipdataplot import ipPlot as ipPlt

import scipy as sp


class fileClass:
    pass


def ipPlotCompare():
    commonPath = r'C:\Users\timl\Documents\IP_data_plots'
    plotThis = 'zPhase'

    folderList = ['190503_oil']
    fileNums = sp.array([1, 2, 3, 4])

    for idx in range(len(folderList)):
        pklFolder = os.path.join(commonPath, folderList[idx])
        ipPlt.ipPlot(pklFolder, fileNums, plotThis)


# Invoke the main function here.
if __name__ == "__main__":
    ipPlotCompare()
