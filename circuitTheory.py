# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 15:47:04 2019

@author: TimL
"""

import commonSense as cs
import scipy as sp
import matplotlib.pyplot as plt
from textwrap import wrap


def circuitTheory():

    ci = cs.emptyClass()
    # Resistors. (Ohm)
    ci.r1 = 0.1
    ci.r2 = 0.1
    ci.r3 = ci.r2
    ci.r4 = 1
    ci.r5 = ci.r4
    ci.r6 = 0.8
    ci.r7 = 8
    # Capacitor. (F)
    ci.c = 3e-6
    # Transmit current. Phase = 0. (complex A)
    ci.i1 = 3

    # Transmit frequency list. (Hz)
    xmitFund = 4
    freqList = sp.array(range(xmitFund, xmitFund*(33 + 1), 2*xmitFund))
    phaseShift = sp.zeros_like(freqList)
    for idx in range(len(freqList)):
        # Frequency. (Hz)
        ci.f = freqList[idx]
        # Phase shift between the voltage across R1 and the transmit current.
        # Convert to milliradian.
        phaseShift[idx] = 10**3*phaseI4(ci)

    params = {'legend.fontsize': 'x-large',
              'figure.figsize': (9, 6.5),
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'x-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    ps = cs.emptyClass()
    ps.color = 'C0'
    ps.markerSize = 6
    ps.marker = 'o'
    ps.legStr = 'Circuit Theory'
    ps.linestyle = 'solid'
    ps.titleStr = 'Capacitor, C = %.2f uF.' % (ci.c*10**6)
    ps.titleWrap = 75
    ps.titleBool = True
    ps.xLabel = 'Frequency (Hz)'
    ps.yLabel = 'Phase Shift (mrad)'
    ps.legOutside = False

    # Plot the main result.
    lines2D = plt.plot(freqList, phaseShift, color=ps.color,
                       markersize=ps.markerSize,
                       marker=ps.marker, label=ps.legStr,
                       linestyle=ps.linestyle)

    titleStr = ps.titleStr
    if ps.titleWrap < sp.inf:
        # Wrap text at a set character length.
        titleStr = '\n'.join(wrap(titleStr, ps.titleWrap))
    if ps.titleBool:
        plt.title(titleStr)
    plt.xlabel(ps.xLabel)
    plt.ylabel(ps.yLabel)
    if ps.legOutside:
        plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        plt.subplots_adjust(right=0.75)
    else:
        plt.legend(loc="lower left")
        plt.tight_layout()
    plt.grid(b=True)
    plt.show()


def phaseI4(ci):
    # Solve for the phase of the current through R1, which is the phase of the
    # voltage across RX1-RX2 in the simplified circuit representation.
    # Source current. (A)
    i1 = ci.i1
    # Resistors. (Ohm)
    r1 = ci.r1
    r2 = ci.r2
    r3 = ci.r3
    r4 = ci.r4
    r5 = ci.r5
    r6 = ci.r6
    r7 = ci.r7
    # Capacitor. (F)
    c = ci.c
    # Angular frequency. (rad/s)
    omega = 2*sp.pi*ci.f
    # Target impedance. (complex Ohm)
    z = r7 + 1/(1j*omega*c)

    # Matrix representation of the circuit system of equations. Nodal analysis.
    m = sp.zeros([11, 11], dtype=complex)
    m[0, :] = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    m[1, :] = [0, 0, -1, 1, 1, 0, 0, 0, 0, 0, 0]
    m[2, :] = [1, 0, 0, 1, 0, -1, 0, 0, 0, 0, 0]
    m[3, :] = [0, 1, 0, 0, 1, 0, -1, 0, 0, 0, 0]
    m[4, :] = [-1, 0, 0, 0, 0, 0, 0, 1/r2, 0, -1/r2, 0]
    m[5, :] = [0, 0, -1, 0, 0, 0, 0, 1/r1, -1/r1, 0, 0]
    m[6, :] = [0, -1, 0, 0, 0, 0, 0, 1/r4, 0, 0, -1/r4]
    m[7, :] = [0, 0, 0, -1, 0, 0, 0, 0, 1/r3, -1/r3, 0]
    m[8, :] = [0, 0, 0, 0, -1, 0, 0, 0, 1/r5, 0, -1/r5]
    m[9, :] = [0, 0, 0, 0, 0, -1, 0, 0, 0, 1/r6, 0]
    m[10, :] = [0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1/z]

    b = sp.zeros([11, 1], dtype=complex)
    b[0] = i1

    x = sp.linalg.solve(m, b)

    # Angle of I4. (rad)
    phase = sp.angle(x[2])

    return(phase)


# Invoke the main function here.
if __name__ == "__main__":
    circuitTheory()
