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



# def ipProcess(save_this, freq_span=200, save_phase=True, select_files=True):
def ipProcess(this_session):
    """
    Reads text files in file_obj_array data folder and saves frequency domain results to file_obj_array
    pickled file to be opened later for plotting.
    """
    # Processed result choice.
    # 'raw': raw voltage waveforms from one packet in each file.
    # 'zAnyF': impedance phase and mag at non-zero fft frequencies,
    #          not skipping.
    # to_save = 'raw'
    # saveThis = save_this
    # Number nonzero frequencies saved to the .pkl file with the zero frequency
    # freqCount = 200
    freqCount = freq_span

    # Whether to save absolute phase results.
    savePhase = save_phase

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
    # TODO: Change this so the file list is in
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
    sort_key = file_number_array.argsort()
    file_array = file_array[sort_key]
    # file_number_array = file_number_array[sort_key]

    # List of class instances containing recorded data.
    file_obj_array = []
    for t in range(len(file_array)):
        file_obj_array.append(fileClass(file_name, raw_data_path, save_this))

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

# Invoke the main function here.
if __name__ == "__main__":
    ipProcess()

