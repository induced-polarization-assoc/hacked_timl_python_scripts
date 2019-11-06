# -*- coding: utf-8 -*-
'''
Created on Mon May 14 16:31:21 2018

@author: TimL
'''
import os
import matplotlib.pyplot as plt
import scipy as sp


class emptyClass:
    pass


def find(arra, val):
    # Matlab-like find function that returns the first (zero-based) index in
    # the array where the array value equals the value to be found. This find
    # function is for 1D scipy/numpy arrays.
    # Returns an integer index. If the value is not found, the output is -1.
    tupleAnswer = sp.where(arra == val)
    arrayAnswer = tupleAnswer[0]
    if len(arrayAnswer) > 0:
        intAnswer = int(arrayAnswer[0])
    else:
        intAnswer = -1
    return intAnswer


def lastName(pathStr):
    # Return the last name in the path of backslash-delimited words.
    lastSlash = pathStr.rfind('\\')
    return pathStr[lastSlash+1:]


def saveImg(folderPath, imgFolder, imgFile):
    imgPath = os.path.join(folderPath, 'plots', imgFolder, imgFile + '.png')
    plt.savefig(imgPath)


def readFilesPlotted(a, folder):
    infoPath = os.path.join(folder, 'filesPlotted.txt')
    # Initialize a boolean array corresponding to the indices of 'a', telling
    # which files are to be plotted.
    filesPlotted = sp.zeros(len(a), dtype=bool)
    with open(infoPath, 'r') as f:
        for lidx, line in enumerate(f, 1):
            # Strip off trailing newline characters.
            line = line.rstrip('\n')
            splitLine = line.split(',')
            fileDateStr = splitLine[0]
            fileNum = splitLine[1]
            fileNum = int(fileNum)

            # Identify the corresponding file in the structure.
            t = -1  # Initialization.
            for fileIdx in range(len(a)):
                if (a[fileIdx].fileNum == fileNum and
                        a[fileIdx].fileDateStr == fileDateStr):
                    t = fileIdx

            filesPlotted[t] = bool(int(splitLine[2]))

    return filesPlotted


def readCropInfo(a, folder, file):
    # Read the crop information, and save in boolean arrays.
    infoPath = os.path.join(folder, file)
    with open(infoPath, 'r') as f:
        for lidx, line in enumerate(f, 1):
            # Strip off trailing newline characters.
            line = line.rstrip('\n')
            splitLine = line.split(',')
            fileDateStr = splitLine[0]
            fileNum = splitLine[1]
            fileNum = int(fileNum)

            # Identify the corresponding file in the structure.
            t = -1  # Initialization.
            for fileIdx in range(len(a)):
                if (a[fileIdx].fileNum == fileNum and
                        a[fileIdx].fileDateStr == fileDateStr):
                    t = fileIdx
            # Initialize the logical array.
            a[t].cropLogic = sp.zeros_like(a[t].pkt, dtype=bool)

            for splitIdx in range(2, len(splitLine), 2):
                startPkt = splitLine[splitIdx]
                endPkt = splitLine[splitIdx + 1]
                startPkt = int(startPkt)
                # Type casting.
                if endPkt == 'inf':
                    endPkt = a[t].pktCount - 1
                else:
                    endPkt = int(endPkt)
                pktRang = range(startPkt, endPkt + 1)
                a[t].cropLogic[pktRang] = True
