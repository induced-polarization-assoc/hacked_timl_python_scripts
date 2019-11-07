# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 10:50:36 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import pickle
from ipdataproc import common_sense as cs


class fileClass:
    pass

# FIXME: ADD A PASSED VARIABLE TO THE FILE OBJECT THAT SETS THE FOLDER PATH BASED ON THE INITIAL CALLS TO THE GUI
def pklCrop():
    folderPath = r'C:\temp\181112_eagle'
    folderName = cs.lastName(folderPath)

    # Processed result choice.
    loadThis = 'zAnyF'

    # Loading the data:
    pklName = folderName + '_' + loadThis + '.pkl'
    filePath = os.path.join(folderPath, pklName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    # Read the crop information.
    infoPath = os.path.join(folderPath, 'pklCropInfo.txt')
    with open(infoPath, 'r') as f:
        for lidx, line in enumerate(f, 1):
            # Strip off trailing newline characters.
            line = line.rstrip('\n')
            # Split up comma-delimited information.
            (fileDateStr, fileNum, startPkt, endPkt) = line.split(',')
            # Type casting.
            fileNum = int(fileNum)
            startPkt = int(startPkt)
            # Identify the corresponding file in the structure.
            t = -1  # Initialization.
            for fileIdx in range(len(a)):
                if (a[fileIdx].fileNum == fileNum and
                        a[fileIdx].fileDateStr == fileDateStr):
                    t = fileIdx
            if endPkt == 'inf':
                endPkt = a[t].pktCount - 1
            else:
                endPkt = int(endPkt)
            pktRang = range(startPkt, endPkt + 1)
            # Crop the data.
            a[t].pktCount = len(pktRang)
            # 0-indexed by packet number.
            a[t].pkt = a[t].pkt[pktRang]
            a[t].cpuDTStr = a[t].cpuDTStr[startPkt:(endPkt + 1)]
            a[t].cpuDT = a[t].cpuDT[startPkt:(endPkt + 1)]
            a[t].gpsDTStr = a[t].gpsDTStr[startPkt:(endPkt + 1)]
            a[t].gpsDT = a[t].gpsDT[startPkt:(endPkt + 1)]
            a[t].lat = a[t].lat[pktRang]
            a[t].longi = a[t].longi[pktRang]
            # 0-indexed by channel number.
            # 0-indexed by packet number.
            a[t].clipHi = a[t].clipHi[:, pktRang]
            a[t].clipLo = a[t].clipLo[:, pktRang]
            a[t].meanPct = a[t].meanPct[:, pktRang]
            a[t].meanUpPct = a[t].meanUpPct[:, pktRang]
            a[t].meanDnPct = a[t].meanDnPct[:, pktRang]
            a[t].meanPhys = a[t].meanPhys[:, pktRang]
            a[t].meanUpPhys = a[t].meanUpPhys[:, pktRang]
            a[t].meanDnPhys = a[t].meanDnPhys[:, pktRang]
            a[t].countUp = a[t].countUp[:, pktRang]
            a[t].countDn = a[t].countDn[:, pktRang]
            # 0-indexed by frequency index.
            a[t].freq = a[t].freq
            # 0-indexed by channel number.
            # 0-indexed by packet number.
            # 0-indexed by frequency index.
            a[t].phaseDiff = a[t].phaseDiff[:, pktRang, :]
            a[t].magPhys = a[t].magPhys[:, pktRang, :]
            a[t].zMag = a[t].zMag[:, pktRang, :]

    # Save the cropped data.
    pklName = folderName + '_' + loadThis + '_crop.pkl'
    pklPath = os.path.join(folderPath, pklName)
    # Saving the list object:
    with open(pklPath, 'wb') as f:  # Python 3: open(..., 'wb')
        pickle.dump(a, f)


# Invoke the main function here.
if __name__ == "__main__":
    pklCrop()
