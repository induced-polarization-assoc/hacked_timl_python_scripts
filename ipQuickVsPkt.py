# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:57 2018

@author: TimL
"""
import scipy as sp
from textwrap import wrap
import matplotlib.pyplot as plt
import commonSense as cs


class fileClass:
    pass


def ipQuickVsPkt(at, ch=1, h=1, plotThis='zPhase', crop=False):
    ps = cs.emptyClass

    # Plotting choice.
    ps.plotThis = plotThis
    # Channel plotted.
    ps.ch = ch
    # Harmonic number plotted.
    ps.h = h
    # Whether to filter out unwanted packets.
    ps.crop = crop

    params = {'legend.fontsize': 'x-large',
              'figure.figsize': (11, 7.5),
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'x-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    plot1VsPkt(at, ps)


def plot1VsPkt(at, ps):
    '''
    Plots a result from 1 file vs packet number.

    Parameters
    ----------
    at  : fileClass object.
    ps : class containing plotting choices
      See construction in ipPlot()
    '''
    # Color.
    if ps.plotThis == 'zPhase':
        color = 'b'
    elif ps.plotThis == 'zMag':
        color = 'r'
    elif ps.plotThis == '2MagPhys':
        color = 'g'
    elif ps.plotThis == 'clip':
        color = 'blueviolet'
    elif ps.plotThis == 'zTime':
        color = 'C1'
    # Marker size.
    mrkSize = 3
    # Index of the requested harmonic number.
    freqIdx = 4*ps.h
    # Legend text.
    legStr = ('%s (%d packets) %s'
              % (at.descript, at.pktCount, at.minor))
    if ps.plotThis == 'zPhase':
        result = at.phaseDiff[ps.ch, :, freqIdx]
    elif ps.plotThis == 'zMag':
        result = at.zMag[ps.ch, :, freqIdx]
    elif ps.plotThis == '2MagPhys':
        result = 2*at.magPhys[ps.ch, :, freqIdx]
    elif ps.plotThis == 'clip':
        result = at.clipHi[ps.ch, :] + at.clipLo[ps.ch, :]
    elif ps.plotThis == 'zTime':
        freq = at.freq[freqIdx]  # (Hz)
        result = (at.phaseDiff[ps.ch, :, freqIdx] /
                  (2*sp.pi * freq))  # (millisecond)

    xVal = sp.array(range(at.pktCount))

    # Filter out unwanted packets if cropping.
    if ps.crop:
        xVal = xVal[at.cropLogic]
        result = result[at.cropLogic]

    # Plot the result vs packet number.
    plt.plot(xVal, result,
             color=color, markersize=mrkSize, marker='o', label=legStr)

    titleStr = ('%s_%d Ch %d (%s). h = %d = %.0f Hz. xmitFund = %.0f Hz. %s'
                % (at.fileDateStr, at.fileNum, ps.ch, at.measStr[ps.ch], ps.h,
                   at.freq[freqIdx], at.xmitFund, at.major))
    # Wrap text at a set character length.
    titleStr = '\n'.join(wrap(titleStr, 75))
    plt.title(titleStr)
    plt.xlabel('Packet')
    if ps.plotThis == 'zPhase':
        plt.ylabel('Impedance Phase (mrad)')
    elif ps.plotThis == 'zMag':
        plt.ylabel('Impedance Magnitude (m$\Omega$)')
    elif ps.plotThis == '2MagPhys':
        if at.measStr[ps.ch] == 'currentMeas':
            plt.ylabel('Twice Complex Mag. (A)')
        else:
            plt.ylabel('Twice Complex Mag. (V)')
    elif ps.plotThis == 'clip':
        plt.ylabel('Samples Clipped (Out of n = %d in packet)' % (at.n))
    elif ps.plotThis == 'zTime':
        plt.ylabel('v-i Time (ms)')

    plt.legend()
    plt.grid(b=True)
#    plt.tight_layout()
    plt.show()


# Invoke the main function here.
if __name__ == "__main__":
    ipQuickVsPkt()
