# -*- coding: utf-8 -*-
'''
Created on Mon May 14 16:31:21 2018

@author: TimL
'''
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import os
import scipy as sp
from ipdataproc import common_sense as cs
from scipy import fftpack as spfftpack
from datetime import datetime
import pickle


def ipProcess():
    '''
    Reads text files in a data folder and saves frequency domain results to a
    pickled file to be opened later for plotting.
    '''
    # Processed result choice.
    # 'raw': raw voltage waveforms from one packet in each file.
    # 'zAnyF': impedance phase and mag at non-zero fft frequencies,
    #          not skipping.
    saveThis = 'raw'

    # Number nonzero frequencies saved to the .pkl file with the zero frequency
    freqCount = 200

    # Whether to save absolute phase results.
    savePhase = False

    # Whether to select a specific file for processing, as opposed to all of
    # them.
    selectedFile = True
    selectedFileNum = 5

    pklFolder = r'C:\Users\timl\Documents\IP_data_plots\190506_eagle'
    rawFolder = os.path.join(pklFolder, 'rawData')
    fileList = ([f for f in os.listdir(rawFolder)
                 if os.path.isfile(os.path.join(rawFolder, f))])
    # Catalog the file numbers stored in each file title. Remove from the list
    # files that don't have a number.
    fileNumList = []
    keepFileList = sp.zeros_like(fileList, dtype=bool)
    for t in range(len(fileList)):
        uscoreIdx = fileList[t].find('_')
        dotIdx = fileList[t].find('.')
        if uscoreIdx >= 0 and dotIdx >= 0:
            try:
                fileNum = int(fileList[t][uscoreIdx+1: dotIdx])
            except ValueError:
                pass
            else:
                if not selectedFile or (selectedFile and
                                        fileNum == selectedFileNum):
                    fileNumList.append(fileNum)
                    # Keep this file in the list.
                    keepFileList[t] = True

    # Drop all files from the list that didn't have a number.
    # Walk through in reverse order so as to not disturb index numbers as
    # elements are removed.
    for t in range(len(fileList))[::-1]:
        if ~keepFileList[t]:
            del fileList[t]
    # Convert to arrays.
    fileArr = sp.array(fileList)
    fileNumArr = sp.array(fileNumList, dtype=int)
    del fileList
    del keepFileList
    # Sort by file numbers.
    sortKey = fileNumArr.argsort()
    fileArr = fileArr[sortKey]
    fileNumArr = fileNumArr[sortKey]

    # List of class instances containing recorded data.
    a = []
    for t in range(len(fileArr)):
        a.append(fileClass())

    # Read the data in from the files.
    for t in range(len(a)):
        # Packet choice if saving raw voltages.
        rawPkt = 102  # 1-indexed.
        filePath = os.path.join(rawFolder, fileArr[t])
        a[t].introduce(fileArr[t])
        a[t].readTxt(filePath, saveThis)
        # Remove unwanted fields to cut down on the saved file size.
        if saveThis == 'zAnyF' or saveThis == 'upsideDown':
            del a[t].raw
            del a[t].fft
            del a[t].phaseUnCorr
            del a[t].mag16Bit
            if not savePhase:
                del a[t].phase
            # Array mask for saving.
            mask = sp.zeros(a[t].n, dtype=bool)
            # Save non-zero frequencies and the DC frequency.
            mask[:freqCount + 1] = True
            a[t].freq = a[t].freq[mask]
            a[t].phaseDiff = a[t].phaseDiff[..., mask]
            a[t].magPhys = a[t].magPhys[..., mask]
            a[t].zMag = a[t].zMag[..., mask]
            if savePhase:
                a[t].phase = a[t].phase[..., mask]
        elif saveThis == 'raw':
            del a[t].fft
            del a[t].phaseUnCorr
            del a[t].mag16Bit
            del a[t].phase
            del a[t].freq
            del a[t].phaseDiff
            del a[t].magPhys
            del a[t].zMag
            p = cs.find(a[t].pkt, rawPkt)
            if p == -1:
                # Save the last packet if the requested packet number isn't in
                # the file.
                rawPkt = a[t].pkt[p]
            a[t].raw = a[t].raw[:, p, :]
            # Overwrite the list of packet numbers with the one packet number
            # that was saved.
            a[t].pkt = rawPkt

    # Save the object to a file named after the folder name.
    lastSlash = pklFolder.rfind('\\')
    saveFile = pklFolder[lastSlash+1:] + '_' + saveThis + '.pkl'
    savePath = os.path.join(pklFolder, saveFile)
    # Saving the list object:
    with open(savePath, 'wb') as f:  # Python 3: open(..., 'wb')
        pickle.dump(a, f)


class fileClass:

    def introduce(self, fileName):
        print('Creating %s from %s.' % (self, fileName))

    def readTxt(self, filePath, saveThis):
        # Read IP measurements from a text file.
        with open(filePath, 'r') as fh:
            # Number of lines in the file.
            lineCount = self.countLines(fh)
            # Rewind the pointer in the file back to the beginning.
            fh.seek(0)
            # Initialize the packet counter.
            p = -1
            # Initialize the sample index.
            s = -1
            for lidx, line in enumerate(fh, 1):
                # Strip off trailing newline characters.
                line = line.rstrip('\n')
                if s >= 0:
                    # Read in raw voltage values.
                    self.raw[:, p, s] = (
                            sp.fromstring(line, dtype=float, sep=','))
                    if s == self.n - 1:
                        # Reset the counter to below zero.
                        s = -1
                    else:
                        # Increment the sample counter for the next read.
                        s += 1
                elif lidx > 10:
                    if line[0] == '$':
                        # Increment the packet index.
                        p += 1
                        # Reset the time domain quality parameter index.
                        qp = 0
                        # Packet number
                        self.pkt[p] = int(line[1:])
                    elif line[0] == '\'':
                        # CPU UTC Date and Time Strings.
                        (self.cpuDTStr[p].d,
                         self.cpuDTStr[p].t) = line[1:].split(',')
                        # Translate to datetime object.
                        self.cpuDT[p] = self.str2DateTime(self.cpuDTStr[p])
                    elif line[0] == '@':
                        # GPS UTC Date and Time Strings,
                        # and latitude and longitude fixes.
                        (self.gpsDTStr[p].d,
                         self.gpsDTStr[p].t,
                         self.lat[p],
                         self.longi[p]) = line[1:].split(',')
                        # Translate to datetime object.
                        self.gpsDT[p] = self.str2DateTime(self.gpsDTStr[p])
                        # Type casting.
                        self.lat[p] = float(self.lat[p])
                        self.longi[p] = float(self.longi[p])
                    elif qp < 7:
                        qp += 1
                        if qp == 3 or qp == 4 or qp == 5:
                            typ = float  # Means are saved as floats.
                        else:
                            typ = int  # Counts are saved as integers.
                        assignArr = sp.fromstring(line, dtype=typ, sep=',')
                        if qp == 1:
                            # Count of measurements clipped on the high end of
                            # the MccDaq board's input range.
                            self.clipHi[:, p] = assignArr
                        elif qp == 2:
                            # Count of measurements clipped on the low end of
                            # the MccDaq board's input range.
                            self.clipLo[:, p] = assignArr
                        elif qp == 3:
                            # Mean measurement value over the packet as a
                            # percentage of the AIn() half range.
                            self.meanPct[:, p] = assignArr
                        elif qp == 4:
                            # (pct) Mean value of sample measurements above
                            # or equal to the mean.
                            self.meanUpPct[:, p] = assignArr
                        elif qp == 5:
                            # (pct) Mean value of sample measurements below
                            # the mean.
                            self.meanDnPct[:, p] = assignArr
                        elif qp == 6:
                            # Count of measurements above or equal to the mean.
                            self.countUp[:, p] = assignArr
                        elif qp == 7:
                            # Count of measurements below the mean.
                            self.countDn[:, p] = assignArr
                            # Set the sample index to 0 to start.
                            s = 0
                elif lidx == 1:
                    (self.fileDateStr,  # UTC date file was created.
                     self.fileNum) = line.split(',')  # File number in set.
                    # Type casting.
                    self.fileNum = int(self.fileNum)
                elif lidx == 2:
                    self.descript = line  # Description of the test.
                elif lidx == 3:
                    self.minor = line  # Minor note.
                elif lidx == 4:
                    self.major = line  # Major note.
                elif lidx == 5:
                    (self.scanChCount,  # number of channels in each A/D scan.
                     self.chCount,  # number of channels written to the file.
                     self.n,  # Number of samples in the FFT time series.
                     self.fs,  # (Hz) FFT sampling frequency.
                     self.xmitFund) = line.split(',')  # (Hz) Transmit Square
                    # wave fundamental frequency.
                    # Type casting.
                    self.scanChCount = int(self.scanChCount)
                    self.chCount = int(self.chCount)
                    self.n = int(self.n)
                    self.fs = int(self.fs)
                    self.xmitFund = float(self.xmitFund)
                    # Each file contains a file header of length 10 lines,
                    # followed by packets. Packets contain (11 + n) lines each.
                    self.pktCount = int((lineCount - 10)/(11 + self.n))
                    # Dimension arrays indexed by packet.
                    self.dimArrays()
                elif lidx == 6:
                    (self.rCurrentMeas,  # (Ohm) resistance.
                     self.rExtraSeries) = line.split(',')  # (Ohm).
                    # Type casting.
                    self.rCurrentMeas = float(self.rCurrentMeas)
                    self.rExtraSeries = float(self.rCurrentMeas)
                elif lidx == 7:
                    # Voltage measurement names.
                    # 0-indexed by channel number.
                    self.measStr = line.split(',')
                elif lidx == 8:
                    # Construct arrays using the scipy package.
                    # 5B amplifier maximum of the input range (V).
                    # 0-indexed by channel number.
                    self.In5BHi = sp.fromstring(line, dtype=float, sep=',')
                elif lidx == 9:
                    # 5B amplifier maximum of the output range (V).
                    # 0-indexed by channel number.
                    self.Out5BHi = sp.fromstring(line, dtype=float, sep=',')
                elif lidx == 10:
                    # MccDaq board AIn() maximum of the input range (V).
                    # 0-indexed by channel number.
                    self.ALoadQHi = sp.fromstring(line, dtype=float, sep=',')
        # After the file has been read, perform some calculations.
        self.postRead(saveThis)

    def dimArrays(self):
        # Initialize numpy arrays and python lists as zeros.
        shape2D = (self.chCount, self.pktCount)
        # 0-indexed by packet number.
        self.pkt = sp.zeros(self.pktCount, dtype=int)
        self.cpuDTStr = [cs.emptyClass()]*self.pktCount
        self.cpuDT = [0]*self.pktCount
        self.gpsDTStr = [cs.emptyClass()]*self.pktCount
        self.gpsDT = [0]*self.pktCount
        self.lat = sp.zeros(self.pktCount, dtype=float)
        self.longi = sp.zeros(self.pktCount, dtype=float)
        # 0-indexed by channel number.
        # 0-indexed by packet number.
        self.clipHi = sp.zeros(shape2D, dtype=int)
        self.clipLo = sp.zeros(shape2D, dtype=int)
        self.meanPct = sp.zeros(shape2D, dtype=float)
        self.meanUpPct = sp.zeros(shape2D, dtype=float)
        self.meanDnPct = sp.zeros(shape2D, dtype=float)
        self.meanPhys = sp.zeros(shape2D, dtype=float)
        self.meanUpPhys = sp.zeros(shape2D, dtype=float)
        self.meanDnPhys = sp.zeros(shape2D, dtype=float)
        self.countUp = sp.zeros(shape2D, dtype=int)
        self.countDn = sp.zeros(shape2D, dtype=int)
        # 0-indexed by channel number.
        # 0-indexed by packet number.
        # 0-indexed by sample number.
        self.raw = sp.zeros((self.chCount, self.pktCount, self.n), dtype=float)

    def str2DateTime(self, dTStr):
        YY = 2000 + int(dTStr.d[0: 0+2])
        MO = int(dTStr.d[2: 2+2])
        DD = int(dTStr.d[4: 4+2])
        HH = int(dTStr.t[0: 0+2])
        MM = int(dTStr.t[2: 2+2])
        SS = int(dTStr.t[4: 4+2])
        micro = 1000 * int(dTStr.t[7: 7+3])
        if YY == 2000:
            return datetime.min
        else:
            return datetime(YY, MO, DD, HH, MM, SS, micro)

    def computePhys(self, currentCh):
        self.meanPhys = self.pct2Phys(self.meanPct, currentCh)
        self.meanUpPhys = self.pct2Phys(self.meanUpPct, currentCh)
        self.meanDnPhys = self.pct2Phys(self.meanDnPct, currentCh)

    def pct2Phys(self, pct, currentCh):
        phys = sp.zeros_like(pct, dtype=float)
        for ch in range(self.chCount):
            phys[ch, :] = (pct[ch, :] / 100 *
                           self.ALoadQHi[ch] * self.In5BHi[ch] /
                           self.Out5BHi[ch])  # (V)
        # Convert the voltage on the current measurement channel to a current.
        phys[currentCh, :] /= self.rCurrentMeas  # (A)
        return phys

    def countLines(self, fh):
        # Counter lidx starts counting at 1 for the first line.
        for lidx, line in enumerate(fh, 1):
            pass
        return lidx

    def postRead(self, saveThis):
        # Whether to correct for channel skew.
        corrChSkewBool = True

        # Channel on which the current is measured. This channel's phase is
        # subtracted from the other channels in phase difference calculation.
        # This channel's voltage is divided by the current measurement
        # resistance to obtain a physical magnitude in Ampere units.
        # Other channels voltages are divided by this channel's current to find
        # impedance magnitude.

        currentCh = 0

        # Flip voltage channels upside-down if requested.
        if saveThis == 'upsideDown':
            for ch in range(self.chCount):
                if ch != currentCh:
                    self.raw[ch, ...] *= -1
                    self.raw[ch, ...] += 2**16 - 1

        self.computePhys(currentCh)
        # Compute FFTs.
        self.freq = spfftpack.fftfreq(self.n, 1 / self.fs, )  # (Hz)
        self.fft = spfftpack.fft(self.raw) / self.n
        # Magnitude and uncorrected phase.
        self.phaseUnCorr = sp.angle(self.fft)  # (rad)
        self.mag16Bit = sp.absolute(self.fft)

        # Convert magnitude to physical units.
        f215 = float(2**15)
        self.magPhys = self.mag16Bit / f215
        for ch in range(self.chCount):
            self.magPhys[ch, :, :] *= (self.ALoadQHi[ch] * self.In5BHi[ch] /
                                       self.Out5BHi[ch])  # (V)
        # Convert the voltage on ch0 to a current.
        self.magPhys[0, :, :] /= self.rCurrentMeas  # (A)

        # Correct phase for channel skew.
        self.phase = self.phaseUnCorr
        if corrChSkewBool:
            for ch in range(self.chCount):
                deltaT = ch / (self.fs * self.scanChCount)  # (s)
                corrSlope = 2*sp.pi*deltaT  # (rad/Hz)
                for p in range(self.pktCount):
                    self.phase[ch, p, :] = sp.subtract(self.phase[ch, p, :],
                                                       self.freq * corrSlope)

        # Compute phase differences.
        # Be careful about angles looping through +/- pi.
        # A phase difference absolute value is less than pi radian.
        self.phaseDiff = sp.zeros_like(self.phase, dtype=float)
        for ch in range(self.chCount):
            self.phaseDiff[ch, :, :] = sp.subtract(self.phase[ch, :, :],
                                                   self.phase[currentCh, :, :])
        self.phaseDiff[self.phaseDiff < -sp.pi] += 2*sp.pi
        self.phaseDiff[self.phaseDiff > sp.pi] -= 2*sp.pi

        # Convert phase differences from radian to milliradian.
        self.phaseDiff *= 1000  # (mrad)

        # Calculate apparent impedance magnitude.
        self.zMag = sp.zeros_like(self.magPhys)
        for ch in range(self.chCount):
            # (Ohm)
            self.zMag[ch, :, :] = sp.divide(self.magPhys[ch, :, :],
                                            self.magPhys[currentCh, :, :])
        # Convert to milliOhm.
        self.zMag *= 1000


# Invoke the main function here.
if __name__ == "__main__":
    ipProcess()
