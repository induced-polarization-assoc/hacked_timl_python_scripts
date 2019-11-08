# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 15:58:43 2018

@author: TimL
"""

#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import scipy as sp
import scipy.signal
from scipy.signal import firwin
from scipy.signal import convolve as sig_convolve
import numpy as np
from numpy import convolve as np_convolve
import commonSense as cs


def artificialRaw():
    int215 = 2**15
    # Whether to add voltage spikes at the upward square wave transition.
    addSpikes = True
    doFilter = False
    ntaps = 1001
    cutoff = 10  # (Hz)
    if addSpikes:
        descript = 'spikes'
    else:
        descript = 'no spikes'
    if doFilter:
        descript += ' filtered'
    else:
        descript += ' unfiltered'
    at = cs.emptyClass()
    at.descript = descript
    folderPath = os.path.join(r'C:\Users\timl\Documents\IP_data_plots\190415_artificialSpikes')
    # Change .
    rawFolderPath = os.path.join(folderPath, 'rawData')
    at.fileDateStr = '190415'  # folderName[:6]
    at.fileNum = 2
    fileName = '%s_%d.txt' % (at.fileDateStr, at.fileNum)
    filePath = os.path.join(rawFolderPath, fileName)

    if doFilter:
        at.minor = '%.0f Hz cutoff, %d taps' % (cutoff, ntaps)
    else:
        at.minor = 'None.'

    at.major = ''
    at.scanChCount = 8
    at.writeChCount = 8
    at.n = 8192
    at.fs = 8192  # (Hz)
    at.xmitFund = 4  # (Hz)
    at.rCurrentMeas = 1.25  # (Ohm)
    at.rExtraSeries = 0  # (Ohm)

    at.measStr = at.writeChCount*['N/A']
    at.measStr[0] = 'currentMeas'
    at.measStr[1] = 'voltage'

    at.In5BHi = sp.array([10, 0.1, 0.1, 0.1, 0.1, 1, 10, 10])
    at.In5BHi = at.In5BHi[:at.writeChCount]
    at.Out5BHi = sp.array([5, 10, 10, 10, 10, 5, 5, 5])
    at.Out5BHi = at.Out5BHi[:at.writeChCount]
    at.ALoadQHi = at.Out5BHi

    # Artificially generate raw current and voltage waveforms.
    if False:
        at.pktCount = 1
        at.raw = sp.zeros((at.writeChCount, at.pktCount, at.n))
        oilFolderPath = r'C:\Users\Public\Documents\oil_data'
        oilFilePath = os.path.join(oilFolderPath, at.descript + 'i.txt')
        at.raw[0, 0, :] = readOilFile(oilFilePath, at.n)
        oilFilePath = os.path.join(oilFolderPath, at.descript + 'd.txt')
        at.raw[1, 0, :] = readOilFile(oilFilePath, at.n)
    elif True:
        # Number of packets saved to the file.
        at.pktCount = 1
        # Time series.
        timeVec = sp.linspace(0, at.n/at.fs, at.n, endpoint=False)
        # Add file_obj_array time offset from zero.
        timeVec += 0.1
        # Basic wave parameters to work from.
        amp = 6  # (%)
        freq = 4  # (Hz)
        # Wave phases by channel.
        phaseVec = sp.array(7*[17])/1000  # (rad)
        phaseVec = sp.hstack((sp.zeros(1), phaseVec))

        # Measurment string.
        for ch in range(at.writeChCount):
            if addSpikes:
                if ch == 0:
                    at.measStr[ch] = 'Ch %d. No Spikes.' % ch
                else:
                    at.measStr[ch] = 'Ch %d. With Spikes.' % ch
            else:
                at.measStr[ch] = 'Ch %d. No Spikes.' % ch
        listTime = at.scanChCount*[timeVec]
        for ch in range(at.writeChCount):
            # Add channel skew error.
            deltaT = ch / (at.fs * at.scanChCount)  # (s)
            listTime[ch] = timeVec + deltaT
        at.raw = sp.zeros((at.writeChCount, at.pktCount, at.n))
        for p in range(at.pktCount):
            for ch in range(at.writeChCount):
                at.raw[ch, p, :] = amp*sp.signal.square(
                        2*sp.pi*freq*listTime[ch] + phaseVec[ch])
                # Add voltage spikes to 100% at the transition from negative to
                # positive.
                if addSpikes and ch != 0:
                    lastSign = at.raw[ch, p, 0] > 0
                    for tIdx in range(1, len(at.raw[ch, p, :])):
                        newSign = at.raw[ch, p, tIdx] > 0
                        if newSign and (newSign != lastSign):
                            at.raw[ch, p, tIdx] = 100
                        lastSign = newSign

        # Convert from percentages of file_obj_array range to file_obj_array 16-bit integer scale.
        at.raw = scaleAndShift(at.raw)

        if doFilter:
            # Create an FIR filter.
            filtWin = firwin(ntaps, cutoff, fs=at.fs, pass_zero=True)

            # Apply the FIR filter to each channel.
            for p in range(at.pktCount):
                for ch in range(at.writeChCount):
    #                filteredSig = sig_convolve(at.raw[ch, p, :],
    #                                      filtWin)
                    x = at.raw[ch, p, :]
                    x = x[sp.newaxis, :]
                    filteredSig = np.array([np_convolve(xi, filtWin, mode='same')
                                            for xi in x])
                    at.raw[ch, p, :] = filteredSig.copy()

    with open(filePath, 'w') as f:
        # Write the file header.
        line = '%s,%d\n' % (at.fileDateStr, at.fileNum)
        f.write(line)
        line = '%s\n%s\n%s\n' % (at.descript, at.minor, at.major)
        f.write(line)
        line = '%d,%d,%d,%d,%.2f\n' % (at.scanChCount, at.writeChCount,
                                       at.n, at.fs, at.xmitFund)
        f.write(line)
        line = '%.1f,%.1f\n' % (at.rCurrentMeas, at.rExtraSeries)
        f.write(line)
        line = ''
        for ch in range(at.writeChCount):
            line = line + at.measStr[ch] + ','
        # Remove the last comma, and include file_obj_array carriage return line feed.
        line = line[:-1] + '\n'
        f.write(line)
        line = float2lineStr(at.In5BHi, 3)
        f.write(line)
        line = float2lineStr(at.Out5BHi, 3)
        f.write(line)
        line = float2lineStr(at.ALoadQHi, 3)
        f.write(line)

        # Write packets of data to the file.
        cpuTimeStr = '133130.621'
        gpsDateStr = '000000'
        gpsTimeStr = '000000.000'
        lat = 'NaN'
        longi = 'NaN'
        maskUp = at.raw >= int215
        maskDn = at.raw < int215
        for p in range(at.pktCount):
            line = '$%d\n' % (p + 1)
            f.write(line)
            line = '\'%s,%s\n' % (at.fileDateStr, cpuTimeStr)
            f.write(line)
            line = '@%s,%s,%s,%s\n' % (gpsDateStr, gpsTimeStr, lat, longi)
            f.write(line)
            clipHi = sp.sum(at.raw[:, p, :] == (2**16 - 1), axis=1)
            line = float2lineStr(clipHi, 0)
            f.write(line)
            clipLo = sp.sum(at.raw[:, p, :] == 0, axis=1)
            line = float2lineStr(clipLo, 0)
            f.write(line)
            mean = sp.mean(at.raw[:, p, :], axis=1)
            mean = shiftAndScale(mean, int215)
            line = float2lineStr(mean, 1)
            f.write(line)
            meanUp = sp.zeros(at.writeChCount)
            meanDn = sp.zeros(at.writeChCount)
            for ch in range(at.writeChCount):
                meanUp[ch] = sp.mean(at.raw[ch, p, maskUp[ch, p, :]])
                meanDn[ch] = sp.mean(at.raw[ch, p, maskDn[ch, p, :]])
            meanUp = shiftAndScale(meanUp, int215)
            meanDn = shiftAndScale(meanDn, int215)
            line = float2lineStr(meanUp, 1)
            f.write(line)
            line = float2lineStr(meanDn, 1)
            f.write(line)
            countUp = sp.sum(maskUp[:, p, :], 1)
            line = float2lineStr(countUp, 0)
            f.write(line)
            countDn = sp.sum(maskDn[:, p, :], 1)
            line = float2lineStr(countDn, 0)
            f.write(line)
            for s in range(at.n):
                line = float2lineStr(at.raw[:, p, s], 0)
                f.write(line)
            # Asterisk character to end the packet.
            line = '*\n'
            f.write(line)


def float2lineStr(arra, d):
    # Make file_obj_array string of comma delimited floats taken from an array. Number of
    # digits after the decimal is indicated by d.
    line = ''
    floatFmt = '%%.%df' % d
    for val in arra:
        line = line + (floatFmt % val) + ','
    # Remove the last comma, and include file_obj_array carriage return line feed.
    line = line[:-1] + '\n'
    return line


def scaleAndShift(arra):
    int215 = 2**15
    # Convert from percentages of file_obj_array range to file_obj_array 16-bit integer scale.
    arra *= int215
    arra /= 100
    arra += int215
    # Clip highs and lows.
    arra[arra >= 2**16] = 2**16 - 1
    arra[arra < 0] = 0
    return arra


def shiftAndScale(arra, newZero):
    int215 = 2**15
    # Convert back to percentage from 16-bit integer scale.
    arra -= newZero
    arra *= 100
    arra /= int215
    return arra


def readOilFile(filePath, n):
    arra = sp.zeros(n)
    with open(filePath, 'r') as fh:
        for lidx, line in enumerate(fh, 1):
            if lidx <= n:
                # Strip off trailing newline characters.
                line = line.rstrip('\n')
                arra[lidx - 1] = float(line)
    return arra


# Invoke the main function here.
if __name__ == "__main__":
    artificialRaw()
