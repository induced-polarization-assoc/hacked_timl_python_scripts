# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:08:57 2018

@author: TimL
"""
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

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
from mpl_toolkits.axes_grid1 import make_axes_locatable


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

    ps.folderPath = r'C:\Users\timl\Documents\IP_data_plots\190506_eagle'
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
            # Estimated water depth on the line.
            senseFt = float(senseFt)  # (ft)
            depth = senseFt / 3.28084  # (m)
            # Dump results in a list.
            depthList.append([fileDateStr, fileNum, depth])

    # Loading the data.
    pklName = folderName + '_' + loadThis + '.pkl'
    filePath = os.path.join(ps.folderPath, pklName)
    with open(filePath, 'rb') as f:  # Python 3: open(..., 'rb')
        a = pickle.load(f)

    # Which files will be plotted.
    filesPlotted = cs.readFilesPlotted(a, ps.folderPath)

    # Crop information.
    if crop:
        cs.readCropInfo(a, ps.folderPath, 'pklCropInfo.txt')

    # Plotting choice.
    ps.plotThis = 'zMag'

    # Channel plotted.
    ps.ch = 1

    # Harmonic number of the xmitFund plotted.
    ps.h = 1
    # Index of the frequency in the list of odd harmonics.
    ps.freqIdx = 4*ps.h

    # Whether the color axis bounds are set manually.
    manualColor = True
    clipColorData = False
    colMin = 1  # /(2*sp.pi*4)
    colMax = 5.5  # /(2*sp.pi*4)

    # Whether to plot line segments and points along the survey track.
    ps.showLines = False

    # Whehter to save polygon and line shape files.
    ps.saveShape = False

    # Rectangle defined by coordinate extrema along longi and lat axes.
    ps.ext = mm.coordExtrema(a)

    # Offset distance to either side of the survey line color strip extends.
    ps.sideRange = 3  # (m)

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
    tList = sp.array(range(len(a)))
    tList = tList[filesPlotted]
    originalFreqIdx = ps.freqIdx
    for t in tList:
        ps.freqIdx = originalFreqIdx
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
            a[t].leadin = 65.25  # (m)
            # Take an average of the 3rd and 5th harmonics to get a reading
            # at 4 Hz when the xmitFund was 1 Hz.
            if a[t].xmitFund == 1 and ps.h == 1:
                ps.freqIdx = 4*4
                freqIdx3Hz = 4*3
                freqIdx5Hz = 4*5
                a[t].phaseDiff[ps.ch, :, ps.freqIdx] = (
                        (a[t].phaseDiff[ps.ch, :, freqIdx3Hz] +
                         a[t].phaseDiff[ps.ch, :, freqIdx5Hz])/2)
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
            elif ps.plotThis == 'crop':
                a[t].color = a[t].cropLogic.astype(float)
            # Edit the color data to clip at the manual bounds, if desired.
            if clipColorData:
                a[t].color[a[t].color < colMin] = colMin
                a[t].color[a[t].color > colMax] = colMax
            # Keep track of the maximum and minimum color values.
            if a[t].xmitFund != 8:
                if not crop:
                    arraMin = sp.amin(a[t].color)
                    arraMax = sp.amax(a[t].color)
                else:
                    if sp.any(a[t].cropLogic):
                        arraMin = sp.amin(a[t].color[a[t].cropLogic])
                        arraMax = sp.amax(a[t].color[a[t].cropLogic])
                    else:
                        arraMin = sp.inf
                        arraMax = -sp.inf
            if arraMin < ps.colMin:
                ps.colMin = arraMin
            if arraMax > ps.colMax:
                ps.colMax = arraMax

    # Manually set the min and max color values.
    if manualColor:
        ps.colMin = colMin
        ps.colMax = colMax

    # Big picture class containing master polygon, color, and line lists for
    # all survey lines.
    bp = cs.emptyClass()
    bp.polyList = []
    bp.colorList = []
    bp.lineList = []
    for t in tList:
        if a[t].pktCount > 0:
            if not crop or (crop and sum(a[t].cropLogic) > 0):
                print('file %s_%d' % (a[t].fileDateStr, a[t].fileNum))
                print(a[t].descript)
                # Print time the file started.
                print(a[t].cpuDTStr[0].t)
                plotStrip(bp, a[t], ps, crop)

    ps.fig = plt.gcf()
    ps.ax = ps.fig.add_subplot(111)
    ps.ax.set_aspect('equal')
    ps.cmap = 'jet'
    ps.lineCol = 'k'  # Color of the basic track line shape.
    # Geopandas data frame object containing each polygon in the list, along
    # with colors.
    dfPoly = gpd.GeoDataFrame({'geometry': bp.polyList,
                               'color': bp.colorList})
    dfPoly.crs = ps.crsAzEq

    dfLine = gpd.GeoDataFrame({'geometry': bp.lineList})
    dfLine.crs = ps.crsAzEq

    # Transform back to (longi,lat), if requested.
    if ps.plotWGS84:
        dfLine = dfLine.to_crs(ps.crsWGS84)
        dfPoly = dfPoly.to_crs(ps.crsWGS84)

    dfPoly.plot(ax=ps.ax, column='color', cmap=ps.cmap,
                vmin=ps.colMin, vmax=ps.colMax)

    if ps.showLines:
        dfLine.plot(ax=ps.ax, color=ps.lineCol)

    # Transform back to (longi,lat).
    if ~ps.plotWGS84:
        dfLine = dfLine.to_crs(ps.crsWGS84)
        dfPoly = dfPoly.to_crs(ps.crsWGS84)

    # Keep axis bounds from before the shorelines are plotted.
    xlimLeft, xlimRight = plt.xlim()
    ylimLeft, ylimRight = plt.ylim()
    xlimLeft = -100
    xlimRight = 500
    ylimLeft = -600
    ylimRight = 600
#    xlimLeft = -100
#    xlimRight = 500
#    ylimLeft = -300
#    ylimRight = 400
#    xlimLeft = 5000
#    xlimRight = 9000
#    ylimLeft = -3500
#    ylimRight = -1500
#    xlimLeft = 7800
#    xlimRight = 9000
#    ylimLeft = -3000
#    ylimRight = -2100

    if ps.saveShape:
        # Save the geodataframes to files for colors and lines.
        polyFileName = '%s_%s_Ch%dH%d' % (a[0].fileDateStr,
                                          ps.plotThis, ps.ch, ps.h)
        if clipColorData:
            polyFileName += '_clip%dand%d' % (colMin, colMax)
        lineFileName = '%s_lines' % (a[0].fileDateStr)
        shapeFolder = r'C:\temp\181213_dataFrameFileEagle'
        polyFilePath = os.path.join(shapeFolder, polyFileName)
        lineFilePath = os.path.join(shapeFolder, lineFileName)
        dfPoly.to_file(polyFilePath)
        dfLine.to_file(lineFilePath)

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
    if ps.plotThis != 'crop':
#        cbaxes = ps.fig.add_axes([0.8, 0.1, 0.03, 0.8])
        divider = make_axes_locatable(ps.ax)
        cax1 = divider.append_axes("right", size="10%", pad=0.05)
        cb = plt.colorbar(sm, cax=cax1)
        cb.set_label(cbarLabel)

    plt.sca(ps.ax)
    # Axes labels.
    if not ps.plotWGS84:
        plt.xlabel('W-E (m)')
        plt.ylabel('S-N (m)')
    else:
        plt.xlabel('Longitude (deg)')
        plt.ylabel('Latitude (deg)')
    plt.grid(b=True)
    # Plot title. Use notes recorded in one of the files plotted.
    tTitle = cs.find(filesPlotted, True)
#    titleStr = ('%s Ch %d (%s). Harmonic %d = %.0f Hz. xmitFund = %.0f Hz.'
#                % (a[tTitle].fileDateStr, ps.ch, a[tTitle].measStr[ps.ch], ps.h,
#                   ps.h*a[tTitle].xmitFund, a[tTitle].xmitFund))
    titleStr = ('Ch %d (%s). Harmonic %d = %.0f Hz. xmitFund = %.0f Hz.'
            % (ps.ch, a[tTitle].measStr[ps.ch], ps.h,
               ps.h*a[tTitle].xmitFund, a[tTitle].xmitFund))
#    titleStr = ('%s Ch %d (%s). Frequency = %.0f Hz.'
#                % (a[tTitle].fileDateStr, ps.ch, a[tTitle].measStr[ps.ch],
#                   ps.h*a[tTitle].xmitFund))
#    titleStr = ('%s_%d Line %s. Ch %d (%s). Frequency = %.0f Hz. '
#                'xmitFund = %.0f Hz.'
#                % (a[tTitle].fileDateStr, a[tTitle].fileNum,
#                   a[tTitle].descript, ps.ch, a[tTitle].measStr[ps.ch],
#                   a[tTitle].freq[ps.freqIdx], a[tTitle].xmitFund))
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
        elif ps.plotThis == 'crop':
            titleStr = '%s Orange = Array on Floor (Guess)' % (a[0].fileDateStr)
#            t = 4
#            titleStr = ('%s_%d Line %s. Average Speed 1.7 kt.' %
#                        (a[t].fileDateStr, a[t].fileNum, a[t].descript))
    plt.title(titleStr)
#    clims = cb.get_clim()
#    print('\n\ncolMin = %.3f\ncolMax = %.3f' % (clims[0], clims[1]))


def despike(arra, thresh):
    # Despike the array of data values based on the threshold spike size.
    # Replace spike values with the average of data values on either side.
    for idx in range(1, len(arra) - 1):
        if (sp.absolute(arra[idx] - arra[idx - 1]) > thresh and
                sp.absolute(arra[idx] - arra[idx + 1]) > thresh):
            arra[idx] = sp.mean(sp.array([arra[idx - 1], arra[idx + 1]]))
    return arra


def plotStrip(bp, at, ps, crop):
    """
    Plot a strip of colored polygons along a trace of GPS coordinates (deg).
    Extension of the strip outward from the line to either side is specified
    by ps.sideRange, in meters.

    Parameters
    ----------
    bp.polyList: master list of polygons, all lines included
    bp.colorList: master list of colors for each polygon
    bp.lineList: master list of survey lines
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
    
    # Print the total line length (m).
#    print('%.1f m along line.' % (sumLen[-1]))
    # Distance between start and endpoints.
    startFinDist = mm.norm(flatFix[0, :] - flatFix[-1, :])
#    print('%.1f m distance from start point to finish point.' % startFinDist)
    # Time elapsed on the line.
    lineTime = (at.cpuDT[-1] - at.cpuDT[0]).total_seconds()
#    print('%.0f s elapsed.' % lineTime)
    lineSpeed = startFinDist/lineTime  # (m/s)
    lineSpeed *= 1.94384  # (kt)
#    print('%.1f kt average speed' % lineSpeed)

    # Interpolate a laidback fix location on the track line.
    # Layback the extra length at the start of the line according to
    # the boat's heading for the first few meters twice the length of
    # the cable lead in.
    newFix = sp.zeros_like(flatFix, dtype=float)
    linLoc = 2*at.leadin
    closeIdx = sp.argmin(abs(sumLen - linLoc))
    # If the line is at least as long as twice the lead in.
    if sumLen[-1] > linLoc:
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
    else:
        # Else just use the heading of the whole line.
        startHeadingFix = flatFix[-1, :]
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
            if l1 != l2:
                newFix[p, :] = flatFix[idx1, :] + (flatFix[idx2, :] -
                      flatFix[idx1, :])*(linLoc - l1)/(l2 - l1)
            else:
                # Case of interpolation between two repeated locations.
                newFix[p, :] = flatFix[idx1, :]
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

    # If cropping, only include fix points where asked.
    plottedPkts = sp.array(range(len(at.pkt)))
    if crop and ps.plotThis != 'crop':
        plottedPkts = plottedPkts[at.cropLogic]
    lastGoodVerts = sp.zeros((4, 2))
    # Polygon patches for each packet.
    for p in plottedPkts:
        # Perpendicular displacement, length sideRange, at the first midpoint.
        if p != 0:
            # Identify a trailing midpoint which is different from the 
            # present fix location. (Not between duplicate fixes.)
            pPrior = p - 1
            while pPrior >= 0 and all(midPts[pPrior, :] == flatFix[p, :]):
                pPrior -= 1
            vert01 = sp.vstack((midPts[pPrior, :] - vPerpSeg[pPrior, :],
                                midPts[pPrior, :] + vPerpSeg[pPrior, :]))
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
        # In the case where IP packets come in at a higher rate than the GPS
        # fixes are updated, consecutive packets have the same position at
        # times. In this case, reuse the last useable polygon. This will plot
        # on top of the reused position.
        if sp.isnan(verts).any():
            verts = lastGoodVerts.copy()
        else:
            lastGoodVerts = verts.copy()
        # Vertices as tuples in a list.
        vertList = [tuple(row) for row in verts]
        # Append the latest polygon vertices to the list of polygons.
        bp.polyList.append(polygon(vertList))

    bp.colorList = sp.hstack((bp.colorList, at.color[plottedPkts]))

    # Include each segment between the fix coordinates as its own line object.
    for p in plottedPkts:
        if p < len(flatFix) - 1:
            endPts = [tuple(row) for row in flatFix[p:p+2, :]]
            if at.xmitFund == 8:
                bp.lineList.append(lineStr(endPts))

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
    """
    .. function:: shoreline()
    Geodataframe containing shorelines to draw as a layer on the chart.
    :param ps:
    :return:
    """
    dfShore = gpd.read_file((r'\\DESKTOP-9TUU31C\Documents\IP_data_plots'
                             r'\181112_eagle\NOAAShorelineDataExplorer'
                             r'\NSDE61619\CUSPLine.shp'),
                            crs=ps.crsWGS84)
#    dfShore = gpd.read_file((r'C:\Users\timl\Documents\IP_data_plots'
#                             r'\190506_eagle\NOAA Shoreline Data Explorer'
#                             r'\CUSPLine.shp'),
#                            crs=ps.crsWGS84)
    if not ps.plotWGS84:
        dfShore = dfShore.to_crs(ps.crsAzEq)
    dfShore.plot(ax=ps.ax, color='k')


# Invoke the main function here.
if __name__ == "__main__":
    ipSurvey()
