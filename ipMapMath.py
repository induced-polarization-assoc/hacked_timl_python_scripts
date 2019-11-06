# -*- coding: utf-8 -*-
"""
Created on Fri May 25 15:57:31 2018

@author: TimL
"""
import scipy as sp
from scipy import linalg as linalg
import commonSense as cs


def deg2rad(deg):
    """
    Convert angle in degrees to radians.

    Parameters
    ----------
    deg : float

    Returns
    -------
    rad : float
    """
    return deg * sp.pi / 180


def perp(vecArra):
    # Return the cross product of the positive z-directed unit vector with each
    # row vector input. The input and output vectors are in the xy-plane, and
    # the z-components aren't included.
    z3 = sp.array([0, 0, 1])
    per = sp.cross(z3, vecArra)
    return per[:, 0:2]


def unit(vecArra):
    nor = norm(vecArra)
    if len(sp.shape(vecArra)) > 1:
        # Return an array of unit row vectors in the same direction as the
        # input.
        return vecArra/nor[:, sp.newaxis]
    else:
        return vecArra/nor


def norm(vecArra):
    if len(sp.shape(vecArra)) > 1:
        # Return an array of vector norms for an array of row vectors.
        return linalg.norm(vecArra, axis=1)
    else:
        return linalg.norm(vecArra)


def coordExtrema(a):
    """
    Return corner coordinate positions of the smallest rectangle aligned with
    lines of longitude and latitude that would contain all the survey data
    points on or within its borders.

    Parameters
    ----------
    a : fileStruct, list
      Contains longitude and latitude information for each packet in each file.

    Returns
    -------
    ext : float (deg), fields of a class
      longiMin, longiMax, latMin, latMax
    """
    # Extreme values of longitude and latitude in the survey.
    longiMin = sp.inf
    latMin = sp.inf
    longiMax = -sp.inf
    latMax = -sp.inf
    for t in range(len(a)):
        if a[t].pktCount > 0:
            arraMin = sp.amin(a[t].longi)
            if arraMin < longiMin:
                longiMin = sp.amin(a[t].longi)
            arraMin = sp.amin(a[t].lat)
            if arraMin < latMin:
                latMin = arraMin
            arraMax = sp.amax(a[t].longi)
            if arraMax > longiMax:
                longiMax = arraMax
            arraMax = sp.amax(a[t].lat)
            if arraMax > latMax:
                latMax = arraMax

    ext = cs.emptyClass()
    ext.longiMin = longiMin
    ext.longiMax = longiMax
    ext.latMin = latMin
    ext.latMax = latMax
    return ext


def cableRange(leng, depth):
    # Estimate the horizontal displacement of the first electrode using a
    # simple static catenary shape for the cable.
    # Equations from:
    # http://ricerca.ismar.cnr.it/CRUISE_REPORTS/1990-1999/
    # URANIA_AZ99_REP/node17.html
    # G.Bortoluzzi 1999-10-16

    # Termination tolerance.
    tol = 1e-6
    # Initialize the iterated solution.
    rangJ1 = depth
    rangJ0 = -sp.inf
    while sp.absolute((rangJ1-rangJ0)/rangJ1) > tol:
        # Overwrite with the latest approximation.
        rangJ0 = rangJ1
        # Newton-Raphson method.
        rangJ1 = rangJ0 - f(rangJ0, leng, depth)/fP(rangJ0, leng, depth)
    return rangJ1


def lengFunc(rang, depth):
    radic = sp.sqrt(rang**2 + 4*depth**2)
    logar = sp.log((2*depth + radic)/rang)
    return 1/2*(radic + rang**2/(2*depth)*logar)


def f(rang, leng, depth):
    return lengFunc(rang, depth) - leng


def fP(rang, leng, depth):
    radic = sp.sqrt(rang**2 + 4*depth**2)
    logar = sp.log((2*depth + radic)/rang)
    return rang/2*(1/radic + logar/depth +
                   (rang**2/radic - 2*depth - radic) /
                   (2*depth*(2*depth + radic)))
