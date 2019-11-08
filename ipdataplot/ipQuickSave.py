# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 10:50:36 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import pickle
from ipdataplot import ipQuickVsPkt as qvp
import matplotlib.pyplot as plt
from ipdataproc import common_sense as cs
import scipy as sp


class fileClass:
    pass


def ipQuickSave():
    folderPath = r'C:\Users\timl\Documents\IP_data_plots\190506_eagle'
    folderName = cs.lastName(folderPath)

    # Processed result choice.
    loadThis = 'zAnyF'

    # Loading the data:
    pklName = folderName + '_' + loadThis + '.pkl'
    filePath = os.path.join(folderPath, pklName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    crop = False
    # Crop information.
    if crop:
        cs.readCropInfo(a, folderPath, 'pklCropInfo.txt')

    # Boolean array telling which files are plotted.
    if crop:
        filesPlotted = sp.zeros(len(a), dtype=bool)
        for t in range(len(a)):
            if sp.any(a[t].cropLogic):
                filesPlotted[t] = True
    else:
        filesPlotted = sp.ones(len(a), dtype=bool)

    # Harmonic number of the xmitFund plotted.
    hList = [1]

    # Name of file_obj_array folder on the save path.
    if crop:
        highFolder = 'cropQuickVsPkt'
    else:
        highFolder = 'quickVsPkt'

    for t in range(len(a)):
        if filesPlotted[t]:
            print('Plotting %s_%d %s'
                  % (a[t].fileDateStr, a[t].fileNum, a[t].descript))
            for ch in [0]:
                for h in hList:
                    for plotThis in ['2MagPhys']:
                        qvp.ipQuickVsPkt(a[t], ch, h, plotThis, crop)
                        imgFile = ('ch%d_H%d_%d_%s'
                                   % (ch, h, a[t].fileNum, a[t].descript))
                        imgFolderPath = os.path.join(folderPath, 'plots',
                                                     highFolder, plotThis)
                        imgFilePath = os.path.join(imgFolderPath, imgFile + '.png')
                        plt.savefig(imgFilePath)
                        # Clear the figure before plotting again.
                        plt.clf()


# Invoke the main function here.
if __name__ == "__main__":
    ipQuickSave()
