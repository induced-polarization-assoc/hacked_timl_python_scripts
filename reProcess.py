# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 15:57:16 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import matplotlib.pyplot as plt
import artificialRaw as ar
import ipProcess as ip
import ipPlot as ipPlt


def reProcess():
    # Reprocess data files of one packet each saved as current and voltages
    # separately.
    descript = 'onm'
    plotFolder = r'C:\Users\Public\Documents\oil_data\reprocess'
    pklFolder = os.path.join(plotFolder, descript)
    os.mkdir(pklFolder)
    # Raw data folder within the pickle folder.
    os.mkdir(os.path.join(pklFolder, 'rawData'))
    ar.artificialRaw(descript)
    ip.ipProcess(pklFolder)
    ipPlt.ipPlot(pklFolder)
    # Save the image.
    imgPath = os.path.join(plotFolder, descript + '.png')
    plt.savefig(imgPath)


# Invoke the main function here.
if __name__ == "__main__":
    reProcess()
