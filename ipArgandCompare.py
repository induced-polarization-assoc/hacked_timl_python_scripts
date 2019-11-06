# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 11:19:02 2019

@author: TimL
"""
import ipArgand as arg
import scipy as sp
import commonSense as cs

class fileClass:
    pass


def ipArgandCompare():

    pklFolder = r'C:\Users\timl\Documents\IP_data_plots\190503_oil'
    fileNums = sp.array([6, 7, 8, 9, 10])
    # File numbers with the low frequency for normalization for each file
    # number.
#    lowFiles = sp.zeros_like(fileNums)
#    shortColors = ['C0', 'C1', 'blueviolet']
#    shortIdx = 0
#    shortLinestyles = ['--', '-', '-']
#
#    colors = []
#    linestyles = []
#    legFilter = sp.zeros_like(fileNums, dtype=bool)
#    for idx in range(0, len(fileNums), 3):
#        lowFiles[idx:idx+3] = fileNums[idx]
#        colors += 3*[shortColors[shortIdx]]
#        linestyles += 3*[shortLinestyles[shortIdx]]
#        shortIdx += 1
#        legFilter[idx] = True

    linestyles = len(fileNums)*['-']
    colors = len(fileNums)*[None]
    legFilter = sp.ones(len(fileNums), dtype=bool)
    lowFiles = fileNums.copy()

    instruct = cs.emptyClass()
    instruct.pklFolder = pklFolder
    instruct.fileNums = fileNums
    instruct.lowFiles = lowFiles
    instruct.colors = colors
    instruct.linestyles = linestyles
    instruct.legFilter = legFilter

    arg.ipArgand(instruct)


# Invoke the main function here.
if __name__ == "__main__":
    ipArgandCompare()
