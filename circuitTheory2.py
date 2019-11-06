# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 15:47:04 2019

@author: TimL
"""

import commonSense as cs
import scipy as sp
import scipy.linalg as la
import matplotlib.pyplot as plt
from textwrap import wrap


def multiMeas():
    plotThis = 'zPhase'
    measList = ['R1', 'R2', 'R3', 'z_t']
    for idx in range(len(measList)):
        circuitTheory(measList[idx], plotThis)

def circuitTheory(meas='R1', plotThis='zPhase'):

    ci = cs.emptyClass()
    # Resistors. (Ohm)
    ci.r1 = 0.1
    ci.r2 = 0.1
    ci.r3 = ci.r2

    ci.r4 = 8
    # Capacitor. (F)
    ci.c = 3e-3
    
    ci.meas = meas
    ci.plotThis = plotThis
    
    # Transmit current. Phase = 0. (complex A)
    ci.i1 = 1

    # Transmit frequency list. (Hz)
    xmitFund = 4
    freqList = sp.array(range(xmitFund, xmitFund*(100 + 1), 2*xmitFund))
    result = sp.zeros_like(freqList)
    for idx in range(len(freqList)):
        # Frequency. (Hz)
        ci.f = freqList[idx]
        # Convert to milliUnits.
        result[idx] = 10**3*circuitSolve(ci)

    params = {'legend.fontsize': 'x-large',
              'figure.figsize': (9, 6.5),
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'x-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    ps = cs.emptyClass()
    ps.color = None
    ps.markerSize = 3
    ps.marker = 'o'
    ps.legStr = meas
    if meas == 'z_t':
        ps.legStr = 'Z_Target'
    ps.linestyle = 'solid'
    ps.titleStr = ('Resistors (Ohm): R1 = %.1f, R2 = %.1f, R3 = %.1f, '
                   'R4 = %.0f. Capacitor: C = %.0f mF. '
                   'Z_Target is the parallel impedance of R4 and C.'
                   % (ci.r1, ci.r2, ci.r3, ci.r4, ci.c*10**3))
    ps.titleWrap = 75
    ps.titleBool = True
    ps.xLabel = 'Frequency (Hz)'
    if plotThis == 'zPhase':
        ps.yLabel = 'Voltage Phase Shift from Transmit Current (mrad)'
    elif plotThis == 'zMag':
        ps.yLabel = 'Voltage Magnitude (mV)'
    ps.legOutside = False

    # Plot the main result.
    lines2D = plt.plot(freqList, result, color=ps.color,
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
        plt.legend(loc="best")
        plt.tight_layout()
    plt.grid(b=True)
    plt.show()


def circuitSolve(ci):
    # Solve for the phase of the current through R1, which is the phase of the
    # voltage across RX1-RX2 in the simplified circuit representation.
    # Source current. (A)
    i1 = ci.i1
    # Resistors. (Ohm)
    r1 = ci.r1
    r2 = ci.r2
    r3 = ci.r3
    r4 = ci.r4
    # Capacitance (F)
    c = ci.c

    # Angular frequency. (rad/s)
    omega = 2*sp.pi*ci.f
    # Target impedance. (complex Ohm)
    # The target is modeled as a capacitor in parallel with a resistor.
    z_t = 1/(1j*omega*c + 1/r4)

    # Matrix representation of the circuit system of equations. Nodal analysis.
    m = sp.zeros([5, 5], dtype=complex)
    m[0, :] = [1, 1, 0, 0, 0]
    m[1, :] = [-1, -1, 1/r1, -1/r1, 0]
    m[2, :] = [-1, 0, 0, 1/r2, 0]
    m[3, :] = [0, -1, 0, 1/r3, -1/r3]
    m[4, :] = [0, -1, 0, 0, 1/z_t]

    b = sp.zeros([sp.size(m, axis=0), 1], dtype=complex)
    b[0] = i1

    x = la.solve(m, b)
    # Potentials.
    v0 = x[2]
    v1 = x[3]
    v2 = x[4]
    
    print('\nFrequency = %.1f Hz' % ci.f)
    print(x)
    # Potential differences.
    if ci.meas == 'R1':
        vDiff = v0 - v1
#        print('Voltage R1: %.2f V\n' % vDiff)
    elif ci.meas == 'R2':
        vDiff = v1
#        print('Voltage R2: %.2f V\n' % vDiff)
    elif ci.meas == 'R3':
        vDiff = v1 - v2
#        print('Voltage R3: %.2f V\n' % vDiff)
    elif ci.meas == 'z_t':
        vDiff = v2
#        print('Voltage Z: %.2f V\n' % vDiff)

    if ci.plotThis == 'zPhase':
        phase = sp.arctan(sp.imag(vDiff)/sp.real(vDiff))
        return(phase)
    elif ci.plotThis == 'zMag':
        mag = sp.absolute(vDiff)
        return(mag)


# Invoke the main function here.
if __name__ == "__main__":
    multiMeas()
