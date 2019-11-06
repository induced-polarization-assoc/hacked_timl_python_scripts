# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:57 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

import scipy as sp
from textwrap import wrap
import matplotlib.pyplot as plt


def plot1MeanSubtract1(ps):
    yValMat = ps.yVal
    # Compute means and standard deviations over the packets (axis 0).
    ps.yVal = sp.mean(yValMat, axis=0)
    ps.yStd = sp.std(yValMat, axis=0)

    yValMatA = ps.yValA
    # Compute means and standard deviations over the packets (axis 0).
    ps.yValA = sp.mean(yValMatA, axis=0)
    ps.yStdA = sp.std(yValMatA, axis=0)

    ps.yVal = ps.yVal - ps.yValA
    ps.yStd = sp.sqrt(ps.yStd**2 + ps.yStdA**2)
    basePlot(ps)

    # Return the unaveraged values to the plotting class objects.
    ps.yVal = yValMat
    ps.yValA = yValMatA


def plot1MeanSubtractAdj(ps):
    yValMat = ps.yVal
    # Compute means and standard deviations over the packets (axis 0).
    ps.yVal = sp.mean(yValMat, axis=0)
    ps.yStd = sp.std(yValMat, axis=0)

    yValMatA = ps.yValA
    # Compute means and standard deviations over the packets (axis 0).
    ps.yValA = sp.mean(yValMatA, axis=0)
    ps.yStdA = sp.std(yValMatA, axis=0)

    yValMatB = ps.yValB
    # Compute means and standard deviations over the packets (axis 0).
    ps.yValB = sp.mean(yValMatB, axis=0)
    ps.yStdB = sp.std(yValMatB, axis=0)

    ps.yVal = ps.yVal - (ps.yValA + ps.yValB)/2
    ps.yStd = sp.sqrt(ps.yStd**2 + (ps.yStdA + ps.yStdB)**2/4)
    basePlot(ps)

    # Return the unaveraged values to the plotting class objects.
    ps.yVal = yValMat
    ps.yValA = yValMatA
    ps.yValB = yValMatB


def plot1Mean(ps):
    '''
    Plots mean file data averaged over the packets.

    Parameters
    ----------
    ps : input class containing plotting choices
    '''
    yValMat = ps.yVal
    # Compute means and standard deviations over the packets (axis 0).
    ps.yVal = sp.mean(yValMat, axis=0)
    ps.yStd = sp.std(yValMat, axis=0)
    basePlot(ps)
    # Return the unaveraged values to the plotting class object.
    ps.yVal = yValMat


def basePlot(ps):
    # Function plots one thing at a time and can update formatting and labels.
    params = {'legend.fontsize': 'x-large',
              'figure.figsize': (11, 7.5),
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'x-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    # Plot the main result.
    # Use the string '_nolegend_' to hide the label from the legend display.
    if ps.normMag:
        ps.yStd = ps.yStd/ps.yVal[0]
        ps.yVal = ps.yVal/ps.yVal[0]
    lines2D = plt.plot(ps.xVal, ps.yVal, color=ps.color,
                       markersize=ps.markerSize,
                       marker=ps.marker, label=ps.legStr,
                       linestyle=ps.linestyle)
    if ps.stdBool:
        if ps.stdColor is None:
            if ps.color == 'LimeGreen':
                stdColor = 'g'
            elif ps.color == 'b':
                stdColor = 'DodgerBlue'
            elif ps.color == 'r':
                stdColor = 'Fuchsia'
            else:
                stdColor = lines2D[0].get_c()
        else:
            stdColor = ps.stdColor
        if len(ps.xVal) == 1:
            # Make a rectangle if there is only one frequency plotted.
            xVal = ps.xVal + sp.array([-0.5, 0.5])
            yVal = ps.yVal + sp.array([0, 0])
        else:
            xVal = ps.xVal
            yVal = ps.yVal
        # Plot a shaded envelope symbolizing the result +/- 1 std. dev.
        plt.fill_between(xVal, yVal - ps.yStd, yVal + ps.yStd,
                         facecolor=stdColor, alpha=0.5)

    titleStr = ps.titleStr
    if ps.omit60Hz:
        titleStr += ' 60 Hz omitted.'
    if ps.titleWrap < sp.inf:
        # Wrap text at a set character length.
        titleStr = '\n'.join(wrap(titleStr, ps.titleWrap))
    if ps.titleBool:
        plt.title(titleStr)
    plt.xlabel(ps.xLabel)
    plt.ylabel(ps.yLabel)
    if ps.legOutside:
        plt.legend(bbox_to_anchor=(1.0, 1), loc=ps.loc)
        plt.subplots_adjust(right=0.7)
#        plt.subplots_adjust(top = 0.85)
    else:
        plt.legend(loc=ps.loc)
        plt.tight_layout()
    plt.grid(b=True)
    plt.show()
