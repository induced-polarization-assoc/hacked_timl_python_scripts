#!/bin/env python

#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

# timspackage.ipProcess.py
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 16:31:21 2018
Heavily modified on Thursday, November 7th, 2019
@author: TimL, jjradler
"""
import os
import scipy as sp
from timspackage import commonSense as cs
# from scipy import fftpack as spfftpack
# from datetime import datetime
import pickle

import mipgui.file_dialogs
import timspackage.FileClass as fileClass


def ipProcess(save_this, freq_span, save_phase=True, select_files=False):
    """
    Reads text files in file_obj_array data folder and saves frequency domain results to file_obj_array
    pickled file to be opened later for plotting.
    """
    # Processed result choice.
    # 'raw': raw voltage waveforms from one packet in each file.
    # 'zAnyF': impedance phase and mag at non-zero fft frequencies,
    #          not skipping.
    # to_save = 'raw'
    saveThis = save_this
    # Number nonzero frequencies saved to the .pkl file with the zero frequency
    # freqCount = 200
    freqCount = freq_span

    # Whether to save absolute phase results.
    savePhase = False

    # Whether to select file_obj_array specific file for processing, as opposed to all of
    # them.
    selected_files = select_files
    selectedFileNum = 5


    # FIXME:  Get it so the user input from the GUI can be used here.
    # pklFolder = r'C:\Users\timl\Documents\IP_data_plots\190506_eagle'
    pkl_folder: object = mipgui.file_dialogs.get_new_data()
    rawFolder = os.path.join(pklFolder, 'rawData')
    fileList = ([f for f in os.listdir(rawFolder)
                 if os.path.isfile(os.path.join(rawFolder, f))])
    # Catalog the file numbers stored in each file title. Remove from the list
    # files that don't have file_obj_array number.
    file_number_list = []
    files_to_keep = sp.zeros_like(fileList, dtype=bool)
    for t in range(len(fileList)):
        uscoreIdx = fileList[t].find('_')
        dotIdx = fileList[t].find('.')
        if uscoreIdx >= 0 and dotIdx >= 0:
            try:
                fileNum = int(fileList[t][uscoreIdx+1: dotIdx])
            except ValueError:
                pass
            else:
                if not selected_files or (selected_files and
                                        fileNum == selectedFileNum):
                    file_number_list.append(fileNum)
                    # Keep this file in the list.
                    files_to_keep[t] = True

    # Drop all files from the list that didn't have file_obj_array number.
    # Walk through in reverse order so as to not disturb index numbers as
    # elements are removed.
    for t in range(len(fileList))[::-1]:
        if ~files_to_keep[t]:
            del fileList[t]
    # Convert to arrays.
    file_array = sp.array(fileList)
    file_number_array = sp.array(file_number_list, dtype=int)
    del fileList
    del files_to_keep
    # Sort by file numbers.
    sortKey = file_number_array.argsort()
    file_array = file_array[sortKey]
    file_number_array = file_number_array[sortKey]

    # List of class instances containing recorded data.
    file_obj_array = []
    for t in range(len(file_array)):
        file_obj_array.append(fileClass())

    # Read the data in from the files.
    for t in range(len(file_obj_array)):
        # Packet choice if saving raw voltages.
        rawPkt = 102  # 1-indexed.
        filePath = os.path.join(rawFolder, file_array[t])
        file_obj_array[t].introduce(file_array[t])
        file_obj_array[t].read_txt(filePath, saveThis)
        # Remove unwanted fields to cut down on the saved file size.
        if saveThis == 'zAnyF' or saveThis == 'upsideDown':
            del file_obj_array[t].raw
            del file_obj_array[t].fft
            del file_obj_array[t].phaseUnCorr
            del file_obj_array[t].mag16Bit
            if not savePhase:
                del file_obj_array[t].phase
            # Array mask for saving.
            mask = sp.zeros(file_obj_array[t].n, dtype=bool)
            # Save non-zero frequencies and the DC frequency.
            mask[:freqCount + 1] = True
            file_obj_array[t].freq = file_obj_array[t].freq[mask]
            file_obj_array[t].phaseDiff = file_obj_array[t].phaseDiff[..., mask]
            file_obj_array[t].magPhys = file_obj_array[t].magPhys[..., mask]
            file_obj_array[t].zMag = file_obj_array[t].zMag[..., mask]
            if savePhase:
                file_obj_array[t].phase = file_obj_array[t].phase[..., mask]
        elif saveThis == 'raw':
            del file_obj_array[t].fft
            del file_obj_array[t].phaseUnCorr
            del file_obj_array[t].mag16Bit
            del file_obj_array[t].phase
            del file_obj_array[t].freq
            del file_obj_array[t].phaseDiff
            del file_obj_array[t].magPhys
            del file_obj_array[t].zMag
            p = cs.find(file_obj_array[t].pkt, rawPkt)
            if p == -1:
                # Save the last packet if the requested packet number isn't in
                # the file.
                rawPkt = file_obj_array[t].pkt[p]
            file_obj_array[t].raw = file_obj_array[t].raw[:, p, :]
            # Overwrite the list of packet numbers with the one packet number
            # that was saved.
            file_obj_array[t].pkt = rawPkt

    # Save the object to file_obj_array file named after the folder name.
    # FIXME: MAKE IT SO THE OUTPUT DIRECTORY IS SAVED AND USED HERE.
    lastSlash = pklFolder.rfind('\\')
    saveFile = pklFolder[lastSlash+1:] + '_' + saveThis + '.pkl'
    savePath = os.path.join(pklFolder, saveFile)
    # Saving the list object:
    with open(savePath, 'wb') as f:  # Python 3: open(..., 'wb')
        pickle.dump(file_obj_array, f)


# class fileclass:
#
#     def introduce(self, fileName):
#         print('Creating %s from %s.' % (self, fileName))
#
#     def read_txt(self, path, to_save):
#         # Read IP measurements from file_obj_array text file.
#         with open(path, 'r') as fh:
#             # Number of lines in the file.
#             lineCount = self.count_lines(fh)
#             # Rewind the pointer in the file back to the beginning.
#             fh.seek(0)
#             # Initialize the packet counter.
#             p = -1
#             # Initialize the sample index.
#             s = -1
#             for lidx, line in enumerate(fh, 1):
#                 # Strip off trailing newline characters.
#                 line = line.rstrip('\n')
#                 if s >= 0:
#                     # Read in raw voltage values.
#                     self.raw[:, p, s] = (
#                             sp.fromstring(line, dtype=float, sep=','))
#                     if s == self.n - 1:
#                         # Reset the counter to below zero.
#                         s = -1
#                     else:
#                         # Increment the sample counter for the next read.
#                         s += 1
#                 elif lidx > 10:
#                     if line[0] == '$':
#                         # Increment the packet index.
#                         p += 1
#                         # Reset the time domain quality parameter index.
#                         qp = 0
#                         # Packet number
#                         self.pkt[p] = int(line[1:])
#                     elif line[0] == '\'':
#                         # CPU UTC Date and Time Strings.
#                         (self.cpuDTStr[p].d,
#                          self.cpuDTStr[p].t) = line[1:].split(',')
#                         # Translate to datetime object.
#                         self.cpuDT[p] = self.string_to_datetime(self.cpuDTStr[p])
#                     elif line[0] == '@':
#                         # GPS UTC Date and Time Strings,
#                         # and latitude and longitude fixes.
#                         (self.gpsDTStr[p].d,
#                          self.gpsDTStr[p].t,
#                          self.lat[p],
#                          self.longi[p]) = line[1:].split(',')
#                         # Translate to datetime object.
#                         self.gpsDT[p] = self.string_to_datetime(self.gpsDTStr[p])
#                         # Type casting.
#                         self.lat[p] = float(self.lat[p])
#                         self.longi[p] = float(self.longi[p])
#                     elif qp < 7:
#                         qp += 1
#                         if qp == 3 or qp == 4 or qp == 5:
#                             typ = float  # Means are saved as floats.
#                         else:
#                             typ = int  # Counts are saved as integers.
#                         assignArr = sp.fromstring(line, dtype=typ, sep=',')
#                         if qp == 1:
#                             # Count of measurements clipped on the high end of
#                             # the MccDaq board's input range.
#                             self.clipHi[:, p] = assignArr
#                         elif qp == 2:
#                             # Count of measurements clipped on the low end of
#                             # the MccDaq board's input range.
#                             self.clipLo[:, p] = assignArr
#                         elif qp == 3:
#                             # Mean measurement value over the packet as file_obj_array
#                             # percentage of the AIn() half range.
#                             self.meanPct[:, p] = assignArr
#                         elif qp == 4:
#                             # (pct) Mean value of sample measurements above
#                             # or equal to the mean.
#                             self.meanUpPct[:, p] = assignArr
#                         elif qp == 5:
#                             # (pct) Mean value of sample measurements below
#                             # the mean.
#                             self.meanDnPct[:, p] = assignArr
#                         elif qp == 6:
#                             # Count of measurements above or equal to the mean.
#                             self.countUp[:, p] = assignArr
#                         elif qp == 7:
#                             # Count of measurements below the mean.
#                             self.countDn[:, p] = assignArr
#                             # Set the sample index to 0 to start.
#                             s = 0
#                 elif lidx == 1:
#                     (self.fileDateStr,  # UTC date file was created.
#                      self.fileNum) = line.split(',')  # File number in set.
#                     # Type casting.
#                     self.fileNum = int(self.fileNum)
#                 elif lidx == 2:
#                     self.descript = line  # Description of the test.
#                 elif lidx == 3:
#                     self.minor = line  # Minor note.
#                 elif lidx == 4:
#                     self.major = line  # Major note.
#                 elif lidx == 5:
#                     (self.scanChCount,  # number of channels in each A/D scan.
#                      self.chCount,  # number of channels written to the file.
#                      self.n,  # Number of samples in the FFT time series.
#                      self.fs,  # (Hz) FFT sampling frequency.
#                      self.xmitFund) = line.split(',')  # (Hz) Transmit Square
#                     # wave fundamental frequency.
#                     # Type casting.
#                     self.scanChCount = int(self.scanChCount)
#                     self.chCount = int(self.chCount)
#                     self.n = int(self.n)
#                     self.fs = int(self.fs)
#                     self.xmitFund = float(self.xmitFund)
#                     # Each file contains file_obj_array file header of length 10 lines,
#                     # followed by packets. Packets contain (11 + n) lines each.
#                     self.pktCount = int((lineCount - 10)/(11 + self.n))
#                     # Dimension arrays indexed by packet.
#                     self.init_array_dims()
#                 elif lidx == 6:
#                     (self.rCurrentMeas,  # (Ohm) resistance.
#                      self.rExtraSeries) = line.split(',')  # (Ohm).
#                     # Type casting.
#                     self.rCurrentMeas = float(self.rCurrentMeas)
#                     self.rExtraSeries = float(self.rCurrentMeas)
#                 elif lidx == 7:
#                     # Voltage measurement names.
#                     # 0-indexed by channel number.
#                     self.measStr = line.split(',')
#                 elif lidx == 8:
#                     # Construct arrays using the scipy package.
#                     # 5B amplifier maximum of the input range (V).
#                     # 0-indexed by channel number.
#                     self.In5BHi = sp.fromstring(line, dtype=float, sep=',')
#                 elif lidx == 9:
#                     # 5B amplifier maximum of the output range (V).
#                     # 0-indexed by channel number.
#                     self.Out5BHi = sp.fromstring(line, dtype=float, sep=',')
#                 elif lidx == 10:
#                     # MccDaq board AIn() maximum of the input range (V).
#                     # 0-indexed by channel number.
#                     self.ALoadQHi = sp.fromstring(line, dtype=float, sep=',')
#         # After the file has been read, perform some calculations.
#         self.post_read(to_save)
#
#     def init_array_dims(self):
#         # Initialize numpy arrays and python lists as zeros.
#         shape2D = (self.chCount, self.pktCount)
#         # 0-indexed by packet number.
#         self.pkt = sp.zeros(self.pktCount, dtype=int)
#         self.cpuDTStr = [cs.emptyClass()]*self.pktCount
#         self.cpuDT = [0]*self.pktCount
#         self.gpsDTStr = [cs.emptyClass()]*self.pktCount
#         self.gpsDT = [0]*self.pktCount
#         self.lat = sp.zeros(self.pktCount, dtype=float)
#         self.longi = sp.zeros(self.pktCount, dtype=float)
#         # 0-indexed by channel number.
#         # 0-indexed by packet number.
#         self.clipHi = sp.zeros(shape2D, dtype=int)
#         self.clipLo = sp.zeros(shape2D, dtype=int)
#         self.meanPct = sp.zeros(shape2D, dtype=float)
#         self.meanUpPct = sp.zeros(shape2D, dtype=float)
#         self.meanDnPct = sp.zeros(shape2D, dtype=float)
#         self.meanPhys = sp.zeros(shape2D, dtype=float)
#         self.meanUpPhys = sp.zeros(shape2D, dtype=float)
#         self.meanDnPhys = sp.zeros(shape2D, dtype=float)
#         self.countUp = sp.zeros(shape2D, dtype=int)
#         self.countDn = sp.zeros(shape2D, dtype=int)
#         # 0-indexed by channel number.
#         # 0-indexed by packet number.
#         # 0-indexed by sample number.
#         self.raw = sp.zeros((self.chCount, self.pktCount, self.n), dtype=float)
#
#     def string_to_datetime(self, date_time_string):
#         YY = 2000 + int(date_time_string.d[0: 0+2])
#         MO = int(date_time_string.d[2: 2+2])
#         DD = int(date_time_string.d[4: 4+2])
#         HH = int(date_time_string.t[0: 0+2])
#         MM = int(date_time_string.t[2: 2+2])
#         SS = int(date_time_string.t[4: 4+2])
#         micro = 1000 * int(date_time_string.t[7: 7+3])
#         if YY == 2000:
#             return datetime.min
#         else:
#             return datetime(YY, MO, DD, HH, MM, SS, micro)
#
#     def compute_phys(self, channel):
#         self.meanPhys = self.pct_to_phys(self.meanPct, channel)
#         self.meanUpPhys = self.pct_to_phys(self.meanUpPct, channel)
#         self.meanDnPhys = self.pct_to_phys(self.meanDnPct, channel)
#
#     def pct_to_phys(self, pct, channel):
#         phys = sp.zeros_like(pct, dtype=float)
#         for ch in range(self.chCount):
#             phys[ch, :] = (pct[ch, :] / 100 *
#                            self.ALoadQHi[ch] * self.In5BHi[ch] /
#                            self.Out5BHi[ch])  # (V)
#         # Convert the voltage on the current measurement channel to file_obj_array current.
#         phys[channel, :] /= self.rCurrentMeas  # (A)
#         return phys
#
#     def count_lines(self, fh):
#         # Counter lidx starts counting at 1 for the first line.
#         for lidx, line in enumerate(fh, 1):
#             pass
#         return lidx
#
#     def post_read(self, to_save):
#         # Whether to correct for channel skew.
#         corrChSkewBool = True
#
#         # Channel on which the current is measured. This channel's phase is
#         # subtracted from the other channels in phase difference calculation.
#         # This channel's voltage is divided by the current measurement
#         # resistance to obtain file_obj_array physical magnitude in Ampere units.
#         # Other channels voltages are divided by this channel's current to find
#         # impedance magnitude.
#
#         channel = 0
#
#         # Flip voltage channels upside-down if requested.
#         if to_save == 'upsideDown':
#             for ch in range(self.chCount):
#                 if ch != channel:
#                     self.raw[ch, ...] *= -1
#                     self.raw[ch, ...] += 2**16 - 1
#
#         self.compute_phys(channel)
#         # Compute FFTs.
#         self.freq = spfftpack.fftfreq(self.n, 1 / self.fs, )  # (Hz)
#         self.fft = spfftpack.fft(self.raw) / self.n
#         # Magnitude and uncorrected phase.
#         self.phaseUnCorr = sp.angle(self.fft)  # (rad)
#         self.mag16Bit = sp.absolute(self.fft)
#
#         # Convert magnitude to physical units.
#         f215 = float(2**15)
#         self.magPhys = self.mag16Bit / f215
#         for ch in range(self.chCount):
#             self.magPhys[ch, :, :] *= (self.ALoadQHi[ch] * self.In5BHi[ch] /
#                                        self.Out5BHi[ch])  # (V)
#         # Convert the voltage on ch0 to file_obj_array current.
#         self.magPhys[0, :, :] /= self.rCurrentMeas  # (A)
#
#         # Correct phase for channel skew.
#         self.phase = self.phaseUnCorr
#         if corrChSkewBool:
#             for ch in range(self.chCount):
#                 deltaT = ch / (self.fs * self.scanChCount)  # (s)
#                 corrSlope = 2*sp.pi*deltaT  # (rad/Hz)
#                 for p in range(self.pktCount):
#                     self.phase[ch, p, :] = sp.subtract(self.phase[ch, p, :],
#                                                        self.freq * corrSlope)
#
#         # Compute phase differences.
#         # Be careful about angles looping through +/- pi.
#         # A phase difference absolute value is less than pi radian.
#         self.phaseDiff = sp.zeros_like(self.phase, dtype=float)
#         for ch in range(self.chCount):
#             self.phaseDiff[ch, :, :] = sp.subtract(self.phase[ch, :, :],
#                                                    self.phase[channel, :, :])
#         self.phaseDiff[self.phaseDiff < -sp.pi] += 2*sp.pi
#         self.phaseDiff[self.phaseDiff > sp.pi] -= 2*sp.pi
#
#         # Convert phase differences from radian to milliradian.
#         self.phaseDiff *= 1000  # (mrad)
#
#         # Calculate apparent impedance magnitude.
#         self.zMag = sp.zeros_like(self.magPhys)
#         for ch in range(self.chCount):
#             # (Ohm)
#             self.zMag[ch, :, :] = sp.divide(self.magPhys[ch, :, :],
#                                             self.magPhys[channel, :, :])
#         # Convert to milliOhm.
#         self.zMag *= 1000


# Invoke the main function here.
if __name__ == "__main__":
    ipProcess()
