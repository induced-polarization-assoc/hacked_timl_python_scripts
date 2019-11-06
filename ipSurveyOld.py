# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:57 2018

@author: TimL
"""
import os
import scipy as sp
import commonSense as cs
import ipMapMath as mm
import pickle
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point as point
from shapely.geometry import LineString as lineStr
from shapely.geometry import Polygon as polygon
from cartopy import crs as ccrs


class fileClass:
    pass


def ipSurvey():
    params = {'legend.fontsize': 'x-large',
              'figure.figsize': (9, 6.5),
              'axes.labelsize': 'x-large',
              'axes.titlesize': 'x-large',
              'xtick.labelsize': 'x-large',
              'ytick.labelsize': 'x-large'}
    plt.rcParams.update(params)

    # Class object holding plot settings.
    ps = cs.emptyClass()

    # Whether to save the plotted datasets to txt files.
    ps.saveTxt = False

    crop = True

    ps.folderPath = r'C:\temp\181112_eagle'
    folderName = cs.lastName(ps.folderPath)

    # Processed result choice.
    loadThis = 'zAnyF'

    # Read the depth information for each file.
    infoPath = os.path.join(ps.folderPath, 'depthInfo.txt')
    depthList = []
    with open(infoPath, 'r') as f:
        for lidx, line in enumerate(f, 1):
            # Strip off trailing newline characters.
            line = line.rstrip('\n')
            # Split up comma-delimited information.
            (fileDateStr, fileNum, senseFt) = line.split(',')
            # Type casting.
            fileNum = int(fileNum)
            senseFt = float(senseFt)  # (ft)
            # Add the depth of the sensor and convert to meter.
            depth = (2.5 + senseFt) / 3.28084  # (m)
            # Dump results in a list.
            depthList.append([fileDateStr, fileNum, depth])

    # Loading the data.
    pklName = folderName + '_' + loadThis + '.pkl'
    filePath = os.path.join(ps.folderPath, pklName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    # Crop information.
    if crop:
        cs.readCropInfo(a, ps.folderPath)

    # Plotting choice.
    ps.plotThis = 'zPhase'

    # Channel plotted.
    ps.ch = 1

    # Harmonic number of the xmitFund plotted.
    ps.h = 13
    # Index of the frequency in the list of odd harmonics.
    ps.freqIdx = 4*ps.h

    # Whether the color axis bounds are set manually.
    manualColor = False
    clipColorData = True
    colMin = 185
    colMax = 420

    # Whether to plot line segments and points along the survey track.
    ps.showLines = False
    ps.showPts = False

    # Rectangle defined by coordinate extrema along longi and lat axes.
    ps.ext = mm.coordExtrema(a)

    # Offset distance to either side of the survey line color strip extends.
    ps.sideRange = 3.5  # (m)

    # Whether to plot in (longi, lat) or a projected reference.
    ps.plotWGS84 = False

    # The WGS84 latitude-longitude Coordinate Reference System (CRS).
    ps.crsWGS84 = {'init': 'epsg:4326'}

    # Define an azimuthal equidistant Coordinate Reference System (CRS).
    longiCent = (ps.ext.longiMax + ps.ext.longiMin)/2
    latCent = (ps.ext.latMax + ps.ext.latMin)/2
    longiCent = -122.50032907675
    latCent = 47.617131187
    ccrsAzEq = ccrs.AzimuthalEquidistant(central_longitude=longiCent,
                                         central_latitude=latCent)
    # This Cartopy CRS (CCRS) can be converted into a `proj4` string/dict
    # compatible with GeoPandas.
    ps.crsAzEq = ccrsAzEq.proj4_init

    # Initializations.
    ps.colMin = sp.inf
    ps.colMax = -sp.inf
    tList = range(len(a))
    for t in tList:
        if a[t].pktCount > 0:
            # Join the longitude and latitude arrays into one matrix with two
            # columns. Col 0: longi, Col 1: lat.
            # (deg)
            a[t].fix = sp.transpose(sp.vstack((a[t].longi, a[t].lat)))
            # Associate a water depth with each fix at the ship location.
            for idx in range(len(depthList)):
                if a[t].fileNum == depthList[idx][1]:
                    if a[t].fileDateStr == depthList[idx][0]:
                        depth = depthList[idx][2]
            a[t].depth = depth*sp.ones_like(a[t].pkt)  # (m)
            # Cable lead-length deployed.
            a[t].leadin = 57  # (m)
            # Pick which data to map to colors in the plot.
            if ps.plotThis == 'zPhase':
                a[t].color = a[t].phaseDiff[ps.ch, :, ps.freqIdx]
                # Despike phase differences with a threshold spike in mrad.
#                a[t].color = despike(a[t].color, 10)
                cbarLabel = 'Impedance Phase (mrad)'
            elif ps.plotThis == 'zMag':
                a[t].color = a[t].zMag[ps.ch, :, ps.freqIdx]
                # Despike magnitudes with a threshold spike in mOhm.
#                a[t].color = despike(a[t].color, 0.5)
                cbarLabel = 'Impedance Magnitude (m$\Omega$)'
            elif ps.plotThis == '2MagPhys':
                a[t].color = 2*a[t].magPhys[ps.ch, :, ps.freqIdx]
#                a[t].color = despike(a[t].color, 0.01)
                if ps.ch == 0:
                    cbarLabel = 'Twice Complex Mag. (A)'
                else:
                    cbarLabel = 'Twice Complex Mag. (V)'
            elif ps.plotThis == 'zTime':
                freq = a[t].freq[ps.freqIdx]  # (Hz)
                a[t].color = (a[t].phaseDiff[ps.ch, :, ps.freqIdx] /
                             (2*sp.pi * freq))  # (millisecond)
                # Despike phase differences with a threshold spike in us.
#                a[t].color = despike(a[t].color, 100)
                cbarLabel = 'v-i Time (ms)'
            # Edit the color data to clip at the manual bounds, if desired.
            if clipColorData:
                a[t].color[a[t].color < colMin] = colMin
                a[t].color[a[t].color > colMax] = colMax
            # Keep track of the maximum and minimum color values.
            arraMin = sp.amin(a[t].color)
            if arraMin < ps.colMin:
                ps.colMin = arraMin
            arraMax = sp.amax(a[t].color)
            if arraMax > ps.colMax:
                ps.colMax = arraMax

    # Manually set the min and max color values.
    if manualColor:
        ps.colMin = colMin
        ps.colMax = colMax

    ps.fig, ps.ax = plt.subplots()
    ps.ax.set_aspect('equal')
    ps.cmap = 'jet'
    ps.lineCol = 'k'  # Color of the basic track line shape.
    for t in tList:
        if a[t].pktCount > 0:
            if not crop or (crop and sum(a[t].cropLogic) > 0):
                print('file %s_%d' % (a[t].fileDateStr, a[t].fileNum))
                print(a[t].descript)
                plotStrip(a[t], ps, crop)

    # Keep axis bounds from before the shorelines are plotted.
    xlimLeft, xlimRight = plt.xlim()
    ylimLeft, ylimRight = plt.ylim()
    xlimLeft = -408.14159194218564
    xlimRight = 383.2435609713969
    ylimLeft = -375.3266408701022
    ylimRight = 325.37655253272123

    if ps.saveShape:
        # Save the geodataframes to files for colors and lines.
        polyFileName = 'ch%d_H%d_%s_%s_%d.txt' % (ps.ch, ps.h, ps.plotThis,
                                             at.fileDateStr, at.fileNum,)

    # Shoreline plotting.
    shoreline(ps)

    # Reset the axis bounds after shorelines are plotted.
    plt.xlim(xlimLeft, xlimRight)
    plt.ylim(ylimLeft, ylimRight)

    # Display the colormap in use as a sidebar colorbar.
    sm = plt.cm.ScalarMappable(cmap=ps.cmap,
                               norm=plt.Normalize(vmin=ps.colMin,
                                                  vmax=ps.colMax))
    sm._A = []
    # colorbar() requires a scalar mappable, "sm".
    cb = plt.colorbar(sm)
    cb.set_label(cbarLabel)

    # Axes labels.
    if not ps.plotWGS84:
        plt.xlabel('W-E (m)')
        plt.ylabel('S-N (m)')
    else:
        plt.xlabel('Longitude (deg)')
        plt.ylabel('Latitude (deg)')
    plt.grid(b=True)
    # Plot title.
    titleStr = ('%s Ch %d (%s). Harmonic %d = %.2f Hz. xmitFund = %.2f Hz.'
                % (a[0].fileDateStr, ps.ch, a[0].measStr[ps.ch], ps.h,
                   ps.h*a[0].xmitFund, a[0].xmitFund))
    if manualColor or clipColorData:
        if ps.plotThis == 'zPhase':
            titleStr += (' \nColors clipped at %d mrad and %d mrad.'
                         % (ps.colMin, ps.colMax))
        elif ps.plotThis == 'zMag':
            titleStr += ((' \nColors clipped at %.1f m$\Omega$ ' +
                         'and %.1f m$\Omega$.')
                         % (ps.colMin, ps.colMax))
        elif ps.plotThis == '2MagPhys':
            titleStr += ((' \nColors clipped at %.2f A ' +
                         'and %.2f A.')
                         % (ps.colMin, ps.colMax))
        elif ps.plotThis == 'zTime':
            titleStr += ((' \nColors clipped at %.2f ms ' +
                          'and %.2f ms.')
                        % (ps.colMin, ps.colMax))
    plt.title(titleStr)


def despike(arra, thresh):
    # Despike the array of data values based on the threshold spike size.
    # Replace spike values with the average of data values on either side.
    for idx in range(1, len(arra) - 1):
        if (sp.absolute(arra[idx] - arra[idx - 1]) > thresh and
                sp.absolute(arra[idx] - arra[idx + 1]) > thresh):
            arra[idx] = sp.mean(sp.array([arra[idx - 1], arra[idx + 1]]))
    return arra


def plotStrip(at, ps, crop):
    """
    Plot a strip of colored polygons along a trace of GPS coordinates (deg).
    Extension of the strip outward from the line to either side is specified
    by ps.sideRange, in meters.

    Parameters
    ----------
    at.fix : float (deg), (pktCount)x2 array
      [longitude, latitude] coordinates of ship, rows are packets in order.
    at.depth :  float (m), array length pktCount
      Water depth beneath the ship at each fix. Used with extended lead-in
      length of cable to estimate sensor position by layback calculation.
    at.leadin : float (m)
    at.color : float (m), array length pktCount
      List of numbers for each position indicating the color to plot
      representing IP data results.
    """
    # Start by transforming the fix points into a local azimuthal equidistant
    # reference system. Units along x and y are meters.
    ptList = [point(tuple(row)) for row in at.fix]
    dfPt = gpd.GeoDataFrame({'geometry': ptList})
    # Assign the WGS84 latitude-longitude Coordinate Reference System (CRS).
    dfPt.crs = ps.crsWGS84

    # Transform to the azimuthal equidistant reference.
    dfPt = dfPt.to_crs(ps.crsAzEq)
    # Extract the transformed coordinates into an array.
    flatFix = sp.zeros_like(at.fix, dtype=float)
    for p in range(len(flatFix)):
        flatFix[p, :] = sp.array(dfPt.geometry[p].coords)  # (m)

    # Track vectors between each pair of consecutive GPS fixes.
    vParSeg = flatFix[1:, :] - flatFix[0:-1, :]
    # Length of each trach vector.
    segLen = sp.sqrt(vParSeg[:, 0]**2 + vParSeg[:, 1]**2)  # (m)
    # Cumulative sum along the track line.
    sumLen = sp.hstack((0, sp.cumsum(segLen)))

    # Interpolate a laidback fix location on the track line.
    # Layback the extra length at the start of the line according to
    # the boat's heading for the first few meters twice the length of
    # the cable lead in.
    newFix = sp.zeros_like(flatFix, dtype=float)
    linLoc = 2*at.leadin
    closeIdx = sp.argmin(abs(sumLen - linLoc))
    if linLoc >= sumLen[closeIdx]:
        idx1 = closeIdx
        idx2 = closeIdx + 1
    else:
        idx1 = closeIdx - 1
        idx2 = closeIdx
    l1 = sumLen[idx1]
    l2 = sumLen[idx2]
    startHeadingFix = flatFix[idx1, :] + (flatFix[idx2, :] -
          flatFix[idx1, :])*(linLoc - l1)/(l2 - l1)
    startHeadingVec = mm.unit(startHeadingFix - flatFix[0, :])
    for p in range(len(flatFix)):
        linLoc = sumLen[p] - mm.cableRange(at.leadin, at.depth[p])
        if linLoc >= 0:
            closeIdx = sp.argmin(abs(sumLen - linLoc))
            if linLoc >= sumLen[closeIdx]:
                idx1 = closeIdx
                idx2 = closeIdx + 1
            else:
                idx1 = closeIdx - 1
                idx2 = closeIdx
            l1 = sumLen[idx1]
            l2 = sumLen[idx2]
            newFix[p, :] = flatFix[idx1, :] + (flatFix[idx2, :] -
                  flatFix[idx1, :])*(linLoc - l1)/(l2 - l1)
        else:
            newFix[p, :] = flatFix[0, :] + linLoc*startHeadingVec
    # Overwrite.
    flatFix = newFix

    # Reevaluate track vectors between each pair of consecutive GPS fixes.
    vParSeg = flatFix[1:, :] - flatFix[0:-1, :]
    # Track vectors at each point, found from points before and after.
    vParPt = flatFix[2:, :] - flatFix[0:-2, :]
    # Include segment parallels for the boundary fix points.
    vParPt = sp.vstack((vParSeg[0, :], vParPt, vParSeg[-1, :]))
    # Midpoints along the sequence of GPS fixes.
    midPts = (flatFix[1:, :] + flatFix[0:-1, :])/2

    # Perpendicular vectors at each segment and fix point.
    # Vector lengths are set to sideRange.
    vPerpSeg = ps.sideRange*mm.unit(mm.perp(vParSeg))  # (m)
    vPerpPt = ps.sideRange*mm.unit(mm.perp(vParPt))  # (m)

    # Include each segment between the fix coordinates as its own line object.
    lineList = []
    for p in range(len(flatFix) - 1):
        endPts = [tuple(row) for row in flatFix[p:p+2, :]]
        lineList.append(lineStr(endPts))
    dfLine = gpd.GeoDataFrame({'geometry': lineList})
    dfLine.crs = ps.crsAzEq

    polyList = []
    # If cropping, only include fix points where asked.
    plottedPkts = sp.array(range(len(at.pkt)))
    if crop:
        plottedPkts = plottedPkts[at.cropLogic]
    # Polygon patches for each packet.
    for p in plottedPkts:
        # Perpendicular displacement, length sideRange, at the first midpoint.
        if p != 0:
            vert01 = sp.vstack((midPts[p-1, :] - vPerpSeg[p-1, :],
                                midPts[p-1, :] + vPerpSeg[p-1, :]))
        else:
            vert01 = sp.zeros((0, 2))
        # Polygon points offset from the flat fix points themselves.
        vert2 = flatFix[p, :] + vPerpPt[p, :]
        vert5 = flatFix[p, :] - vPerpPt[p, :]
        if p != len(flatFix) - 1:
            # at the second midpoint.
            vert34 = sp.vstack((midPts[p, :] + vPerpSeg[p, :],
                                midPts[p, :] - vPerpSeg[p, :]))
        else:
            vert34 = sp.zeros((0, 2))
        # Polygon vertices.
        verts = sp.vstack((vert01, vert2, vert34, vert5))
        # Vertices as tuples in a list.
        vertList = [tuple(row) for row in verts]
        # Append the latest polygon vertices to the list of polygons.
        polyList.append(polygon(vertList))

    # Geopandas data frame object containing each polygon in the list, along
    # with colors.
    dfPoly = gpd.GeoDataFrame({'geometry': polyList,
                               'color': at.color[plottedPkts]})
    dfPoly.crs = ps.crsAzEq
    # Transform back to (longi,lat), if requested.
    if ps.plotWGS84:
        dfPt = dfPt.to_crs(ps.crsWGS84)
        dfLine = dfLine.to_crs(ps.crsWGS84)
        dfPoly = dfPoly.to_crs(ps.crsWGS84)

    dfPoly.plot(ax=ps.ax, column='color', cmap=ps.cmap,
                vmin=ps.colMin, vmax=ps.colMax)

    if ps.showLines:
        dfLine.plot(ax=ps.ax, color=ps.lineCol)
    if ps.showPts:
        dfPt.plot(ax=ps.ax)

    # Transform back to (longi,lat).
    if ~ps.plotWGS84:
        dfPt = dfPt.to_crs(ps.crsWGS84)
        dfLine = dfLine.to_crs(ps.crsWGS84)
        dfPoly = dfPoly.to_crs(ps.crsWGS84)

    if ps.saveTxt:
        # Pseudocolor plots.
        txtName = 'ch%d_H%d_%s_%s_%d.txt' % (ps.ch, ps.h, ps.plotThis,
                                             at.fileDateStr, at.fileNum,)
        txtPath = os.path.join(ps.folderPath, 'plotData', ps.plotThis, txtName)
        with open(txtPath, 'w') as f:
            for p in range(at.pktCount):
                # longi (deg), lat (deg), color (?)
                wStr = (str(dfPt.geometry[p].x) + ',' +
                        str(dfPt.geometry[p].y) + ',' +
                        str(at.color[p]) + '\n')
                f.write(wStr)


def shoreline(ps):
    # Geodataframe containing shorelines to draw as a layer on the chart.
    dfShore = gpd.read_file((r'C:\temp\181112_eagle' +
                             r'\NOAAShorelineDataExplorer' +
                             r'\NSDE61619\CUSPLine.shp'),
                            crs=ps.crsWGS84)
    if not ps.plotWGS84:
        dfShore = dfShore.to_crs(ps.crsAzEq)
    dfShore.plot(ax=ps.ax, color='k')


# Invoke the main function here.
if __name__ == "__main__":
    ipSurvey()
